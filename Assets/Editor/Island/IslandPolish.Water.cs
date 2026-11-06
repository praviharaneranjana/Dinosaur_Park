using System.Collections.Generic;
using System.Linq;
using System.Text.RegularExpressions;
using UnityEngine;
using UnityEngine.Rendering;

namespace DinoPark.EditorTools
{
    public static partial class IslandPolish
    {
        private const string WaterShader = "DinoPark/Environment/Water";
        private const string FallShader = "DinoPark/Environment/Waterfall";
        private const string ParticleShader = "DinoPark/Environment/SoftParticle";

        /// <summary>River centre line, pool to sea (island_map shapes.river), with half widths.</summary>
        private static readonly Vector3[] RiverLine =
        {
            B(-1.68f, 49.52f, 0), B(-11.07f, 44.91f, 0), B(-21.99f, 41.83f, 0), B(-30.57f, 38.25f, 0), B(-34.43f, 31.25f, 0),
            B(-35.73f, 22.78f, 0), B(-38.47f, 14.91f, 0), B(-44.22f, 9.82f, 0), B(-50.72f, 3.6f, 0), B(-57.71f, -5.12f, 0),
            B(-64.81f, -10.95f, 0), B(-71.73f, -16.62f, 0), B(-77.52f, -22.15f, 0), B(-82.27f, -27.28f, 0), B(-87.25f, -31.5f, 0),
            B(-93.54f, -36.02f, 0), B(-98.95f, -40.44f, 0),
        };

        /// <summary>Plateau stream, spring to the falls lip (island_map shapes.plateau_stream).</summary>
        private static readonly Vector3[] StreamLine =
        {
            B(-24.66f, 88.45f, 0), B(-18.54f, 81.51f, 0), B(-13.31f, 76.42f, 0), B(-12.99f, 73.08f, 0),
            B(-9.06f, 69.79f, 0), B(-4.5f, 66.13f, 0), B(-0.45f, 61.34f, 0),
        };

        private static readonly Regex StrandName = new Regex(@"(Waterfall_\d+|Cascade_\d+|SpringTrickle)", RegexOptions.Compiled);

        // ------------------------------------------------------------------ river, ponds, waterfalls
        private static void RestyleWater(Ctx ctx)
        {
            Transform water = ctx.Island.Find("Water");
            if (water == null) { ctx.Log.Add("Water: group not found"); return; }

            Texture2D normal = ProceduralTextures.WaterNormal;
            Texture2D foam = ProceduralTextures.Foam;
            Material river = Mat("M_Water_River", WaterShader, m => WaterBase(m, normal, foam,
                new Color(0.30f, 0.82f, 0.76f), new Color(0.04f, 0.36f, 0.44f), 1.6f, 0.22f, 0.9f, 0.2f, 0.7f, 1.6f, 0.16f, 0.3f));
            Material pond = Mat("M_Water_Pond", WaterShader, m => WaterBase(m, normal, foam,
                new Color(0.28f, 0.78f, 0.74f), new Color(0.03f, 0.30f, 0.40f), 2.4f, 0.22f, 1.2f, 0.16f, 0.45f, 0.4f, 0.14f, 0.0f));
            Material mud = Mat("M_Water_Mud", WaterShader, m =>
            {
                WaterBase(m, normal, foam, new Color(0.42f, 0.33f, 0.22f), new Color(0.22f, 0.16f, 0.10f), 0.8f, 0.75f, 0.5f, 0.3f, 0.25f, 0.2f, 0.25f, 0f);
                m.SetColor("_FoamColor", new Color(0.62f, 0.54f, 0.42f));
                m.SetFloat("_Reflectivity", 0.25f);
            });
            Material swamp = Mat("M_Water_Swamp", WaterShader, m =>
            {
                WaterBase(m, normal, foam, new Color(0.30f, 0.34f, 0.15f), new Color(0.09f, 0.13f, 0.06f), 1.2f, 0.7f, 0.7f, 0.25f, 0.3f, 0.2f, 0.3f, 0f);
                m.SetColor("_FoamColor", new Color(0.55f, 0.62f, 0.35f));
                m.SetFloat("_Reflectivity", 0.3f);
            });

            // River and plateau stream: Blender's are thin strips (vertices only on the banks), so build
            // new surfaces along the centre lines with a real cross-section, at the Blender water height.
            Transform waterOut = Group(ctx.Polish, "Rivers");
            var blenderRivers = new[] { "ISL2_River", "ISL2_StreamUpper", "ISL2_StreamLower" }
                .Select(n => Find(water, n)).Where(g => g != null).ToList();
            var temp = blenderRivers.Where(g => g.GetComponent<Collider>() == null).Select(g => g.AddComponent<MeshCollider>()).ToList();
            Physics.SyncTransforms();
            var surfaces = blenderRivers.Select(g => g.GetComponent<Collider>()).ToList();
            RiverSurface(ctx, waterOut, "River", RiverLine, t => SampleWidths(RiverWidths, t), 0.65f, river, surfaces, true);
            RiverSurface(ctx, waterOut, "Stream", StreamLine, t => Mathf.Lerp(5.4f, 8.6f, t), 0.95f, river, surfaces, false);
            foreach (MeshCollider c in temp) Object.DestroyImmediate(c);
            foreach (GameObject g in blenderRivers) g.SetActive(false);

            var strands = new List<Renderer>();
            int restyled = 0;
            foreach (Transform child in water)
            {
                var r = child.GetComponent<MeshRenderer>();
                if (r == null || !child.gameObject.activeSelf) continue;
                string n = child.name;
                if (n.StartsWith("ISL_Ocean")) { child.gameObject.SetActive(false); continue; }
                if (n.StartsWith("ISL_Seabed")) continue;
                if (Has(n, "Boil", "Foam", "Mist")) { child.gameObject.SetActive(false); continue; }
                if (StrandName.IsMatch(n)) { strands.Add(r); child.gameObject.SetActive(false); continue; }

                Material mat = Has(n, "Mud") ? mud : Has(n, "Swamp", "Algae") ? swamp : Has(n, "River", "Stream", "Spring") ? river : pond;
                r.sharedMaterial = mat;
                r.shadowCastingMode = ShadowCastingMode.Off;
                var mf = child.GetComponent<MeshFilter>();
                if (mf != null && mf.sharedMesh != null && mf.sharedMesh.isReadable)
                    mf.sharedMesh = FlowMesh(mf.sharedMesh, child, n);
                restyled++;
            }

            int built = BuildWaterfalls(ctx, strands);
            ctx.Log.Add($"Water: {restyled} river/pond/mud pieces restyled, {built} waterfall strands rebuilt");
        }

