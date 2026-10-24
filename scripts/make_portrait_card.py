"""Create a recognizable terminal-style portrait card from a supplied photo."""
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw


OUT = Path(__file__).parent.parent / "avi-portrait.png"
SIZE = (640, 640)


def build(source: str) -> None:
    image = Image.open(source).convert("RGB")
    w, h = image.size
    # A portrait crop that keeps the face and shoulders, not the room.
    side = min(w, int(h * 0.78))
    left = max(0, (w - side) // 2)
    top = max(0, int(h * 0.055))
    crop = image.crop((left, top, min(w, left + side), min(h, top + side)))
    crop = ImageOps.fit(crop, SIZE, method=Image.Resampling.LANCZOS, centering=(0.5, 0.47))

    gray = ImageOps.grayscale(crop)
    gray = ImageEnhance.Contrast(gray).enhance(1.35)
    gray = ImageEnhance.Brightness(gray).enhance(1.08)
    gray = ImageEnhance.Sharpness(gray).enhance(1.35)
    gray = gray.filter(ImageFilter.UnsharpMask(radius=1.4, percent=130, threshold=3))
    arr = np.asarray(gray, dtype=np.float32) / 255.0
    # Pull attention toward the face and shoulders so the bright window does
    # not compete with the portrait at GitHub's small display size.
    yy, xx = np.mgrid[0:SIZE[1], 0:SIZE[0]]
    focus = np.exp(-(((xx / SIZE[0] - 0.56) / 0.42) ** 2 +
                     ((yy / SIZE[1] - 0.46) / 0.55) ** 2))
    arr = arr * (0.48 + 0.52 * focus)

    # Deep navy to cyan to warm-white palette: terminal identity, readable face.
    stops = np.array([
        [5, 12, 24],
        [8, 45, 70],
        [24, 143, 181],
        [127, 230, 244],
        [239, 248, 242],
    ], dtype=np.float32)
    indexes = arr * (len(stops) - 1)
    lo = np.floor(indexes).astype(int).clip(0, len(stops) - 2)
    hi = lo + 1
    mix = (indexes - lo)[..., None]
    rgb = (stops[lo] * (1 - mix) + stops[hi] * mix).astype(np.uint8)
    result = Image.fromarray(rgb, "RGB")

    # Subtle terminal scanlines without obscuring facial landmarks.
    draw = ImageDraw.Draw(result, "RGBA")
    for y in range(0, SIZE[1], 8):
        draw.line((0, y, SIZE[0], y), fill=(0, 8, 20, 28), width=1)
    for x in range(0, SIZE[0], 32):
        draw.line((x, 0, x, SIZE[1]), fill=(80, 226, 245, 10), width=1)
    result.save(OUT, optimize=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/make_portrait_card.py <photo>")
    build(sys.argv[1])
