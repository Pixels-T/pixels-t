import math

from PIL import Image

from services.image_codec import buffer_to_pil


def export_png(document, path, frame_index=None, scale=1):
    index = frame_index if frame_index is not None else document.active_frame_index
    composite = document.frames[index].composite()
    image = buffer_to_pil(composite)
    if scale != 1:
        image = image.resize((image.width * scale, image.height * scale), Image.NEAREST)
    image.save(path, format="PNG")


def export_sprite_sheet(document, path, columns=None, scale=1):
    frame_count = len(document.frames)
    if columns is None:
        columns = math.ceil(math.sqrt(frame_count))
    rows = math.ceil(frame_count / columns)
    cell_width = document.width * scale
    cell_height = document.height * scale
    sheet = Image.new("RGBA", (cell_width * columns, cell_height * rows), (0, 0, 0, 0))
    for index, frame in enumerate(document.frames):
        composite = frame.composite()
        image = buffer_to_pil(composite)
        if scale != 1:
            image = image.resize((cell_width, cell_height), Image.NEAREST)
        col = index % columns
        row = index // columns
        sheet.paste(image, (col * cell_width, row * cell_height), image)
    sheet.save(path, format="PNG")
    return columns, rows


def export_gif(document, path, scale=1, loop=0):
    images = []
    durations = []
    for frame in document.frames:
        composite = frame.composite()
        image = buffer_to_pil(composite)
        if scale != 1:
            image = image.resize((image.width * scale, image.height * scale), Image.NEAREST)
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        background.paste(image, (0, 0), image)
        images.append(background.convert("RGB"))
        durations.append(max(frame.duration_ms, 20))
    if not images:
        return
    images[0].save(
        path,
        format="GIF",
        save_all=True,
        append_images=images[1:],
        duration=durations,
        loop=loop,
        disposal=2,
    )


def export_all_frames(document, directory, prefix="frame", scale=1):
    import os
    os.makedirs(directory, exist_ok=True)
    paths = []
    for index in range(len(document.frames)):
        path = os.path.join(directory, f"{prefix}_{index:03d}.png")
        export_png(document, path, frame_index=index, scale=scale)
        paths.append(path)
    return paths
