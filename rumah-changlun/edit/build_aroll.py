"""Cut the A-roll from the EDL: video (silent) + cleaned voice track, and remap word timings.
usage: python3 build_aroll.py <proxy.mp4> <audio48k.wav> <transcript.json> <project_dir>
"""
import json, subprocess, sys, os
proxy, wav, tjson, proj = sys.argv[1:5]
here = os.path.dirname(os.path.abspath(__file__))
edl = json.load(open(os.path.join(here, "edl.json")))["segments"]
FPS = 30
snap = lambda t: round(t * FPS) / FPS
vf, af, out_t = [], [], 0.0
remap = []
for i, s in enumerate(edl):
    a, b = snap(s["in"]), snap(s["out"])
    d = b - a
    vf.append(f"[0:v]trim=start={a:.4f}:end={b:.4f},setpts=PTS-STARTPTS[v{i}]")
    af.append(f"[1:a]atrim=start={a:.4f}:end={b:.4f},asetpts=PTS-STARTPTS,afade=t=in:d=0.012,afade=t=out:st={d-0.02:.4f}:d=0.02[a{i}]")
    remap.append({"id": s["id"], "src_in": a, "src_out": b, "out_in": round(out_t, 4), "out_out": round(out_t + d, 4), "text": s["text"]})
    out_t += d
n = len(edl)
fc = ";".join(vf + af) + ";" + "".join(f"[v{i}]" for i in range(n)) + f"concat=n={n}:v=1:a=0[v];" + "".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[a]"
# voice cleanup: rumble cut, gentle denoise, presence, compression, then loudness target
fc += ";[a]highpass=f=90,afftdn=nf=-30:nt=w,equalizer=f=250:t=q:w=1:g=-2,equalizer=f=3200:t=q:w=1:g=2.5,acompressor=threshold=-22dB:ratio=3:attack=6:release=90:makeup=3,loudnorm=I=-16:TP=-2:LRA=8,aresample=48000[ao]"
os.makedirs(os.path.join(proj, "assets"), exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", proxy, "-i", wav, "-filter_complex", fc,
                "-map", "[v]", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-g", "30", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", os.path.join(proj, "assets", "aroll.mp4"),
                "-map", "[ao]", "-c:a", "pcm_s16le", os.path.join(proj, "assets", "voice.wav")], check=True)
# word remap
words = [w for seg in json.load(open(tjson)) for w in seg["words"]]
out_words = []
for r in remap:
    for w in words:
        mid = (w["s"] + w["e"]) / 2
        if r["src_in"] <= mid < r["src_out"]:
            out_words.append({"text": w["w"].strip(), "start": round(max(w["s"], r["src_in"]) - r["src_in"] + r["out_in"], 3),
                              "end": round(min(w["e"], r["src_out"]) - r["src_in"] + r["out_in"], 3), "seg": r["id"]})
json.dump({"duration": round(out_t, 4), "segments": remap, "words": out_words}, open(os.path.join(here, "timeline.json"), "w"), indent=1, ensure_ascii=False)
print("total", round(out_t, 3), "segments", n, "words", len(out_words))
