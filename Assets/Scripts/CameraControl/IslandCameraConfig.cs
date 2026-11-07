using UnityEngine;

namespace DinoPark.CameraControl
{
    /// <summary>
    /// Tuning data for <see cref="IslandCameraRig"/>. Lives in a ScriptableObject so designers
    /// can tune the feel without touching code.
    /// </summary>
    [CreateAssetMenu(menuName = "Dino Park/Camera/Island Camera Config", fileName = "IslandCameraConfig")]
    public sealed class IslandCameraConfig : ScriptableObject
    {
        [Header("Angle")]
        [Tooltip("Downward tilt. 90 = straight down. Keep above 35 so the horizon never shows.")]
        [SerializeField, Range(35f, 80f)] private float pitchDegrees = 50f;

        [Tooltip("Heading around Y. Keep 0 while the island grid is axis-aligned.")]
        [SerializeField, Range(-180f, 180f)] private float yawDegrees = 0f;

        [SerializeField, Range(15f, 60f)] private float verticalFov = 30f;

        [Header("Zoom")]
        [Tooltip("Closest the camera may get to the look-at point, in metres.")]
        [SerializeField, Min(1f)] private float minDistance = 18f;

        [Tooltip("Hard cap on zoom-out. The island fit normally stops zoom first.")]
        [SerializeField, Min(10f)] private float absoluteMaxDistance = 600f;

        [Tooltip("Multiplier on the fitted zoom-out limit. 1 = island plus ocean margin exactly fills the view.")]
        [SerializeField, Range(0.8f, 1.2f)] private float zoomOutPadding = 1f;

        [Tooltip("How fast zoom eases to its target. Higher is snappier.")]
        [SerializeField, Min(0.1f)] private float zoomSmoothing = 12f;

        [Tooltip("Mouse wheel zoom step per notch (editor and desktop testing).")]
        [SerializeField, Range(0.01f, 0.5f)] private float wheelSensitivity = 0.1f;

        [Header("Pan")]
        [Tooltip("How quickly drag momentum fades after release. Higher stops sooner.")]
        [SerializeField, Min(0.1f)] private float panDamping = 6f;

        [Tooltip("Speed cap for drag momentum, in metres per second.")]
        [SerializeField, Min(1f)] private float maxPanSpeed = 150f;

        [Header("Border")]
        [Tooltip("1 = the screen can never show beyond the playable area. 0 = only the look-at point is limited.")]
        [SerializeField, Range(0f, 1f)] private float edgeContainment = 1f;

        /// <summary>Downward tilt in degrees.</summary>
        public float PitchDegrees => pitchDegrees;
        /// <summary>Heading around Y in degrees.</summary>
        public float YawDegrees => yawDegrees;
        /// <summary>Vertical field of view in degrees.</summary>
        public float VerticalFov => verticalFov;
        /// <summary>Closest camera distance in metres.</summary>
        public float MinDistance => minDistance;
        /// <summary>Hard cap on camera distance in metres.</summary>
        public float AbsoluteMaxDistance => absoluteMaxDistance;
        /// <summary>Multiplier on the fitted maximum distance.</summary>
        public float ZoomOutPadding => zoomOutPadding;
        /// <summary>Zoom easing rate.</summary>
        public float ZoomSmoothing => zoomSmoothing;
        /// <summary>Mouse wheel zoom step.</summary>
        public float WheelSensitivity => wheelSensitivity;
        /// <summary>Pan momentum decay rate.</summary>
        public float PanDamping => panDamping;
        /// <summary>Pan momentum speed cap in metres per second.</summary>
        public float MaxPanSpeed => maxPanSpeed;
        /// <summary>How strictly the screen is kept inside the playable area (0 to 1).</summary>
        public float EdgeContainment => edgeContainment;
    }
}
