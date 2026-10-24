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

try:
    from rembg import remove
except ModuleNotFoundError:
    # Background removal is an optional enhancement.  Keep the deterministic
    # grayscale pipeline usable in lightweight environments (for example,
    # GitHub/profile-art generation) where onnxruntime is not installed.
    remove = None

OUT_PATH = Path(__file__).parent / "source-prepped.png"


def prep(photo_path: str) -> None:
    src = Path(photo_path)
    if not src.exists():
        raise SystemExit(f"File not found: {photo_path}")

    # 1. Remove background when the optional rembg runtime is available.
    with open(src, "rb") as f:
        input_bytes = f.read()
    if remove is not None:
        output_bytes = remove(input_bytes)
    else:
        # Deterministic OpenCV fallback: keep the centered subject when the
        # optional ONNX background-removal model is unavailable.
        raw = cv2.imread(str(src), cv2.IMREAD_COLOR)
        if raw is None:
            raise SystemExit(f"Unable to read image: {photo_path}")
        h, w = raw.shape[:2]
        mask = np.full((h, w), cv2.GC_PR_BGD, dtype=np.uint8)
        margin_x, margin_y = max(8, w // 18), max(8, h // 24)
        mask[margin_y:h - margin_y, margin_x:w - margin_x] = cv2.GC_PR_FGD
        # The central face and torso are definite foreground anchors.
        cv2.ellipse(mask, (w // 2, int(h * .42)),
                    (max(20, int(w * .25)), max(20, int(h * .32))),
                    0, 0, 360, cv2.GC_FGD, -1)
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)
        cv2.grabCut(raw, mask, None, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_MASK)
        alpha = np.where(
            (mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD), 255, 0
        ).astype(np.uint8)
        rgba = cv2.cvtColor(raw, cv2.COLOR_BGR2RGBA)
        rgba[:, :, 3] = alpha
        output_bytes = cv2.imencode('.png', rgba)[1].tobytes()

    # 2. Composite the result onto a pure white background,
    #    so the removed background maps to the blank end of the ASCII ramp.
    from io import BytesIO
    fg = Image.open(BytesIO(output_bytes)).convert("RGBA")
    bbox = fg.getchannel("A").getbbox()
    if bbox:
        pad = max(12, int(min(fg.size) * 0.025))
        bbox = (
            max(0, bbox[0] - pad), max(0, bbox[1] - pad),
            min(fg.width, bbox[2] + pad), min(fg.height, bbox[3] + pad),
        )
        fg = fg.crop(bbox)
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
