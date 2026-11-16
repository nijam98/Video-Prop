#!/usr/bin/env bash
# Rebuilds assets/footage.mp4 + assets/voice.wav from the original iPhone clip (HLG HDR, 4K HEVC).
# Usage: tools/prepare-footage.sh /path/to/original.MOV
set -euo pipefail
SRC="$1"; cd "$(dirname "$0")/.."
ffmpeg -y -i "$SRC" -map 0:v:0 -map 0:a:0 \
  -vf "zscale=tin=arib-std-b67:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=brightness=0.03:contrast=1.10:saturation=1.25:gamma=1.05,colorbalance=rm=-0.02:bm=0.02,scale=1080:1920:flags=lanczos,fps=30" \
  -c:v libx264 -preset medium -crf 17 -g 15 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -af "highpass=f=90,afftdn=nf=-30:nr=10,acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3dB,loudnorm=I=-16:TP=-1.5:LRA=9" \
  -ar 48000 -c:a aac -b:a 256k -movflags +faststart assets/footage.mp4
ffmpeg -y -i assets/footage.mp4 -vn -c:a pcm_s16le -ar 48000 assets/voice.wav
