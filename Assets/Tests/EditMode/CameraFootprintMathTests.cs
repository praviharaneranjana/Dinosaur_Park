using DinoPark.CameraControl;
using NUnit.Framework;
using UnityEngine;

namespace DinoPark.Tests
{
    public class CameraFootprintMathTests
    {
        private const float Pitch = 50f;
        private const float Yaw = 0f;
        private const float Fov = 30f;
        private const float Aspect = 16f / 9f;

        private static readonly Rect Playable = new Rect(-96f, -96f, 192f, 192f);

        private static Vector2[] Footprint() =>
            CameraFootprintMath.ComputeUnitFootprint(Pitch, Yaw, Fov, Aspect);

        private static void Bounds(Vector2[] unitQuad, float distance, out Vector2 min, out Vector2 max)
        {
            min = new Vector2(float.MaxValue, float.MaxValue);
            max = new Vector2(float.MinValue, float.MinValue);
            foreach (Vector2 corner in unitQuad)
            {
                min = Vector2.Min(min, corner * distance);
                max = Vector2.Max(max, corner * distance);
            }
        }

        [Test]
        public void ComputeUnitFootprint_TiltedCameraYawZero_FarEdgeIsWiderAndFurtherThanNearEdge()
        {
            // Arrange + Act
            Vector2[] quad = Footprint(); // 0 BL, 1 BR, 2 TR, 3 TL

            // Assert
            Assert.Greater(quad[2].y, quad[0].y, "top of screen is further ahead than bottom");
            Assert.Greater(quad[2].x, quad[1].x, "far edge is wider than near edge");
            Assert.Less(quad[3].x, quad[0].x, "far edge is wider on the left too");
        }

        [Test]
        public void ComputeUnitFootprint_YawZero_IsMirroredLeftToRight()
        {
            // Arrange + Act
            Vector2[] quad = Footprint();

            // Assert
            Assert.AreEqual(quad[0].x, -quad[1].x, 1e-4f);
            Assert.AreEqual(quad[3].x, -quad[2].x, 1e-4f);
            Assert.AreEqual(quad[0].y, quad[1].y, 1e-4f);
        }

        [Test]
        public void ComputeUnitFootprint_AnyPitchAbove35_ContainsThePivot()
        {
            // Arrange
            for (float pitch = 35f; pitch <= 80f; pitch += 5f)
            {
                // Act
                Vector2[] quad = CameraFootprintMath.ComputeUnitFootprint(pitch, 30f, Fov, Aspect);

                // Assert
                Assert.IsTrue(CameraFootprintMath.ContainsPoint(quad, 1f, Vector2.zero), $"pitch {pitch}");
            }
        }

        [Test]
        public void ContainsPoint_PointOutsideQuad_ReturnsFalse()
        {
            // Arrange
            Vector2[] quad = Footprint();

            // Act + Assert
            Assert.IsFalse(CameraFootprintMath.ContainsPoint(quad, 10f, new Vector2(0f, -500f)));
            Assert.IsFalse(CameraFootprintMath.ContainsPoint(quad, 10f, new Vector2(500f, 0f)));
        }

        [Test]
        public void FitDistance_PlayableAreaCorners_AreInsideAtFitAndNotInsideJustBelow()
        {
            // Arrange
            Vector2[] quad = Footprint();
            Vector2 c = Playable.center;
            Vector2[] targets =
            {
                new Vector2(Playable.xMin, Playable.yMin) - c, new Vector2(Playable.xMax, Playable.yMin) - c,
                new Vector2(Playable.xMax, Playable.yMax) - c, new Vector2(Playable.xMin, Playable.yMax) - c,
            };

            // Act
            float fit = CameraFootprintMath.FitDistance(quad, targets);

            // Assert
            foreach (Vector2 t in targets)
            {
                Assert.IsTrue(CameraFootprintMath.ContainsPoint(quad, fit * 1.001f, t), "fits at fit distance");
            }

            bool allInsideBelow = true;
            foreach (Vector2 t in targets)
            {
                allInsideBelow &= CameraFootprintMath.ContainsPoint(quad, fit * 0.98f, t);
            }

            Assert.IsFalse(allInsideBelow, "does not fit 2% closer");
        }

        [Test]
        public void ClampPivot_PivotFarOutsideBounds_KeepsWholeFootprintInsideBounds()
        {
            // Arrange
            Vector2[] quad = Footprint();
            const float distance = 25f;

            // Act
            Vector2 pivot = CameraFootprintMath.ClampPivot(new Vector2(5000f, -5000f), Playable, quad, distance);

            // Assert
            Bounds(quad, distance, out Vector2 min, out Vector2 max);
            Assert.GreaterOrEqual(pivot.x + min.x, Playable.xMin - 1e-3f);
            Assert.LessOrEqual(pivot.x + max.x, Playable.xMax + 1e-3f);
            Assert.GreaterOrEqual(pivot.y + min.y, Playable.yMin - 1e-3f);
            Assert.LessOrEqual(pivot.y + max.y, Playable.yMax + 1e-3f);
        }

        [Test]
        public void ClampPivot_PivotAlreadyValid_IsUnchanged()
        {
            // Arrange
            Vector2[] quad = Footprint();
            var start = new Vector2(3f, -2f);

            // Act
            Vector2 pivot = CameraFootprintMath.ClampPivot(start, Playable, quad, 20f);

            // Assert
            Assert.AreEqual(start.x, pivot.x, 1e-4f);
            Assert.AreEqual(start.y, pivot.y, 1e-4f);
        }

        [Test]
        public void ClampPivot_FootprintLargerThanBounds_HoldsPivotAtBoundsCentre()
        {
            // Arrange
            Vector2[] quad = Footprint();

            // Act
            Vector2 pivot = CameraFootprintMath.ClampPivot(new Vector2(40f, 40f), Playable, quad, 2000f);

            // Assert
            Assert.AreEqual(Playable.center.x, pivot.x, 1e-3f);
            Assert.AreEqual(Playable.center.y, pivot.y, 1e-3f);
        }

        [Test]
        public void ClampPivot_ContainmentZero_OnlyLimitsPivotToBounds()
        {
            // Arrange
            Vector2[] quad = Footprint();

            // Act
            Vector2 pivot = CameraFootprintMath.ClampPivot(new Vector2(5000f, 5000f), Playable, quad, 25f, 0f);

            // Assert
            Assert.AreEqual(Playable.xMax, pivot.x, 1e-3f);
            Assert.AreEqual(Playable.yMax, pivot.y, 1e-3f);
        }

        [Test]
        public void PlayableRect_OceanMarginSet_ExpandsIslandRectOnEverySide()
        {
            // Arrange
            var go = new GameObject("Bounds");
            try
            {
                IslandBounds bounds = go.AddComponent<IslandBounds>();

                // Act
                Rect island = bounds.IslandRect;
                Rect playable = bounds.PlayableRect;

                // Assert
                Assert.AreEqual(island.width + 2f * bounds.OceanMargin, playable.width, 1e-3f);
                Assert.AreEqual(island.center.x, playable.center.x, 1e-3f);
                Assert.AreEqual(island.center.y, playable.center.y, 1e-3f);
            }
            finally
            {
                Object.DestroyImmediate(go);
            }
        }
    }
}
