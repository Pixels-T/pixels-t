from commands.command import Command
from core.events import DocumentEvents


class AddFrameCommand(Command):
    label = "Add Frame"

    def __init__(self, document, index, frame):
        self.document = document
        self.index = index
        self.frame = frame

    def execute(self):
        self.document.frames.insert(self.index, self.frame)
        self.document.active_frame_index = self.index
        self.document.events.emit(DocumentEvents.FRAME_ADDED, self.index)
        self.document.notify_pixels_changed()

    def undo(self):
        del self.document.frames[self.index]
        if self.document.active_frame_index >= len(self.document.frames):
            self.document.active_frame_index = len(self.document.frames) - 1
        self.document.events.emit(DocumentEvents.FRAME_REMOVED, self.index)
        self.document.notify_pixels_changed()


class RemoveFrameCommand(Command):
    label = "Remove Frame"

    def __init__(self, document, index, frame):
        self.document = document
        self.index = index
        self.frame = frame

    def execute(self):
        del self.document.frames[self.index]
        if self.document.active_frame_index >= len(self.document.frames):
            self.document.active_frame_index = len(self.document.frames) - 1
        self.document.events.emit(DocumentEvents.FRAME_REMOVED, self.index)
        self.document.notify_pixels_changed()

    def undo(self):
        self.document.frames.insert(self.index, self.frame)
        self.document.active_frame_index = self.index
        self.document.events.emit(DocumentEvents.FRAME_ADDED, self.index)
        self.document.notify_pixels_changed()


class ReorderFrameCommand(Command):
    label = "Reorder Frames"

    def __init__(self, document, from_index, to_index):
        self.document = document
        self.from_index = from_index
        self.to_index = to_index

    def execute(self):
        frame = self.document.frames.pop(self.from_index)
        self.document.frames.insert(self.to_index, frame)
        self.document.active_frame_index = self.to_index
        self.document.events.emit(DocumentEvents.FRAMES_REORDERED)
        self.document.notify_pixels_changed()

    def undo(self):
        frame = self.document.frames.pop(self.to_index)
        self.document.frames.insert(self.from_index, frame)
        self.document.active_frame_index = self.from_index
        self.document.events.emit(DocumentEvents.FRAMES_REORDERED)
        self.document.notify_pixels_changed()


class FrameDurationCommand(Command):
    label = "Change Frame Duration"

    def __init__(self, document, frame_index, before_value, after_value):
        self.document = document
        self.frame_index = frame_index
        self.before_value = before_value
        self.after_value = after_value

    def execute(self):
        self.document.frames[self.frame_index].duration_ms = self.after_value
        self.document.events.emit(DocumentEvents.FRAME_DURATION_CHANGED, self.frame_index)

    def undo(self):
        self.document.frames[self.frame_index].duration_ms = self.before_value
        self.document.events.emit(DocumentEvents.FRAME_DURATION_CHANGED, self.frame_index)
