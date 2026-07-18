#!/usr/bin/env python3
"""
make_heatmap_svg.py — animated terminal-style GitHub contribution heatmap.

Renders the last ~53 weeks of a user's public contribution calendar as a
self-contained SVG: a dark terminal-window frame around a grid of cells
that reveal one-by-one (SMIL opacity animation baked into the file, so it
plays for anyone viewing it as an <img>, including on GitHub).

Data source (in priority order):
  1. GitHub GraphQL API, if a token is available (GITHUB_TOKEN env var or
     --token). Gives exact per-day contribution counts.
  2. Public calendar fallback: https://github.com/users/<user>/contributions
     No auth required, works for any public profile, gives 5-level
     intensity buckets (same data GitHub itself renders with).

Usage:
    python make_heatmap_svg.py <username> <output.svg> [--token TOKEN]

Intended to run daily from a GitHub Action (see update-profile-art.yml),
but safe to run locally with zero setup — it'll just use the fallback path.
"""

import sys
import json
import os
import argparse
import datetime
import urllib.request
import re

CELL = 11          # px per cell
GAP = 3             # px gap between cells
LEFT_PAD = 28        # room for weekday labels
TOP_PAD = 34          # room for month labels + terminal title bar
RIGHT_PAD = 16
BOTTOM_PAD = 30
COLS = 53

# Blue-toned intensity ramp instead of GitHub green, to match a dark
# terminal aesthetic. Index = contribution level (0-4).
LEVEL_COLORS = ["#1f2335", "#2c3a5c", "#3f5b8f", "#5b85c9", "#7aa2f7"]

BG = "#1a1b26"
FRAME = "#2a2e42"
TEXT_DIM = "#565f89"
TEXT = "#c0caf5"
ACCENT = "#7aa2f7"


