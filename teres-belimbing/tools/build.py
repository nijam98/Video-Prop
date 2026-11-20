#!/usr/bin/env python3
"""Generates index.html + compositions/*.html for the Teres End Lot Taman Belimbing reel.

Look: "Editorial Glass" — magazine-cover subtitles in a big serif (Instrument Serif) that sit BEHIND the
presenter (a person matte, assets/person.webm, is layered over the captions), frosted-glass cards for the key
points (Manrope labels), small photo prints pulled from the walk-through, chapter tags like a magazine index,
and a soft glass-blur sweep on the big cuts. Palette: ink #13241D, terracotta #B5482A, sand #EFE6D6, gold #C9A45C.

Edit the tables below (EDL, captions, cards, SFX) and re-run:
    python3 tools/build.py
"""
import json, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
TAIL = 3.2  # end card after the last word

INK, TERRA, SAND, GOLD, CREAM = "#13241D", "#A63F22", "#EFE6D6", "#C9A45C", "#FBF7F0"

# ---------------------------------------------------------------- edit decision list
# parts = [(src_in, src_out)] of speech kept. Picture = same moment unless `pics` = [(src_in, dur)] overrides it.
EDL = [
    dict(id="s01", parts=[(0.36, 3.78)]),                                  # HOOK yang mana nak cari rumah open facing, ada satu ni teres end lot
    dict(id="s02", parts=[(9.30, 12.20)], pics=[(10.20, 2.90)]),          # rumah ni freehold, non-bumi lot
    dict(id="s03", parts=[(3.78, 6.40), (6.64, 8.52)]),                    # taman belimbing, depan ni taman permainan, sebelah kanan belimbing eco park
    dict(id="s04", parts=[(12.24, 15.58)]),                                # nampak ruang parking yang sangat luas, siap dengan imprint
    dict(id="s05", parts=[(17.00, 18.22)]),                                # kita dekat ruang tamu
    dict(id="s06", parts=[(21.26, 24.92)]),                                # owner buat semua dah, L-box ada siap, lampu sangat-sangat cantik
    dict(id="s07", parts=[(24.92, 27.64)], pics=[(18.30, 2.72)]),         # rumah ni ada 3 bilik dan 2 tandas
    dict(id="s08", parts=[(29.50, 30.92)]),                                # master bedroom memang sangat luas
    dict(id="s09", parts=[(31.00, 31.70), (33.78, 34.90)]),                # yang penting, 1 tandas
    dict(id="s10", parts=[(36.98, 39.40), (39.90, 42.86)]),                # dekat sini owner dah buat siap ruang makan / ada ruang untuk letak peti ais
    dict(id="s11", parts=[(44.80, 46.22), (47.14, 50.98)]),                # sini bilik yang kedua / tinggi, siap ada ruang pencahayaan kat atas ni
    dict(id="s12", parts=[(52.06, 53.58), (56.70, 59.18)], pics=[(54.60, 1.52), (56.70, 2.48)]),  # sini pula dapur / kitchen cabinet atas sampai bawah
    dict(id="s13", parts=[(60.50, 62.16)]),                                # bilik yang ketiga
    dict(id="s14", parts=[(63.52, 64.82), (65.32, 66.98)]),                # dia estetik sikit lah / sebab ada tirai ni
    dict(id="s15", parts=[(67.68, 71.08)]),                                # yang ni toilet yang kedua, full tiles sampai kat atas
    dict(id="s16", parts=[(71.52, 72.76), (75.22, 76.58)]),                # belakang ni ruang laundry / sidai kain belah tepi ni
    dict(id="s17", parts=[(77.54, 81.40)]),                                # ada tanah tepi ni, memang sangat-sangat privacy kawasan sini
    dict(id="s18", parts=[(82.20, 84.64), (84.86, 86.96)]),                # berminat? LPPSA boleh, loan bank boleh / berniaga perlukan SSM dan statement bank 6 bulan
    dict(id="s19", parts=[(87.14, 89.66), (90.04, 91.00)], pics=[(87.14, 2.52), (90.04, 0.96), (0.40, TAIL)], extra=TAIL),  # CTA + end card over the house
]
# removed: "okey" fillers, "and then", "jom kita masuk tengok dalam", "ruang tamu ni ZZ (unclear), jadi kita dapat privacy",
# "sekarang kita masuk master bedroom" (said twice), unclear "master bedroom ni petok built-in", "bilik kedua" (repeat),
# "dapur owner pergi semua" + "macam mana tengok macam tu dapat?" (unclear), "sebelah sini kita ada", "ruang laundry letak
# macam-macam sini" (repeat), "orang tu" (unclear), "terima kasih kerana menonton", and every pause.

t = 0.0
for s in EDL:
    s["start"] = round(t, 3)
    offs, acc = [], 0.0
    for a0, a1 in s["parts"]:
        offs.append(round(acc, 3))
        acc += a1 - a0
    s["offs"] = offs
    s["dur"] = round(acc, 3)
    t += s["dur"]
VOICE_END = round(t, 3)
TOTAL = round(VOICE_END + TAIL, 3)
ST = {s["id"]: s["start"] for s in EDL}
EN = {s["id"]: round(s["start"] + s["dur"], 3) for s in EDL}
SEG = {s["id"]: s for s in EDL}


def o(seg, src):
    """source second -> output second (handles multi-part segments)"""
    s = SEG[seg]
    for (a0, a1), off in zip(s["parts"], s["offs"]):
        if src <= a1 + 0.001:
            return round(s["start"] + off + max(0.0, src - a0), 3)
    a0, a1 = s["parts"][-1]
    return round(s["start"] + s["offs"][-1] + (src - a0), 3)


