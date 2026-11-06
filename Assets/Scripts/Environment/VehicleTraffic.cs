using System.Collections.Generic;
using UnityEngine;

namespace DinoPark.Environment
{
    /// <summary>
    /// Visitor cars that come out of the mountain tunnel, drive the entrance road to the plaza,
    /// turn and drive back into the tunnel, where they are recycled. Cars follow one closed
    /// waypoint loop at constant speed, spaced evenly. Pooled: no runtime allocation after Start.
    /// </summary>
    public sealed class VehicleTraffic : MonoBehaviour
    {
        [Tooltip("Car models to pick from (any mesh prefab; forward is +Z after the offset rotation).")]
        [SerializeField] private GameObject[] carPrefabs = new GameObject[0];

        [Tooltip("Closed loop of world positions: tunnel -> plaza (right lane), turn, back (other lane).")]
        [SerializeField] private Vector3[] waypoints = new Vector3[0];

        [SerializeField, Min(1)] private int carCount = 5;
        [SerializeField, Min(0.5f)] private float speed = 9f;
        [Tooltip("Car length the models are scaled to, in metres.")]
        [SerializeField, Min(1f)] private float carLength = 4.3f;
        [Tooltip("Extra yaw applied to every model so its nose points along the road.")]
        [SerializeField] private float modelYawOffset = 0f;
        [SerializeField] private int seed = 7;

        private readonly List<Transform> cars = new List<Transform>();
        private readonly List<float> distances = new List<float>();
        private float[] cumulative;
        private float loopLength;

        /// <summary>The waypoint loop in world space (read-only copy for tools and tests).</summary>
        public IReadOnlyList<Vector3> Waypoints => waypoints;

        /// <summary>Sets the loop and car models (used by the island builder).</summary>
        public void Configure(Vector3[] loop, GameObject[] prefabs, float yawOffset)
        {
            waypoints = loop;
            carPrefabs = prefabs;
            modelYawOffset = yawOffset;
        }

        private void Start()
        {
            if (waypoints == null || waypoints.Length < 2 || carPrefabs == null || carPrefabs.Length == 0) return;
            BuildTable();
            var rng = new System.Random(seed);
            for (int i = 0; i < carCount; i++)
            {
                GameObject prefab = carPrefabs[rng.Next(carPrefabs.Length)];
                if (prefab == null) continue;
                GameObject car = Instantiate(prefab, transform);
                car.name = "Car_" + i;
                FitLength(car.transform);
                cars.Add(car.transform);
                distances.Add(loopLength * i / carCount);
            }
            Step(0f);
        }

        private void Update() => Step(Time.deltaTime);

        private void Step(float dt)
        {
            for (int i = 0; i < cars.Count; i++)
            {
                float d = Mathf.Repeat(distances[i] + speed * dt, loopLength);
                distances[i] = d;
                Vector3 p = PointAt(d, out Vector3 forward);
                Vector3 ahead = PointAt(Mathf.Repeat(d + 2.5f, loopLength), out _);
                Vector3 look = ahead - p;
                if (look.sqrMagnitude < 1e-4f) look = forward;
                cars[i].SetPositionAndRotation(p, Quaternion.LookRotation(look, Vector3.up) * Quaternion.Euler(0f, modelYawOffset, 0f));
            }
        }

        private void BuildTable()
        {
            int n = waypoints.Length;
            cumulative = new float[n + 1];
            for (int i = 0; i < n; i++)
                cumulative[i + 1] = cumulative[i] + Vector3.Distance(waypoints[i], waypoints[(i + 1) % n]);
            loopLength = Mathf.Max(cumulative[n], 0.01f);
        }

        private Vector3 PointAt(float d, out Vector3 forward)
        {
            int n = waypoints.Length;
            int lo = 0, hi = n;
            while (hi - lo > 1)
            {
                int mid = (lo + hi) / 2;
                if (cumulative[mid] <= d) lo = mid; else hi = mid;
            }
            Vector3 a = waypoints[lo];
            Vector3 b = waypoints[(lo + 1) % n];
            float seg = cumulative[lo + 1] - cumulative[lo];
            float t = seg > 0f ? (d - cumulative[lo]) / seg : 0f;
            forward = (b - a).normalized;
            return Vector3.Lerp(a, b, t);
        }

        private void FitLength(Transform car)
        {
            var renderers = car.GetComponentsInChildren<Renderer>();
            if (renderers.Length == 0) return;
            Bounds b = renderers[0].bounds;
            foreach (Renderer r in renderers) b.Encapsulate(r.bounds);
            float longest = Mathf.Max(b.size.x, b.size.z);
            if (longest > 0.01f) car.localScale *= carLength / longest;
        }

        private void OnDrawGizmosSelected()
        {
            if (waypoints == null || waypoints.Length < 2) return;
            Gizmos.color = Color.yellow;
            for (int i = 0; i < waypoints.Length; i++)
                Gizmos.DrawLine(waypoints[i], waypoints[(i + 1) % waypoints.Length]);
        }
    }
}
