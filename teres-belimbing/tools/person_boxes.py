#!/usr/bin/env python3
"""Measures where the presenter is in every segment (from assets/person.webm) -> tools/person-boxes.json.

build.py uses the head height to drop the big serif subtitles just over the presenter's head/shoulders,
so they read as sitting behind him, and the occupancy map (share of sampled frames where each 20 px cell is
the presenter) to park the key-point cards where they do not cover him. Run after tools/matte.py:
    python3 tools/person_boxes.py && python3 tools/build.py
"""
import json, os, subprocess, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402  (tables only; build() is not run)

ROOT = build.ROOT
W, H = 1080, 1920
SRC = os.path.join(ROOT, "assets", "person.webm")


def alpha_at(t):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-c:v", "libvpx-vp9", "-ss", f"{t:.3f}", "-i", SRC, "-frames:v", "1",
                          "-vf", "alphaextract", "-f", "rawvideo", "-pix_fmt", "gray", "-"], capture_output=True).stdout
    if len(raw) < W * H:
        return None
    return np.frombuffer(raw[:W * H], np.uint8).reshape(H, W)


def seg_pictures(sg):
    """source (in, dur) of the picture pieces of one segment, voice part only"""
    if sg.get("pics"):
        out, acc = [], 0.0
        for src, d in sg["pics"]:
            d = min(d, sg["dur"] - acc)
            if d > 0.05:
                out.append((src, d))
            acc += d
        return out
    return [(a0, a1 - a0) for a0, a1 in sg["parts"]]


CELL = 20
boxes = {}
tail = dict(id="tail", pics=[(0.40, build.TAIL)], dur=build.TAIL)
for sg in build.EDL + [tail]:
    tops, area, occ, n = [], 0, np.zeros((H // CELL, W // CELL)), 0
    for src, d in seg_pictures(sg):
        K = max(3, int(d * 3))
        for k in range(K):
            a = alpha_at(src + d * (0.05 + 0.9 * k / (K - 1)))
            if a is None:
                continue
            m = a > 128
            occ += m.reshape(H // CELL, CELL, W // CELL, CELL).mean(axis=(1, 3)) > 0.08
            n += 1
            rows = np.where(m.sum(1) > 6)[0]
            if m.sum() > 9000 and len(rows):
                tops.append(int(rows[0]))
                area = max(area, int(m.sum()))
    occ = occ / max(1, n)
    boxes[sg["id"]] = {"top": int(np.median(tops)) if tops else None, "samples": len(tops), "area": area,
                       "occ": [[round(float(v), 2) for v in row] for row in occ]}
    print(sg["id"], {k: v for k, v in boxes[sg["id"]].items() if k != "occ"})
json.dump(boxes, open(os.path.join(ROOT, "tools", "person-boxes.json"), "w"))