# ---------------------------------------------------------------- captions (word, source time[, 1 = key word]), group end
CAPS = [
    ("s01", [("Yang", 0.38), ("mana", 0.54), ("nak", 0.72), ("cari", 0.80)], 1.06),
    ("s01", [("rumah", 1.06), ("open", 1.20, 1), ("facing?", 1.58, 1)], 2.18),
    ("s01", [("Ada", 2.18), ("satu", 2.36), ("ni,", 2.62)], 2.82),
    ("s01", [("teres", 2.82, 1), ("end", 3.30, 1), ("lot.", 3.44, 1)], 3.78),
    ("s02", [("Rumah", 9.34), ("ni", 9.50)], 9.82),
    ("s02", [("freehold,", 9.82, 1)], 11.30),
    ("s02", [("non-bumi", 11.32, 1), ("lot.", 11.94, 1)], 12.20),
    ("s03", [("Taman", 3.80), ("Belimbing.", 4.00, 1)], 4.60),
    ("s03", [("Depan", 4.60), ("ni", 5.06)], 5.24),
    ("s03", [("taman", 5.24, 1), ("permainan,", 5.74, 1)], 6.40),
    ("s03", [("sebelah", 6.64), ("kanan", 6.98), ("kita", 7.24), ("ada", 7.36)], 7.56),
    ("s03", [("Belimbing", 7.56, 1), ("Eco", 8.10, 1), ("Park.", 8.24, 1)], 8.52),
    ("s04", [("Nampak", 12.28), ("ruang", 12.82), ("parking", 13.28, 1)], 13.56),
    ("s04", [("yang", 13.56), ("sangat", 13.76), ("luas,", 14.04, 1)], 14.38),
    ("s04", [("siap", 14.38), ("dengan", 15.12), ("imprint.", 15.26, 1)], 15.58),
    ("s05", [("Kita", 17.04), ("dekat", 17.16), ("ruang", 17.42, 1), ("tamu.", 17.88, 1)], 18.22),
    ("s06", [("Owner", 21.30), ("buat", 21.44), ("semua", 21.66), ("dah,", 21.86)], 22.10),
    ("s06", [("L-box", 22.10, 1), ("ada", 22.44), ("siap,", 22.84)], 23.18),
    ("s06", [("lampu", 23.18), ("yang", 23.80)], 23.92),
    ("s06", [("sangat-sangat", 23.92), ("cantik.", 24.52, 1)], 24.92),
    ("s07", [("Rumah", 24.94), ("ni", 25.40)], 25.76),
    ("s07", [("3", 25.76, 1), ("bilik", 26.04, 1)], 26.60),
    ("s07", [("dan", 26.60), ("2", 26.76, 1), ("tandas.", 27.12, 1)], 27.64),
    ("s08", [("Master", 29.54, 1), ("bedroom", 29.94, 1)], 30.30),
    ("s08", [("memang", 30.30), ("sangat", 30.44), ("luas.", 30.66, 1)], 30.92),
    ("s09", [("Yang", 31.00), ("penting,", 31.42)], 31.70),
    ("s09", [("1", 33.80, 1), ("tandas.", 34.02, 1)], 34.90),
    ("s10", [("Dekat", 37.00), ("sini,", 37.14)], 37.54),
    ("s10", [("owner", 37.54), ("dah", 37.86), ("buat", 38.24), ("siap", 38.56)], 38.86),
    ("s10", [("ruang", 38.86, 1), ("makan.", 39.08, 1)], 39.40),
    ("s10", [("Ada", 39.90), ("ruang", 40.10), ("untuk", 41.04)], 41.34),
    ("s10", [("letak", 41.34), ("peti", 42.08, 1), ("ais.", 42.70, 1)], 42.86),
    ("s11", [("Sini", 44.82), ("bilik", 45.16, 1), ("yang", 45.76), ("kedua.", 45.86, 1)], 46.22),
    ("s11", [("Tinggi,", 47.16, 1)], 47.84),
    ("s11", [("siap", 47.84), ("ada", 48.78), ("dengan", 49.06)], 49.26),
    ("s11", [("ruang", 49.26), ("pencahayaan", 49.56, 1)], 50.38),
    ("s11", [("kat", 50.38), ("atas", 50.54, 1), ("ni.", 50.86)], 50.98),
    ("s12", [("Sini", 52.10), ("pula", 52.38), ("dapur.", 52.82, 1)], 53.58),
    ("s12", [("Siap", 56.72), ("dengan", 57.16)], 57.36),
    ("s12", [("kitchen", 57.36, 1), ("cabinet,", 57.84, 1)], 58.22),
    ("s12", [("atas", 58.22, 1), ("sampai", 58.64), ("bawah.", 58.78, 1)], 59.18),
    ("s13", [("Bilik", 60.54, 1), ("yang", 61.16), ("ketiga.", 61.40, 1)], 62.16),
    ("s14", [("Dia", 63.54), ("estetik", 64.02, 1), ("sikit", 64.50), ("lah,", 64.68)], 64.82),
    ("s14", [("sebab", 65.34), ("ada", 65.68)], 66.14),
    ("s14", [("tirai", 66.14, 1), ("ni.", 66.80)], 66.98),
    ("s15", [("Yang", 67.70), ("ni", 67.78), ("toilet", 67.92, 1)], 68.82),
    ("s15", [("yang", 68.82), ("kedua.", 69.06, 1)], 69.40),
    ("s15", [("Full", 69.44, 1), ("tiles", 70.24, 1)], 70.42),
    ("s15", [("sampai", 70.42), ("kat", 70.62), ("atas.", 70.80, 1)], 71.08),
    ("s16", [("Belakang", 71.54), ("ni", 72.02)], 72.12),
    ("s16", [("ruang", 72.12, 1), ("laundry.", 72.42, 1)], 72.76),
    ("s16", [("Sidai kain", 75.24, 1), ("belah", 75.82), ("tepi", 76.10), ("ni.", 76.42)], 76.58),
    ("s17", [("Ada", 77.56), ("tanah", 78.12, 1), ("tepi", 78.52, 1), ("ni,", 78.74)], 79.02),
    ("s17", [("memang", 79.02), ("sangat-sangat", 79.38)], 80.30),
    ("s17", [("privacy", 80.30, 1)], 80.72),
    ("s17", [("kawasan", 80.72), ("sini.", 81.20)], 81.40),
    ("s18", [("Berminat?", 82.22, 1)], 82.94),
    ("s18", [("LPPSA", 82.94, 1), ("boleh,", 83.64)], 84.08),
    ("s18", [("loan", 84.08, 1), ("bank", 84.22, 1), ("boleh.", 84.40)], 84.64),
    ("s18", [("Berniaga", 84.88, 1), ("perlukan", 85.20)], 85.52),
    ("s18", [("SSM", 85.52, 1), ("dan", 85.88)], 86.06),
    ("s18", [("statement", 86.06), ("bank", 86.24)], 86.46),
    ("s18", [("6", 86.46, 1), ("bulan.", 86.60, 1)], 86.96),
    ("s19", [("Boleh", 87.16), ("klik", 87.60)], 87.84),
    ("s19", [("link", 87.84, 1), ("bio", 87.92, 1)], 88.16),
    ("s19", [("ataupun", 88.16), ("tekan", 88.54)], 88.80),
    ("s19", [("butang", 88.80, 1), ("biru", 88.96, 1)], 89.24),
    ("s19", [("kat", 89.24), ("bawah", 89.32), ("ni.", 89.56)], 89.66),
    ("s19", [("Jumpa", 90.06), ("dekat", 90.50), ("WhatsApp!", 90.72, 1)], 91.00),
]

# caption block top (px) per segment: chosen so the words cross the presenter's head / shoulders,
# which is what makes them read as "behind" him. Overwritten from tools/person-boxes.json when present.
CAP_TOP = {k: 420 for k in SEG}
CAP_SIZE = {k: 156 for k in SEG}
CAP_SIZE["s01"] = 172
CAP_W = 760  # caption column: x 128-888 (clear of the TikTok / Reels right rail)


def load_boxes():
    p = os.path.join(ROOT, "tools", "person-boxes.json")
    if not os.path.exists(p):
        return
    boxes = json.load(open(p))
    for k, b in boxes.items():
        if k in CAP_TOP and b:
            head = b["top"]
            # words start a little above the head and run across it; kept clear of the cards (y >= 960)
            CAP_TOP[k] = int(min(620, max(380, head - 40)))


# ---------------------------------------------------------------- key beats (output seconds)
B = dict(
    open=o("s01", 1.20), teres=o("s01", 2.82), lot=o("s01", 3.44),
    free=o("s02", 9.82), nonbumi=o("s02", 11.32),
    taman=o("s03", 3.80), main=o("s03", 5.24), eco=o("s03", 7.56),
    parking=o("s04", 13.28), luas=o("s04", 14.04), imprint=o("s04", 15.26),
    tamu=o("s05", 17.42), lbox=o("s06", 22.10), lampu=o("s06", 23.18), cantik=o("s06", 24.52),
    bilik3=o("s07", 25.76), tandas2=o("s07", 26.76),
    master=o("s08", 29.54), mluas=o("s08", 30.66), satu=o("s09", 33.80),
    makan=o("s10", 38.86), peti=o("s10", 42.08),
    kedua=o("s11", 45.16), tinggi=o("s11", 47.16), cahaya=o("s11", 49.56),
    dapur=o("s12", 52.82), cabinet=o("s12", 57.36), atasbawah=o("s12", 58.22),
    ketiga=o("s13", 60.54), estetik=o("s14", 64.02), tirai=o("s14", 66.14),
    toilet=o("s15", 67.92), tiles=o("s15", 69.44),
    laundry=o("s16", 72.12), sidai=o("s16", 75.24),
    tanah=o("s17", 78.12), privacy=o("s17", 80.30),
    minat=o("s18", 82.22), lppsa=o("s18", 82.94), bank=o("s18", 84.08), niaga=o("s18", 84.88), ssm=o("s18", 85.52),
    bulan=o("s18", 86.46),
    link=o("s19", 87.84), butang=o("s19", 88.80), bawah=o("s19", 89.32), wa=o("s19", 90.06),
)

