import tkinter as tk
from tkinter import ttk

from config.constants import BLEND_MODES
from core.events import DocumentEvents
from rendering.thumbnail_renderer import render_thumbnail


class LayersPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=8)
        self.app = app
        self._thumbnails = {}
        self._drag_index = None

        header = ttk.Frame(self)
        header.pack(fill="x")
        ttk.Label(header, text="Layers", font=("TkDefaultFont", 10, "bold")).pack(side="left")
        button_bar = ttk.Frame(header)
        button_bar.pack(side="right")
        ttk.Button(button_bar, text="+", width=2, command=self._add_layer).pack(side="left", padx=1)
        ttk.Button(button_bar, text="\u2398", width=2, command=self._duplicate_layer).pack(side="left", padx=1)
        ttk.Button(button_bar, text="\u2013", width=2, command=self._remove_layer).pack(side="left", padx=1)
        ttk.Button(button_bar, text="\u2193", width=2, command=self._merge_down).pack(side="left", padx=1)

        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(fill="both", expand=True, pady=(6, 6))

        options_frame = ttk.Frame(self)
        options_frame.pack(fill="x")
        ttk.Label(options_frame, text="Opacity").grid(row=0, column=0, sticky="w")
        self.opacity_var = tk.DoubleVar(value=100.0)
        opacity_slider = ttk.Scale(options_frame, from_=0, to=100, variable=self.opacity_var, command=self._on_opacity_changed)
        opacity_slider.grid(row=0, column=1, sticky="ew", padx=6)
        options_frame.columnconfigure(1, weight=1)

        ttk.Label(options_frame, text="Blend").grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.blend_var = tk.StringVar(value=BLEND_MODES[0])
        blend_combo = ttk.Combobox(options_frame, textvariable=self.blend_var, values=BLEND_MODES, state="readonly", width=10)
        blend_combo.grid(row=1, column=1, sticky="w", pady=(4, 0))
        blend_combo.bind("<<ComboboxSelected>>", self._on_blend_changed)

        self.app.events.subscribe(DocumentEvents.PIXELS_CHANGED, lambda rect=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.LAYER_ADDED, lambda layer_id=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.LAYER_REMOVED, lambda layer_id=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.LAYER_CHANGED, lambda layer_id=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.LAYERS_REORDERED, self.refresh)
        self.app.events.subscribe(DocumentEvents.ACTIVE_LAYER_CHANGED, lambda layer_id=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.ACTIVE_FRAME_CHANGED, lambda index=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.DOCUMENT_LOADED, self.refresh)

        self.refresh()

    def _add_layer(self):
        self.app.add_layer()

    def _duplicate_layer(self):
        self.app.duplicate_layer(self.app.document.active_layer_id)

    def _remove_layer(self):
        self.app.remove_layer(self.app.document.active_layer_id)

    def _merge_down(self):
        self.app.merge_layer_down(self.app.document.active_layer_id)

    def _on_opacity_changed(self, value):
        layer_id = self.app.document.active_layer_id
        self.app.set_layer_property(layer_id, "opacity", float(value) / 100.0)

    def _on_blend_changed(self, event=None):
        layer_id = self.app.document.active_layer_id
        self.app.set_layer_property(layer_id, "blend_mode", self.blend_var.get())

    def _select_layer(self, layer_id):
        self.app.document.set_active_layer(layer_id)

    def _toggle_visible(self, layer_id, current):
        self.app.set_layer_property(layer_id, "visible", not current)

    def _toggle_locked(self, layer_id, current):
        self.app.set_layer_property(layer_id, "locked", not current)

    def _start_drag(self, index):
        self._drag_index = index

    def _drop_drag(self, target_index):
        if self._drag_index is not None and self._drag_index != target_index:
            self.app.reorder_layer(self._drag_index, target_index)
        self._drag_index = None

    def refresh(self, *args):
        for child in self.list_frame.winfo_children():
            child.destroy()
        frame = self.app.document.active_frame
        active_layer_id = self.app.document.active_layer_id
        for display_index, layer in enumerate(reversed(frame.layers)):
            actual_index = len(frame.layers) - 1 - display_index
            row = ttk.Frame(self.list_frame, padding=2)
            row.pack(fill="x", pady=1)
            if layer.id == active_layer_id:
                row.configure(style="Selected.TFrame")
            thumbnail = render_thumbnail(layer.buffer, size=32)
            self._thumbnails[layer.id] = thumbnail
            thumb_label = ttk.Label(row, image=thumbnail)
            thumb_label.pack(side="left", padx=(0, 6))
            visible_button = ttk.Checkbutton(row, text="\U0001F441", command=lambda l=layer: self._toggle_visible(l.id, l.visible))
            visible_state = tk.BooleanVar(value=layer.visible)
            visible_button.configure(variable=visible_state)
            visible_button.pack(side="left")
            locked_button = ttk.Checkbutton(row, text="\U0001F512", command=lambda l=layer: self._toggle_locked(l.id, l.locked))
            locked_state = tk.BooleanVar(value=layer.locked)
            locked_button.configure(variable=locked_state)
            locked_button.pack(side="left")
            name_label = ttk.Label(row, text=layer.name, width=14, anchor="w")
            name_label.pack(side="left", padx=(4, 0), fill="x", expand=True)
            for widget in (row, thumb_label, name_label):
                widget.bind("<Button-1>", lambda event, l=layer, i=actual_index: (self._select_layer(l.id), self._start_drag(i)))
                widget.bind("<ButtonRelease-1>", lambda event, i=actual_index: self._drop_drag(i))
        if frame.layers:
            active_layer = self.app.document.active_layer
            self.opacity_var.set(active_layer.opacity * 100.0)
            self.blend_var.set(active_layer.blend_mode)
