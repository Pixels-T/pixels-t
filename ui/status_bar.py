import tkinter as tk
from tkinter import ttk

from core.events import DocumentEvents


class StatusBar(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=(8, 2))
        self.app = app

        self.coords_var = tk.StringVar(value="X: - Y: -")
        self.zoom_var = tk.StringVar(value="Zoom: 100%")
        self.size_var = tk.StringVar(value="")
        self.tool_var = tk.StringVar(value="")
        self.history_var = tk.StringVar(value="")

        ttk.Label(self, textvariable=self.coords_var, width=16).pack(side="left")
        ttk.Separator(self, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Label(self, textvariable=self.zoom_var, width=12).pack(side="left")
        ttk.Separator(self, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Label(self, textvariable=self.size_var, width=16).pack(side="left")
        ttk.Separator(self, orient="vertical").pack(side="left", fill="y", padx=6)
        ttk.Label(self, textvariable=self.tool_var, width=14).pack(side="left")
        ttk.Label(self, textvariable=self.history_var).pack(side="right")

        self.app.events.subscribe(DocumentEvents.ZOOM_CHANGED, lambda zoom=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.CANVAS_RESIZED, lambda w=None, h=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.TOOL_CHANGED, lambda name=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.HISTORY_CHANGED, self.refresh)
        self.app.events.subscribe(DocumentEvents.DOCUMENT_LOADED, self.refresh)
        self.refresh()

    def set_coordinates(self, x, y):
        document = self.app.document
        if 0 <= x < document.width and 0 <= y < document.height:
            self.coords_var.set(f"X: {x} Y: {y}")
        else:
            self.coords_var.set("X: - Y: -")

    def refresh(self, *args):
        self.zoom_var.set(f"Zoom: {round(self.app.zoom * 100)}%")
        self.size_var.set(f"{self.app.document.width} x {self.app.document.height}")
        self.tool_var.set(self.app.tool_manager.active_tool_name.capitalize())
        self.history_var.set(f"Undo: {len(self.app.history.undo_stack)}  Redo: {len(self.app.history.redo_stack)}")
