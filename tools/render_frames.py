"""Render an overlay's 2 s intro + 4 s seamless loop as PNG sequences (in parallel).

Usage: render_frames.py part1|part2 OUTDIR [--check]
Writes OUTDIR/intro_0000.png.. (120 frames) and OUTDIR/loop_0000.png.. (240 frames),
plus OUTDIR/band.txt with "y height" of the overlay band in the 4K frame.
"""
import os
import sys
from multiprocessing import Pool

import numpy as np

from common import FPS

INTRO, LOOP = 2 * FPS, 4 * FPS
_r = None


def load(part):
    if part == "part1":
        from part1_y2k import Part1
        r = Part1()
        return r, r.band_y
    from part2_iso import Part2
    return Part2(), 0


def init(part):
    global _r
    _r = load(part)[0]


def job(args):
    i, out = args
    name = f"intro_{i:04d}.png" if i < INTRO else f"loop_{i - INTRO:04d}.png"
    _r.frame(i / FPS).save(os.path.join(out, name), compress_level=1)
    return i


def main():
    part, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    r, band_y = load(part)
    if "--check" in sys.argv:
        for t0 in (2.0, 3.3, 5.5):
            a = np.asarray(r.frame(t0)).astype(int)
            b = np.asarray(r.frame(t0 + 4.0)).astype(int)
            print(f"t={t0}: max diff vs t+4s = {np.abs(a - b).max()}")
        return
    first = r.frame(0)
    with open(os.path.join(out, "band.txt"), "w") as f:
        f.write(f"{band_y} {first.height}\n")
    with Pool(4, initializer=init, initargs=(part,)) as pool:
        for n, _ in enumerate(pool.imap_unordered(job, [(i, out) for i in range(INTRO + LOOP)],
                                                  chunksize=4)):
            if n % 60 == 0:
                print(part, n, file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
