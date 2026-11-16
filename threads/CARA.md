# Auto-post Threads — Cara Ia Berfungsi

5 kali sehari (waktu Malaysia: 08:00, 12:00, 15:00, 18:00, 21:00) tugasan berjadual akan:
1. Baca `GAYA.md`, `idea.md`, `listing.md` dan log hari ini dalam `log/`.
2. Pilih idea `[ ]` yang sesuai dengan slot.
3. Tulis post (hook padu, ≤ 450 aksara), simpan ke fail sementara.
4. `python3 threads/post.py --file <fail>` untuk terbitkan.
5. Tanda idea `[x]` dalam `idea.md`, tambah ke `log/YYYY-MM-DD.md`, commit & push.

Nak tambah idea? Tambah baris `- [ ] ...` dalam `idea.md`.
Nak tambah listing? Isi `listing.md`.
