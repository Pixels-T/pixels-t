import json

from config.constants import APP_VERSION
from models.document import Document
from models.frame import Frame
from models.layer import Layer
from models.palette import Palette
from services.image_codec import buffer_to_base64, base64_to_buffer


def serialize_document(document):
    data = {
        "app_version": APP_VERSION,
        "name": document.name,
        "width": document.width,
        "height": document.height,
        "palette": document.palette.to_dict(),
        "active_frame_index": document.active_frame_index,
        "frames": [],
    }
    for frame in document.frames:
        frame_data = {
            "duration_ms": frame.duration_ms,
            "layers": [],
        }
        for layer in frame.layers:
            frame_data["layers"].append({
                "name": layer.name,
                "visible": layer.visible,
                "locked": layer.locked,
                "opacity": layer.opacity,
                "blend_mode": layer.blend_mode,
                "pixels": buffer_to_base64(layer.buffer),
            })
        data["frames"].append(frame_data)
    return data


def deserialize_document(data, event_bus=None):
    width = data["width"]
    height = data["height"]
    document = Document(width, height, name=data.get("name", "Untitled"), event_bus=event_bus)
    document.frames = []
    for frame_data in data["frames"]:
        frame = Frame(width, height, duration_ms=frame_data.get("duration_ms", 100), layers=[])
        for layer_data in frame_data["layers"]:
            layer = Layer(width, height, name=layer_data.get("name", "Layer"))
            layer.buffer = base64_to_buffer(layer_data["pixels"])
            layer.visible = layer_data.get("visible", True)
            layer.locked = layer_data.get("locked", False)
            layer.opacity = layer_data.get("opacity", 1.0)
            layer.blend_mode = layer_data.get("blend_mode", "normal")
            frame.layers.append(layer)
        document.frames.append(frame)
    if "palette" in data:
        document.palette = Palette.from_dict(data["palette"])
    document.active_frame_index = min(data.get("active_frame_index", 0), len(document.frames) - 1)
    if document.frames[document.active_frame_index].layers:
        document.active_layer_id = document.frames[document.active_frame_index].layers[0].id
    return document


def save_project(document, path):
    data = serialize_document(document)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle)
    document.filepath = path
    document.mark_clean()


def load_project(path, event_bus=None):
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)
    document = deserialize_document(data, event_bus=event_bus)
    document.filepath = path
    document.mark_clean()
    return document
