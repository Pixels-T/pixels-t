import tkinter as tk
from tkinter import messagebox

from config.shortcuts import ACTION_SHORTCUTS


class MenuBar(tk.Menu):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label="New Project...", command=controller.on_new_project, accelerator="Ctrl+N")
        file_menu.add_command(label="Open Project...", command=controller.on_open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Project", command=controller.on_save_project, accelerator="Ctrl+S")
        file_menu.add_command(label="Save Project As...", command=controller.on_save_project_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export PNG...", command=controller.on_export_dialog, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=controller.on_exit)
        self.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(self, tearoff=False)
        edit_menu.add_command(label="Undo", command=controller.on_undo, accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=controller.on_redo, accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Cut", command=controller.on_cut, accelerator="Ctrl+X")
        edit_menu.add_command(label="Copy", command=controller.on_copy, accelerator="Ctrl+C")
        edit_menu.add_command(label="Paste", command=controller.on_paste, accelerator="Ctrl+V")
        edit_menu.add_command(label="Delete", command=controller.on_delete_selection)
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", command=controller.on_select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Deselect", command=controller.on_deselect, accelerator="Esc")
        edit_menu.add_separator()
        edit_menu.add_command(label="Preferences...", command=controller.on_preferences)
        self.add_cascade(label="Edit", menu=edit_menu)

        image_menu = tk.Menu(self, tearoff=False)
        image_menu.add_command(label="Resize Canvas...", command=controller.on_resize_canvas)
        image_menu.add_command(label="Flip Layer Horizontal", command=controller.on_flip_horizontal, accelerator="Ctrl+H")
        image_menu.add_command(label="Flip Layer Vertical", command=controller.on_flip_vertical, accelerator="Ctrl+Shift+H")
        image_menu.add_command(label="Rotate Layer 90 CW", command=lambda: controller.on_rotate_layer(True))
        image_menu.add_command(label="Rotate Layer 90 CCW", command=lambda: controller.on_rotate_layer(False))
        image_menu.add_command(label="Replace Color...", command=controller.on_replace_color)
        self.add_cascade(label="Image", menu=image_menu)

        layer_menu = tk.Menu(self, tearoff=False)
        layer_menu.add_command(label="New Layer", command=controller.on_new_layer, accelerator="Ctrl+Shift+N")
        layer_menu.add_command(label="Duplicate Layer", command=controller.on_duplicate_layer)
        layer_menu.add_command(label="Delete Layer", command=controller.on_delete_layer, accelerator="Ctrl+Delete")
        layer_menu.add_command(label="Merge Down", command=controller.on_merge_down)
        self.add_cascade(label="Layer", menu=layer_menu)

        frame_menu = tk.Menu(self, tearoff=False)
        frame_menu.add_command(label="New Frame", command=lambda: controller.app.add_frame(copy_active=False), accelerator="Ctrl+F")
        frame_menu.add_command(label="Duplicate Frame", command=lambda: controller.app.add_frame(copy_active=True))
        frame_menu.add_command(label="Delete Frame", command=controller.on_delete_frame)
        self.add_cascade(label="Frame", menu=frame_menu)

        view_menu = tk.Menu(self, tearoff=False)
        view_menu.add_command(label="Zoom In", command=controller.on_zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=controller.on_zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Reset Zoom", command=controller.on_zoom_reset, accelerator="Ctrl+0")
        view_menu.add_separator()
        view_menu.add_checkbutton(label="Pixel Grid", variable=controller.pixel_grid_var, command=controller.on_toggle_pixel_grid)
        view_menu.add_checkbutton(label="Custom Grid", variable=controller.grid_var, command=controller.on_toggle_grid)
        self.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label="About", command=self._show_about)
        self.add_cascade(label="Help", menu=help_menu)

    def _show_about(self):
        from config.constants import APP_NAME, APP_VERSION
        messagebox.showinfo("About", f"{APP_NAME} {APP_VERSION}\nA lightweight pixel art editor.")
