---
trigger: "When writing, refactoring, or optimizing Unity C# scripts, MonoBehaviours, custom editors, or physics/memory queries."
---

# Unity Engine Internals & Zero-Allocation Coding Rules

## 1. Null-Checking & Operator Safety
- **Strictly Avoid `?.` and `??` on `UnityEngine.Object`**: Never use the C# null-conditional (`?.`) or null-coalescing (`??`) operators on types deriving from `UnityEngine.Object` (e.g. `GameObject`, `Component`, `Transform`, `MonoBehaviour`). These operators bypass Unity's overloaded `operator ==` and fail to detect destroyed native C++ objects.
  - *Wrong*: `myComponent?.DoAction();`
  - *Correct*: `if (myComponent != null) myComponent.DoAction();` or `if (myComponent) myComponent.DoAction();`

## 2. Zero-Allocation Memory Standards
- **Tag Checking**: Always use `gameObject.CompareTag("TagName")` instead of `gameObject.tag == "TagName"`. The property `.tag` allocates a brand new managed string on the GC heap per call.
- **Physics Non-Alloc Overloads**: Use `Physics.RaycastNonAlloc`, `Physics.SphereCastNonAlloc`, and `Physics2D.RaycastNonAlloc` with pre-allocated static or cached buffers instead of allocating arrays via `RaycastAll`.
- **List-Based Component Queries**: Prefer `GetComponents<T>(List<T>)` and `GetComponentsInChildren<T>(List<T>)` over the array-returning variants to avoid garbage collection spikes.
- **Yield Instruction Caching**: Cache `WaitForSeconds`, `WaitForEndOfFrame`, and other yield instructions in private fields when used in repeating coroutines.
- **Avoid Material Cloning Leaks**: Never access `renderer.material` in `Update()` loops. Use `MaterialPropertyBlock` or `renderer.sharedMaterial`.

## 3. Editor & Serialization Standards
- **Serialized Property Workflows**: In custom inspectors (`Editor`), always wrap property changes in `serializedObject.Update()` and `serializedObject.ApplyModifiedProperties()` to support undo, prefab overrides, and multi-object editing.
- **IMGUI Event Stability**: In IMGUI (`OnGUI`, `OnInspectorGUI`), never alter the visual control count or layout structure conditionally based on dynamic values between the `Layout` and `Repaint` passes.
- **Modern UI Toolkit Adoption**: For new Editor tools, prefer UI Toolkit (`VisualElement`, `PropertyField`, `BindProperty`) over IMGUI for retained-mode zero-per-frame execution.

## 4. PlayerLoop & Ticking Rules
- **Exception Safety in Loops**: If injecting custom phases into `UnityEngine.LowLevel.PlayerLoop`, ensure callbacks never throw unhandled exceptions, as this can crash or skip the native player loop.
