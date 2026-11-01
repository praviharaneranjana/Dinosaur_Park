using UnityEngine;

namespace MiniGame
{
    /// <summary>
    /// Adds natural atmospheric wind swaying motion to trees, leaves, and bushes.
    /// Creates realistic waving in the breeze with localized gust variations.
    /// </summary>
    [SelectionBase]
    public class FoliageWindSway : MonoBehaviour
    {
        [Header("Wind Settings")]
        [Tooltip("Strength of the wind sway")]
        [SerializeField] private float swayIntensity = 2.2f;

        [Tooltip("Speed/frequency of the wind oscillations")]
        [SerializeField] private float swayFrequency = 1.1f;

        [Tooltip("Maximum tilt angle in degrees")]
        [SerializeField] private float maxTiltAngle = 3.5f;

        [Tooltip("Whether to affect scale subtly for branch breathing")]
        [SerializeField] private bool microBreathing = true;

        private Quaternion initialLocalRotation;
        private Vector3 initialLocalScale;
        private float phaseOffset;
        private float gustFactor;
        private float gustTimer;

        private void Start()
        {
            initialLocalRotation = transform.localRotation;
            initialLocalScale = transform.localScale;

            // Spatial phase offset based on world position so adjacent foliage doesn't sway in lockstep
            phaseOffset = (transform.position.x * 0.37f + transform.position.z * 0.43f);
            gustTimer = Random.Range(0f, 5f);
            gustFactor = 1.0f;
        }

        private void Update()
        {
            float time = Time.time;

            // Dynamic periodic wind gusts
            gustTimer -= Time.deltaTime;
            if (gustTimer <= 0f)
            {
                gustFactor = Random.Range(0.7f, 1.6f);
                gustTimer = Random.Range(3f, 7f);
            }

            // Dual harmonic wave for organic wind motion
            float wave1 = Mathf.Sin((time * swayFrequency) + phaseOffset);
            float wave2 = Mathf.Cos((time * swayFrequency * 0.65f) + phaseOffset * 1.5f);
            float combinedWave = (wave1 + wave2 * 0.4f) * swayIntensity * gustFactor;

            // Wind direction (default gentle breeze along X/Z axis)
            float pitch = combinedWave * (maxTiltAngle * 0.7f);
            float roll = (wave2 * 0.8f) * maxTiltAngle * gustFactor;

            transform.localRotation = initialLocalRotation * Quaternion.Euler(pitch, 0f, roll);

            if (microBreathing)
            {
                float breathe = 1.0f + (wave1 * 0.015f * gustFactor);
                transform.localScale = new Vector3(initialLocalScale.x * breathe, initialLocalScale.y, initialLocalScale.z * breathe);
            }
        }
    }
}
