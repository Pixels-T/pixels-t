from tkinter import filedialog

from config.constants import PROJECT_FILE_EXTENSION


def ask_open_project_path():
    return filedialog.askopenfilename(
        title="Open Project",
        filetypes=[("Pixels-T Project", f"*{PROJECT_FILE_EXTENSION}"), ("All Files", "*.*")],
        defaultextension=PROJECT_FILE_EXTENSION,
    )


def ask_save_project_path(initial_name="Untitled"):
    return filedialog.asksaveasfilename(
        title="Save Project",
        initialfile=initial_name + PROJECT_FILE_EXTENSION,
        filetypes=[("Pixels-T Project", f"*{PROJECT_FILE_EXTENSION}")],
        defaultextension=PROJECT_FILE_EXTENSION,
    )


def ask_export_png_path(initial_name="sprite"):
    return filedialog.asksaveasfilename(
        title="Export PNG",
        initialfile=initial_name + ".png",
        filetypes=[("PNG Image", "*.png")],
        defaultextension=".png",
    )


def ask_export_gif_path(initial_name="animation"):
    return filedialog.asksaveasfilename(
        title="Export GIF",
        initialfile=initial_name + ".gif",
        filetypes=[("GIF Image", "*.gif")],
        defaultextension=".gif",
    )


def ask_export_directory():
    return filedialog.askdirectory(title="Choose Export Folder")
