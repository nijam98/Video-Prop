"""Two-pass loudnorm to -14 LUFS / -1.5 dBTP for TikTok & Reels; video stream copied."""
import json, re, subprocess, sys
src, dst = sys.argv[1], sys.argv[2]
base = "loudnorm=I=-14:TP=-1.5:LRA=11"
err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-map", "0:a", "-af", base + ":print_format=json",
                      "-f", "null", "-"], capture_output=True, text=True).stderr
d = json.loads(re.search(r"\{[^{}]*\"input_i\"[^{}]*\}", err).group(0))
f = (f"{base}:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}"
     f":measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-c:v", "copy", "-af", f, "-ar", "48000", "-c:a", "aac", "-b:a", "256k",
                "-movflags", "+faststart", dst, "-y"], check=True)
print("input", d["input_i"], "LUFS, tp", d["input_tp"], "->", dst)
