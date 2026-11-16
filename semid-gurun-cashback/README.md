# Semi-D Gurun "cashback" — reel (HyperFrames)

Vertical 1080×1920 reel (20.8 s) cut from a 24.8 s exterior clip (IMG_0890.MOV), built with HyperFrames.

- **Look: "Krayon & Oil Pastel"** — waxy crayon strokes with grain (SVG turbulence filter), hatched crayon fills,
  Gochi Hand lettering + Rubik Doodle Shadow numbers, 8 fps "boil" jitter, Remotion-style springs
  (pin drop, cashback gauge needle, checklist ticks, spec chips). Palette: sun #FFC83D, coral #FF6A4D,
  sky #4C9BFF, leaf #43C46B, lilac #A07CFF, plum ink #2B1E3F, cream #FFF6E6.
- **House first:** every graphic sits in the sky band (y 260–650) or the caption band; the house (y ≈ 620–1120) stays clear.
- **Safe zone:** passes `hyperframes check --safe-zone tiktok` and `--safe-zone reels`
  (captions x 116–780, bottom ≤ 1240; below y 840 nothing right of x 780).
- **Edit:** hook = "Harga bawah RM300 ribu, putus tali kasut tak jumpa dah" moved to the front.
  Cut: "macam biasa", unclear "yang berniaga ok", the repeated "nak tahu detail, isi saja", all pauses.
  "Cashback sangat tinggi" moved before "unit terhad"; CTA "isi maklumat kat bawah ni" ends the reel.
- **Cuts:** one continuous shot, so jump cuts are carried by camera moves (whip pans, punch-ins,
  zoom-through into the cashback beat) and the picture is taken from hand-free stretches of the clip.
- **Audio:** voice cleaned (-15 LUFS); every SFX pre-normalised to -20 LUFS and placed at 0.16–0.45 gain,
  so effects sit well under the voice; music bed ducked under speech, rises for the end card. Mix ≈ -14.9 LUFS.

## Rebuild

```bash
tools/prepare-footage.sh /path/to/IMG_0890.MOV   # HLG HDR -> SDR 1080x1920 60fps footage + cleaned voice (not in git)
python3 tools/build.py                           # regenerates index.html + compositions/*
npx hyperframes check --safe-zone tiktok
npx hyperframes render -q draft -f 30 -o renders/preview-draft.mp4    # preview
npx hyperframes render -q high -f 60 -o renders/semid-gurun-cashback.mp4  # final
```

All timings (cuts, captions, SFX, camera) live in the tables at the top of `tools/build.py`.

Previous looks to avoid next time: Bauhaus, kinetic type, Y2K, art deco, holographic, split-flap,
paper cut-out, stick-figure comic, pop-art halftone comic, architect's sketchbook, and now crayon & oil pastel.
