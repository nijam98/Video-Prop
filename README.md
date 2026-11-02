# Rumah Utara

Laman carian rumah di Kedah dan Perlis (Alor Setar, Jitra, Changlun, Sungai Petani, Gurun, Perlis) mengikut 5 pilihan bajet.

- `src/page.html` ialah fail sumber. Ia juga laman yang diterbitkan di claude.ai.
- `index.html` dijana daripada `src/page.html`: `python3 scripts/build.py src/page.html index.html`
- Senarai rumah disimpan dalam `<script id="ru-data">` di dalam laman. Pemilik menambah, mengedit atau memadam rumah melalui "Mod pemilik" di laman claude.ai. Gambar disimpan sebagai aset laman tersebut.
- Nombor WhatsApp ejen: `AGENT_PHONE` dalam `src/page.html`.
