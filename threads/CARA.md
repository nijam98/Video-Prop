# Auto-post Threads — Cara Ia Berfungsi

5 kali sehari (waktu Malaysia: 08:00, 12:00, 15:00, 18:00, 21:00) tugasan berjadual akan:
1. Baca `GAYA.md`, `idea.md`, `listing.md` dan log hari ini dalam `log/`.
2. Pilih idea `[ ]` yang sesuai dengan slot.
3. Tulis post (hook padu, ≤ 450 aksara), simpan ke fail sementara.
4. `python3 threads/post.py --file <fail>` untuk terbitkan.
5. Tanda idea `[x]` dalam `idea.md`, tambah ke `log/YYYY-MM-DD.md`, commit & push.

Nak tambah idea? Tambah baris `- [ ] ...` dalam `idea.md`.
Nak tambah listing? Isi `listing.md`.

## Post cari penjual (owner jual rumah & rumah busuk)

1 kali sehari, 10:00 waktu Malaysia, ke Threads **dan** Facebook Page:
1. Baca `cari-penjual.md` dan `profil.md` (berhenti jika `profil.md` belum lengkap).
2. Pilih sudut seterusnya (lihat log untuk elak ulang), tulis post.
3. `python3 threads/post.py --file <fail>` (Threads) dan `python3 threads/fb_post.py --file <fail>` (Facebook Page).
4. Catat dalam `log/YYYY-MM-DD.md` (slot `10:00-penjual`), commit & push.
