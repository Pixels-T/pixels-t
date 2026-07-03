class ClipboardService:
    def __init__(self):
        self._buffer = None

    def has_content(self):
        return self._buffer is not None

    def copy(self, pixel_buffer):
        self._buffer = pixel_buffer.clone()

    def get(self):
        if self._buffer is None:
            return None
        return self._buffer.clone()

    def clear(self):
        self._buffer = None
