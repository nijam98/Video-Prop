# Y2K property reel (Evoke Kondominium Permata Pauh)

Same brief as the hand-drawn version (60s, 1080x1920, 60fps, boring parts cut, strong hook),
but the footage stays clean and sharp and the animation is Y2K motion graphics on top.

- `edit.py` – cut list. Hook = 4 fast "money shots" (chandelier, LED ceiling, feature wall,
  glossy living room) under "macam mana tengok, macam tu dapat, masuk cuci kaki". The blurry balcony
  pan (21–26s in the source) is left out. Writes `work/cut30.mkv`, `work/audio60.wav`, `work/edl.json`.
- `sr_pass.py` / `sr.py` – AI upscale with Real-ESRGAN **general-x4v3** (for real photos; keeps texture
  natural) 478x850 → 1080x1920, then 30→60fps motion interpolation at full 1080 so in-between frames stay sharp.
- `style.py` – light grade: lights keep their glow, a bit more punch, cool shadows / soft pink highlights, light sharpen.
- `gfx.py` – Y2K graphics: chrome + gold chrome text with shine sweep, holographic text, glossy gel pills,
  Win9x pop-up windows with typing text, sparkles, pixel cursor, segmented loading bar.
- `render.py` – animation + compositing: chrome slams with sparkle bursts, pills sliding in, windows popping
  with typewriter text, CRT power-on, flash + RGB-split glitch on cuts, zoom punches.
- `sfx.py` – light synthesized Y2K sounds (shing, blip, ding, whoosh) under the voice → `work/audio_mix.wav`.

Needs ffmpeg, `pip install opencv-python-headless pillow numpy` and CPU `torch`.
Weights in `models/` (realesr-general-x4v3.pth from the Real-ESRGAN v0.2.5.0 release).
Fonts in `fonts/` (Google Fonts): RubikMonoOne, Audiowide, PressStart2P.
Source video in `dl/src.mp4`, mono 16k audio in `dl/audio.wav`.

Run from the work folder:
```
python3 y2k/edit.py
python3 y2k/sr_pass.py work/cut30.mkv work/cut60_sr.mp4          # ~80 min on 4 CPUs
FONTS=fonts python3 y2k/sfx.py
FONTS=fonts python3 y2k/render.py                                 # -> work/final.mp4
```
Preview: `python3 y2k/sr_pass.py work/cut30.mkv work/prev_sr.mp4 390` then
`SRC_VID=work/prev_sr.mp4 FONTS=fonts python3 y2k/render.py 780 work/preview.mp4`.
