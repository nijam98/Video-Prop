/**
 * Nazproperty: simpan borang laman web ke Google Sheet.
 * Tampal kod ini dalam Extensions > Apps Script pada Google Sheet anda.
 */

// Email untuk notifikasi setiap kali ada pelanggan baru. Letak "" jika tak mahu email.
const NOTIFY_EMAIL = "ijamazhar@gmail.com";

const HEADERS = [
  "Tarikh", "Pilihan", "Nama", "No telefon", "Kawasan",
  "Jenis hartanah", "Harga diminta", "Gaji bersih sebulan", "Komitmen bulanan"
];

function doPost(e) {
  const p = (e && e.parameter) || {};
  if (p._honey) return reply_({ ok: true }); // bot spam

  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    if (sheet.getLastRow() === 0) {
      sheet.appendRow(HEADERS);
      sheet.setFrozenRows(1);
      sheet.getRange(1, 1, 1, HEADERS.length).setFontWeight("bold");
    }
    // Awalan ' supaya Sheets simpan sebagai teks (kekalkan 0 di depan no. telefon, elak formula).
    const row = HEADERS.map(function (h, i) {
      if (i === 0) return new Date();
      const v = String(p[h] || "").slice(0, 500);
      return v ? "'" + v : "";
    });
    sheet.appendRow(row);
  } finally {
    lock.releaseLock();
  }

  if (NOTIFY_EMAIL) {
    try {
      const lines = HEADERS.slice(1)
        .filter(function (h) { return p[h] && p[h] !== "-"; })
        .map(function (h) { return h + ": " + p[h]; });
      MailApp.sendEmail(
        NOTIFY_EMAIL,
        "Pelanggan baru: " + (p["Pilihan"] || "") + " – " + (p["Nama"] || ""),
        lines.join("\n") + "\n\nSemua rekod: " + SpreadsheetApp.getActiveSpreadsheet().getUrl()
      );
    } catch (err) {
      // Email gagal tidak menjejaskan rekod dalam Sheet.
    }
  }
  return reply_({ ok: true });
}

// Untuk uji: buka URL Web App dalam pelayar, patut nampak {"ok":true,...}
function doGet() {
  return reply_({ ok: true, info: "Nazproperty form endpoint aktif" });
}

function reply_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
