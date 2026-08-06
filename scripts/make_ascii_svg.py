"""
make_ascii_svg.py

Converts scripts/source-prepped.png into a self-typing, monochrome
ASCII-art SVG. Each row wipes in left-to-right, staggered top to
bottom, then freezes (no looping).

Usage:
    python scripts/make_ascii_svg.py
Output:
    avi-ascii.svg   (repo root)
"""
from pathlib import Path

import numpy as np
from PIL import Image

# Bright (sparse) -> dark (dense). Leading space clears the background.
RAMP = " .`:-=+*cs#%@"

GRID_COLS = 100
GRID_ROWS = 53
FONT_SIZE = 8
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.05
FILL_COLOR = "#4cc9f0"  # Vibrant cyberpunk cyan
STAGGER_S = 0.02        # delay added per row
WIPE_S = 0.35           # duration of each row's wipe

SRC = Path(__file__).parent / "source-prepped.png"
OUT = Path(__file__).parent.parent / "avi-ascii.svg"


def image_to_ascii_rows(img: Image.Image) -> list[str]:
    img = img.convert("L").resize((GRID_COLS, GRID_ROWS))
    arr = np.array(img)
    rows = []
    ramp_len = len(RAMP) - 1
    for r in range(GRID_ROWS):
        line = []
        for c in range(GRID_COLS):
            brightness = arr[r, c] / 255.0
            idx = int((1 - brightness) * ramp_len)
            line.append(RAMP[idx])
        rows.append("".join(line))
    return rows


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(rows: list[str]) -> str:
    width = GRID_COLS * CHAR_W
    height = GRID_ROWS * CHAR_H

    parts = [
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="monospace" '
        f'font-size="{FONT_SIZE}">',
        f'<rect width="100%" height="100%" fill="transparent"/>',
    ]



    for i, row in enumerate(rows):
        y = (i + 1) * CHAR_H - (CHAR_H * 0.25)
        text = escape_xml(row.rstrip())
        if not text.strip():
            continue
        delay = 0.5 + i * STAGGER_S
        parts.append(
            f'<g opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" '
            f'begin="{delay:.2f}s" dur="{WIPE_S}s" fill="freeze"/>'
            f'<text x="0" y="{y:.1f}" fill="{FILL_COLOR}" '
            f'xml:space="preserve">{text}</text></g>'
        )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    if not SRC.exists():
        raise SystemExit(
            f"Missing {SRC}. Run prep_photo.py first: "
            "python scripts/prep_photo.py source-photo.jpg"
        )
    img = Image.open(SRC)
    rows = image_to_ascii_rows(img)
    svg = build_svg(rows)
    OUT.write_text(svg)
    print(f"Wrote {OUT}")
