"""Upscale chosen frames (Real-ESRGAN x4) into 4:5 framed prints for the photo overlays.
usage: python3 tools/stills.py WEIGHTS.pth SRC.mp4"""
import sys, subprocess, numpy as np, torch, cv2
sys.path.insert(0, __import__('os').path.dirname(__file__))
from sr import SRVGG  # noqa (sr.py guards its main below)
W = {"living": 12.6, "kitchen": 30.4, "family": 46.6, "master": 53.6, "bilik2": 73.4, "bilik3": 80.6, "foyer": 1.0}
torch.set_num_threads(2)
m = SRVGG(); sd = torch.load(sys.argv[1], map_location="cpu", weights_only=True); m.load_state_dict(sd.get("params", sd)); m.eval()
for name, t in W.items():
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", sys.argv[2], "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
    f = np.frombuffer(raw, np.uint8).reshape(1024, 576, 3)[152:872]            # 4:5 centre crop
    with torch.inference_mode():
        y = m(torch.from_numpy(f.copy()).permute(2, 0, 1).float().div(255)[None]).clamp(0, 1)[0].permute(1, 2, 0).numpy()
    y = cv2.resize((y * 255 + .5).astype(np.uint8), (864, 1080), interpolation=cv2.INTER_AREA).astype(np.float32) / 255
    y = np.clip((y - .5) * 1.05 + .5, 0, 1)                                    # gentle contrast
    y[..., 0] *= 1.015; y[..., 2] *= 0.985                                     # a touch warmer
    cv2.imwrite(f"assets/photos/{name}.jpg", cv2.cvtColor((np.clip(y, 0, 1) * 255).astype(np.uint8), cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print(name)
