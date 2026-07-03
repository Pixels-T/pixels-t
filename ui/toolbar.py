from tkinter import ttk

from config.constants import (
    TOOL_PENCIL, TOOL_ERASER, TOOL_BUCKET, TOOL_LINE, TOOL_RECTANGLE,
    TOOL_ELLIPSE, TOOL_EYEDROPPER, TOOL_SELECTION, TOOL_MOVE,
    TOOL_GRADIENT, TOOL_SPRAY,
)
from core.events import DocumentEvents

TOOL_LABELS = [
    (TOOL_PENCIL, "\u270f", "Pencil (P)"),
    (TOOL_ERASER, "\u2b1b", "Eraser (E)"),
    (TOOL_BUCKET, "\U0001FAA3", "Bucket Fill (B)"),
    (TOOL_LINE, "\u2571", "Line (L)"),
    (TOOL_RECTANGLE, "\u25ad", "Rectangle (R)"),
    (TOOL_ELLIPSE, "\u25ef", "Ellipse (O)"),
    (TOOL_EYEDROPPER, "\U0001F441", "Eyedropper (I)"),
    (TOOL_SELECTION, "\u2b1a", "Selection (M)"),
    (TOOL_MOVE, "\u2725", "Move (V)"),
    (TOOL_GRADIENT, "\u25a4", "Gradient (G)"),
    (TOOL_SPRAY, "\u2734", "Spray (S)"),
]


class Toolbar(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=4)
        self.app = app
        self.buttons = {}
        for name, glyph, tooltip in TOOL_LABELS:
            button = ttk.Button(self, text=glyph, width=3, command=lambda n=name: self.app.tool_manager.set_active_tool(n))
            button.pack(pady=2)
            self.buttons[name] = button
        self.app.events.subscribe(DocumentEvents.TOOL_CHANGED, lambda name=None: self.refresh())
        self.refresh()

    def refresh(self, *args):
        active = self.app.tool_manager.active_tool_name
        for name, button in self.buttons.items():
            button.state(["pressed"] if name == active else ["!pressed"])
