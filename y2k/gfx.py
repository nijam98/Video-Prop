# Y2K graphics: chrome text, holo text, gel pills, retro windows, sparkles, pixel cursor.
# Every builder returns an RGBA uint8 numpy array (premultiplied=False).
import os, math, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

FD = os.environ.get("FONTS", "fonts")
F_CHROME = f"{FD}/RubikMonoOne-Regular.ttf"
F_WIDE = f"{FD}/Audiowide-Regular.ttf"
F_PIX = f"{FD}/PressStart2P-Regular.ttf"



def _mask(text, font, size, pad):
    f = ImageFont.truetype(font, size)
    bb = f.getbbox(text)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    im = Image.new("L", (w + 2 * pad, h + 2 * pad), 0)
    ImageDraw.Draw(im).text((pad - bb[0], pad - bb[1]), text, font=f, fill=255)
    return np.array(im).astype(np.float32) / 255, (pad, pad, w, h)


def _grad(h, stops):
    """vertical gradient h x 3 (RGB) from [(pos, (r,g,b)), ...]"""
    y = np.linspace(0, 1, h)
    out = np.zeros((h, 3), np.float32)
    ps = [p for p, _ in stops]
    for c in range(3):
        out[:, c] = np.interp(y, ps, [col[c] for _, col in stops])
    return out / 255


CHROME = [(0, (255, 255, 255)), (0.38, (205, 218, 240)), (0.49, (90, 105, 150)), (0.52, (25, 30, 70)),
          (0.6, (110, 160, 225)), (0.82, (225, 238, 255)), (1, (150, 175, 220))]
GOLD = [(0, (255, 252, 225)), (0.4, (255, 220, 120)), (0.5, (150, 85, 20)), (0.53, (90, 45, 10)),
        (0.62, (230, 160, 60)), (0.85, (255, 240, 180)), (1, (210, 150, 60))]


def chrome_text(text, size=150, stops=CHROME, outline=(18, 16, 60), glow=(255, 80, 220), ow=10):
    pad = 70
    m, (x, y, w, h) = _mask(text, F_CHROME, size, pad)
    H, W = m.shape
    g = np.zeros((H, W, 3), np.float32)
    g[:] = _grad(h, stops)[np.clip(np.arange(H) - y, 0, h - 1)][:, None, :]
    # bevel: light from top-left on a blurred height map
    hm = cv2.GaussianBlur(m, (0, 0), size / 40)
    gx = cv2.Sobel(hm, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(hm, cv2.CV_32F, 0, 1, ksize=3)
    shade = np.clip(-(gx + gy) * 2.2, -1, 1)
    g = np.clip(g + 0.35 * np.maximum(shade, 0)[..., None] - 0.25 * np.maximum(-shade, 0)[..., None], 0, 1)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ow + 1, 2 * ow + 1))
    dil = cv2.dilate(m, k)
    k2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ow + 9, 2 * ow + 9))
    dil2 = cv2.dilate(m, k2)
    glo = cv2.GaussianBlur(dil2, (0, 0), 16)
    rgb = np.zeros((H, W, 3), np.float32); a = np.zeros((H, W), np.float32)
    # outer glow
    rgb[:] = np.array(glow, np.float32) / 255; a = np.clip(glo * 1.3, 0, 1) * 0.85
    # white thin rim then dark outline
    rim = np.clip(dil2 - dil, 0, 1)
    rgb = rgb * (1 - dil2[..., None]) + np.ones(3) * dil2[..., None]; a = np.maximum(a, dil2)
    ol = np.array(outline, np.float32) / 255
    rgb = rgb * (1 - dil[..., None]) + ol * dil[..., None]
    rgb = rgb * (1 - m[..., None]) + g * m[..., None]
    out = np.dstack([rgb * 255, a[..., None] * 255]).astype(np.uint8)
    return out, m  # m used for shine sweeps


