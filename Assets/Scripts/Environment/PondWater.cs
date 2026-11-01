using System.Collections.Generic;
using UnityEngine;

namespace MiniGame
{
    /// <summary>
    /// Controls the moving water pond inside the dinosaur enclosure.
    /// Handles procedural ripple scrolling, surface bobbing, and water drinking spots for dinosaurs.
    /// </summary>
    [RequireComponent(typeof(Renderer))]
    public class PondWater : MonoBehaviour
    {
        [Header("Water Motion")]
        [SerializeField] private Vector2 flowDirection = new Vector2(0.04f, 0.03f);
        [SerializeField] private float waveSpeed = 1.2f;
        [SerializeField] private float waveHeight = 0.05f;

        [Header("Drinking Spots")]
        [Tooltip("Waypoints around the shoreline where dinosaurs come to drink")]
        [SerializeField] private List<Transform> drinkingWaypoints = new List<Transform>();

        private Renderer rend;
        private Material waterMat;
        private Vector3 initialPosition;
        private Vector2 uvOffset;

        public IReadOnlyList<Transform> DrinkingWaypoints => drinkingWaypoints;

        private void Awake()
        {
            rend = GetComponent<Renderer>();
            if (rend != null)
            {
                waterMat = rend.material; // unique runtime instance
            }
            initialPosition = transform.position;

            // Auto-discover child drinking spots if not manually assigned
            if (drinkingWaypoints.Count == 0)
            {
                for (int i = 0; i < transform.childCount; i++)
                {
                    var child = transform.GetChild(i);
                    if (child.name.Contains("Drink") || child.name.Contains("Spot"))
                    {
                        drinkingWaypoints.Add(child);
                    }
                }
            }
        }

        private void Update()
        {
            float t = Time.time;

            // Subtle vertical water bobbing
            float bob = Mathf.Sin(t * waveSpeed) * waveHeight * 0.5f;
            transform.position = initialPosition + new Vector3(0f, bob, 0f);

            // Animate surface texture/ripples offset
            if (waterMat != null)
            {
                uvOffset += flowDirection * Time.deltaTime;
                if (waterMat.HasProperty("_BaseMap"))
                    waterMat.SetTextureOffset("_BaseMap", uvOffset);
                if (waterMat.HasProperty("_BumpMap"))
                    waterMat.SetTextureOffset("_BumpMap", uvOffset * 1.5f);
            }
        }

        /// <summary>
        /// Gets a random drinking spot along the pond perimeter for a dinosaur.
        /// </summary>
        public Vector3 GetDrinkingSpot(Vector3 dinoPos)
        {
            if (drinkingWaypoints.Count == 0)
            {
                // Fallback: point along pond perimeter facing the dino
                Vector3 dir = (dinoPos - transform.position).normalized;
                dir.y = 0;
                return transform.position + dir * 4.5f;
            }

            // Find closest or random drinking spot
            Transform best = drinkingWaypoints[Random.Range(0, drinkingWaypoints.Count)];
            return best.position;
        }

        private void OnDestroy()
        {
            if (waterMat != null)
            {
                Destroy(waterMat);
            }
        }
    }
}
