"""Cut base1080.mov (1080x1920 60fps, tone-mapped) into assets/footage.mp4 + voice_raw.wav.

Usage: python3 tools_cut.py base1080.mov assets/footage.mp4 voice_raw.wav
Prints the cut-timeline position of every segment (used for timings in build.py).
"""
import json, subprocess, sys

# (source start, source end) in seconds, in play order
SEG = [
    (42.28, 43.06),  # hook: "Rumah ni akan"
    (43.66, 45.60),  #       "bebas banjir, jangan risau"
    (0.18, 2.66),    # "Ok, progres terkini Taman Keriang Permai Changlun"
    (2.89, 4.90),    # "siap dengan dah basuh batu"
    (5.26, 6.37),    # "dan rumah pun dah"
    (7.03, 8.78),    # "hampir siap lah, lebih kurang 80% lah"
    (9.29, 11.88),   # "unit pun tak banyak lah, unit pun hampir separuh lah, dah ..."
    (15.13, 18.50),  # "rumah medium cost, 3 bilik, 2 tandas"
    (19.96, 22.30),  # "unit end lot ada lagi, unit corner lot pun ada lagi"
    (23.14, 24.12),  # "right, ni ruang master"
    (24.54, 26.36),  # "bedroom, bilik yang kedua"
    (27.64, 29.08),  # "bilik yang ketiga"
    (29.58, 30.60),  # "right, ni ruang makan"
    (31.04, 31.74),  # "dan dapur"
    (39.24, 41.78),  # "yang memang minat nak cari rumah kat Changlun, Taman Keriang Permai"
    (13.44, 15.10),  # CTA: "macam biasa, tekan link dekat bio ni"
]
TAIL = (15.10, 16.50)  # video only, holds the CTA after the voice ends



def cut_time(src_t):
    """Map a source time to the cut timeline."""
    pos = 0.0
    for s, e in SEG:
        if s - 0.05 <= src_t <= e + 0.05:
            return round(pos + max(0.0, src_t - s), 3)
        pos += e - s
    raise ValueError(f"{src_t} is cut out")


TOTAL = round(sum(e - s for s, e in SEG) + TAIL[1] - TAIL[0], 3)


def main():
    src, out_v, out_a = sys.argv[1:4]
    fc = []
    n = len(SEG)
    for i, (s, e) in enumerate(SEG):
        d = e - s
        fc.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}]")
        fc.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d - 0.02:.3f}:d=0.02[a{i}]")
    ts, te = TAIL
    fc.append(f"[0:v]trim={ts}:{te},setpts=PTS-STARTPTS[vt]")
    fc.append(f"anullsrc=r=48000:cl=mono,atrim=0:{te - ts}[at]")
    fc.append("".join(f"[v{i}][a{i}]" for i in range(n)) + f"[vt][at]concat=n={n + 1}:v=1:a=1[v][a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", ";".join(fc),
                    "-map", "[v]", "-r", "60", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-g", "60",
                    "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-movflags", "+faststart", "-an", out_v,
                    "-map", "[a]", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le", out_a], check=True)
    t = 0
    marks = []
    for s, e in SEG + [TAIL]:
        marks.append((round(t, 3), s, e))
        t += e - s
    print(json.dumps({"total": round(t, 3), "segs": marks}))


if __name__ == "__main__":
    main()
