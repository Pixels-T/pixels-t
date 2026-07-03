from config.constants import TOOL_RECTANGLE
from core.geometry import rasterize_rectangle_filled, rasterize_rectangle_outline
from tools.shape_tool import ShapeTool


class RectangleTool(ShapeTool):
    name = TOOL_RECTANGLE
    cursor = "crosshair"

    def rasterize(self, x0, y0, x1, y1):
        if self.filled:
            return rasterize_rectangle_filled(x0, y0, x1, y1)
        return rasterize_rectangle_outline(x0, y0, x1, y1)
