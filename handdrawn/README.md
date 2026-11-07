# Hand-drawn property reel (Evoke Kondominium Permata Pauh)

Turns the walkthrough video into a 60s, 1080x1920, 60fps hand-drawn style reel.

- `edit.py` – cut list: hook first ("macam mana tengok, macam tu dapat, masuk cuci kaki"),
  boring parts removed, each clip interpolated to 60fps. Writes `work/cut60.mkv` + `work/audio60.wav`.
- `sr_pass.py` / `sr.py` – AI upscale (Real-ESRGAN animevideov3, bf16 on CPU) of the 478x850 cut to
  1080x1920 so the result is sharp, not blurry. Writes `work/cut60_sr.mp4`. Weights go in `models/`.
- `style.py` – hand-drawn look: ink edge lines with "boil", watercolor washes, pencil hatching in
  shadows, paper texture, and light glow kept from the original.
- `render.py` – stylizes every frame at 1080x1920, adds marker-style captions, encodes `work/final.mp4`.

Needs: ffmpeg, `pip install opencv-python-headless pillow numpy`, fonts in `fonts/`
(Permanent Marker from Google Fonts). Source video goes in `dl/src.mp4` (audio in `dl/audio.wav`).

Needs `torch` (CPU build) for the upscaler.

Run: `python3 edit.py && python3 sr_pass.py work/cut60.mkv work/cut60_sr.mp4 3600 && python3 render.py`
