using UnityEngine;

namespace DinoPark.Environment
{
    /// <summary>
    /// Feeds the global wind used by DinoPark/Environment/VertexColorLit (plants bend with height,
    /// leaves and grass flutter). One per scene; runs in edit mode too so the Scene view moves.
    /// </summary>
    [ExecuteAlways]
    public sealed class WindSettings : MonoBehaviour
    {
        private static readonly int WindDirId = Shader.PropertyToID("_DP_WindDir");
        private static readonly int WindParamsId = Shader.PropertyToID("_DP_WindParams");

        [Tooltip("Direction the wind blows toward, in world XZ (y is ignored).")]
        [SerializeField] private Vector3 direction = new Vector3(0.96f, 0f, 0.28f);

        [Tooltip("Overall bend and flutter strength. 1 = gentle breeze, 2 = windy.")]
        [SerializeField, Range(0f, 3f)] private float strength = 1f;

        [Tooltip("Speed of the sway cycle.")]
        [SerializeField, Range(0.1f, 3f)] private float speed = 1f;

        /// <summary>Current wind strength (0..3).</summary>
        public float Strength
        {
            get => strength;
            set { strength = Mathf.Clamp(value, 0f, 3f); Apply(); }
        }

        private void OnEnable() => Apply();

        private void OnValidate() => Apply();

        private void Apply()
        {
            Vector3 d = new Vector3(direction.x, 0f, direction.z);
            if (d.sqrMagnitude < 1e-4f) d = Vector3.right;
            d.Normalize();
            // w must be > 0 for the shader to use these values; it falls back to defaults at 0.
            Shader.SetGlobalVector(WindDirId, new Vector4(d.x, 0f, d.z, Mathf.Max(strength, 1e-4f)));
            Shader.SetGlobalVector(WindParamsId, new Vector4(speed, 0f, 0f, 0f));
        }
    }
}
