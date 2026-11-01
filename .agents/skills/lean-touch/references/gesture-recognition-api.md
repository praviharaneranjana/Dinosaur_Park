# Lean Touch: Gesture Recognition & Mathematical Helpers

This reference details the `LeanFinger` data structure, gesture calculations (`LeanGesture`), simulated multi-touch, and UI occlusion filtering.

---

## 1. Anatomy of `LeanFinger`

A `LeanFinger` instance represents an ongoing or recently released touch point:

| Property | Type | Description |
| :--- | :--- | :--- |
| `Index` | `int` | Finger ID (`-1` = mouse/simulated, `0+` = physical fingers). |
| `ScreenPosition` | `Vector2` | Current screen coordinates in pixels. |
| `LastScreenPosition` | `Vector2` | Position in previous frame. |
| `ScreenDelta` | `Vector2` | Movement vector since last frame. |
| `StartScreenPosition` | `Vector2` | Initial contact coordinate. |
| `TotalScreenDelta` | `Vector2` | Total travel distance from start. |
| `Age` | `float` | Duration of contact in seconds. |
| `TapCount` | `int` | Consecutive taps (e.g. 2 for double tap). |
| `IsOverGui` | `bool` | True if the finger is hovering over a Unity uGUI or UI Toolkit element. |

---

## 2. Multi-Finger Gesture Calculations with `LeanGesture`

`LeanGesture` processes a list of fingers (`List<LeanFinger>`) to extract collective geometric transformations:

```csharp
using Lean.Touch;
using UnityEngine;
using System.Collections.Generic;

public class GestureMath
{
    public static void ProcessFingers(List<LeanFinger> fingers)
    {
        // 1. Screen Center of all active fingers
        Vector2 screenCenter = LeanGesture.GetScreenCenter(fingers);

        // 2. Average Screen Delta (pan / drag vector)
        Vector2 screenDelta = LeanGesture.GetScreenDelta(fingers);

        // 3. Pinch Ratio (1.0 = no change, >1.0 = zooming in, <1.0 = zooming out)
        float pinchScale = LeanGesture.GetPinchScale(fingers);

        // 4. Twist Angle in degrees (clockwise / counter-clockwise rotation)
        float twistDegrees = LeanGesture.GetTwistDegrees(fingers);

        // 5. World Delta projected onto a plane (e.g. ground plane Y=0)
        Vector3 worldDelta = LeanGesture.GetWorldDelta(fingers, distance: 10f);
    }
}
```

---

## 3. UI Filtering & Event Suppression

To prevent touch gestures from firing when interacting with virtual joysticks, HUD buttons, or menus:

```csharp
using Lean.Touch;
using UnityEngine;

public class TouchInteractivityFilter : MonoBehaviour
{
    private void Update()
    {
        // Get only fingers that are NOT over UI elements
        List<LeanFinger> worldFingers = LeanTouch.GetFingers(ignoreStartedOverGui: true, ignoreIsOverGui: true);

        if (worldFingers.Count == 1)
        {
            // Process single-finger gameplay interaction
        }
        else if (worldFingers.Count == 2)
        {
            // Process two-finger pinch/twist
        }
    }
}
```

---

## 4. Editor Simulation Controls

When running in the Unity Editor:
- **Single Touch**: Left mouse button click and drag.
- **Two-Finger Pinch**: Hold **`Left Ctrl`** or **`Left Cmd`** and drag mouse to pinch in/out relative to screen center.
- **Two-Finger Twist**: Hold **`Left Alt`** and drag mouse to rotate around screen center.
- **Multi-Touch Simulation**: `LeanTouchSimulator` component emulates complex gestures with customizable keyboard shortcuts.
