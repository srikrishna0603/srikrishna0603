"""
render_heatmap_svg.py

Renders data/contributions.json as a 53-week x 7-day grid of rounded
boxes. Reveals once with a diagonal, line-after-line slide-down, then
freezes (no looping "glow").

Usage:
    python scripts/render_heatmap_svg.py
Output:
    contrib-heatmap.svg   (repo root)
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "contributions.json"
OUT = Path(__file__).parent.parent / "contrib-heatmap.svg"

PALETTE = ["#0d1117", "#4a044e", "#86198f", "#d946ef", "#f0abfc", "#fdf4ff"]

CELL = 11
GAP = 3
LEFT_PAD = 30
TOP_PAD = 20
STAGGER_S = 0.012
FADE_S = 0.25


def load() -> dict:
    if not DATA.exists():
        raise SystemExit("Missing data/contributions.json — run fetch_contributions.py first")
    return json.loads(DATA.read_text())


def build_weeks(days: list[dict]) -> list[list[dict | None]]:
    by_date = {d["date"]: d for d in days}
    first = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    # Align to the preceding Sunday so columns are full weeks.
    start = first
    while start.weekday() != 6:  # walk back to the preceding Sunday
        start = start.fromordinal(start.toordinal() - 1)

    last = datetime.strptime(days[-1]["date"], "%Y-%m-%d").date()

    weeks: list[list[dict | None]] = []
    cur = start
    week: list[dict | None] = []
    while cur <= last:
        cell = by_date.get(cur.isoformat())
        week.append(cell)
        if cur.weekday() == 5:  # Saturday -> close out the week column
            weeks.append(week)
            week = []
        cur = cur.fromordinal(cur.toordinal() + 1)
    if week:
        weeks.append(week)
    return weeks


def build_svg(weeks: list[list[dict | None]], stats: dict) -> str:
    n_weeks = len(weeks)
    width = LEFT_PAD + n_weeks * (CELL + GAP) + 20
    height = TOP_PAD + 7 * (CELL + GAP) + 40

    parts = [
        f'<svg viewBox="0 0 {width:.0f} {height:.0f}" '
        f'xmlns="http://www.w3.org/2000/svg" font-family="monospace">',
        '<rect width="100%" height="100%" fill="transparent"/>',
    ]

    idx = 0
    for w, week in enumerate(weeks):
        for d in range(7):
            cell = week[d] if d < len(week) else None
            level = cell["level"] if cell else 0
            x = LEFT_PAD + w * (CELL + GAP)
            y = TOP_PAD + d * (CELL + GAP)
            delay = 0.5 + (w + d) * STAGGER_S  # diagonal stagger
            color = PALETTE[min(level, len(PALETTE) - 1)]
            parts.append(
                f'<rect x="{x}" y="{y - 6}" width="{CELL}" height="{CELL}" rx="2" '
                f'fill="{color}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" '
                f'begin="{delay:.3f}s" dur="{FADE_S}s" fill="freeze"/>'
                f'<animate attributeName="y" from="{y-6}" to="{y}" '
                f'begin="{delay:.3f}s" dur="{FADE_S}s" fill="freeze" '
                f'calcMode="spline" keySplines="0.3 0 0.2 1"/>'
                f"</rect>"
            )
            idx += 1

    # legend
    legend_y = height - 14
    parts.append(
        f'<text x="{LEFT_PAD}" y="{legend_y}" font-size="10" fill="#8b949e">Less</text>'
    )
    lx = LEFT_PAD + 34
    for c in PALETTE:
        parts.append(f'<rect x="{lx}" y="{legend_y-9}" width="{CELL}" height="{CELL}" rx="2" fill="{c}"/>')
        lx += CELL + GAP
    parts.append(f'<text x="{lx+4}" y="{legend_y}" font-size="10" fill="#8b949e">More</text>')

    footer = f"{stats['total_active_days']} active days · {stats['longest_streak']}-day longest streak · {stats['current_streak']}-day current streak"
    parts.append(
        f'<text x="{width - 20}" y="{legend_y}" font-size="10" fill="#8b949e" '
        f'text-anchor="end">{footer}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    payload = load()
    weeks = build_weeks(payload["days"])
    svg = build_svg(weeks, payload["stats"])
    OUT.write_text(svg)
    print(f"Wrote {OUT}")
