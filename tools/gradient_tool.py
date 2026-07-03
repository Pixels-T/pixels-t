import numpy as np

from config.constants import TOOL_GRADIENT
from core.geometry import Rect
from commands.drawing_commands import PixelRegionCommand
from tools.base_tool import BaseTool


class GradientTool(BaseTool):
    name = TOOL_GRADIENT
    cursor = "crosshair"
    uses_preview = True

    def __init__(self, context):
        super().__init__(context)
        self.start = None
        self.color_a = (0, 0, 0, 255)
        self.color_b = (255, 255, 255, 255)

    def on_pointer_down(self, x, y, button):
        if self.context.document.active_layer.locked:
            return
        self.start = (x, y)
        self.color_a = self.context.primary_color
        self.color_b = self.context.secondary_color

    def on_pointer_drag(self, x, y):
        if self.start is None:
            return
        preview = self._compute_gradient(x, y, restrict_to=self.context.document.selection_or_full())
        points = []
        rect = self.context.document.selection_or_full()
        for row in range(preview.shape[0]):
            for col in range(preview.shape[1]):
                pixel = preview[row, col]
                points.append((rect.x + col, rect.y + row, tuple(int(v) for v in pixel)))
        self.context.request_preview(points)

    def _compute_gradient(self, end_x, end_y, restrict_to):
        rect = restrict_to.clamped(self.context.document.width, self.context.document.height)
        start_x, start_y = self.start
        dx = end_x - start_x
        dy = end_y - start_y
        length_sq = max(dx * dx + dy * dy, 1)
        ys, xs = np.mgrid[rect.y:rect.y + rect.height, rect.x:rect.x + rect.width]
        t = ((xs - start_x) * dx + (ys - start_y) * dy) / length_sq
        t = np.clip(t, 0.0, 1.0)
        color_a = np.array(self.color_a, dtype=np.float32)
        color_b = np.array(self.color_b, dtype=np.float32)
        gradient = color_a[None, None, :] * (1 - t[:, :, None]) + color_b[None, None, :] * t[:, :, None]
        return gradient.astype(np.uint8)

    def on_pointer_up(self, x, y):
        if self.start is None:
            return
        document = self.context.document
        layer = document.active_layer
        rect = document.selection_or_full().clamped(document.width, document.height)
        if rect.is_empty():
            self.start = None
            self.context.clear_preview()
            return
        before_data = layer.buffer.data.copy()
        gradient = self._compute_gradient(x, y, restrict_to=rect)
        before_region = before_data[rect.y:rect.y + rect.height, rect.x:rect.x + rect.width]
        alpha = gradient[:, :, 3:4].astype(np.float32) / 255.0
        blended = gradient.astype(np.float32) * alpha + before_region.astype(np.float32) * (1 - alpha)
        layer.buffer.data[rect.y:rect.y + rect.height, rect.x:rect.x + rect.width] = blended.astype(np.uint8)
        after_region = layer.buffer.data[rect.y:rect.y + rect.height, rect.x:rect.x + rect.width].copy()
        command = PixelRegionCommand(document, document.active_frame_index, layer.id, rect, before_region.copy(), after_region)
        self.context.history.push_applied(command)
        document.notify_pixels_changed(rect)
        self.start = None
        self.context.clear_preview()
        self.context.request_redraw()

    def cancel(self):
        self.start = None
        self.context.clear_preview()
