import torch, torch.nn as nn, torch.nn.functional as F, numpy as np, cv2
class SRVGG(nn.Module):
    def __init__(s,num_conv=32,num_feat=64,up=4):
        super().__init__(); s.up=up
        b=[nn.Conv2d(3,num_feat,3,1,1),nn.PReLU(num_parameters=num_feat)]
        for _ in range(num_conv): b+=[nn.Conv2d(num_feat,num_feat,3,1,1),nn.PReLU(num_parameters=num_feat)]
        b+=[nn.Conv2d(num_feat,3*up*up,3,1,1)]
        s.body=nn.ModuleList(b); s.upsampler=nn.PixelShuffle(up)
    def forward(s,x):
        o=x
        for m in s.body: o=m(o)
        return s.upsampler(o)+F.interpolate(x,scale_factor=s.up,mode="nearest")
def load(path,num_conv):
    m=SRVGG(num_conv); sd=torch.load(path,map_location="cpu",weights_only=True)
    sd=sd.get("params",sd.get("params_ema",sd)); m.load_state_dict(sd); return m.eval()
@torch.inference_mode()
def upscale(m,bgr):
    x=torch.from_numpy(bgr[...,::-1].copy()).permute(2,0,1).float().div(255)[None]
    y=m(x).clamp(0,1)[0].permute(1,2,0).numpy()[...,::-1]
    return (y*255+0.5).astype(np.uint8)
