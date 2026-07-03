from config.constants import (
    TOOL_PENCIL, TOOL_ERASER, TOOL_BUCKET, TOOL_LINE, TOOL_RECTANGLE,
    TOOL_ELLIPSE, TOOL_EYEDROPPER, TOOL_SELECTION, TOOL_MOVE,
    TOOL_GRADIENT, TOOL_SPRAY,
)

TOOL_SHORTCUTS = {
    "p": TOOL_PENCIL,
    "e": TOOL_ERASER,
    "b": TOOL_BUCKET,
    "l": TOOL_LINE,
    "r": TOOL_RECTANGLE,
    "o": TOOL_ELLIPSE,
    "i": TOOL_EYEDROPPER,
    "m": TOOL_SELECTION,
    "v": TOOL_MOVE,
    "g": TOOL_GRADIENT,
    "s": TOOL_SPRAY,
}

ACTION_SHORTCUTS = {
    "new_project": "<Control-n>",
    "open_project": "<Control-o>",
    "save_project": "<Control-s>",
    "save_project_as": "<Control-Shift-S>",
    "export_png": "<Control-e>",
    "undo": "<Control-z>",
    "redo": "<Control-y>",
    "redo_alt": "<Control-Shift-Z>",
    "copy": "<Control-c>",
    "paste": "<Control-v>",
    "cut": "<Control-x>",
    "select_all": "<Control-a>",
    "deselect": "<Escape>",
    "zoom_in": "<Control-plus>",
    "zoom_out": "<Control-minus>",
    "zoom_reset": "<Control-0>",
    "toggle_grid": "<Control-g>",
    "new_layer": "<Control-Shift-N>",
    "delete_layer": "<Control-Delete>",
    "new_frame": "<Control-F>",
    "flip_horizontal": "<Control-h>",
    "flip_vertical": "<Control-Shift-H>",
}
