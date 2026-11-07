# AI-upscale the 30fps cut (478x850) to 1080x1920 with Real-ESRGAN general-x4v3 (made for real photos,
# keeps texture natural), then make 60fps at full 1080 so in-between frames stay sharp.
# usage: python3 sr_pass.py work/cut30.mkv work/cut60_sr.mp4 [max_30fps_frames]
import sys, os, subprocess, time, torch
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import sr
inp,out=sys.argv[1],sys.argv[2]; nmax=int(sys.argv[3]) if len(sys.argv)>3 else 1800
W,H,w,h=1080,1920,478,850
torch.set_num_threads(os.cpu_count())
m=sr.load("models/realesr-general-x4v3.pth",32).to(memory_format=torch.channels_last)
rd=subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-frames:v",str(nmax),"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
# 30 -> 60fps motion interpolation on the sharp 1080 frames; scd stops blending across cuts
wr=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","30","-i","-",
    "-vf","minterpolate=fps=60:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=fdiff:scd_threshold=8",
    "-c:v","libx264","-preset","fast","-crf","10","-pix_fmt","yuv444p",out],stdin=subprocess.PIPE)
t0=time.time(); n=0
with torch.inference_mode(), torch.autocast("cpu",dtype=torch.bfloat16):
    while True:
        b=rd.stdout.read(w*h*3)
        if len(b)<w*h*3: break
        x=torch.frombuffer(bytearray(b),dtype=torch.uint8).view(h,w,3).permute(2,0,1).float().div(255)[None].contiguous(memory_format=torch.channels_last)
        y=m(x).float().clamp(0,1)
        y=torch.nn.functional.interpolate(y,size=(H,W),mode="area")   # 4x -> 1080x1920, stays crisp
        wr.stdin.write((y[0].permute(1,2,0)*255+0.5).byte().numpy().tobytes())
        n+=1
        if n%30==0: print("sr frame",n,round(time.time()-t0),"s",flush=True)
wr.stdin.close(); wr.wait(); print("sr done",n,round(time.time()-t0),"s")
