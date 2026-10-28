"""Part 1 overlay: Y2K chrome CTA in the bottom of the frame.

Writes raw RGBA frames (W x BAND_H) to stdout, or PNG previews with --preview.
Usage: part1_y2k.py NFRAMES            -> raw frames on stdout
       part1_y2k.py --preview T1 T2 .. -> PNGs of the full 4K frame layer
"""
import math
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from common import (FPS, W, H, REF, OWNER, KLIK, LINK, font, emoji,
                    text_mask, solid, hstack, pad, glow, place, prog, clamp, ease_out_back,
                    ease_out_cubic, ease_out_elastic, star4)

BOTTOM = 3470          # content ends here (keeps clear of app UI at the very bottom)
NAVY = (14, 12, 44)

CHROME_STOPS = [(0.00, (255, 255, 255)), (0.28, (206, 222, 246)), (0.47, (126, 142, 186)),
                (0.50, (36, 40, 84)), (0.55, (150, 110, 190)), (0.74, (250, 232, 255)),
                (1.00, (168, 182, 226))]


def gradient(n, stops):
    t = np.linspace(0, 1, n)
    out = np.zeros((n, 3), np.float32)
    for c in range(3):
        out[:, c] = np.interp(t, [s[0] for s in stops], [s[1][c] for s in stops])
    return out


def chrome_fill(mask_arr, stops=CHROME_STOPS, bevel=True):
    """RGB chrome shading for a float mask (h, w) in 0..1."""
    h, w = mask_arr.shape
    rows = np.where(mask_arr.max(1) > 0.5)[0]
    top, bot = (rows[0], rows[-1]) if len(rows) else (0, h - 1)
    grad = gradient(max(2, bot - top + 1), stops)
    rgb = np.zeros((h, w, 3), np.float32)
    rgb[:top] = grad[0]
    rgb[top:bot + 1] = grad[:, None, :]
    rgb[bot + 1:] = grad[-1]
    if bevel:
        m = Image.fromarray((mask_arr * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))
        m = np.asarray(m, np.float32) / 255
        gy = np.zeros_like(m)
        gy[1:-1] = (m[2:] - m[:-2]) * 0.5
        gx = np.zeros_like(m)
        gx[:, 1:-1] = (m[:, 2:] - m[:, :-2]) * 0.5
        light = gy * 0.8 + gx * 0.45          # light from top-left
        rgb += np.clip(light, 0, None)[..., None] * 900
        rgb -= np.clip(-light, 0, None)[..., None] * 500
    return np.clip(rgb, 0, 255)


def chrome_text(text, fnt, outline=12, depth=14, tracking=0):
    m = text_mask(text, fnt, pad=outline + depth + 40, tracking=tracking)
    fill_a = np.asarray(m, np.float32) / 255
    rgb = chrome_fill(fill_a)
    ol = m.filter(ImageFilter.MaxFilter(outline * 2 + 1))
    ext = Image.new("L", m.size, 0)
    for d in range(0, depth + 1, 2):
        ext = Image.fromarray(np.maximum(np.asarray(ext), np.asarray(ol.transform(
            m.size, Image.AFFINE, (1, 0, 0, 0, 1, -d)))))
    base = Image.new("RGBA", m.size, (0, 0, 0, 0))
    g = glow(solid(ext, (255, 255, 255)), 26, (255, 90, 220), 1.1, grow=4)
    base.alpha_composite(g)
    base.alpha_composite(solid(ext, (60, 30, 110)))         # extrusion (violet)
    base.alpha_composite(solid(ol, NAVY))                    # outline
    face = Image.fromarray(np.dstack([rgb, fill_a * 255]).astype(np.uint8), "RGBA")
    base.alpha_composite(face)
    return base, fill_a


def rounded(size, r, fill=255):
    im = Image.new("L", (size[0] * 2, size[1] * 2), 0)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), r * 2, fill=fill)
    return im.resize(size, Image.LANCZOS)


