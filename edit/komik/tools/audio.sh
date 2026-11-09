#!/usr/bin/env bash
# Clean the voice and build a ducked music bed.  Run after tools/cut.py.
set -euo pipefail
cd "$(dirname "$0")/.."
# Voice: rumble cut, light denoise, de-mud, presence, gentle compression, -16 LUFS
ffmpeg -v error -y -i build/voice_raw.wav -af "highpass=f=85,afftdn=nf=-28:nr=10,equalizer=f=250:t=q:w=1.2:g=-2.5,equalizer=f=3200:t=q:w=1.0:g=2.5,equalizer=f=7500:t=q:w=1.5:g=-1.5,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=2,loudnorm=I=-16:TP=-1.5:LRA=7,aresample=48000" -ar 48000 -ac 1 -c:a pcm_s16le assets/voice.wav
# Music: "D-Funk Express" from its first strong bar (8.09 s), 60 s, side-chained under the voice
ffmpeg -v error -y -ss 8.09 -t 60 -i build/music_src.mp3 -i assets/voice.wav -filter_complex \
 "[0:a]aformat=sample_rates=48000:channel_layouts=stereo,highpass=f=40,equalizer=f=2800:t=q:w=1.4:g=-4,loudnorm=I=-18:TP=-2,aresample=48000,afade=t=in:d=0.05,afade=t=out:st=57.6:d=2.4[m];[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=2.5[sc];[m][sc]sidechaincompress=threshold=0.06:ratio=3:attack=30:release=400:makeup=1[out]" \
 -map "[out]" -c:a pcm_s16le build/music_ducked.wav
ffmpeg -v error -y -i build/music_ducked.wav -c:a libmp3lame -b:a 256k assets/music.mp3
