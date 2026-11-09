# Rumah Fully Renovated, Kulim — edit "Pop-Art Komik" (HyperFrames)

Video menegak 1080×1920 (Full HD), 60 fps, 60 s, untuk TikTok / IG Reels.

- Fail akhir: `renders/Kulim_Komik_1080p60_final_upload.mp4` (H.264 High, AAC 48 kHz, -15.7 LUFS)
- Render semula: `npx --yes hyperframes@0.8.210 render -q delivery -f 60 --resolution portrait -o renders/Kulim_Komik_1080p60_final.mp4`

## Cara bina semula

```bash
python3 tools/cut.py /path/ke/video_asal.mov   # potong video + suara -> assets/footage.mp4, build/voice_raw.wav
./tools/audio.sh                               # bersihkan suara (-16 LUFS), muzik di-duck bawah suara
python3 build.py                               # jana index.html + compositions/*.html
npx --yes hyperframes@0.8.210 check            # lint + layout
npx --yes hyperframes@0.8.210 render -q draft -f 30 -o renders/PREVIEW_draft.mp4   # preview
```

`assets/footage.mp4` (131 MB) tidak disimpan dalam git — jana semula dengan `tools/cut.py`.

## Suntingan (ikut transcript)

| Masa | Isi | Grafik |
|---|---|---|
| 0.0–4.4 | **Hook** (diambil dari hujung klip asal): "Nak cari rumah fully renovated dekat kawasan Kulim? Ini masanya, ini rumahnya" atas montaj 4 shot | Bingkai panel komik, tajuk, starburst KULIM?!, INI RUMAHNYA! |
| 4.4–7.6 | Kawasan, dekat semua kemudahan | Pin peta + kad KULIM, checklist |
| 7.6–17.2 | Fully renovated depan–belakang, cantik, plaster ceiling, lampu, grill | Starburst, bar progres depan→belakang, belon "CANTIK TAK?", checklist spring |
| 17.2–28.1 | Bilik utama, 3 bilik 2 tandas, freehold, non-bumi lot, semua boleh beli | Kotak narasi, kad statistik, cop FREEHOLD / NON-BUMI LOT |
| 28.1–45.5 | Bilik kedua, 1,194 sqft, ruang makan, dapur, tandas kedua, bilik ketiga | Odometer 1,194, kotak "panel #", checklist |
| 45.5–56.4 | RM370,000, tekan link, urusan loan A–Z | Odometer harga + KA-CHING!, butang TEKAN LINK, bar A→Z |
| 56.4–60.0 | End card | Ringkasan + harga |

Dibuang: ayat pembuka yang sama dengan hook, "KTC 1 / teres tingkat" (tak jelas), "ok," berulang, jeda senyap > 0.2 s.
