# Rebuilding footage (not in git, 133 MB)

From IMG_0377.MOV (iPhone 4K HLG):
1. `ffmpeg -i IMG_0377.MOV -map 0:v:0 -map 0:a:0 -vf "scale=1080:1920:flags=lanczos,fps=60,eq=contrast=1.07:saturation=1.15:gamma=0.97,format=yuv420p" -c:v libx264 -crf 12 -g 30 -c:a pcm_s16le -ar 48000 -ac 1 base1080.mov`
2. `python3 tools_cut.py base1080.mov cut_v.mp4 voice_raw.wav` (segment list inside)
3. Append source 21.62–22.58 s (video only) to cut_v.mp4 → assets/footage.mp4 (25.6 s)
4. voice: highpass 80, afftdn, EQ, compressor, loudnorm -16 → assets/voice.wav
5. music: Retro Freak Dance from 60.30 s, 25.8 s, fades → assets/music.mp3
