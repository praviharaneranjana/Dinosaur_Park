using System.Collections.Generic;
using Lean.Touch;
using NaughtyAttributes;
using UnityEngine;

namespace DinoPark.CameraControl
{
    /// <summary>
    /// Touch camera for the island: drag to pan, pinch to zoom (mouse wheel in the editor).
    /// The rig transform sits on the ground at the look-at point (the pivot) and tilts; the camera
    /// is a child pulled back along its own -Z by the zoom distance.
    /// The view is locked to <see cref="IslandBounds.PlayableRect"/> so the player only ever sees
    /// the island plus the ocean margin. Fully zoomed out, the whole playable area is on screen.
    /// </summary>
    [DefaultExecutionOrder(100)]
    public sealed class IslandCameraRig : MonoBehaviour
    {
        [SerializeField, Required] private IslandCameraConfig config;
        [SerializeField, Required] private IslandBounds bounds;
        [SerializeField, Required] private Camera targetCamera;

        private readonly Vector2[] unitFootprint = new Vector2[CameraFootprintMath.CornerCount];
        private readonly Vector2[] fitTargets = new Vector2[CameraFootprintMath.CornerCount];

        private Vector3 pivot;
        private Vector3 panVelocity;
        private float distance;
        private float targetDistance;
        private bool initialised;

        /// <summary>Current look-at point on the ground.</summary>
        public Vector3 Pivot => pivot;

        /// <summary>Current camera distance from the look-at point, in metres.</summary>
        public float Distance => distance;

        /// <summary>Moves the look-at point to a world position (clamped to the island) and stops momentum.</summary>
        public void FocusOn(Vector3 worldPoint)
        {
            pivot = new Vector3(worldPoint.x, GroundY, worldPoint.z);
            panVelocity = Vector3.zero;
        }

        /// <summary>Sets zoom from 0 (closest) to 1 (whole island in view).</summary>
        public void SetZoom01(float t)
        {
            RefreshFootprint();
            ComputeDistanceLimits(out float min, out float max);
            targetDistance = Mathf.Lerp(min, max, Mathf.Clamp01(t));
        }

        [Button("Frame Whole Island")]
        private void FrameWholeIsland()
        {
            FocusOn(bounds.PlayableRect.center.ToWorld(GroundY));
            SetZoom01(1f);
            distance = targetDistance;
        }

        private float GroundY => bounds != null ? bounds.GroundY : 0f;

        private void LateUpdate()
        {
            if (config == null || bounds == null || targetCamera == null)
            {
                return;
            }

            float dt = Time.unscaledDeltaTime;

            RefreshFootprint();
            ComputeDistanceLimits(out float minDistance, out float maxDistance);

            if (!initialised)
            {
                Vector2 center = bounds.PlayableRect.center;
                pivot = new Vector3(center.x, GroundY, center.y);
                distance = targetDistance = maxDistance;
                initialised = true;
            }

            // Pose from last frame so screen-to-ground maths matches what the player is touching.
            ApplyPose();

            List<LeanFinger> fingers = LeanTouch.GetFingers(true, false);
            HandlePan(fingers, dt);
            HandleZoom(fingers);

            targetDistance = Mathf.Clamp(targetDistance, minDistance, maxDistance);
            float blend = 1f - Mathf.Exp(-config.ZoomSmoothing * dt);
            distance = Mathf.Clamp(Mathf.Lerp(distance, targetDistance, blend), minDistance, maxDistance);

            ClampPivot();
            ApplyPose();
        }

