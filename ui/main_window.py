import tkinter as tk
from tkinter import ttk, messagebox

import sv_ttk

from app.application import Application
from config.constants import APP_NAME, ZOOM_STEP_FACTOR, DEFAULT_ZOOM
from config.shortcuts import TOOL_SHORTCUTS
from core.events import DocumentEvents
from services import file_service, export_service
from ui.canvas_view import CanvasView
from ui.toolbar import Toolbar
from ui.tool_options_panel import ToolOptionsPanel
from ui.color_panel import ColorPanel
from ui.palette_panel import PalettePanel
from ui.layers_panel import LayersPanel
from ui.frames_panel import FramesPanel
from ui.status_bar import StatusBar
from ui.menu_bar import MenuBar
from ui.dialogs.new_project_dialog import NewProjectDialog
from ui.dialogs.resize_dialog import ResizeDialog
from ui.dialogs.export_dialog import ExportDialog
from ui.dialogs.preferences_dialog import PreferencesDialog
from ui.dialogs.replace_color_dialog import ReplaceColorDialog


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.app = Application()
        self.root.title(f"{APP_NAME} - {self.app.document.name}")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 640)

        sv_ttk.set_theme(self.app.settings.get("theme", "dark"))
        self._configure_styles()

        self.pixel_grid_var = tk.BooleanVar(value=self.app.settings.get("show_pixel_grid", True))
        self.grid_var = tk.BooleanVar(value=self.app.settings.get("show_grid", False))

        self.menu_bar = MenuBar(self.root, self)
        self.root.configure(menu=self.menu_bar)

        self._build_layout()
        self._wire_tool_context()
        self._bind_shortcuts()
        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)
        self._schedule_autosave()
        self.canvas_view.after(100, self.canvas_view.center_view)

    def _configure_styles(self):
        style = ttk.Style()
        try:
            style.configure("Selected.TFrame", background="#3a6ea5")
        except tk.TclError:
            pass

    def _build_layout(self):
        outer = ttk.Frame(self.root)
        outer.pack(fill="both", expand=True)

        self.toolbar = Toolbar(outer, self.app)
        self.toolbar.pack(side="left", fill="y")

        center = ttk.Frame(outer)
        center.pack(side="left", fill="both", expand=True)

        self.tool_options = ToolOptionsPanel(center, self.app)
        self.tool_options.pack(side="top", fill="x")

        self.canvas_view = CanvasView(center, self.app)
        self.canvas_view.pack(side="top", fill="both", expand=True)
        self.canvas_view.on_pointer_moved = self._on_pointer_moved

        bottom_container = ttk.Frame(center)
        bottom_container.pack(side="top", fill="x")
        self.status_bar = StatusBar(bottom_container, self.app)
        self.status_bar.pack(fill="x")

        side_panel = ttk.Frame(outer, width=260)
        side_panel.pack(side="right", fill="y")
        side_panel.pack_propagate(False)

        notebook = ttk.Notebook(side_panel)
        notebook.pack(fill="both", expand=True)

        color_tab = ttk.Frame(notebook)
        self.color_panel = ColorPanel(color_tab, self.app)
        self.color_panel.pack(fill="both", expand=True)
        self.palette_panel = PalettePanel(color_tab, self.app)
        self.palette_panel.pack(fill="both", expand=True)
        notebook.add(color_tab, text="Color")

        layers_tab = ttk.Frame(notebook)
        self.layers_panel = LayersPanel(layers_tab, self.app)
        self.layers_panel.pack(fill="both", expand=True)
        notebook.add(layers_tab, text="Layers")

        frames_tab = ttk.Frame(notebook)
        self.frames_panel = FramesPanel(frames_tab, self.app)
        self.frames_panel.pack(fill="both", expand=True)
        notebook.add(frames_tab, text="Frames")

        self.app.events.subscribe(DocumentEvents.LAYER_ADDED, lambda layer_id=None: self.palette_panel.refresh())

    def _wire_tool_context(self):
        context = self.app.tool_context
        context.request_redraw = self.canvas_view.redraw
        context.request_preview = self.canvas_view.set_preview
        context.clear_preview = self.canvas_view.clear_preview
        self.canvas_view.show_pixel_grid = self.pixel_grid_var.get()
        self.canvas_view.show_grid = self.grid_var.get()

    def _on_pointer_moved(self, x, y):
        self.status_bar.set_coordinates(x, y)

    def _bind_shortcuts(self):
        for key, tool_name in TOOL_SHORTCUTS.items():
            self.root.bind(f"<KeyPress-{key}>", lambda event, name=tool_name: self.app.tool_manager.set_active_tool(name))
        self.root.bind("<Control-n>", lambda event: self.on_new_project())
        self.root.bind("<Control-o>", lambda event: self.on_open_project())
        self.root.bind("<Control-s>", lambda event: self.on_save_project())
        self.root.bind("<Control-S>", lambda event: self.on_save_project_as())
        self.root.bind("<Control-e>", lambda event: self.on_export_dialog())
        self.root.bind("<Control-z>", lambda event: self.on_undo())
        self.root.bind("<Control-y>", lambda event: self.on_redo())
        self.root.bind("<Control-Z>", lambda event: self.on_redo())
        self.root.bind("<Control-c>", lambda event: self.on_copy())
        self.root.bind("<Control-x>", lambda event: self.on_cut())
        self.root.bind("<Control-v>", lambda event: self.on_paste())
        self.root.bind("<Control-a>", lambda event: self.on_select_all())
        self.root.bind("<Escape>", lambda event: self.on_deselect())
        self.root.bind("<Control-plus>", lambda event: self.on_zoom_in())
        self.root.bind("<Control-equal>", lambda event: self.on_zoom_in())
        self.root.bind("<Control-minus>", lambda event: self.on_zoom_out())
        self.root.bind("<Control-0>", lambda event: self.on_zoom_reset())
        self.root.bind("<Control-h>", lambda event: self.on_flip_horizontal())
        self.root.bind("<Control-H>", lambda event: self.on_flip_vertical())
        self.root.bind("<Control-N>", lambda event: self.on_new_layer())
        self.root.bind("<Control-Delete>", lambda event: self.on_delete_layer())
        self.root.bind("<KeyPress-space>", lambda event: self.canvas_view.set_space_held(True))
        self.root.bind("<KeyRelease-space>", lambda event: self.canvas_view.set_space_held(False))
        self.root.bind("<Control-bracketright>", lambda event: self._change_brush_size(1))
        self.root.bind("<Control-bracketleft>", lambda event: self._change_brush_size(-1))

    def _change_brush_size(self, delta):
        current = self.app.tool_context.brush_size
        self.app.tool_context.brush_size = max(1, min(32, current + delta))
        self.tool_options.brush_size_var.set(self.app.tool_context.brush_size)

    def _schedule_autosave(self):
        from config.constants import AUTOSAVE_INTERVAL_MS
        self.app.autosave.maybe_autosave(self.app.document, AUTOSAVE_INTERVAL_MS / 1000.0)
        self.root.after(AUTOSAVE_INTERVAL_MS, self._schedule_autosave)

    def on_new_project(self):
        dialog = NewProjectDialog(self.root)
        if dialog.result is None:
            return
        name, width, height = dialog.result
        self.app.new_document(width, height, name=name)
        self.root.title(f"{APP_NAME} - {name}")
        self._refresh_all_panels()

    def on_open_project(self):
        path = file_service.ask_open_project_path()
        if not path:
            return
        try:
            self.app.open_document(path)
        except (OSError, ValueError, KeyError) as error:
            messagebox.showerror("Open Failed", str(error))
            return
        self.root.title(f"{APP_NAME} - {self.app.document.name}")
        self._refresh_all_panels()

    def on_save_project(self):
        if self.app.document.filepath:
            self.app.save_document(self.app.document.filepath)
            self.status_bar.refresh()
        else:
            self.on_save_project_as()

    def on_save_project_as(self):
        path = file_service.ask_save_project_path(self.app.document.name)
        if not path:
            return
        self.app.save_document(path)
        self.root.title(f"{APP_NAME} - {self.app.document.name}")
        self.status_bar.refresh()

    def on_export_dialog(self):
        dialog = ExportDialog(self.root, len(self.app.document.frames))
        if dialog.result is None:
            return
        export_format, scale = dialog.result
        document = self.app.document
        try:
            if export_format == "png":
                path = file_service.ask_export_png_path(document.name)
                if path:
                    export_service.export_png(document, path, scale=scale)
            elif export_format == "png_sprite_sheet":
                path = file_service.ask_export_png_path(document.name + "_sheet")
                if path:
                    export_service.export_sprite_sheet(document, path, scale=scale)
            elif export_format == "gif":
                path = file_service.ask_export_gif_path(document.name)
                if path:
                    export_service.export_gif(document, path, scale=scale)
            elif export_format == "png_sequence":
                directory = file_service.ask_export_directory()
                if directory:
                    export_service.export_all_frames(document, directory, prefix=document.name, scale=scale)
        except OSError as error:
            messagebox.showerror("Export Failed", str(error))

    def on_exit(self):
        if self.app.document.dirty:
            answer = messagebox.askyesnocancel("Unsaved Changes", "Save changes before exiting?")
            if answer is None:
                return
            if answer:
                self.on_save_project()
                if self.app.document.dirty:
                    return
        self.app.shutdown()
        self.root.destroy()

    def on_undo(self):
        self.app.undo()

    def on_redo(self):
        self.app.redo()

    def on_cut(self):
        self.app.cut_selection()

    def on_copy(self):
        self.app.copy_selection()

    def on_paste(self):
        self.app.paste_clipboard()

    def on_delete_selection(self):
        self.app.delete_selection_content()

    def on_select_all(self):
        from core.geometry import Rect
        self.app.document.set_selection(Rect(0, 0, self.app.document.width, self.app.document.height))

    def on_deselect(self):
        self.app.document.clear_selection()
        self.app.tool_manager.active_tool.cancel()

    def on_preferences(self):
        PreferencesDialog(self.root, self.app.settings)

    def on_resize_canvas(self):
        document = self.app.document
        dialog = ResizeDialog(self.root, document.width, document.height)
        if dialog.result is None:
            return
        new_width, new_height, anchor_x, anchor_y = dialog.result
        self.app.resize_canvas(new_width, new_height, anchor_x, anchor_y)
        self.canvas_view.center_view()

    def on_flip_horizontal(self):
        self.app.flip_layer_horizontal(self.app.document.active_layer_id)

    def on_flip_vertical(self):
        self.app.flip_layer_vertical(self.app.document.active_layer_id)

    def on_rotate_layer(self, clockwise):
        self.app.rotate_layer(self.app.document.active_layer_id, clockwise)

    def on_replace_color(self):
        current_color = self.app.tool_context.primary_color
        dialog = ReplaceColorDialog(self.root, current_color)
        if dialog.result is None:
            return
        old_color, new_color, tolerance = dialog.result
        self.app.replace_color(old_color, new_color, tolerance)

    def on_new_layer(self):
        self.app.add_layer()

    def on_duplicate_layer(self):
        self.app.duplicate_layer(self.app.document.active_layer_id)

    def on_delete_layer(self):
        self.app.remove_layer(self.app.document.active_layer_id)

    def on_merge_down(self):
        self.app.merge_layer_down(self.app.document.active_layer_id)

    def on_delete_frame(self):
        self.app.remove_frame(self.app.document.active_frame_index)

    def on_zoom_in(self):
        self.app.set_zoom(self.app.zoom * ZOOM_STEP_FACTOR)

    def on_zoom_out(self):
        self.app.set_zoom(self.app.zoom / ZOOM_STEP_FACTOR)

    def on_zoom_reset(self):
        self.app.set_zoom(DEFAULT_ZOOM)
        self.canvas_view.center_view()

    def on_toggle_pixel_grid(self):
        self.canvas_view.show_pixel_grid = self.pixel_grid_var.get()
        self.app.settings.set("show_pixel_grid", self.pixel_grid_var.get())
        self.canvas_view.redraw()

    def on_toggle_grid(self):
        self.canvas_view.show_grid = self.grid_var.get()
        self.app.settings.set("show_grid", self.grid_var.get())
        self.canvas_view.redraw()

    def _refresh_all_panels(self):
        self.layers_panel.refresh()
        self.frames_panel.refresh()
        self.color_panel.refresh()
        self.palette_panel.refresh()
        self.status_bar.refresh()
        self.canvas_view.center_view()
