#!/usr/bin/env python3
"""
make_info_card.py — neofetch-style "whoami" terminal card for a GitHub
profile README. Static by design (this data changes rarely) — edit the
FIELDS list below and re-run whenever your stack/focus/goals change.

Usage:
    python make_info_card.py <output.svg>
"""

import sys

BG = "#1a1b26"
FRAME = "#2a2e42"
LABEL = "#7aa2f7"
VALUE = "#c0caf5"
DIM = "#565f89"
TITLE = "#9ece6a"

WIDTH = 490
LINE_H = 24
PAD_TOP = 56
PAD_X = 24

# Edit these to update the card — order is preserved top to bottom.
FIELDS = [
    ("OS", "Full-Stack Developer"),
    ("Host", "J.C. Bose University — Computer Engineering"),
    ("Shell", "JavaScript / TypeScript"),
    ("Languages", "JS · TS · Python · C++"),
    ("Frameworks", "React · Node.js · Express"),
    ("Databases", "MongoDB · PostgreSQL"),
    ("Building", "First SaaS MVP"),
    ("Status", "🟢 Open to Internships"),
    ("2026 Goals", "5 projects · 500+ DSA · OSS"),
]

SWATCHES = ["#1a1b26", "#f7768e", "#9ece6a", "#e0af68", "#7aa2f7", "#bb9af7", "#7dcfff", "#c0caf5"]


def render_svg(username="piyush"):
    height = PAD_TOP + len(FIELDS) * LINE_H + 46
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" '
        f'width="{WIDTH}" height="{height}" font-family="Consolas, Menlo, monospace">'
    )
    parts.append(f'<rect x="0" y="0" width="{WIDTH}" height="{height}" rx="10" fill="{BG}" stroke="{FRAME}"/>')
    parts.append('<circle cx="16" cy="16" r="4.5" fill="#f7768e"/>')
    parts.append('<circle cx="32" cy="16" r="4.5" fill="#e0af68"/>')
    parts.append('<circle cx="48" cy="16" r="4.5" fill="#9ece6a"/>')
    parts.append(
        f'<text x="{WIDTH/2}" y="20" text-anchor="middle" fill="{DIM}" font-size="11">'
        f'{username}@github ~ $ whoami</text>'
    )

    header = f"{username}@github"
    parts.append(f'<text x="{PAD_X}" y="{PAD_TOP - 12}" fill="{TITLE}" font-size="15" font-weight="bold">{header}</text>')
    parts.append(
        f'<line x1="{PAD_X}" y1="{PAD_TOP - 4}" x2="{WIDTH - PAD_X}" y2="{PAD_TOP - 4}" '
        f'stroke="{FRAME}" stroke-width="1"/>'
    )

    y = PAD_TOP + LINE_H - 6
    label_w = 118
    for i, (label, value) in enumerate(FIELDS):
        delay = i * 0.09
        parts.append(
            f'<g opacity="0.15"><animate attributeName="opacity" from="0.15" to="1" '
            f'begin="{delay:.2f}s" dur="0.3s" fill="freeze"/>'
            f'<text x="{PAD_X}" y="{y}" fill="{LABEL}" font-size="13">{label}</text>'
            f'<text x="{PAD_X + label_w}" y="{y}" fill="{VALUE}" font-size="13">{value}</text>'
            f'</g>'
        )
        y += LINE_H

    sw_y = y + 6
    sw_size = 16
    for i, color in enumerate(SWATCHES):
        sx = PAD_X + i * (sw_size + 4)
        parts.append(f'<rect x="{sx}" y="{sw_y}" width="{sw_size}" height="{sw_size}" rx="3" fill="{color}"/>')

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "info-card.svg"
    username = sys.argv[2] if len(sys.argv) > 2 else "piyush"
    with open(output, "w") as f:
        f.write(render_svg(username))
    print(f"wrote {output}")