        private static void WaterBase(Material m, Texture2D normal, Texture2D foam, Color shallow, Color deep, float depthRange,
            float alphaShallow, float alphaDepth, float normalTiling, float normalStrength, float flowSpeed, float edgeFoam, float flowFoam)
        {
            m.DisableKeyword("_OCEAN");
            m.SetFloat("_Ocean", 0f);
            m.SetTexture("_NormalMap", normal);
            m.SetTexture("_FoamTex", foam);
            m.SetColor("_ShallowColor", shallow);
            m.SetColor("_DeepColor", deep);
            m.SetFloat("_DepthRange", depthRange);
            m.SetFloat("_VertexDepthMax", RiverDepthMax);
            m.SetFloat("_AlphaShallow", alphaShallow);
            m.SetFloat("_AlphaDepth", alphaDepth);
            m.SetFloat("_NormalTiling", normalTiling);
            m.SetFloat("_NormalStrength", normalStrength);
            m.SetFloat("_FlowSpeed", flowSpeed);
            m.SetFloat("_FoamTiling", 0.35f);
            m.SetFloat("_EdgeFoamDistance", edgeFoam);
            m.SetFloat("_FlowFoam", flowFoam);
            m.SetFloat("_DriftSpeed", 0.03f);
            m.SetFloat("_Reflectivity", 0.35f);
            m.SetColor("_SkyColor", new Color(0.30f, 0.52f, 0.80f));
            m.SetColor("_HorizonColor", new Color(0.55f, 0.72f, 0.86f));
            m.SetFloat("_SpecPower", 220f);
            m.SetFloat("_SpecIntensity", 1.6f);
            m.renderQueue = (int)RenderQueue.Transparent - 10;
        }

        /// <summary>Copies a water mesh and writes the flow field into vertex colours (RG dir, B speed).</summary>
        private static Mesh FlowMesh(Mesh source, Transform t, string name)
        {
            Mesh mesh = Object.Instantiate(source);
            Vector3[] v = mesh.vertices;
            var c = new Color[v.Length];
            float[] bankDepth = BankDepth(mesh, t, name.Contains("Mud") || name.Contains("Puddle") ? 0.25f : 0.38f, 3.6f);
            for (int i = 0; i < v.Length; i++)
            {
                Vector3 w = t.TransformPoint(v[i]);
                Vector2 dir = Vector2.zero;
                float speed = 0f;
                if (FlowAt(w, RiverLine, 9f, out Vector2 d1, out float near1)) { dir = d1; speed = 0.65f; }
                if (FlowAt(w, StreamLine, 7f, out Vector2 d2, out float near2) && (speed == 0f || near2 < near1))
                {
                    dir = d2;
                    float toLip = Vector2.Distance(new Vector2(w.x, w.z), new Vector2(StreamLine[StreamLine.Length - 1].x, StreamLine[StreamLine.Length - 1].z));
                    speed = Mathf.Lerp(1f, 0.7f, Mathf.Clamp01(toLip / 25f));
                }
                if (name.Contains("Spring")) speed *= 0.4f;
                c[i] = new Color(dir.x * 0.5f + 0.5f, dir.y * 0.5f + 0.5f, speed, bankDepth[i] / RiverDepthMax);
            }
            mesh.colors = c;
            return SaveMesh(mesh, "Water_" + name);
        }

        private const float RiverDepthMax = 4f;

