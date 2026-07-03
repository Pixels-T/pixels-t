import base64
import io

from PIL import Image

from models.pixel_buffer import PixelBuffer


def buffer_to_pil(buffer):
    return Image.fromarray(buffer.data, mode="RGBA")


def pil_to_buffer(image):
    converted = image.convert("RGBA")
    return PixelBuffer.from_array(_image_to_array(converted))


def _image_to_array(image):
    import numpy as np
    return np.array(image, dtype=np.uint8)


def buffer_to_png_bytes(buffer):
    stream = io.BytesIO()
    buffer_to_pil(buffer).save(stream, format="PNG")
    return stream.getvalue()


def png_bytes_to_buffer(data):
    stream = io.BytesIO(data)
    image = Image.open(stream)
    return pil_to_buffer(image)


def buffer_to_base64(buffer):
    return base64.b64encode(buffer_to_png_bytes(buffer)).decode("ascii")


def base64_to_buffer(text):
    return png_bytes_to_buffer(base64.b64decode(text))
