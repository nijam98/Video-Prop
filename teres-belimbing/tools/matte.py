#!/usr/bin/env python3
"""Person matte for the "subtitles behind the presenter" layer.

Runs RobustVideoMatting (mobilenetv3 / resnet50 torchscript) over assets/footage.mp4 and writes
assets/person.webm: VP9 with alpha, RGB = footage, A = presenter matte (same frame rate + timing as footage).
Only the source ranges where the presenter is on screen (RANGES) are matted; other frames get alpha 0.
Small blobs (hanging lamps, fan blades) are dropped: only the biggest connected shape and shapes touching
its box survive.
Usage: python3 tools/matte.py /path/to/rvm_xxx.torchscript [start_s] [dur_s] [out]
"""
import subprocess, sys, time, os
import numpy as np, torch
from scipy import ndimage

RANGES = [(0.2, 4.9), (10.1, 22.7), (29.4, 31.8), (36.9, 43.0), (44.7, 51.1), (54.5, 61.1), (67.6, 68.7),
          (71.4, 72.9), (82.1, 91.1)]


def keep_person(a):
    small = a[::4, ::4] > 128
    lab, n = ndimage.label(small)
    if n == 0:
        return a
    sizes = ndimage.sum(small, lab, range(1, n + 1))
    big = int(np.argmax(sizes)) + 1
    if sizes[big - 1] < 600:  # under ~1% of the frame: no presenter
        return np.zeros_like(a)
    sl = ndimage.find_objects(lab)[big - 1]
    y0, y1, x0, x1 = sl[0].start - 6, sl[0].stop + 6, sl[1].start - 6, sl[1].stop + 6
    keep = np.zeros(n + 1, bool); keep[big] = True
    for i, s_ in enumerate(ndimage.find_objects(lab), 1):
        if s_ and sizes[i - 1] > 40 and s_[0].start < y1 and s_[0].stop > y0 and s_[1].start < x1 and s_[1].stop > x0:
            keep[i] = True
    m = ndimage.binary_dilation(keep[lab], iterations=3)
    m = np.kron(m, np.ones((4, 4), bool))[:a.shape[0], :a.shape[1]]
    return np.where(m, a, 0).astype(np.uint8)


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = sys.argv[1]
ss = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
dur = float(sys.argv[3]) if len(sys.argv) > 3 else None
out = sys.argv[4] if len(sys.argv) > 4 else os.path.join(ROOT, "assets", "person.webm")
W, H, FPS = 1080, 1920, 60
torch.set_num_threads(4)
model = torch.jit.load(model_path).eval()

src = os.path.join(ROOT, "assets", "footage.mp4")
rd = ["ffmpeg", "-v", "error", "-ss", str(ss)] + (["-t", str(dur)] if dur else []) + ["-i", src, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
wr = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
      "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "30", "-deadline", "good", "-cpu-used", "4",
      "-row-mt", "1", "-auto-alt-ref", "0", "-g", "30", out]
pr = subprocess.Popen(rd, stdout=subprocess.PIPE)
pw = subprocess.Popen(wr, stdin=subprocess.PIPE)
rec = [None] * 4
n, t0 = 0, time.time()
with torch.no_grad():
    while True:
        buf = pr.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        fr = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        t = ss + n / FPS
        if any(r0 <= t <= r1 for r0, r1 in RANGES):
            x = torch.from_numpy(fr.copy()).permute(2, 0, 1).float().div(255).unsqueeze(0)
            fgr, pha, *rec = model(x, *rec, 0.25)
            a = keep_person((pha[0, 0].clamp(0, 1).numpy() * 255).astype(np.uint8))
        else:
            rec = [None] * 4
            a = np.zeros((H, W), np.uint8)
        rgb = np.where((a > 0)[..., None], fr, 0).astype(np.uint8)  # black where clear: smaller file
        pw.stdin.write(np.dstack([rgb, a]).tobytes())
        n += 1
        if n % 300 == 0:
            print(f"{n} frames, {n / (time.time() - t0):.1f} fps", flush=True)
pw.stdin.close(); pw.wait(); pr.wait()
print(f"done {n} frames in {time.time() - t0:.0f}s -> {out}")
