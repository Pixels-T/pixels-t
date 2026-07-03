import numpy as np

from config.constants import CHECKER_LIGHT, CHECKER_DARK, CHECKER_CELL_SIZE
from models.pixel_buffer import PixelBuffer

_cache = {}


def generate_checkerboard(width, height, cell_size=CHECKER_CELL_SIZE):
    key = (width, height, cell_size)
    if key in _cache:
        return _cache[key].clone()
    ys, xs = np.mgrid[0:height, 0:width]
    checker = ((xs // cell_size) + (ys // cell_size)) % 2 == 0
    data = np.zeros((height, width, 4), dtype=np.uint8)
    data[checker] = CHECKER_LIGHT
    data[~checker] = CHECKER_DARK
    buffer = PixelBuffer.from_array(data)
    _cache[key] = buffer
    return buffer.clone()
