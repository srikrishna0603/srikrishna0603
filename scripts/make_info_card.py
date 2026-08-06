"""
make_info_card.py

Hand-authored neofetch-style info card SVG. Lines fade + slide in on
a stagger, like a terminal printing them one at a time, then freeze.

Set STATIC=1 to emit a frozen (non-animated) frame for local preview.

Usage:
    python scripts/make_info_card.py
Output:
    info-card.svg   (repo root)
"""
import os
from pathlib import Path

OUT = Path(__file__).parent.parent / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

# --- EDIT THESE — keep it factual, this is what recruiters actually read ---
TITLE = "srikrishna0603@github"
ROWS = [
    ("Now", "Final-year ECE @ CBIT Hyderabad · SDE Intern @ CES Neosilica"),
    ("Focus", "Software Engineering, applied to Computer Vision systems"),
    ("Stack", "Python · FastAPI · PyTorch · OpenCV · YOLOv11 · SQL"),
    ("Anchor 1", "Solar Panel Thermal Defect Detection (YOLOv11, 8-class)"),
    ("Anchor 2", "Multimodal Industrial Inspection & Analytics Assistant"),
]
# ----------------------------------------------------------------------------

WIDTH = 490
PAD_X = 20
TITLE_H = 34
ROW_H = 30
FONT = "monospace"
BG = "#0d1117"
BORDER = "#30363d"
TITLE_BG = "#161b22"
KEY_COLOR = "#58a6ff"
VAL_COLOR = "#c9d1d9"
STAGGER_S = 0.15
FADE_S = 0.4


def escape_xml(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    height = TITLE_H + ROW_H * len(ROWS) + 16

    parts = [
        f'<svg viewBox="0 0 {WIDTH} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="{FONT}">',
        f'<rect width="100%" height="100%" rx="8" fill="{BG}" '
        f'stroke="{BORDER}" stroke-width="1"/>',
        f'<rect width="100%" height="{TITLE_H}" rx="8" fill="{TITLE_BG}"/>',
        f'<rect y="{TITLE_H - 8}" width="100%" height="8" fill="{TITLE_BG}"/>',
        # traffic-light dots
        f'<circle cx="18" cy="{TITLE_H/2:.0f}" r="5" fill="#ff5f56"/>',
        f'<circle cx="34" cy="{TITLE_H/2:.0f}" r="5" fill="#ffbd2e"/>',
        f'<circle cx="50" cy="{TITLE_H/2:.0f}" r="5" fill="#27c93f"/>',
        f'<text x="{WIDTH/2}" y="{TITLE_H/2 + 4:.0f}" text-anchor="middle" '
        f'fill="{VAL_COLOR}" font-size="12">{escape_xml(TITLE)}</text>',
    ]

    for i, (key, val) in enumerate(ROWS):
        y = TITLE_H + 16 + i * ROW_H + ROW_H / 2
        key_txt = escape_xml(key)
        val_txt = escape_xml(val)
        opacity_attr = "1" if STATIC else "0"
        anim = ""
        transform_start = "translate(-8,0)"
        if not STATIC:
            delay = 0.5 + i * STAGGER_S
            anim = (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.2f}s" dur="{FADE_S}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-8,0" to="0,0" begin="{delay:.2f}s" dur="{FADE_S}s" '
                f'fill="freeze"/>'
            )
        parts.append(
            f'<g opacity="{opacity_attr}" transform="{transform_start}">'
            f'<text x="{PAD_X}" y="{y:.0f}" font-size="13" fill="{KEY_COLOR}">'
            f'{key_txt}</text>'
            f'<text x="{PAD_X + 90}" y="{y:.0f}" font-size="12" fill="{VAL_COLOR}">'
            f'{val_txt}</text>'
            f"{anim}</g>"
        )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    OUT.write_text(build_svg())
    print(f"Wrote {OUT}")
