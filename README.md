# Pixels-T

A modular, multi-layer, multi-frame pixel art editor built with Python 3, Tkinter, and sv_ttk.

## Setup

```
pip install -r requirements.txt
python3 main.py
```

Python 3.10+ is recommended. Tkinter must be available (on Debian/Ubuntu: `sudo apt install python3-tk`).

## Architecture

The codebase is organized into clean, single-responsibility layers:

- `core/` — framework-free primitives: `Color`, `Rect`/`Point`, Bresenham/shape rasterization, and the `EventBus` used for decoupled pub/sub between the model layer and every UI panel.
- `models/` — the domain model: `PixelBuffer` (numpy-backed RGBA raster with flood fill, compositing, resizing, flipping), `Layer`, `Frame` (a stack of layers with blend-mode compositing), `Document` (the full sprite project: frames, palette, selection, active layer/frame), `Palette`.
- `commands/` — the undo/redo system. Every mutation (pixel edits, layer/frame add-remove-reorder-property changes, canvas resize) is expressed as a `Command` with `execute()`/`undo()`, coordinated by `HistoryManager`.
- `tools/` — one class per tool (`PencilTool`, `EraserTool`, `BucketTool`, `LineTool`, `RectangleTool`, `EllipseTool`, `EyedropperTool`, `SelectionTool`, `MoveTool`, `GradientTool`, `SprayTool`, `PanTool`) driven through a shared `ToolContext` (active color, brush size, symmetry, pixel-perfect mode) and `ToolManager`. `brush_engine.py` and `shape_tool.py` factor out shared stroke/rasterization logic.
- `services/` — I/O and cross-cutting concerns: `project_service` (JSON + base64-PNG project save/load), `export_service` (PNG / GIF / sprite sheet / PNG-sequence export), `image_codec` (buffer to/from PNG/base64), `clipboard_service`, `autosave_service`, `file_service` (native file dialogs).
- `rendering/` — presentation-only rendering: nearest-neighbor scaling to `PhotoImage`, transparency checkerboard generation, layer/frame thumbnail generation, onion-skin tinting.
- `app/application.py` — the `Application` controller: the single place that turns a UI action ("add layer", "undo", "resize canvas") into model mutations wrapped in commands. The UI layer never mutates the document directly.
- `ui/` — Tkinter/ttk views: `MainWindow` (layout + menu wiring), `CanvasView` (the zoomable/pannable pixel canvas with rulers, grid, selection and live tool-preview overlays), `Toolbar`, `ToolOptionsPanel`, `ColorPanel`, `PalettePanel`, `LayersPanel`, `FramesPanel` (with playback and onion skinning), `StatusBar`, `MenuBar`, and `ui/dialogs/` for New Project, Resize, Export, Preferences, and Replace Color.
- `config/` — `constants.py` (all tunables), `shortcuts.py` (keyboard bindings), `settings.py` (JSON preferences persisted to `~/.pixels-t/`).

All cross-component communication goes through `EventBus`/`DocumentEvents` rather than direct references between panels, so panels can be added, removed, or reordered independently.

## Implemented features

- Pixel-perfect pencil (corner-artifact removal), eraser, bucket fill (tolerance-aware flood fill), line, rectangle, ellipse (outline/filled), gradient, spray/airbrush, eyedropper, rectangular selection, move (cut/paste-drag of the selection or whole layer)
- Horizontal/vertical symmetry (mirrored drawing) for every drawing tool
- Unlimited undo/redo via a command stack with bounded memory (region-diff commands, not full-canvas snapshots, for brush strokes/fills/shapes)
- Unlimited layers per frame: add, duplicate, delete, merge-down, drag-to-reorder, visibility, lock, opacity, per-layer blend mode (normal/multiply/screen/additive), live thumbnails
- Unlimited animation frames: add, duplicate, delete, drag-to-reorder, per-frame duration, playback (respecting each frame's duration), onion skinning (configurable before/after range)
- Infinite smooth zoom (ctrl+wheel or menu/shortcuts) anchored at the cursor, smooth panning (space+drag or middle-mouse-drag), pixel grid + custom snapping grid, rulers
- RGBA / HSV / HEX color management, primary+secondary colors with swap, recent colors, favorite colors, an editable palette panel
- Copy/cut/paste/delete of the active selection (or whole layer), select-all/deselect, canvas resize with 9-point anchoring, layer flip/rotate
- Project save/load as a single JSON file (`.pxlst`, pixel data embedded as base64 PNG per layer) and autosave-to-disk on a timer with crash-recovery lookup
- Export to PNG (with integer upscaling), animated GIF, a packed sprite sheet, or a PNG sequence
- A live status bar (cursor coordinates, zoom, canvas size, active tool, undo/redo depth), a fully wired menu bar, and configurable keyboard shortcuts (`config/shortcuts.py`)
- High-DPI aware Tk scaling and nearest-neighbor (no blur) rendering throughout

## Scope notes

To keep the codebase honest and fully functional rather than padded with stubs, the following Piskel-class features were intentionally left out of this pass: text/polygon/bezier-curve/clone-stamp tools, layer groups and masks, sprite-sheet *import*, in-app shortcut remapping UI, and OS-level drag-and-drop import of image files. The architecture (in particular `tools/base_tool.py` and `commands/command.py`) is designed so each of these can be added as a new, self-contained module without touching existing code.

## Testing

This code was validated with `py_compile` across every module and with two harnesses (not included here to keep the deliverable clean): a pure-logic smoke test driving every tool/command/service without any GUI, and a mocked-Tkinter smoke test that constructs the full `MainWindow` and exercises menu actions, dialogs, export, and save/load. Both passed. A real display with Tk/sv_ttk installed is required to runtime-verify actual pixel-level rendering and mouse interaction, since the tool that generated this project ran headless.
