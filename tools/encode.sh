#!/usr/bin/env bash
# Encode one part: HDR(HLG) iPhone source -> SDR 4K 60fps H.264 with the overlay on top.
# Usage: encode.sh SRC START DURATION OVERLAY_DIR OUT.mp4 [PRESET]
set -euo pipefail
SRC=$1; START=$2; DUR=$3; OV=$4; OUT=$5; PRESET=${6:-faster}

# Overlay PNGs -> YUVA 4:2:0 (BT.709) once, so the main pass skips per-frame RGB conversion
for k in intro loop; do
  [ -f "$OV/$k.mkv" ] || ffmpeg -hide_banner -loglevel error -y -framerate 60 -i "$OV/${k}_%04d.png" \
    -vf "scale=out_color_matrix=bt709:out_range=tv,format=yuva420p" -c:v ffv1 "$OV/$k.mkv"
done
read -r BAND_Y BAND_H < "$OV/band.txt"
N=$(python3 -c "print(round($DUR*60))")
LOOPN=$((N - 120))
FADE_OUT=$(python3 -c "print(max(0, $DUR-0.35))")

ffmpeg -hide_banner -y -stats -loglevel error \
  -ss "$START" -t "$DUR" -i "$SRC" \
  -i "$OV/intro.mkv" \
  -stream_loop -1 -i "$OV/loop.mkv" \
  -filter_complex "\
[0:v]colorspace=all=bt709:iall=bt2020:itrc=bt2020-10:irange=tv:range=tv:format=yuv420p,fps=60,setsar=1[base];\
[2:v]trim=end_frame=${LOOPN},setpts=PTS-STARTPTS[lp];\
[1:v][lp]concat=n=2:v=1:a=0[ov];\
[base][ov]overlay=0:${BAND_Y}:format=yuv420:eof_action=pass:repeatlast=0,trim=end_frame=${N}[v]" \
  -map "[v]" -map 0:a:0 \
  -af "afade=t=in:d=0.15,afade=t=out:st=${FADE_OUT}:d=0.35" \
  -c:v libx264 -preset "$PRESET" -crf 19 -maxrate "${MAXRATE:-50M}" -bufsize "${BUFSIZE:-100M}" \
  -profile:v high -level:v 5.2 -pix_fmt yuv420p -r 60 \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  -c:a aac -b:a 256k -ar 48000 \
  -metadata:s:v:0 rotate=0 -movflags +faststart "$OUT"
