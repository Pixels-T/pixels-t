import tkinter as tk
from tkinter import ttk

import sv_ttk


class PreferencesDialog(tk.Toplevel):
    def __init__(self, parent, settings):
        super().__init__(parent)
        self.title("Preferences")
        self.resizable(False, False)
        self.settings = settings
        self.transient(parent)
        self.grab_set()

        form = ttk.Frame(self, padding=16)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Theme").grid(row=0, column=0, sticky="w", pady=4)
        self.theme_var = tk.StringVar(value=settings.get("theme", "dark"))
        theme_combo = ttk.Combobox(form, textvariable=self.theme_var, state="readonly", values=["dark", "light"], width=10)
        theme_combo.grid(row=0, column=1, pady=4)
        theme_combo.bind("<<ComboboxSelected>>", self._on_theme_changed)

        self.autosave_var = tk.BooleanVar(value=settings.get("autosave_enabled", True))
        ttk.Checkbutton(form, text="Enable Autosave", variable=self.autosave_var, command=self._on_autosave_changed).grid(row=1, column=0, columnspan=2, sticky="w", pady=4)

        ttk.Button(form, text="Close", command=self.destroy).grid(row=2, column=0, columnspan=2, pady=(12, 0), sticky="e")

        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def _on_theme_changed(self, event=None):
        theme = self.theme_var.get()
        sv_ttk.set_theme(theme)
        self.settings.set("theme", theme)
        self.settings.save()

    def _on_autosave_changed(self):
        self.settings.set("autosave_enabled", self.autosave_var.get())
        self.settings.save()
