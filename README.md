# Nazproperty – laman ringkas

Laman satu halaman (HTML statik) dengan 4 pilihan:

1. **Semak kelayakan loan**: borang (nama, gaji, komitmen, kawasan, telefon)
2. **Saya nak jual rumah / tanah**: borang (nama, jenis, lokasi, harga, telefon)
3. **Saya nak beli rumah**: borang (nama, kawasan, telefon)
4. **Kalkulator loan**: kira ansuran bulanan

Maklumat borang disimpan ke **Google Sheet** (lihat [google-sheet/PANDUAN.md](google-sheet/PANDUAN.md)). Jika `sheetUrl` kosong, borang dihantar ke email melalui [FormSubmit](https://formsubmit.co).

## Tetapan

Buka `index.html` dan cari bahagian `CONFIG` di dalam `<script>`:

```js
const CONFIG = {
  sheetUrl: "",   // URL Web App Google Apps Script
  email: "ijamazhar@gmail.com",
  whatsapp: "601112452726",
  agent: "Nizam"
};
```

Logo ada dalam folder `assets/`. Gantikan `logo-qhomes.png` dan `logo-nexus.png` dengan fail asal untuk kualiti lebih tajam.

## Kali pertama guna (hanya jika guna email, tanpa Google Sheet)

Selepas laman dihoskan, hantar satu borang ujian. FormSubmit akan hantar email **"Activate Form"** ke alamat di atas (semak folder Spam). Tekan **Activate**. Selepas itu semua borang akan terus masuk ke email.

## Hoskan

GitHub Pages (Settings → Pages) atau seret folder ini ke https://app.netlify.com/drop. Borang hanya berfungsi bila laman dibuka dari alamat web (bukan dibuka terus sebagai fail).
