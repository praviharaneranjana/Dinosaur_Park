# Unity UI Framework Guidelines

This rule establishes technical standards across Unity's UI systems: **UI Toolkit** (`UnityEngine.UIElements`), **uGUI** (`UnityEngine.UI`), and **IMGUI** (`UnityEditor`).

## 1. Framework Selection Matrix

| Context | Recommended Framework | Rationale |
| :--- | :--- | :--- |
| **New Runtime Menus & HUDs (Unity 6+)** | **UI Toolkit** (`.uxml` + `.uss`) | Flexbox layouts, DOM-style styling, automatic batching, zero Canvas rebuild overhead. |
| **Worldspace HUDs & Existing Canvases** | **uGUI** (`Canvas`, `RectTransform`) | 3D billboarding, camera space attachment, legacy asset compatibility. |
| **Editor Windows & Custom Inspectors** | **UI Toolkit** (preferred) or **IMGUI** | UI Toolkit for responsive editor layouts; IMGUI for legacy `PropertyDrawer` overrides. |

## 2. UI Toolkit Directives
- **Separation of Structure & Style**: Define visual element hierarchy in `.uxml` files and all visual styles (colors, flex, margins, border radius) in `.uss` stylesheets.
- **Dynamic Elements**: Use `<ListView>`, `<ScrollView>`, or `<VisualElement>` containers. Bind data via `Bind(serializedObject)` or direct property binding.
- **Avoid Inline Styles**: Do not hardcode style properties in C# unless animating dynamic properties frame-by-frame.

## 3. uGUI Performance Directives
- **Canvas Splitting**: Separate dynamic HUD elements (health bars, timers) onto a sub-canvas separate from static UI (borders, static labels) to avoid full canvas re-batching every frame.
- **Disable Unused Raycast Targets**: Always uncheck `Raycast Target` on decorative `Image` and `TextMeshProUGUI` components to reduce graphic raycaster CPU overhead.
- **Text Rendering**: Always use **TextMeshPro** (`TextMeshProUGUI`) instead of legacy `UnityEngine.UI.Text`.

## 4. IMGUI Directives
- Use `EditorGUILayout` / `EditorGUI` strictly within `Editor/` scripts (`OnGUI`, `OnInspectorGUI`).
- Never run IMGUI code in runtime gameplay builds.
