import tkinter as tk
from tkinter import ttk

from config.constants import (
    TOOL_PENCIL, TOOL_ERASER, TOOL_BUCKET, TOOL_RECTANGLE, TOOL_ELLIPSE,
    TOOL_SPRAY,
)
from core.events import DocumentEvents


class ToolOptionsPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=(8, 4))
        self.app = app
        self.brush_size_var = tk.IntVar(value=1)
        self.pixel_perfect_var = tk.BooleanVar(value=True)
        self.symmetry_h_var = tk.BooleanVar(value=False)
        self.symmetry_v_var = tk.BooleanVar(value=False)
        self.tolerance_var = tk.IntVar(value=0)
        self.filled_var = tk.BooleanVar(value=False)
        self.spray_radius_var = tk.IntVar(value=4)
        self.spray_density_var = tk.DoubleVar(value=25.0)

        self.brush_size_label = ttk.Label(self, text="Size")
        self.brush_size_spin = ttk.Spinbox(self, from_=1, to=32, textvariable=self.brush_size_var, width=4, command=self._on_brush_size_changed)

        self.pixel_perfect_check = ttk.Checkbutton(self, text="Pixel Perfect", variable=self.pixel_perfect_var, command=self._on_pixel_perfect_changed)
        self.symmetry_h_check = ttk.Checkbutton(self, text="Mirror X", variable=self.symmetry_h_var, command=self._on_symmetry_changed)
        self.symmetry_v_check = ttk.Checkbutton(self, text="Mirror Y", variable=self.symmetry_v_var, command=self._on_symmetry_changed)

        self.tolerance_label = ttk.Label(self, text="Tolerance")
        self.tolerance_spin = ttk.Spinbox(self, from_=0, to=255, textvariable=self.tolerance_var, width=4, command=self._on_tolerance_changed)

        self.filled_check = ttk.Checkbutton(self, text="Filled", variable=self.filled_var, command=self._on_filled_changed)

        self.spray_radius_label = ttk.Label(self, text="Radius")
        self.spray_radius_spin = ttk.Spinbox(self, from_=1, to=64, textvariable=self.spray_radius_var, width=4, command=self._on_spray_changed)
        self.spray_density_label = ttk.Label(self, text="Density")
        self.spray_density_spin = ttk.Spinbox(self, from_=1, to=100, textvariable=self.spray_density_var, width=4, command=self._on_spray_changed)

        self.app.events.subscribe(DocumentEvents.TOOL_CHANGED, lambda name=None: self.refresh())
        self.refresh()

    def _on_brush_size_changed(self):
        self.app.tool_context.brush_size = self.brush_size_var.get()

    def _on_pixel_perfect_changed(self):
        self.app.tool_context.pixel_perfect = self.pixel_perfect_var.get()

    def _on_symmetry_changed(self):
        self.app.tool_context.symmetry_horizontal = self.symmetry_h_var.get()
        self.app.tool_context.symmetry_vertical = self.symmetry_v_var.get()

    def _on_tolerance_changed(self):
        self.app.tool_context.fill_tolerance = self.tolerance_var.get()

    def _on_filled_changed(self):
        tool = self.app.tool_manager.active_tool
        if hasattr(tool, "filled"):
            tool.filled = self.filled_var.get()

    def _on_spray_changed(self):
        self.app.tool_context.spray_radius = self.spray_radius_var.get()
        self.app.tool_context.spray_density = self.spray_density_var.get() / 100.0

    def refresh(self, *args):
        for widget in self.winfo_children():
            widget.pack_forget()
        active = self.app.tool_manager.active_tool_name
        self.symmetry_h_check.pack(side="left", padx=4)
        self.symmetry_v_check.pack(side="left", padx=4)
        if active in (TOOL_PENCIL, TOOL_ERASER, TOOL_SPRAY):
            self.brush_size_label.pack(side="left", padx=(12, 2))
            self.brush_size_spin.pack(side="left")
        if active == TOOL_PENCIL:
            self.pixel_perfect_check.pack(side="left", padx=8)
        if active == TOOL_BUCKET:
            self.tolerance_label.pack(side="left", padx=(12, 2))
            self.tolerance_spin.pack(side="left")
        if active in (TOOL_RECTANGLE, TOOL_ELLIPSE):
            self.filled_check.pack(side="left", padx=8)
        if active == TOOL_SPRAY:
            self.spray_radius_label.pack(side="left", padx=(12, 2))
            self.spray_radius_spin.pack(side="left")
            self.spray_density_label.pack(side="left", padx=(12, 2))
            self.spray_density_spin.pack(side="left")
