from config.constants import TOOL_BUCKET
from core.geometry import Rect
from commands.drawing_commands import PixelRegionCommand
from tools.base_tool import BaseTool


class BucketTool(BaseTool):
    name = TOOL_BUCKET
    cursor = "spraycan"

    def on_pointer_down(self, x, y, button):
        document = self.context.document
        layer = document.active_layer
        if layer.locked:
            return
        color = self.context.primary_color if button == 1 else self.context.secondary_color
        before_data = layer.buffer.data.copy()
        targets = self.context.mirrored_points(x, y)
        affected = Rect(0, 0, 0, 0)
        for tx, ty in targets:
            region = layer.buffer.flood_fill(tx, ty, color, self.context.fill_tolerance)
            if not region.is_empty():
                affected = affected.union(region)
        if affected.is_empty():
            return
        after_region = layer.buffer.data[affected.y:affected.y + affected.height, affected.x:affected.x + affected.width].copy()
        before_region = before_data[affected.y:affected.y + affected.height, affected.x:affected.x + affected.width].copy()
        command = PixelRegionCommand(document, document.active_frame_index, layer.id, affected, before_region, after_region)
        self.context.history.push_applied(command)
        document.notify_pixels_changed(affected)
        self.context.request_redraw()

    def on_pointer_up(self, x, y):
        pass
