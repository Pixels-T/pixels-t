import time

from services.project_service import save_project, load_project


class AutosaveService:
    def __init__(self, settings):
        self.settings = settings
        self._last_saved_at = 0

    def _target_path(self, document):
        directory = self.settings.autosave_directory()
        identifier = document.filepath or document.name
        safe_name = "".join(char if char.isalnum() else "_" for char in str(identifier))
        return directory / f"{safe_name}.autosave.pxlst"

    def maybe_autosave(self, document, interval_seconds):
        if not self.settings.get("autosave_enabled", True):
            return False
        now = time.time()
        if now - self._last_saved_at < interval_seconds:
            return False
        if not document.dirty:
            return False
        path = self._target_path(document)
        original_path = document.filepath
        original_dirty = document.dirty
        save_project(document, str(path))
        document.filepath = original_path
        document.dirty = original_dirty
        self._last_saved_at = now
        return True

    def recover(self, document, event_bus=None):
        path = self._target_path(document)
        if path.exists():
            return load_project(str(path), event_bus=event_bus)
        return None

    def has_recovery(self, document):
        return self._target_path(document).exists()
