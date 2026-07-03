from config.constants import TOOL_SELECTION
from core.geometry import Rect
from tools.base_tool import BaseTool


class SelectionTool(BaseTool):
    name = TOOL_SELECTION
    cursor = "crosshair"
    uses_preview = True

    def __init__(self, context):
        super().__init__(context)
        self.start = None

    def on_pointer_down(self, x, y, button):
        self.start = (x, y)
        self.context.document.set_selection(Rect(x, y, 1, 1))

    def on_pointer_drag(self, x, y):
        if self.start is None:
            return
        sx, sy = self.start
        rect = Rect(sx, sy, x - sx + (1 if x >= sx else -1), y - sy + (1 if y >= sy else -1))
        self.context.document.set_selection(rect.normalized())

    def on_pointer_up(self, x, y):
        self.start = None

    def cancel(self):
        self.start = None
        self.context.document.clear_selection()
