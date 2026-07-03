from commands.command import Command


class PixelRegionCommand(Command):
    label = "Draw"

    def __init__(self, document, frame_index, layer_id, rect, before_data, after_data):
        self.document = document
        self.frame_index = frame_index
        self.layer_id = layer_id
        self.rect = rect
        self.before_data = before_data
        self.after_data = after_data

    def _target_layer(self):
        frame = self.document.frames[self.frame_index]
        index = frame.find_layer_index(self.layer_id)
        if index == -1:
            return None
        return frame.layers[index]

    def _apply(self, data):
        layer = self._target_layer()
        if layer is None:
            return
        layer.buffer.data[self.rect.y:self.rect.y + self.rect.height, self.rect.x:self.rect.x + self.rect.width] = data
        self.document.notify_pixels_changed(self.rect)

    def execute(self):
        self._apply(self.after_data)

    def undo(self):
        self._apply(self.before_data)


class FullBufferCommand(Command):
    label = "Edit"

    def __init__(self, document, frame_index, layer_id, before_data, after_data):
        self.document = document
        self.frame_index = frame_index
        self.layer_id = layer_id
        self.before_data = before_data
        self.after_data = after_data

    def _target_layer(self):
        frame = self.document.frames[self.frame_index]
        index = frame.find_layer_index(self.layer_id)
        if index == -1:
            return None
        return frame.layers[index]

    def execute(self):
        layer = self._target_layer()
        if layer is None:
            return
        layer.buffer.data[:, :] = self.after_data
        self.document.notify_pixels_changed()

    def undo(self):
        layer = self._target_layer()
        if layer is None:
            return
        layer.buffer.data[:, :] = self.before_data
        self.document.notify_pixels_changed()


class CanvasResizeCommand(Command):
    label = "Resize Canvas"

    def __init__(self, document, before_frames, after_frames, before_size, after_size):
        self.document = document
        self.before_frames = before_frames
        self.after_frames = after_frames
        self.before_size = before_size
        self.after_size = after_size

    def execute(self):
        self.document.frames = self.after_frames
        self.document.width, self.document.height = self.after_size
        self.document.notify_pixels_changed()

    def undo(self):
        self.document.frames = self.before_frames
        self.document.width, self.document.height = self.before_size
        self.document.notify_pixels_changed()
