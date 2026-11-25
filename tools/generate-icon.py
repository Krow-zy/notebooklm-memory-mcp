"""Regenerate assets/icon-256.png using only the Python standard library."""

from __future__ import annotations

import math
import struct
import zlib
from pathlib import Path

SIZE = 256
OUTPUT = Path(__file__).resolve().parents[1] / "assets" / "icon-256.png"
DARK = (17, 20, 26)
TEAL = (0, 214, 178)
WHITE = (240, 248, 247)


def smoothstep(low: float, high: float, value: float) -> float:
    t = min(1.0, max(0.0, (value - low) / (high - low)))
    return t * t * (3.0 - 2.0 * t)


def segment_distance(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    dx, dy = bx - ax, by - ay
    t = min(1.0, max(0.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def sample(x: float, y: float) -> tuple[int, int, int, int]:
    d = math.hypot(x, y)
    circle = 1.0 - smoothstep(117.0, 119.0, d)
    ring = smoothstep(101.0, 103.0, d) * (1.0 - smoothstep(113.0, 115.0, d))

    strokes = (
        (-42.0, -58.0, -42.0, 58.0),
        (-42.0, -58.0, 42.0, 58.0),
        (42.0, -58.0, 42.0, 58.0),
    )
    nearest = min(segment_distance(x, y, *stroke) for stroke in strokes)
    ink = (1.0 - smoothstep(5.5, 7.5, nearest)) * circle

    base = tuple(DARK[i] * (1.0 - ring) + TEAL[i] * ring for i in range(3))
    rgb = tuple(base[i] * (1.0 - ink) + WHITE[i] * ink for i in range(3))
    return (*(round(channel) for channel in rgb), round(circle * 255))


def chunk(kind: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def main() -> None:
    raw = bytearray()
    for y in range(SIZE):
        raw.append(0)
        for x in range(SIZE):
            raw.extend(sample(x - SIZE / 2 + 0.5, y - SIZE / 2 + 0.5))
    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 6, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_bytes(png)
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    assert len(png) > 1000
    print(f"wrote {OUTPUT} ({len(png)} bytes)")


if __name__ == "__main__":
    main()
