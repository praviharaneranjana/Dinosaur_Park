# Touch Camera Navigation & Selection Controls

This reference covers setting up mobile touch camera controls (RTS drag, pinch-to-zoom, orbit) and 3D object selection with Lean Touch.

---

## 1. Mobile Touch Camera Setup

### RTS / Strategy Ground-Plane Camera
To implement standard mobile strategy game camera panning (drag to move, pinch to zoom):

1. Attach `Camera` to a parent rig `CameraRig`.
2. Attach `LeanDragCamera` to `CameraRig`:
   - Set `Sensitivity = 1.0`
   - Set `ScreenDepth.Conversion = DepthApproximation` or `PlaneIntersection` (ground plane `Vector3.up`).
3. Attach `LeanPinchScale` to `CameraRig`:
   - Bind `ScaleClampMin = 5f`, `ScaleClampMax = 30f`
   - Target camera field of view or orthographic size.

```csharp
using Lean.Touch;
using UnityEngine;

[RequireComponent(typeof(Camera))]
public class MobilePinchZoom : MonoBehaviour
{
    public float zoomSpeed = 2f;
    public float minFov = 20f;
    public float maxFov = 75f;

    private Camera _cam;

    private void Awake() => _cam = GetComponent<Camera>();

    private void Update()
    {
        var fingers = LeanTouch.GetFingers(true, true);
        if (fingers.Count == 2)
        {
            float pinchRatio = LeanGesture.GetPinchRatio(fingers);
            if (_cam.orthographic)
            {
                _cam.orthographicSize = Mathf.Clamp(_cam.orthographicSize / pinchRatio, minFov, maxFov);
            }
            else
            {
                _cam.fieldOfView = Mathf.Clamp(_cam.fieldOfView / pinchRatio, minFov, maxFov);
            }
        }
    }
}
```

---

## 2. Object Selection by Touch

### 3D Touch Raycasting
```csharp
using Lean.Touch;
using UnityEngine;

public class TouchSelector : MonoBehaviour
{
    public LayerMask interactableLayers;

    private void OnEnable() => LeanTouch.OnFingerTap += HandleTap;
    private void OnDisable() => LeanTouch.OnFingerTap -= HandleTap;

    private void HandleTap(LeanFinger finger)
    {
        if (finger.IsOverGui) return;

        // Cast ray from camera through touch screen coordinate
        Ray ray = finger.GetRay();
        if (Physics.Raycast(ray, out RaycastHit hit, 100f, interactableLayers))
        {
            if (hit.collider.TryGetComponent<LeanSelectableByFinger>(out var selectable))
            {
                selectable.Select(finger);
                Debug.Log($"Selected object: {hit.collider.name}");
            }
        }
    }
}
```

---

## 3. Drag and Drop with `LeanDragTranslate`

To make any 3D object draggable along the terrain surface:
1. Attach `Collider` to the target GameObject.
2. Attach `LeanSelectableByFinger` to enable selection when tapped.
3. Attach `LeanDragTranslate`:
   - Set `Use = ManuallySelected` or `Hover`
   - Set `ScreenDepth.Conversion = PlaneIntersection`
   - Set `ScreenDepth.PlaneNormal = Vector3.up` (ground plane)