        private void HandlePan(List<LeanFinger> fingers, float dt)
        {
            if (fingers.Count == 0)
            {
                // Finger lifted: let the drag coast to a stop.
                pivot += panVelocity * dt;
                panVelocity *= Mathf.Exp(-config.PanDamping * dt);
                if (panVelocity.sqrMagnitude < 0.0004f)
                {
                    panVelocity = Vector3.zero;
                }

                return;
            }

            Vector2 lastScreen = LeanGesture.GetLastScreenCenter(fingers);
            Vector2 nowScreen = LeanGesture.GetScreenCenter(fingers);

            if (TryScreenToGround(lastScreen, out Vector3 lastGround) &&
                TryScreenToGround(nowScreen, out Vector3 nowGround))
            {
                // Move the world with the finger: the ground point under the finger stays put.
                Vector3 delta = lastGround - nowGround;
                delta.y = 0f;
                pivot += delta;

                if (dt > 0f)
                {
                    Vector3 velocity = Vector3.ClampMagnitude(delta / dt, config.MaxPanSpeed);
                    panVelocity = Vector3.Lerp(panVelocity, velocity, 0.5f);
                }
            }
        }

        private void HandleZoom(List<LeanFinger> fingers)
        {
            // Lean's pinch ratio is lastDistance / distance, so spreading fingers gives < 1
            // (closer). Wheel sensitivity is negated so wheel-up zooms in.
            float ratio = LeanGesture.GetPinchRatio(fingers, -config.WheelSensitivity);
            targetDistance *= ratio;
        }

        private void RefreshFootprint()
        {
            if (config == null || targetCamera == null) return;

            CameraFootprintMath.ComputeUnitFootprint(
                config.PitchDegrees, config.YawDegrees, config.VerticalFov,
                targetCamera.aspect, unitFootprint);
        }

        private void ComputeDistanceLimits(out float min, out float max)
        {
            Rect playable = bounds.PlayableRect;
            Vector2 center = playable.center;

            fitTargets[0] = new Vector2(playable.xMin, playable.yMin) - center;
            fitTargets[1] = new Vector2(playable.xMax, playable.yMin) - center;
            fitTargets[2] = new Vector2(playable.xMax, playable.yMax) - center;
            fitTargets[3] = new Vector2(playable.xMin, playable.yMax) - center;

            float fit = CameraFootprintMath.FitDistance(unitFootprint, fitTargets) * config.ZoomOutPadding;
            max = Mathf.Min(fit, config.AbsoluteMaxDistance);
            min = Mathf.Min(config.MinDistance, max);
        }

        private void ClampPivot()
        {
            Vector2 clamped = CameraFootprintMath.ClampPivot(
                new Vector2(pivot.x, pivot.z), bounds.PlayableRect, unitFootprint, distance,
                config.EdgeContainment);

            if (!Mathf.Approximately(clamped.x, pivot.x) || !Mathf.Approximately(clamped.y, pivot.z))
            {
                // Hit the border: kill momentum so we don't grind against it.
                panVelocity = Vector3.zero;
            }

            pivot = new Vector3(clamped.x, GroundY, clamped.y);
        }

        private void ApplyPose()
        {
            transform.SetPositionAndRotation(
                new Vector3(pivot.x, GroundY, pivot.z),
                Quaternion.Euler(config.PitchDegrees, config.YawDegrees, 0f));

            Transform cameraTransform = targetCamera.transform;
            cameraTransform.localPosition = new Vector3(0f, 0f, -distance);
            cameraTransform.localRotation = Quaternion.identity;
            targetCamera.fieldOfView = config.VerticalFov;
        }

        private bool TryScreenToGround(Vector2 screenPoint, out Vector3 groundPoint)
        {
            Ray ray = targetCamera.ScreenPointToRay(screenPoint);
            var ground = new Plane(Vector3.up, new Vector3(0f, GroundY, 0f));

            if (ground.Raycast(ray, out float enter))
            {
                groundPoint = ray.GetPoint(enter);
                return true;
            }

            groundPoint = default;
            return false;
        }
    }

    internal static class Vector2WorldExtensions
    {
        /// <summary>Maps a 2D (X, Z) point to a world position at the given height.</summary>
        public static Vector3 ToWorld(this Vector2 xz, float y) => new Vector3(xz.x, y, xz.y);
    }
}
