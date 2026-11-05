import subprocess,sys,json
src,out_v,out_a=sys.argv[1:4]
SEG=[(0.30,2.62),(2.96,4.95),(4.95,5.24),(5.70,6.24),(6.24,9.82),(10.00,13.40),(13.40,15.22),
     (21.88,22.86),(23.28,24.36),(26.46,27.92),(27.92,29.52),(29.96,33.34),(19.40,21.62)]
fc=[];n=len(SEG)
for i,(s,e) in enumerate(SEG):
    d=e-s
    fc.append(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}]")
    fc.append(f"[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,afade=t=in:d=0.015,afade=t=out:st={d-0.02:.3f}:d=0.02[a{i}]")
fc.append("".join(f"[v{i}][a{i}]" for i in range(n))+f"concat=n={n}:v=1:a=1[v][a]")
subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-filter_complex",";".join(fc),"-map","[v]","-c:v","libx264","-preset","slow","-crf","15","-g","60","-pix_fmt","yuv420p","-color_primaries","bt709","-color_trc","bt709","-colorspace","bt709","-movflags","+faststart",out_v,
  "-map","[a]","-ac","1","-ar","48000","-c:a","pcm_s16le",out_a],check=True)
t=0;marks=[]
for s,e in SEG: marks.append((round(t,3),s,e)); t+=e-s
print(json.dumps({"total":round(t,3),"segs":marks}))
