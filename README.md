# Autopost Affiliate Shopee → Facebook & Threads

Sistem ini pos produk affiliate Shopee secara automatik ke **Facebook Page** dan **Threads** mengikut jadual (contoh: 9 pagi, 1 tengah hari, 8 malam).

- ✅ Guna **API rasmi Meta**, bukan bot browser, jadi akaun lebih selamat
- ✅ Kapsyen **berubah-ubah** (template + hook rawak) supaya tidak nampak spam
- ✅ Link affiliate boleh diletak dalam **komen pertama** (FB) atau **reply** (Threads)
- ✅ Produk dipusing secara adil: yang belum pernah dipos didahulukan, ada tempoh cooldown
- ✅ Jalan **percuma di GitHub Actions** (tak perlu server), atau di PC/VPS sendiri
- ✅ (Pilihan) Shopee Affiliate Open API: import produk ikut kata kunci + short link dengan `sub_id` untuk jejak klik FB vs Threads

> ⚠️ Meta **tidak benarkan** pos automatik ke **profil peribadi** Facebook. Anda perlukan **Facebook Page**.

---

## 1. Pasang

```bash
git clone <repo-ini>
cd Video-Prop
pip install -r requirements.txt
cp .env.example .env
```

## 2. Masukkan produk — `data/products.csv`

| Lajur | Wajib | Keterangan |
|---|---|---|
| `id` | ✅ | ID unik (apa-apa, cth `kipas-01`) |
| `name` | ✅ | Nama produk |
| `affiliate_link` | ✅ | Link affiliate dari Shopee Affiliate (cth `https://s.shopee.com.my/xxxx`) |
| `price` | | Harga sekarang (cth `12.50`) |
| `original_price` | | Harga asal, untuk kira % diskaun |
| `image_url` | | URL gambar **awam** (gambar produk Shopee boleh dipakai). Kalau kosong, sistem buat pos teks + link |
| `hashtags` | | cth `#gadget #murah` |
| `caption` | | Kapsyen khas (pilihan). Boleh guna `{name} {price} {link} {hashtags}`, dan `\n` untuk baris baru |
| `active` | | `1` = pos, `0` = jangan pos |

> Fail ini ada **3 produk contoh**. Padam dan ganti dengan produk sebenar. Sistem akan menolak pos sebenar selagi link contoh masih ada.

