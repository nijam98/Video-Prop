# Design log

## Rumah fully renovated, Kulim — "Pop-Art Komik" (Nov 2026)
- Source: video POV house tour 67 s (1080×1920 HEVC 30fps, voiceover, no face)
- Project: `edit/komik` (HyperFrames). Rebuild: `tools/cut.py` → `tools/audio.sh` → `build.py`.
- Look: silver-age pop-art comic — Ben-Day halftone dots, CMYK inks (cyan #00B4EF, magenta #FF2D8A,
  yellow #FFE500, ink #111, paper #FFF6DE), jagged starbursts, speed lines, yellow narration boxes,
  misregistered cyan print shadow on lettering, comic-panel frame on hook + end card.
- Type: Bangers (lettering) + Comic Neue Bold (narration boxes).
- Motion: Remotion-style springs (custom spring ease), slot-machine odometer counters, checklist springs,
  progress bars. Transitions: 3-strip skewed halftone panel wipes (Y/M/C) on 4 big cuts; punch-ins on the rest.
- Safe zone: words inside x 72–900, y 240–1300.
- Music: "D-Funk Express" — Doctor Frost (Jamendo, CC BY 3.0), ~117 BPM, side-chained under the voice (~13 dB below).
- SFX: Freesound (CC0 / CC BY) via Openverse — punch, whooshes, page flip, pop, ding, ka-ching, riser, keys.

Previous looks to avoid next time: Bauhaus, kinetic type, Y2K, art deco, holographic, split-flap,
paper cut-out, hand-drawn stick-figure comic, and now pop-art halftone comic.
