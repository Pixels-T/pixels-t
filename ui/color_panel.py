import tkinter as tk
from tkinter import ttk

from core.color import Color
from core.events import DocumentEvents


class ColorPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=8)
        self.app = app
        self._updating = False

        swatch_frame = ttk.Frame(self)
        swatch_frame.pack(fill="x", pady=(0, 8))
        self.primary_swatch = tk.Canvas(swatch_frame, width=48, height=48, highlightthickness=1, highlightbackground="#555555")
        self.primary_swatch.grid(row=0, column=0, padx=(0, 6))
        self.secondary_swatch = tk.Canvas(swatch_frame, width=32, height=32, highlightthickness=1, highlightbackground="#555555")
        self.secondary_swatch.grid(row=1, column=1, sticky="se")
        self.primary_swatch.bind("<Button-1>", lambda event: self._open_picker(True))
        self.secondary_swatch.bind("<Button-1>", lambda event: self._open_picker(False))
        swap_button = ttk.Button(swatch_frame, text="\u21c4", width=2, command=self._swap_colors)
        swap_button.grid(row=0, column=2, rowspan=2, padx=6)

        hex_frame = ttk.Frame(self)
        hex_frame.pack(fill="x", pady=4)
        ttk.Label(hex_frame, text="HEX").pack(side="left")
        self.hex_var = tk.StringVar()
        hex_entry = ttk.Entry(hex_frame, textvariable=self.hex_var, width=10)
        hex_entry.pack(side="left", padx=6)
        hex_entry.bind("<Return>", self._on_hex_entered)

        self.rgba_vars = {}
        rgba_frame = ttk.Frame(self)
        rgba_frame.pack(fill="x", pady=4)
        for index, channel in enumerate(("R", "G", "B", "A")):
            ttk.Label(rgba_frame, text=channel).grid(row=0, column=index * 2, padx=(0, 2))
            var = tk.IntVar(value=255)
            self.rgba_vars[channel] = var
            spin = ttk.Spinbox(rgba_frame, from_=0, to=255, textvariable=var, width=4, command=self._on_rgba_changed)
            spin.grid(row=0, column=index * 2 + 1, padx=(0, 6))
            spin.bind("<Return>", lambda event: self._on_rgba_changed())

        self.hsv_vars = {}
        hsv_frame = ttk.Frame(self)
        hsv_frame.pack(fill="x", pady=4)
        for index, channel in enumerate(("H", "S", "V")):
            ttk.Label(hsv_frame, text=channel).grid(row=0, column=index * 2, padx=(0, 2))
            var = tk.DoubleVar(value=0.0)
            self.hsv_vars[channel] = var
            spin = ttk.Spinbox(hsv_frame, from_=0, to=360 if channel == "H" else 100, textvariable=var, width=5, command=self._on_hsv_changed)
            spin.grid(row=0, column=index * 2 + 1, padx=(0, 6))
            spin.bind("<Return>", lambda event: self._on_hsv_changed())

        ttk.Label(self, text="Recent Colors").pack(anchor="w", pady=(8, 2))
        self.recent_frame = ttk.Frame(self)
        self.recent_frame.pack(fill="x")

        ttk.Label(self, text="Favorites").pack(anchor="w", pady=(8, 2))
        self.favorites_frame = ttk.Frame(self)
        self.favorites_frame.pack(fill="x")

        favorite_toggle = ttk.Button(self, text="Toggle Favorite", command=self._toggle_favorite)
        favorite_toggle.pack(fill="x", pady=(6, 0))

        self.app.events.subscribe(DocumentEvents.COLOR_CHANGED, self.refresh)
        self.refresh()

    def _current_color(self):
        return Color(*self.app.tool_context.primary_color)

    def _open_picker(self, is_primary):
        from tkinter import colorchooser
        current = self.app.tool_context.primary_color if is_primary else self.app.tool_context.secondary_color
        result = colorchooser.askcolor(color="#%02x%02x%02x" % (current[0], current[1], current[2]))
        if result and result[0] is not None:
            r, g, b = (int(v) for v in result[0])
            color = Color(r, g, b, 255)
            if is_primary:
                self.app.set_primary_color(color)
            else:
                self.app.set_secondary_color(color)

    def _swap_colors(self):
        primary = self.app.tool_context.primary_color
        secondary = self.app.tool_context.secondary_color
        self.app.set_primary_color(Color(*secondary))
        self.app.set_secondary_color(Color(*primary))

    def _on_hex_entered(self, event=None):
        try:
            color = Color.from_hex(self.hex_var.get())
        except ValueError:
            return
        self.app.set_primary_color(color)

    def _on_rgba_changed(self):
        if self._updating:
            return
        try:
            color = Color(self.rgba_vars["R"].get(), self.rgba_vars["G"].get(), self.rgba_vars["B"].get(), self.rgba_vars["A"].get())
        except tk.TclError:
            return
        self.app.set_primary_color(color)

    def _on_hsv_changed(self):
        if self._updating:
            return
        try:
            color = Color.from_hsv(self.hsv_vars["H"].get(), self.hsv_vars["S"].get(), self.hsv_vars["V"].get())
        except tk.TclError:
            return
        self.app.set_primary_color(color)

    def _toggle_favorite(self):
        color = self._current_color()
        self.app.settings.toggle_favorite_color(color.to_hex())
        self.app.settings.save()
        self._render_swatch_row(self.favorites_frame, self.app.settings.get("favorite_colors", []))

    def _render_swatch_row(self, frame, hex_colors):
        for child in frame.winfo_children():
            child.destroy()
        for index, hex_color in enumerate(hex_colors):
            swatch = tk.Canvas(frame, width=18, height=18, highlightthickness=1, highlightbackground="#555555")
            swatch.create_rectangle(0, 0, 18, 18, fill=hex_color, outline="")
            swatch.grid(row=index // 8, column=index % 8, padx=1, pady=1)
            swatch.bind("<Button-1>", lambda event, value=hex_color: self.app.set_primary_color(Color.from_hex(value)))

    def refresh(self, *args):
        primary = self.app.tool_context.primary_color
        secondary = self.app.tool_context.secondary_color
        self.primary_swatch.delete("all")
        self.primary_swatch.create_rectangle(0, 0, 48, 48, fill=self._to_hex(primary), outline="")
        self.secondary_swatch.delete("all")
        self.secondary_swatch.create_rectangle(0, 0, 32, 32, fill=self._to_hex(secondary), outline="")
        self._updating = True
        color = Color(*primary)
        self.hex_var.set(color.to_hex())
        for channel, value in zip(("R", "G", "B", "A"), primary):
            self.rgba_vars[channel].set(value)
        h, s, v = color.to_hsv()
        self.hsv_vars["H"].set(round(h, 1))
        self.hsv_vars["S"].set(round(s, 1))
        self.hsv_vars["V"].set(round(v, 1))
        self._updating = False
        self._render_swatch_row(self.recent_frame, self.app.settings.get("recent_colors", []))
        self._render_swatch_row(self.favorites_frame, self.app.settings.get("favorite_colors", []))

    def _to_hex(self, rgba):
        return "#%02x%02x%02x" % (rgba[0], rgba[1], rgba[2])