        /// <summary>River widths per centre-line point (island_map shapes.river_w).</summary>
        private static readonly float[] RiverWidths = { 8f, 7f, 7f, 7f, 7f, 7f, 7.5f, 7.5f, 8f, 8f, 8.5f, 8.5f, 9f, 9f, 10f, 12f, 14f };

        private static float SampleWidths(float[] w, float t)
        {
            float f = Mathf.Clamp01(t) * (w.Length - 1);
            int i = Mathf.Min((int)f, w.Length - 2);
            return Mathf.Lerp(w[i], w[i + 1], f - i);
        }

        /// <summary>
        /// Water surface along a centre line: 9 vertices across (overlapping the banks by 0.6 m each side),
        /// surface height ray-cast from the Blender water and never rising downstream, flow along the line,
        /// depth profile deepest mid-channel (vertex A) so bank foam sits on the real bank line.
        /// </summary>
        private static void RiverSurface(Ctx ctx, Transform parent, string name, Vector3[] line, System.Func<float, float> widthAt,
            float speed, Material mat, List<Collider> surfaces, bool toSea)
        {
            List<Vector3> pts = Resample(line, 1.5f);
            for (int it = 0; it < 4; it++)
            {
                var copy = new List<Vector3>(pts);
                for (int i = 1; i < pts.Count - 1; i++) pts[i] = (copy[i - 1] + copy[i] * 2f + copy[i + 1]) * 0.25f;
            }
            int n = pts.Count;
            var ys = new float[n];
            float last = float.NaN;
            for (int i = 0; i < n; i++)
            {
                float best = float.NegativeInfinity;
                var ray = new Ray(new Vector3(pts[i].x, 200f, pts[i].z), Vector3.down);
                foreach (Collider c in surfaces)
                    if (c.Raycast(ray, out RaycastHit hit, 400f)) best = Mathf.Max(best, hit.point.y);
                if (float.IsNegativeInfinity(best)) best = float.IsNaN(last) ? GroundY(ctx, pts[i].x, pts[i].z, 0f) + 0.25f : last;
                if (!float.IsNaN(last)) best = Mathf.Min(best, last);
                if (toSea) best = Mathf.Max(best, SeaLevel + 0.03f);
                ys[i] = last = best;
            }

            const int across = 9;
            var v = new List<Vector3>();
            var col = new List<Color>();
            var tris = new List<int>();
            for (int i = 0; i < n; i++)
            {
                Vector3 tan = pts[Mathf.Min(i + 1, n - 1)] - pts[Mathf.Max(i - 1, 0)];
                tan.y = 0f;
                tan.Normalize();
                Vector3 side = Vector3.Cross(Vector3.up, tan);
                float w = widthAt(i / (float)(n - 1));
                float deepest = Mathf.Min(w * 0.17f, 2.5f);
                for (int k = 0; k < across; k++)
                {
                    float off = (k / (float)(across - 1) - 0.5f) * (w + 1.2f);
                    float a = Mathf.Clamp01(1f - Mathf.Abs(off) / (w * 0.5f));
                    v.Add(new Vector3(pts[i].x, ys[i], pts[i].z) + side * off);
                    col.Add(new Color(tan.x * 0.5f + 0.5f, tan.z * 0.5f + 0.5f, speed * (0.4f + 0.6f * a), Mathf.Pow(a, 0.6f) * deepest / RiverDepthMax));
                }
                if (i > 0)
                {
                    int b0 = (i - 1) * across, b1 = i * across;
                    for (int k = 0; k < across - 1; k++)
                        tris.AddRange(new[] { b0 + k, b1 + k, b0 + k + 1, b0 + k + 1, b1 + k, b1 + k + 1 });
                }
            }
            var mesh = new Mesh();
            mesh.SetVertices(v);
            mesh.SetColors(col);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            // normals must face up
            if (mesh.normals.Length > 0 && mesh.normals[across / 2].y < 0f)
            {
                for (int i = 0; i < tris.Count; i += 3) (tris[i + 1], tris[i + 2]) = (tris[i + 2], tris[i + 1]);
                mesh.SetTriangles(tris, 0);
                mesh.RecalculateNormals();
            }
            MeshObject(name, parent, SaveMesh(mesh, "Water_" + name), new[] { mat }, false, ShadowCastingMode.Off);
        }

