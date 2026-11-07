import json, wave, numpy as np, subprocess, os
SRC="dl/src.mp4"; OUT="work"
w=wave.open("dl/audio.wav"); A=np.frombuffer(w.readframes(w.getnframes()),np.int16).astype(np.float32)/32768
def snap(t,r=0.12):
    # move cut point to quietest 20ms window nearby
    best=t;bv=9
    for c in np.arange(t-r,t+r+1e-6,0.01):
        s=int(c*16000); e=s+320
        if s<0 or e>len(A): continue
        v=np.sqrt((A[s:e]**2).mean())
        if v<bv: bv=v;best=c
    return round(float(best),3)
# sections: audio pieces + video pieces (last video piece auto-adjusted to fit)
SECTIONS=[
 dict(name="hook", audio=[(93.14,96.78)], video=[(45.0,48.7)]),
 dict(name="intro",audio=[(0.0,7.50)],   video=[(0.0,7.50)]),
 dict(name="spec", audio=[(9.10,20.02)], video=[(63.0,67.0),(69.5,71.5),(12.0,None)]),
 dict(name="park", audio=[(22.78,27.50),(29.36,32.86)], video=[(21.0,24.5),(16.95,19.0),(74.0,None)]),
 dict(name="reno", audio=[(43.22,54.10)], video=[(33.0,39.45),(41.5,44.0),(10.0,None)]),
 dict(name="furn", audio=[(72.84,80.80)], video=[(48.7,51.5),(105.5,108.6),(59.0,None)]),
 dict(name="loc",  audio=[(96.74,104.42)],video=[(81.0,83.5),(89.0,92.0),(108.6,None)]),
 dict(name="cta",  audio=[(106.94,110.48)],video=[(27.5,None)]),
]
apieces=[];vpieces=[];t=0;secinfo=[]
for S in SECTIONS:
    aps=list(S["audio"])
    dur=sum(b-a for a,b in aps)
    used=sum(b-a for a,b in S["video"] if b is not None)
    vs=[(a,b if b is not None else a+(dur-used)) for a,b in S["video"]]
    secinfo.append(dict(name=S["name"],start=t,dur=dur,audio=aps))
    apieces+=aps; vpieces+=vs; t+=dur
total=t; tempo=total/60.0
print("total",round(total,3),"tempo",round(tempo,4))
for s in secinfo: print(s["name"],round(s["start"],2),round(s["dur"],2),s["audio"])
json.dump(dict(sections=secinfo,total=total,tempo=tempo,vpieces=vpieces),open(f"{OUT}/edl.json","w"),indent=1)
# audio: trim pieces with 25ms fades, concat, tempo -> 60s
fc=[];
for i,(a,b) in enumerate(apieces):
    d=b-a
    fc.append(f"[0:a]atrim={a}:{b},asetpts=PTS-STARTPTS,afade=t=in:d=0.025,afade=t=out:st={d-0.03:.3f}:d=0.03[a{i}]")
fc.append("".join(f"[a{i}]" for i in range(len(apieces)))+f"concat=n={len(apieces)}:v=0:a=1,atempo={tempo:.5f},afade=t=out:st=59.6:d=0.4,loudnorm=I=-14:TP=-1.0:LRA=11[aout]")
subprocess.run(["ffmpeg","-v","error","-y","-i",SRC,"-filter_complex",";".join(fc),"-map","[aout]","-ar","48000","-c:a","pcm_s16le",f"{OUT}/audio60.wav"],check=True)
# video pieces -> each interpolated to 60fps separately (no blending across cuts)
os.makedirs(f"{OUT}/clips",exist_ok=True)
lst=open(f"{OUT}/clips/list.txt","w")
for i,(a,b) in enumerate(vpieces):
    fn=f"{OUT}/clips/c{i:02d}.mkv"
    subprocess.run(["ffmpeg","-v","error","-y","-ss",f"{a:.3f}","-i",SRC,"-t",f"{b-a:.3f}","-an","-vf",
      "fps=30,minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=fdiff","-c:v","ffv1",fn],check=True)
    lst.write(f"file 'c{i:02d}.mkv'\n"); print("clip",i,a,round(b,3),flush=True)
lst.close()
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",f"{OUT}/clips/list.txt","-vf",f"setpts=(PTS-STARTPTS)/{tempo:.5f},fps=60","-frames:v","3600","-c:v","ffv1",f"{OUT}/cut60.mkv"],check=True)
print(subprocess.run(["ffprobe","-v","error","-count_frames","-show_entries","stream=nb_read_frames,width,height,r_frame_rate","-of","csv=p=0",f"{OUT}/cut60.mkv"],capture_output=True,text=True).stdout)
