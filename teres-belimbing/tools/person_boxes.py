#!/usr/bin/env python3
"""Measures where the presenter is in every segment (from assets/person.webm) -> tools/person-boxes.json.

build.py uses the head height to drop the big serif subtitles just over the presenter's head/shoulders,
so they read as sitting behind him. Run after tools/matte.py:
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


boxes = {}
for sg in build.EDL:
    tops, area = [], 0
    for src, d in seg_pictures(sg):
        for k in range(4):
            a = alpha_at(src + d * (0.15 + 0.7 * k / 3))
            if a is None:
                continue
            m = a > 128
            rows = np.where(m.sum(1) > 6)[0]
            if m.sum() > 9000 and len(rows):
                tops.append(int(rows[0]))
                area = max(area, int(m.sum()))
    boxes[sg["id"]] = {"top": int(np.median(tops)), "samples": len(tops), "area": area} if tops else None
    print(sg["id"], boxes[sg["id"]])
json.dump(boxes, open(os.path.join(ROOT, "tools", "person-boxes.json"), "w"), indent=1)