        /// <summary>
        /// Depth estimate per vertex from its XZ distance to the mesh outline (open edges), in metres:
        /// 0 at the bank, <paramref name="slope"/> m deeper per metre inward, capped. Vertices are matched
        /// by position so split normals do not create fake open edges.
        /// </summary>
        private static float[] BankDepth(Mesh mesh, Transform t, float slope, float max)
        {
            Vector3[] v = mesh.vertices;
            int[] tri = mesh.triangles;
            var key = new int[v.Length];
            var byPos = new Dictionary<Vector3Int, int>();
            for (int i = 0; i < v.Length; i++)
            {
                var k = Vector3Int.RoundToInt(v[i] * 200f);
                if (!byPos.TryGetValue(k, out int id)) byPos[k] = id = i;
                key[i] = id;
            }
            var edges = new Dictionary<long, int>();
            for (int i = 0; i < tri.Length; i += 3)
            for (int e = 0; e < 3; e++)
            {
                int a = key[tri[i + e]], b = key[tri[i + (e + 1) % 3]];
                long k = a < b ? ((long)a << 32) | (uint)b : ((long)b << 32) | (uint)a;
                edges[k] = edges.TryGetValue(k, out int n) ? n + 1 : 1;
            }
            var open = new List<(Vector2, Vector2)>();
            foreach (var kv in edges)
            {
                if (kv.Value != 1) continue;
                Vector3 a = t.TransformPoint(v[(int)(kv.Key >> 32)]), b = t.TransformPoint(v[(int)(kv.Key & 0xffffffff)]);
                open.Add((new Vector2(a.x, a.z), new Vector2(b.x, b.z)));
            }
            var depth = new float[v.Length];
            for (int i = 0; i < v.Length; i++)
            {
                Vector3 w = t.TransformPoint(v[i]);
                var q = new Vector2(w.x, w.z);
                float best = float.MaxValue;
                foreach (var (a, b) in open)
                {
                    Vector2 ab = b - a;
                    float s = Mathf.Clamp01(Vector2.Dot(q - a, ab) / Mathf.Max(ab.sqrMagnitude, 1e-6f));
                    best = Mathf.Min(best, Vector2.Distance(q, a + ab * s));
                }
                depth[i] = open.Count == 0 ? max : Mathf.Min(best * slope, max);
            }
            return depth;
        }

        private static bool FlowAt(Vector3 w, Vector3[] line, float reach, out Vector2 dir, out float dist)
        {
            dir = Vector2.zero; dist = float.MaxValue;
            var q = new Vector2(w.x, w.z);
            for (int i = 0; i < line.Length - 1; i++)
            {
                Vector2 a = new Vector2(line[i].x, line[i].z), b = new Vector2(line[i + 1].x, line[i + 1].z);
                Vector2 ab = b - a;
                float t = Mathf.Clamp01(Vector2.Dot(q - a, ab) / Mathf.Max(ab.sqrMagnitude, 1e-5f));
                float d = Vector2.Distance(q, a + ab * t);
                if (d < dist)
                {
                    dist = d;
                    // blend with the next segment near the joint so the flow turns smoothly
                    Vector2 here = ab.normalized;
                    Vector2 next = i + 2 < line.Length ? new Vector2(line[i + 2].x - line[i + 1].x, line[i + 2].z - line[i + 1].z).normalized : here;
                    dir = Vector2.Lerp(here, next, Mathf.SmoothStep(0.6f, 1f, t)).normalized;
                }
            }
            return dist < reach;
        }

