from config.constants import TOOL_EYEDROPPER
from tools.base_tool import BaseTool


class EyedropperTool(BaseTool):
    name = TOOL_EYEDROPPER
    cursor = "target"

    def __init__(self, context):
        super().__init__(context)
        self.on_color_picked = None

    def on_pointer_down(self, x, y, button):
        composite = self.context.document.active_frame.composite()
        color = composite.get_pixel(x, y)
        if button == 1:
            self.context.primary_color = color
        else:
            self.context.secondary_color = color
        if self.on_color_picked is not None:
            self.on_color_picked(color, button)

    def on_pointer_drag(self, x, y):
        self.on_pointer_down(x, y, 1)
