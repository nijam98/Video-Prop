# Video-Prop — Naz Property: "Formula Gaji × 12 × 10"

Video iklan menegak (TikTok / Reels / Shorts) gaya **hologram + lukisan tangan**.

- Output: `out/naz-property-formula-gaji-1080x1920.mp4`
- 1080×1920 (Full HD menegak), 30fps, H.264 high, audio AAC 192k, -14 LUFS
- Durasi 64 saat (ikut panjang suara latar asal)

## Storyboard (ikut masa suara latar)

| Masa | Visual | Efek bunyi |
|---|---|---|
| 0–10.6s | Zoom laju dari slip gaji RM2,500 → lelaki terkejut pandang rumah idaman, tanda "?" & cop "TAK CUKUP?", jam hologram "10 SAAT" | Whoosh + BOOM, pop |
| 10.6–20.1s | Holo-kalkulator: GAJI KASAR × 12 × 10 = HARGA RUMAH, butang ditekan ikut suara, nombor terbang, jam undur 10→0 | Bunyi digital, blip, ding |
| 20.1–35.1s | RM2,500 → RM30,000 → **RM300,000**, rumah 3D naik dari bawah (wireframe hologram → lukisan tangan), confetti & syiling | Ka-ching, BOOM, confetti |
| 35.1–51.3s | Record scratch (rewind), lampu siren merah, pegawai bank angkat kad AMARAN "RM300K ≠ LULUS", ikon Hutang Kereta / Kad Kredit / DSR / Bayaran Bulanan → "GAJI KECIL ~~TAK MAMPU?~~ BOLEH BELI RUMAH!" | Record scratch, alarm, pop, chime |
| 51.3–64s | Logo Naz Property, rumah 3D berputar, watak tunjuk ke bawah (borang / link di bio), butang CTA berdenyut "SEMAK KELAYAKAN PERCUMA!", lencana LPPSA · BANK · PENIAGA, "Bye bye" | Whoosh + CTA berdenyut |

Sari kata (Bahasa Melayu, loghat utara "hampa") dipaparkan sepanjang video dengan perkataan penting berwarna kuning.

## Bina semula

```bash
./build.sh        # perlukan node, python3 (numpy, scipy), ffmpeg, playwright chromium
```

- `tools/audio.py` — bersihkan suara latar, jana muzik + kesan bunyi, campur & normalise
- `src/scene.js` — semua animasi (rough.js untuk garisan lukisan tangan, canvas glow untuk hologram)
- `tools/render.js` — render frame dengan Chromium → ffmpeg (`node tools/render.js stills 1,12,27` untuk semak frame)

Logo "Naz Property" dilukis sebagai placeholder — boleh ganti dengan fail logo sebenar.
