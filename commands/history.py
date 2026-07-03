from config.constants import MAX_UNDO_HISTORY
from core.events import DocumentEvents


class HistoryManager:
    def __init__(self, event_bus, max_size=MAX_UNDO_HISTORY):
        self.events = event_bus
        self.max_size = max_size
        self.undo_stack = []
        self.redo_stack = []

    def execute(self, command):
        command.execute()
        self._push(command)

    def push_applied(self, command):
        self._push(command)

    def _push(self, command):
        self.undo_stack.append(command)
        if len(self.undo_stack) > self.max_size:
            self.undo_stack.pop(0)
        self.redo_stack.clear()
        self.events.emit(DocumentEvents.HISTORY_CHANGED)

    def undo(self):
        if not self.undo_stack:
            return False
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        self.events.emit(DocumentEvents.HISTORY_CHANGED)
        return True

    def redo(self):
        if not self.redo_stack:
            return False
        command = self.redo_stack.pop()
        command.execute()
        self.undo_stack.append(command)
        self.events.emit(DocumentEvents.HISTORY_CHANGED)
        return True

    def can_undo(self):
        return len(self.undo_stack) > 0

    def can_redo(self):
        return len(self.redo_stack) > 0

    def clear(self):
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.events.emit(DocumentEvents.HISTORY_CHANGED)

    def labels(self):
        return [command.label for command in self.undo_stack]