def fetch_via_graphql(username, token):
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                date
                contributionCount
                color
              }
            }
          }
        }
      }
    }
    """
    body = json.dumps({"query": query, "variables": {"login": username}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": username,
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())

    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    total = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]

    # bucket raw counts into 0-4 levels the same way GitHub's own UI does
    counts = [d["contributionCount"] for w in weeks for d in w["contributionDays"]]
    nonzero = sorted(c for c in counts if c > 0)

    def level_of(c):
        if c == 0:
            return 0
        if not nonzero:
            return 1
        q1 = nonzero[len(nonzero) // 4] if len(nonzero) >= 4 else nonzero[0]
        q2 = nonzero[len(nonzero) // 2] if len(nonzero) >= 2 else nonzero[-1]
        q3 = nonzero[3 * len(nonzero) // 4] if len(nonzero) >= 4 else nonzero[-1]
        if c <= q1:
            return 1
        if c <= q2:
            return 2
        if c <= q3:
            return 3
        return 4

    days = []
    for w in weeks:
        for d in w["contributionDays"]:
            days.append({"date": d["date"], "level": level_of(d["contributionCount"]), "count": d["contributionCount"]})
    return days, total


def fetch_via_public_page(username):
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode("utf-8", "ignore")

    cells = re.findall(r'data-date="([\d-]+)"[^>]*data-level="(\d)"', html)
    total_match = re.search(r'([\d,]+)\s*\n?\s*contributions?\s+in the last year', html)
    total = int(total_match.group(1).replace(",", "")) if total_match else sum(1 for _, l in cells if l != "0")

    days = [{"date": d, "level": int(lvl), "count": None} for d, lvl in cells]
    return days, total


def build_grid(days):
    """Map a flat list of {date, level} into [week][weekday] = day dict."""
    grid = [[None] * 7 for _ in range(COLS)]
    if not days:
        return grid
    first_date = datetime.date.fromisoformat(days[0]["date"])
    col_start = first_date - datetime.timedelta(days=first_date.weekday() + 1 if first_date.weekday() != 6 else 0)
    for day in days:
        d = datetime.date.fromisoformat(day["date"])
        weekday = (d.weekday() + 1) % 7  # convert Mon=0..Sun=6 -> Sun=0..Sat=6
        week_index = (d - col_start).days // 7
        if 0 <= week_index < COLS:
            grid[week_index][weekday] = day
    return grid


def month_labels(grid):
    labels = []
    seen = set()
    for col, week in enumerate(grid):
        for day in week:
            if day is None:
                continue
            d = datetime.date.fromisoformat(day["date"])
            key = (d.year, d.month)
            if d.day <= 7 and key not in seen:
                seen.add(key)
                labels.append((col, d.strftime("%b")))
            break
    return labels


def render_svg(days, total, username):
    grid = build_grid(days)
    width = LEFT_PAD + COLS * (CELL + GAP) + RIGHT_PAD
    height = TOP_PAD + 7 * (CELL + GAP) + BOTTOM_PAD

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
        f'width="{width}" height="{height}" font-family="Consolas, Menlo, monospace">'
    )
    # terminal frame
    parts.append(f'<rect x="0" y="0" width="{width}" height="{height}" rx="10" fill="{BG}" stroke="{FRAME}"/>')
    parts.append(f'<circle cx="16" cy="16" r="4.5" fill="#f7768e"/>')
    parts.append(f'<circle cx="32" cy="16" r="4.5" fill="#e0af68"/>')
    parts.append(f'<circle cx="48" cy="16" r="4.5" fill="#9ece6a"/>')
    parts.append(
        f'<text x="{width/2}" y="20" text-anchor="middle" fill="{TEXT_DIM}" font-size="11">'
        f'{username}@github ~ $ ./contributions.sh</text>'
    )

    for col, label in month_labels(grid):
        x = LEFT_PAD + col * (CELL + GAP)
        parts.append(f'<text x="{x}" y="{TOP_PAD - 6}" fill="{TEXT_DIM}" font-size="9">{label}</text>')

    day_labels = {1: "Mon", 3: "Wed", 5: "Fri"}
    for row, label in day_labels.items():
        y = TOP_PAD + row * (CELL + GAP) + CELL - 2
        parts.append(f'<text x="2" y="{y}" fill="{TEXT_DIM}" font-size="9">{label}</text>')

    idx = 0
    max_idx = sum(1 for week in grid for day in week if day is not None) or 1
    for col, week in enumerate(grid):
        for row, day in enumerate(week):
            if day is None:
                continue
            x = LEFT_PAD + col * (CELL + GAP)
            y = TOP_PAD + row * (CELL + GAP)
            color = LEVEL_COLORS[min(day["level"], 4)]
            delay = (idx / max_idx) * 2.2  # full sweep across ~2.2s
            idx += 1
            title = day["date"] + (f' • {day["count"]} contributions' if day.get("count") is not None else "")
            parts.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" fill="{color}" opacity="0.12">'
                f'<title>{title}</title>'
                f'<animate attributeName="opacity" from="0.12" to="1" begin="{delay:.3f}s" dur="0.25s" '
                f'fill="freeze"/>'
                f'</rect>'
            )

    parts.append(
        f'<text x="{LEFT_PAD}" y="{height - 10}" fill="{ACCENT}" font-size="10">'
        f'{total} contributions in the last year</text>'
    )
    parts.append(
        f'<text x="{width - RIGHT_PAD}" y="{height - 10}" text-anchor="end" fill="{TEXT_DIM}" font-size="9">'
        f'auto-updated daily</text>'
    )
    parts.append("</svg>")
    return "\n".join(parts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("username")
    ap.add_argument("output")
    ap.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"))
    ap.add_argument("--fixture", help=argparse.SUPPRESS)  # for local testing against saved JSON
    args = ap.parse_args()

    if args.fixture:
        with open(args.fixture) as f:
            raw = json.load(f)
        days = [{"date": d, "level": int(l), "count": None} for d, l in raw]
        total = sum(1 for d in days if d["level"] != 0)
    elif args.token:
        try:
            days, total = fetch_via_graphql(args.username, args.token)
        except Exception as e:
            print(f"GraphQL fetch failed ({e}), falling back to public page", file=sys.stderr)
            days, total = fetch_via_public_page(args.username)
    else:
        days, total = fetch_via_public_page(args.username)

    svg = render_svg(days, total, args.username)
    with open(args.output, "w") as f:
        f.write(svg)
    print(f"wrote {args.output} ({len(days)} days, {total} total contributions)")


if __name__ == "__main__":
    main()
