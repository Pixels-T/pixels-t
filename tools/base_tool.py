from abc import ABC, abstractmethod


class BaseTool(ABC):
    name = "base"
    cursor = "crosshair"
    uses_preview = False

    def __init__(self, context):
        self.context = context

    @abstractmethod
    def on_pointer_down(self, x, y, button):
        raise NotImplementedError

    def on_pointer_drag(self, x, y):
        pass

    def on_pointer_move(self, x, y):
        pass

    def on_pointer_up(self, x, y):
        pass

    def cancel(self):
        pass

    def option_definitions(self):
        return []
