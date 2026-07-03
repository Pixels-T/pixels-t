<div align="center">

# 🎨 Pixels-T

**A modular, multi-layer, multi-frame pixel art editor**  
Built with Python 3, Tkinter, and sv_ttk


<img width="1918" height="1078" alt="image" src="https://github.com/user-attachments/assets/5f32ea5f-a2c2-475d-aece-abdc4173705f" />

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com)
[![Download for Windows](https://img.shields.io/badge/Download_for_Windows-blue?logo=download&logoColor=lightgrey)](https://github.com/Pixels-T/pixels-t/releases/download/v1.0.0/Pixels-T_v1.0.0.exe)
[![Website](https://img.shields.io/badge/Website-blue?logo=googlechrome&logoColor=lightgrey)](https://pixels-t.github.io/)
</div>
---

## ⚡ Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/pixels-t.git
cd pixels-t

# Install dependencies
pip install -r requirements.txt

# Launch the editor
python3 main.py
```

> **Note:** Python 3.10+ is recommended. Tkinter must be available on your system.  
> On Debian/Ubuntu: `sudo apt install python3-tk`

---

## 🏗️ Architecture

The codebase is organized into clean, single-responsibility layers:

| Layer | Path | Responsibility |
|-------|------|----------------|
| **Core** | `core/` | Framework-free primitives: `Color`, `Rect`/`Point`, Bresenham/shape rasterization, and the `EventBus` used for decoupled pub/sub between the model layer and every UI panel. |
| **Models** | `models/` | Domain model: `PixelBuffer` (numpy-backed RGBA raster with flood fill, compositing, resizing, flipping), `Layer`, `Frame` (stack of layers with blend-mode compositing), `Document` (full sprite project), `Palette`. |
| **Commands** | `commands/` | Undo/redo system. Every mutation is a `Command` with `execute()`/`undo()`, coordinated by `HistoryManager`. |
| **Tools** | `tools/` | One class per tool (`PencilTool`, `EraserTool`, `BucketTool`, `LineTool`, `RectangleTool`, `EllipseTool`, `EyedropperTool`, `SelectionTool`, `MoveTool`, `GradientTool`, `SprayTool`, `PanTool`). |
| **Services** | `services/` | I/O and cross-cutting concerns: project save/load, export, image codec, clipboard, autosave, file dialogs. |
| **Rendering** | `rendering/` | Presentation-only: nearest-neighbor scaling, transparency checkerboard, thumbnails, onion-skin tinting. |
| **App** | `app/application.py` | The `Application` controller — turns UI actions into model mutations wrapped in commands. |
| **UI** | `ui/` | Tkinter/ttk views: `MainWindow`, `CanvasView`, `Toolbar`, panels, dialogs, status bar, menu bar. |
| **Config** | `config/` | `constants.py`, `shortcuts.py`, `settings.py` (JSON preferences persisted to `~/.pixels-t/`). |

> All cross-component communication goes through `EventBus`/`DocumentEvents` rather than direct references between panels.

---

## ✨ Features

<div align="center">

| 🖌️ Drawing | 🧩 Layers | 🎬 Animation | 🎨 Color | 📤 Export |
|-----------|-----------|-------------|----------|----------|
| Pixel-perfect pencil | Unlimited layers per frame | Unlimited animation frames | RGBA / HSV / HEX | PNG (integer upscaling) |
| Eraser, bucket fill | Add, duplicate, delete, merge-down | Add, duplicate, delete, reorder | Primary + secondary colors | Animated GIF |
| Line, rectangle, ellipse | Drag-to-reorder | Per-frame duration | Recent & favorite colors | Sprite sheet |
| Gradient, spray/airbrush | Visibility, lock, opacity | Playback with durations | Editable palette panel | PNG sequence |
| Eyedropper, selection, move | Per-layer blend modes | Onion skinning (before/after) | Color swap | — |
| Horizontal/vertical symmetry | Live thumbnails | — | — | — |

</div>

### Additional Goodies
- **Infinite smooth zoom** (Ctrl+Wheel) anchored at cursor
- **Smooth panning** (Space+Drag or Middle-Mouse-Drag)
- **Pixel grid + custom snapping grid + rulers**
- **Copy / Cut / Paste / Delete** of selection or whole layer
- **Canvas resize** with 9-point anchoring
- **Layer flip / rotate**
- **Project save/load** as `.pxlst` (JSON + base64 PNG per layer)
- **Autosave** with crash-recovery lookup
- **Live status bar** (cursor coords, zoom, canvas size, active tool, undo/redo depth)
- **Fully wired menu bar** + configurable keyboard shortcuts
- **High-DPI aware** Tk scaling + nearest-neighbor rendering (no blur)

---

## ⌨️ Keyboard Shortcuts

### 🛠️ Tool Shortcuts

| Shortcut | Tool | Description |
|----------|------|-------------|
| <kbd>P</kbd> | 🖊️ Pencil | Pixel-perfect pencil with corner-artifact removal |
| <kbd>E</kbd> | 🧽 Eraser | Erase pixels from the active layer |
| <kbd>B</kbd> | 🪣 Bucket Fill | Tolerance-aware flood fill |
| <kbd>L</kbd> | 📏 Line | Draw straight lines |
| <kbd>R</kbd> | ⬜ Rectangle | Outline or filled rectangles |
| <kbd>O</kbd> | ⭕ Ellipse | Outline or filled ellipses |
| <kbd>I</kbd> | 💧 Eyedropper | Pick color from canvas |
| <kbd>M</kbd> | ⬚ Selection | Rectangular selection tool |
| <kbd>V</kbd> | ✋ Move | Cut/paste-drag selection or whole layer |
| <kbd>G</kbd> | 🌈 Gradient | Linear gradient fill |
| <kbd>S</kbd> | 💨 Spray | Airbrush / spray paint tool |

### ⚡ Action Shortcuts

| Shortcut | Action | Description |
|----------|--------|-------------|
| <kbd>Ctrl</kbd> + <kbd>N</kbd> | 📁 New Project | Create a new sprite project |
| <kbd>Ctrl</kbd> + <kbd>O</kbd> | 📂 Open Project | Open an existing `.pxlst` file |
| <kbd>Ctrl</kbd> + <kbd>S</kbd> | 💾 Save Project | Save current project |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd> | 💾 Save As | Save project with a new name |
| <kbd>Ctrl</kbd> + <kbd>E</kbd> | 📤 Export PNG | Export current frame as PNG |
| <kbd>Ctrl</kbd> + <kbd>Z</kbd> | ↩️ Undo | Undo last action |
| <kbd>Ctrl</kbd> + <kbd>Y</kbd> | ↪️ Redo | Redo last undone action |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Z</kbd> | ↪️ Redo (Alt) | Alternative redo shortcut |
| <kbd>Ctrl</kbd> + <kbd>C</kbd> | 📋 Copy | Copy selection or layer |
| <kbd>Ctrl</kbd> + <kbd>V</kbd> | 📋 Paste | Paste from clipboard |
| <kbd>Ctrl</kbd> + <kbd>X</kbd> | ✂️ Cut | Cut selection or layer |
| <kbd>Ctrl</kbd> + <kbd>A</kbd> | 🔲 Select All | Select entire canvas |
| <kbd>Esc</kbd> | ❌ Deselect | Clear current selection |
| <kbd>Ctrl</kbd> + <kbd>+</kbd> | 🔍 Zoom In | Increase canvas zoom |
| <kbd>Ctrl</kbd> + <kbd>-</kbd> | 🔍 Zoom Out | Decrease canvas zoom |
| <kbd>Ctrl</kbd> + <kbd>0</kbd> | 🔎 Zoom Reset | Reset zoom to 100% |
| <kbd>Ctrl</kbd> + <kbd>G</kbd> | #️⃣ Toggle Grid | Show/hide pixel grid |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>N</kbd> | ➕ New Layer | Add a new layer |
| <kbd>Ctrl</kbd> + <kbd>Delete</kbd> | 🗑️ Delete Layer | Remove active layer |
| <kbd>Ctrl</kbd> + <kbd>F</kbd> | 🎞️ New Frame | Add a new animation frame |
| <kbd>Ctrl</kbd> + <kbd>H</kbd> | ↔️ Flip Horizontal | Flip layer horizontally |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>H</kbd> | ↕️ Flip Vertical | Flip layer vertically |

> 💡 **Tip:** Shortcuts are fully configurable in `config/shortcuts.py`.

---

## 🧪 Testing

This code was validated with `py_compile` across every module and with two harnesses (not included here to keep the deliverable clean):

- ✅ **Pure-logic smoke test** — drives every tool/command/service without any GUI
- ✅ **Mocked-Tkinter smoke test** — constructs the full `MainWindow` and exercises menu actions, dialogs, export, and save/load

> A real display with Tk/sv_ttk installed is required to runtime-verify actual pixel-level rendering and mouse interaction.

---

## 📝 Scope Notes

To keep the codebase honest and fully functional rather than padded with stubs, the following Piskel-class features were intentionally left out of this pass:

- Text / polygon / bezier-curve / clone-stamp tools
- Layer groups and masks
- Sprite-sheet **import**
- In-app shortcut remapping UI
- OS-level drag-and-drop import of image files

The architecture (in particular `tools/base_tool.py` and `commands/command.py`) is designed so each of these can be added as a new, self-contained module without touching existing code.

---

<div align="center">

### 🚀 Happy Pixel Art-ing!

</div>
