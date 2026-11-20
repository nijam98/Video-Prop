"""Real-ESRGAN (realesr-general-x4v3) upscale of work/cut_native.mp4 -> work/cut_sr.mp4 at 1080x1920.
usage: python3 tools/sr.py WEIGHTS.pth IN.mp4 OUT.mp4"""
import sys, subprocess, numpy as np, torch, torch.nn as nn, torch.nn.functional as F, cv2
torch.set_num_threads(4)
class SRVGG(nn.Module):
    def __init__(s, num_conv=32, num_feat=64, up=4):
        super().__init__(); s.up = up
        b = [nn.Conv2d(3, num_feat, 3, 1, 1), nn.PReLU(num_parameters=num_feat)]
        for _ in range(num_conv): b += [nn.Conv2d(num_feat, num_feat, 3, 1, 1), nn.PReLU(num_parameters=num_feat)]
        b += [nn.Conv2d(num_feat, 3 * up * up, 3, 1, 1)]
        s.body = nn.ModuleList(b); s.upsampler = nn.PixelShuffle(up)
    def forward(s, x):
        o = x
        for m in s.body: o = m(o)
        return s.upsampler(o) + F.interpolate(x, scale_factor=s.up, mode="nearest")
def main():
    w, inp, out = sys.argv[1:4]
    m = SRVGG(); sd = torch.load(w, map_location="cpu", weights_only=True); m.load_state_dict(sd.get("params", sd.get("params_ema", sd))); m.eval()
    W, H = 576, 1024
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", inp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "1080x1920", "-r", "30", "-i", "-",
        "-c:v", "libx264", "-crf", "14", "-preset", "medium", "-g", "30", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    n = 0
    with torch.inference_mode():
        while True:
            buf = dec.stdout.read(W * H * 3)
            if len(buf) < W * H * 3: break
            f = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
            x = torch.from_numpy(f.copy()).permute(2, 0, 1).float().div(255)[None]
            y = m(x).clamp(0, 1)[0].permute(1, 2, 0).numpy()
            y = cv2.resize((y * 255 + 0.5).astype(np.uint8), (1080, 1920), interpolation=cv2.INTER_AREA)
            l = cv2.resize(f, (1080, 1920), interpolation=cv2.INTER_LANCZOS4)
            y = cv2.addWeighted(y, 0.75, l, 0.25, 0)          # keep some natural texture
            enc.stdin.write(y.tobytes()); n += 1
            if n % 100 == 0: print(n, flush=True)
    enc.stdin.close(); enc.wait(); print("done", n)


if __name__ == "__main__":
    main()