# chapter index (magazine contents style) — (segment it starts on, number, title)
CHAPTERS = [("s01", "01", "Luar rumah"), ("s05", "02", "Ruang tamu"), ("s08", "03", "Master bedroom"),
            ("s10", "04", "Ruang makan"), ("s11", "05", "Bilik kedua"), ("s12", "06", "Dapur"),
            ("s13", "07", "Bilik ketiga"), ("s15", "08", "Tandas kedua"), ("s16", "09", "Laundry"),
            ("s17", "10", "Tanah tepi"), ("s18", "11", "Pembiayaan")]

# full-frame glass sweeps (centre = the cut)
SWEEPS = [ST["s05"], ST["s18"], VOICE_END]


# ---------------------------------------------------------------- sound effects (output time, file, volume)
# every file is pre-normalised to -20 LUFS (voice sits at -15): 0.12-0.35 keeps them tucked under the voice
def fx(at, name, vol=0.25, ms=0.0, dur=None):
    return dict(at=round(max(0.0, at), 3), name=name, vol=vol, ms=ms, dur=dur)


SFX = [
    fx(0.00, "whoosh-impact", 0.22),
    fx(B["open"] + 0.02, "ui-select", 0.20),
    fx(B["teres"] - 0.05, "light-button", 0.26),
    fx(B["free"] + 0.05, "check", 0.30), fx(B["nonbumi"] + 0.05, "check", 0.30),
    fx(ST["s03"] - 0.06, "sweep-short", 0.18),
    fx(B["taman"] + 0.05, "light-button", 0.22),
    fx(B["main"] + 0.10, "shutter", 0.20), fx(B["eco"] + 0.10, "shutter", 0.20),
    fx(B["parking"] + 0.02, "ui-click", 0.24), fx(B["imprint"] + 0.02, "pop-dry", 0.18),
    fx(SWEEPS[0] - 0.32, "air-woosh", 0.22),
    fx(B["lbox"] + 0.02, "ui-click", 0.24), fx(B["cantik"] + 0.02, "chime", 0.10),
    fx(ST["s07"] - 0.04, "sweep-small", 0.16),
    fx(B["bilik3"] + 0.02, "ui-select", 0.20), fx(B["tandas2"] + 0.02, "ui-select", 0.18),
    fx(B["bilik3"] + 0.25, "shutter", 0.14),
    fx(ST["s08"] - 0.06, "sweep-short", 0.16), fx(B["master"] + 0.05, "ui-click", 0.22),
    fx(B["satu"] + 0.02, "pop-dry", 0.20),
    fx(ST["s10"] - 0.06, "sweep-short", 0.16), fx(B["makan"] + 0.02, "ui-click", 0.22), fx(B["peti"] + 0.02, "pop-dry", 0.18),
    fx(ST["s11"] - 0.06, "sweep-short", 0.16), fx(B["tinggi"] - 0.10, "tech-slide", 0.16), fx(B["cahaya"] + 0.05, "chime", 0.08),
    fx(ST["s12"] - 0.06, "sweep-short", 0.16), fx(B["cabinet"] + 0.02, "ui-click", 0.22),
    fx(ST["s13"] - 0.06, "sweep-short", 0.16), fx(B["estetik"] + 0.02, "ui-click", 0.20), fx(B["tirai"] + 0.05, "shutter", 0.16),
    fx(ST["s15"] - 0.06, "sweep-short", 0.16), fx(B["tiles"] + 0.02, "ui-click", 0.22),
    fx(ST["s16"] - 0.06, "sweep-short", 0.16), fx(B["laundry"] + 0.02, "ui-click", 0.22), fx(B["sidai"] + 0.02, "pop-dry", 0.18),
    fx(ST["s17"] - 0.06, "sweep-short", 0.16), fx(B["tanah"] + 0.02, "ui-click", 0.22), fx(B["privacy"] + 0.02, "chime", 0.10),
    fx(SWEEPS[1] - 0.32, "air-woosh", 0.22),
    fx(B["lppsa"] + 0.08, "check", 0.30), fx(B["bank"] + 0.08, "check", 0.30), fx(B["ssm"] + 0.08, "check", 0.30),
    fx(B["bulan"] + 0.20, "confirm", 0.12),
    fx(B["link"] + 0.02, "ui-select", 0.20), fx(B["butang"] + 0.02, "light-button", 0.26),
    fx(B["wa"] + 0.02, "pop-dry", 0.20),
    fx(SWEEPS[2] - 0.32, "air-woosh", 0.24),
    fx(VOICE_END + 0.35, "chime", 0.14),
    fx(VOICE_END + 0.70, "shutter", 0.14),
]
# chapter-change sweeps already listed above are the soft "sweep-short" ticks


# ---------------------------------------------------------------- camera (applied to footage AND the person layer)
def picture_cuts():
    cuts = []
    for s in EDL:
        if s.get("pics"):
            acc = 0.0
            for src, d in s["pics"]:
                cuts.append(round(s["start"] + acc, 3))
                acc += d
        else:
            for off in s["offs"]:
                cuts.append(round(s["start"] + off, 3))
    return sorted(set(cuts))


def cam_js():
    js = []
    cuts = picture_cuts()
    sweeps = [round(x, 3) for x in SWEEPS]
    for i, c in enumerate(cuts):
        nxt = cuts[i + 1] if i + 1 < len(cuts) else TOTAL
        big = any(abs(c - w) < 0.02 for w in sweeps) or c == 0
        s0 = 1.10 if big else 1.055
        js.append(f'tl.fromTo(CAM, {{ scale: {s0} }}, {{ scale: 1.0, duration: 0.55, ease: "expo.out", immediateRender: false }}, {c:.3f});')
        if nxt - c > 0.7:
            js.append(f'tl.to(CAM, {{ scale: 1.03, duration: {nxt - c - 0.55:.3f}, ease: "none" }}, {c + 0.55:.3f});')
    return "\n      ".join(js)


# ================================================================ shared building blocks
FONTS = """
@font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif.woff2") format("woff2"); font-style: normal; font-display: block; }
@font-face { font-family: "Instrument Serif"; src: url("assets/fonts/instrument-serif-italic.woff2") format("woff2"); font-style: italic; font-display: block; }
@font-face { font-family: "Manrope"; src: url("assets/fonts/manrope-var.woff2") format("woff2"); font-weight: 200 800; font-display: block; }
"""

