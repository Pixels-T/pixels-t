from core.geometry import Rect
from commands.drawing_commands import PixelRegionCommand


def brush_stamp_points(cx, cy, size):
    points = []
    half = size // 2
    start = -half
    end = size - half
    for dx in range(start, end):
        for dy in range(start, end):
            points.append((cx + dx, cy + dy))
    return points


class StrokeSession:
    def __init__(self, context, layer):
        self.context = context
        self.layer = layer
        self.document = context.document
        self.before_data = layer.buffer.data.copy()
        self.touched = set()
        self.last_point = None
        self.pixel_perfect_history = []

    def paint_point(self, x, y, rgba, size=1):
        points = brush_stamp_points(x, y, size)
        for px, py in points:
            for mx, my in self.context.mirrored_points(px, py):
                self.layer.buffer.set_pixel(mx, my, rgba)
                self.touched.add((mx, my))

    def paint_pixel_perfect(self, x, y, rgba, size):
        if size == 1 and self.context.pixel_perfect:
            self.pixel_perfect_history.append((x, y))
            if len(self.pixel_perfect_history) >= 3:
                a, b, c = self.pixel_perfect_history[-3:]
                if abs(a[0] - c[0]) == 1 and abs(a[1] - c[1]) == 1 and b[0] in (a[0], c[0]) and b[1] in (a[1], c[1]):
                    for mx, my in self.context.mirrored_points(*b):
                        self.layer.buffer.set_pixel(mx, my, self._original_pixel(mx, my))
                    self.touched.discard(b)
        self.paint_point(x, y, rgba, size)

    def _original_pixel(self, x, y):
        if 0 <= x < self.before_data.shape[1] and 0 <= y < self.before_data.shape[0]:
            pixel = self.before_data[y, x]
            return (int(pixel[0]), int(pixel[1]), int(pixel[2]), int(pixel[3]))
        return (0, 0, 0, 0)

    def line_to(self, x, y, rgba, size, pixel_perfect_enabled):
        from core.geometry import bresenham_line
        if self.last_point is None:
            if pixel_perfect_enabled:
                self.paint_pixel_perfect(x, y, rgba, size)
            else:
                self.paint_point(x, y, rgba, size)
        else:
            lx, ly = self.last_point
            for px, py in bresenham_line(lx, ly, x, y):
                if pixel_perfect_enabled:
                    self.paint_pixel_perfect(px, py, rgba, size)
                else:
                    self.paint_point(px, py, rgba, size)
        self.last_point = (x, y)

    def commit(self):
        if not self.touched:
            return None
        xs = [p[0] for p in self.touched if 0 <= p[0] < self.layer.buffer.width and 0 <= p[1] < self.layer.buffer.height]
        ys = [p[1] for p in self.touched if 0 <= p[0] < self.layer.buffer.width and 0 <= p[1] < self.layer.buffer.height]
        if not xs:
            return None
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        rect = Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)
        after_region = self.layer.buffer.data[rect.y:rect.y + rect.height, rect.x:rect.x + rect.width].copy()
        before_region = self.before_data[rect.y:rect.y + rect.height, rect.x:rect.x + rect.width].copy()
        command = PixelRegionCommand(self.document, self.document.active_frame_index, self.layer.id, rect, before_region, after_region)
        self.context.history.push_applied(command)
        self.document.notify_pixels_changed(rect)
        return command
