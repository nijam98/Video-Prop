"""Build the edit decision list: snap cut points to quiet spots, map words to output time."""
import json, wave, sys, numpy as np
W = sys.argv[1]  # work dir with audio16k.wav + transcript.json
# (src_in, src_out, label) — rough cuts from the transcript; snapped below
SEGS = [
 (32.20, 36.62, "hook"),          # "Rumah ni memiliki empat bilik, lima toilet, paling rare lima toilet"
 (0.72, 6.54, "s1"),              # "kita ada satu perumahan baru ... sekolah teknik"
 (7.73, 17.56, "s2"),             # "Taman ... corner lot ... Jom kita masuk tengok dalam"
 (21.48, 22.74, "s3a"),           # "Auto gate, porch"
 (23.64, 26.46, "s3b"),           # "yang sangat-sangat luas dan sangat tinggi"
 (28.56, 32.10, "s4"),            # "dekat sini kita ada ruang tamu, memang paling luas"
 (36.62, 37.72, "s5"),            # "Ada ruang store"
 (40.40, 41.50, "s6"),            # "kat sini open"
 (41.80, 43.02, "s7"),            # "kitchen"
 (43.20, 47.20, "s8"),            # "and then ada ruang belakang ... 15 kaki lagi"
 (52.95, 55.40, "s9"),            # "sebelah sini kita ada bilik nombor empat"
 (58.15, 62.86, "s10"),           # "built-in satu toilet, tak sharing ..., dia seorang"
 (62.96, 66.02, "s11"),           # "Elok sangat untuk bilik tetamu"
 (70.72, 71.86, "s12"),           # "kita duduk tingkat atas pulak"
 (75.40, 80.56, "s13"),           # "Dia tinggi sikit lah ... sama tinggi dengan sekolah"
 (81.16, 82.76, "s14"),           # "Nampak tak, bumbung sekolah tu"
 (84.86, 89.08, "s15"),           # "sebab tu harga dia premium. Semi-premium, ada balkoni luar satu"
]
FIX = {"Kolor,":"Kuala,", "Cali,":"Challi,", "pos":"porch", "rumbung":"bumbung", "lah,":"lah,"}
wf = wave.open(f"{W}/audio16k.wav"); a = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32)/32768
def rms(t):
    i = int(t*16000); s = a[max(0,i-80):i+80]; return float(np.sqrt((s**2).mean()+1e-12))
def snap(t, win=0.06, keep_lo=None, keep_hi=None):
    best = t; bv = rms(t)
    for d in np.arange(-win, win+1e-9, 0.005):
        c = round(t+d, 3)
        if keep_lo is not None and c < keep_lo: continue
        if keep_hi is not None and c > keep_hi: continue
        v = rms(c)
        if v < bv: bv, best = v, c
    return round(best, 3)
tr = json.load(open(f"{W}/transcript.json"))
words = [dict(w=w["w"].strip(), s=w["s"], e=w["e"]) for seg in tr for w in seg["words"]]
# merge split tokens and fix mishears (by position, not text)
m = []
for w in words:
    if w["w"].startswith("-") and m:
        m[-1]["w"] += w["w"]; m[-1]["e"] = w["e"]; continue
    m.append(w)
words = m
for i, w in enumerate(words):
    if w["w"] == "6": w["w"] = "non-bumi,"; w["e"] = words[i+1]["e"]; words[i+1]["drop"] = True
    if w["w"] == "lima" and words[i+1]["w"] == "belah": w["w"] = "15"; w["e"] = words[i+1]["e"]; words[i+1]["drop"] = True
    w["w"] = FIX.get(w["w"], w["w"])
words = [w for w in words if not w.get("drop")]
out = []; t = 0.0
for a_, b_, lab in SEGS:
    si, so = snap(a_, keep_hi=a_), snap(min(b_, 89.0), keep_lo=min(b_, 89.0))
    so = 89.06 if b_ >= 89.0 else min(so, 89.06)
    seg = dict(id=lab, src_in=si, src_out=so, start=round(t,3), dur=round(so-si,3))
    seg["words"] = [dict(text=w["w"], start=round(max(w["s"],si)-si+t,3), end=round(min(w["e"],so)-si+t,3), src=w["s"])
                    for w in words if w["s"] >= si-0.02 and w["s"] < so-0.05]
    out.append(seg); t += so-si
json.dump(dict(segments=out, total=round(t,3)), open(sys.argv[2], "w"), indent=1, ensure_ascii=False)
for s in out:
    print(f'{s["id"]:5} src {s["src_in"]:6.2f}-{s["src_out"]:6.2f} out {s["start"]:6.2f} dur {s["dur"]:5.2f} | ' + " ".join(w["text"] for w in s["words"]))
print("TOTAL", round(t,2))
