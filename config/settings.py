import json
import os
from pathlib import Path

from config.constants import APP_NAME, DEFAULT_ZOOM


class Settings:
    def __init__(self):
        self._config_dir = Path.home() / f".{APP_NAME.lower()}"
        self._config_file = self._config_dir / "settings.json"
        self._data = {
            "theme": "dark",
            "last_zoom": DEFAULT_ZOOM,
            "show_pixel_grid": True,
            "show_grid": False,
            "grid_size": 8,
            "pixel_perfect": True,
            "symmetry_horizontal": False,
            "symmetry_vertical": False,
            "recent_projects": [],
            "recent_colors": [],
            "favorite_colors": [],
            "autosave_enabled": True,
            "window_geometry": None,
        }
        self._load()

    def _load(self):
        if self._config_file.exists():
            try:
                with open(self._config_file, "r", encoding="utf-8") as handle:
                    loaded = json.load(handle)
                self._data.update(loaded)
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        try:
            self._config_dir.mkdir(parents=True, exist_ok=True)
            with open(self._config_file, "w", encoding="utf-8") as handle:
                json.dump(self._data, handle, indent=2)
        except OSError:
            pass

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value

    def add_recent_project(self, path):
        recents = self._data.get("recent_projects", [])
        path_str = str(path)
        if path_str in recents:
            recents.remove(path_str)
        recents.insert(0, path_str)
        self._data["recent_projects"] = recents[:10]

    def add_recent_color(self, hex_color):
        recents = self._data.get("recent_colors", [])
        if hex_color in recents:
            recents.remove(hex_color)
        recents.insert(0, hex_color)
        self._data["recent_colors"] = recents[:16]

    def toggle_favorite_color(self, hex_color):
        favorites = self._data.get("favorite_colors", [])
        if hex_color in favorites:
            favorites.remove(hex_color)
        else:
            favorites.append(hex_color)
        self._data["favorite_colors"] = favorites

    def autosave_directory(self):
        directory = self._config_dir / "autosave"
        directory.mkdir(parents=True, exist_ok=True)
        return directory