        // ------------------------------------------------------------------ waterfalls
        private static int BuildWaterfalls(Ctx ctx, List<Renderer> strands)
        {
            if (strands.Count == 0) return 0;
            Transform root = Group(ctx.Polish, "Waterfalls");
            Texture2D streaks = ProceduralTextures.Streaks;
            Texture2D foam = ProceduralTextures.Foam;
            Material curtain = Mat("M_Waterfall", FallShader, m =>
            {
                m.DisableKeyword("_RADIAL");
                m.SetFloat("_Radial", 0f);
                m.SetTexture("_StreakTex", streaks);
                m.SetTexture("_FoamTex", foam);
                m.SetColor("_TopColor", new Color(0.36f, 0.76f, 0.78f));
                m.SetColor("_MidColor", new Color(0.66f, 0.88f, 0.92f));
                m.SetFloat("_FallSpeed", 7.5f);
                m.SetVector("_StreakTiling", new Vector4(2.6f, 0.11f, 0, 0));
                m.SetFloat("_Alpha", 0.92f);
                m.SetFloat("_FoamStart", 0.5f);
                m.SetFloat("_Wobble", 0.06f);
            });
            Material plunge = Mat("M_Waterfall_Plunge", FallShader, m =>
            {
                m.EnableKeyword("_RADIAL");
                m.SetFloat("_Radial", 1f);
                m.SetTexture("_StreakTex", streaks);
                m.SetTexture("_FoamTex", foam);
                m.SetColor("_MidColor", new Color(0.62f, 0.87f, 0.88f));
                m.SetFloat("_Alpha", 0.95f);
                m.SetFloat("_Wobble", 0f);
            });
            Material spray = Mat("M_Waterfall_Spray", ParticleShader, m =>
            {
                m.SetTexture("_BaseMap", ProceduralTextures.Mist);
                m.SetColor("_BaseColor", new Color(1f, 1f, 1f, 0.6f));
                m.SetFloat("_SoftDistance", 1.2f);
                m.renderQueue = (int)RenderQueue.Transparent + 10;
            });
            Material mist = Mat("M_Waterfall_Mist", ParticleShader, m =>
            {
                m.SetTexture("_BaseMap", ProceduralTextures.Mist);
                m.SetColor("_BaseColor", new Color(0.95f, 0.98f, 1f, 0.16f));
                m.SetFloat("_SoftDistance", 3f);
                m.renderQueue = (int)RenderQueue.Transparent + 11;
            });

            int built = 0;
            var hiddenRocks = 0;
            foreach (Renderer r in strands)
            {
                Mesh src = r.GetComponent<MeshFilter>().sharedMesh;
                if (src == null || !src.isReadable) continue;
                Vector3[] w = src.vertices.Select(v => r.transform.TransformPoint(v)).ToArray();
                float top = w.Max(p => p.y), bottom = w.Min(p => p.y);
                float H = top - bottom;
                if (H < 0.8f) continue;
                Vector3 lip = Avg(w.Where(p => p.y > top - Mathf.Max(0.4f, H * 0.04f)));
                Vector3 baseC = Avg(w.Where(p => p.y < bottom + Mathf.Max(0.4f, H * 0.04f)));
                Vector3 flow = new Vector3(baseC.x - lip.x, 0, baseC.z - lip.z);
                float D = flow.magnitude;
                flow = D > 0.05f ? flow / D : r.transform.forward;
                Vector3 side = Vector3.Cross(Vector3.up, flow).normalized;
                float width = Mathf.Max(1.0f, ExtentAlong(w.Where(p => p.y > top - H * 0.15f), side));
                D = Mathf.Max(D, H * 0.12f);

                Transform fall = Group(root, "Fall_" + r.name);
                Mesh sheet = CurtainMesh(lip, flow, side, width, H, D);
                MeshObject("Curtain", fall, SaveMesh(sheet, "Fall_" + r.name), new[] { curtain }, false, ShadowCastingMode.Off);

                float poolY = bottom + 0.12f;
                Vector3 impact = new Vector3(lip.x + flow.x * D, poolY, lip.z + flow.z * D);
                float radius = width * 1.1f + Mathf.Clamp(H * 0.12f, 0.6f, 2.5f);
                MeshObject("Plunge", fall, SaveMesh(DiscMesh(impact + Vector3.up * 0.04f, radius), "Plunge_" + r.name), new[] { plunge }, false, ShadowCastingMode.Off);

                float k = Mathf.Clamp(width / 4f, 0.35f, 1.6f) * Mathf.Clamp(H / 12f, 0.5f, 1.3f);
                AddParticles(fall, "Spray", impact, side, width, spray, k, mistMode: false);
                AddParticles(fall, "Mist", impact + Vector3.up * 0.5f, side, width, mist, k, mistMode: true);
                built++;

                // Rocks the Blender build left hanging in front of the falling water.
                Transform props = ctx.Island.Find("Props");
                if (props != null)
                {
                    foreach (Transform p in props)
                    {
                        var pr = p.GetComponent<Renderer>();
                        if (pr == null || !p.gameObject.activeSelf) continue;
                        Vector3 c = pr.bounds.center;
                        if (c.y < bottom + 1.5f || c.y > top - 2.0f) continue;
                        Vector3 rel = c - lip;
                        float along = Vector3.Dot(rel, flow), across = Mathf.Abs(Vector3.Dot(rel, side));
                        if (across < width * 0.75f + 1f && along > -0.5f && along < D + 2.5f) { p.gameObject.SetActive(false); hiddenRocks++; }
                    }
                }
            }
            ctx.Log.Add($"Waterfalls: {built} curtains, {hiddenRocks} mid-air rocks hidden");
            return built;
        }

        private static Vector3 Avg(IEnumerable<Vector3> pts)
        {
            Vector3 s = Vector3.zero; int n = 0;
            foreach (Vector3 p in pts) { s += p; n++; }
            return n > 0 ? s / n : Vector3.zero;
        }

        private static float ExtentAlong(IEnumerable<Vector3> pts, Vector3 axis)
        {
            float lo = float.MaxValue, hi = float.MinValue;
            foreach (Vector3 p in pts) { float d = Vector3.Dot(p, axis); lo = Mathf.Min(lo, d); hi = Mathf.Max(hi, d); }
            return hi > lo ? hi - lo : 0f;
        }

