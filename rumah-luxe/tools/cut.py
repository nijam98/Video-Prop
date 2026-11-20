"""--native: write work/cut_native.mp4 (source res, for tools/sr.py). --sr FILE: use an upscaled cut as the video source (already cut; trims skipped).
Build the cut: assets/footage.mp4 (video only, 1080x1920 30fps) + work/voice_cut.wav + tools/cutmap.json.
usage: python3 tools/cut.py SRC.mp4 [--sr SR_SOURCE.mp4]"""
import json, subprocess, sys, os
here = os.path.dirname(os.path.abspath(__file__)); root = os.path.dirname(here)
src = sys.argv[1]
vsrc = sys.argv[sys.argv.index('--sr')+1] if '--sr' in sys.argv else src
edl = json.load(open(os.path.join(here, 'edl.json')))
FPS = 30
def q(t): return round(t * FPS) / FPS          # snap to frame grid
vparts, aparts, cutmap, t = [], [], [], 0.0
for (s, e) in edl['hook']['video']:
    s, e = q(s), q(e); vparts.append((s, e)); cutmap.append({"id": "hook", "src": [s, e], "out": [round(t,3), round(t+e-s,3)]}); t += e - s
hook_len = t
hs, he = edl['hook']['audio']; off = edl['hook']['audio_offset']
aparts.append(('sil', off)); aparts.append((hs, he)); aparts.append(('sil', hook_len - off - (he - hs)))
for seg in edl['segments']:
    s, e = map(q, seg['v']); vparts.append((s, e)); aparts.append((s, e))
    cutmap.append({"id": seg['id'], "src": [s, e], "out": [round(t,3), round(t+e-s,3)]}); t += e - s
total = round(t, 3)
# video graph
native = '--native' in sys.argv
scale = "scale=1080:1920:flags=lanczos,unsharp=5:5:0.6:5:5:0.0" if vsrc == src else "null"
if native: scale = "null"
vout = os.path.join(root, "work/cut_native.mp4" if native else "assets/footage.mp4")
fc = []
for i, (s, e) in enumerate(vparts):
    fc.append(f"[0:v]trim=start={s}:end={e},setpts=PTS-STARTPTS[v{i}]")
fc.append("".join(f"[v{i}]" for i in range(len(vparts))) + f"concat=n={len(vparts)}:v=1:a=0,fps={FPS},{scale},format=yuv420p[vo]")
os.makedirs(os.path.join(root, 'work'), exist_ok=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", vsrc, "-filter_complex", ";".join(fc), "-map", "[vo]",
    "-c:v", "libx264", "-crf", "8" if native else "14", "-preset", "medium", "-g", str(FPS), "-an", vout], check=True)
# audio graph (10 ms fades at every edge)
fa, n = [], 0
for p in aparts:
    if p[0] == 'sil':
        if p[1] > 0.001: fa.append(f"anullsrc=r=48000:cl=mono,atrim=duration={p[1]:.4f}[a{n}]"); n += 1
    else:
        s, e = p; d = e - s
        fa.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,aformat=sample_rates=48000:channel_layouts=mono,afade=t=in:d=0.012,afade=t=out:st={d-0.015:.4f}:d=0.015[a{n}]"); n += 1
fa.append("".join(f"[a{i}]" for i in range(n)) + f"concat=n={n}:v=0:a=1[ao]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-filter_complex", ";".join(fa), "-map", "[ao]",
    "-c:a", "pcm_s16le", os.path.join(root, "work/voice_cut.wav")], check=True)
json.dump({"total": total, "hook_len": round(hook_len,3), "clips": cutmap}, open(os.path.join(here, 'cutmap.json'), 'w'), indent=1)
print("total", total)
