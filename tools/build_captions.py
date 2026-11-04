"""Builds site-notes/compositions/captions.html from word timings of the cut (seconds in film time)."""
import html, json, pathlib

W = """Yang .00 .10|penting .10 .54|sini .54 .70|tak .70 1.12|naik 1.12 1.42|air, 1.42 1.54|tak 1.54 1.80|banjir. 1.80 2.18
Kalau 2.24 2.36|banjir 2.36 2.80|sini, 2.80 2.98|tenggelam 2.98 3.66|pekan 3.66 3.92|Changlun. 3.92 4.16
Bulanan 4.34 4.74|lebih 4.74 4.92|kurang 4.92 5.14|dalam 5.14 5.26|RM1,200 5.26 5.80
baru 6.04 6.46|boleh 6.46 6.56|dapat 6.56 6.76|teres 6.76 7.44|dekat 7.44 8.00|dengan 8.00 8.36|Taman 8.36 8.76|Keriang 8.76 9.06|Permai, 9.06 9.48|Changlun. 9.48 9.84
Rumah 9.90 10.16|siap 10.16 10.24|dah, 10.24 10.38|tinggal 10.38 10.76|nak 10.76 10.92|buat 10.92 11.10|pagar. 11.10 11.48
And 11.50 11.68|then 11.68 11.92|infra 11.92 12.22|sikit, 12.22 12.82
anggaran 13.26 13.78|CCC 13.78 14.06|tahun 14.06 14.32|depan 14.32 14.60|lah. 14.60 14.66
Jadi 14.72 14.92|yang 14.92 15.02|mana 15.02 15.18|berminat 15.18 15.70|nak 15.70 15.82|cari 15.82 16.22|rumah 16.22 16.40|mampu 16.40 16.86|milik, 16.86 17.22
mampu 17.34 17.86|beli 17.86 18.20|dekat 18.20 18.62|Changlun, 18.62 18.94
tekan 18.96 19.28|link 19.28 19.42|di 19.42 19.58|bio 19.58 19.82|Taman 19.82 20.30|Keriang 20.36 20.76|Permai. 20.76 21.08"""
words = []
for line in W.splitlines():
    for tok in line.split("|"):
        t, s, e = tok.rsplit(" ", 2)
        words.append({"text": t, "start": float(s), "end": float(e)})

# group sizes (by word count), in order
SIZES = [3, 3, 2, 3, 1, 2, 3, 2, 4, 2, 3, 1, 3, 4, 4, 2, 3, 4, 3, 2, 2, 2, 4, 3]
EMPH = {"tak", "banjir.", "tenggelam", "RM1,200", "teres", "siap", "CCC", "mampu", "milik,", "beli", "link", "bio"}
assert sum(SIZES) == len(words), (sum(SIZES), len(words))

groups, i = [], 0
for n in SIZES:
    groups.append(words[i:i + n]); i += n

FILM_END = 21.8
out_groups = []
for gi, g in enumerate(groups):
    start = max(0.08, g[0]["start"] - 0.04)
    nxt = groups[gi + 1][0]["start"] - 0.04 if gi + 1 < len(groups) else FILM_END
    end = min(nxt, g[-1]["end"] + 0.45)
    if gi == len(groups) - 1:
        end = 21.6
    out_groups.append((start, end, g))

parts, data = [], []
for gi, (s, e, g) in enumerate(out_groups):
    spans = []
    wd = []
    for wi, w in enumerate(g):
        cls = "cw emph" if w["text"].strip(",.").rstrip(",.") in {x.strip(",.") for x in EMPH} else "cw"
        spans.append(f'<span id="cw-{gi}-{wi}" class="{cls}"><span class="cw-hl"></span><b class="base">{html.escape(w["text"])}</b><b class="act">{html.escape(w["text"])}</b></span>')
        nxt = g[wi + 1]["start"] if wi + 1 < len(g) else e
        wd.append([round(w["start"], 2), round(nxt, 2)])
    parts.append(f'      <div id="cg-{gi}" class="cg">{" ".join(spans)}</div>')
    data.append({"s": round(s, 2), "e": round(e, 2), "w": wd})

tpl = pathlib.Path(__file__).with_name("captions.template.html").read_text()
out = tpl.replace("<!--GROUPS-->", "\n".join(parts)).replace("/*DATA*/[]", json.dumps(data))
dst = pathlib.Path(__file__).parents[1] / "site-notes/compositions/captions.html"
dst.write_text(out)
print("groups", len(out_groups))
for s, e, g in out_groups:
    print(f"{s:5.2f}-{e:5.2f}  {' '.join(w['text'] for w in g)}")
