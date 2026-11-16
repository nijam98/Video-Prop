# Semi-D Gurun — reel (HyperFrames)

Vertical 1080×1920 reel (~52 s) edited from a 78 s walkthrough, built with HyperFrames.

- **Look:** "architect's sketchbook" — navy marker doodles drawn on the walls, torn-paper room tags with tape,
  yellow highlighter captions, paper-swipe / yellow scribble / whip / zoom-through transitions.
- **Safe zone:** every word sits inside the TikTok + Instagram Reels clear area (y 290–1248; x 120–888 above y 840, x 120–780 below).
- **Edit:** repeats and dead air removed (78 s → 50.2 s of speech), hook = "Semi-D paling murah dekat Gurun, RM281K" over the exterior at 2×.

## Rebuild

```bash
tools/prepare-footage.sh /path/to/original.MOV   # HLG HDR -> SDR 1080x1920 footage + cleaned voice (not in git)
python3 tools/build.py                           # regenerates index.html + compositions/*
npx hyperframes check --safe-zone tiktok
npx hyperframes render -q high -o renders/semid-gurun.mp4
```

All timings (cuts, captions, SFX, chapters) live in the tables at the top of `tools/build.py`.
Audio: Mixkit, see `assets/CREDITS.md`.
