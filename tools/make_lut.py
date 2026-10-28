"""Bake iPhone HLG (BT.2020, limited YUV) -> SDR BT.709 (limited YUV) into a 3D LUT.

The LUT works on YUV planes relabelled as RGB (R=V, G=Y, B=U) so ffmpeg can skip
slow YUV<->RGB conversions. Values come from ffmpeg's own zscale+hable chain."""
import numpy as np, subprocess, sys
N = 65
out = sys.argv[1]
gain = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
g = np.linspace(0, 1, N)
B, G, R = np.meshgrid(g, g, g, indexing="ij")            # .cube order: R fastest
V, Y, U = R.reshape(N * N, N), G.reshape(N * N, N), B.reshape(N * N, N)
raw = b"".join(np.round(p * 65535).astype("<u2").tobytes() for p in (Y, U, V))
vf = ("setparams=color_primaries=bt2020:color_trc=arib-std-b67:colorspace=bt2020nc:range=tv,"
      "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,"
      "zscale=t=bt709:m=bt709:r=full,format=gbrpf32le")
res = subprocess.run(["ffmpeg", "-v", "error", "-f", "rawvideo", "-pix_fmt", "yuv444p16le",
                      "-s", f"{N}x{N*N}", "-i", "-", "-vf", vf, "-f", "rawvideo", "-"],
                     input=raw, capture_output=True, check=True).stdout
gp, bp, rp = np.frombuffer(res, "<f4").reshape(3, -1)       # gbr plane order
rgb = np.clip(np.stack([rp, gp, bp], -1), 0, 1)
lin = np.power(rgb, 2.4) * gain                             # optional lift
rgb = np.power(np.clip(lin, 0, 1), 1 / 2.4)
Kr, Kb = 0.2126, 0.0722
yy = rgb @ np.array([Kr, 1 - Kr - Kb, Kb])
cb = (rgb[:, 2] - yy) / (2 * (1 - Kb))
cr = (rgb[:, 0] - yy) / (2 * (1 - Kr))
# limited range, normalised to the 16-bit code space used by lut3d
Yo = (16 + 219 * yy) / 255 * 65280 / 65535
Uo = (128 + 224 * cb) / 255 * 65280 / 65535
Vo = (128 + 224 * cr) / 255 * 65280 / 65535
with open(out, "w") as f:
    f.write(f"LUT_3D_SIZE {N}\n")
    np.savetxt(f, np.stack([Vo, Yo, Uo], -1), fmt="%.6f")
