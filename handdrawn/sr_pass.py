# AI-upscale the 60fps cut (478x850) to 1080x1920 with Real-ESRGAN animevideov3 (bf16 on CPU)
import sys, subprocess, numpy as np, cv2, torch, time
sys.path.insert(0,".")
import sr
inp, out, nmax = sys.argv[1], sys.argv[2], int(sys.argv[3])
W,H,w,h=1080,1920,478,850
m=sr.load("models/realesr-animevideov3.pth",16).to(memory_format=torch.channels_last)
rd=subprocess.Popen(["ffmpeg","-v","error","-i",inp,"-frames:v",str(nmax),"-f","rawvideo","-pix_fmt","rgb24","-"],stdout=subprocess.PIPE)
wr=subprocess.Popen(["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r","60","-i","-",
    "-c:v","libx264","-preset","fast","-crf","8","-pix_fmt","yuv444p",out],stdin=subprocess.PIPE)
t0=time.time(); n=0
with torch.inference_mode(), torch.autocast("cpu",dtype=torch.bfloat16):
    while True:
        b=rd.stdout.read(w*h*3)
        if len(b)<w*h*3: break
        x=torch.frombuffer(bytearray(b),dtype=torch.uint8).view(h,w,3).permute(2,0,1).float().div(255)[None].contiguous(memory_format=torch.channels_last)
        y=m(x).float().clamp(0,1)
        y=torch.nn.functional.interpolate(y,size=(H,W),mode="area")   # 4x -> 1080x1920, keeps it crisp
        wr.stdin.write((y[0].permute(1,2,0)*255+0.5).byte().numpy().tobytes())
        n+=1
        if n%300==0: print("sr frame",n,round(time.time()-t0),"s",flush=True)
wr.stdin.close(); wr.wait(); print("sr done",n,round(time.time()-t0),"s")
