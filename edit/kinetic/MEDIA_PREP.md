# Rebuilding footage and audio (footage not in git)

From IMG_0374.MOV (iPhone 17 Pro, 4K HLG, 46.7 s):
1. Tone-map HLG -> SDR and scale to 1080x1920 60fps:
   `ffmpeg -i IMG_0374.MOV -map 0:v:0 -map 0:a:0 -vf "zscale=w=1080:h=1920:f=lanczos:tin=arib-std-b67:min=bt2020nc:pin=bt2020:t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=mobius:param=0.3:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p,eq=contrast=1.08:gamma=0.95:saturation=1.06,fps=60" -c:v libx264 -crf 12 -g 30 -c:a pcm_s16le -ar 48000 -ac 1 base1080.mov`
2. `python3 tools_cut.py base1080.mov assets/footage.mp4 voice_raw.wav` (cut list inside; hook "bebas banjir" moved to the front, CTA to the end)
3. voice: `highpass=f=90:poles=2,afftdn=nr=10:nf=-45:tn=1,equalizer=f=250:t=q:w=1:g=-2.5,equalizer=f=3200:t=q:w=0.9:g=3,deesser=i=0.3,acompressor=threshold=-24dB:ratio=2.5:attack=8:release=160:knee=6:makeup=1,loudnorm=I=-16:TP=-1.5:LRA=9` -> assets/voice.wav
4. music: "Bring back tha funk" from 48.0 s, 30.2 s, fade in 0.25 s / out 1.5 s -> assets/music.mp3
5. `python3 build.py`, then `npx hyperframes render --fps 60 --sdr`
