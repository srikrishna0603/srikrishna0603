"""
prep_photo.py

Turns a normal photo into a clean, high-contrast grayscale image ready
for ASCII conversion. Run this once per photo, not on every commit.

Usage:
    python scripts/prep_photo.py source-photo.jpg
Output:
    scripts/source-prepped.png
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

OUT_PATH = Path(__file__).parent / "source-prepped.png"


def prep(photo_path: str) -> None:
    src = Path(photo_path)
    if not src.exists():
        raise SystemExit(f"File not found: {photo_path}")

    # 1. Remove background so only the subject remains.
    with open(src, "rb") as f:
        input_bytes = f.read()
    output_bytes = remove(input_bytes)

    # 2. Composite the transparent result onto a pure white background,
    #    so the removed background maps to the blank end of the ASCII ramp.
    from io import BytesIO
    fg = Image.open(BytesIO(output_bytes)).convert("RGBA")
    white_bg = Image.new("RGBA", fg.size, (255, 255, 255, 255))
    composited = Image.alpha_composite(white_bg, fg).convert("RGB")

    # 3. Boost local contrast with CLAHE so flat lighting still reads
    #    with real highlights and shadows once it's ASCII.
    arr = np.array(composited)
    gray = cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    Image.fromarray(enhanced).save(OUT_PATH)
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/prep_photo.py <photo.jpg>")
    prep(sys.argv[1])
