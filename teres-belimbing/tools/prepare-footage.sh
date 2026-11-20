#!/usr/bin/env bash
# Rebuilds assets/footage.mp4 + assets/voice.wav from the original iPhone clip (HLG HDR, 1080x1920 HEVC 59.94fps, 92.6 s).
# Usage: tools/prepare-footage.sh /path/to/original.MOV
set -euo pipefail
SRC="$1"; cd "$(dirname "$0")/.."
ffmpeg -y -i "$SRC" -map 0:v:0 -an \
  -vf "zscale=tin=arib-std-b67:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=brightness=0.02:contrast=1.10:saturation=1.18:gamma=1.04,unsharp=5:5:0.45" \
  -r 60 -c:v libx264 -preset medium -crf 15 -g 30 -pix_fmt yuv420p -color_primaries bt709 -color_trc bt709 -colorspace bt709 \
  -movflags +faststart assets/footage.mp4
ffmpeg -y -i "$SRC" -map 0:a:0 -ac 1 \
  -af "highpass=f=85,afftdn=nf=-28:nr=12,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3500:t=q:w=1:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=5:release=120:makeup=4dB,loudnorm=I=-15:TP=-1.5:LRA=7" \
  -ar 48000 -c:a pcm_s16le assets/voice.wav
