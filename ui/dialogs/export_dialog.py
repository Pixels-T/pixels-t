import tkinter as tk
from tkinter import ttk


class ExportDialog(tk.Toplevel):
    def __init__(self, parent, frame_count):
        super().__init__(parent)
        self.title("Export")
        self.resizable(False, False)
        self.result = None
        self.transient(parent)
        self.grab_set()

        form = ttk.Frame(self, padding=16)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Format").grid(row=0, column=0, sticky="w", pady=4)
        self.format_var = tk.StringVar(value="png")
        format_combo = ttk.Combobox(form, textvariable=self.format_var, state="readonly", width=18,
                                     values=["png", "png_sprite_sheet", "gif", "png_sequence"])
        format_combo.grid(row=0, column=1, pady=4)

        ttk.Label(form, text="Scale").grid(row=1, column=0, sticky="w", pady=4)
        self.scale_var = tk.IntVar(value=1)
        ttk.Spinbox(form, from_=1, to=32, textvariable=self.scale_var, width=6).grid(row=1, column=1, pady=4, sticky="w")

        ttk.Label(form, text=f"Frames available: {frame_count}").grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 4))

        button_frame = ttk.Frame(form)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side="right", padx=(6, 0))
        ttk.Button(button_frame, text="Export", command=self._on_confirm).pack(side="right")

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window(self)

    def _on_confirm(self):
        self.result = (self.format_var.get(), self.scale_var.get())
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()
