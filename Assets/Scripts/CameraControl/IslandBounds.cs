using UnityEngine;

namespace DinoPark.CameraControl
{
    /// <summary>
    /// Defines the island footprint and the playable area (island plus a strip of ocean) in world
    /// XZ. The camera is locked inside the playable area. The box is centred on this transform's
    /// position and is axis-aligned: rotation and scale of the transform are ignored.
    /// </summary>
    public sealed class IslandBounds : MonoBehaviour
    {
        [Tooltip("Island size in metres (X, Z). 1 grid cell = 2 m.")]
        [SerializeField] private Vector2 islandSize = new Vector2(160f, 160f);

        [Tooltip("Ocean shown past the shoreline, in metres. This is the most the player can see beyond the island.")]
        [SerializeField, Min(0f)] private float oceanMargin = 16f;

        /// <summary>Island size in metres (X, Z).</summary>
        public Vector2 IslandSize => islandSize;

        /// <summary>Ocean strip width around the island in metres.</summary>
        public float OceanMargin => oceanMargin;

        /// <summary>World height of the ground plane the camera looks at.</summary>
        public float GroundY => transform.position.y;

        /// <summary>The island rectangle in world XZ (x,y of the Rect = world X,Z).</summary>
        public Rect IslandRect => BuildRect(0f);

        /// <summary>Island plus ocean margin: the area the camera may show.</summary>
        public Rect PlayableRect => BuildRect(oceanMargin);

        private Rect BuildRect(float margin)
        {
            Vector3 c = transform.position;
            Vector2 size = islandSize + Vector2.one * (margin * 2f);
            return new Rect(c.x - size.x * 0.5f, c.z - size.y * 0.5f, size.x, size.y);
        }

        private void OnDrawGizmos()
        {
            DrawRect(IslandRect, new Color(0.37f, 0.61f, 0.29f, 1f));
            DrawRect(PlayableRect, new Color(0.56f, 0.8f, 0.8f, 1f));
        }

        private void DrawRect(Rect r, Color color)
        {
            Gizmos.color = color;
            float y = GroundY;
            var a = new Vector3(r.xMin, y, r.yMin);
            var b = new Vector3(r.xMax, y, r.yMin);
            var c = new Vector3(r.xMax, y, r.yMax);
            var d = new Vector3(r.xMin, y, r.yMax);
            Gizmos.DrawLine(a, b);
            Gizmos.DrawLine(b, c);
            Gizmos.DrawLine(c, d);
            Gizmos.DrawLine(d, a);
        }
    }
}
