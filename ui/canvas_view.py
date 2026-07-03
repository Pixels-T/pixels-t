import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

from config.constants import (
    CANVAS_BACKGROUND, GRID_LINE_COLOR, PIXEL_GRID_MIN_ZOOM, RULER_SIZE,
    RULER_BACKGROUND, RULER_TEXT_COLOR, SELECTION_COLOR, MIN_ZOOM, MAX_ZOOM,
    ZOOM_STEP_FACTOR,
)
from core.events import DocumentEvents
from rendering.canvas_renderer import CanvasRenderer


class CanvasView(ttk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.renderer = CanvasRenderer()
        self.offset_x = 40.0
        self.offset_y = 40.0
        self.show_pixel_grid = True
        self.show_grid = False
        self.grid_size = 8
        self.preview_points = None
        self._photo_image = None
        self._image_item = None
        self._space_held = False
        self._pan_start = None
        self._pan_offset_start = None
        self._last_doc_point = None

        self.corner = tk.Canvas(self, width=RULER_SIZE, height=RULER_SIZE, bg=RULER_BACKGROUND, highlightthickness=0)
        self.top_ruler = tk.Canvas(self, height=RULER_SIZE, bg=RULER_BACKGROUND, highlightthickness=0)
        self.left_ruler = tk.Canvas(self, width=RULER_SIZE, bg=RULER_BACKGROUND, highlightthickness=0)
        self.canvas = tk.Canvas(self, bg=CANVAS_BACKGROUND, highlightthickness=0)

        self.corner.grid(row=0, column=0, sticky="nsew")
        self.top_ruler.grid(row=0, column=1, sticky="nsew")
        self.left_ruler.grid(row=1, column=0, sticky="nsew")
        self.canvas.grid(row=1, column=1, sticky="nsew")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.canvas.bind("<Button-1>", self._on_button1_down)
        self.canvas.bind("<B1-Motion>", self._on_button1_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_button1_up)
        self.canvas.bind("<Button-3>", self._on_button3_down)
        self.canvas.bind("<B3-Motion>", self._on_button3_drag)
        self.canvas.bind("<ButtonRelease-3>", self._on_button3_up)
        self.canvas.bind("<Button-2>", self._on_pan_start)
        self.canvas.bind("<B2-Motion>", self._on_pan_drag)
        self.canvas.bind("<Motion>", self._on_motion)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.canvas.bind("<Button-4>", self._on_wheel_linux_up)
        self.canvas.bind("<Button-5>", self._on_wheel_linux_down)
        self.canvas.bind("<Configure>", lambda event: self.redraw())

        self.app.events.subscribe(DocumentEvents.PIXELS_CHANGED, lambda rect=None: self.redraw())
        self.app.events.subscribe(DocumentEvents.LAYER_CHANGED, lambda layer_id=None: self.redraw())
        self.app.events.subscribe(DocumentEvents.ACTIVE_FRAME_CHANGED, lambda index=None: self.redraw())
        self.app.events.subscribe(DocumentEvents.CANVAS_RESIZED, lambda w=None, h=None: self.redraw())
        self.app.events.subscribe(DocumentEvents.DOCUMENT_LOADED, lambda: self.center_view())
        self.app.events.subscribe(DocumentEvents.ZOOM_CHANGED, lambda zoom=None: self.redraw())
        self.app.events.subscribe(DocumentEvents.SELECTION_CHANGED, lambda rect=None: self.redraw())

        self.on_pointer_moved = None

    def center_view(self):
        canvas_width = max(self.canvas.winfo_width(), 200)
        canvas_height = max(self.canvas.winfo_height(), 200)
        doc_width = self.app.document.width * self.app.zoom
        doc_height = self.app.document.height * self.app.zoom
        self.offset_x = max(0, (canvas_width - doc_width) / 2)
        self.offset_y = max(0, (canvas_height - doc_height) / 2)
        self.redraw()

    def screen_to_doc(self, sx, sy):
        zoom = self.app.zoom
        doc_x = (sx - self.offset_x) / zoom
        doc_y = (sy - self.offset_y) / zoom
        return int(doc_x) if doc_x >= 0 else int(doc_x) - 1, int(doc_y) if doc_y >= 0 else int(doc_y) - 1

    def _active_tool(self):
        return self.app.tool_manager.active_tool

    def _on_button1_down(self, event):
        if self._space_held:
            self._on_pan_start(event)
            return
        x, y = self.screen_to_doc(event.x, event.y)
        self._last_doc_point = (x, y)
        self._active_tool().on_pointer_down(x, y, 1)

    def _on_button1_drag(self, event):
        if self._space_held:
            self._on_pan_drag(event)
            return
        x, y = self.screen_to_doc(event.x, event.y)
        if self._last_doc_point == (x, y):
            return
        self._last_doc_point = (x, y)
        self._active_tool().on_pointer_drag(x, y)

    def _on_button1_up(self, event):
        x, y = self.screen_to_doc(event.x, event.y)
        self._active_tool().on_pointer_up(x, y)
        self._last_doc_point = None

    def _on_button3_down(self, event):
        x, y = self.screen_to_doc(event.x, event.y)
        self._active_tool().on_pointer_down(x, y, 3)

    def _on_button3_drag(self, event):
        x, y = self.screen_to_doc(event.x, event.y)
        self._active_tool().on_pointer_drag(x, y)

    def _on_button3_up(self, event):
        x, y = self.screen_to_doc(event.x, event.y)
        self._active_tool().on_pointer_up(x, y)

    def _on_pan_start(self, event):
        self._pan_start = (event.x, event.y)
        self._pan_offset_start = (self.offset_x, self.offset_y)

    def _on_pan_drag(self, event):
        if self._pan_start is None:
            return
        dx = event.x - self._pan_start[0]
        dy = event.y - self._pan_start[1]
        self.offset_x = self._pan_offset_start[0] + dx
        self.offset_y = self._pan_offset_start[1] + dy
        self.redraw()

    def _on_motion(self, event):
        x, y = self.screen_to_doc(event.x, event.y)
        if self.on_pointer_moved is not None:
            self.on_pointer_moved(x, y)
        self._active_tool().on_pointer_move(x, y)

    def _on_wheel(self, event):
        factor = ZOOM_STEP_FACTOR if event.delta > 0 else 1.0 / ZOOM_STEP_FACTOR
        self._zoom_at(event.x, event.y, factor)

    def _on_wheel_linux_up(self, event):
        self._zoom_at(event.x, event.y, ZOOM_STEP_FACTOR)

    def _on_wheel_linux_down(self, event):
        self._zoom_at(event.x, event.y, 1.0 / ZOOM_STEP_FACTOR)

    def _zoom_at(self, screen_x, screen_y, factor):
        old_zoom = self.app.zoom
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, old_zoom * factor))
        if new_zoom == old_zoom:
            return
        doc_x = (screen_x - self.offset_x) / old_zoom
        doc_y = (screen_y - self.offset_y) / old_zoom
        self.app.set_zoom(new_zoom)
        self.offset_x = screen_x - doc_x * new_zoom
        self.offset_y = screen_y - doc_y * new_zoom
        self.redraw()

    def set_space_held(self, held):
        self._space_held = held
        self.canvas.configure(cursor="fleur" if held else "")

    def set_preview(self, points_with_colors):
        self.preview_points = points_with_colors
        self.redraw()

    def clear_preview(self):
        self.preview_points = None
        self.redraw()

    def _build_composite_image(self):
        document = self.app.document
        frame = document.active_frame
        composite = frame.composite()
        display_buffer = self.renderer.compose_with_checkerboard(composite)
        if document.onion_skin_enabled:
            before = []
            after = []
            index = document.active_frame_index
            for offset in range(1, document.onion_skin_before + 1):
                target = index - offset
                if 0 <= target < len(document.frames):
                    before.append(document.frames[target].composite())
            for offset in range(1, document.onion_skin_after + 1):
                target = index + offset
                if 0 <= target < len(document.frames):
                    after.append(document.frames[target].composite())
            display_buffer = self.renderer.compose_with_onion_skin(composite, before, after)
        pil_image = Image.fromarray(display_buffer.data, mode="RGBA")
        if self.preview_points:
            overlay = Image.new("RGBA", pil_image.size, (0, 0, 0, 0))
            pixels = overlay.load()
            for point in self.preview_points:
                x, y, color = point
                if 0 <= x < overlay.width and 0 <= y < overlay.height:
                    pixels[x, y] = tuple(color)
            pil_image = Image.alpha_composite(pil_image, overlay)
        return pil_image

    def redraw(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        if canvas_width <= 1 or canvas_height <= 1:
            return
        document = self.app.document
        zoom = self.app.zoom
        pil_image = self._build_composite_image()
        target_width = max(1, round(document.width * zoom))
        target_height = max(1, round(document.height * zoom))
        scaled = pil_image.resize((target_width, target_height), Image.NEAREST)
        self._photo_image = ImageTk.PhotoImage(scaled)
        self.canvas.delete("all")
        self._image_item = self.canvas.create_image(self.offset_x, self.offset_y, anchor="nw", image=self._photo_image)
        self._draw_grid(zoom, target_width, target_height)
        self._draw_selection(zoom)
        self._draw_rulers(zoom)

    def _draw_grid(self, zoom, pixel_width, pixel_height):
        document = self.app.document
        if self.show_pixel_grid and zoom >= PIXEL_GRID_MIN_ZOOM:
            for x in range(document.width + 1):
                sx = self.offset_x + x * zoom
                self.canvas.create_line(sx, self.offset_y, sx, self.offset_y + pixel_height, fill=GRID_LINE_COLOR, width=1)
            for y in range(document.height + 1):
                sy = self.offset_y + y * zoom
                self.canvas.create_line(self.offset_x, sy, self.offset_x + pixel_width, sy, fill=GRID_LINE_COLOR, width=1)
        if self.show_grid and self.grid_size > 0:
            for x in range(0, document.width + 1, self.grid_size):
                sx = self.offset_x + x * zoom
                self.canvas.create_line(sx, self.offset_y, sx, self.offset_y + pixel_height, fill="#7fdcff", width=1, dash=(3, 2))
            for y in range(0, document.height + 1, self.grid_size):
                sy = self.offset_y + y * zoom
                self.canvas.create_line(self.offset_x, sy, self.offset_x + pixel_width, sy, fill="#7fdcff", width=1, dash=(3, 2))

    def _draw_selection(self, zoom):
        selection = self.app.document.selection
        if selection is None or selection.is_empty():
            return
        x0 = self.offset_x + selection.x * zoom
        y0 = self.offset_y + selection.y * zoom
        x1 = self.offset_x + (selection.x + selection.width) * zoom
        y1 = self.offset_y + (selection.y + selection.height) * zoom
        self.canvas.create_rectangle(x0, y0, x1, y1, outline=SELECTION_COLOR, width=1, dash=(4, 3))

    def _draw_rulers(self, zoom):
        self.top_ruler.delete("all")
        self.left_ruler.delete("all")
        document = self.app.document
        ruler_width = self.canvas.winfo_width()
        ruler_height = self.canvas.winfo_height()
        self.top_ruler.configure(width=ruler_width)
        self.left_ruler.configure(height=ruler_height)
        step = self._ruler_step(zoom)
        for x in range(0, document.width + 1, step):
            sx = self.offset_x + x * zoom
            self.top_ruler.create_line(sx, RULER_SIZE - 6, sx, RULER_SIZE, fill=RULER_TEXT_COLOR)
            self.top_ruler.create_text(sx + 2, 2, text=str(x), fill=RULER_TEXT_COLOR, anchor="nw", font=("TkDefaultFont", 7))
        for y in range(0, document.height + 1, step):
            sy = self.offset_y + y * zoom
            self.left_ruler.create_line(RULER_SIZE - 6, sy, RULER_SIZE, sy, fill=RULER_TEXT_COLOR)
            self.left_ruler.create_text(2, sy + 2, text=str(y), fill=RULER_TEXT_COLOR, anchor="nw", font=("TkDefaultFont", 7))

    def _ruler_step(self, zoom):
        if zoom >= 16:
            return 1
        if zoom >= 8:
            return 2
        if zoom >= 4:
            return 5
        if zoom >= 2:
            return 10
        return 20
