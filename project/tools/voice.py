import subprocess, json, re, sys
src, out = sys.argv[1], sys.argv[2]
CH="highpass=f=85,afftdn=nr=8:nf=-45,equalizer=f=220:t=q:w=1.2:g=-2.5,equalizer=f=3200:t=q:w=1:g=2.5,equalizer=f=9000:t=q:w=1:g=1.5,acompressor=threshold=-22dB:ratio=3:attack=8:release=120:makeup=2"
r=subprocess.run(["ffmpeg","-hide_banner","-i",src,"-vn","-ac","1","-ar","48000","-af",CH+",loudnorm=I=-15:TP=-1.5:LRA=7:print_format=json","-f","null","-"],capture_output=True,text=True).stderr
d=json.loads(r[r.rindex("{"):r.rindex("}")+1]); print(d)
ln=f"loudnorm=I=-15:TP=-1.5:LRA=7:measured_I={d['input_i']}:measured_TP={d['input_tp']}:measured_LRA={d['input_lra']}:measured_thresh={d['input_thresh']}:offset={d['target_offset']}:linear=true,aresample=48000,volume=3dB,alimiter=limit=0.82:attack=2:release=60:level=disabled"
subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-vn","-ac","1","-ar","48000","-af",CH+","+ln,"-c:a","pcm_s16le",out],check=True)
r=subprocess.run(["ffmpeg","-hide_banner","-i",out,"-af","ebur128=peak=true","-f","null","-"],capture_output=True,text=True).stderr
print("\n".join(l for l in r.splitlines()[-12:] if "I:" in l or "Peak:" in l))
