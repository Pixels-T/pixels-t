from config.constants import TOOL_ELLIPSE
from core.geometry import rasterize_ellipse_filled, rasterize_ellipse_outline
from tools.shape_tool import ShapeTool


class EllipseTool(ShapeTool):
    name = TOOL_ELLIPSE
    cursor = "crosshair"

    def rasterize(self, x0, y0, x1, y1):
        if self.filled:
            return rasterize_ellipse_filled(x0, y0, x1, y1)
        return rasterize_ellipse_outline(x0, y0, x1, y1)
