# Simpan maklumat pelanggan ke Google Sheet

Setiap borang (beli, jual, kelayakan loan) akan masuk sebagai satu baris dalam Google Sheet anda.
Anda boleh buka dalam app **Google Sheets** di telefon bila-bila masa. Setiap kali ada pelanggan baru,
anda akan dapat notifikasi **Telegram** (melalui bot @nazproperty_bot) dan email ke ijamazhar@gmail.com.

Setup sekali sahaja, lebih kurang 5 minit. Lebih mudah buat di komputer.

## Langkah

1. Log masuk Google (ijamazhar@gmail.com), buka **https://sheets.new**.
   Namakan sheet, contoh: `Nazproperty – Pelanggan`.
2. Menu **Extensions → Apps Script**.
3. Padam semua kod yang ada, kemudian tampal semua kod daripada fail `Code.gs`. Tekan ikon **Save**.
   - Jika guna fail `Code.gs` yang Claude hantar dalam chat, token dan Id Telegram sudah diisi.
   - Jika guna fail dalam repo, isi `TELEGRAM_TOKEN` dan `TELEGRAM_CHAT_ID` di bahagian atas kod.
   - Uji Telegram: pilih fungsi **ujiTelegram** di menu atas editor → tekan **Run** → beri kebenaran
     (langkah 5 di bawah). Mesej "Pelanggan baru: Ujian" patut masuk ke Telegram.
4. Tekan **Deploy → New deployment**.
   - Ikon gear di sebelah "Select type" → pilih **Web app**.
   - **Execute as:** Me
   - **Who has access:** Anyone
   - Tekan **Deploy**.
5. Google akan minta kebenaran: **Authorize access** → pilih akaun anda →
   **Advanced** → **Go to (nama projek) (unsafe)** → **Allow**.
   (Amaran "unsafe" ini biasa untuk skrip yang anda buat sendiri.)
6. Salin **Web app URL** (bermula `https://script.google.com/macros/s/.../exec`).
7. Letak URL itu dalam `index.html` pada `CONFIG.sheetUrl`, atau hantar kepada Claude untuk dimasukkan.

## Uji

Buka laman web, isi satu borang dan tekan Hantar. Satu baris baru patut muncul dalam Sheet,
dengan tajuk lajur di baris pertama.

## Jika ubah kod Apps Script

Tekan **Deploy → Manage deployments → ikon pensel → Version: New version → Deploy**.
URL kekal sama.
