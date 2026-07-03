import tkinter as tk
from tkinter import ttk

from core.color import Color


class PalettePanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=8)
        self.app = app

        header = ttk.Frame(self)
        header.pack(fill="x")
        ttk.Label(header, text="Palette", font=("TkDefaultFont", 10, "bold")).pack(side="left")
        ttk.Button(header, text="+", width=2, command=self._add_current_color).pack(side="right")

        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(fill="both", expand=True, pady=(6, 0))

        self.refresh()

    def _add_current_color(self):
        color = Color(*self.app.tool_context.primary_color)
        self.app.document.palette.add_color(color)
        self.refresh()

    def _remove_color(self, index):
        self.app.document.palette.remove_color(index)
        self.refresh()

    def refresh(self):
        for child in self.grid_frame.winfo_children():
            child.destroy()
        columns = 8
        for index, color in enumerate(self.app.document.palette.colors):
            swatch = tk.Canvas(self.grid_frame, width=22, height=22, highlightthickness=1, highlightbackground="#555555")
            swatch.create_rectangle(0, 0, 22, 22, fill=color.to_hex(), outline="")
            swatch.grid(row=index // columns, column=index % columns, padx=1, pady=1)
            swatch.bind("<Button-1>", lambda event, c=color: self.app.set_primary_color(c))
            swatch.bind("<Button-3>", lambda event, i=index: self._remove_color(i))
