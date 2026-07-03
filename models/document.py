from core.events import EventBus, DocumentEvents
from core.geometry import Rect
from models.frame import Frame
from models.palette import Palette


class Document:
    def __init__(self, width, height, name="Untitled", event_bus=None):
        self.width = width
        self.height = height
        self.name = name
        self.filepath = None
        self.frames = [Frame(width, height)]
        self.active_frame_index = 0
        self.active_layer_id = self.frames[0].layers[0].id
        self.palette = Palette()
        self.selection = None
        self.dirty = False
        self.events = event_bus if event_bus is not None else EventBus()
        self.onion_skin_enabled = False
        self.onion_skin_before = 1
        self.onion_skin_after = 1

    @property
    def active_frame(self):
        return self.frames[self.active_frame_index]

    @property
    def active_layer(self):
        frame = self.active_frame
        index = frame.find_layer_index(self.active_layer_id)
        if index == -1 and frame.layers:
            self.active_layer_id = frame.layers[0].id
            return frame.layers[0]
        return frame.layers[index]

    def mark_dirty(self):
        if not self.dirty:
            self.dirty = True
            self.events.emit(DocumentEvents.DIRTY_STATE_CHANGED, True)

    def mark_clean(self):
        if self.dirty:
            self.dirty = False
            self.events.emit(DocumentEvents.DIRTY_STATE_CHANGED, False)

    def set_active_layer(self, layer_id):
        self.active_layer_id = layer_id
        self.events.emit(DocumentEvents.ACTIVE_LAYER_CHANGED, layer_id)

    def set_active_frame(self, index):
        if 0 <= index < len(self.frames):
            self.active_frame_index = index
            if self.active_frame.layers:
                self.active_layer_id = self.active_frame.layers[0].id
            self.events.emit(DocumentEvents.ACTIVE_FRAME_CHANGED, index)

    def notify_pixels_changed(self, rect=None):
        self.mark_dirty()
        self.events.emit(DocumentEvents.PIXELS_CHANGED, rect)

    def set_selection(self, rect):
        self.selection = rect
        self.events.emit(DocumentEvents.SELECTION_CHANGED, rect)

    def clear_selection(self):
        self.set_selection(None)

    def selection_or_full(self):
        if self.selection is not None and not self.selection.is_empty():
            return self.selection.clamped(self.width, self.height)
        return Rect(0, 0, self.width, self.height)

    def resize_canvas(self, new_width, new_height, anchor_x=0, anchor_y=0):
        for frame in self.frames:
            frame.resize(new_width, new_height, anchor_x, anchor_y)
        self.width = new_width
        self.height = new_height
        self.events.emit(DocumentEvents.CANVAS_RESIZED, new_width, new_height)
        self.notify_pixels_changed()

    def duplicate_frame(self, index):
        clone = self.frames[index].clone()
        self.frames.insert(index + 1, clone)
        self.events.emit(DocumentEvents.FRAME_ADDED, index + 1)
        self.mark_dirty()
        return clone

    def add_frame(self, index=None, copy_active=False):
        if copy_active:
            frame = self.active_frame.clone()
        else:
            frame = Frame(self.width, self.height)
        insert_at = index if index is not None else len(self.frames)
        self.frames.insert(insert_at, frame)
        self.events.emit(DocumentEvents.FRAME_ADDED, insert_at)
        self.mark_dirty()
        return frame

    def remove_frame(self, index):
        if len(self.frames) <= 1:
            return
        del self.frames[index]
        if self.active_frame_index >= len(self.frames):
            self.active_frame_index = len(self.frames) - 1
        self.events.emit(DocumentEvents.FRAME_REMOVED, index)
        self.mark_dirty()

    def reorder_frame(self, from_index, to_index):
        frame = self.frames.pop(from_index)
        self.frames.insert(to_index, frame)
        self.active_frame_index = to_index
        self.events.emit(DocumentEvents.FRAMES_REORDERED)
        self.mark_dirty()

    def total_layer_count_for_frame(self, index):
        return len(self.frames[index].layers)
