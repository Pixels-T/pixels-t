import colorsys
from dataclasses import dataclass


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int
    a: int = 255

    def as_tuple(self):
        return (self.r, self.g, self.b, self.a)

    def as_rgb_tuple(self):
        return (self.r, self.g, self.b)

    def to_hex(self, include_alpha=False):
        if include_alpha:
            return "#{:02x}{:02x}{:02x}{:02x}".format(self.r, self.g, self.b, self.a)
        return "#{:02x}{:02x}{:02x}".format(self.r, self.g, self.b)

    def to_hsv(self):
        h, s, v = colorsys.rgb_to_hsv(self.r / 255.0, self.g / 255.0, self.b / 255.0)
        return (h * 360.0, s * 100.0, v * 100.0)

    def to_hsl(self):
        h, l, s = colorsys.rgb_to_hls(self.r / 255.0, self.g / 255.0, self.b / 255.0)
        return (h * 360.0, s * 100.0, l * 100.0)

    def with_alpha(self, alpha):
        return Color(self.r, self.g, self.b, alpha)

    @staticmethod
    def from_hex(hex_string):
        text = hex_string.strip().lstrip("#")
        if len(text) == 6:
            r = int(text[0:2], 16)
            g = int(text[2:4], 16)
            b = int(text[4:6], 16)
            return Color(r, g, b, 255)
        if len(text) == 8:
            r = int(text[0:2], 16)
            g = int(text[2:4], 16)
            b = int(text[4:6], 16)
            a = int(text[6:8], 16)
            return Color(r, g, b, a)
        raise ValueError(f"Invalid hex color: {hex_string}")

    @staticmethod
    def from_hsv(h, s, v, a=255):
        r, g, b = colorsys.hsv_to_rgb(h / 360.0, s / 100.0, v / 100.0)
        return Color(round(r * 255), round(g * 255), round(b * 255), a)

    @staticmethod
    def from_hsl(h, s, l, a=255):
        r, g, b = colorsys.hls_to_rgb(h / 360.0, l / 100.0, s / 100.0)
        return Color(round(r * 255), round(g * 255), round(b * 255), a)

    @staticmethod
    def transparent():
        return Color(0, 0, 0, 0)

    @staticmethod
    def black():
        return Color(0, 0, 0, 255)

    @staticmethod
    def white():
        return Color(255, 255, 255, 255)
