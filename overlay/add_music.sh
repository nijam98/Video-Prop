#!/usr/bin/env bash
# Mix background music under the voice and remux (video stream is copied, not re-encoded).
# usage: add_music.sh <video.mp4> <music.mp3> <music_offset_s> <music_gain_db> <out.mp4>
# The music is ducked whenever the presenter talks, then the mix is normalised to -14 LUFS.
set -euo pipefail
IN=$1 MUSIC=$2 OFF=$3 GAIN=$4 OUT=$5
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$IN")
FO=$(python3 -c "print(max(0,$D-1.5))")
ffmpeg -v error -y -i "$IN" -ss "$OFF" -i "$MUSIC" -filter_complex "
  [0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,asplit=2[voice][key];
  [1:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,atrim=0:$D,asetpts=PTS-STARTPTS,
       volume=${GAIN}dB,afade=t=in:d=0.4,afade=t=out:st=$FO:d=1.5[m];
  [m][key]sidechaincompress=threshold=0.02:ratio=3:attack=25:release=500:knee=4[duck];
  [voice][duck]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.2:LRA=11,aresample=48000[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart "$OUT"
echo "music added -> $OUT"
