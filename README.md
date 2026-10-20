# QHomes Realty – laman ringkas

Laman satu halaman (HTML statik) dengan 4 pilihan:

1. **Semak kelayakan loan**: borang (nama, gaji, komitmen, kawasan, telefon)
2. **Saya nak jual rumah / tanah**: borang (nama, jenis, lokasi, harga, telefon)
3. **Saya nak beli rumah**: borang (nama, kawasan, telefon)
4. **Kalkulator loan**: kira ansuran bulanan

Setiap borang dihantar ke email melalui [FormSubmit](https://formsubmit.co) (percuma, tiada server).

## Tetapan

Buka `index.html` dan cari bahagian `CONFIG` di dalam `<script>`:

```js
const CONFIG = {
  email: "qhairilutm@gmail.com",
  whatsapp: "60123456789",   // tukar kepada no. WhatsApp sebenar
  agent: "Qhairil"
};
```

Logo ada dalam folder `assets/`. Gantikan `logo-qhomes.png` dan `logo-nexus.png` dengan fail asal untuk kualiti lebih tajam.

## Kali pertama guna

Selepas laman dihoskan, hantar satu borang ujian. FormSubmit akan hantar email **"Activate Form"** ke alamat di atas (semak folder Spam). Tekan **Activate**. Selepas itu semua borang akan terus masuk ke email.

## Hoskan

GitHub Pages (Settings → Pages) atau seret folder ini ke https://app.netlify.com/drop. Borang hanya berfungsi bila laman dibuka dari alamat web (bukan dibuka terus sebagai fail).
