using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace DinoPark.EditorTools
{
    public static partial class IslandPolish
    {
        /// <summary>The main fall: where the plateau stream leaves the cliff edge.</summary>
        private struct FallLip
        {
            public bool Valid;
            public Vector3 Lip;      // centre of the stream at the cliff edge, at water height
            public Vector3 Flow;     // horizontal flow direction over the edge
            public float Width;
        }

        /// <summary>
        /// The lowland river as ONE water surface from the falls pool to the sea, replacing the Blender
        /// pool and the old river ribbon (two overlapping layers with a stair-step seam). It is a 1 m height
        /// grid at the water level, kept wherever the ground is below or just above the water, so its edges
        /// always sit under the bank and the shoreline is where water meets terrain. The channel is carved
        /// all the way through the beach so the mouth opens into the sea, and the banks get rocks and reeds.
        /// </summary>
        private static void BuildRiverSystem(Ctx ctx, Transform parent, Material mat, List<Collider> surfaces, GameObject pool)
        {
            // centre line, extended past the old end out through the sand bar into the sea
            var line = new List<Vector3>(RiverLine);
            Vector3 last = line[line.Count - 1], dir = last - line[line.Count - 2];
            dir.y = 0f;
            dir.Normalize();
            float origLen = 0f;
            for (int i = 1; i < RiverLine.Length; i++) origLen += Vector2.Distance(new Vector2(RiverLine[i - 1].x, RiverLine[i - 1].z), new Vector2(RiverLine[i].x, RiverLine[i].z));
            line.Add(last + dir * 16f);
            line.Add(last + dir * 34f);
            List<Vector3> pts = Resample(line, 1.5f);
            for (int it = 0; it < 4; it++)
            {
                var copy = new List<Vector3>(pts);
                for (int i = 1; i < pts.Count - 1; i++) pts[i] = (copy[i - 1] + copy[i] * 2f + copy[i + 1]) * 0.25f;
            }
            int n = pts.Count;
            var arcs = new float[n];
            for (int i = 1; i < n; i++) arcs[i] = arcs[i - 1] + Vector2.Distance(new Vector2(pts[i - 1].x, pts[i - 1].z), new Vector2(pts[i].x, pts[i].z));
            float total = arcs[n - 1];
            float WidthAt(float arc) => arc <= origLen ? SampleWidths(RiverWidths, arc / origLen) : Mathf.Lerp(14f, 28f, Mathf.SmoothStep(0f, 1f, (arc - origLen) / Mathf.Max(total - origLen, 1f)));

            // water level: the Blender river surface, never rising downstream, eased out of the pool level
            float poolY = pool != null ? pool.GetComponent<Renderer>().bounds.max.y : 0.07f;
            float lastY = poolY;
            for (int i = 0; i < n; i++)
            {
                float best = float.NegativeInfinity;
                var ray = new Ray(new Vector3(pts[i].x, 200f, pts[i].z), Vector3.down);
                foreach (Collider c in surfaces)
                    if (c.Raycast(ray, out RaycastHit hit, 400f)) best = Mathf.Max(best, hit.point.y);
                if (float.IsNegativeInfinity(best)) best = lastY;
                best = Mathf.Min(best, lastY);
                float y = Mathf.Lerp(poolY, best, Mathf.SmoothStep(0f, 1f, arcs[i] / 14f));
                if (arcs[i] <= origLen) y = Mathf.Max(y, SeaLevel + 0.03f);
                else y = Mathf.Lerp(SeaLevel + 0.03f, SeaLevel - 0.1f, (arcs[i] - origLen) / Mathf.Max(total - origLen, 1f));   // slips under the sea surface
                pts[i] = new Vector3(pts[i].x, y, pts[i].z);
                lastY = y;
            }

            CarveChannel(ctx, pts, arcs, WidthAt);
            Physics.SyncTransforms();

            // ---- water grid
            Bounds box = new Bounds(pts[0], Vector3.zero);
            foreach (Vector3 p in pts) box.Encapsulate(p);
            Bounds poolBox = pool != null ? pool.GetComponent<Renderer>().bounds : new Bounds(pts[0], Vector3.one * 8f);
            poolBox.Expand(new Vector3(8f, 0f, 8f));
            box.Encapsulate(poolBox);
            box.Expand(new Vector3(32f, 0f, 32f));
            const float cell = 1f;
            int nx = Mathf.CeilToInt(box.size.x / cell) + 1, nz = Mathf.CeilToInt(box.size.z / cell) + 1;
            var index = new int[nx * nz];
            var verts = new List<Vector3>();
            var cols = new List<Color>();
            var fades = new List<Vector2>();
            Vector3 start = pts[0], outFlow = (pts[Mathf.Min(6, n - 1)] - pts[0]);
            for (int j = 0; j < nz; j++)
            for (int i = 0; i < nx; i++)
            {
                index[j * nx + i] = -1;
                float x = box.min.x + i * cell, z = box.min.z + j * cell;
                var p = new Vector3(x, 0f, z);
                float dR = DistToPath(p, pts, out float arc, out float wlR);
                float half = WidthAt(arc) * 0.5f;
                bool inRiver = dR < half + 10f;
                bool inPool = poolBox.Contains(new Vector3(x, poolBox.center.y, z));
                if (!inRiver && !inPool) continue;
                float g = GroundY(ctx, x, z, -20f);
                float wl = inRiver && (!inPool || arc > 3f) ? wlR : poolY;
                if (inPool && inRiver && arc <= 3f) wl = Mathf.Max(wlR, poolY);
                float depth = wl - g;
                if (depth < -0.7f) continue;
                // fade out where the river runs into the sea, so the ocean takes over without an edge
                float fade = inPool && !(inRiver && dR < half) ? 1f : 1f - Mathf.SmoothStep(0f, 1f, (arc - (origLen - 18f)) / 28f);
                // where low ground (the sea floor at the mouth) lets the water reach the edge of the river band, feather it out sideways
                if (!inPool) fade *= 1f - Mathf.SmoothStep(0f, 1f, (dR - half - 3f) / 6.5f);
                if (fade <= 0.001f) continue;

                Vector2 flowDir;
                float speed;
                if (inRiver && (!inPool || dR < half))
                {
                    int k = ArcIndex(arcs, arc);
                    Vector3 tan = pts[k] - pts[k - 1];
                    flowDir = new Vector2(tan.x, tan.z).normalized;
                    float a = Mathf.Clamp01(1f - dR / Mathf.Max(half, 0.5f));
                    speed = 0.65f * (0.35f + 0.65f * a) * Mathf.SmoothStep(0f, 1f, arc / 10f);
                    speed = Mathf.Max(speed, 0.05f);
                }
                else
                {
                    Vector3 toOut = start - p;
                    flowDir = new Vector2(toOut.x + outFlow.x * 0.2f, toOut.z + outFlow.z * 0.2f).normalized;
                    speed = 0.05f;
                }
                index[j * nx + i] = verts.Count;
                verts.Add(new Vector3(x, wl, z));
                cols.Add(new Color(flowDir.x * 0.5f + 0.5f, flowDir.y * 0.5f + 0.5f, speed, Mathf.Clamp(depth, 0f, RiverDepthMax) / RiverDepthMax));
                fades.Add(new Vector2(fade, 0f));
            }
            var tris = new List<int>();
            for (int j = 0; j < nz - 1; j++)
            for (int i = 0; i < nx - 1; i++)
            {
                int a = index[j * nx + i], b = index[j * nx + i + 1], c = index[(j + 1) * nx + i], d = index[(j + 1) * nx + i + 1];
                if (a >= 0 && c >= 0 && b >= 0) tris.AddRange(new[] { a, c, b });
                if (b >= 0 && c >= 0 && d >= 0) tris.AddRange(new[] { b, c, d });
                else if (a >= 0 && c >= 0 && d >= 0 && b < 0) tris.AddRange(new[] { a, c, d });
                if (a >= 0 && b >= 0 && d >= 0 && c < 0) tris.AddRange(new[] { a, d, b });
            }
            var mesh = new Mesh { indexFormat = IndexFormat.UInt32 };
            mesh.SetVertices(verts);
            mesh.SetColors(cols);
            mesh.SetUVs(0, fades);
            mesh.SetTriangles(tris, 0);
            mesh.SetNormals(Enumerable.Repeat(Vector3.up, verts.Count).ToList());
            mesh.RecalculateBounds();
            Material main = Mat("M_Water_RiverMain", WaterShader, m =>
            {
                m.CopyPropertiesFromMaterial(mat);
                m.SetFloat("_UseFadeUV", 1f);
                m.renderQueue = mat.renderQueue;
            });
            MeshObject("River", parent, SaveMesh(mesh, "Water_River"), new[] { main }, false, ShadowCastingMode.Off);
            if (pool != null) pool.SetActive(false);

            int cleared = ClearChannel(ctx, pts, WidthAt);
            int dressed = DressBanks(ctx, parent, pts, arcs, origLen, WidthAt);
            ctx.Log.Add($"River: one surface pool->sea ({verts.Count} verts, {tris.Count / 3} tris), channel {total:F0} m carved through the mouth, {cleared} things cleared from the channel, {dressed} bank rocks/plants");
        }

        /// <summary>Index of the first centre-line point at or after <paramref name="arc"/> metres (at least 1).</summary>
        private static int ArcIndex(float[] arcs, float arc)
        {
            int b = System.Array.BinarySearch(arcs, arc);
            if (b < 0) b = ~b;
            return Mathf.Clamp(b, 1, arcs.Length - 1);
        }

        /// <summary>Lowers the island ground along the river so the channel is continuous down to the sea.</summary>
        private static void CarveChannel(Ctx ctx, List<Vector3> pts, float[] arcs, System.Func<float, float> widthAt)
        {
            MeshFilter mf = ctx.Ground.GetComponent<MeshFilter>();
            Mesh mesh = Object.Instantiate(mf.sharedMesh);
            Transform gt = ctx.Ground.transform;
            Vector3[] v = mesh.vertices;
            Bounds box = new Bounds(pts[0], Vector3.zero);
            foreach (Vector3 p in pts) box.Encapsulate(p);
            box.Expand(new Vector3(40f, 400f, 40f));
            int changed = 0;
            for (int i = 0; i < v.Length; i++)
            {
                Vector3 w = gt.TransformPoint(v[i]);
                if (!box.Contains(w)) continue;
                float d = DistToPath(w, pts, out float arc, out float wl);
                if (arc < 8f) continue;   // the falls pool is already deep
                float half = widthAt(arc) * 0.5f;
                float y = w.y;
                if (d < half) y = Mathf.Min(y, wl - Mathf.Lerp(1.3f, 0.3f, (d / half) * (d / half)));
                else if (d < half + 3f) y = Mathf.Min(y, Mathf.Lerp(wl - 0.3f, wl + 0.45f, (d - half) / 3f));
                if (y < w.y - 0.001f)
                {
                    w.y = y;
                    v[i] = gt.InverseTransformPoint(w);
                    changed++;
                }
            }
            mesh.vertices = v;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            mesh = SaveMesh(mesh, "ISL2_Ground_Polished");
            mf.sharedMesh = mesh;
            ctx.GroundCollider.sharedMesh = null;
            ctx.GroundCollider.sharedMesh = mesh;
            ctx.Log.Add($"River channel: {changed} ground vertices lowered");
        }

        /// <summary>Hides island plants and props that would now stand in the water.</summary>
        private static int ClearChannel(Ctx ctx, List<Vector3> pts, System.Func<float, float> widthAt)
        {
            int hidden = 0;
            foreach (string g in new[] { "Plants", "Props" })
            {
                Transform group = ctx.Island.Find(g);
                if (group == null) continue;
                foreach (Transform child in group)
                {
                    var r = child.GetComponent<Renderer>();
                    if (r == null || !child.gameObject.activeSelf || child.name.Contains("Bridge") || child.name.Contains("Lily")) continue;
                    Vector3 c = r.bounds.center;
                    float d = DistToPath(c, pts, out float arc, out _);
                    if (arc > 6f && d < widthAt(arc) * 0.5f - 0.3f) { child.gameObject.SetActive(false); hidden++; }
                }
            }
            return hidden;
        }

        /// <summary>Boulders along the waterline and reeds, cattails, horsetails and ferns on the banks.</summary>
        private static int DressBanks(Ctx ctx, Transform parent, List<Vector3> pts, float[] arcs, float origLen, System.Func<float, float> widthAt)
        {
            List<(GameObject prefab, float scale)> Load(string group, string[] kinds, float fallback)
            {
                var list = new List<(GameObject, float)>();
                Transform src = ctx.Island.Find(group);
                foreach (string k in kinds)
                {
                    var prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{PrefabFolder}/{k}.prefab");
                    if (prefab == null) continue;
                    float s = fallback;
                    if (src != null)
                    {
                        var same = src.Cast<Transform>().Where(c => PrefabUtility.GetCorrespondingObjectFromSource(c.gameObject) == prefab).ToList();
                        if (same.Count > 0) s = same.Average(c => c.localScale.y);
                    }
                    list.Add((prefab, s));
                }
                return list;
            }
            var rocks = Load("Props", new[] { "TRN_Boulder_Round", "TRN_Boulder_Split", "TRN_Boulder_Block" }, 1f);
            var plants = Load("Plants", new[] { "PLN_Reeds", "PLN_Cattails", "PLN_Horsetails_Small", "PLN_Horsetails_Large", "PLN_Ferns_Medium", "PLN_Ferns_Small" }, 1.5f);
            if (rocks.Count == 0 && plants.Count == 0) return 0;

            var avoid = new List<Vector3>();
            Transform props = ctx.Island.Find("Props");
            if (props != null)
                foreach (Transform p in props)
                    if (p.name.Contains("Bridge") && p.GetComponent<Renderer>() != null) avoid.Add(p.GetComponent<Renderer>().bounds.center);

            Transform group = Group(parent, "River Banks");
            var rng = new System.Random(808);
            int placed = 0;
            for (float s = 10f; s < origLen - 4f; s += 2.2f)
            {
                int k = ArcIndex(arcs, s);
                Vector3 c = pts[k];
                Vector3 tan = pts[k] - pts[k - 1];
                tan.y = 0f;
                Vector3 side = Vector3.Cross(Vector3.up, tan.normalized);
                float half = widthAt(s) * 0.5f;
                for (int sgn = -1; sgn <= 1; sgn += 2)
                {
                    if (avoid.Any(a => Vector2.Distance(new Vector2(a.x, a.z), new Vector2(c.x, c.z)) < 9f)) continue;
                    bool rock = rng.NextDouble() < 0.42;
                    float off = rock ? half + (float)rng.NextDouble() * 1.4f - 0.3f : half + 1.0f + (float)rng.NextDouble() * 3f;
                    Vector3 at = c + side * (sgn * off) + tan.normalized * ((float)rng.NextDouble() - 0.5f) * 1.5f;
                    float g = GroundY(ctx, at.x, at.z, float.NaN);
                    if (float.IsNaN(g) || g > c.y + 2.5f) continue;                     // cliff or a high bank: leave it
                    if (!rock && g < c.y - 0.05f) continue;                             // plants stay out of the water
                    if (DistToPath(at, RampRoad, out _, out _) < RampHalfWidth + 1.5f) continue;
                    var kinds = rock ? rocks : plants;
                    if (kinds.Count == 0 || (!rock && rng.NextDouble() < 0.25)) continue;
                    var pick = kinds[rng.Next(kinds.Count)];
                    var go = (GameObject)PrefabUtility.InstantiatePrefab(pick.prefab, group);
                    float size = rock ? 0.35f + (float)rng.NextDouble() * 0.55f : 0.75f + (float)rng.NextDouble() * 0.5f;
                    go.transform.SetPositionAndRotation(new Vector3(at.x, g - (rock ? 0.25f : 0.05f), at.z),
                        Quaternion.Euler(rock ? (float)rng.NextDouble() * 20f : 0f, (float)rng.NextDouble() * 360f, 0f));
                    go.transform.localScale = Vector3.one * pick.scale * size;
                    placed++;
                }
            }
            return placed;
        }
    }
}
