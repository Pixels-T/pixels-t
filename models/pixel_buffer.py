import numpy as np

from core.geometry import Rect


class PixelBuffer:
    def __init__(self, width, height, fill_color=(0, 0, 0, 0)):
        self.width = width
        self.height = height
        self.data = np.zeros((height, width, 4), dtype=np.uint8)
        if fill_color != (0, 0, 0, 0):
            self.data[:, :] = fill_color

    @staticmethod
    def from_array(array):
        buffer = PixelBuffer(array.shape[1], array.shape[0])
        buffer.data = array.copy()
        return buffer

    def clone(self):
        return PixelBuffer.from_array(self.data)

    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_pixel(self, x, y):
        if not self.in_bounds(x, y):
            return (0, 0, 0, 0)
        pixel = self.data[y, x]
        return (int(pixel[0]), int(pixel[1]), int(pixel[2]), int(pixel[3]))

    def set_pixel(self, x, y, rgba):
        if not self.in_bounds(x, y):
            return
        self.data[y, x] = rgba

    def set_pixels(self, points, rgba):
        for x, y in points:
            self.set_pixel(x, y, rgba)

    def clear(self):
        self.data[:, :] = (0, 0, 0, 0)

    def fill(self, rgba):
        self.data[:, :] = rgba

    def clear_region(self, rect):
        clamped = rect.clamped(self.width, self.height)
        if clamped.is_empty():
            return
        self.data[clamped.y:clamped.y + clamped.height, clamped.x:clamped.x + clamped.width] = (0, 0, 0, 0)

    def paste(self, other, x, y):
        source_rect = Rect(0, 0, other.width, other.height)
        target_left = max(0, x)
        target_top = max(0, y)
        target_right = min(self.width, x + other.width)
        target_bottom = min(self.height, y + other.height)
        if target_right <= target_left or target_bottom <= target_top:
            return
        source_left = target_left - x
        source_top = target_top - y
        source_right = source_left + (target_right - target_left)
        source_bottom = source_top + (target_bottom - target_top)
        source_slice = other.data[source_top:source_bottom, source_left:source_right]
        source_alpha = source_slice[:, :, 3:4].astype(np.float32) / 255.0
        destination_slice = self.data[target_top:target_bottom, target_left:target_right]
        blended = source_slice.astype(np.float32) * source_alpha + destination_slice.astype(np.float32) * (1 - source_alpha)
        self.data[target_top:target_bottom, target_left:target_right] = blended.astype(np.uint8)

    def replace_paste(self, other, x, y):
        target_left = max(0, x)
        target_top = max(0, y)
        target_right = min(self.width, x + other.width)
        target_bottom = min(self.height, y + other.height)
        if target_right <= target_left or target_bottom <= target_top:
            return
        source_left = target_left - x
        source_top = target_top - y
        source_right = source_left + (target_right - target_left)
        source_bottom = source_top + (target_bottom - target_top)
        self.data[target_top:target_bottom, target_left:target_right] = other.data[source_top:source_bottom, source_left:source_right]

    def extract_region(self, rect):
        clamped = rect.clamped(self.width, self.height)
        sub = PixelBuffer(max(1, clamped.width), max(1, clamped.height))
        if not clamped.is_empty():
            sub.data[:clamped.height, :clamped.width] = self.data[clamped.y:clamped.y + clamped.height, clamped.x:clamped.x + clamped.width]
        return sub

    def resized_canvas(self, new_width, new_height, anchor_x=0, anchor_y=0):
        result = PixelBuffer(new_width, new_height)
        result.paste_replace_full(self, anchor_x, anchor_y)
        return result

    def paste_replace_full(self, other, x, y):
        target_left = max(0, x)
        target_top = max(0, y)
        target_right = min(self.width, x + other.width)
        target_bottom = min(self.height, y + other.height)
        if target_right <= target_left or target_bottom <= target_top:
            return
        source_left = target_left - x
        source_top = target_top - y
        source_right = source_left + (target_right - target_left)
        source_bottom = source_top + (target_bottom - target_top)
        self.data[target_top:target_bottom, target_left:target_right] = other.data[source_top:source_bottom, source_left:source_right]

    def scaled(self, new_width, new_height):
        y_indices = (np.arange(new_height) * self.height / new_height).astype(np.int32)
        x_indices = (np.arange(new_width) * self.width / new_width).astype(np.int32)
        y_indices = np.clip(y_indices, 0, self.height - 1)
        x_indices = np.clip(x_indices, 0, self.width - 1)
        scaled_data = self.data[y_indices[:, None], x_indices[None, :]]
        return PixelBuffer.from_array(scaled_data)

    def flipped_horizontal(self):
        return PixelBuffer.from_array(np.fliplr(self.data))

    def flipped_vertical(self):
        return PixelBuffer.from_array(np.flipud(self.data))

    def rotated_90(self, clockwise=True):
        if clockwise:
            return PixelBuffer.from_array(np.rot90(self.data, k=-1))
        return PixelBuffer.from_array(np.rot90(self.data, k=1))

    def flood_fill(self, start_x, start_y, new_rgba, tolerance=0):
        if not self.in_bounds(start_x, start_y):
            return Rect(0, 0, 0, 0)
        target = self.data[start_y, start_x].astype(np.int32)
        if tuple(int(v) for v in target) == tuple(new_rgba):
            return Rect(0, 0, 0, 0)
        visited = np.zeros((self.height, self.width), dtype=bool)
        stack = [(start_x, start_y)]
        min_x, min_y = start_x, start_y
        max_x, max_y = start_x, start_y
        diff = np.abs(self.data.astype(np.int32) - target.reshape(1, 1, 4)).sum(axis=2)
        matches = diff <= tolerance
        while stack:
            x, y = stack.pop()
            if x < 0 or x >= self.width or y < 0 or y >= self.height:
                continue
            if visited[y, x] or not matches[y, x]:
                continue
            visited[y, x] = True
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x)
            max_y = max(max_y, y)
            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))
        self.data[visited] = new_rgba
        return Rect(min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    def is_empty_at(self, x, y):
        if not self.in_bounds(x, y):
            return True
        return self.data[y, x, 3] == 0

    def bounding_box_of_content(self):
        alpha = self.data[:, :, 3]
        nonzero_rows = np.any(alpha > 0, axis=1)
        nonzero_cols = np.any(alpha > 0, axis=0)
        if not nonzero_rows.any():
            return Rect(0, 0, 0, 0)
        top = int(np.argmax(nonzero_rows))
        bottom = int(len(nonzero_rows) - 1 - np.argmax(nonzero_rows[::-1]))
        left = int(np.argmax(nonzero_cols))
        right = int(len(nonzero_cols) - 1 - np.argmax(nonzero_cols[::-1]))
        return Rect(left, top, right - left + 1, bottom - top + 1)
