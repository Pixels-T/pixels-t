from config.constants import DEFAULT_PALETTE
from core.color import Color


class Palette:
    def __init__(self, name="Default", colors=None):
        self.name = name
        self.colors = colors if colors is not None else [Color.from_hex(value) for value in DEFAULT_PALETTE]

    def add_color(self, color):
        if color.to_hex() not in [c.to_hex() for c in self.colors]:
            self.colors.append(color)

    def remove_color(self, index):
        if 0 <= index < len(self.colors):
            del self.colors[index]

    def move_color(self, from_index, to_index):
        if 0 <= from_index < len(self.colors) and 0 <= to_index < len(self.colors):
            color = self.colors.pop(from_index)
            self.colors.insert(to_index, color)

    def to_dict(self):
        return {"name": self.name, "colors": [color.to_hex(include_alpha=True) for color in self.colors]}

    @staticmethod
    def from_dict(data):
        colors = [Color.from_hex(value) for value in data.get("colors", [])]
        return Palette(name=data.get("name", "Palette"), colors=colors)
