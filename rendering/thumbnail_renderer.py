from PIL import Image, ImageTk

from config.constants import THUMBNAIL_SIZE
from rendering.checkerboard import generate_checkerboard


def render_thumbnail(pixel_buffer, size=THUMBNAIL_SIZE):
    checker = generate_checkerboard(pixel_buffer.width, pixel_buffer.height, cell_size=max(2, pixel_buffer.width // 8 or 2))
    checker.paste(pixel_buffer, 0, 0)
    pil_image = Image.fromarray(checker.data, mode="RGBA")
    scale = min(size / pixel_buffer.width, size / pixel_buffer.height)
    target_width = max(1, round(pixel_buffer.width * scale))
    target_height = max(1, round(pixel_buffer.height * scale))
    resample = Image.NEAREST if scale >= 1 else Image.BOX
    scaled = pil_image.resize((target_width, target_height), resample)
    canvas_image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    paste_x = (size - target_width) // 2
    paste_y = (size - target_height) // 2
    canvas_image.paste(scaled, (paste_x, paste_y))
    return ImageTk.PhotoImage(canvas_image)