        /// <summary>
        /// Two-layer water curtain: flat run over the lip, then a ballistic fall (horizontal ~ sqrt of drop),
        /// widening slightly toward the bottom. uv.y = 0 at the lip, uv2.x = length in metres.
        /// </summary>
        private static Mesh CurtainMesh(Vector3 lip, Vector3 flow, Vector3 side, float width, float H, float D)
        {
            const int rows = 30, cols = 10;
            float length = H + D + 1.2f;
            var verts = new List<Vector3>();
            var uvs = new List<Vector2>();
            var uv2 = new List<Vector2>();
            var tris = new List<int>();
            for (int layer = 0; layer < 2; layer++)
            {
                float push = layer == 0 ? 0.25f : -0.2f;
                float wScale = layer == 0 ? 1f : 0.86f;
                int start = verts.Count;
                for (int r = 0; r <= rows; r++)
                {
                    float v = r / (float)rows;
                    Vector3 centre;
                    float wr;
                    if (v < 0.06f)
                    {
                        float a = v / 0.06f;                                  // over the lip
                        centre = lip - flow * (1.2f * (1f - a)) + Vector3.up * (0.08f * (1f - a));
                        wr = width;
                    }
                    else
                    {
                        float f = (v - 0.06f) / 0.94f;
                        centre = lip + flow * (D * Mathf.Sqrt(f) + push * f) - Vector3.up * (H * f);
                        wr = width * (1f + 0.3f * f);
                    }
                    for (int c = 0; c <= cols; c++)
                    {
                        float u = c / (float)cols;
                        float bulge = Mathf.Sin(u * Mathf.PI) * 0.18f * (layer == 0 ? 1f : -1f);
                        verts.Add(centre + side * ((u - 0.5f) * wr * wScale) + flow * bulge);
                        uvs.Add(new Vector2(u, Mathf.Max(0f, v)));
                        uv2.Add(new Vector2(length, layer));
                    }
                }
                for (int r = 0; r < rows; r++)
                for (int c = 0; c < cols; c++)
                {
                    int a = start + r * (cols + 1) + c, b = a + 1, d = a + cols + 1, e = d + 1;
                    tris.AddRange(new[] { a, d, b, b, d, e });
                }
            }
            var mesh = new Mesh();
            mesh.SetVertices(verts);
            mesh.SetUVs(0, uvs);
            mesh.SetUVs(1, uv2);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        /// <summary>Flat foam disc for the plunge pool: uv.x = angle 0..1, uv.y = radius 0..1.</summary>
        private static Mesh DiscMesh(Vector3 centre, float radius)
        {
            const int seg = 40, rings = 6;
            var verts = new List<Vector3>();
            var uvs = new List<Vector2>();
            var uv2 = new List<Vector2>();
            var tris = new List<int>();
            for (int r = 0; r <= rings; r++)
            for (int s = 0; s <= seg; s++)
            {
                float rr = r / (float)rings, a = s / (float)seg * Mathf.PI * 2f;
                float wob = 1f + 0.12f * Mathf.Sin(a * 5f + 1.3f) * rr;
                verts.Add(centre + new Vector3(Mathf.Cos(a), 0, Mathf.Sin(a)) * (radius * rr * wob));
                uvs.Add(new Vector2(s / (float)seg, rr));
                uv2.Add(new Vector2(radius * 4f, 0));
            }
            for (int r = 0; r < rings; r++)
            for (int s = 0; s < seg; s++)
            {
                int a = r * (seg + 1) + s, b = a + 1, c = a + seg + 1, d = c + 1;
                tris.AddRange(new[] { a, c, b, b, c, d });
            }
            var mesh = new Mesh();
            mesh.SetVertices(verts);
            mesh.SetUVs(0, uvs);
            mesh.SetUVs(1, uv2);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            return mesh;
        }

        private static void AddParticles(Transform parent, string name, Vector3 at, Vector3 side, float width, Material mat, float k, bool mistMode)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.transform.position = at;
            go.transform.rotation = Quaternion.LookRotation(Vector3.Cross(side, Vector3.up), Vector3.up);   // local X = side
            var ps = go.AddComponent<ParticleSystem>();
            ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);

            var main = ps.main;
            main.loop = true;
            main.prewarm = true;
            main.playOnAwake = true;
            main.simulationSpace = ParticleSystemSimulationSpace.World;
            main.startLifetime = mistMode ? new ParticleSystem.MinMaxCurve(5f, 8f) : new ParticleSystem.MinMaxCurve(1.4f, 2.6f);
            main.startSpeed = mistMode ? new ParticleSystem.MinMaxCurve(0.3f, 1.2f) : new ParticleSystem.MinMaxCurve(1.5f * k + 1f, 3.5f * k + 1.5f);
            main.startSize = mistMode ? new ParticleSystem.MinMaxCurve(5f * k + 2f, 10f * k + 3f) : new ParticleSystem.MinMaxCurve(1.0f * k + 0.6f, 2.6f * k + 0.8f);
            main.startRotation = new ParticleSystem.MinMaxCurve(0f, Mathf.PI * 2f);
            main.gravityModifier = mistMode ? -0.015f : 0.12f;
            main.maxParticles = mistMode ? 40 : 160;
            main.startColor = Color.white;

            var emission = ps.emission;
            emission.rateOverTime = mistMode ? 5f * k + 1f : 40f * k + 6f;

            var shape = ps.shape;
            shape.shapeType = ParticleSystemShapeType.Box;
            shape.scale = new Vector3(width * 1.1f, 0.4f, Mathf.Max(1f, width * 0.35f));
            shape.rotation = new Vector3(-90f, 0f, 0f);   // emit upward
            shape.randomDirectionAmount = mistMode ? 0.6f : 0.35f;

            var vel = ps.velocityOverLifetime;
            vel.enabled = true;
            vel.space = ParticleSystemSimulationSpace.World;
            vel.y = new ParticleSystem.MinMaxCurve(mistMode ? 0.25f : 0.1f);
            vel.x = new ParticleSystem.MinMaxCurve(0f);
            vel.z = new ParticleSystem.MinMaxCurve(0f);

