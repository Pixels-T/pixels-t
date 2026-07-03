from PIL import Image, ImageTk

from rendering.checkerboard import generate_checkerboard


class CanvasRenderer:
    def __init__(self):
        self._last_photo = None

    def compose_with_checkerboard(self, pixel_buffer):
        checker = generate_checkerboard(pixel_buffer.width, pixel_buffer.height)
        checker.paste(pixel_buffer, 0, 0)
        return checker

    def compose_with_onion_skin(self, pixel_buffer, before_buffers, after_buffers):
        checker = generate_checkerboard(pixel_buffer.width, pixel_buffer.height)
        for buffer in before_buffers:
            tinted = self._tint(buffer, (255, 0, 0), 0.25)
            checker.paste(tinted, 0, 0)
        for buffer in after_buffers:
            tinted = self._tint(buffer, (0, 120, 255), 0.25)
            checker.paste(tinted, 0, 0)
        checker.paste(pixel_buffer, 0, 0)
        return checker

    def _tint(self, buffer, rgb, strength):
        import numpy as np
        clone = buffer.clone()
        alpha = clone.data[:, :, 3:4].astype(np.float32) / 255.0
        tint_color = np.array(rgb, dtype=np.float32)
        rgb_data = clone.data[:, :, :3].astype(np.float32)
        blended = rgb_data * (1 - strength) + tint_color * strength
        clone.data[:, :, :3] = blended.astype(np.uint8)
        clone.data[:, :, 3:4] = (alpha * strength * 255.0).astype(np.uint8)
        return clone

    def render_photo_image(self, pixel_buffer, zoom):
        pil_image = Image.fromarray(pixel_buffer.data, mode="RGBA")
        target_width = max(1, round(pixel_buffer.width * zoom))
        target_height = max(1, round(pixel_buffer.height * zoom))
        scaled = pil_image.resize((target_width, target_height), Image.NEAREST)
        photo = ImageTk.PhotoImage(scaled)
        self._last_photo = photo
        return photo
