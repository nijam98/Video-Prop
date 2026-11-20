# Teres End Lot, Taman Belimbing — reel (HyperFrames)

Video menegak 1080×1920 (65.3 s) diedit daripada walkthrough 92.6 s (iPhone, HLG HDR 1080×1920 59.94fps), dibina dengan HyperFrames.

- **Rupa: "Editorial Glass"** — subtitle serif besar gaya kulit majalah (Instrument Serif; kata kunci italik terakota)
  yang duduk **di belakang orang**: matte orang (RobustVideoMatting → `assets/person.webm`, VP9 + alpha) diletak atas
  lapisan subtitle, jadi presenter berdiri di depan perkataan. Point penting dalam kad kaca frosted (backdrop blur)
  dengan label Manrope, chip ✓, cetakan foto kecil yang diambil dari video sendiri (taman permainan, Eco Park,
  bilik-bilik, dapur, L-box), tag bab gaya indeks majalah (01 Luar rumah … 11 Pembiayaan), dan sapuan kaca kabur
  pada potongan besar. Tiada kartun: gerakan expo ease, tiada boil / sticker / doodle.
  Palet: dakwat hijau #13241D, terakota #A63F22, pasir #EFE6D6, krim #FBF7F0, butang biru #1D6BF3.
- **Hook:** "Yang mana nak cari rumah open facing? Ada satu ni, teres end lot" + terus "freehold, non-bumi lot"
  (asal pada 9 s, dibawa ke depan) — tiga point jualan terkuat dalam 6 saat pertama.
- **Dibuang:** semua "okey", "and then", "jom kita masuk tengok dalam", "ruang tamu ni ZZ … privacy" (tak jelas),
  "sekarang kita masuk master bedroom" (diulang), "master bedroom ni petok built-in" (tak jelas),
  "bilik kedua" (ulang), "dapur owner pergi semua / macam mana tengok macam tu dapat?" (tak jelas),
  "ruang laundry letak macam-macam" (ulang), "orang tu" (tak jelas), "terima kasih kerana menonton", dan semua jeda.
  Gambar "3 bilik dan 2 tandas" diganti dengan syot ruang tamu; gambar "sini pula dapur" diganti dengan syot dapur.
- **Safe zone:** lulus `hyperframes check --safe-zone tiktok` dan `--safe-zone reels` (tiada amaran safe zone):
  teks dalam x 128–888, kad dalam y 940–1240 dan x ≤ 780, tag bab y ≈ 296.
- **Audio:** suara dibersihkan (-15 LUFS) dengan fade pada setiap potongan; SFX lembut (klik UI, shutter kamera,
  sweep, chime) pra-normal -20 LUFS pada gain 0.08–0.30; muzik deep house "Deep Urban" diduck bawah suara, naik pada end card.

## Bina semula

```bash
tools/prepare-footage.sh /path/to/original.MOV                 # HLG HDR -> SDR footage + suara bersih (tidak dalam git)
python3 tools/matte.py /path/to/rvm_mobilenetv3_fp32.torchscript  # matte orang -> assets/person.webm (~20 min CPU)
python3 tools/person_boxes.py                                  # kedudukan kepala presenter per segmen
python3 tools/build.py                                         # jana index.html + compositions/*
npx hyperframes@0.9.63 check --safe-zone tiktok
npx hyperframes@0.9.63 check --safe-zone reels
npx hyperframes@0.9.63 render -q draft -f 30 -o renders/preview-draft.mp4   # preview
npx hyperframes@0.9.63 render -q high -f 60 -o renders/teres-belimbing.mp4  # final
```

Model RVM: https://github.com/PeterL1n/RobustVideoMatting/releases (v1.0.0, `rvm_mobilenetv3_fp32.torchscript`).
Perlu `pip install torch scipy numpy`. Semua masa (EDL, caption, kad, SFX, kamera) ada dalam jadual di atas `tools/build.py`.

Rupa yang dah digunakan (elak lain kali): Bauhaus, kinetic type, Y2K, art deco, holographic, split-flap, paper cut-out,
stick-figure comic, pop-art halftone comic, architect's sketchbook, crayon & oil pastel, street spray / graffiti,
ink brush & chop seal, site notes, dan sekarang **editorial glass (subtitle di belakang orang)**.
