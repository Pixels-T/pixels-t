import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: int
    y: int


@dataclass
class Rect:
    x: int
    y: int
    width: int
    height: int

    def normalized(self):
        x = min(self.x, self.x + self.width)
        y = min(self.y, self.y + self.height)
        w = abs(self.width)
        h = abs(self.height)
        return Rect(x, y, w, h)

    def clamped(self, max_width, max_height):
        normalized = self.normalized()
        x0 = max(0, normalized.x)
        y0 = max(0, normalized.y)
        x1 = min(max_width, normalized.x + normalized.width)
        y1 = min(max_height, normalized.y + normalized.height)
        return Rect(x0, y0, max(0, x1 - x0), max(0, y1 - y0))

    def contains(self, x, y):
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height

    def is_empty(self):
        return self.width <= 0 or self.height <= 0

    def union(self, other):
        if self.is_empty():
            return Rect(other.x, other.y, other.width, other.height)
        if other.is_empty():
            return Rect(self.x, self.y, self.width, self.height)
        x0 = min(self.x, other.x)
        y0 = min(self.y, other.y)
        x1 = max(self.x + self.width, other.x + other.width)
        y1 = max(self.y + self.height, other.y + other.height)
        return Rect(x0, y0, x1 - x0, y1 - y0)


def bresenham_line(x0, y0, x1, y1):
    points = []
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    error = dx + dy
    x, y = x0, y0
    while True:
        points.append((x, y))
        if x == x1 and y == y1:
            break
        doubled_error = 2 * error
        if doubled_error >= dy:
            if x == x1:
                break
            error += dy
            x += sx
        if doubled_error <= dx:
            if y == y1:
                break
            error += dx
            y += sy
    return points


def rasterize_rectangle_outline(x0, y0, x1, y1):
    left, right = min(x0, x1), max(x0, x1)
    top, bottom = min(y0, y1), max(y0, y1)
    points = set()
    for x in range(left, right + 1):
        points.add((x, top))
        points.add((x, bottom))
    for y in range(top, bottom + 1):
        points.add((left, y))
        points.add((right, y))
    return points


def rasterize_rectangle_filled(x0, y0, x1, y1):
    left, right = min(x0, x1), max(x0, x1)
    top, bottom = min(y0, y1), max(y0, y1)
    points = set()
    for x in range(left, right + 1):
        for y in range(top, bottom + 1):
            points.add((x, y))
    return points


def rasterize_ellipse_outline(x0, y0, x1, y1):
    left, right = min(x0, x1), max(x0, x1)
    top, bottom = min(y0, y1), max(y0, y1)
    cx = (left + right) / 2.0
    cy = (top + bottom) / 2.0
    rx = (right - left) / 2.0
    ry = (bottom - top) / 2.0
    points = set()
    if rx < 0.5 or ry < 0.5:
        for x in range(left, right + 1):
            for y in range(top, bottom + 1):
                points.add((x, y))
        return points
    steps = max(360, int(4 * (rx + ry)))
    for i in range(steps):
        theta = (2 * 3.141592653589793 * i) / steps
        x = round(cx + rx * math.cos(theta))
        y = round(cy + ry * math.sin(theta))
        points.add((x, y))
    return points


def rasterize_ellipse_filled(x0, y0, x1, y1):
    left, right = min(x0, x1), max(x0, x1)
    top, bottom = min(y0, y1), max(y0, y1)
    cx = (left + right) / 2.0
    cy = (top + bottom) / 2.0
    rx = max((right - left) / 2.0, 0.5)
    ry = max((bottom - top) / 2.0, 0.5)
    points = set()
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            nx = (x - cx) / rx
            ny = (y - cy) / ry
            if nx * nx + ny * ny <= 1.0:
                points.add((x, y))
    return points