            var col = ps.colorOverLifetime;
            col.enabled = true;
            var g = new Gradient();
            g.SetKeys(new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                new[] { new GradientAlphaKey(0f, 0f), new GradientAlphaKey(1f, 0.15f), new GradientAlphaKey(0.6f, 0.6f), new GradientAlphaKey(0f, 1f) });
            col.color = g;

            var size = ps.sizeOverLifetime;
            size.enabled = true;
            size.size = new ParticleSystem.MinMaxCurve(1f, AnimationCurve.Linear(0f, 0.6f, 1f, mistMode ? 1.8f : 2.2f));

            var rot = ps.rotationOverLifetime;
            rot.enabled = true;
            rot.z = new ParticleSystem.MinMaxCurve(-0.4f, 0.4f);

            var renderer = go.GetComponent<ParticleSystemRenderer>();
            renderer.sharedMaterial = mat;
            renderer.renderMode = ParticleSystemRenderMode.Billboard;
            renderer.sortingFudge = mistMode ? -2f : 0f;
            renderer.shadowCastingMode = ShadowCastingMode.Off;
            renderer.receiveShadows = false;
            ps.Play();
        }

        // ------------------------------------------------------------------ ocean
        /// <summary>
        /// Wave ocean around the island. Water depth under each vertex is baked into vertex colour R by
        /// ray casts against the terrain, cliff, mountain, rocks and the Blender seabed; water not
        /// connected to the open sea (inland hollows below sea level) gets alpha 0.
        /// </summary>
        private static void BuildOcean(Ctx ctx)
        {
            Transform water = ctx.Island.Find("Water");
            GameObject seabed = water != null ? Find(water, "ISL_Seabed") : null;
            MeshCollider tempCollider = null;
            if (seabed != null && seabed.GetComponent<Collider>() == null)
                tempCollider = seabed.AddComponent<MeshCollider>();
            Physics.SyncTransforms();

            List<float> xs = Axis(-560f, 560f, -190f, 175f, 2f, 14f);
            List<float> zs = Axis(-430f, 560f, -215f, 200f, 2f, 14f);
            int nx = xs.Count, nz = zs.Count;
            var verts = new Vector3[nx * nz];
            var depth = new float[nx * nz];
            var land = new bool[nx * nz];
            var seabedDepth = new float[nx * nz];
            const float maxDepth = 40f;
            for (int j = 0; j < nz; j++)
            for (int i = 0; i < nx; i++)
            {
                int id = j * nx + i;
                verts[id] = new Vector3(xs[i], SeaLevel, zs[j]);
                float d = maxDepth;
                if (Physics.Raycast(new Vector3(xs[i], 300f, zs[j]), Vector3.down, out RaycastHit hit, 360f, ~0, QueryTriggerInteraction.Ignore))
                    d = Mathf.Clamp(SeaLevel - hit.point.y, 0f, maxDepth);
                seabedDepth[id] = d;
                land[id] = d <= 0.02f;
            }
            if (tempCollider != null) Object.DestroyImmediate(tempCollider);

            // Depth from the distance to the shore (two-pass chamfer on the uneven grid), so the sea
            // deepens smoothly instead of jumping where the Blender seabed mesh ends; reefs and
            // sandbanks of the seabed still show where they are shallower.
            var dist = new float[nx * nz];
            for (int id = 0; id < dist.Length; id++) dist[id] = land[id] ? 0f : 1e9f;
            void Relax(int id, int nb)
            {
                float dd = dist[nb] + Vector3.Distance(verts[id], verts[nb]);
                if (dd < dist[id]) dist[id] = dd;
            }
            for (int j = 0; j < nz; j++)
            for (int i = 0; i < nx; i++)
            {
                int id = j * nx + i;
                if (i > 0) Relax(id, id - 1);
                if (j > 0) { Relax(id, id - nx); if (i > 0) Relax(id, id - nx - 1); if (i < nx - 1) Relax(id, id - nx + 1); }
            }
            for (int j = nz - 1; j >= 0; j--)
            for (int i = nx - 1; i >= 0; i--)
            {
                int id = j * nx + i;
                if (i < nx - 1) Relax(id, id + 1);
                if (j < nz - 1) { Relax(id, id + nx); if (i < nx - 1) Relax(id, id + nx + 1); if (i > 0) Relax(id, id + nx - 1); }
            }
            for (int id = 0; id < depth.Length; id++)
            {
                if (land[id]) { depth[id] = 0f; continue; }
                float dd = dist[id];
                float wobble = (ProceduralTextures.WorldFbm(verts[id].x * 0.02f, verts[id].z * 0.02f, 2, 1f, 47) - 0.5f) * 6f;
                float shore = Mathf.Max(0.25f, 0.25f + dd * 0.11f + dd * dd * 0.0011f + wobble * Mathf.Clamp01(dd / 40f));
                float reef = seabedDepth[id] < maxDepth - 0.1f ? seabedDepth[id] : maxDepth;
                depth[id] = Mathf.Clamp(dd < 45f ? Mathf.Min(shore, Mathf.Lerp(reef, shore, dd / 45f)) : shore, 0.05f, maxDepth);
            }

            // flood fill the open sea from the border
            var open = new bool[nx * nz];
            var queue = new Queue<int>();
            for (int i = 0; i < nx; i++) { Seed(i); Seed((nz - 1) * nx + i); }
            for (int j = 0; j < nz; j++) { Seed(j * nx); Seed(j * nx + nx - 1); }
            void Seed(int id)
            {
                if (open[id] || depth[id] <= 0.02f) return;
                open[id] = true;
                queue.Enqueue(id);
            }
            while (queue.Count > 0)
            {
                int id = queue.Dequeue();
                int i = id % nx, j = id / nx;
                if (i > 0) Seed(id - 1);
                if (i < nx - 1) Seed(id + 1);
                if (j > 0) Seed(id - nx);
                if (j < nz - 1) Seed(id + nx);
            }

            var colors = new Color[nx * nz];
            int inland = 0;
            for (int id = 0; id < colors.Length; id++)
            {
                bool hiddenWater = depth[id] > 0.02f && !open[id];
                if (hiddenWater) inland++;
                colors[id] = new Color(depth[id] / maxDepth, 0f, 0f, hiddenWater ? 0f : 1f);
            }

            var tris = new int[(nx - 1) * (nz - 1) * 6];
            int t = 0;
            for (int j = 0; j < nz - 1; j++)
            for (int i = 0; i < nx - 1; i++)
            {
                int a = j * nx + i, b = a + 1, c = a + nx, d = c + 1;
                tris[t++] = a; tris[t++] = c; tris[t++] = b;
                tris[t++] = b; tris[t++] = c; tris[t++] = d;
            }
            var mesh = new Mesh { indexFormat = IndexFormat.UInt32 };
            mesh.vertices = verts;
            mesh.colors = colors;
            mesh.triangles = tris;
            mesh.normals = Enumerable.Repeat(Vector3.up, verts.Length).ToArray();
            mesh.RecalculateBounds();
            Bounds bb = mesh.bounds;
            bb.Expand(new Vector3(0f, 6f, 0f));
            mesh.bounds = bb;
            mesh = SaveMesh(mesh, "Ocean");

            Material ocean = Mat("M_Water_Ocean", WaterShader, m =>
            {
                m.EnableKeyword("_OCEAN");
                m.SetFloat("_Ocean", 1f);
                m.SetTexture("_NormalMap", ProceduralTextures.WaterNormal);
                m.SetTexture("_FoamTex", ProceduralTextures.Foam);
                m.SetColor("_ShallowColor", new Color(0.26f, 0.88f, 0.82f));
                m.SetColor("_DeepColor", new Color(0.02f, 0.19f, 0.40f));
                m.SetFloat("_DepthRange", 16f);
                m.SetFloat("_AlphaShallow", 0.22f);
                m.SetFloat("_AlphaDepth", 3.5f);
                m.SetFloat("_VertexDepthMax", maxDepth);
                m.SetFloat("_NormalTiling", 0.07f);
                m.SetFloat("_NormalStrength", 0.55f);
                m.SetFloat("_DriftSpeed", 0.05f);
                m.SetFloat("_FoamTiling", 0.14f);
                m.SetFloat("_EdgeFoamDistance", 1.4f);
                m.SetFloat("_SurfRange", 4.5f);
                m.SetFloat("_SurfFrequency", 2.4f);
                m.SetFloat("_SurfSpeed", 1.3f);
                m.SetFloat("_SurfStrength", 0.85f);
                m.SetFloat("_WaveAmp", 1f);
                m.SetFloat("_WaveSpeed", 1f);
                m.SetVector("_WaveDir", new Vector4(0.35f, 0f, -1f, 0f));
                m.SetFloat("_Reflectivity", 0.38f);
                m.SetColor("_SkyColor", new Color(0.24f, 0.45f, 0.76f));
                m.SetColor("_HorizonColor", new Color(0.45f, 0.64f, 0.82f));
                m.SetFloat("_SpecPower", 200f);
                m.SetFloat("_SpecIntensity", 1.4f);
                m.renderQueue = (int)RenderQueue.Transparent - 20;
            });
            MeshObject("Ocean", Group(ctx.Polish, "Water"), mesh, new[] { ocean }, false, ShadowCastingMode.Off)
                .GetComponent<MeshRenderer>().receiveShadows = true;
            ctx.Log.Add($"Ocean: {nx}x{nz} grid, {inland} inland vertices hidden (Blender ocean disabled)");
        }

        /// <summary>Coordinates from lo to hi: fine spacing inside [innerLo, innerHi], coarse outside.</summary>
        private static List<float> Axis(float lo, float hi, float innerLo, float innerHi, float fine, float coarse)
        {
            var a = new List<float>();
            for (float x = lo; x < innerLo; x += coarse) a.Add(x);
            for (float x = innerLo; x < innerHi; x += fine) a.Add(x);
            for (float x = innerHi; x <= hi; x += coarse) a.Add(x);
            return a;
        }
    }
}
