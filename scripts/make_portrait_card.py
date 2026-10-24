"""Create a recognizable terminal-style portrait card from a supplied photo."""
from pathlib import Path
import sys

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageDraw


OUT = Path(__file__).parent.parent / "avi-portrait-natural.png"
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

    # Keep the founder's real colors and facial landmarks; add restrained
    # polish so the image remains recognizable at GitHub's small size.
    result = ImageEnhance.Color(crop).enhance(1.08)
    result = ImageEnhance.Contrast(result).enhance(1.10)
    result = ImageEnhance.Sharpness(result).enhance(1.30)
    result = result.filter(ImageFilter.UnsharpMask(radius=1.1, percent=115, threshold=3))

    # Navy edge vignette creates the terminal-card feel without recoloring the face.
    yy, xx = np.mgrid[0:SIZE[1], 0:SIZE[0]]
    distance = np.sqrt(((xx - SIZE[0] * .52) / (SIZE[0] * .72)) ** 2 +
                       ((yy - SIZE[1] * .45) / (SIZE[1] * .76)) ** 2)
    alpha = np.clip((distance - .48) * 150, 0, 105).astype(np.uint8)
    vignette = Image.new("RGBA", SIZE, (4, 12, 26, 0))
    vignette.putalpha(Image.fromarray(alpha, "L"))
    result = Image.alpha_composite(result.convert("RGBA"), vignette)

    draw = ImageDraw.Draw(result, "RGBA")
    draw.rectangle((10, 10, SIZE[0] - 11, SIZE[1] - 11), outline=(80, 221, 239, 210), width=2)
    draw.rectangle((18, 18, SIZE[0] - 19, SIZE[1] - 19), outline=(215, 178, 103, 150), width=1)
    for x, y in ((31, 31), (SIZE[0] - 91, SIZE[1] - 39)):
        draw.line((x, y, x + 24, y), fill=(80, 221, 239, 180), width=2)
        draw.line((x + 30, y, x + 44, y), fill=(215, 178, 103, 170), width=2)
        draw.line((x + 50, y, x + 72, y), fill=(80, 221, 239, 110), width=2)
    result.convert("RGB").save(OUT, optimize=True)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/make_portrait_card.py <photo>")
    build(sys.argv[1])
