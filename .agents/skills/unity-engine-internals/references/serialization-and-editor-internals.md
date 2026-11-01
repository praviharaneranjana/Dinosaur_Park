# Serialization & Editor Internals (SerializedObject & Property Mechanics)

Inspecting `Editor/Mono/Inspector/SerializedObject.bindings.cs` and `Editor/Mono/Inspector/SerializedProperty.bindings.cs` in **`UnityCsReference`** reveals how Unity manages editor state, undo/redo history, dirty tracking, and prefab overrides.

---

## 1. The Serialization Pipeline: SerializedObject

When authoring custom Inspectors (`Editor`) or Property Drawers (`PropertyDrawer`), modifying public fields directly (`target.myValue = 10;`) creates severe issues:
- Bypasses Unity's Undo/Redo stack.
- Does not register changes for scene/prefab dirty flags.
- Fails when multi-object editing multiple GameObjects.
- Breaks prefab override tracking (the blue vertical indicator in the inspector).

`SerializedObject` solves this by acting as a transaction manager wrapping native serialized data:

```
+-------------------------------------------------------------+
| 1. serializedObject.Update()                                |
|    Reads latest native C++ serialized state into managed    |
|    change buffer.                                           |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 2. SerializedProperty Edits                                 |
|    prop.floatValue = 10f;                                   |
|    Modifies managed property representation buffer.         |
+-------------------------------------------------------------+
                              |
                              v
+-------------------------------------------------------------+
| 3. serializedObject.ApplyModifiedProperties()               |
|    - Computes diff against original state                   |
|    - Commits modifications to native C++ engine             |
|    - Pushes atomic state snapshot to Undo stack             |
|    - Marks active Scene / Prefab dirty                      |
|    - Flags prefab instance property overrides               |
+-------------------------------------------------------------+
```

### The Standard Inspector Template
```csharp
using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(CharacterStats))]
[CanEditMultipleObjects] // Enables multi-selection editing
public class CharacterStatsEditor : Editor
{
    private SerializedProperty healthProp;
    private SerializedProperty speedProp;

    private void OnEnable()
    {
        // Cache serialized property lookups (string lookup done once)
        healthProp = serializedObject.FindProperty("health");
        speedProp = serializedObject.FindProperty("movementSpeed");
    }

    public override void OnInspectorGUI()
    {
        // 1. Synchronize managed properties with native serialized state
        serializedObject.Update();

        // 2. Render properties (automatically handles prefab bold overrides and multi-edit "-")
        EditorGUILayout.PropertyField(healthProp);
        EditorGUILayout.PropertyField(speedProp);

        // 3. Commit changes to native state, push undo, and mark dirty
        serializedObject.ApplyModifiedProperties();
    }
}
```

---

## 2. IMGUI Dual-Pass Event Architecture

In `Editor/Mono/GUI/GUIUtility.cs` and `IMGUI/`, Unity executes the GUI loop across multiple event passes:
- **`EventType.Layout`**: Queries every control to compute layout rects, minimum/maximum sizes, and vertical/horizontal group dimensions.
- **`EventType.Repaint`**: Uses computed layout rects to render text, icons, borders, and textures.
- **`EventType.MouseDown` / `MouseUp` / `KeyDown`**: Handles user input.

### The IMGUI "Layout Mismatch" Error
A very common exception is:
`ArgumentException: Getting control 0's position in a group with only 0 controls when doing Repaint`

**Root Cause**: The GUI control hierarchy changed between the `Layout` pass and the `Repaint` pass!
```csharp
// WRONG: Modifying structure conditionally on dynamic values during loop
if (Random.value > 0.5f) // Condition can change between Layout and Repaint!
{
    GUILayout.Button("Click");
}

// CORRECT: Evaluate conditions before GUI loop or rely strictly on SerializedProperty state
bool showButton = healthProp.floatValue > 0f;
if (showButton)
{
    GUILayout.Button("Click");
}
```

---

## 3. UI Toolkit vs IMGUI: Internal Shift

Unity 6 strongly favors **UI Toolkit** over IMGUI for Editor authoring:

| Feature | Legacy IMGUI (`OnInspectorGUI`) | Modern UI Toolkit (`CreateInspectorGUI`) |
|---|---|---|
| **Execution Model** | Polling: Called multiple times per frame (`Layout`, `Repaint`, Input) | Retained Mode: Visual tree built once, event-driven updates |
| **Performance** | High CPU overhead (continuous string layouts, boxing) | Zero-per-frame overhead; layout calculated via native Yoga engine |
| **Styling** | Hardcoded C# `GUIStyle` calls | CSS-like USS stylesheets and UXML templates |
| **Property Binding** | Manual `serializedObject.Update()` & `ApplyModifiedProperties()` | Two-way automated binding via `BindProperty(prop)` |

### Modern UI Toolkit Inspector Example
```csharp
using UnityEditor;
using UnityEditor.UIElements;
using UnityEngine.UIElements;

[CustomEditor(typeof(CharacterStats))]
public class CharacterStatsUIElementsEditor : Editor
{
    public override VisualElement CreateInspectorGUI()
    {
        var root = new VisualElement();

        // Automatically creates bound UI controls with undo/redo and prefab overrides
        var healthField = new PropertyField(serializedObject.FindProperty("health"));
        var speedField = new PropertyField(serializedObject.FindProperty("movementSpeed"));

        root.Add(healthField);
        root.Add(speedField);

        return root;
    }
}
```
