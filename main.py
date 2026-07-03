import sys
import tkinter as tk
from tkinter import messagebox

from ui.main_window import MainWindow


def main():
    root = tk.Tk()
    try:
        root.tk.call("tk", "scaling", root.winfo_fpixels("1i") / 72.0)
    except tk.TclError:
        pass
    try:
        MainWindow(root)
    except Exception as error:
        messagebox.showerror("Startup Error", str(error))
        raise
    root.mainloop()


if __name__ == "__main__":
    sys.exit(main() or 0)
