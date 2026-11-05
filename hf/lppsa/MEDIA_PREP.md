# Rebuilding the large media (not in git)

`assets/footage.mp4` and `assets/voice.wav` are made from the original `IMG_0376.MOV`:

```bash
# footage: 4K HLG -> 1080x1920 30fps, stabilised
ffmpeg -i IMG_0376.MOV -map 0:v:0 -vf "scale=1080:1920:flags=lanczos,fps=30,format=yuv420p" -c:v libx264 -crf 12 -an base1080.mp4
ffmpeg -i base1080.mp4 -vf vidstabdetect=shakiness=6:accuracy=12:result=transforms.trf -f null -
ffmpeg -i base1080.mp4 -vf "vidstabtransform=input=transforms.trf:smoothing=18:zoom=4:interpol=bicubic,unsharp=5:5:0.4" \
  -c:v libx264 -preset slow -crf 16 -g 30 -pix_fmt yuv420p -an -movflags +faststart assets/footage.mp4

# voice: light clean-up, mono 48 kHz
ffmpeg -i IMG_0376.MOV -map 0:a:0 -af "highpass=f=75,afftdn=nr=10:nf=-45:tn=1,aformat=sample_rates=48000:channel_layouts=mono" -c:a pcm_s16le assets/voice.wav
```