BASE_CSS = f"""
#root {{ position: absolute; inset: 0; overflow: visible; pointer-events: none; }}
.abs {{ position: absolute; }}
.glass {{ position: absolute; border-radius: 30px; color: {INK};
  background: linear-gradient(140deg, rgba(255,255,255,0.80), rgba(255,255,255,0.58));
  -webkit-backdrop-filter: blur(22px) saturate(1.35); backdrop-filter: blur(22px) saturate(1.35);
  border: 1.5px solid rgba(255,255,255,0.8);
  box-shadow: 0 24px 60px rgba(19,36,29,0.22), inset 0 1px 0 rgba(255,255,255,0.95); }}
.lbl {{ font-family: "Manrope"; font-weight: 800; font-size: 28px; letter-spacing: 0.16em; text-transform: uppercase; color: {TERRA}; white-space: nowrap; }}
.ser {{ font-family: "Instrument Serif"; font-weight: 400; line-height: 0.98; color: {INK}; white-space: nowrap; }}
.ser i {{ font-style: italic; color: {TERRA}; }}
.sans {{ font-family: "Manrope"; font-weight: 700; color: {INK}; white-space: nowrap; }}
.chip {{ position: absolute; display: flex; align-items: center; gap: 14px; padding: 16px 26px 16px 18px; border-radius: 999px;
  font-family: "Manrope"; font-weight: 800; font-size: 30px; letter-spacing: 0.02em; color: {INK}; white-space: nowrap;
  background: linear-gradient(140deg, rgba(255,255,255,0.82), rgba(255,255,255,0.60));
  -webkit-backdrop-filter: blur(18px) saturate(1.3); backdrop-filter: blur(18px) saturate(1.3);
  border: 1.5px solid rgba(255,255,255,0.85); box-shadow: 0 16px 40px rgba(19,36,29,0.2); }}
.dot {{ width: 40px; height: 40px; border-radius: 50%; background: {INK}; display: flex; align-items: center; justify-content: center; flex: none; }}
.dot svg {{ width: 22px; height: 22px; }}
.photo {{ position: absolute; border-radius: 18px; overflow: hidden; background: {SAND};
  border: 6px solid {CREAM}; box-shadow: 0 18px 40px rgba(19,36,29,0.3); }}
.photo img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
.rule {{ position: absolute; height: 2px; background: {INK}; opacity: 0.25; transform-origin: 0 50%; }}
"""

