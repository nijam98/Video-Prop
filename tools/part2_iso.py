"""Part 2 overlay: isometric 3D CTA card + button with CTA zoom, top of the frame.

Usage: part2_iso.py NFRAMES            -> raw RGBA frames (W x BAND_H) on stdout
       part2_iso.py --preview T1 T2 .. -> PNGs of the full 4K frame layer
"""
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from common import (FPS, W, H, REF, GREETING, HEAD1, HEAD2, OWNER, KLIK, LINK, font, emoji,
                    text_mask, solid, hstack, pad, place, prog, clamp, ease_out_back,
                    ease_out_cubic, ease_in_out, ease_out_elastic, star4)

TH = math.atan(0.5)                       # 2:1 pixel-art isometric angle
A = np.array([math.cos(TH), -math.sin(TH)])   # along the wall (text direction, rising right)
B = np.array([0.0, 1.0])                      # down
C = np.array([-math.cos(TH), -math.sin(TH)]) * 0.75   # depth (away from viewer, up-left)
S = 0.95                                   # layout scale
BAND_H = 2240
TOP = 300                                  # top of the CTA group at rest (4K coords)

NAVY = (24, 36, 104)
ORANGE = (255, 104, 26)
CARD_W, CARD_H, CARD_D = 1300, 610, 70
LBL_V0, LBL_H = 650, 96
BTN_U0, BTN_W, BTN_V0, BTN_H, BTN_D = 90, 1120, 850, 196, 90
PAD = 6


def fit_font(name, text, size, max_w, variation=None):
    f = font(name, size, variation)
    while f.getlength(text) > max_w and size > 10:
        size -= 2
        f = font(name, size, variation)
    return f


def put_text(im, text, fnt, cx, cy, fill):
    m = text_mask(text, fnt, pad=2)
    im.alpha_composite(solid(m, fill), (round(cx - m.width / 2), round(cy - m.height / 2)))
    return m.width


def vgrad(w, h, c0, c1):
    t = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(c0, np.float32) * (1 - t) + np.array(c1, np.float32) * t
    arr = np.broadcast_to(arr, (h, w, len(c0)))
    return Image.fromarray(arr.astype(np.uint8), "RGBA" if len(c0) == 4 else "RGB")


def padded(im):
    return pad(im, PAD)