def chrome_pill(content, padx, pady, ring=10, glass=(14, 10, 46, 215)):
    w, h = content.width + 2 * padx, content.height + 2 * pady
    outer = rounded((w, h), h // 2)
    inner = rounded((w - 2 * ring, h - 2 * ring), (h - 2 * ring) // 2)
    oa = np.asarray(outer, np.float32) / 255
    ring_rgb = chrome_fill(oa, bevel=False)
    pill = Image.fromarray(np.dstack([ring_rgb, oa * 255]).astype(np.uint8), "RGBA")
    # glass centre with violet->navy gradient
    gl = np.zeros((h - 2 * ring, w - 2 * ring, 4), np.float32)
    gx = np.linspace(0, 1, w - 2 * ring)[None, :, None]
    c0, c1 = np.array(glass[:3], np.float32), np.array((70, 20, 110), np.float32)
    gl[..., :3] = c0 * (1 - gx) + c1 * gx
    gl[..., 3] = np.asarray(inner, np.float32) / 255 * glass[3]
    # top gloss
    yy = np.linspace(0, 1, h - 2 * ring)[:, None]
    gl[..., :3] += (np.clip(0.45 - yy, 0, 1) * 160)[..., None]
    glass_im = Image.fromarray(np.clip(gl, 0, 255).astype(np.uint8), "RGBA")
    # replace ring centre with glass (glass is opaque-ish, so composite over)
    hole = Image.new("RGBA", pill.size, (0, 0, 0, 0))
    hole.paste(Image.new("RGBA", glass_im.size, (0, 0, 0, 0)), (ring, ring),
               inner)  # punch
    pa = np.asarray(pill).copy()
    ia = np.zeros((h, w), np.float32)
    ia[ring:h - ring, ring:w - ring] = np.asarray(inner, np.float32) / 255
    pa[..., 3] = (pa[..., 3] * (1 - ia)).astype(np.uint8)
    pill = Image.fromarray(pa, "RGBA")
    pill.alpha_composite(glass_im, (ring, ring))
    pill.alpha_composite(content, ((w - content.width) // 2, (h - content.height) // 2))
    return pad(pill, 40)


def white_text(text, fnt, shadow=True, tracking=0):
    m = text_mask(text, fnt, pad=30, tracking=tracking)
    im = Image.new("RGBA", m.size, (0, 0, 0, 0))
    if shadow:
        sh = solid(m.filter(ImageFilter.MaxFilter(5)), (8, 4, 30, 200)).filter(
            ImageFilter.GaussianBlur(6))
        im.alpha_composite(sh, (0, 0))
        im.alpha_composite(sh, (0, 0))
    im.alpha_composite(solid(m, (255, 255, 255)))
    return im


def rgb_split(text, fnt, off=6):
    """White text with cyan / magenta offset copies (Y2K chromatic look)."""
    m = text_mask(text, fnt, pad=40)
    base = Image.new("RGBA", m.size, (0, 0, 0, 0))
    sh = solid(m.filter(ImageFilter.MaxFilter(7)), (8, 4, 30, 230)).filter(
        ImageFilter.GaussianBlur(8))
    base.alpha_composite(sh)
    cyan, mag, white = solid(m, (0, 240, 255, 230)), solid(m, (255, 40, 200, 230)), solid(m, (255, 255, 255))
    return base, cyan, mag, white


class Part1:
    def __init__(self):
        f_head = font("RubikMono.ttf", 196)
        f_pill = font("Orbitron.ttf", 74, "Black")
        f_owner = font("InterDisplay-ExtraBoldItalic.otf", 86)
        f_klik = font("InterDisplay-SemiBold.otf", 64)
        f_link = font("InterDisplay-Bold.otf", 82)

        # "Rumah | Tanah Untuk Dijual" lives only in Part 2's CTA; Part 1 headlines the greeting
        self.head1, self.head1_mask = chrome_text("JEMPUT MAI", f_head)
        self.head2, self.head2_mask = chrome_text("TENGOK DULU", f_head)
        self.head_arr = [np.asarray(self.head1).astype(np.float32),
                         np.asarray(self.head2).astype(np.float32)]

        star_small = star4(60, (180, 230, 255))
        ref_txt = solid(text_mask(REF, f_pill, pad=4, tracking=10), (255, 255, 255))
        pill = chrome_pill(hstack([star_small, ref_txt, star_small], gap=26), 54, 22)
        self.pill = hstack([pill, emoji("😍", 120)], gap=-14)

        self.owner = rgb_split(OWNER, f_owner)
        self.klik = white_text(KLIK, f_klik)
        self.finger = emoji("👇", 92)

        link_txt = solid(text_mask(LINK, f_link, pad=4), (255, 255, 255))
        self.link = chrome_pill(hstack([emoji("🔗", 78), link_txt], gap=26), 70, 36, ring=12)
        self.link_glow = glow(self.link, 30, (0, 220, 255), 1.0, grow=6)

        # ---- layout (absolute 4K coordinates of each row's centre) ----
        rows = [("pill", self.pill.height - 80 + 10),
                ("head1", self.head1.height - 112), ("head2", self.head2.height - 112),
                ("owner", self.owner[0].height - 60), ("klik", self.klik.height - 40),
                ("link", self.link.height - 80)]
        gaps = {"head1": 24, "head2": 0, "owner": 26, "klik": 20, "link": 26}
        total = sum(h for _, h in rows) + sum(gaps.values())
        y = BOTTOM - total
        self.top = y
        self.cy = {}
        for name, h in rows:
            y += gaps.get(name, 0)
            self.cy[name] = y + h / 2
            y += h
        # band covered by this overlay
        self.band_y = int(self.top - 360)
        self.band_h = H - self.band_y
        self.band_h -= self.band_h % 2
        # scrim
        yy = np.arange(self.band_h, dtype=np.float32)[:, None]
        a = np.clip((yy - 0) / 520, 0, 1) ** 1.4 * 0.70
        scr = np.zeros((self.band_h, W, 4), np.float32)
        scr[..., 0], scr[..., 1], scr[..., 2] = 10, 6, 32
        scr[..., 3] = np.broadcast_to(a * 255, (self.band_h, W))
        self.scrim = Image.fromarray(scr.astype(np.uint8), "RGBA")
        hy = self.cy["head1"] - self.band_y
        self.sparkles = [  # (x, y, size, period, phase)
            (230, hy - 120, 130, 2.0, 0.0), (1960, hy - 90, 100, 4 / 3, 0.35),
            (1890, self.cy["head2"] - self.band_y + 120, 150, 4.0, 0.6),
            (300, self.cy["head2"] - self.band_y + 110, 90, 2.0, 0.8),
            (1080, hy - 190, 70, 1.0, 0.5), (1760, self.cy["pill"] - self.band_y, 80, 4.0, 0.15),
            (380, self.cy["pill"] - self.band_y - 10, 70, 2.0, 0.7),
        ]
        self.star = star4(200, (200, 225, 255))
        self.star_pink = star4(200, (255, 170, 240))

    def shine(self, idx, t):
        """Chrome headline with a moving specular sweep."""
        arr = self.head_arr[idx]
        mask = self.head1_mask if idx == 0 else self.head2_mask
        h, w = mask.shape
        period, dur = 2.0, 0.75
        ph = ((t - 1.4 - idx * 0.18) % period) / dur
        if t < 1.4 or ph > 1:
            return self.head1 if idx == 0 else self.head2
        pos = -400 + ph * (w + 800)
        xx = np.arange(w, dtype=np.float32)[None, :]
        yy = np.arange(h, dtype=np.float32)[:, None]
        d = xx + (yy - h / 2) * 0.55 - pos
        band = np.exp(-(d / 70) ** 2) * 0.85 + np.exp(-((d - 150) / 22) ** 2) * 0.6
        out = arr.copy()
        out[..., :3] += (band * mask)[..., None] * 255
        return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")

    def frame(self, t):
        c = Image.new("RGBA", (W, self.band_h), (0, 0, 0, 0))
        by = self.band_y
        sa = ease_out_cubic(prog(t, 0, 0.6))
        if sa > 0.999:
            c.alpha_composite(self.scrim)
        else:
            place(c, self.scrim, W / 2, self.band_h / 2, alpha=sa)
        bob = math.sin(t * 2 * math.pi / 4.0) * 6
        cx = W / 2

        # REF pill: slide up
        p = prog(t, 0.10, 0.55)
        place(c, self.pill, cx, self.cy["pill"] - by + (1 - ease_out_back(p)) * 120 + bob,
              alpha=clamp(p * 3))
        # chrome headlines: slam in from big
        for i, key in enumerate(("head1", "head2")):
            p = prog(t, 0.40 + i * 0.2, 0.7)
            s = 1 + (1 - ease_out_elastic(p)) * 0.9 if p < 1 else 1.0
            pulse = 1 + 0.012 * math.sin((t - i * 0.4) * 2 * math.pi / 2.0) if t > 1.6 else 1
            place(c, self.shine(i, t), cx, self.cy[key] - by + bob, scale=s * pulse,
                  alpha=clamp(p * 4))
        # owner line with RGB split jitter
        p = prog(t, 0.85, 0.5)
        if p > 0:
            base, cyan, mag, white = self.owner
            y = self.cy["owner"] - by + (1 - ease_out_cubic(p)) * 80 + bob
            glitch = (round(t * FPS) % 120) < 7 and t >= 1.99
            off = 6 + (14 if glitch else 0) + (1 - p) * 40
            a = clamp(p * 2)
            place(c, base, cx, y, alpha=a)
            place(c, cyan, cx - off, y, alpha=a)
            place(c, mag, cx + off, y + (3 if glitch else 0), alpha=a)
            place(c, white, cx, y, alpha=a)
        # klik line + bouncing finger
        p = prog(t, 1.0, 0.5)
        if p > 0:
            y = self.cy["klik"] - by + (1 - ease_out_cubic(p)) * 60 + bob
            place(c, self.klik, cx - 40, y, alpha=clamp(p * 2))
            fb = abs(math.sin(t * math.pi * 2.0)) * 22
            place(c, self.finger, cx - 40 + self.klik.width / 2 + 30, y - 6 + fb,
                  alpha=clamp(p * 2))
        # link pill: pop + glow pulse
        p = prog(t, 1.15, 0.6)
        if p > 0:
            y = self.cy["link"] - by + bob
            s = ease_out_back(p, 2.4)
            pulse = 0.5 + 0.5 * math.sin(t * 2 * math.pi / 1.0)
            if t > 1.6:
                place(c, self.link_glow, cx, y, scale=1.0 + 0.02 * pulse, alpha=0.35 + 0.5 * pulse)
            place(c, self.link, cx, y, scale=s * (1 + 0.015 * pulse), alpha=clamp(p * 3))
        # sparkles twinkle
        if t > 0.9:
            for k, (x, y, size, period, phase) in enumerate(self.sparkles):
                v = math.sin(2 * math.pi * ((t - 0.9) / period + phase))
                if v <= 0:
                    continue
                s = size / 200 * (v ** 1.5)
                st = self.star_pink if k % 2 else self.star
                place(c, st, x, y + bob, scale=s, rot=(t * 45 + k * 30) % 90)
        return c


def main():
    r = Part1()
    if sys.argv[1] == "--preview":
        for ts in sys.argv[2:]:
            t = float(ts)
            full = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            full.alpha_composite(r.frame(t), (0, r.band_y))
            full.save(f"p1_{ts}.png")
        print("band_y", r.band_y, "band_h", r.band_h, file=sys.stderr)
        return
    if sys.argv[1] == "--band":
        print(r.band_y, r.band_h)
        return
    n = int(sys.argv[1])
    out = sys.stdout.buffer
    for i in range(n):
        out.write(r.frame(i / FPS).tobytes())


if __name__ == "__main__":
    main()
