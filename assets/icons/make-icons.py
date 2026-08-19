#!/usr/bin/env python3
"""Generate the site icons from the CSS tokens.

The mark is a drawing sheet quartered with one cell filled. It is nothing but
axis-aligned rectangles, so the raster versions are written pixel by pixel on a
32px grid rather than rasterised from the SVG: at tab size that is sharper than
any converter, and it needs no dependency (no rsvg, no cairo, no ImageMagick).

    python3 make-icons.py             # write icon.svg, icon-32.png, icon-192.png
    python3 make-icons.py --selfcheck # no files written, no network

ponytail: hard-codes one 32px layout. If the mark ever stops being rectangles,
render the SVG in a real rasteriser instead of extending this.
"""

import argparse
import struct
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent

# straight from :root in assets/css/main.css
GROUND_OKLCH = (0.192, 0.036, 255.0)
DRAW_OKLCH = (0.840, 0.120, 200.0)

SIZE = 32  # the design grid; every raster size is an integer multiple


def oklch_to_srgb8(L, C, h_deg):
    """OKLCH -> 8-bit sRGB, clipped. Keeps the icon matching the CSS tokens."""
    import math

    h = math.radians(h_deg)
    a, b = C * math.cos(h), C * math.sin(h)

    l_ = L + 0.3963377774 * a + 0.2158037573 * b
    m_ = L - 0.1055613458 * a - 0.0638541728 * b
    s_ = L - 0.0894841775 * a - 1.2914855480 * b
    l, m, s = l_ ** 3, m_ ** 3, s_ ** 3

    lin = (
        +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    )

    out = []
    for v in lin:
        v = max(0.0, min(1.0, v))
        v = 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055
        out.append(max(0, min(255, round(v * 255))))
    return tuple(out)


def hexstr(rgb):
    return "#%02x%02x%02x" % rgb


def grid(fg, bg):
    """The 32x32 mark as a list of rows of (r,g,b).

    Frame inset 3px with a 2px stroke, a 2px cross through the middle, and the
    bottom-right cell filled.
    """
    px = [[bg for _ in range(SIZE)] for _ in range(SIZE)]

    def fill(x0, y0, x1, y1):
        for y in range(y0, y1):
            for x in range(x0, x1):
                px[y][x] = fg

    lo, hi, w = 3, 29, 2          # frame box and stroke width
    mid = SIZE // 2 - 1           # 15, so the cross occupies 15..16

    fill(lo, lo, hi, lo + w)          # frame top
    fill(lo, hi - w, hi, hi)          # frame bottom
    fill(lo, lo, lo + w, hi)          # frame left
    fill(hi - w, lo, hi, hi)          # frame right
    fill(lo, mid, hi, mid + w)        # cross, horizontal
    fill(mid, lo, mid + w, hi)        # cross, vertical
    fill(mid + w, mid + w, hi - w, hi - w)  # filled bottom-right cell

    return px


def write_png(path, px, scale):
    """Minimal RGB8 PNG. Nearest-neighbour at an integer scale, so edges stay hard."""
    raw = bytearray()
    for row in px:
        line = bytearray()
        for rgb in row:
            line += bytes(rgb) * scale
        raw += (b"\x00" + line) * scale

    n = len(px) * scale

    def chunk(kind, data):
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", n, n, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    path.write_bytes(png)
    return n, len(png)


SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" fill="{bg}"/>
  <rect x="4" y="4" width="24" height="24" fill="none" stroke="{fg}" stroke-width="2"/>
  <path d="M3 16h26M16 3v26" stroke="{fg}" stroke-width="2"/>
  <rect x="17" y="17" width="10" height="10" fill="{fg}"/>
</svg>
"""


def selfcheck():
    bg, fg = oklch_to_srgb8(*GROUND_OKLCH), oklch_to_srgb8(*DRAW_OKLCH)
    assert all(0 <= c <= 255 for c in bg + fg), "colour conversion out of gamut"
    assert sum(bg) < sum(fg), "ground should be darker than the draw colour"

    px = grid(fg, bg)
    assert len(px) == SIZE and all(len(r) == SIZE for r in px), "grid is not 32x32"
    assert px[0][0] == bg, "corner should be background"
    assert px[3][3] == fg, "frame should start at 3,3"
    assert px[22][22] == fg, "bottom-right cell should be filled"
    assert px[22][8] == bg, "bottom-left cell should be empty"
    assert px[8][8] == bg, "top-left cell should be empty"
    assert px[16][16] == fg, "cross should cross the centre"

    # PNG round-trip: header, dimensions, and a decodable IDAT
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "t.png"
        n, size = write_png(p, px, 2)
        blob = p.read_bytes()
        assert blob[:8] == b"\x89PNG\r\n\x1a\n", "bad PNG signature"
        w, h = struct.unpack(">II", blob[16:24])
        assert (w, h) == (64, 64) == (n, n), "scale did not apply"
        start = blob.index(b"IDAT") + 4
        end = start + struct.unpack(">I", blob[start - 8 : start - 4])[0]
        assert len(zlib.decompress(blob[start:end])) == 64 * (64 * 3 + 1), "bad IDAT"

    print("selfcheck ok:", hexstr(bg), hexstr(fg))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selfcheck", action="store_true", help="run assertions, write nothing")
    args = ap.parse_args()
    if args.selfcheck:
        return selfcheck()

    bg, fg = oklch_to_srgb8(*GROUND_OKLCH), oklch_to_srgb8(*DRAW_OKLCH)
    px = grid(fg, bg)

    (HERE / "icon.svg").write_text(SVG.format(bg=hexstr(bg), fg=hexstr(fg)))
    print("icon.svg")
    for scale, name in ((1, "icon-32.png"), (6, "icon-192.png")):
        n, size = write_png(HERE / name, px, scale)
        print("%s  %dx%d  %d bytes" % (name, n, n, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
