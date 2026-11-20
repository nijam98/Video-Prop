# rumah-luxe — rumah teres 2 tingkat, "Galeri Linen"

HyperFrames edit of the show-unit walk-through (1080x1920, 30 fps, 56 s). Look and decisions: `../DESIGN_LOG.md`.

## Rebuild the media (footage is not in git, 114 MB)
Source: the 576x1024 phone video from Google Drive (`src.mp4`).
1. `python3 tools/cut.py src.mp4` → `assets/footage.mp4` (cut, lanczos to 1080x1920, light sharpen) + `work/voice_cut.wav`.
   The cut lives in `tools/edl.json` (hook flash-forward + 27 segments); `tools/cutmap.json` maps source → film time.
2. Voice: `ffmpeg -i work/voice_cut.wav -af "highpass=f=85,afftdn=nf=-30,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1:g=2,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=3,loudnorm=I=-16:TP=-1.5:LRA=7" -ar 48000 -ac 1 assets/voice.wav`
3. Music: Mixkit "Hazy After Hours" (track 132) from 63.515 s, 56.6 s long, loudnorm -16 → `assets/music.mp3`.
4. Photos: `python3 tools/stills.py realesr-general-x4v3.pth src.mp4` (Real-ESRGAN x4, 4:5 crops) → `assets/photos/`.

## Edit
- Shared styles/motion: `tools/common.css`, `tools/common.js` → `python3 tools/build.py` inlines them into every scene.
- Captions: edit groups in `tools/captions.py`, then run it.
- `npx hyperframes check`, `npx hyperframes snapshot --at …`, `npx hyperframes render --quality delivery`.

## Credits
Music and SFX: Mixkit (Mixkit free licence, no attribution required). Fonts: Cormorant Garamond, Manrope (SIL OFL).
