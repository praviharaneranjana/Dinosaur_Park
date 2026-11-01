---
name: lean-touch
description: Implements multi-touch input, mobile gestures, finger tracking, and touch camera controls using Lean Touch (Lean.Touch). Covers LeanFinger event handling (tap, swipe, pinch, twist, drag), camera pan/zoom/orbit controls, object selection, touch raycasting, and UI interaction filtering.
---

# Lean Touch Skill

This skill guides implementing multi-touch mobile gestures, touchscreen camera controls, and object manipulation using **Lean Touch** (`Lean.Touch`) in Unity.

## Quick Reference & Core Types

| Component / Class | Namespace | Core Purpose |
| :--- | :--- | :--- |
| **`LeanTouch`** | `Lean.Touch` | Central input engine. Emulates multi-touch in Editor (mouse + Alt/Ctrl), dispatches finger callbacks. |
| **`LeanFinger`** | `Lean.Touch` | Represents an individual finger contact (screen position, delta, age, tap count, start position). |
| **`LeanGesture`** | `Lean.Touch` | Calculates aggregate gesture vectors (pinch scale delta, twist angle delta, drag delta) across fingers. |
| **`LeanDragTranslate`** | `Lean.Touch` | Moves a 3D/2D GameObject based on one or more finger drag gestures. |
| **`LeanPinchScale`** | `Lean.Touch` | Scales a GameObject proportionally to two-finger pinch-in / pinch-out gestures. |
| **`LeanTwistRotate`** | `Lean.Touch` | Rotates a GameObject around an axis in response to two-finger twist gestures. |
| **`LeanDragCamera`** | `Lean.Touch` | Smoothly pans/drags the camera across a 3D ground plane or 2D orthographic bounds. |
| **`LeanSelectableByFinger`**| `Lean.Touch` | Marks a GameObject selectable when tapped by a finger; supports deselection and highlighting. |

---

## Core Workflows

### 1. Scene Initialization
Every scene utilizing Lean Touch requires a GameObject with the `LeanTouch` component attached. It can be instantiated dynamically via C#:

```csharp
using Lean.Touch;
using UnityEngine;

public static class LeanTouchInitializer
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    public static void EnsureLeanTouchManager()
    {
        if (Object.FindAnyObjectByType<LeanTouch>() == null)
        {
            var go = new GameObject("LeanTouchManager");
            var lt = go.AddComponent<LeanTouch>();
            lt.TapThreshold = 0.5f; // Max seconds for a tap
            lt.SwipeThreshold = 50f; // Min pixels for a swipe
            Object.DontDestroyOnLoad(go);
        }
    }
}
```

### 2. Event-Driven Gesture Callbacks
```csharp
using Lean.Touch;
using UnityEngine;

public class TouchGestureHandler : MonoBehaviour
{
    private void OnEnable()
    {
        LeanTouch.OnFingerDown += OnFingerDown;
        LeanTouch.OnFingerUp += OnFingerUp;
        LeanTouch.OnFingerTap += OnFingerTap;
        LeanTouch.OnFingerSwipe += OnFingerSwipe;
        LeanTouch.OnGesture += OnMultiFingerGesture;
    }

    private void OnDisable()
    {
        LeanTouch.OnFingerDown -= OnFingerDown;
        LeanTouch.OnFingerUp -= OnFingerUp;
        LeanTouch.OnFingerTap -= OnFingerTap;
        LeanTouch.OnFingerSwipe -= OnFingerSwipe;
        LeanTouch.OnGesture -= OnMultiFingerGesture;
    }

    private void OnFingerTap(LeanFinger finger)
    {
        if (finger.IsOverGui) return; // Ignore taps over UI elements
        Debug.Log($"Tap at screen position: {finger.ScreenPosition}");
    }

    private void OnFingerSwipe(LeanFinger finger)
    {
        Vector2 swipe = finger.SwipeScreenDelta;
        if (Mathf.Abs(swipe.x) > Mathf.Abs(swipe.y))
        {
            Debug.Log(swipe.x > 0 ? "Swiped Right" : "Swiped Left");
        }
        else
        {
            Debug.Log(swipe.y > 0 ? "Swiped Up" : "Swiped Down");
        }
    }

    private void OnMultiFingerGesture(List<LeanFinger> fingers)
    {
        // Aggregate pinch scale across fingers
        float pinchScale = LeanGesture.GetPinchScale(fingers);
        // Aggregate twist degrees across fingers
        float twistDegrees = LeanGesture.GetTwistDegrees(fingers);
    }
}
```

---

## Detailed References
- [Gesture Recognition, Mathematical Helpers & API](file:///d:/Unity%20Projects/mini_game/.agents/skills/lean-touch/references/gesture-recognition-api.md)
- [Touch Camera Navigation & Selection Controls](file:///d:/Unity%20Projects/mini_game/.agents/skills/lean-touch/references/camera-and-selection-controls.md)
