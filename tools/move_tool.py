from config.constants import TOOL_MOVE
from commands.drawing_commands import FullBufferCommand
from tools.base_tool import BaseTool


class MoveTool(BaseTool):
    name = TOOL_MOVE
    cursor = "fleur"

    def __init__(self, context):
        super().__init__(context)
        self.layer = None
        self.before_data = None
        self.cut_buffer = None
        self.origin_rect = None
        self.drag_start = None
        self.current_offset = (0, 0)

    def on_pointer_down(self, x, y, button):
        document = self.context.document
        layer = document.active_layer
        if layer.locked:
            return
        self.layer = layer
        self.before_data = layer.buffer.data.copy()
        self.origin_rect = document.selection_or_full()
        self.cut_buffer = layer.buffer.extract_region(self.origin_rect)
        layer.buffer.clear_region(self.origin_rect)
        layer.buffer.paste(self.cut_buffer, self.origin_rect.x, self.origin_rect.y)
        self.drag_start = (x, y)
        self.current_offset = (0, 0)

    def on_pointer_drag(self, x, y):
        if self.drag_start is None:
            return
        dx = x - self.drag_start[0]
        dy = y - self.drag_start[1]
        self.current_offset = (dx, dy)
        self.layer.buffer.data[:, :] = self.before_data
        self.layer.buffer.clear_region(self.origin_rect)
        self.layer.buffer.paste(self.cut_buffer, self.origin_rect.x + dx, self.origin_rect.y + dy)
        self.context.document.notify_pixels_changed()
        self.context.request_redraw()

    def on_pointer_up(self, x, y):
        if self.layer is None:
            return
        after_data = self.layer.buffer.data.copy()
        command = FullBufferCommand(self.context.document, self.context.document.active_frame_index, self.layer.id, self.before_data, after_data)
        self.context.history.push_applied(command)
        dx, dy = self.current_offset
        if self.context.document.selection is not None:
            moved_rect = self.origin_rect
            from core.geometry import Rect
            self.context.document.set_selection(Rect(moved_rect.x + dx, moved_rect.y + dy, moved_rect.width, moved_rect.height))
        self.layer = None
        self.drag_start = None

    def cancel(self):
        if self.layer is not None and self.before_data is not None:
            self.layer.buffer.data[:, :] = self.before_data
            self.context.document.notify_pixels_changed()
        self.layer = None
        self.drag_start = None
