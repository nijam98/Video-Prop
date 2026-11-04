"""Draw the PT412 lot border (from the geran / Borang B2 plan) onto the drone photo.

The lot shape comes from the bearings and lengths on the land plan. It is placed
on the photo with a perspective fit to landmarks we can see (back wall, tree line
on the left, neighbour's fence on the right). Adjust IMAGE_ANCHORS to fine-tune.

Run: python3 draw_border_pt412.py
"""
import math

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

PHOTO = "input/drone_pt412.jpg"
OUT_PHOTO = "output/pt412_border.jpg"
OUT_OVERLAY = "output/pt412_border_overlay.png"  # transparent, for video editing

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
    print("corners (px):", {n: (round(x), round(y)) for n, (x, y) in zip(names, poly)})


if __name__ == "__main__":
    main()
