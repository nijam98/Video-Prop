#!/usr/bin/env bash
# Usage: render.sh <input.mov> <output.mp4> <preview|final>
# Ringkas + hook text. Warna HDR (HLG / BT.2020 10-bit) dikekalkan, tiada motion/transition.
# 29.97 -> 59.94 fps guna frame duplicate (tiada interpolation).
set -euo pipefail
IN="$1"; OUT="$2"; MODE="${3:-preview}"

if [ "$MODE" = final ]; then W=2160; H=3840; CRF=14; PRESET=slow
else W=1080; H=1920; CRF=22; PRESET=fast; fi

# Segmen (saat, ikut video asal) — A/V dipotong bersama
SEGS=(
  "10.80 13.20"   # "semi-D yang paling premium dalam kawasan ni"  (HOOK)
  "0.00 3.80"     # "Dekat dengan Tasik Darulaman, dekat dengan Taman Tengku Intan Safinaz"
  "8.50 10.80"    # "rumah dah siap semua tu. CCC dah dapat dah"
  "13.40 19.95"   # "Non-bumi lot ... bumi lot ... semi-D dah siap, boleh masuk terus"
  "21.80 23.75"   # "isi dekat bawah ni"
  "24.55 25.68"   # "Ataupun WhatsApp"
)
HOOK_END=6.10     # hook text dipapar sepanjang 2 segmen pertama

FONT_B=/usr/share/fonts/opentype/inter/InterDisplay-Black.otf
FONT_S=/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf
# Putih HLG ~92% signal = sama terang dengan langit dalam video (bukan 100%, elak silau di HDR)
WHITE=0xEBEBEB
S=$(python3 -c "print($W/2160)")
px(){ python3 -c "print(round($1*$S))"; }
F1=$(px 66); F2=$(px 132); BW1=$(px 22); BW2=$(px 30)
Y1=$(px 560); Y2=$(px 680); Y3=$(px 870)

# Setiap segmen = input berasingan (elak buffer frame 4K dalam RAM)
FC=""; CAT=""; INS=(); n=${#SEGS[@]}
for i in "${!SEGS[@]}"; do
  read a b <<<"${SEGS[$i]}"; d=$(python3 -c "print(round($b-$a,3))"); fo=$(python3 -c "print(round($b-$a-0.015,3))")
  INS+=(-ss "$a" -t "$d" -i "$IN")
  FC+="[$i:v:0]setpts=PTS-STARTPTS[v$i];"
  FC+="[$i:a:0]asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st=$fo:d=0.015[a$i];"
  CAT+="[v$i][a$i]"
done
EN="enable='lt(t,$HOOK_END)'"
DT="fontcolor=$WHITE:box=1:boxcolor=black@0.55:x=(w-text_w)/2:$EN"
FC+="${CAT}concat=n=$n:v=1:a=1[vc][ac];"
FC+="[vc]scale=$W:$H:flags=lanczos,fps=60000/1001,"
FC+="drawtext=fontfile=$FONT_S:text='JITRA, KEDAH  •  DEKAT TASIK DARULAMAN':fontsize=$F1:boxborderw=$BW1:y=$Y1:$DT,"
FC+="drawtext=fontfile=$FONT_B:text='SEMI-D PALING PREMIUM':fontsize=$F2:boxborderw=$BW2:y=$Y2:$DT,"
FC+="drawtext=fontfile=$FONT_B:text='SIAP, BOLEH MASUK TERUS':fontsize=$F2:boxborderw=$BW2:y=$Y3:$DT,"
FC+="format=yuv420p10le[vo]"

ffmpeg -hide_banner -y -nostats "${INS[@]}" -filter_complex "$FC" -map "[vo]" -map "[ac]" \
  -c:v libx265 -preset $PRESET -threads 4 -crf $CRF -pix_fmt yuv420p10le -profile:v main10 -tag:v hvc1 \
  -x265-params "colorprim=bt2020:transfer=arib-std-b67:colormatrix=bt2020nc:range=limited:log-level=error" \
  -color_primaries bt2020 -color_trc arib-std-b67 -colorspace bt2020nc -color_range tv \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart "$OUT"
