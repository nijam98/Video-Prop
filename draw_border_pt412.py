"""Draw the PT412 lot border (from the geran / Borang B2 plan) onto the drone photo.

The lot shape comes from the bearings and lengths on the land plan. It is placed
on the photo with a perspective fit to landmarks we can see (back wall, tree line
on the left, neighbour's fence on the right). Adjust IMAGE_ANCHORS to fine-tune.

Also makes a version with the geran drawing itself laid inside the lot.

Run: python3 draw_border_pt412.py
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PHOTO = "input/drone_pt412.jpg"
OUT_PHOTO = "output/pt412_border.jpg"
OUT_OVERLAY = "output/pt412_border_overlay.png"  # transparent, for video editing
GERAN = "input/geran_pt412.png"
OUT_GERAN = "output/pt412_geran_overlay.jpg"
GERAN_OPACITY = 0.75  # how solid the geran paper looks on the lot

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def deg(d, m=0, s=0):
    return d + m / 60 + s / 3600


# Boundary legs of PT412, clockwise from the north-west corner (bearing, metres).
# Copied from the geran plan.
LEGS = [
    ("A", deg(93, 3), 11.623),
    ("B", deg(101, 54, 10), 12.232),
    ("C", deg(111, 46, 50), 15.059),
    ("D", deg(207, 14), 26.689),
    ("E", deg(147, 40, 50), 15.987),
    ("F", deg(237, 29), 6.096),
    ("G", deg(311, 45, 40), 38.624),
    ("H", deg(356, 35, 50), 24.822),
]

# Where some plan corners appear in the photo (pixels).
IMAGE_ANCHORS = {
    "A": (1105, 245),  # NW: back wall meets the left tree line
    "D": (1490, 255),  # NE: back wall meets the right tree line
    "E": (1480, 480),  # start of neighbour's (PT413) fence
    "F": (1810, 760),  # bend in neighbour's fence
    "H": (1058, 450),  # SW: on the left tree line (Kawasan Hijau)
}


# PT412 corners in the geran scan (pixels), same order as LEGS.
GERAN_CORNERS = {
    "A": (490, 1274), "B": (567, 1280), "C": (646, 1295), "D": (737, 1334),
    "E": (657, 1490), "F": (713, 1582), "G": (680, 1603), "H": (499, 1440),
}


def plan_points():
    pts, x, y = {}, 0.0, 0.0
    for name, bearing, dist in LEGS:
        pts[name] = (x, y)
        r = math.radians(bearing)
        x += math.sin(r) * dist
        y += math.cos(r) * dist
    return pts


def fit_homography(src, dst):
    rows = []
    for (x, y), (u, v) in zip(src, dst):
        rows.append([-x, -y, -1, 0, 0, 0, u * x, u * y, u])
        rows.append([0, 0, 0, -x, -y, -1, v * x, v * y, v])
    _, _, vt = np.linalg.svd(np.array(rows))
    h = vt[-1].reshape(3, 3)
    return h / h[2, 2]


def project(h, p):
    q = h @ [p[0], p[1], 1.0]
    return (q[0] / q[2], q[1] / q[2])


def fit_homography_lsq(src, dst):
    """Least-squares homography (h33 = 1) for more than 4 point pairs."""
    rows, rhs = [], []
    for (x, y), (u, v) in zip(src, dst):
        rows.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); rhs.append(u)
        rows.append([0, 0, 0, x, y, 1, -v * x, -v * y]); rhs.append(v)
    sol, *_ = np.linalg.lstsq(np.array(rows), np.array(rhs), rcond=None)
    return np.append(sol, 1.0).reshape(3, 3)


GERAN_UPSCALE = 4


def clean_scan(scan, k):
    """Flatten uneven lighting, then turn the scan into crisp black ink on white."""
    big = scan.resize((scan.width * k, scan.height * k), Image.BICUBIC)
    a = np.asarray(big, dtype=np.float32)
    bg = np.asarray(big.filter(ImageFilter.GaussianBlur(25 * k)), dtype=np.float32)
    ratio = a / np.maximum(bg, 1)  # paper ~1.0, ink well below
    smooth = Image.fromarray(np.clip(ratio * 200, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(k * 0.6))
    r = np.asarray(smooth, dtype=np.float32) / 200
    # Soft threshold: below 0.72 is ink, above 0.86 is paper.
    v = np.clip((r - 0.72) / 0.14, 0, 1) * 255
    return Image.fromarray(v.astype(np.uint8))


def geran_layer(size, poly):
    """Geran scan warped onto the lot, clipped to the lot shape."""
    names = [n for n, _, _ in LEGS]
    # Map photo pixels -> geran pixels (PIL wants output -> input).
    m = fit_homography_lsq(poly, [GERAN_CORNERS[n] for n in names])
    scan = clean_scan(Image.open(GERAN).convert("L"), GERAN_UPSCALE)
    m = np.diag([GERAN_UPSCALE, GERAN_UPSCALE, 1.0]) @ m  # geran px -> upscaled px
    m = m / m[2, 2]
    warped = scan.transform(size, Image.PERSPECTIVE, tuple(m.flatten()[:8]), Image.BICUBIC, fillcolor=255)
    paper = Image.new("RGBA", size, (252, 250, 243, 255))
    # Ink a dark navy so the lines read like a printed plan.
    ink = Image.new("RGBA", size, (20, 30, 70, 255))
    layer = Image.composite(paper, ink, warped)
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).polygon(poly, fill=int(255 * GERAN_OPACITY))
    layer.putalpha(mask)
    return layer


def text_with_outline(draw, xy, text, font, fill, anchor="mm"):
    draw.text(xy, text, font=font, fill=fill, anchor=anchor,
              stroke_width=max(3, font.size // 8), stroke_fill=(0, 0, 0, 230))


def main():
    photo = Image.open(PHOTO).convert("RGBA")
    W, H = photo.size
    plan = plan_points()
    names = [n for n, _, _ in LEGS]
    h = fit_homography([plan[k] for k in IMAGE_ANCHORS], list(IMAGE_ANCHORS.values()))

    # Draw on a 2x canvas, then downscale for smooth lines.
    S = 2
    poly = [project(h, plan[n]) for n in names]
    polyS = [(x * S, y * S) for x, y in poly]

    overlay = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))

    # Soft dark shadow under the line so it reads on grass and trees.
    shadow = Image.new("RGBA", overlay.size, (0, 0, 0, 0))
    ImageDraw.Draw(shadow).line(polyS + [polyS[0]], fill=(0, 0, 0, 170), width=22 * S, joint="curve")
    overlay.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(6 * S)))

    d = ImageDraw.Draw(overlay)
    d.polygon(polyS, fill=(255, 214, 0, 55))
    d.line(polyS + [polyS[0]], fill=(255, 255, 255, 255), width=14 * S, joint="curve")
    d.line(polyS + [polyS[0]], fill=(255, 196, 0, 255), width=8 * S, joint="curve")
    for x, y in polyS:
        r = 9 * S
        d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 196, 0, 255), outline=(255, 255, 255, 255), width=3 * S)

    # Edge lengths, placed just outside each edge.
    cx = sum(p[0] for p in polyS) / len(polyS)
    cy = sum(p[1] for p in polyS) / len(polyS)
    small = ImageFont.truetype(FONT, 22 * S)
    for i, (_, _, dist) in enumerate(LEGS):
        (x1, y1), (x2, y2) = polyS[i], polyS[(i + 1) % len(polyS)]
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        nx, ny = -(y2 - y1), (x2 - x1)
        n = math.hypot(nx, ny) or 1
        nx, ny = nx / n, ny / n
        if (mx - cx) * nx + (my - cy) * ny < 0:
            nx, ny = -nx, -ny
        off = 28 * S
        text_with_outline(d, (mx + nx * off, my + ny * off), f"{dist:.1f} m", small, (255, 255, 255, 255))

    # Lot label in the middle of the lot (use plan centroid for a natural spot).
    pc = (sum(plan[n][0] for n in names) / len(names), sum(plan[n][1] for n in names) / len(names))
    lx, ly = project(h, pc)
    big = ImageFont.truetype(FONT, 54 * S)
    mid = ImageFont.truetype(FONT, 30 * S)
    text_with_outline(d, (lx * S, ly * S - 30 * S), "PT 412", big, (255, 214, 0, 255))
    text_with_outline(d, (lx * S, ly * S + 28 * S), "1079 m²", mid, (255, 255, 255, 255))

    overlay = overlay.resize((W, H), Image.LANCZOS)
    overlay.save(OUT_OVERLAY)
    out = photo.copy()
    out.alpha_composite(overlay)
    out.convert("RGB").save(OUT_PHOTO, quality=93)
    # Version with the geran drawing laid inside the lot.
    border_only = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    bd = ImageDraw.Draw(border_only)
    bd.line(polyS + [polyS[0]], fill=(255, 255, 255, 255), width=14 * S, joint="curve")
    bd.line(polyS + [polyS[0]], fill=(255, 196, 0, 255), width=8 * S, joint="curve")
    border_only = border_only.resize((W, H), Image.LANCZOS)
    g = photo.copy()
    g.alpha_composite(shadow.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(4)))
    g.alpha_composite(geran_layer((W, H), poly))
    g.alpha_composite(border_only)
    g.convert("RGB").save(OUT_GERAN, quality=93)

    print("corners (px):", {n: (round(x), round(y)) for n, (x, y) in zip(names, poly)})


if __name__ == "__main__":
    main()
