import itertools

from config.constants import BLEND_MODE_NORMAL
from models.pixel_buffer import PixelBuffer

_layer_id_counter = itertools.count(1)


class Layer:
    def __init__(self, width, height, name=None):
        self.id = next(_layer_id_counter)
        self.name = name or f"Layer {self.id}"
        self.buffer = PixelBuffer(width, height)
        self.visible = True
        self.locked = False
        self.opacity = 1.0
        self.blend_mode = BLEND_MODE_NORMAL

    def clone(self):
        clone = Layer(self.buffer.width, self.buffer.height, name=self.name)
        clone.buffer = self.buffer.clone()
        clone.visible = self.visible
        clone.locked = self.locked
        clone.opacity = self.opacity
        clone.blend_mode = self.blend_mode
        return clone

    @property
    def width(self):
        return self.buffer.width

    @property
    def height(self):
        return self.buffer.height