def shine(rgba, m, p, width=0.12):
    """diagonal white sweep across the letters; p in [0,1]"""
    H, W = m.shape
    if p <= 0 or p >= 1:
        return rgba
    xx = np.arange(W)[None, :] / W + np.arange(H)[:, None] / H * 0.35
    c = -0.2 + 1.55 * p
    band = np.clip(1 - np.abs(xx - c) / width, 0, 1) ** 2 * m
    o = rgba.astype(np.float32)
    o[..., :3] = o[..., :3] + (255 - o[..., :3]) * band[..., None] * 0.9
    return o.astype(np.uint8)


def holo_text(text, size=90, font=None, ow=6):
    """pastel iridescent gradient text with dark outline (Y2K holographic foil)"""
    pad = 40
    m, (x, y, w, h) = _mask(text, font or F_WIDE, size, pad)
    H, W = m.shape
    xx = np.linspace(0, 1, W)[None, :] + np.linspace(0, 0.4, H)[:, None]
    hue = (xx * 1.4) % 1.0
    cols = np.array([(255, 150, 230), (200, 160, 255), (130, 230, 255), (160, 255, 210), (255, 245, 170), (255, 150, 230)], np.float32) / 255
    idx = hue * 5; i0 = np.floor(idx).astype(int); fr = (idx - i0)[..., None]
    g = cols[i0] * (1 - fr) + cols[np.minimum(i0 + 1, 5)] * fr
    g = np.clip(g + 0.25 * _grad(H, [(0, (255, 255, 255)), (0.5, (0, 0, 0)), (1, (60, 60, 60))])[:, None, :] - 0.1, 0, 1)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * ow + 1, 2 * ow + 1))
    dil = cv2.dilate(m, k)
    glo = cv2.GaussianBlur(dil, (0, 0), 10)
    rgb = np.ones((H, W, 3), np.float32) * np.array([0.55, 0.85, 1.0])
    a = glo * 0.7
    rgb = rgb * (1 - dil[..., None]) + np.array([0.08, 0.06, 0.22]) * dil[..., None]; a = np.maximum(a, dil)
    rgb = rgb * (1 - m[..., None]) + g * m[..., None]
    return np.dstack([rgb * 255, a[..., None] * 255]).astype(np.uint8)


PILL = {  # top colour, bottom colour (RGB)
    "pink": ((255, 150, 220), (225, 20, 150)),
    "aqua": ((150, 240, 255), (0, 140, 230)),
    "lime": ((220, 255, 140), (60, 190, 40)),
    "purple": ((215, 170, 255), (120, 40, 220)),
    "silver": ((250, 252, 255), (150, 165, 195)),
}


def _star(d, cx, cy, r, fill, thin=0.22):
    pts = []
    for i in range(8):
        ang = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * thin
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)


