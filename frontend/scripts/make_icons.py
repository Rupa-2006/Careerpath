"""
Draws the CareerPath app icons (the same design as public/favicon.svg) as PNG files, with no extra libraries.
Run from the frontend folder:  ..\\backend\\venv\\Scripts\\python scripts\\make_icons.py
"""
import struct
import zlib
from pathlib import Path

PINE, GOLD, WHITE = (15, 61, 62), (244, 183, 64), (255, 255, 255)
SCALE = 4  # draw 4 times bigger, then shrink, for smooth edges


def cubic(p0, p1, p2, p3, steps=120):
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        yield tuple(u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d for a, b, c, d in zip(p0, p1, p2, p3))


# The favicon's shapes, on its 48 by 48 grid
GOLD_LINE = [*cubic((12, 36), (20, 36), (20, 24), (24, 24)), *cubic((24, 24), (28, 24), (28, 12), (36, 12))]
WHITE_LINE = list(cubic((24, 24), (28, 24), (28, 36), (36, 36)))


def draw(size: int, maskable: bool) -> bytes:
    big = size * SCALE
    grid = [[None] * big for _ in range(big)]
    # A maskable icon is cropped by the phone, so its picture sits inside the middle 80%
    shrink = 0.8 if maskable else 1.0
    offset = big * (1 - shrink) / 2
    unit = big * shrink / 48

    def to_px(x, y):
        return offset + x * unit, offset + y * unit

    radius = 0 if maskable else 12 * big / 48
    for y in range(big):
        for x in range(big):
            dx = max(radius - x, 0, x - (big - 1 - radius))
            dy = max(radius - y, 0, y - (big - 1 - radius))
            if dx * dx + dy * dy <= radius * radius or radius == 0:
                grid[y][x] = PINE

    def disc(cx, cy, r, colour):
        for y in range(max(0, int(cy - r)), min(big, int(cy + r) + 2)):
            for x in range(max(0, int(cx - r)), min(big, int(cx + r) + 2)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    grid[y][x] = colour

    for line, colour in ((GOLD_LINE, GOLD), (WHITE_LINE, WHITE)):
        for x, y in line:
            disc(*to_px(x, y), 2 * unit, colour)
    disc(*to_px(12, 36), 4 * unit, WHITE)

    rows = []
    for y in range(size):
        row = bytearray([0])
        for x in range(size):
            r = g = b = a = 0
            for sy in range(SCALE):
                for sx in range(SCALE):
                    pixel = grid[y * SCALE + sy][x * SCALE + sx]
                    if pixel:
                        r, g, b, a = r + pixel[0], g + pixel[1], b + pixel[2], a + 1
            count = SCALE * SCALE
            row += bytes((r // a, g // a, b // a, 255 * a // count)) if a else bytes(4)
        rows.append(bytes(row))
    return png(size, b"".join(rows))


def png(size: int, raw: bytes) -> bytes:
    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "public"
    for name, size, maskable in (("icon-192.png", 192, False), ("icon-512.png", 512, False),
                                 ("icon-maskable-512.png", 512, True), ("apple-touch-icon.png", 180, True)):
        (out / name).write_bytes(draw(size, maskable))
        print("made", name)
