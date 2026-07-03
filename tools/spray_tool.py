import math
import random

from config.constants import TOOL_SPRAY
from core.geometry import Rect
from commands.drawing_commands import PixelRegionCommand
from tools.base_tool import BaseTool


class SprayTool(BaseTool):
    name = TOOL_SPRAY
    cursor = "spraycan"

    def __init__(self, context):
        super().__init__(context)
        self.layer = None
        self.before_data = None
        self.touched = set()
        self.color = (0, 0, 0, 255)

    def _spray_once(self, x, y):
        radius = self.context.spray_radius
        density = self.context.spray_density
        count = max(1, int((radius * radius) * density))
        for _ in range(count):
            angle = random.uniform(0, 6.283185307179586)
            distance = random.uniform(0, radius)
            px = int(x + distance * math.cos(angle))
            py = int(y + distance * math.sin(angle))
            for mx, my in self.context.mirrored_points(px, py):
                self.layer.buffer.set_pixel(mx, my, self.color)
                self.touched.add((mx, my))

    def on_pointer_down(self, x, y, button):
        layer = self.context.document.active_layer
        if layer.locked:
            return
        self.layer = layer
        self.before_data = layer.buffer.data.copy()
        self.touched = set()
        self.color = self.context.primary_color if button == 1 else self.context.secondary_color
        self._spray_once(x, y)
        self.context.request_redraw()

    def on_pointer_drag(self, x, y):
        if self.layer is None:
            return
        self._spray_once(x, y)
        self.context.request_redraw()

    def on_pointer_up(self, x, y):
        if self.layer is None or not self.touched:
            self.layer = None
            return
        xs = [p[0] for p in self.touched if 0 <= p[0] < self.layer.buffer.width]
        ys = [p[1] for p in self.touched if 0 <= p[1] < self.layer.buffer.height]
        if xs and ys:
            rect = Rect(min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)
            after_region = self.layer.buffer.data[rect.y:rect.y + rect.height, rect.x:rect.x + rect.width].copy()
            before_region = self.before_data[rect.y:rect.y + rect.height, rect.x:rect.x + rect.width].copy()
            command = PixelRegionCommand(self.context.document, self.context.document.active_frame_index, self.layer.id, rect, before_region, after_region)
            self.context.history.push_applied(command)
            self.context.document.notify_pixels_changed(rect)
        self.layer = None

    def cancel(self):
        if self.layer is not None and self.before_data is not None:
            self.layer.buffer.data[:, :] = self.before_data
        self.layer = None