def pill(text, color="pink", size=46, star=True, dark_text=False):
    f = ImageFont.truetype(F_WIDE, size)
    bb = f.getbbox(text); tw, th = bb[2] - bb[0], bb[3] - bb[1]
    ph = int(size * 1.75); px = int(size * 0.75); icon = int(ph * 0.75) if star else 0
    pw = tw + 2 * px + icon
    S = 3  # supersample for smooth edges
    pad = 30
    W, H = pw + 2 * pad, ph + 2 * pad
    base = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(base)
    r = ph * S // 2
    box = (pad * S, pad * S, (pad + pw) * S, (pad + ph) * S)
    # gradient fill via mask
    top, bot = PILL[color]
    grad = np.zeros((H * S, W * S, 4), np.uint8)
    gy = _grad(H * S, [(0, top), (pad / H, top), ((pad + ph) / H, bot), (1, bot)])
    grad[..., :3] = (gy[:, None, :] * 255).astype(np.uint8); grad[..., 3] = 255
    mk = Image.new("L", (W * S, H * S), 0); ImageDraw.Draw(mk).rounded_rectangle(box, r, fill=255)
    body = Image.fromarray(grad); body.putalpha(mk)
    # soft shadow
    sh = Image.new("L", (W * S, H * S), 0); ImageDraw.Draw(sh).rounded_rectangle((box[0] + 6 * S, box[1] + 10 * S, box[2] + 6 * S, box[3] + 10 * S), r, fill=150)
    sh = np.array(sh).astype(np.float32); sh = cv2.GaussianBlur(sh, (0, 0), 8 * S)
    shadow = np.zeros((H * S, W * S, 4), np.uint8); shadow[..., :3] = (20, 10, 50); shadow[..., 3] = sh.astype(np.uint8)
    out = Image.alpha_composite(Image.fromarray(shadow), body)
    d = ImageDraw.Draw(out)
    # glossy highlight on the upper half
    gl = Image.new("L", (W * S, H * S), 0)
    ImageDraw.Draw(gl).rounded_rectangle((box[0] + r // 3, box[1] + 5 * S, box[2] - r // 3, box[1] + int(ph * S * 0.48)), r // 2, fill=255)
    gla = np.array(gl).astype(np.float32) / 255
    fade = np.clip(1 - (np.arange(H * S)[:, None] - box[1]) / (ph * S * 0.5), 0, 1)
    gla = gla * (0.25 + 0.5 * fade)
    o = np.array(out).astype(np.float32)
    o[..., :3] = o[..., :3] * (1 - gla[..., None]) + 255 * gla[..., None]
    out = Image.fromarray(o.astype(np.uint8)); d = ImageDraw.Draw(out)
    d.rounded_rectangle(box, r, outline=(255, 255, 255, 235), width=4 * S)
    if star:
        cx = box[0] + px * S * 0.7 + icon * S / 2; cy = (box[1] + box[3]) / 2
        _star(d, cx + 3 * S, cy + 3 * S, icon * S * 0.42, (40, 10, 70, 120))
        _star(d, cx, cy, icon * S * 0.42, (255, 255, 255, 255))
    fS = ImageFont.truetype(F_WIDE, size * S)
    tx = box[0] + (px + icon) * S - bb[0] * S; ty = (box[1] + box[3]) / 2 - (bb[1] + th / 2) * S
    tc = (30, 20, 60, 255) if dark_text else (255, 255, 255, 255)
    sc = (255, 255, 255, 160) if dark_text else (40, 10, 70, 200)
    d.text((tx + 3 * S, ty + 4 * S), text, font=fS, fill=sc)
    d.text((tx, ty), text, font=fS, fill=tc, stroke_width=S if not dark_text else 0, stroke_fill=(60, 20, 90, 255))
    out = out.resize((W, H), Image.LANCZOS)
    return np.array(out)


def window(title, lines, width=860, body_size=40, ok=False, title_cols=((10, 20, 140), (240, 40, 200))):
    """Win9x-style dialog with gradient title bar (Y2K pink/blue)."""
    tb = 64; padb = 34
    f = ImageFont.truetype(F_PIX, body_size); ft = ImageFont.truetype(F_PIX, 26)
    lh = int(body_size * 1.6)
    bh = padb * 2 + lh * max(1, len(lines)) + (90 if ok else 0)
    W, H = width + 24, tb + bh + 24
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # drop shadow block (hard, retro)
    d.rectangle((14, 14, W - 1, H - 1), fill=(20, 10, 40, 150))
    x0, y0, x1, y1 = 0, 0, width, tb + bh
    d.rectangle((x0, y0, x1, y1), fill=(235, 234, 242, 255))
    d.line((x0, y0, x1, y0), fill=(255, 255, 255), width=4); d.line((x0, y0, x0, y1), fill=(255, 255, 255), width=4)
    d.line((x0, y1, x1, y1), fill=(60, 60, 80), width=4); d.line((x1, y0, x1, y1), fill=(60, 60, 80), width=4)
    g = np.linspace(0, 1, width - 12)
    c0, c1 = np.array(title_cols[0]), np.array(title_cols[1])
    for i, t in enumerate(g):
        c = tuple(int(v) for v in c0 * (1 - t) + c1 * t)
        d.line((6 + i, 6, 6 + i, tb), fill=c)
    d.text((22, 22), title, font=ft, fill=(255, 255, 255))
    # title buttons
    for k, ch in enumerate(["X", "", "_"]):
        bx = width - 16 - 52 * (k + 1) + 6
        d.rectangle((bx, 14, bx + 44, 56), fill=(225, 225, 232)); d.line((bx, 14, bx + 44, 14), fill=(255, 255, 255), width=3)
        d.line((bx, 56, bx + 44, 56), fill=(70, 70, 90), width=3); d.line((bx + 44, 14, bx + 44, 56), fill=(70, 70, 90), width=3)
        if ch == "X":
            d.line((bx + 13, 25, bx + 31, 45), fill=(20, 20, 30), width=5); d.line((bx + 31, 25, bx + 13, 45), fill=(20, 20, 30), width=5)
        elif ch == "_":
            d.rectangle((bx + 12, 41, bx + 32, 46), fill=(20, 20, 30))
        else:
            d.rectangle((bx + 12, 22, bx + 32, 46), outline=(20, 20, 30), width=4)
    for i, ln in enumerate(lines):
        d.text((34, tb + padb + i * lh), ln, font=f, fill=(20, 16, 40))
    if ok:
        bw, bhh = 220, 66; bx = width // 2 - bw // 2; by = tb + bh - 90
        d.rectangle((bx, by, bx + bw, by + bhh), fill=(225, 225, 232), outline=(20, 20, 30), width=3)
        d.line((bx + 3, by + 3, bx + bw - 3, by + 3), fill=(255, 255, 255), width=3)
        d.line((bx + 3, by + bhh - 4, bx + bw - 3, by + bhh - 4), fill=(80, 80, 100), width=3)
        fo = ImageFont.truetype(F_PIX, 32); tb_ = fo.getbbox("OK")
        d.text((bx + bw / 2 - (tb_[2] - tb_[0]) / 2 - tb_[0], by + bhh / 2 - (tb_[3] - tb_[1]) / 2 - tb_[1]), "OK", font=fo, fill=(20, 16, 40))
    return np.array(im)


def sparkle(r=60, col=(255, 255, 255), glow=(140, 220, 255)):
    S = 3; n = int(r * 2.6)
    im = Image.new("RGBA", (n * S, n * S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    _star(d, n * S / 2, n * S / 2, r * S, col + (255,), thin=0.16)
    a = np.array(im.resize((n, n), Image.LANCZOS)).astype(np.float32)
    gl = cv2.GaussianBlur(a[..., 3], (0, 0), r / 5)
    rgb = np.ones((n, n, 3), np.float32) * np.array(glow, np.float32)
    al = np.clip(gl * 1.4, 0, 255)
    m = a[..., 3:4] / 255
    rgb = rgb * (1 - m) + a[..., :3] * m
    al = np.maximum(al, a[..., 3])
    # tiny core dot
    return np.dstack([rgb, al]).astype(np.uint8)


_CUR = [
    "X...........",
    "XX..........",
    "XWX.........",
    "XWWX........",
    "XWWWX.......",
    "XWWWWX......",
    "XWWWWWX.....",
    "XWWWWWWX....",
    "XWWWWWWWX...",
    "XWWWWWWWWX..",
    "XWWWWWXXXXX.",
    "XWWXWWX.....",
    "XWX.XWWX....",
    "XX..XWWX....",
    "X....XWWX...",
    ".....XWWX...",
    "......XX....",
]


def cursor(scale=6):
    h, w = len(_CUR), len(_CUR[0])
    a = np.zeros((h, w, 4), np.uint8)
    for y, row in enumerate(_CUR):
        for x, ch in enumerate(row):
            if ch == "X": a[y, x] = (0, 0, 0, 255)
            elif ch == "W": a[y, x] = (255, 255, 255, 255)
    return cv2.resize(a, (w * scale, h * scale), interpolation=cv2.INTER_NEAREST)


def pixel_label(text, size=26, fg=(255, 255, 255), bg=(20, 10, 60, 200)):
    f = ImageFont.truetype(F_PIX, size); bb = f.getbbox(text)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    im = Image.new("RGBA", (w + 36, h + 26), bg); d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w + 35, h + 25), outline=(255, 120, 230, 255), width=3)
    d.text((18 - bb[0], 13 - bb[1]), text, font=f, fill=fg)
    return np.array(im)
