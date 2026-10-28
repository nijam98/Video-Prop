"""Build caption chunks with per-word timing.
Corrected segment text is aligned to Whisper's word timestamps; unmatched words get interpolated times."""
import json, re, sys, difflib

def norm(w): return re.sub(r"[^\w]", "", w.lower())

def build(transcript, corrections, max_words=4, max_chars=24):
    out = []
    for i, seg in enumerate(transcript):
        key = str(i)
        if key in corrections and corrections[key] is None:
            continue
        text = corrections.get(key) or seg["text"]
        words = text.split()
        ww = seg["words"]
        a = [norm(x["w"]) for x in ww]; b = [norm(x) for x in words]
        times = [None] * len(words)
        for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
            for k in range(blk.size):
                times[blk.b + k] = (ww[blk.a + k]["s"], ww[blk.a + k]["e"])
        # interpolate missing timings across the segment
        s0, s1 = seg["start"], seg["end"]
        n = len(words)
        for k in range(n):
            if times[k] is None:
                prev = next((times[j][1] for j in range(k - 1, -1, -1) if times[j]), s0)
                nxt_i = next((j for j in range(k + 1, n) if times[j]), None)
                nxt = times[nxt_i][0] if nxt_i is not None else s1
                gap = sum(1 for j in range(k, nxt_i if nxt_i is not None else n) if times[j] is None)
                step = (nxt - prev) / max(gap, 1)
                times[k] = (prev, prev + step)
        # split into phrases at punctuation, then balance each phrase into even chunks
        phrases, cur = [], []
        for w, t in zip(words, times):
            cur.append((w, t[0], t[1]))
            if re.search(r"[.?!,]$", w): phrases.append(cur); cur = []
        if cur: phrases.append(cur)
        merged = []
        for ph in phrases:  # glue 1-word phrases onto the next one
            if merged and len(merged[-1]) == 1:
                merged[-1] = merged[-1] + ph
            else:
                merged.append(ph)
        for ph in merged:
            chars = len(" ".join(x[0] for x in ph))
            k = max(-(-len(ph) // max_words), -(-chars // max_chars))
            size = -(-len(ph) // k)
            for j in range(0, len(ph), size):
                c = ph[j:j + size]
                out.append({"s": c[0][1], "e": c[-1][2], "words": [{"w": w, "s": s, "e": e} for w, s, e in c]})
    # hold each chunk until the next one starts (max +0.6s)
    for k, c in enumerate(out):
        nxt = out[k + 1]["s"] if k + 1 < len(out) else c["e"] + 0.6
        c["e"] = min(max(c["e"], c["s"] + 0.5), nxt, c["e"] + 0.6) if nxt > c["s"] else c["e"]
    return out

if __name__ == "__main__":
    tr = json.load(open(sys.argv[1])); cor = json.load(open(sys.argv[2]))
    caps = build(tr, cor)
    json.dump(caps, open(sys.argv[3], "w"), ensure_ascii=False, indent=1)
    for c in caps: print(f'{c["s"]:7.2f}-{c["e"]:7.2f}  {" ".join(w["w"] for w in c["words"])}')
