from config.constants import TOOL_LINE
from core.geometry import bresenham_line, Rect
from commands.drawing_commands import PixelRegionCommand
from tools.base_tool import BaseTool
from tools.brush_engine import brush_stamp_points


class LineTool(BaseTool):
    name = TOOL_LINE
    cursor = "crosshair"
    uses_preview = True

    def __init__(self, context):
        super().__init__(context)
        self.start = None
        self.color = (0, 0, 0, 255)

    def on_pointer_down(self, x, y, button):
        if self.context.document.active_layer.locked:
            return
        self.start = (x, y)
        self.color = self.context.primary_color if button == 1 else self.context.secondary_color
        self._update_preview(x, y)

    def on_pointer_drag(self, x, y):
        if self.start is not None:
            self._update_preview(x, y)

    def _points_for(self, end_x, end_y):
        raw_points = bresenham_line(self.start[0], self.start[1], end_x, end_y)
        points = set()
        for px, py in raw_points:
            for stamp_x, stamp_y in brush_stamp_points(px, py, self.context.brush_size):
                for mx, my in self.context.mirrored_points(stamp_x, stamp_y):
                    points.add((mx, my))
        return points

    def _update_preview(self, x, y):
        points = self._points_for(x, y)
        self.context.request_preview([(px, py, self.color) for px, py in points])

    def on_pointer_up(self, x, y):
        if self.start is None:
            return
        layer = self.context.document.active_layer
        points = self._points_for(x, y)
        if points:
            before_data = layer.buffer.data.copy()
            for px, py in points:
                layer.buffer.set_pixel(px, py, self.color)
            xs = [p[0] for p in points if 0 <= p[0] < layer.buffer.width]
            ys = [p[1] for p in points if 0 <= p[1] < layer.buffer.height]
            if xs and ys:
                rect = Rect(min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)
                after_region = layer.buffer.data[rect.y:rect.y + rect.height, rect.x:rect.x + rect.width].copy()
                before_region = before_data[rect.y:rect.y + rect.height, rect.x:rect.x + rect.width].copy()
                command = PixelRegionCommand(self.context.document, self.context.document.active_frame_index, layer.id, rect, before_region, after_region)
                self.context.history.push_applied(command)
                self.context.document.notify_pixels_changed(rect)
        self.start = None
        self.context.clear_preview()
        self.context.request_redraw()

    def cancel(self):
        self.start = None
        self.context.clear_preview()
