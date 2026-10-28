#!/usr/bin/env bash
# Build one part: cut the base video, render overlays, composite.
# usage: build_part.sh <part> <start> <end> <base.mp4> <workdir> <out.mp4> "<extra query: title=..&sub=..&sub2=..>"
# expects data/track_part<part>.json (make_track.py) for subtitles + callouts
# env: FPS (30), SCALE (1 = 1080x1920, 2 = 2160x3840), HDR=1 when <base> is the original HDR clip (tone-mapped here),
#      CRF (20), PRESET (slow), REUSE=1 to keep already-rendered overlay layers
set -euo pipefail
PART=$1 START=$2 END=$3 BASE=$4 WORK=$5 OUT=$6 EXTRA=${7:-}
HERE="$(cd "$(dirname "$0")" && pwd)"
INTRO=5.5 HOLD=1.3 CTA=5.0 FPS=${FPS:-30} SCALE=${SCALE:-1} CRF=${CRF:-20} PRESET=${PRESET:-slow}
OW=$((1080*SCALE)) OH=$((1920*SCALE))
if [ "${HDR:-0}" = 1 ]; then
  VF="scale=$OW:$OH:flags=lanczos,zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,fps=$FPS"
else
  VF="scale=$OW:$OH:flags=lanczos,fps=$FPS,format=yuv420p"
fi
D=$(python3 -c "print(round($END-$START,3))")
CTA_AT=$(python3 -c "print(round($D-$CTA,3))")
W="$WORK/part$PART"; [ "${REUSE:-0}" = 1 ] || rm -rf "$W"; mkdir -p "$W"
# REUSE=1 keeps already-rendered layers (delete a layer dir to re-render it)
r() { [ "${REUSE:-0}" = 1 ] && [ -d "$1" ] || "${@:2}"; }

export SCALE
r "$W/intro" node "$HERE/render.js" "$W/intro" $INTRO $FPS "part=$PART&scene=intro&hold=$HOLD&$EXTRA" &
r "$W/badge" node "$HERE/render.js" "$W/badge" 0 $FPS "part=$PART&scene=intro&hold=$HOLD&$EXTRA" $INTRO &
r "$W/track" env TRACK_FILE="$HERE/data/track_part$PART.json" node "$HERE/render.js" "$W/track" $D $FPS "part=$PART&scene=track" &
r "$W/cta" node "$HERE/render.js" "$W/cta" $CTA $FPS "part=$PART&scene=cta&$EXTRA" &
wait

ffmpeg -v error -stats -y \
  -ss "$START" -to "$END" -i "$BASE" \
  -framerate $FPS -i "$W/intro/f_%04d.png" \
  -loop 1 -framerate $FPS -i "$W/badge/still_$(printf %.2f $INTRO).png" \
  -framerate $FPS -i "$W/cta/f_%04d.png" \
  -framerate $FPS -i "$W/track/f_%04d.png" \
  -filter_complex "
    [0:v]setpts=PTS-STARTPTS,$VF[v];
    [1:v]setpts=PTS-STARTPTS[i];
    [3:v]setpts=PTS-STARTPTS+$CTA_AT/TB[c];
    [4:v]setpts=PTS-STARTPTS[tr];
    [v][i]overlay=eof_action=pass[a];
    [a][2:v]overlay=shortest=1:enable='gte(t,$INTRO-0.04)'[b];
    [b][c]overlay=eof_action=pass[bc];
    [bc][tr]overlay=eof_action=pass,format=yuv420p[out];
    [0:a]asetpts=PTS-STARTPTS,afade=t=in:d=0.25,afade=t=out:st=$(python3 -c "print($D-0.6)"):d=0.6[aout]" \
  -map "[out]" -map "[aout]" -r $FPS \
  -c:v libx264 -preset $PRESET -crf $CRF -profile:v high -pix_fmt yuv420p \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "built $OUT ($D s)"
