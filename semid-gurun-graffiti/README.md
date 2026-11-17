# Semi-D Gurun — "Street Spray" reel (HyperFrames)

Video menegak 1080×1920 (44.3 s) diedit daripada walkthrough 72.7 s (iPhone, 4K HLG HDR 60fps), dibina dengan HyperFrames.

- **Rupa: "Street Spray / Graffiti"** — tag cat sembur (Sedgwick Ave Display) dengan kabus overspray & titisan cat
  yang meleleh, nombor stensil (Rubik Spray Paint), caption gaya *slap sticker* (Archivo Black) dengan penanda
  hijau lime pada perkataan yang sedang disebut, anak panah / mahkota / bintang / tanda ✓ yang "disembur" tangan
  (SVG + "boil" 12fps), lap peralihan cat sembur 4 warna. Palet: pink #FF2E88, lime #C6FF1A, cyan #1EE3FF,
  oren #FF7A00, kuning #FFD400, ungu #8B3DFF, dakwat #141414.
- **Hook:** "Mana nak cari tau? Rumah semi-D cluster macam ni, harga RM281K sahaja selepas rebate" (asal pada 55 s) dibawa ke depan,
  diikuti "Tengok, lawa tak lawa? Tak kena dengan harga dia… harga murah-murah ni".
- **Dibuang:** nama taman (tak jelas), "tanah belakang takda" (bercanggah), "sliding" berulang, "tingkat satu / door bedroom in"
  (tak jelas), "boleh buat … sekali" (tak jelas), "ruang dapur" berulang, "sini tanah tepi" kali kedua, "tuan-tuan dan puan-puan",
  dan semua jeda.
- **Safe zone:** lulus `hyperframes check --safe-zone tiktok` dan `--safe-zone reels` (tiada amaran).
- **Audio:** suara dibersihkan (-15 LUFS), SFX -20 LUFS pada 0.12–0.40 gain, muzik boom-bap diduck bawah suara, naik pada end card. Mix ≈ -15 LUFS.

## Bina semula

```bash
tools/prepare-footage.sh /path/to/original.MOV   # HDR -> SDR footage + suara bersih (tidak dalam git)
python3 tools/build.py                           # jana index.html + compositions/*
npx hyperframes@0.9.63 check --safe-zone tiktok
npx hyperframes@0.9.63 check --safe-zone reels
npx hyperframes@0.9.63 render -q draft -f 30 -o renders/preview-draft.mp4     # preview
npx hyperframes@0.9.63 render -q high -f 60 -o renders/semid-gurun-graffiti.mp4  # final
```

Semua masa (EDL, caption, SFX, kamera) ada dalam jadual di atas `tools/build.py`. Transkrip Whisper asal: `tools/transcript-source.json`.

Rupa yang dah digunakan (elak lain kali): Bauhaus, kinetic type, Y2K, art deco, holographic, split-flap, paper cut-out,
stick-figure comic, pop-art halftone comic, architect's sketchbook, crayon & oil pastel, dan sekarang **street spray / graffiti**.

## Render final
- `renders/semid-gurun-graffiti-upload.mp4` — 1080×1920, 60fps, H.264 high, 15 Mbps, AAC, -15.2 LUFS, 44.3 s (87 MB, sedia upload TikTok / IG).
  Master penuh (176 MB, `-q high`) tidak disimpan dalam git kerana melebihi had 100 MB GitHub.
