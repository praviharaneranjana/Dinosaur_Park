# Hierarchy Organization Standards & Color Palette Customization

This reference details the `ColorPalette` asset settings in `Assets/M Studio/Colorful Hierarchy Category GameObject/Color Palette.asset`.

---

## 1. Creating Custom Category Designs

In the Project window, select `Color Palette.asset` (or create one via `Assets > Create > MStudio > Color Palette`):
Each `ColorDesign` entry specifies:
- `key`: The matching substring or prefix (e.g. `===`, `---`, `[DEBUG]`).
- `textColor`: Text color in the hierarchy list.
- `backgroundColor`: Highlight banner color behind the item.
- `fontStyle`: Bold, Italic, or BoldAndItalic.
- `textAlignment`: Left, Center, or Right.

---

## 2. Best Practice Directives for Category Roots
- Keep header GameObjects purely as organizational folders:
  - Position at `(0, 0, 0)` with no rotation or scale distortion.
  - Disable any unnecessary colliders or renderers.
  - Mark static if containing purely static environment objects.
