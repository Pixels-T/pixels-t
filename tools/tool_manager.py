from config.constants import (
    TOOL_PENCIL, TOOL_ERASER, TOOL_BUCKET, TOOL_LINE, TOOL_RECTANGLE,
    TOOL_ELLIPSE, TOOL_EYEDROPPER, TOOL_SELECTION, TOOL_MOVE,
    TOOL_GRADIENT, TOOL_SPRAY, TOOL_PAN,
)
from tools.pencil_tool import PencilTool
from tools.eraser_tool import EraserTool
from tools.bucket_tool import BucketTool
from tools.line_tool import LineTool
from tools.rectangle_tool import RectangleTool
from tools.ellipse_tool import EllipseTool
from tools.eyedropper_tool import EyedropperTool
from tools.selection_tool import SelectionTool
from tools.move_tool import MoveTool
from tools.gradient_tool import GradientTool
from tools.spray_tool import SprayTool
from tools.pan_tool import PanTool

TOOL_REGISTRY = {
    TOOL_PENCIL: PencilTool,
    TOOL_ERASER: EraserTool,
    TOOL_BUCKET: BucketTool,
    TOOL_LINE: LineTool,
    TOOL_RECTANGLE: RectangleTool,
    TOOL_ELLIPSE: EllipseTool,
    TOOL_EYEDROPPER: EyedropperTool,
    TOOL_SELECTION: SelectionTool,
    TOOL_MOVE: MoveTool,
    TOOL_GRADIENT: GradientTool,
    TOOL_SPRAY: SprayTool,
    TOOL_PAN: PanTool,
}


class ToolManager:
    def __init__(self, context, event_bus):
        self.context = context
        self.events = event_bus
        self.tools = {name: cls(context) for name, cls in TOOL_REGISTRY.items()}
        self.active_tool_name = TOOL_PENCIL
        self.active_tool = self.tools[self.active_tool_name]

    def set_active_tool(self, name):
        if name not in self.tools:
            return
        if self.active_tool is not None:
            self.active_tool.cancel()
        self.active_tool_name = name
        self.active_tool = self.tools[name]
        from core.events import DocumentEvents
        self.events.emit(DocumentEvents.TOOL_CHANGED, name)

    def get_tool(self, name):
        return self.tools.get(name)
