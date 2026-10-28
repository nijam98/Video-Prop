# Review — Semi-D Taman Pulasan, Jitra (TikTok/IG 9:16)

## Source & cleanup
- Source: iPhone HLG/Dolby Vision 1080×1920 59.94 fps, 97.7 s. Converted to SDR BT.709 (mobius tone-map) at 30 fps.
- Removed: the burned-in 5-line caption ("CCC DAH DAPAT … TANAH BELAKANG 25FT") on every frame, using a
  pixel-exact mask (temporal std of the static overlay) + LaMa inpainting per frame.
- Removed: the "TV rosak" colour-bar clip (4.07–5.07 s) and its 1 kHz test-tone beep.

## Edit (97.7 s → 69.9 s)
- Hook: "Semi-D … tanah belakang 25 kaki" + pulled forward "Dan yang paling rare, semi-D ada jalan rizab belakang".
- Cut: pauses over ~0.2 s, "Alright, jom kita masuk ruang tamu" (repeat of the next line), first "ruang makan dengan
  ruang dapur" (said again later), "Ada rizab jalan" (repeat), "yang mana berminat nak cari semi-D" (repeat of CTA),
  "Dan yang paling rare" in the backyard (used as hook).
- Every jump cut is hidden with a hard punch-in (scale 1.0 ↔ 1.04–1.14).

## Look: "Spec sheet"
Ink navy cards, signal orange, Archivo Black + JetBrains Mono; numbered room index (01 PORCH … 08 DAPUR) that
slot-rolls; architect dimension lines for "25 KAKI"; top-down plan diagram explaining the road reserve.
Four diagonal ink/orange wipes on chapter changes. All copy inside 236–1240 px (TikTok/IG safe band), left side.

## Sound
- Voice (v2, "bagi clear"): double HPF 105 Hz, denoise, −4.5 dB at 260 Hz (room mud), +4.5 dB at 3 kHz and +2 dB at 5.5 kHz (presence), de-esser, light expander for empty-room echo, 3.5:1 comp, −15 LUFS. Low band −5 dB, 2–8 kHz +6–7 dB vs raw.
- Music: "Hustle" — Kevin MacLeod (incompetech.com), CC BY 4.0. Credit required in the post caption.
  Joined intro + real ending on the bar; voice band carved out of the music (−4 dB 1.5 kHz, −3 dB 3.2 kHz), side-chain ducked 7:1, bed ~18 dB under the voice.
- SFX: Pixabay licence (bundled HyperFrames library), each placed so its peak lands 1 frame after its visual.
- Measured, not heard.

## Not shown on purpose
- Price ("Semi-D bawah …") — the transcript is unclear, so no number is printed.
- "Beg biru" in the CTA is unclear; the CTA says "WHATSAPP TERUS" only.

## v2 animation pass
Render-time motion blur; letter/word-level entrances; light sweeps on cards; zoom-through camera transitions between rooms;
3-band wipes; star burst + camera kick on "PALING RARE"; car driving the road reserve (hook + plan view); shockwave on
"25 KAKI"; tour progress bar under the room tag; route line linking location stops; CTA letters roll in, button sheen + arrow nudge.
