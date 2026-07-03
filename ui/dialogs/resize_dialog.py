import tkinter as tk
from tkinter import ttk

from config.constants import MAX_CANVAS_DIMENSION, MIN_CANVAS_DIMENSION


class ResizeDialog(tk.Toplevel):
    def __init__(self, parent, current_width, current_height):
        super().__init__(parent)
        self.title("Resize Canvas")
        self.resizable(False, False)
        self.result = None
        self.transient(parent)
        self.grab_set()

        form = ttk.Frame(self, padding=16)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Width").grid(row=0, column=0, sticky="w", pady=4)
        self.width_var = tk.IntVar(value=current_width)
        ttk.Spinbox(form, from_=MIN_CANVAS_DIMENSION, to=MAX_CANVAS_DIMENSION, textvariable=self.width_var, width=10).grid(row=0, column=1, pady=4)

        ttk.Label(form, text="Height").grid(row=1, column=0, sticky="w", pady=4)
        self.height_var = tk.IntVar(value=current_height)
        ttk.Spinbox(form, from_=MIN_CANVAS_DIMENSION, to=MAX_CANVAS_DIMENSION, textvariable=self.height_var, width=10).grid(row=1, column=1, pady=4)

        ttk.Label(form, text="Anchor").grid(row=2, column=0, sticky="nw", pady=4)
        anchor_frame = ttk.Frame(form)
        anchor_frame.grid(row=2, column=1, pady=4)
        self.anchor_var = tk.StringVar(value="top_left")
        anchors = [
            ("top_left", "\u2196", 0, 0), ("top", "\u2191", 0, 1), ("top_right", "\u2197", 0, 2),
            ("left", "\u2190", 1, 0), ("center", "\u25cf", 1, 1), ("right", "\u2192", 1, 2),
            ("bottom_left", "\u2199", 2, 0), ("bottom", "\u2193", 2, 1), ("bottom_right", "\u2198", 2, 2),
        ]
        for value, glyph, row, col in anchors:
            ttk.Radiobutton(anchor_frame, text=glyph, value=value, variable=self.anchor_var, width=3).grid(row=row, column=col)

        button_frame = ttk.Frame(form)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(16, 0), sticky="e")
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side="right", padx=(6, 0))
        ttk.Button(button_frame, text="Resize", command=self._on_confirm).pack(side="right")

        self.current_width = current_width
        self.current_height = current_height
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window(self)

    def _compute_anchor_offset(self, new_width, new_height):
        anchor = self.anchor_var.get()
        key_map = {
            "top_left": (0.0, 0.0), "top": (0.5, 0.0), "top_right": (1.0, 0.0),
            "left": (0.0, 0.5), "center": (0.5, 0.5), "right": (1.0, 0.5),
            "bottom_left": (0.0, 1.0), "bottom": (0.5, 1.0), "bottom_right": (1.0, 1.0),
        }
        h_factor, v_factor = key_map[anchor]
        anchor_x = round((new_width - self.current_width) * h_factor)
        anchor_y = round((new_height - self.current_height) * v_factor)
        return anchor_x, anchor_y

    def _on_confirm(self):
        new_width = self.width_var.get()
        new_height = self.height_var.get()
        anchor_x, anchor_y = self._compute_anchor_offset(new_width, new_height)
        self.result = (new_width, new_height, anchor_x, anchor_y)
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()
