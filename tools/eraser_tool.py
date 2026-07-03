from config.constants import TOOL_ERASER
from tools.base_tool import BaseTool
from tools.brush_engine import StrokeSession


class EraserTool(BaseTool):
    name = TOOL_ERASER
    cursor = "circle"

    def __init__(self, context):
        super().__init__(context)
        self.session = None

    def on_pointer_down(self, x, y, button):
        layer = self.context.document.active_layer
        if layer.locked:
            return
        self.session = StrokeSession(self.context, layer)
        self.session.line_to(x, y, (0, 0, 0, 0), self.context.brush_size, False)
        self.context.request_redraw()

    def on_pointer_drag(self, x, y):
        if self.session is None:
            return
        self.session.line_to(x, y, (0, 0, 0, 0), self.context.brush_size, False)
        self.context.request_redraw()

    def on_pointer_up(self, x, y):
        if self.session is not None:
            self.session.commit()
            self.session = None

    def cancel(self):
        self.session = None
