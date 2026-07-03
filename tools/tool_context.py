class ToolContext:
    def __init__(self, document, history):
        self.document = document
        self.history = history
        self.primary_color = (0, 0, 0, 255)
        self.secondary_color = (255, 255, 255, 255)
        self.brush_size = 1
        self.pixel_perfect = True
        self.symmetry_horizontal = False
        self.symmetry_vertical = False
        self.fill_tolerance = 0
        self.spray_radius = 4
        self.spray_density = 0.25
        self.request_redraw = lambda: None
        self.request_preview = lambda points_colors: None
        self.clear_preview = lambda: None

    def mirrored_points(self, x, y):
        points = [(x, y)]
        width = self.document.width
        height = self.document.height
        if self.symmetry_horizontal:
            points.append((width - 1 - x, y))
        if self.symmetry_vertical:
            points.append((x, height - 1 - y))
        if self.symmetry_horizontal and self.symmetry_vertical:
            points.append((width - 1 - x, height - 1 - y))
        return points
