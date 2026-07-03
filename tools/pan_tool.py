from config.constants import TOOL_PAN
from tools.base_tool import BaseTool


class PanTool(BaseTool):
    name = TOOL_PAN
    cursor = "fleur"

    def __init__(self, context):
        super().__init__(context)
        self.on_pan = None

    def on_pointer_down(self, x, y, button):
        pass

    def on_pointer_drag(self, x, y):
        pass
