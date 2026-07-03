import tkinter as tk
from tkinter import ttk

from config.constants import DEFAULT_CANVAS_WIDTH, DEFAULT_CANVAS_HEIGHT, MAX_CANVAS_DIMENSION, MIN_CANVAS_DIMENSION


class NewProjectDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("New Project")
        self.resizable(False, False)
        self.result = None
        self.transient(parent)
        self.grab_set()

        form = ttk.Frame(self, padding=16)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Name").grid(row=0, column=0, sticky="w", pady=4)
        self.name_var = tk.StringVar(value="Untitled")
        ttk.Entry(form, textvariable=self.name_var, width=24).grid(row=0, column=1, pady=4)

        ttk.Label(form, text="Width").grid(row=1, column=0, sticky="w", pady=4)
        self.width_var = tk.IntVar(value=DEFAULT_CANVAS_WIDTH)
        ttk.Spinbox(form, from_=MIN_CANVAS_DIMENSION, to=MAX_CANVAS_DIMENSION, textvariable=self.width_var, width=10).grid(row=1, column=1, pady=4)

        ttk.Label(form, text="Height").grid(row=2, column=0, sticky="w", pady=4)
        self.height_var = tk.IntVar(value=DEFAULT_CANVAS_HEIGHT)
        ttk.Spinbox(form, from_=MIN_CANVAS_DIMENSION, to=MAX_CANVAS_DIMENSION, textvariable=self.height_var, width=10).grid(row=2, column=1, pady=4)

        preset_frame = ttk.Frame(form)
        preset_frame.grid(row=3, column=0, columnspan=2, pady=(6, 0))
        for size in (16, 32, 64, 128):
            ttk.Button(preset_frame, text=f"{size}x{size}", command=lambda s=size: self._apply_preset(s)).pack(side="left", padx=2)

        button_frame = ttk.Frame(form)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(16, 0), sticky="e")
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side="right", padx=(6, 0))
        ttk.Button(button_frame, text="Create", command=self._on_create).pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window(self)

    def _apply_preset(self, size):
        self.width_var.set(size)
        self.height_var.set(size)

    def _on_create(self):
        self.result = (self.name_var.get() or "Untitled", self.width_var.get(), self.height_var.get())
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()
