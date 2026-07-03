from config.constants import TOOL_PENCIL
from tools.base_tool import BaseTool
from tools.brush_engine import StrokeSession


class PencilTool(BaseTool):
    name = TOOL_PENCIL
    cursor = "tcross"

    def __init__(self, context):
        super().__init__(context)
        self.session = None
        self.active_color = (0, 0, 0, 255)

    def on_pointer_down(self, x, y, button):
        layer = self.context.document.active_layer
        if layer.locked:
            return
        self.active_color = self.context.primary_color if button == 1 else self.context.secondary_color
        self.session = StrokeSession(self.context, layer)
        self.session.line_to(x, y, self.active_color, self.context.brush_size, self.context.pixel_perfect)
        self.context.request_redraw()

    def on_pointer_drag(self, x, y):
        if self.session is None:
            return
        self.session.line_to(x, y, self.active_color, self.context.brush_size, self.context.pixel_perfect)
        self.context.request_redraw()

    def on_pointer_up(self, x, y):
        if self.session is not None:
            self.session.commit()
            self.session = None

    def cancel(self):
        self.session = None