def card_texture():
    im = vgrad(CARD_W, CARD_H, (255, 255, 255, 255), (236, 241, 255, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, CARD_W, 148), fill=NAVY + (255,))
    d.rectangle((0, 148, CARD_W, 160), fill=ORANGE + (255,))
    f_ref = fit_font("RubikMono.ttf", REF, 70, 460)
    w = put_text(im, REF, f_ref, 60 + f_ref.getlength(REF) / 2, 76, (255, 255, 255))
    f_g = fit_font("InterDisplay-BlackItalic.otf", GREETING, 60, CARD_W - w - 230)
    gt = solid(text_mask(GREETING, f_g, pad=2), (255, 214, 64))
    row = hstack([gt, emoji("😍", 70)], gap=14)
    im.alpha_composite(row, (CARD_W - 50 - row.width, 76 - row.height // 2))
    f_h = fit_font("Bungee.ttf", HEAD1, 156, CARD_W - 110)
    put_text(im, HEAD1, f_h, CARD_W / 2, 268, NAVY)
    f_h2 = fit_font("Bungee.ttf", HEAD2, 156, CARD_W - 110)
    put_text(im, HEAD2, f_h2, CARD_W / 2, 422, ORANGE)
    f_o = fit_font("InterDisplay-Bold.otf", OWNER, 64, CARD_W - 140)
    put_text(im, OWNER, f_o, CARD_W / 2, 545, (70, 80, 120))
    return padded(im)


def label_texture():
    im = Image.new("RGBA", (CARD_W, LBL_H), (14, 18, 52, 190))
    f = fit_font("InterDisplay-Bold.otf", KLIK, 56, CARD_W - 160)
    m = text_mask(KLIK, f, pad=2)
    row = hstack([solid(m, (255, 255, 255)), emoji("👇", 64)], gap=14)
    im.alpha_composite(row, ((CARD_W - row.width) // 2, (LBL_H - row.height) // 2))
    return padded(im)


def button_texture():
    im = vgrad(BTN_W, BTN_H, (255, 222, 70, 255), (255, 170, 0, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, BTN_W, 10), fill=(255, 246, 190, 255))
    f = fit_font("InterDisplay-Black.otf", LINK, 82, BTN_W - 190)
    m = text_mask(LINK, f, pad=2)
    row = hstack([emoji("🔗", 74), solid(m, NAVY)], gap=22)
    im.alpha_composite(row, ((BTN_W - row.width) // 2, (BTN_H - row.height) // 2))
    return padded(im)


def flat(w, h, color):
    return padded(Image.new("RGBA", (max(1, int(w)), max(1, int(h))), color))


def warp(tex, origin, a, b, canvas_size):
    """Affine-map texture so texel (PAD, PAD) lands on `origin`, x-axis -> a, y-axis -> b.
    Returns (image, x0, y0) cropped to the projected bbox."""
    corners = []
    for x, y in ((0, 0), (tex.width, 0), (0, tex.height), (tex.width, tex.height)):
        p = origin + a * (x - PAD) + b * (y - PAD)
        corners.append(p)
    corners = np.array(corners)
    x0, y0 = np.floor(corners.min(0)).astype(int)
    x1, y1 = np.ceil(corners.max(0)).astype(int)
    x0, y0 = max(x0, 0), max(y0, 0)
    x1, y1 = min(x1, canvas_size[0]), min(y1, canvas_size[1])
    if x1 <= x0 or y1 <= y0:
        return None, 0, 0
    M = np.array([[a[0], b[0]], [a[1], b[1]]])
    inv = np.linalg.inv(M)
    # input = inv @ (out + (x0,y0) - origin) + PAD
    off = inv @ (np.array([x0, y0]) - origin) + PAD
    data = (inv[0, 0], inv[0, 1], off[0], inv[1, 0], inv[1, 1], off[1])
    im = tex.transform((x1 - x0, y1 - y0), Image.AFFINE, data, Image.BICUBIC)
    return im, x0, y0


def cube_sprite(size, top, left, right):
    s = size * 4
    im = Image.new("RGBA", (s, int(s * 1.15)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx, hw = s / 2, s / 2 * 0.98
    hh = hw * 0.5
    t0 = (cx, 2)
    tl, tr, tc = (cx - hw, 2 + hh), (cx + hw, 2 + hh), (cx, 2 + 2 * hh)
    hgt = hw * 1.05
    d.polygon([t0, tr, tc, tl], fill=top)
    d.polygon([tl, tc, (tc[0], tc[1] + hgt), (tl[0], tl[1] + hgt)], fill=left)
    d.polygon([tc, tr, (tr[0], tr[1] + hgt), (tc[0], tc[1] + hgt)], fill=right)
    im = im.crop(im.getbbox())
    return im.resize((im.width // 4, im.height // 4), Image.LANCZOS)


class Part2:
    def __init__(self):
        self.card = card_texture()
        self.card_top = flat(CARD_W, CARD_D, (214, 224, 250, 255))
        self.card_side = flat(CARD_D, CARD_H, (38, 62, 170, 255))
        self.label = label_texture()
        self.btn = button_texture()
        self.btn_arr = np.asarray(self.btn).astype(np.float32)
        self.btn_top = flat(BTN_W, BTN_D, (255, 236, 150, 255))
        self.btn_side = flat(BTN_D, BTN_H, (214, 110, 0, 255))
        self.socket = flat(BTN_W + 36, BTN_H + 36, (20, 22, 60, 235))
        sh = Image.new("RGBA", (CARD_W + 200, CARD_H + BTN_V0 + 200), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rectangle((100, 100, 100 + CARD_W, 100 + CARD_H),
                                     fill=(0, 0, 20, 105))  # card only
        self.shadow = pad(sh.filter(ImageFilter.GaussianBlur(45)), 0)
        self.cubes = [cube_sprite(150, (255, 150, 60), (230, 90, 20), (180, 60, 10)),
                      cube_sprite(110, (90, 230, 220), (20, 170, 170), (10, 120, 130)),
                      cube_sprite(90, (255, 130, 190), (220, 70, 140), (170, 40, 110)),
                      cube_sprite(120, (150, 170, 255), (80, 100, 230), (50, 60, 180))]
        self.hand = emoji("👆", 150)
        self.star = star4(140, (255, 240, 180))
        # layout: place group so it is horizontally centred with its top at TOP
        pts = [self.proj(u, v, w) for u in (0, CARD_W) for v in (0, BTN_V0 + BTN_H)
               for w in (0, CARD_D)]
        pts = np.array(pts)
        mn, mx = pts.min(0), pts.max(0)
        self.offset = np.array([W / 2 - (mn[0] + mx[0]) / 2, TOP - mn[1]])
        self.btn_center = self.proj(BTN_U0 + BTN_W / 2, BTN_V0 + BTN_H / 2, 0) + self.offset
        self.group_center = (mn + mx) / 2 + self.offset

    @staticmethod
    def proj(u, v, w):
        return S * (u * A + v * B + w * C)

    def button_face(self, shine_ph):
        if shine_ph is None:
            return self.btn
        h, w = self.btn_arr.shape[:2]
        pos = -300 + shine_ph * (w + 600)
        xx = np.arange(w, dtype=np.float32)[None, :]
        yy = np.arange(h, dtype=np.float32)[:, None]
        d = xx + (yy - h / 2) * 0.6 - pos
        band = np.exp(-(d / 55) ** 2) * 0.75
        out = self.btn_arr.copy()
        out[..., :3] += band[..., None] * 255 * (out[..., 3:] / 255)
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")

    def frame(self, t):
        c = Image.new("RGBA", (W, BAND_H), (0, 0, 0, 0))
        # ---- global zoom (intro zoom-in, then periodic CTA zoom toward the button) ----
        p_in = prog(t, 0, 0.95)
        z = ease_out_back(p_in, 1.5) if p_in < 1 else 1.0
        pivot = self.group_center
        press = 0.0           # 0 = button out, 1 = pushed in
        shine = None
        tap = None
        ripple = None
        if t >= 1.6:
            cyc = (t - 1.6) % 4.0
            if cyc < 0.6:
                zz = ease_in_out(cyc / 0.6)
            elif cyc < 1.5:
                zz = 1.0
            elif cyc < 2.1:
                zz = 1 - ease_in_out((cyc - 1.5) / 0.6)
            else:
                zz = 0.0
            # blend pivot to the button so the zoom pushes into the CTA
            z = 1 + 0.11 * zz
            pivot = self.btn_center
            if 0.55 <= cyc < 0.70:
                press = ease_in_out((cyc - 0.55) / 0.15)
            elif 0.70 <= cyc < 1.05:
                press = 1 - ease_out_elastic((cyc - 0.70) / 0.35)
            if 0.25 <= cyc < 1.25:
                tap = (cyc - 0.25) / 1.0
            if 0.68 <= cyc < 1.3:
                ripple = (cyc - 0.68) / 0.62
            if 1.05 <= cyc < 1.75:
                shine = (cyc - 1.05) / 0.7
        bob = math.sin(t * 2 * math.pi / 4.0) * 9 * clamp(t - 1)
        alpha = clamp(p_in * 3)

        def P(u, v, w):
            p = self.proj(u, v, w) + self.offset
            return pivot + z * (p - pivot) + np.array([0, bob])

        a_u, b_v, c_w = z * S * A, z * S * B, z * S * C
        layers = []
        # shadow (projected slightly below-right of the card)
        layers.append((self.shadow, P(-100, -100, 0) + np.array([40, 70]) * z, a_u, b_v))
        # card: top face, side face, then front
        layers.append((self.card_top, P(0, 0, CARD_D), a_u, -c_w))
        layers.append((self.card_side, P(0, 0, CARD_D), -c_w, b_v))
        layers.append((self.card, P(0, 0, 0), a_u, b_v))
        # label row (appears after card)
        lab_a = clamp((t - 0.6) / 0.35)
        # button: grows out of its socket during intro
        grow = ease_out_back(prog(t, 0.75, 0.55), 2.0)
        depth = BTN_D * grow * (1 - 0.75 * press)
        bw = BTN_D  # wall plane of the button
        sock = (self.socket, P(BTN_U0 - 18, BTN_V0 - 18, bw), a_u, b_v)
        front_w = bw - depth
        btn_layers = [sock]
        if depth > 1:
            btn_layers.append((self.btn_top, P(BTN_U0, BTN_V0, bw), a_u, -c_w * (depth / BTN_D)))
            btn_layers.append((self.btn_side, P(BTN_U0, BTN_V0, bw), -c_w * (depth / BTN_D), b_v))
        btn_layers.append((self.button_face(shine), P(BTN_U0, BTN_V0, front_w), a_u, b_v))

        for tex, org, a, b in layers:
            im, x, y = warp(tex, org, a, b, c.size)
            if im is not None:
                if alpha < 1:
                    im.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
                c.alpha_composite(im, (x, y))
        if lab_a > 0:
            im, x, y = warp(self.label, P(0, LBL_V0, 0), a_u, b_v, c.size)
            if im is not None:
                if lab_a < 1:
                    im.putalpha(im.getchannel("A").point(lambda v: int(v * lab_a)))
                c.alpha_composite(im, (x, y))
        if t > 0.75:
            for tex, org, a, b in btn_layers:
                im, x, y = warp(tex, org, a, b, c.size)
                if im is not None:
                    c.alpha_composite(im, (x, y))

        # ripple rings from the button on each tap
        bc = P(BTN_U0 + BTN_W / 2, BTN_V0 + BTN_H / 2, front_w)
        if ripple is not None:
            for k in range(2):
                r = clamp(ripple - k * 0.18)
                if r <= 0:
                    continue
                rad = 120 + ease_out_cubic(r) * 520
                ring = Image.new("RGBA", (int(rad * 2 + 40), int(rad * 2 + 40)), (0, 0, 0, 0))
                ImageDraw.Draw(ring).ellipse((20, 20, 20 + rad * 2, 20 + rad * 2),
                                             outline=(255, 230, 120, int(230 * (1 - r))),
                                             width=max(2, int(18 * (1 - r))))
                place(c, ring, bc[0], bc[1])
            for k in range(6):  # burst sparkles
                ang = k / 6 * 2 * math.pi + 0.3
                dist = 200 + ease_out_cubic(ripple) * 420
                place(c, self.star, bc[0] + math.cos(ang) * dist * 1.2, bc[1] + math.sin(ang) * dist * 0.6,
                      scale=(1 - ripple) * 0.9, rot=ripple * 90)
        # tapping hand
        if tap is not None:
            move = ease_out_cubic(clamp(tap / 0.3))
            back = ease_in_out(clamp((tap - 0.6) / 0.4))
            k = move * (1 - back)
            hx = bc[0] + 330 + (1 - k) * 260
            hy = bc[1] + 120 + (1 - k) * 220
            s = 1 - 0.12 * press
            place(c, self.hand, hx, hy, scale=s * z, alpha=clamp(k * 1.5))
        # floating iso cubes
        cube_pos = [(-120, 80, 0.0), (CARD_W + 70, 140, 0.4), (CARD_W + 120, CARD_H - 20, 0.7),
                    (-140, CARD_H + 200, 0.2)]
        for k, (u, v, ph) in enumerate(cube_pos):
            p = prog(t, 1.0 + k * 0.12, 0.5)
            if p <= 0:
                continue
            q = P(u, v, -40)
            fy = math.sin(2 * math.pi * (t / 2.0 + ph)) * 22
            place(c, self.cubes[k], q[0], q[1] + fy, scale=ease_out_back(p, 2.2) * z)
        return c


def main():
    r = Part2()
    if sys.argv[1] == "--preview":
        for ts in sys.argv[2:]:
            full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            full.alpha_composite(r.frame(float(ts)), (0, 0))
            full.save(f"p2_{ts}.png")
        return
    if sys.argv[1] == "--band":
        print(0, BAND_H)
        return
    n = int(sys.argv[1])
    out = sys.stdout.buffer
    for i in range(n):
        out.write(r.frame(i / FPS).tobytes())


if __name__ == "__main__":
    main()
