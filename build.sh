#!/usr/bin/env bash
# Build the Naz Property video: audio -> frames -> final mp4 (1080x1920, 30fps)
set -euo pipefail
cd "$(dirname "$0")"
[ -d node_modules ] || npm install
python3 tools/audio.py
node tools/render.js video "${1:-4}"
mkdir -p out
ffmpeg -v error -y -i build/video.mp4 -i build/mix.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -shortest -movflags +faststart out/naz-property-formula-gaji-1080x1920.mp4
echo "done -> out/naz-property-formula-gaji-1080x1920.mp4"
