"""Shared helpers for the overlay renderers: fonts, emoji-aware text, easing, sprites."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(HERE, "fonts")
INTER = "/usr/share/fonts/opentype/inter"
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"

FPS = 60
W = 2160  # output width (4K portrait)
H = 3840

# Text taken from the listing post
REF = "REN51072"
GREETING = "Jemput Mai Tengok Dulu"
HEAD1 = "RUMAH | TANAH"
HEAD2 = "UNTUK DIJUAL"
OWNER = "Owner Nak Jual @ Pembeli Nak Beli"
KLIK = "Untuk mudahkan urusan boleh klik link bawah ini"
LINK = "nijam98.github.io/Video-Prop"


def font(name, size, variation=None):
    path = name if os.path.isabs(name) else (
        os.path.join(FONT_DIR, name) if os.path.exists(os.path.join(FONT_DIR, name))
        else os.path.join(INTER, name))
    f = ImageFont.truetype(path, size)
    if variation:
        f.set_variation_by_name(variation)
    return f


_emoji_cache = {}


def emoji(ch, size):
    """Colour emoji rendered at `size` px tall (Noto only ships 109 px bitmaps)."""
    key = (ch, size)
    if key not in _emoji_cache:
        f = ImageFont.truetype(EMOJI_FONT, 109)
        im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10, 10), ch, font=f, embedded_color=True)
        im = im.crop(im.getbbox())
        s = size / im.height
        _emoji_cache[key] = im.resize((max(1, round(im.width * s)), size), Image.LANCZOS)
    return _emoji_cache[key]


def text_mask(text, fnt, pad=0, tracking=0):
    """Grayscale mask of text, tightly cropped (plus padding)."""
    if tracking:
        widths = [fnt.getlength(c) + tracking for c in text]
        tw = int(sum(widths))
    else:
        tw = int(fnt.getlength(text))
    asc, desc = fnt.getmetrics()
    im = Image.new("L", (tw + 4 * pad + 40, asc + desc + 4 * pad + 40), 0)
    d = ImageDraw.Draw(im)
    if tracking:
        x = 2 * pad + 20
        for c, w_ in zip(text, widths):
            d.text((x, 2 * pad + 20), c, font=fnt, fill=255)
            x += w_
    else:
        d.text((2 * pad + 20, 2 * pad + 20), text, font=fnt, fill=255)
    bb = im.getbbox()
    return im.crop((bb[0] - pad, bb[1] - pad, bb[2] + pad, bb[3] + pad))


def solid(mask, color):
    im = Image.new("RGBA", mask.size, color)
    a = np.asarray(mask, np.float32) * (color[3] / 255.0 if len(color) > 3 else 1.0)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im


def hstack(items, gap=0, align="center"):
    h = max(i.height for i in items)
    w = sum(i.width for i in items) + gap * (len(items) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for i in items:
        y = (h - i.height) // 2 if align == "center" else h - i.height
        out.alpha_composite(i, (x, y))
        x += i.width + gap
    return out


def pad(im, p):
    out = Image.new("RGBA", (im.width + 2 * p, im.height + 2 * p), (0, 0, 0, 0))
    out.alpha_composite(im, (p, p))
    return out


def glow(im, radius, color, strength=1.0, grow=0):
    """Soft coloured glow from an RGBA sprite's alpha (same size as input)."""
    a = im.getchannel("A")
    if grow:
        a = a.filter(ImageFilter.MaxFilter(grow * 2 + 1))
    a = a.filter(ImageFilter.GaussianBlur(radius))
    if strength != 1.0:
        a = a.point(lambda v: min(255, int(v * strength)))
    g = Image.new("RGBA", im.size, color[:3] + (255,))
    g.putalpha(a)
    return g


def with_alpha(im, alpha):
    if alpha >= 0.999:
        return im
    if alpha <= 0.001:
        return None
    out = im.copy()
    out.putalpha(im.getchannel("A").point(lambda v: int(v * alpha)))
    return out


def place(canvas, im, cx, cy, scale=1.0, alpha=1.0, rot=0.0):
    """Composite sprite centred at (cx, cy) with scale / alpha / rotation."""
    if im is None or scale <= 0.01 or alpha <= 0.001:
        return
    if abs(scale - 1) > 1e-3:
        im = im.resize((max(1, round(im.width * scale)), max(1, round(im.height * scale))),
                       Image.BICUBIC)
    if abs(rot) > 0.05:
        im = im.rotate(rot, Image.BICUBIC, expand=True)
    im = with_alpha(im, alpha)
    if im is None:
        return
    x, y = round(cx - im.width / 2), round(cy - im.height / 2)
    # clip to canvas
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(im.width, canvas.width - x), min(im.height, canvas.height - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    if (sx0, sy0, sx1, sy1) != (0, 0, im.width, im.height):
        im = im.crop((sx0, sy0, sx1, sy1))
    canvas.alpha_composite(im, (x + sx0, y + sy0))


# ---- easing -------------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, t0, dur):
    return clamp((t - t0) / dur)


def ease_out_cubic(x):
    return 1 - (1 - x) ** 3


def ease_in_out(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def ease_out_back(x, s=1.70158):
    x -= 1
    return 1 + (s + 1) * x ** 3 + s * x ** 2


def ease_out_elastic(x):
    if x <= 0 or x >= 1:
        return clamp(x)
    return 2 ** (-10 * x) * math.sin((x * 10 - 0.75) * (2 * math.pi) / 3) + 1


def star4(size, color=(255, 255, 255), core=(255, 255, 255)):
    """Y2K four-point sparkle sprite."""
    s = size * 4
    yy, xx = np.mgrid[0:s, 0:s].astype(np.float32)
    c = (s - 1) / 2
    dx, dy = np.abs(xx - c) / c, np.abs(yy - c) / c
    # astroid-ish star: |x|^0.5 + |y|^0.5 <= 1
    v = np.sqrt(dx) + np.sqrt(dy)
    a = np.clip((1.0 - v) * 6, 0, 1)
    halo = np.clip(1 - np.sqrt(dx * dx + dy * dy) * 1.6, 0, 1) ** 2 * 0.55
    alpha = np.maximum(a, halo)
    rgb = np.zeros((s, s, 3), np.float32)
    rgb[:] = color
    rgb = rgb * (1 - a[..., None]) + np.array(core, np.float32) * a[..., None]
    im = Image.fromarray(np.dstack([rgb, alpha * 255]).astype(np.uint8), "RGBA")
    return im.resize((size, size), Image.LANCZOS)
