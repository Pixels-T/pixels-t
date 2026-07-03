from config.constants import DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT, DEFAULT_ZOOM
from config.settings import Settings
from core.color import Color
from core.events import EventBus, DocumentEvents
from core.geometry import Rect
from commands.history import HistoryManager
from commands.drawing_commands import FullBufferCommand
from commands.layer_commands import AddLayerCommand, RemoveLayerCommand, ReorderLayerCommand, LayerPropertyCommand
from commands.frame_commands import AddFrameCommand, RemoveFrameCommand, ReorderFrameCommand, FrameDurationCommand
from models.document import Document
from models.layer import Layer
from services.clipboard_service import ClipboardService
from services.autosave_service import AutosaveService
from services import project_service
from tools.tool_context import ToolContext
from tools.tool_manager import ToolManager


class Application:
    def __init__(self):
        self.events = EventBus()
        self.settings = Settings()
        self.document = Document(DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT, event_bus=self.events)
        self.history = HistoryManager(self.events)
        self.clipboard = ClipboardService()
        self.autosave = AutosaveService(self.settings)
        self.zoom = self.settings.get("last_zoom", DEFAULT_ZOOM)
        self.tool_context = ToolContext(self.document, self.history)
        self.tool_context.pixel_perfect = self.settings.get("pixel_perfect", True)
        self.tool_context.symmetry_horizontal = self.settings.get("symmetry_horizontal", False)
        self.tool_context.symmetry_vertical = self.settings.get("symmetry_vertical", False)
        self.tool_manager = ToolManager(self.tool_context, self.events)
        self.playback_active = False

    def new_document(self, width, height, name="Untitled"):
        self.document = Document(width, height, name=name, event_bus=self.events)
        self.tool_context.document = self.document
        self.history.clear()
        self.events.emit(DocumentEvents.DOCUMENT_LOADED)

    def open_document(self, path):
        document = project_service.load_project(path, event_bus=self.events)
        self.document = document
        self.tool_context.document = document
        self.history.clear()
        self.settings.add_recent_project(path)
        self.settings.save()
        self.events.emit(DocumentEvents.DOCUMENT_LOADED)

    def save_document(self, path):
        project_service.save_project(self.document, path)
        self.settings.add_recent_project(path)
        self.settings.save()

    def undo(self):
        self.history.undo()

    def redo(self):
        self.history.redo()

    def set_zoom(self, zoom):
        from config.constants import MIN_ZOOM, MAX_ZOOM
        self.zoom = max(MIN_ZOOM, min(MAX_ZOOM, zoom))
        self.settings.set("last_zoom", self.zoom)
        self.events.emit(DocumentEvents.ZOOM_CHANGED, self.zoom)

    def set_primary_color(self, color):
        self.tool_context.primary_color = color.as_tuple() if isinstance(color, Color) else color
        self.settings.add_recent_color(Color(*self.tool_context.primary_color).to_hex())
        self.events.emit(DocumentEvents.COLOR_CHANGED)

    def set_secondary_color(self, color):
        self.tool_context.secondary_color = color.as_tuple() if isinstance(color, Color) else color
        self.events.emit(DocumentEvents.COLOR_CHANGED)

    def add_layer(self):
        frame = self.document.active_frame
        layer = Layer(self.document.width, self.document.height, name=f"Layer {len(frame.layers) + 1}")
        index = len(frame.layers)
        command = AddLayerCommand(self.document, self.document.active_frame_index, layer, index)
        self.history.execute(command)
        return layer

    def remove_layer(self, layer_id):
        frame = self.document.active_frame
        if len(frame.layers) <= 1:
            return
        index = frame.find_layer_index(layer_id)
        if index == -1:
            return
        layer = frame.layers[index]
        command = RemoveLayerCommand(self.document, self.document.active_frame_index, layer, index)
        self.history.execute(command)

    def duplicate_layer(self, layer_id):
        frame = self.document.active_frame
        index = frame.find_layer_index(layer_id)
        if index == -1:
            return
        source = frame.layers[index]
        clone = source.clone()
        clone.name = f"{source.name} copy"
        command = AddLayerCommand(self.document, self.document.active_frame_index, clone, index + 1)
        self.history.execute(command)

    def reorder_layer(self, from_index, to_index):
        command = ReorderLayerCommand(self.document, self.document.active_frame_index, from_index, to_index)
        self.history.execute(command)

    def set_layer_property(self, layer_id, property_name, value):
        frame = self.document.active_frame
        index = frame.find_layer_index(layer_id)
        if index == -1:
            return
        before_value = getattr(frame.layers[index], property_name)
        if before_value == value:
            return
        command = LayerPropertyCommand(self.document, self.document.active_frame_index, layer_id, property_name, before_value, value)
        self.history.execute(command)

    def merge_layer_down(self, layer_id):
        frame = self.document.active_frame
        index = frame.find_layer_index(layer_id)
        if index <= 0:
            return
        top_layer = frame.layers[index]
        bottom_layer = frame.layers[index - 1]
        before_data = bottom_layer.buffer.data.copy()
        merged = bottom_layer.buffer.clone()
        merged.paste(top_layer.buffer, 0, 0)
        bottom_layer.buffer.data[:, :] = merged.data
        command = FullBufferCommand(self.document, self.document.active_frame_index, bottom_layer.id, before_data, merged.data.copy())
        remove_command = RemoveLayerCommand(self.document, self.document.active_frame_index, top_layer, index)
        remove_command.execute()
        self.history.push_applied(command)

    def add_frame(self, copy_active=False):
        if copy_active:
            frame = self.document.active_frame.clone()
        else:
            from models.frame import Frame
            frame = Frame(self.document.width, self.document.height)
        index = self.document.active_frame_index + 1
        command = AddFrameCommand(self.document, index, frame)
        self.history.execute(command)

    def remove_frame(self, index):
        if len(self.document.frames) <= 1:
            return
        frame = self.document.frames[index]
        command = RemoveFrameCommand(self.document, index, frame)
        self.history.execute(command)

    def reorder_frame(self, from_index, to_index):
        command = ReorderFrameCommand(self.document, from_index, to_index)
        self.history.execute(command)

    def set_frame_duration(self, frame_index, duration_ms):
        before_value = self.document.frames[frame_index].duration_ms
        command = FrameDurationCommand(self.document, frame_index, before_value, duration_ms)
        self.history.execute(command)

    def flip_layer_horizontal(self, layer_id):
        self._transform_layer(layer_id, lambda buffer: buffer.flipped_horizontal())

    def flip_layer_vertical(self, layer_id):
        self._transform_layer(layer_id, lambda buffer: buffer.flipped_vertical())

    def rotate_layer(self, layer_id, clockwise=True):
        self._transform_layer(layer_id, lambda buffer: buffer.rotated_90(clockwise))

    def _transform_layer(self, layer_id, transform_fn):
        frame = self.document.active_frame
        index = frame.find_layer_index(layer_id)
        if index == -1:
            return
        layer = frame.layers[index]
        before_data = layer.buffer.data.copy()
        transformed = transform_fn(layer.buffer)
        if transformed.width != layer.buffer.width or transformed.height != layer.buffer.height:
            return
        layer.buffer.data[:, :] = transformed.data
        command = FullBufferCommand(self.document, self.document.active_frame_index, layer.id, before_data, transformed.data.copy())
        self.history.push_applied(command)

    def copy_selection(self):
        rect = self.document.selection_or_full()
        layer = self.document.active_layer
        extracted = layer.buffer.extract_region(rect)
        self.clipboard.copy(extracted)

    def cut_selection(self):
        rect = self.document.selection_or_full()
        layer = self.document.active_layer
        if layer.locked:
            return
        before_data = layer.buffer.data.copy()
        extracted = layer.buffer.extract_region(rect)
        self.clipboard.copy(extracted)
        layer.buffer.clear_region(rect)
        command = FullBufferCommand(self.document, self.document.active_frame_index, layer.id, before_data, layer.buffer.data.copy())
        self.history.push_applied(command)
        self.document.notify_pixels_changed(rect)

    def paste_clipboard(self):
        content = self.clipboard.get()
        if content is None:
            return
        layer = self.document.active_layer
        if layer.locked:
            return
        before_data = layer.buffer.data.copy()
        paste_x = max(0, (self.document.width - content.width) // 2)
        paste_y = max(0, (self.document.height - content.height) // 2)
        layer.buffer.paste(content, paste_x, paste_y)
        command = FullBufferCommand(self.document, self.document.active_frame_index, layer.id, before_data, layer.buffer.data.copy())
        self.history.push_applied(command)
        self.document.set_selection(Rect(paste_x, paste_y, content.width, content.height))
        self.document.notify_pixels_changed()

    def delete_selection_content(self):
        rect = self.document.selection_or_full()
        layer = self.document.active_layer
        if layer.locked:
            return
        before_data = layer.buffer.data.copy()
        layer.buffer.clear_region(rect)
        command = FullBufferCommand(self.document, self.document.active_frame_index, layer.id, before_data, layer.buffer.data.copy())
        self.history.push_applied(command)
        self.document.notify_pixels_changed(rect)

    def resize_canvas(self, new_width, new_height, anchor_x=0, anchor_y=0):
        before_frames = [frame.clone() for frame in self.document.frames]
        before_size = (self.document.width, self.document.height)
        self.document.resize_canvas(new_width, new_height, anchor_x, anchor_y)
        after_frames = [frame.clone() for frame in self.document.frames]
        after_size = (new_width, new_height)
        from commands.drawing_commands import CanvasResizeCommand
        command = CanvasResizeCommand(self.document, before_frames, after_frames, before_size, after_size)
        self.history.push_applied(command)

    def replace_color(self, old_rgba, new_rgba, tolerance=0):
        import numpy as np
        layer = self.document.active_layer
        if layer.locked:
            return
        before_data = layer.buffer.data.copy()
        target = np.array(old_rgba, dtype=np.int32)
        diff = np.abs(layer.buffer.data.astype(np.int32) - target.reshape(1, 1, 4)).sum(axis=2)
        mask = diff <= tolerance
        layer.buffer.data[mask] = new_rgba
        command = FullBufferCommand(self.document, self.document.active_frame_index, layer.id, before_data, layer.buffer.data.copy())
        self.history.push_applied(command)
        self.document.notify_pixels_changed()

    def shutdown(self):
        self.settings.set("pixel_perfect", self.tool_context.pixel_perfect)
        self.settings.set("symmetry_horizontal", self.tool_context.symmetry_horizontal)
        self.settings.set("symmetry_vertical", self.tool_context.symmetry_vertical)
        self.settings.save()
