using UnityEngine;

namespace DinoPark.CameraControl
{
    /// <summary>
    /// Pure math for the island camera: where the screen lands on the ground, how far out the
    /// camera may zoom, and where the look-at point may sit. No scene or Camera access, so it is
    /// unit-testable. All footprints are 2D (x = world X, y = world Z) and relative to the pivot,
    /// the ground point at the centre of the screen.
    /// </summary>
    public static class CameraFootprintMath
    {
        /// <summary>Number of corners of the screen footprint.</summary>
        public const int CornerCount = 4;

        // A ray that points at or above the horizon never hits the ground; tilt it down to this.
        private const float MinDownwardSlope = 0.05f;

        /// <summary>
        /// Fills <paramref name="result"/> with the ground footprint of a camera whose look-at point
        /// is the origin and which sits 1 unit away. Footprint scales linearly with distance, so
        /// multiply by the real distance. Corners are in perimeter order:
        /// bottom-left, bottom-right, top-right, top-left of the screen.
        /// </summary>
        /// <param name="pitchDeg">Downward tilt in degrees (90 = straight down).</param>
        /// <param name="yawDeg">Heading in degrees around Y.</param>
        /// <param name="verticalFovDeg">Vertical field of view in degrees.</param>
        /// <param name="aspect">Screen width divided by height.</param>
        /// <param name="result">Array of length <see cref="CornerCount"/> to fill.</param>
        public static void ComputeUnitFootprint(float pitchDeg, float yawDeg, float verticalFovDeg,
            float aspect, Vector2[] result)
        {
            Quaternion rotation = Quaternion.Euler(pitchDeg, yawDeg, 0f);
            Vector3 cameraPosition = rotation * new Vector3(0f, 0f, -1f);
            float tanHalfV = Mathf.Tan(verticalFovDeg * 0.5f * Mathf.Deg2Rad);
            float tanHalfH = tanHalfV * aspect;

            for (int i = 0; i < CornerCount; i++)
            {
                // Perimeter order: (-1,-1), (1,-1), (1,1), (-1,1)
                float sx = (i == 1 || i == 2) ? 1f : -1f;
                float sy = (i >= 2) ? 1f : -1f;

                Vector3 dir = rotation * new Vector3(sx * tanHalfH, sy * tanHalfV, 1f);
                if (dir.y > -MinDownwardSlope)
                {
                    dir.y = -MinDownwardSlope;
                }

                float t = -cameraPosition.y / dir.y;
                result[i] = new Vector2(cameraPosition.x + dir.x * t, cameraPosition.z + dir.z * t);
            }
        }

        /// <summary>Allocating convenience wrapper for <see cref="ComputeUnitFootprint(float,float,float,float,Vector2[])"/>.</summary>
        public static Vector2[] ComputeUnitFootprint(float pitchDeg, float yawDeg, float verticalFovDeg, float aspect)
        {
            var result = new Vector2[CornerCount];
            ComputeUnitFootprint(pitchDeg, yawDeg, verticalFovDeg, aspect, result);
            return result;
        }

        /// <summary>
        /// True when <paramref name="point"/> (relative to the pivot) lies inside the convex quad
        /// <paramref name="unitQuad"/> scaled by <paramref name="scale"/>.
        /// </summary>
        public static bool ContainsPoint(Vector2[] unitQuad, float scale, Vector2 point)
        {
            bool hasPositive = false;
            bool hasNegative = false;

            for (int i = 0; i < CornerCount; i++)
            {
                Vector2 a = unitQuad[i] * scale;
                Vector2 b = unitQuad[(i + 1) % CornerCount] * scale;
                Vector2 edge = b - a;
                Vector2 toPoint = point - a;
                float cross = edge.x * toPoint.y - edge.y * toPoint.x;

                if (cross > 1e-4f) hasPositive = true;
                else if (cross < -1e-4f) hasNegative = true;
            }

            return !(hasPositive && hasNegative);
        }

        /// <summary>
        /// Smallest camera distance at which every point in <paramref name="targets"/> (relative to
        /// the pivot) is inside the screen footprint. Used to find the maximum zoom-out.
        /// </summary>
        public static float FitDistance(Vector2[] unitQuad, Vector2[] targets, float searchLimit = 10000f)
        {
            float low = 0f;
            float high = searchLimit;

            for (int iteration = 0; iteration < 40; iteration++)
            {
                float mid = (low + high) * 0.5f;
                if (ContainsAll(unitQuad, mid, targets)) high = mid;
                else low = mid;
            }

            return high;
        }

        /// <summary>
        /// Moves <paramref name="pivot"/> (world XZ) the shortest way so the screen footprint at
        /// <paramref name="distance"/> stays inside <paramref name="bounds"/>.
        /// </summary>
        /// <param name="containment">1 = footprint must stay fully inside (strict). 0 = only the
        /// pivot is limited (Clash-of-Clans style, ocean may show past the edge).</param>
        /// <remarks>On an axis where the footprint is larger than the bounds, no position keeps it
        /// inside, so the pivot is held as near the bounds centre as the axis allows.</remarks>
        public static Vector2 ClampPivot(Vector2 pivot, Rect bounds, Vector2[] unitQuad, float distance,
            float containment = 1f)
        {
            Vector2 offsetMin = new Vector2(float.MaxValue, float.MaxValue);
            Vector2 offsetMax = new Vector2(float.MinValue, float.MinValue);

            for (int i = 0; i < CornerCount; i++)
            {
                Vector2 corner = unitQuad[i] * distance;
                offsetMin = Vector2.Min(offsetMin, corner);
                offsetMax = Vector2.Max(offsetMax, corner);
            }

            containment = Mathf.Clamp01(containment);
            Vector2 center = bounds.center;

            return new Vector2(
                ClampAxis(pivot.x, bounds.xMin - offsetMin.x * containment, bounds.xMax - offsetMax.x * containment, center.x),
                ClampAxis(pivot.y, bounds.yMin - offsetMin.y * containment, bounds.yMax - offsetMax.y * containment, center.y));
        }

        private static float ClampAxis(float value, float low, float high, float center)
        {
            if (low <= high)
            {
                return Mathf.Clamp(value, low, high);
            }

            // Footprint wider than the bounds: no valid range. Stay as close to centre as possible.
            return Mathf.Clamp(center, high, low);
        }

        private static bool ContainsAll(Vector2[] unitQuad, float scale, Vector2[] targets)
        {
            for (int i = 0; i < targets.Length; i++)
            {
                if (!ContainsPoint(unitQuad, scale, targets[i])) return false;
            }

            return true;
        }
    }
}