CHECK_SVG = (f'<svg viewBox="0 0 24 24"><path class="ck" d="M5 12.5 L10 17 L19 7" fill="none" stroke="{CREAM}" '
             f'stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
PIN_SVG = (f'<svg viewBox="0 0 24 24"><path d="M12 22s7-6.6 7-12.2A7 7 0 0 0 5 9.8C5 15.4 12 22 12 22z" fill="{CREAM}"/>'
           f'<circle cx="12" cy="9.8" r="2.6" fill="{INK}"/></svg>')
ARROW_DOWN = (f'<svg viewBox="0 0 24 24"><path d="M12 4v15M5.5 12.5 12 19l6.5-6.5" fill="none" stroke="{CREAM}" '
              f'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>')

COMMON_JS = r"""
      var tl = gsap.timeline({ paused: true });
      // frosted card: lifts in from below, no filter on the element so the backdrop blur stays live
      function glassIn(sel, at, d) {
        tl.fromTo(sel, { y: 46, opacity: 0, scale: 0.965 },
          { y: 0, opacity: 1, scale: 1, duration: d || 0.7, ease: "expo.out", immediateRender: true }, at);
      }
      function glassOut(sel, at) {
        tl.to(sel, { y: -18, opacity: 0, duration: 0.28, ease: "power2.in" }, at);
      }
      function chipIn(sel, at) {
        tl.fromTo(sel, { x: -28, opacity: 0 }, { x: 0, opacity: 1, duration: 0.55, ease: "expo.out", immediateRender: true }, at);
      }
      // check mark draws itself
      function tick(sel, at) {
        gsap.utils.toArray(sel + " .ck").forEach(function (p) {
          var len = p.getTotalLength() + 1;
          gsap.set(p, { strokeDasharray: len + " " + len, strokeDashoffset: len });
          tl.to(p, { strokeDashoffset: 0, duration: 0.32, ease: "power2.out" }, at);
        });
      }
      // photo print: drops in with a small tilt, like a print laid on the frame
      function printIn(sel, at, rot) {
        tl.fromTo(sel, { y: 70, opacity: 0, rotation: (rot || 0) + 8, scale: 1.08 },
          { y: 0, opacity: 1, rotation: rot || 0, scale: 1, duration: 0.8, ease: "expo.out", immediateRender: true }, at);
      }
      function lineIn(sel, at, d) {
        tl.fromTo(sel, { scaleX: 0 }, { scaleX: 1, duration: d || 0.6, ease: "expo.inOut", immediateRender: true }, at);
      }
      function count(sel, at, n) {
        var o = { v: 0 }, el = document.querySelector(sel);
        el.textContent = "0";
        tl.to(o, { v: n, duration: 0.6, ease: "power2.out", onUpdate: function () { el.textContent = Math.round(o.v); } }, at);
      }
      function pulse(sel, at, n) {
        tl.to(sel, { scale: 1.045, duration: 0.32, ease: "sine.inOut", yoyo: true, repeat: n * 2 - 1 }, at);
      }
      function finish(id) { window.__timelines[id] = tl; }
"""


def comp(cid, dur, css, body, js):
    return f"""<template>
  <style>
{FONTS}
{BASE_CSS}
{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}" data-duration="{dur:.3f}">
{body}
  </div>
  <script>
    (function () {{
{COMMON_JS}
{js}
      finish("{cid}");
    }})();
  </script>
</template>
"""


def chip(id_, text, left, top, icon=CHECK_SVG, extra=""):
    return f'<div class="chip" id="{id_}" style="left:{left}px;top:{top}px;{extra}"><span class="dot">{icon}</span>{text}</div>'


def photo(id_, src, left, top, w, h, rot=0, pos="50% 50%"):
    return (f'<div class="photo" id="{id_}" style="left:{left}px;top:{top}px;width:{w}px;height:{h}px;rotate:{rot}deg">'
            f'<img src="assets/photos/{src}.jpg" style="object-position:{pos}" alt=""></div>')


SCENES = []  # (cid, start, dur, html)


def span(first, last):
    s = ST[first]
    e = EN[last] if last != "s19" else TOTAL
    return s, round(e - s, 3), (lambda x: round(x - s, 3))


# card zone: x 128-780, y 940-1240 (clear of the TikTok / Reels caption block and right rail)
CX, CB = 128, 1240


# ================================================================ scenes
def scene_hook():
    """hook + freehold line: the 'Teres End Lot' card holds through both, chips swap above it"""
    s, d, rel = span("s01", "s02")
    body = (
        chip("hk-open", "Open facing", CX, 990)
        + chip("hk-free", "Freehold", CX, 990) + chip("hk-nb", "Non-Bumi Lot", CX + 262, 990)
        + f'<div class="glass" id="hk-card" style="left:{CX}px;top:1080px;width:620px;height:160px;padding:24px 34px">'
          f'<div class="lbl">Untuk dijual · Taman Belimbing</div>'
          f'<div class="ser" style="font-size:80px;margin-top:8px">Teres <i>End Lot</i></div></div>'
    )
    js = f"""
      gsap.set(["#hk-open", "#hk-card", "#hk-free", "#hk-nb"], {{ opacity: 0 }});
      chipIn("#hk-open", {rel(B['open']):.3f}); tick("#hk-open", {rel(B['open']) + 0.15:.3f});
      glassIn("#hk-card", {rel(o('s01', 2.18)):.3f});
      glassOut("#hk-open", {rel(B['free']) - 0.3:.3f});
      chipIn("#hk-free", {rel(B['free']):.3f}); tick("#hk-free", {rel(B['free']) + 0.15:.3f});
      chipIn("#hk-nb", {rel(B['nonbumi']) - 0.5:.3f}); tick("#hk-nb", {rel(B['nonbumi']) - 0.35:.3f});
"""
    SCENES.append(("hook", s, d, comp("hook", d, "", body, js)))


def scene_lokasi():
    s, d, rel = span("s03", "s03")
    css = ""
    body = (
        f'<div class="glass" id="lk-card" style="left:{CX}px;top:900px;width:670px;height:340px">'
        f'<div class="abs" style="left:30px;top:28px;display:flex;align-items:center;gap:16px">'
        f'<span class="dot" style="width:46px;height:46px">{PIN_SVG}</span>'
        f'<span class="ser" style="font-size:58px">Taman <i>Belimbing</i></span></div>'
        f'<div class="rule" id="lk-rule" style="left:30px;top:104px;width:610px"></div>'
        + photo("lk-p1", "playground", 30, 124, 290, 150, -2, "50% 70%")
        + photo("lk-p2", "park", 350, 124, 290, 150, 2, "50% 45%")
        + '</div>'
        + f'<div class="abs sans" id="lk-t1" style="left:{CX + 34}px;top:1190px;font-size:28px">Taman permainan · <span style="color:{TERRA}">depan</span></div>'
        + f'<div class="abs sans" id="lk-t2" style="left:{CX + 360}px;top:1190px;font-size:28px">Eco Park · <span style="color:{TERRA}">kanan</span></div>'
    )
    js = f"""
      gsap.set(["#lk-card", "#lk-p1", "#lk-p2", "#lk-t1", "#lk-t2"], {{ opacity: 0 }});
      glassIn("#lk-card", {rel(B['taman']) - 0.05:.3f});
      lineIn("#lk-rule", {rel(B['taman']) + 0.25:.3f});
      printIn("#lk-p1", {rel(B['main']) + 0.05:.3f}, -2); chipIn("#lk-t1", {rel(B['main']) + 0.3:.3f});
      printIn("#lk-p2", {rel(o('s03', 6.64)):.3f}, 2); chipIn("#lk-t2", {rel(o('s03', 6.64)) + 0.25:.3f});
"""
    SCENES.append(("lokasi", s, d, comp("lokasi", d, css, body, js)))


def scene_parking():
    s, d, rel = span("s04", "s04")
    body = (
        f'<div class="glass" id="pk-card" style="left:{CX}px;top:1050px;width:560px;height:190px;padding:26px 34px">'
        f'<div class="lbl">Porch</div><div class="ser" style="font-size:74px;margin-top:8px">Parking <i>luas</i></div></div>'
        + chip("pk-imp", "Siap imprint", CX + 300, 970)
    )
    js = f"""
      gsap.set(["#pk-card", "#pk-imp"], {{ opacity: 0 }});
      glassIn("#pk-card", {rel(B['parking']) - 0.05:.3f});
      chipIn("#pk-imp", {rel(B['luas']):.3f}); tick("#pk-imp", {rel(B['luas']) + 0.15:.3f});
"""
    SCENES.append(("parking", s, d, comp("parking", d, "", body, js)))


def scene_tamu():
    s, d, rel = span("s05", "s06")
    body = (
        f'<div class="glass" id="tm-card" style="left:{CX}px;top:1050px;width:600px;height:190px;padding:26px 34px">'
        f'<div class="lbl">Owner dah siapkan</div><div class="ser" style="font-size:74px;margin-top:8px">L-Box <i>&amp; lampu</i></div></div>'
        + chip("tm-c1", "Siling L-box", CX, 960) + chip("tm-c2", "Lampu hiasan", CX + 330, 960)
    )
    js = f"""
      gsap.set(["#tm-card", "#tm-c1", "#tm-c2"], {{ opacity: 0 }});
      chipIn("#tm-c1", {rel(B['lbox']):.3f}); tick("#tm-c1", {rel(B['lbox']) + 0.15:.3f});
      chipIn("#tm-c2", {rel(B['lampu']):.3f}); tick("#tm-c2", {rel(B['lampu']) + 0.15:.3f});
      glassIn("#tm-card", {rel(B['tamu']) - 0.1:.3f});
"""
    SCENES.append(("tamu", s, d, comp("tamu", d, "", body, js)))


def scene_spec():
    s, d, rel = span("s07", "s07")
    css = """
.num { font-family:"Instrument Serif"; font-size:150px; line-height:1; color:%s; }
.unit { font-family:"Manrope"; font-weight:800; font-size:28px; letter-spacing:0.12em; text-transform:uppercase; color:%s; }
""" % (INK, TERRA)
    body = (
        f'<div class="glass" id="sp-card" style="left:{CX}px;top:990px;width:670px;height:250px">'
        f'<div class="abs" style="left:40px;top:34px;text-align:center"><div class="num" id="sp-n1">3</div><div class="unit">Bilik</div></div>'
        f'<div class="abs" style="left:150px;top:60px;width:2px;height:140px;background:{INK};opacity:0.2"></div>'
        f'<div class="abs" style="left:184px;top:34px;text-align:center"><div class="num" id="sp-n2">2</div><div class="unit">Tandas</div></div>'
        + photo("sp-p1", "master", 360, 36, 120, 180, -6)
        + photo("sp-p2", "room2", 440, 30, 120, 180, 2, "50% 60%")
        + photo("sp-p3", "room3", 520, 40, 120, 180, 7)
        + '</div>'
    )
    js = f"""
      gsap.set(["#sp-card", "#sp-p1", "#sp-p2", "#sp-p3"], {{ opacity: 0 }});
      glassIn("#sp-card", {rel(B['bilik3']) - 0.25:.3f});
      count("#sp-n1", {rel(B['bilik3']) - 0.1:.3f}, 3);
      count("#sp-n2", {rel(B['tandas2']) - 0.1:.3f}, 2);
      printIn("#sp-p1", {rel(B['bilik3']) + 0.2:.3f}, -6);
      printIn("#sp-p2", {rel(B['bilik3']) + 0.35:.3f}, 2);
      printIn("#sp-p3", {rel(B['bilik3']) + 0.5:.3f}, 7);
"""
    SCENES.append(("spec", s, d, comp("spec", d, css, body, js)))


def simple_card(cid, p, first, last, label, title_html, beat, chips=(), w=600):
    """label + serif title card, optional chips above it: chips = [(text, beat)]"""
    s, d, rel = span(first, last)
    body = (f'<div class="glass" id="{p}-card" style="left:{CX}px;top:1050px;width:{w}px;height:190px;padding:26px 34px">'
            f'<div class="lbl">{label}</div><div class="ser" style="font-size:74px;margin-top:8px">{title_html}</div></div>')
    ids = [f"#{p}-card"]
    js = ""
    x = CX
    for i, (text, bt) in enumerate(chips):
        body += chip(f"{p}-c{i}", text, x, 960)
        ids.append(f"#{p}-c{i}")
        bt = min(rel(bt), d - 1.2)
        js += f'      chipIn("#{p}-c{i}", {bt:.3f}); tick("#{p}-c{i}", {bt + 0.15:.3f});\n'
        x += 30 + 26 * len(text) + 70
    js = f'      gsap.set({json.dumps(ids)}, {{ opacity: 0 }});\n      glassIn("#{p}-card", {min(rel(beat) - 0.05, 0.15):.3f});\n' + js
    SCENES.append((cid, s, d, comp(cid, d, "", body, js)))


def scene_rooms():
    simple_card("master", "ms", "s08", "s09", "Bilik utama", "Master <i>bedroom</i>", B["master"],
                [("Luas", B["mluas"]), ("Bilik air sendiri", B["satu"])], 620)
    simple_card("makan", "mk", "s10", "s10", "Owner dah buat siap", "Ruang <i>makan</i>", B["makan"],
                [("Ruang peti ais", o("s10", 39.90))])
    simple_card("dapur", "dp", "s12", "s12", "Siap dengan", "Kitchen <i>cabinet</i>", B["cabinet"],
                [("Atas sampai bawah", B["cabinet"] + 0.3)], 620)
    simple_card("bilik3", "b3", "s13", "s14", "Bilik ketiga", "Estetik <i>sikit</i>", B["estetik"],
                [("Tirai siap", B["tirai"])])
    simple_card("tandas", "td", "s15", "s15", "Tandas kedua", "Full <i>tiles</i>", B["tiles"],
                [("Sampai siling", B["tiles"] + 0.5)])
    simple_card("laundry", "ld", "s16", "s16", "Belakang rumah", "Ruang <i>laundry</i>", B["laundry"],
                [("Tempat sidai kain", B["sidai"])], 620)
    simple_card("tanah", "tn", "s17", "s17", "Kelebihan end lot", "Tanah <i>tepi</i>", B["tanah"],
                [("Sangat privacy", B["privacy"])])


def scene_bilik2():
    """high ceiling: a thin dimension line runs floor -> ceiling beside the card"""
    s, d, rel = span("s11", "s11")
    body = (
        f'<div class="glass" id="b2-card" style="left:{CX}px;top:1050px;width:600px;height:190px;padding:26px 34px">'
        f'<div class="lbl">Bilik kedua</div><div class="ser" style="font-size:74px;margin-top:8px">Siling <i>tinggi</i></div></div>'
        + chip("b2-c0", "Ruang pencahayaan", CX, 960)
        + f'<div class="abs" id="b2-dim" style="left:742px;top:330px;width:40px;height:600px">'
          f'<div class="abs" id="b2-line" style="left:19px;top:0;width:2px;height:600px;background:{CREAM};box-shadow:0 0 12px rgba(0,0,0,0.35);transform-origin:50% 100%"></div>'
          f'<div class="abs" style="left:4px;top:0;width:32px;height:2px;background:{CREAM}"></div>'
          f'<div class="abs" style="left:4px;top:598px;width:32px;height:2px;background:{CREAM}"></div></div>'
    )
    js = f"""
      gsap.set(["#b2-card", "#b2-c0", "#b2-dim"], {{ opacity: 0 }});
      tl.set("#b2-dim", {{ opacity: 1 }}, {rel(B['tinggi']) - 0.1:.3f});
      tl.fromTo("#b2-line", {{ scaleY: 0 }}, {{ scaleY: 1, duration: 0.8, ease: "expo.inOut", immediateRender: true }}, {rel(B['tinggi']) - 0.1:.3f});
      glassIn("#b2-card", {rel(B['tinggi']):.3f});
      chipIn("#b2-c0", {rel(B['cahaya']):.3f}); tick("#b2-c0", {rel(B['cahaya']) + 0.15:.3f});
"""
    SCENES.append(("bilik2", s, d, comp("bilik2", d, "", body, js)))


def scene_loan():
    s, d, rel = span("s18", "s18")
    css = f"""
.row {{ position:absolute; left:34px; display:flex; align-items:center; gap:18px; }}
.row .t {{ font-family:"Manrope"; font-weight:800; font-size:34px; color:{INK}; }}
.row .s {{ font-family:"Manrope"; font-weight:700; font-size:28px; color:{INK}; opacity:0.7; }}
"""
    body = (
        f'<div class="glass" id="ln-card" style="left:{CX}px;top:840px;width:640px;height:400px">'
        f'<div class="abs lbl" style="left:34px;top:30px">Pembiayaan</div>'
        f'<div class="abs ser" style="left:34px;top:62px;font-size:64px">Boleh <i>beli</i> dengan</div>'
        f'<div class="row" id="ln-r1" style="top:156px"><span class="dot">{CHECK_SVG}</span><span class="t">LPPSA</span></div>'
        f'<div class="row" id="ln-r2" style="top:216px"><span class="dot">{CHECK_SVG}</span><span class="t">Loan bank</span></div>'
        f'<div class="row" id="ln-r3" style="top:276px"><span class="dot">{CHECK_SVG}</span><span class="t">Berniaga</span></div>'
        f'<div class="row" id="ln-s" style="top:330px;left:92px"><span class="s">SSM + statement bank 6 bulan</span></div>'
        '</div>'
    )
    js = f"""
      gsap.set(["#ln-card", "#ln-r1", "#ln-r2", "#ln-r3", "#ln-s"], {{ opacity: 0 }});
      glassIn("#ln-card", {rel(B['minat']):.3f});
      chipIn("#ln-r1", {rel(B['lppsa']):.3f}); tick("#ln-r1", {rel(B['lppsa']) + 0.12:.3f});
      chipIn("#ln-r2", {rel(B['bank']):.3f}); tick("#ln-r2", {rel(B['bank']) + 0.12:.3f});
      chipIn("#ln-r3", {rel(B['niaga']):.3f});
      chipIn("#ln-s", {rel(B['niaga']) + 0.2:.3f}); tick("#ln-r3", {rel(B['ssm']) + 0.12:.3f});
"""
    SCENES.append(("loan", s, d, comp("loan", d, css, body, js)))


def scene_cta():
    s, d, rel = span("s19", "s19")
    ve = round(VOICE_END - s, 3)
    css = f"""
.btn {{ position:absolute; display:flex; align-items:center; gap:18px; padding:22px 34px 22px 22px; border-radius:999px;
  background:#1D6BF3; color:#fff; font-family:"Manrope"; font-weight:800; font-size:38px; white-space:nowrap;
  box-shadow:0 20px 50px rgba(29,107,243,0.45), inset 0 1px 0 rgba(255,255,255,0.4); }}
.btn .dot {{ background: rgba(255,255,255,0.22); width:52px; height:52px; }}
.btn .dot svg {{ width:30px; height:30px; }}
.sum {{ position:absolute; font-family:"Manrope"; font-weight:800; font-size:30px; letter-spacing:0.12em; text-transform:uppercase; color:{INK}; }}
"""
    body = (
        chip("ct-link", "Link di bio", CX, 930, PIN_SVG)
        + f'<div class="btn" id="ct-btn" style="left:{CX}px;top:1028px"><span class="dot">{ARROW_DOWN}</span>Tekan butang biru</div>'
        + chip("ct-wa", "Jumpa di WhatsApp", CX, 1158)
        # end card: frosted panel over the house
        + f'<div class="glass" id="ec-card" style="left:128px;top:330px;width:740px;height:900px;border-radius:40px">'
          f'<div class="abs lbl" style="left:50px;top:52px">Untuk dijual · Taman Belimbing</div>'
          f'<div class="abs ser" style="left:46px;top:92px;font-size:132px">Teres</div>'
          f'<div class="abs ser" style="left:46px;top:212px;font-size:132px"><i>End Lot</i></div>'
          f'<div class="rule" id="ec-rule" style="left:50px;top:360px;width:640px"></div>'
          f'<div class="abs sum" id="ec-s1" style="left:50px;top:392px">Freehold · Non-Bumi</div>'
          f'<div class="abs sum" id="ec-s2" style="left:50px;top:436px">3 Bilik · 2 Tandas · Tanah tepi</div>'
          + photo("ec-p1", "lbox", 50, 500, 200, 250, -3)
          + photo("ec-p2", "kitchen", 270, 492, 200, 250, 1)
          + photo("ec-p3", "master", 490, 500, 200, 250, 4)
          + f'<div class="abs sans" id="ec-cta" style="left:50px;top:800px;font-size:34px">Tekan <span style="color:#1D6BF3">butang biru</span> ↓ · link di bio</div>'
          '</div>'
    )
    pulse_n = max(1, int((ve - rel(B['butang']) - 0.8) / 0.64))
    js = f"""
      gsap.set(["#ct-link", "#ct-btn", "#ct-wa", "#ec-card", "#ec-s1", "#ec-s2", "#ec-p1", "#ec-p2", "#ec-p3", "#ec-cta"], {{ opacity: 0 }});
      chipIn("#ct-link", {rel(B['link']):.3f});
      glassIn("#ct-btn", {rel(B['butang']) - 0.05:.3f});
      pulse("#ct-btn", {rel(B['butang']) + 0.6:.3f}, {pulse_n});
      chipIn("#ct-wa", {rel(B['wa']):.3f}); tick("#ct-wa", {rel(B['wa']) + 0.15:.3f});
      glassOut(["#ct-link", "#ct-btn", "#ct-wa"], {ve - 0.05:.3f});
      glassIn("#ec-card", {ve + 0.05:.3f}, 0.9);
      lineIn("#ec-rule", {ve + 0.45:.3f});
      chipIn("#ec-s1", {ve + 0.55:.3f}); chipIn("#ec-s2", {ve + 0.7:.3f});
      printIn("#ec-p1", {ve + 0.7:.3f}, -3); printIn("#ec-p2", {ve + 0.82:.3f}, 1); printIn("#ec-p3", {ve + 0.94:.3f}, 4);
      chipIn("#ec-cta", {ve + 0.85:.3f});
"""
    SCENES.append(("cta", s, d, comp("cta", d, css, body, js)))


def scene_chapters():
    """magazine index tag, top-left: '02 — RUANG TAMU' with a hairline that grows"""
    s, d = 0.0, VOICE_END
    css = f"""
.chp {{ position:absolute; left:128px; top:296px; display:flex; align-items:center; gap:16px; visibility:hidden;
  padding:10px 26px 10px 22px; border-radius:999px;
  background: linear-gradient(140deg, rgba(255,255,255,0.82), rgba(255,255,255,0.60));
  -webkit-backdrop-filter: blur(18px) saturate(1.3); backdrop-filter: blur(18px) saturate(1.3);
  border: 1.5px solid rgba(255,255,255,0.85); box-shadow: 0 12px 30px rgba(19,36,29,0.18); }}
.chp .n {{ font-family:"Instrument Serif"; font-style:italic; font-size:50px; color:{TERRA}; line-height:1; }}
.chp .ln {{ width:54px; height:2px; background:{INK}; opacity:0.5; transform-origin:0 50%; }}
.chp .tt {{ font-family:"Manrope"; font-weight:800; font-size:28px; letter-spacing:0.16em; text-transform:uppercase; color:{INK}; }}
"""
    body, js = "", ""
    for i, (seg, num, title) in enumerate(CHAPTERS):
        t0 = ST[seg]
        t1 = ST[CHAPTERS[i + 1][0]] if i + 1 < len(CHAPTERS) else VOICE_END
        body += f'<div class="chp" id="ch{i}"><span class="n">{num}</span><span class="ln" id="ch{i}l"></span><span class="tt">{title}</span></div>\n'
        js += f'      tl.set("#ch{i}", {{ visibility: "visible" }}, {t0:.3f}); tl.set("#ch{i}", {{ visibility: "hidden" }}, {t1 - 0.02:.3f});\n'
        js += f'      tl.fromTo("#ch{i}", {{ x: -30, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.55, ease: "expo.out", immediateRender: false }}, {t0:.3f});\n'
        js += f'      tl.fromTo("#ch{i} .n", {{ y: 24, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "expo.out", immediateRender: false }}, {t0:.3f});\n'
        js += f'      tl.fromTo("#ch{i}l", {{ scaleX: 0 }}, {{ scaleX: 1, duration: 0.6, ease: "expo.inOut", immediateRender: false }}, {t0 + 0.1:.3f});\n'
        js += f'      tl.fromTo("#ch{i} .tt", {{ x: -14, opacity: 0 }}, {{ x: 0, opacity: 1, duration: 0.5, ease: "expo.out", immediateRender: false }}, {t0 + 0.3:.3f});\n'
    SCENES.append(("chapters", s, d, comp("chapters", d, css, body, js)))


def scene_captions():
    """the big serif subtitles. This layer sits UNDER the person matte, so the presenter walks in front of them."""
    s, d = 0.0, VOICE_END
    css = f"""
.cap {{ position:absolute; left:128px; width:{CAP_W}px; visibility:hidden; text-align:left; }}
.cw {{ display:inline-block; font-family:"Instrument Serif"; font-weight:400; line-height:0.95; color:{INK};
  margin-right:0.2em; text-shadow: 0 0 40px rgba(255,255,255,0.7), 0 0 14px rgba(255,255,255,0.5); }}
.cw.k {{ font-style:italic; color:{TERRA}; }}
"""
    body, js = "", ""
    for ci, (seg, words, end_src) in enumerate(CAPS):
        t0 = o(seg, words[0][1])
        t1 = o(seg, end_src)
        nxt = CAPS[ci + 1] if ci + 1 < len(CAPS) else None
        if nxt:
            t1 = min(t1, o(nxt[0], nxt[1][0][1]) - 0.02)
        size = CAP_SIZE[seg]
        longest = max(len(w[0]) for w in words)
        size = int(min(size, CAP_W / (0.43 * longest)))  # a long single word must still fit the column
        # greedy wrap estimate -> lift the block so its last line ends above the card zone (y 940)
        lines, cur = 1, 0.0
        for w in words:
            ww = 0.5 * size * len(w[0])
            if cur and cur + 0.2 * size + ww > CAP_W:
                lines, cur = lines + 1, ww
            else:
                cur += (0.2 * size if cur else 0) + ww
        floor_ = {"s03": 870, "s18": 820}.get(seg, 930)  # tall cards in these scenes
        top = min(CAP_TOP[seg], int(floor_ - lines * size * 0.95))
        spans = ""
        for wi, w in enumerate(words):
            k = len(w) > 2 and w[2]
            spans += f'<span class="cw{" k" if k else ""}" id="c{ci}w{wi}">{w[0]}</span>'
        body += f'<div class="cap" id="c{ci}" style="top:{max(380, top)}px;font-size:{size}px">{spans}</div>\n'
        js += f'      tl.set("#c{ci}", {{ visibility: "visible" }}, {max(0, t0 - 0.06):.3f}); tl.set("#c{ci}", {{ visibility: "hidden" }}, {t1:.3f});\n'
        for wi, w in enumerate(words):
            wt = max(0, o(seg, w[1]) - 0.06)
            js += (f'      tl.fromTo("#c{ci}w{wi}", {{ yPercent: 38, opacity: 0, filter: "blur(10px)" }}, '
                   f'{{ yPercent: 0, opacity: 1, filter: "blur(0px)", duration: 0.42, ease: "expo.out", immediateRender: true }}, {wt:.3f});\n')
        js += f'      tl.to("#c{ci}", {{ opacity: 0, duration: 0.12, ease: "power1.in" }}, {max(t0, t1 - 0.12):.3f});\n'
    SCENES.append(("captions", s, d, comp("captions", d, css, body, js)))


def sweep_comp():
    """frosted-glass band that sweeps across the frame on the big cuts"""
    d = 0.9
    css = f"""
#sw {{ position:absolute; left:-700px; top:-300px; width:620px; height:2520px; rotate:14deg;
  -webkit-backdrop-filter: blur(28px) saturate(1.3) brightness(1.08); backdrop-filter: blur(28px) saturate(1.3) brightness(1.08);
  background: linear-gradient(90deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.38) 45%, rgba(255,255,255,0.55) 52%, rgba(255,255,255,0) 100%); }}
#fl {{ position:absolute; inset:0; background:{CREAM}; opacity:0; }}
"""
    body = '<div id="fl"></div><div id="sw"></div>'
    js = """
      tl.fromTo("#sw", { x: 0 }, { x: 2100, duration: 0.8, ease: "power3.inOut", immediateRender: true }, 0);
      tl.to("#fl", { opacity: 0.22, duration: 0.2, ease: "power2.in" }, 0.25);
      tl.to("#fl", { opacity: 0, duration: 0.35, ease: "power2.out" }, 0.45);
"""
    return d, comp("sweep", d, css, body, js)


# ================================================================ index.html
def build():
    load_boxes()
    scene_hook(); scene_lokasi(); scene_parking(); scene_tamu(); scene_spec(); scene_rooms()
    scene_bilik2(); scene_loan(); scene_cta(); scene_chapters(); scene_captions()
    os.makedirs(os.path.join(ROOT, "compositions"), exist_ok=True)
    for cid, s, d, html in SCENES:
        with open(os.path.join(ROOT, "compositions", f"{cid}.html"), "w") as f:
            f.write(html)
    sw_d, sw_html = sweep_comp()
    with open(os.path.join(ROOT, "compositions", "sweep.html"), "w") as f:
        f.write(sw_html)

    vids, fgs, auds, comps = [], [], [], []
    vi = 0
    chain = json.dumps({"version": 1, "nodes": [
        {"type": "highpass", "id": "vo1", "label": "Remove rumble", "params": {"frequency": 85}},
        {"type": "peaking", "id": "vo2", "label": "Presence", "params": {"frequency": 3200, "gain": 2, "q": 1}},
        {"type": "limiter", "id": "vo3", "params": {"limit": -1}}]}).replace('"', "&quot;")
    for sg in EDL:
        extra = sg.get("extra", 0)
        if sg.get("pics"):
            pics, acc = [], 0.0
            for src, dd in sg["pics"]:
                pics.append((round(sg["start"] + acc, 3), round(dd, 3), src))
                acc += dd
        else:
            pics = []
            for (a0, a1), off in zip(sg["parts"], sg["offs"]):
                pics.append((round(sg["start"] + off, 3), round(a1 - a0, 3), a0))
            if extra:
                st_, dd, src = pics[-1]
                pics[-1] = (st_, round(dd + extra, 3), src)
        for st_, dd, src in pics:
            vi += 1
            vids.append(f'        <video id="v{vi}" class="clip" src="assets/footage.mp4" muted playsinline data-start="{st_}" '
                        f'data-duration="{dd}" data-media-start="{src}" data-track-index="0"></video>')
            fgs.append(f'        <video id="p{vi}" class="clip" src="assets/person.webm" muted playsinline data-start="{st_}" '
                       f'data-duration="{dd}" data-media-start="{src}" data-track-index="1"></video>')
        for k, ((a0, a1), off) in enumerate(zip(sg["parts"], sg["offs"])):
            auds.append(f'      <audio id="vo-{sg["id"]}-{k}" src="assets/voice.wav" data-start="{round(sg["start"] + off, 3)}" '
                        f'data-duration="{round(a1 - a0, 3)}" data-media-start="{a0}" data-volume="1.0" data-fade-in="0.012" '
                        f'data-fade-out="0.02" data-fx-chain="{chain}" data-track-index="10"></audio>')
    lanes = {"version": 1, "lanes": [{"target": "volume", "points": [
        {"t": 0, "v": 0.34}, {"t": 0.5, "v": 0.22}, {"t": VOICE_END, "v": 0.22},
        {"t": VOICE_END + 0.4, "v": 0.5}, {"t": TOTAL - 0.9, "v": 0.5}, {"t": TOTAL, "v": 0.0}]}]}
    mfx = {"version": 1, "nodes": [
        {"type": "peaking", "id": "mu1", "label": "Make room for the voice", "params": {"frequency": 2500, "gain": -5, "q": 0.8}},
        {"type": "peaking", "id": "mu2", "label": "Clear low mids", "params": {"frequency": 300, "gain": -3, "q": 1}}]}
    auds.append(f'      <audio id="music" src="assets/music/deep-urban.mp3" data-start="0" data-duration="{TOTAL}" '
                f'data-media-start="0" data-volume="1" data-automation="{json.dumps(lanes).replace(chr(34), "&quot;")}" '
                f'data-fx-chain="{json.dumps(mfx).replace(chr(34), "&quot;")}" data-track-index="11"></audio>')

    def dur_of(name):
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                              os.path.join(ROOT, "assets", "sfx", name + ".mp3")], capture_output=True, text=True).stdout
        return float(out.strip())
    lane_end = {}
    for i, e in enumerate(sorted(SFX, key=lambda x: x["at"])):
        fd = dur_of(e["name"]) - e["ms"]
        dd = min(fd, e["dur"]) if e["dur"] else fd
        dd = min(dd, TOTAL - e["at"])
        ms = f' data-media-start="{e["ms"]}"' if e["ms"] else ""
        lane = next(l for l in range(20, 60) if lane_end.get(l, -1) <= e["at"])
        lane_end[lane] = e["at"] + dd
        auds.append(f'      <audio id="fx{i:02d}" src="assets/sfx/{e["name"]}.mp3" data-start="{e["at"]}" data-duration="{dd:.3f}"{ms} '
                    f'data-volume="{e["vol"]}" data-fade-out="0.05" data-track-index="{lane}"></audio>')
    for cid, s, d, _ in SCENES:
        if cid == "captions":
            z, tr, kind = 3, 3, "captions"
        elif cid == "chapters":
            z, tr, kind = 6, 4, "graphics"
        else:
            z, tr, kind = 6, 5, "graphics"
        comps.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" data-start="{s:.3f}" '
                     f'data-duration="{d:.3f}" data-width="{W}" data-height="{H}" data-track-index="{tr}" data-track-kind="{kind}" style="z-index:{z}"></div>')
    for i, at in enumerate(SWEEPS):
        comps.append(f'      <div id="sweep-{i + 1}" data-composition-id="sweep" data-composition-src="compositions/sweep.html" '
                     f'data-start="{at - 0.42:.3f}" data-duration="{sw_d}" data-width="{W}" data-height="{H}" data-track-index="6" '
                     f'data-track-kind="graphics" style="z-index:8"></div>')

    html = f"""<!doctype html>
<html lang="ms" data-resolution="portrait">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: {INK}; }}
      #root {{ position: relative; width: 100%; height: 100%; overflow: hidden; }}
      .cam {{ position: absolute; inset: 0; transform-origin: 50% 45%; }}
      .cam video {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      #cam {{ z-index: 1; }}
      #camfg {{ z-index: 4; }}
      #vign {{ position: absolute; inset: 0; z-index: 5; pointer-events: none;
        background: linear-gradient(180deg, rgba(19,36,29,0.30) 0%, rgba(19,36,29,0) 22%, rgba(19,36,29,0) 60%, rgba(19,36,29,0.22) 100%); }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}" data-fps="{FPS}" data-motion-blur="on">
      <div id="cam" class="cam">
{chr(10).join(vids)}
      </div>
      <div id="camfg" class="cam">
{chr(10).join(fgs)}
      </div>
      <div id="vign"></div>
{chr(10).join(comps)}
{chr(10).join(auds)}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      const CAM = ["#cam", "#camfg"];
      gsap.set(CAM, {{ scale: 1 }});
      {cam_js()}
      window.__timelines["main"] = tl;
      tl.seek(0);
    </script>
  </body>
</html>
"""
    with open(os.path.join(ROOT, "index.html"), "w") as f:
        f.write(html)
    print(f"voice {VOICE_END}s, total {TOTAL}s")
    print("segments:", {k: v for k, v in ST.items()})


if __name__ == "__main__":
    build()
