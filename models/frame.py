import itertools

import numpy as np

from config.constants import (
    DEFAULT_FRAME_DURATION_MS,
    BLEND_MODE_NORMAL,
    BLEND_MODE_MULTIPLY,
    BLEND_MODE_SCREEN,
    BLEND_MODE_ADDITIVE,
)
from models.layer import Layer
from models.pixel_buffer import PixelBuffer

_frame_id_counter = itertools.count(1)


def _apply_blend(base_rgb, top_rgb, mode):
    base = base_rgb.astype(np.float32) / 255.0
    top = top_rgb.astype(np.float32) / 255.0
    if mode == BLEND_MODE_MULTIPLY:
        result = base * top
    elif mode == BLEND_MODE_SCREEN:
        result = 1.0 - (1.0 - base) * (1.0 - top)
    elif mode == BLEND_MODE_ADDITIVE:
        result = np.clip(base + top, 0.0, 1.0)
    else:
        result = top
    return np.clip(result * 255.0, 0, 255).astype(np.uint8)


class Frame:
    def __init__(self, width, height, duration_ms=DEFAULT_FRAME_DURATION_MS, layers=None):
        self.id = next(_frame_id_counter)
        self.width = width
        self.height = height
        self.duration_ms = duration_ms
        self.layers = layers if layers is not None else [Layer(width, height, name="Layer 1")]

    def clone(self):
        clone = Frame(self.width, self.height, duration_ms=self.duration_ms, layers=[layer.clone() for layer in self.layers])
        return clone

    def composite(self):
        result = PixelBuffer(self.width, self.height)
        for layer in self.layers:
            if not layer.visible or layer.opacity <= 0.0:
                continue
            source = layer.buffer.data.astype(np.float32)
            source_alpha = (source[:, :, 3:4] / 255.0) * layer.opacity
            base_rgb = result.data[:, :, :3]
            blended_rgb = _apply_blend(base_rgb, source[:, :, :3].astype(np.uint8), layer.blend_mode).astype(np.float32)
            base_alpha = result.data[:, :, 3:4].astype(np.float32) / 255.0
            out_alpha = source_alpha + base_alpha * (1 - source_alpha)
            safe_out_alpha = np.where(out_alpha <= 0, 1.0, out_alpha)
            out_rgb = (blended_rgb * source_alpha + base_rgb.astype(np.float32) * base_alpha * (1 - source_alpha)) / safe_out_alpha
            result.data[:, :, :3] = np.clip(out_rgb, 0, 255).astype(np.uint8)
            result.data[:, :, 3:4] = np.clip(out_alpha * 255.0, 0, 255).astype(np.uint8)
        return result

    def add_layer(self, name=None, index=None):
        layer = Layer(self.width, self.height, name=name)
        if index is None:
            self.layers.append(layer)
        else:
            self.layers.insert(index, layer)
        return layer

    def remove_layer(self, layer_id):
        self.layers = [layer for layer in self.layers if layer.id != layer_id]

    def find_layer_index(self, layer_id):
        for index, layer in enumerate(self.layers):
            if layer.id == layer_id:
                return index
        return -1

    def resize(self, new_width, new_height, anchor_x=0, anchor_y=0):
        for layer in self.layers:
            layer.buffer = layer.buffer.resized_canvas(new_width, new_height, anchor_x, anchor_y)
        self.width = new_width
        self.height = new_height
