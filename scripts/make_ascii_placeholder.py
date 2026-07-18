#!/usr/bin/env python3
"""
make_ascii_placeholder.py — a no-photo-required placeholder for the ASCII
portrait slot: an ASCII-bordered monogram. Swap it out by running
make_ascii_svg.py on a real photo once you have one you like.
"""

import sys

BG = "#1a1b26"
FRAME = "#2a2e42"
BORDER = "#414868"
GLYPH = "#7aa2f7"
DIM = "#565f89"

WIDTH = 370
HEIGHT = 300


def render_svg(initials="PJ", username="piyush"):
    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" '
        f'width="{WIDTH}" height="{HEIGHT}" font-family="Consolas, Menlo, monospace">'
    )
    parts.append(f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" rx="10" fill="{BG}" stroke="{FRAME}"/>')
    parts.append('<circle cx="16" cy="16" r="4.5" fill="#f7768e"/>')
    parts.append('<circle cx="32" cy="16" r="4.5" fill="#e0af68"/>')
    parts.append('<circle cx="48" cy="16" r="4.5" fill="#9ece6a"/>')
    parts.append(
        f'<text x="{WIDTH/2}" y="20" text-anchor="middle" fill="{DIM}" font-size="11">'
        f'{username}@github ~ $ ./whoami.sh</text>'
    )

    # ASCII-style dashed border box framing the monogram
    bx, by, bw, bh = 40, 50, WIDTH - 80, 170
    dash = "+" + "-" * 30 + "+"
    parts.append(f'<text x="{bx}" y="{by}" fill="{BORDER}" font-size="12">{dash[:26]}</text>')
    parts.append(f'<text x="{bx}" y="{by + bh}" fill="{BORDER}" font-size="12">{dash[:26]}</text>')
    for y in range(by + 18, by + bh, 18):
        parts.append(f'<text x="{bx}" y="{y}" fill="{BORDER}" font-size="12">|</text>')
        parts.append(f'<text x="{bx + bw - 8}" y="{y}" fill="{BORDER}" font-size="12">|</text>')

    parts.append(
        f'<text x="{WIDTH/2}" y="{by + bh/2 + 14}" text-anchor="middle" fill="{GLYPH}" '
        f'font-size="64" font-weight="bold" opacity="0">{initials}'
        f'<animate attributeName="opacity" from="0" to="1" begin="0.2s" dur="0.6s" fill="freeze"/>'
        f'</text>'
    )

    parts.append(
        f'<text x="{WIDTH/2}" y="{by + bh + 34}" text-anchor="middle" fill="{DIM}" font-size="11">'
        f'// portrait pending</text>'
    )
    parts.append(
        f'<text x="{WIDTH/2}" y="{by + bh + 52}" text-anchor="middle" fill="{DIM}" font-size="10">'
        f'run make_ascii_svg.py on a photo to replace this</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    output = sys.argv[1] if len(sys.argv) > 1 else "ascii-portrait.svg"
    with open(output, "w") as f:
        f.write(render_svg())
    print(f"wrote {output}")
