#!/usr/bin/env python3
"""
make_ascii_svg.py — converts a photo into a terminal-style ASCII-art
portrait SVG, with a line-by-line "typing in" reveal animation.

Usage:
    python make_ascii_svg.py <photo.jpg> <output.svg> [--cols 60]

Requires Pillow:  pip install Pillow
"""

import sys
import argparse
from PIL import Image, ImageOps

# Dark-to-bright ramp. Rendered on a dark terminal background, so bright
# pixels get the "densest" glyph and dark/background pixels get a space —
# this reads as a bright portrait glowing out of a black terminal, rather
# than classic light-background ASCII art (which would be inverted).
RAMP = " .:-=+*#%@"

BG = "#1a1b26"
FRAME = "#2a2e42"
GLYPH_COLOR = "#7aa2f7"
BRIGHT_COLOR = "#c0caf5"

# Monospace glyphs are roughly twice as tall as they are wide, so we
# under-sample rows relative to columns to keep the portrait's proportions
# correct instead of stretched.
CHAR_ASPECT = 0.55


def image_to_ascii_rows(path, cols):
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)  # respect phone photo orientation
    img = img.convert("L")  # grayscale

    w, h = img.size
    rows = max(1, round((h / w) * cols * CHAR_ASPECT))
    img = img.resize((cols, rows))

    pixels = list(img.getdata())
    ramp_len = len(RAMP) - 1
    lines = []
    for r in range(rows):
        row_pixels = pixels[r * cols:(r + 1) * cols]
        line = "".join(RAMP[int((p / 255) * ramp_len)] for p in row_pixels)
        lines.append(line)
    return lines


def escape_xml(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def render_svg(lines, username="piyush"):
    cols = max(len(l) for l in lines) if lines else 1
    font_size = 7
    char_w = font_size * 0.6
    line_h = font_size * 1.05

    pad_top = 34
    pad_x = 14
    pad_bottom = 14
    width = pad_x * 2 + cols * char_w
    height = pad_top + len(lines) * line_h + pad_bottom

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}" font-family="Consolas, Menlo, monospace">'
    )
    parts.append(f'<rect x="0" y="0" width="{width:.0f}" height="{height:.0f}" rx="10" fill="{BG}" stroke="{FRAME}"/>')
    parts.append('<circle cx="16" cy="16" r="4.5" fill="#f7768e"/>')
    parts.append('<circle cx="32" cy="16" r="4.5" fill="#e0af68"/>')
    parts.append('<circle cx="48" cy="16" r="4.5" fill="#9ece6a"/>')
    parts.append(
        f'<text x="{width/2:.0f}" y="20" text-anchor="middle" fill="#565f89" font-size="11">'
        f'{username}@github ~ $ ./whoami.sh</text>'
    )

    parts.append(
        f'<text x="{pad_x}" y="{pad_top}" font-size="{font_size}" fill="{GLYPH_COLOR}" '
        f'xml:space="preserve" style="white-space:pre">'
    )
    for i, line in enumerate(lines):
        y = pad_top + i * line_h
        delay = i * 0.04
        parts.append(
            f'<tspan x="{pad_x}" y="{y:.1f}" opacity="0.1">{escape_xml(line)}'
            f'<animate attributeName="opacity" from="0.1" to="1" begin="{delay:.2f}s" '
            f'dur="0.15s" fill="freeze"/></tspan>'
        )
    parts.append("</text>")
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo")
    ap.add_argument("output")
    ap.add_argument("--cols", type=int, default=60)
    ap.add_argument("--username", default="piyush")
    args = ap.parse_args()

    lines = image_to_ascii_rows(args.photo, args.cols)
    svg = render_svg(lines, args.username)
    with open(args.output, "w") as f:
        f.write(svg)
    print(f"wrote {args.output} ({len(lines)} rows x {args.cols} cols)")


if __name__ == "__main__":
    main()
