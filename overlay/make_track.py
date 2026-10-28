"""Slice captions, callouts and smoothed head track for one part (times made relative to the part start)."""
import json, sys, math
caps_f, calls_f, head_f, start, end, out = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), sys.argv[6]
caps = json.load(open(caps_f)); calls = json.load(open(calls_f)); head = json.load(open(head_f))
DEF_X, DEF_Y = 540, 600
xs = [h.get("hx", h.get("x")) if h["ok"] else DEF_X for h in head]
ys = [h["top"] if h["ok"] else DEF_Y for h in head]
xs = [min(max(x, 0), 1080) for x in xs]
def smooth(a, sigma=5):
    k = [math.exp(-(i * i) / (2 * sigma * sigma)) for i in range(-3 * sigma, 3 * sigma + 1)]
    out = []
    for i in range(len(a)):
        s = w = 0
        for j, kk in enumerate(k):
            idx = min(max(i + j - 3 * sigma, 0), len(a) - 1)
            s += a[idx] * kk; w += kk
        out.append(round(s / w, 1))
    return out
xs, ys = smooth(xs), smooth(ys)
dt = head[1]["t"] - head[0]["t"]
i0 = int(start / dt); i1 = int(end / dt) + 2
rel = lambda t: round(t - start, 3)
data = {
    "captions": [{"s": rel(c["s"]), "e": rel(c["e"]), "words": [{"w": w["w"], "s": rel(w["s"]), "e": rel(w["e"])} for w in c["words"]]}
                 for c in caps if c["s"] >= start - 0.05 and c["s"] < end],
    "callouts": [{"s": rel(c["s"]), "e": rel(c["e"]), "text": c["text"], "emoji": c.get("emoji", "")} for c in calls if c["s"] >= start and c["s"] < end],
    "head": {"dt": dt, "x": xs[i0:i1], "y": ys[i0:i1]},
}
off = start - i0 * dt  # head index 0 is this many seconds before the part start (< one sample)
json.dump(data, open(out, "w"), ensure_ascii=False)
print(out, len(data["captions"]), "captions", len(data["callouts"]), "callouts", f"head offset {off:.3f}s")
