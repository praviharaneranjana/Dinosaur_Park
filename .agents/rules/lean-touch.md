# Lean Touch Multi-Touch Guidelines

This project utilizes **Lean Touch** (`Lean.Touch`) for cross-platform touchscreen gesture detection, pinch-to-zoom, camera navigation, and touch-based object interaction.

## Core Directives

1. **Manager Lifecycle**:
   - Ensure exactly one `LeanTouch` manager component exists in the scene hierarchy.
   - Use `DontDestroyOnLoad` on the `LeanTouch` GameObject to persist gesture detection across scene transitions.
   - Set `TapThreshold = 0.5f` and `SwipeThreshold = 50f` as baseline defaults for mobile screens.

2. **UI Occlusion & Event Filtering**:
   - Always verify `finger.IsOverGui == false` before triggering gameplay actions (selection, raycasting, unit movement).
   - When retrieving fingers in `Update()`, use:
     ```csharp
     var fingers = LeanTouch.GetFingers(ignoreStartedOverGui: true, ignoreIsOverGui: true);
     ```
   - On uGUI UI elements, ensure `Raycast Target` is unchecked on purely decorative Images and TextMeshPro components to avoid unintentional touch blocking.

3. **Multi-Finger Gesture Calculations**:
   - Prefer calling `LeanGesture` mathematical static helpers (`GetScreenDelta`, `GetPinchScale`, `GetTwistDegrees`) over manual per-finger vector math.
   - Clamp pinch zoom boundaries (e.g. `Mathf.Clamp(fov, 20f, 75f)`) to prevent camera clipping through ground geometry or inverting matrices.

4. **Editor Multi-Touch Testing**:
   - Test two-finger pinch with **`Ctrl + Drag`** (or `Cmd + Drag`).
   - Test two-finger twist with **`Alt + Drag`**.
   - Ensure custom gameplay interactions function identically with real touch events and editor simulated mouse gestures.
