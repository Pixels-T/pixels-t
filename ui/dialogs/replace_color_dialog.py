import tkinter as tk
from tkinter import ttk, colorchooser


class ReplaceColorDialog(tk.Toplevel):
    def __init__(self, parent, current_color):
        super().__init__(parent)
        self.title("Replace Color")
        self.resizable(False, False)
        self.result = None
        self.transient(parent)
        self.grab_set()

        self.old_color = current_color
        self.new_color = (255, 255, 255, 255)

        form = ttk.Frame(self, padding=16)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Old Color").grid(row=0, column=0, sticky="w", pady=4)
        self.old_swatch = tk.Canvas(form, width=28, height=20, highlightthickness=1, highlightbackground="#555555")
        self.old_swatch.grid(row=0, column=1, pady=4)
        self.old_swatch.bind("<Button-1>", lambda event: self._pick_old())

        ttk.Label(form, text="New Color").grid(row=1, column=0, sticky="w", pady=4)
        self.new_swatch = tk.Canvas(form, width=28, height=20, highlightthickness=1, highlightbackground="#555555")
        self.new_swatch.grid(row=1, column=1, pady=4)
        self.new_swatch.bind("<Button-1>", lambda event: self._pick_new())

        ttk.Label(form, text="Tolerance").grid(row=2, column=0, sticky="w", pady=4)
        self.tolerance_var = tk.IntVar(value=0)
        ttk.Spinbox(form, from_=0, to=255, textvariable=self.tolerance_var, width=6).grid(row=2, column=1, pady=4, sticky="w")

        button_frame = ttk.Frame(form)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(12, 0), sticky="e")
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side="right", padx=(6, 0))
        ttk.Button(button_frame, text="Replace", command=self._on_confirm).pack(side="right")

        self._redraw_swatches()
        self.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.wait_window(self)

    def _redraw_swatches(self):
        self.old_swatch.delete("all")
        self.old_swatch.create_rectangle(0, 0, 28, 20, fill=self._hex(self.old_color), outline="")
        self.new_swatch.delete("all")
        self.new_swatch.create_rectangle(0, 0, 28, 20, fill=self._hex(self.new_color), outline="")

    def _hex(self, rgba):
        return "#%02x%02x%02x" % (rgba[0], rgba[1], rgba[2])

    def _pick_old(self):
        result = colorchooser.askcolor(color=self._hex(self.old_color))
        if result and result[0] is not None:
            r, g, b = (int(v) for v in result[0])
            self.old_color = (r, g, b, 255)
            self._redraw_swatches()

    def _pick_new(self):
        result = colorchooser.askcolor(color=self._hex(self.new_color))
        if result and result[0] is not None:
            r, g, b = (int(v) for v in result[0])
            self.new_color = (r, g, b, 255)
            self._redraw_swatches()

    def _on_confirm(self):
        self.result = (self.old_color, self.new_color, self.tolerance_var.get())
        self.destroy()

    def _on_cancel(self):
        self.result = None
        self.destroy()
