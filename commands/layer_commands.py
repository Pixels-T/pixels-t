from commands.command import Command
from core.events import DocumentEvents


class AddLayerCommand(Command):
    label = "Add Layer"

    def __init__(self, document, frame_index, layer, index):
        self.document = document
        self.frame_index = frame_index
        self.layer = layer
        self.index = index

    def execute(self):
        frame = self.document.frames[self.frame_index]
        frame.layers.insert(self.index, self.layer)
        self.document.active_layer_id = self.layer.id
        self.document.events.emit(DocumentEvents.LAYER_ADDED, self.layer.id)
        self.document.notify_pixels_changed()

    def undo(self):
        frame = self.document.frames[self.frame_index]
        frame.remove_layer(self.layer.id)
        if frame.layers:
            self.document.active_layer_id = frame.layers[0].id
        self.document.events.emit(DocumentEvents.LAYER_REMOVED, self.layer.id)
        self.document.notify_pixels_changed()


class RemoveLayerCommand(Command):
    label = "Remove Layer"

    def __init__(self, document, frame_index, layer, index):
        self.document = document
        self.frame_index = frame_index
        self.layer = layer
        self.index = index

    def execute(self):
        frame = self.document.frames[self.frame_index]
        frame.remove_layer(self.layer.id)
        if frame.layers:
            self.document.active_layer_id = frame.layers[0].id
        self.document.events.emit(DocumentEvents.LAYER_REMOVED, self.layer.id)
        self.document.notify_pixels_changed()

    def undo(self):
        frame = self.document.frames[self.frame_index]
        frame.layers.insert(self.index, self.layer)
        self.document.active_layer_id = self.layer.id
        self.document.events.emit(DocumentEvents.LAYER_ADDED, self.layer.id)
        self.document.notify_pixels_changed()


class ReorderLayerCommand(Command):
    label = "Reorder Layers"

    def __init__(self, document, frame_index, from_index, to_index):
        self.document = document
        self.frame_index = frame_index
        self.from_index = from_index
        self.to_index = to_index

    def execute(self):
        frame = self.document.frames[self.frame_index]
        layer = frame.layers.pop(self.from_index)
        frame.layers.insert(self.to_index, layer)
        self.document.events.emit(DocumentEvents.LAYERS_REORDERED)
        self.document.notify_pixels_changed()

    def undo(self):
        frame = self.document.frames[self.frame_index]
        layer = frame.layers.pop(self.to_index)
        frame.layers.insert(self.from_index, layer)
        self.document.events.emit(DocumentEvents.LAYERS_REORDERED)
        self.document.notify_pixels_changed()


class LayerPropertyCommand(Command):
    label = "Change Layer Property"

    def __init__(self, document, frame_index, layer_id, property_name, before_value, after_value):
        self.document = document
        self.frame_index = frame_index
        self.layer_id = layer_id
        self.property_name = property_name
        self.before_value = before_value
        self.after_value = after_value

    def _apply(self, value):
        frame = self.document.frames[self.frame_index]
        index = frame.find_layer_index(self.layer_id)
        if index == -1:
            return
        setattr(frame.layers[index], self.property_name, value)
        self.document.events.emit(DocumentEvents.LAYER_CHANGED, self.layer_id)
        self.document.notify_pixels_changed()

    def execute(self):
        self._apply(self.after_value)

    def undo(self):
        self._apply(self.before_value)
