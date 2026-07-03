from collections import defaultdict


class EventBus:
    def __init__(self):
        self._listeners = defaultdict(list)

    def subscribe(self, event_name, callback):
        self._listeners[event_name].append(callback)
        return callback

    def unsubscribe(self, event_name, callback):
        if callback in self._listeners[event_name]:
            self._listeners[event_name].remove(callback)

    def emit(self, event_name, *args, **kwargs):
        for callback in list(self._listeners[event_name]):
            callback(*args, **kwargs)


class DocumentEvents:
    PIXELS_CHANGED = "pixels_changed"
    LAYER_ADDED = "layer_added"
    LAYER_REMOVED = "layer_removed"
    LAYER_CHANGED = "layer_changed"
    LAYERS_REORDERED = "layers_reordered"
    ACTIVE_LAYER_CHANGED = "active_layer_changed"
    FRAME_ADDED = "frame_added"
    FRAME_REMOVED = "frame_removed"
    FRAMES_REORDERED = "frames_reordered"
    ACTIVE_FRAME_CHANGED = "active_frame_changed"
    FRAME_DURATION_CHANGED = "frame_duration_changed"
    SELECTION_CHANGED = "selection_changed"
    CANVAS_RESIZED = "canvas_resized"
    DOCUMENT_LOADED = "document_loaded"
    HISTORY_CHANGED = "history_changed"
    COLOR_CHANGED = "color_changed"
    TOOL_CHANGED = "tool_changed"
    ZOOM_CHANGED = "zoom_changed"
    DIRTY_STATE_CHANGED = "dirty_state_changed"
