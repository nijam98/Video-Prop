"""Cut the source clip into the edit timeline.

usage: python3 tools/cut.py SOURCE.mov
writes assets/footage.mp4 (video only), build/voice_raw.wav, build/timeline.json

Each piece: (audio_start, audio_end, pad, video) — times in SOURCE seconds.
  pad   = seconds of silence added after the voice (footage keeps rolling)
  video = None -> same range as the audio (plus pad), or a list of (s, e) B-roll ranges
"""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30

PIECES = [
    # HOOK: line recorded at the very end of the clip, over a 4-shot montage
    ("hook",   63.15, 67.02, 0.50, [(6.00, 7.10), (1.80, 2.90), (26.00, 27.10), (61.90, 62.97)]),
    ("lokasi", 3.80, 6.75, 0.30, None),     # kawasan ... dekat dengan semua kemudahan
    ("reno",   9.58, 15.42, 0.00, None),    # fully renovated depan sampai belakang, nampak cantik? siap plaster ceiling
    ("lampu",  15.90, 19.64, 0.00, None),   # sampai ke belakang, siap lampu, grill
    ("utama",  20.18, 22.70, 0.30, None),   # yang ni bilik utama, built-in 1 tandas
    ("bilik",  23.58, 29.95, 0.00, None),   # 3 bilik 2 tandas, freehold, non-bumi, jadi semua boleh beli
    ("semua",  30.37, 31.70, 0.40, None),   # tak ada yang berkecuali
    ("kedua",  32.02, 34.15, 0.00, None),   # yang ni bilik yang kedua
    ("luas",   34.55, 38.50, 0.50, None),   # berkeluasan 1194 sqft
    ("makan",  39.00, 42.48, 0.00, None),   # ruang makan, partition
    ("dapur",  43.52, 45.88, 0.00, None),   # depan ni ada ruang dapur
    ("tiles",  46.28, 50.85, 0.00, None),   # fully tiles, tabletop, tandas kedua
    ("akhir",  51.25, 62.56, 3.58, None),   # bilik ketiga, RM370k, tekan link, loan A-Z + end hold
]


def main(src):
    os.makedirs(os.path.join(HERE, "build"), exist_ok=True)
    fc, vlab, alab = [], [], []
    t, marks = 0.0, []
    vi = 0
    for i, (name, a0, a1, pad, video) in enumerate(PIECES):
        d = a1 - a0
        fc.append(f"[0:a]atrim={a0}:{a1},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,"
                  f"afade=t=out:st={d-0.02:.3f}:d=0.02,apad=pad_dur={pad}[a{i}]")
        alab.append(f"[a{i}]")
        ranges = video or [(a0, a1 + pad)]
        for (s, e) in ranges:
            fc.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{vi}]")
            vlab.append(f"[v{vi}]"); vi += 1
        marks.append({"name": name, "t": round(t, 3), "src": a0, "voice_end": round(t + d, 3), "end": round(t + d + pad, 3)})
        t += d + pad
    grade = "eq=contrast=1.06:saturation=1.14:gamma=0.98,unsharp=5:5:0.35,format=yuv420p"
    fc.append("".join(vlab) + f"concat=n={len(vlab)}:v=1:a=0,fps={FPS},{grade}[v]")
    fc.append("".join(alab) + f"concat=n={len(alab)}:v=0:a=1[a]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", ";".join(fc),
                    "-map", "[v]", "-an", "-c:v", "libx264", "-preset", "slow", "-crf", "14", "-g", "30",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
                    "-movflags", "+faststart", os.path.join(HERE, "assets/footage.mp4"),
                    "-map", "[a]", "-ac", "1", "-ar", "48000", "-c:a", "pcm_s16le",
                    os.path.join(HERE, "build/voice_raw.wav")], check=True)
    out = {"total": round(t, 3), "pieces": marks}
    json.dump(out, open(os.path.join(HERE, "build/timeline.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(sys.argv[1])