**Cara dapat link affiliate:** buka [affiliate.shopee.com.my](https://affiliate.shopee.com.my) → *Custom Link* / *Product Offer* → salin link.
**Gambar:** buka produk di Shopee (versi web) → klik kanan gambar → *Copy image address*.

## 3. Ubah gaya kapsyen — `data/templates.json`

- `hooks` = ayat pembuka rawak
- `templates` = format kapsyen. Placeholder: `{hook} {name} {price} {original_price} {discount} {link} {hashtags}`
  Baris yang placeholdernya kosong (cth tiada harga asal) **dibuang automatik**.
- `cta_link_elsewhere` = ayat bila link diletak dalam komen/reply
- `default_hashtags` = hashtag kalau produk tiada hashtag sendiri

Lihat contoh hasil tanpa pos apa-apa:

```bash
python -m autopost preview -n 5
```

---

## 4. Dapatkan token Facebook Page

1. Pergi ke [developers.facebook.com](https://developers.facebook.com/apps) → **Create App** → pilih use case **"Manage everything on your Page"**.
2. Buka **[Graph API Explorer](https://developers.facebook.com/tools/explorer/)** → pilih app anda → **Get User Access Token** dengan permission:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `pages_manage_engagement` (untuk komen link)
3. Panjangkan token: buka **[Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)** → tampal token → **Extend Access Token**.
4. Kembali ke Graph API Explorer, guna token yang dipanjangkan tadi dan jalankan `GET me/accounts`.
   Cari Page anda. Salin:
   - `id` → `FB_PAGE_ID`
   - `access_token` → `FB_PAGE_ACCESS_TOKEN` (token Page dari user token yang dipanjangkan **tidak luput**)

## 5. Dapatkan token Threads

1. Dalam app yang sama (atau app baru), **Add use case** → **"Access the Threads API"**.
2. Dalam use case itu, aktifkan permission `threads_basic` dan `threads_content_publish`.
3. **App roles → Roles → Add People → Threads Tester** → masukkan username Threads anda.
   Kemudian dalam app Threads: **Settings → Account → Website permissions → Invites** → Accept.
4. Dalam tetapan use case Threads, guna **User Token Generator** untuk jana token → `THREADS_ACCESS_TOKEN`.
   (`THREADS_USER_ID` boleh dibiarkan `me`.)
5. Token Threads sah **60 hari**. Sebelum luput, jalankan:
   ```bash
   python -m autopost refresh-threads-token
   ```
   dan gantikan nilai lama dengan token baru.

## 6. Uji

```bash
python -m autopost check            # semak token
python -m autopost run --dry-run    # lihat apa yang akan dipos
python -m autopost run              # pos SATU produk sekarang
```

---

## 7. Jalankan secara automatik

### Pilihan A: GitHub Actions (percuma, tak perlu PC hidup) ⭐

1. Push repo ini ke GitHub. Fail `.github/workflows/autopost.yml` mesti berada dalam **branch utama (default)**, kerana jadual hanya jalan dari branch itu.
2. Repo → **Settings → Secrets and variables → Actions → New repository secret**, tambah:
   - `FB_PAGE_ID`, `FB_PAGE_ACCESS_TOKEN`
   - `THREADS_USER_ID` (isi `me`), `THREADS_ACCESS_TOKEN`
   - (pilihan) `SHOPEE_APP_ID`, `SHOPEE_APP_SECRET`
3. (Pilihan) Tab **Variables**: `FB_LINK_IN_COMMENT`, `THREADS_LINK_IN_REPLY`, `FB_ENABLED`, `THREADS_ENABLED`.
4. Tab **Actions** → *Autopost Shopee Affiliate* → **Run workflow** untuk uji.

Jadual asal: 09:00, 13:00 dan 20:00 waktu Malaysia. Untuk tukar, edit baris `cron` (waktu **UTC** = waktu Malaysia − 8 jam).
Nota: GitHub kadang lewat 5–30 minit semasa sibuk.

Rekod produk yang sudah dipos (`data/state.json`) di-commit semula secara automatik.
**Kalau repo public**, sesiapa boleh lihat senarai produk anda. Token tetap selamat dalam Secrets.

### Pilihan B: PC / VPS sendiri

```bash
python -m autopost daemon
```

Ia pos pada setiap waktu dalam `POST_TIMES` (ikut `TIMEZONE`). Untuk VPS, jalankan dengan `tmux`, `screen` atau `systemd`.

Atau guna cron Linux:
```cron
0 9,13,20 * * * cd /path/Video-Prop && python3 -m autopost run >> logs/autopost.log 2>&1
```

---

## 8. (Pilihan) Shopee Affiliate Open API

Jika anda ada akses Open API (mohon di portal Shopee Affiliate), isi `SHOPEE_APP_ID` dan `SHOPEE_APP_SECRET`, kemudian:

```bash
# Import 20 produk paling laris untuk kata kunci "kipas mini"
python -m autopost import-shopee --keyword "kipas mini" --limit 20 --hashtags "#kipasmini #gadget"
# --sort: 1=relevan 2=jualan 3=harga tinggi 4=harga rendah 5=komisen tertinggi
```

Bila API diset, setiap link yang **belum** berbentuk short link akan ditukar automatik kepada short link dengan `sub_id` `facebook` atau `threads`. Jadi dalam laporan Shopee Affiliate anda boleh nampak platform mana yang lebih banyak jualan.

> Medan API Shopee boleh berubah. Kalau `import-shopee` keluarkan ralat, semak dokumentasi Open API dalam portal affiliate anda.

---

## Tips supaya akaun tidak disekat

- Jangan pos terlalu kerap. **2–4 pos sehari** sudah memadai.
- Tambah banyak template dan hook dalam `templates.json` supaya kapsyen tidak berulang.
- Biarkan `FB_LINK_IN_COMMENT=true`. Pos yang ada link luar dalam kapsyen biasanya dapat reach lebih rendah.
- Selit juga kandungan bukan jualan secara manual (tips, review, soalan) supaya Page nampak hidup.
- Patuhi terma Shopee Affiliate. Jangan buat dakwaan palsu tentang harga atau produk.

## Struktur projek

```
autopost/
  __main__.py   CLI (run, daemon, preview, check, refresh-threads-token, import-shopee)
  runner.py     logik utama & penjadual
  facebook.py   Facebook Graph API (Page)
  threads.py    Threads API
  shopee.py     Shopee Affiliate Open API (pilihan)
  captions.py   penjana kapsyen
  products.py   baca CSV & pilih produk
  state.py      rekod pos
data/
  products.csv  senarai produk anda
  templates.json gaya kapsyen
tests/          ujian (python -m pytest)
```
