import tkinter as tk
from tkinter import ttk

from config.constants import MIN_FRAME_DURATION_MS, MAX_FRAME_DURATION_MS
from core.events import DocumentEvents
from rendering.thumbnail_renderer import render_thumbnail


class FramesPanel(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, padding=8)
        self.app = app
        self._thumbnails = {}
        self._drag_index = None
        self._playback_job = None

        header = ttk.Frame(self)
        header.pack(fill="x")
        ttk.Label(header, text="Frames", font=("TkDefaultFont", 10, "bold")).pack(side="left")
        button_bar = ttk.Frame(header)
        button_bar.pack(side="right")
        ttk.Button(button_bar, text="+", width=2, command=lambda: self.app.add_frame(copy_active=False)).pack(side="left", padx=1)
        ttk.Button(button_bar, text="\u2398", width=2, command=lambda: self.app.add_frame(copy_active=True)).pack(side="left", padx=1)
        ttk.Button(button_bar, text="\u2013", width=2, command=self._remove_active_frame).pack(side="left", padx=1)

        self.scroll_canvas = tk.Canvas(self, height=90, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="horizontal", command=self.scroll_canvas.xview)
        self.scroll_canvas.configure(xscrollcommand=scrollbar.set)
        self.scroll_canvas.pack(fill="x", pady=(6, 0))
        scrollbar.pack(fill="x")
        self.strip_frame = ttk.Frame(self.scroll_canvas)
        self.scroll_canvas.create_window((0, 0), window=self.strip_frame, anchor="nw")
        self.strip_frame.bind("<Configure>", lambda event: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all")))

        controls = ttk.Frame(self)
        controls.pack(fill="x", pady=(6, 0))
        self.play_button = ttk.Button(controls, text="\u25b6 Play", command=self._toggle_playback)
        self.play_button.pack(side="left")
        ttk.Label(controls, text="Duration (ms)").pack(side="left", padx=(10, 2))
        self.duration_var = tk.IntVar(value=100)
        duration_spin = ttk.Spinbox(controls, from_=MIN_FRAME_DURATION_MS, to=MAX_FRAME_DURATION_MS, textvariable=self.duration_var, width=6, command=self._on_duration_changed)
        duration_spin.pack(side="left")
        duration_spin.bind("<Return>", lambda event: self._on_duration_changed())

        onion_frame = ttk.Frame(self)
        onion_frame.pack(fill="x", pady=(6, 0))
        self.onion_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(onion_frame, text="Onion Skin", variable=self.onion_var, command=self._on_onion_toggle).pack(side="left")

        self.app.events.subscribe(DocumentEvents.FRAME_ADDED, lambda index=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.FRAME_REMOVED, lambda index=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.FRAMES_REORDERED, self.refresh)
        self.app.events.subscribe(DocumentEvents.ACTIVE_FRAME_CHANGED, lambda index=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.PIXELS_CHANGED, lambda rect=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.FRAME_DURATION_CHANGED, lambda index=None: self.refresh())
        self.app.events.subscribe(DocumentEvents.DOCUMENT_LOADED, self.refresh)

        self.refresh()

    def _remove_active_frame(self):
        self.app.remove_frame(self.app.document.active_frame_index)

    def _on_duration_changed(self):
        self.app.set_frame_duration(self.app.document.active_frame_index, self.duration_var.get())

    def _on_onion_toggle(self):
        self.app.document.onion_skin_enabled = self.onion_var.get()
        self.app.document.notify_pixels_changed()

    def _select_frame(self, index):
        self.app.document.set_active_frame(index)

    def _start_drag(self, index):
        self._drag_index = index

    def _drop_drag(self, target_index):
        if self._drag_index is not None and self._drag_index != target_index:
            self.app.reorder_frame(self._drag_index, target_index)
        self._drag_index = None

    def _toggle_playback(self):
        if self._playback_job is not None:
            self.after_cancel(self._playback_job)
            self._playback_job = None
            self.play_button.configure(text="\u25b6 Play")
        else:
            self.play_button.configure(text="\u23f8 Pause")
            self._advance_playback()

    def _advance_playback(self):
        document = self.app.document
        next_index = (document.active_frame_index + 1) % len(document.frames)
        document.set_active_frame(next_index)
        duration = document.frames[next_index].duration_ms
        self._playback_job = self.after(duration, self._advance_playback)

    def refresh(self, *args):
        for child in self.strip_frame.winfo_children():
            child.destroy()
        document = self.app.document
        for index, frame in enumerate(document.frames):
            cell = ttk.Frame(self.strip_frame, padding=3)
            cell.grid(row=0, column=index, padx=2)
            if index == document.active_frame_index:
                cell.configure(style="Selected.TFrame")
            composite = frame.composite()
            thumbnail = render_thumbnail(composite, size=48)
            self._thumbnails[frame.id] = thumbnail
            label = ttk.Label(cell, image=thumbnail)
            label.pack()
            number_label = ttk.Label(cell, text=str(index + 1))
            number_label.pack()
            for widget in (cell, label, number_label):
                widget.bind("<Button-1>", lambda event, i=index: (self._select_frame(i), self._start_drag(i)))
                widget.bind("<ButtonRelease-1>", lambda event, i=index: self._drop_drag(i))
        if document.frames:
            self.duration_var.set(document.active_frame.duration_ms)
