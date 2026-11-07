# Clean Y2K grade: footage stays sharp and real. Lights keep their glow (bloom), a little more punch,
# cool cyan shadows + soft pink highlights, light sharpen.
import cv2, numpy as np
W, H = 1080, 1920
TONE_SH = np.array([0.035, 0.012, -0.012], np.float32)   # BGR: cool shadows
TONE_HI = np.array([0.010, -0.006, 0.020], np.float32)   # BGR: soft pink highlights


def grade(bgr):
    f = bgr.astype(np.float32) / 255
    sm = cv2.resize(f, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    br = np.clip((sm.max(2) - 0.72) / 0.28, 0, 1) ** 1.5
    b = sm * br[..., None]
    glow = cv2.GaussianBlur(b, (0, 0), 4) * 0.55 + cv2.GaussianBlur(b, (0, 0), 13) * 0.5
    glow = cv2.resize(glow, (W, H), interpolation=cv2.INTER_LINEAR)
    s = f * f * (3 - 2 * f)
    f = 0.8 * f + 0.2 * s
    g = f.mean(2, keepdims=True)
    f = g + (f - g) * 1.12
    L = f.mean(2, keepdims=True)
    f = f + (1 - L) ** 2 * TONE_SH + L ** 2 * TONE_HI
    f = 1 - (1 - np.clip(f, 0, 1)) * (1 - np.clip(glow, 0, 1) * 0.8)
    o = np.clip(f * 255 + 0.5, 0, 255).astype(np.uint8)
    bl = cv2.GaussianBlur(o, (0, 0), 1.0)
    return cv2.addWeighted(o, 1.3, bl, -0.3, 0)
