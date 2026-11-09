using System.Collections.Generic;
using System.Linq;
using DinoPark.CameraControl;
using DinoPark.Environment;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace DinoPark.EditorTools
{
    public static partial class IslandPolish
    {
        private const string CarFolder = "Assets/Models/Vehicles/Cars";
        private const string CameraConfigPath = "Assets/Data/Camera/IslandCameraConfig.asset";

        /// <summary>Mainland ground height (m) away from the coast.</summary>
        private const float LandLevel = 1.0f;
        /// <summary>Highway centre line (Unity z) and half width (4 lanes of 3.5 m plus kerbs).</summary>
        private const float HighwayZ = -215f;
        private const float HighwayHalfWidth = 7.5f;
        private const float HighwayReach = 640f;
        /// <summary>Park entrance gate across the park road (Unity z).</summary>
        private const float GateZ = -128f;
        private const float ParkRoadHalfWidth = 3.5f;

        private static readonly Color Concrete = new Color(0.93f, 0.90f, 0.82f);   // off-white concrete #F4EDD8 (slightly darker)
        private static readonly Color Brass = new Color(0.95f, 0.72f, 0.29f);      // brass gold #F2B84B
        private static readonly Color Timber = new Color(0.78f, 0.60f, 0.39f);     // light timber #C79A63
        private static readonly Color Steel = new Color(0.23f, 0.28f, 0.26f);      // charcoal steel #3B4743
        private static readonly Color Glass = new Color(0.56f, 0.80f, 0.80f);      // teal glass #8FCBCB
        private static readonly Color LivingGreen = new Color(0.37f, 0.61f, 0.29f);// living roof #5E9B4A
        private static readonly Color Amber = new Color(1f, 0.67f, 0.2f);          // amber glow #FFAA33

        // ------------------------------------------------------------------ mainland
        /// <summary>Mainland coastline (Unity z of the waterline) at x: hugs the headland neck, then curves away south.</summary>
        private static float CoastZ(float x)
        {
            float ax = Mathf.Abs(x);
            float wiggle = (ProceduralTextures.WorldFbm(x * 0.01f, 0.73f, 3, 1f, 41) - 0.5f) * 16f;
            float far = -150f - 28f * Mathf.SmoothStep(0f, 1f, (ax - 120f) / 160f) + wiggle;
            return Mathf.Lerp(-114f, far, Mathf.SmoothStep(0f, 1f, (ax - 60f) / 80f));
        }

        /// <summary>
        /// Mainland height before roads are cut in: sea floor offshore, a sandy shore, then low farmland
        /// with gentle hills that flatten out near the highway and the park road.
        /// </summary>
        private static float MainlandRaw(float x, float z)
        {
            float d = CoastZ(x) - z;   // metres inland
            float shore = Mathf.SmoothStep(0f, 1f, (d + 12f) / 34f);
            float clearHighway = Mathf.SmoothStep(0f, 1f, (Mathf.Abs(z - HighwayZ) - 14f) / 31f);
            float clearRoad = z > HighwayZ ? Mathf.SmoothStep(0f, 1f, (Mathf.Abs(x) - 14f) / 26f) : 1f;
            float hills = Mathf.Max(-1f, (ProceduralTextures.WorldFbm(x * 0.012f, z * 0.012f, 3, 1f, 53) - 0.42f) * 7f);
            float inland = Mathf.SmoothStep(0f, 1f, (d - 30f) / 80f) * Mathf.Min(clearHighway, clearRoad);
            float bumps = (ProceduralTextures.WorldFbm(x * 0.05f, z * 0.05f, 2, 1f, 59) - 0.5f) * 0.5f;
            float land = LandLevel + hills * inland + bumps * shore * Mathf.Min(clearHighway, clearRoad);
            return Mathf.Lerp(SeaLevel - 3.5f, land, shore);
        }

        /// <summary>
        /// The land side: the headland's neck joins flat mainland that runs east-west along the whole
        /// south edge, with a beach where it meets the sea, scattered trees, and room for the highway.
        /// Replaces the old mountain and tunnel.
        /// </summary>
        private static void BuildMainland(Ctx ctx)
        {
            foreach (string old in new[] { "Mountain_South", "Tunnel_Headwall", "Tunnel_Tube" })
                AssetDatabase.DeleteAsset($"{GeneratedFolder}/{old}.asset");
            foreach (string old in new[] { "M_Mountain", "M_Tunnel_Concrete", "M_Tunnel_Inside" })
                AssetDatabase.DeleteAsset($"{MaterialFolder}/{old}.mat");

            Transform land = Group(ctx.Polish, "Land Side");
            const float x0 = -HighwayReach, x1 = HighwayReach, z0 = -440f, z1 = -100f, step = 4f;
            int nx = Mathf.RoundToInt((x1 - x0) / step) + 1, nz = Mathf.RoundToInt((z1 - z0) / step) + 1;
            var verts = new Vector3[nx * nz];
            for (int j = 0; j < nz; j++)
            for (int i = 0; i < nx; i++)
            {
                float x = x0 + i * step, z = z0 + j * step;
                var w = new Vector3(x, 0f, z);
                float y = MainlandRaw(x, z);
                y = Flatten(w, y, ctx.Highway, HighwayHalfWidth + 1f, 10f);
                y = Flatten(w, y, ctx.EntranceProfile, RoadHalfWidth, RoadShoulder);
                verts[j * nx + i] = new Vector3(x, y - 0.05f, z);   // just under the island ground where they overlap
            }
            var tris = new List<int>((nx - 1) * (nz - 1) * 6);
            for (int j = 0; j < nz - 1; j++)
            for (int i = 0; i < nx - 1; i++)
            {
                int a = j * nx + i, b = a + 1, c = a + nx, d = c + 1;
                tris.AddRange(new[] { a, c, b, b, c, d });
            }
            var mesh = new Mesh { indexFormat = IndexFormat.UInt32 };
            mesh.vertices = verts;
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            var colors = new Color[verts.Length];
            for (int i = 0; i < verts.Length; i++)
            {
                Vector3 p = verts[i];
                float n = ProceduralTextures.WorldFbm(p.x * 0.03f, p.z * 0.03f, 3, 1f, 23);
                float patch = ProceduralTextures.WorldFbm(p.x * 0.008f, p.z * 0.008f, 2, 1f, 61);
                Color grass = Color.Lerp(new Color(0.38f, 0.55f, 0.22f), new Color(0.53f, 0.66f, 0.30f), n);
                grass = Color.Lerp(grass, new Color(0.47f, 0.60f, 0.27f), Mathf.SmoothStep(0.6f, 0.8f, patch) * 0.6f);   // field patches, still green
                Color sand = Color.Lerp(new Color(0.80f, 0.73f, 0.56f), new Color(0.86f, 0.79f, 0.62f), n);
                float inland = CoastZ(p.x) - p.z;   // sand only on the shore, never inland hollows
                Color c = Color.Lerp(sand, grass, Mathf.Max(Mathf.Clamp01((p.y - (SeaLevel + 0.5f)) / 1.0f), Mathf.SmoothStep(14f, 26f, inland)));
                if (p.y < SeaLevel - 0.2f) c = Color.Lerp(sand * 0.75f, sand, Mathf.Clamp01((p.y - SeaLevel + 2.5f) / 2.3f));
                c.a = 1f;
                colors[i] = c;
            }
            mesh.colors = colors;
            mesh.RecalculateBounds();
            mesh = SaveMesh(mesh, "Mainland");
            Material groundMat = Mat("M_Mainland", LitShader, m =>
            {
                Opaque(m, Color.white, 0.05f);
                RockDetail(m, 0.35f, 0f, 0f);
                m.SetFloat("_DetailTiling", 0.25f);
                m.SetFloat("_Cull", (float)CullMode.Back);
            });
            GameObject mainland = MeshObject("Mainland", land, mesh, new[] { groundMat }, true);
            Physics.SyncTransforms();

            int trees = ScatterMainlandTrees(ctx, land, mainland.GetComponent<MeshCollider>());
            ctx.Log.Add($"Mainland: {nx}x{nz} grid, {trees} trees, coast at z {CoastZ(0f):F0} (neck) to {CoastZ(300f):F0}, highway at z {HighwayZ}");
        }

        private static int ScatterMainlandTrees(Ctx ctx, Transform land, MeshCollider ground)
        {
            string[] inland = { "PLN_Broadleaf_Round", "PLN_Broadleaf_Tall", "PLN_Broadleaf_Wide", "PLN_Broadleaf_Oak", "PLN_Conifer_Mature", "PLN_Bush_Round", "PLN_Bush_Berry" };
            string[] coast = { "PLN_Palm_Coconut", "PLN_Palm_Tall", "PLN_Palm_Short" };
            List<(GameObject prefab, float scale)> Load(string[] kinds)
            {
                var list = new List<(GameObject, float)>();
                Transform plants = ctx.Island.Find("Plants");
                foreach (string k in kinds)
                {
                    var prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{PrefabFolder}/{k}.prefab");
                    if (prefab == null) continue;
                    float s = 2.5f;
                    if (plants != null)
                    {
                        var same = plants.Cast<Transform>().Where(c => PrefabUtility.GetCorrespondingObjectFromSource(c.gameObject) == prefab).ToList();
                        if (same.Count > 0) s = same.Average(c => c.localScale.y);
                    }
                    list.Add((prefab, s));
                }
                return list;
            }
            var inlandKinds = Load(inland);
            var coastKinds = Load(coast);
            if (inlandKinds.Count == 0) return 0;

            Transform group = Group(land, "Mainland Trees");
            var rng = new System.Random(4242);
            int placed = 0;
            for (int tries = 0; tries < 20000 && placed < 460; tries++)
            {
                float x = (float)(rng.NextDouble() * 640.0 - 320.0);
                float z = (float)(rng.NextDouble() * 300.0 - 430.0);
                if (Mathf.Abs(z - HighwayZ) < HighwayHalfWidth + 9f) continue;                    // highway verge
                if (z > HighwayZ && Mathf.Abs(x) < ParkRoadHalfWidth + 9f) continue;               // park road verge
                if (Mathf.Abs(x) < 26f && Mathf.Abs(z - GateZ) < 14f) continue;                    // gate forecourt
                if (Mathf.Abs(z - GateZ) < 3f) continue;                                           // perimeter wall
                float inlandDist = CoastZ(x) - z;
                bool nearCoast = inlandDist < 32f;
                if (!nearCoast && ProceduralTextures.WorldFbm(x * 0.02f, z * 0.02f, 2, 1f, 31) < 0.45f) continue;   // groves, not a carpet
                if (!ground.Raycast(new Ray(new Vector3(x, 400f, z), Vector3.down), out RaycastHit hit, 800f)) continue;
                if (hit.point.y < SeaLevel + 0.7f || hit.normal.y < 0.8f) continue;
                if (z > -150f && GroundY(ctx, x, z, -50f) > hit.point.y + 0.3f) continue;          // island ground covers it: leave the island as it is
                var kinds = nearCoast && coastKinds.Count > 0 ? coastKinds : inlandKinds;
                var pick = kinds[rng.Next(kinds.Count)];
                var go = (GameObject)PrefabUtility.InstantiatePrefab(pick.prefab, group);
                go.transform.SetPositionAndRotation(hit.point - Vector3.up * 0.15f, Quaternion.Euler(0f, (float)rng.NextDouble() * 360f, 0f));
                go.transform.localScale = Vector3.one * pick.scale * (0.8f + (float)rng.NextDouble() * 0.45f);
                placed++;
            }
            return placed;
        }

        // ------------------------------------------------------------------ roads
        /// <summary>Highway along the mainland and the two-lane park road from it to the plaza.</summary>
        private static void BuildRoads(Ctx ctx)
        {
            if (ctx.EntranceProfile == null || ctx.Highway == null) return;
            Transform roads = Group(ctx.Polish, "Roads");

            Material highwayMat = Mat("M_Road_Highway", LitShader, m =>
            {
                Opaque(m, Color.white, 0.2f);
                m.DisableKeyword("_TRIPLANAR");
                m.SetFloat("_Triplanar", 0f);
                m.SetTexture("_BaseMap", ProceduralTextures.Highway);
                m.SetFloat("_UseMapColor", 1f);
                m.SetFloat("_Cull", (float)CullMode.Back);
            });
            Material roadMat = Mat("M_Road_Asphalt", LitShader, m =>
            {
                Opaque(m, Color.white, 0.2f);
                m.DisableKeyword("_TRIPLANAR");
                m.SetFloat("_Triplanar", 0f);
                m.SetTexture("_BaseMap", ProceduralTextures.Road);
                m.SetFloat("_UseMapColor", 1f);
                m.SetFloat("_Cull", (float)CullMode.Back);
            });

            var highway = ctx.Highway.Select(p => p + Vector3.up * 0.08f).ToList();
            MeshObject("Highway", roads, SaveMesh(RoadStrip(highway, HighwayHalfWidth, 16f), "Highway"), new[] { highwayMat }, true, ShadowCastingMode.Off);

            var park = ctx.EntranceProfile.Select(p => p + Vector3.up * 0.1f).ToList();
            park[0] = new Vector3(0f, park[0].y, HighwayZ + HighwayHalfWidth - 0.05f);
            MeshObject("Park_Road", roads, SaveMesh(RoadStrip(park, ParkRoadHalfWidth, 8f), "Entrance_Road"), new[] { roadMat }, true, ShadowCastingMode.Off);
            ctx.Log.Add($"Roads: {HighwayReach * 2f:F0} m four-lane highway at z {HighwayZ}, park road {park[park.Count - 1].z - park[0].z:F0} m to the plaza");
        }

        /// <summary>Flat strip along a centre line; uv.x 0..1 across, uv.y = metres / uvLength along.</summary>
        private static Mesh RoadStrip(List<Vector3> path, float halfWidth, float uvLength)
        {
            var v = new List<Vector3>();
            var uv = new List<Vector2>();
            var tris = new List<int>();
            float arc = 0f;
            for (int i = 0; i < path.Count; i++)
            {
                if (i > 0) arc += Vector3.Distance(path[i - 1], path[i]);
                Vector3 tan = path[Mathf.Min(i + 1, path.Count - 1)] - path[Mathf.Max(i - 1, 0)];
                tan.y = 0f;
                Vector3 side = Vector3.Cross(Vector3.up, tan.normalized) * halfWidth;
                v.Add(path[i] - side);
                v.Add(path[i] + side);
                uv.Add(new Vector2(0f, arc / uvLength));
                uv.Add(new Vector2(1f, arc / uvLength));
                if (i > 0)
                {
                    int a = (i - 1) * 2;
                    tris.AddRange(new[] { a, a + 2, a + 1, a + 1, a + 2, a + 3 });
                }
            }
            var mesh = new Mesh();
            mesh.SetVertices(v);
            mesh.SetUVs(0, uv);
            mesh.SetColors(Enumerable.Repeat(Color.white, v.Count).ToList());
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            if (mesh.normals[0].y < 0f)
            {
                for (int i = 0; i < tris.Count; i += 3) (tris[i + 1], tris[i + 2]) = (tris[i + 2], tris[i + 1]);
                mesh.SetTriangles(tris, 0);
                mesh.RecalculateNormals();
            }
            mesh.RecalculateBounds();
            return mesh;
        }

        // ------------------------------------------------------------------ entrance gate
        /// <summary>
        /// Grand entrance where the park road enters the headland: two concrete pylons with brass bands,
        /// a timber beam with a living roof, the hanging brass "DINO PARK" sign, ticket booths on both
        /// sides, a perimeter wall along the neck to both shores, and street lamps down the park road.
        /// </summary>
        private static void BuildEntrance(Ctx ctx)
        {
            if (ctx.EntranceProfile == null) return;
            Transform gate = Group(ctx.Polish, "Entrance Gate");
            DistToPath(new Vector3(0f, 0f, GateZ), ctx.EntranceProfile, out _, out float gy);
            gy += 0.1f;

            var v = new List<Vector3>();
            var c = new List<Color>();
            var t = new List<int>();
            void Box(float x, float y, float z, float sx, float sy, float sz, Color col) =>
                AddBox(v, c, t, new Vector3(x, y, z), new Vector3(sx, sy, sz), Quaternion.identity, col);

            // pylons
            for (int s = -1; s <= 1; s += 2)
            {
                float px = s * 7.4f;
                Box(px, gy + 0.5f, GateZ, 4.2f, 1.0f, 4.2f, Concrete * 0.9f);
                Box(px, gy + 6f, GateZ, 3.2f, 10f, 3.2f, Concrete);
                Box(px, gy + 7.6f, GateZ, 3.35f, 0.5f, 3.35f, Brass);
                Box(px, gy + 11.3f, GateZ, 3.8f, 0.6f, 3.8f, Steel);
                Box(px, gy + 3.2f, GateZ - 1.62f, 1.2f, 4.5f, 0.06f, Glass);   // tall slot window, road side
                Box(px, gy + 3.2f, GateZ + 1.62f, 1.2f, 4.5f, 0.06f, Glass);
            }
            // beam with living roof
            Box(0f, gy + 9.4f, GateZ, 18.6f, 1.4f, 1.9f, Timber);
            Box(0f, gy + 10.3f, GateZ, 19.0f, 0.4f, 2.3f, Steel);
            Box(0f, gy + 10.65f, GateZ, 17.2f, 0.35f, 1.7f, LivingGreen);
            // hanging sign
            Box(-4.2f, gy + 8.25f, GateZ, 0.15f, 1.0f, 0.15f, Steel);
            Box(4.2f, gy + 8.25f, GateZ, 0.15f, 1.0f, 0.15f, Steel);
            Box(0f, gy + 6.75f, GateZ, 11.2f, 2.1f, 0.3f, Brass);
            Box(0f, gy + 6.75f, GateZ, 11.6f, 2.4f, 0.18f, Steel);
            // ticket booths
            for (int s = -1; s <= 1; s += 2)
            {
                float bx = s * 14.5f;
                Box(bx, gy + 1.6f, GateZ, 4.0f, 3.2f, 3.6f, Concrete);
                Box(bx, gy + 1.9f, GateZ, 4.06f, 1.2f, 3.66f, Glass);
                Box(bx, gy + 3.35f, GateZ, 5.0f, 0.3f, 4.6f, Timber);
                Box(bx, gy + 3.6f, GateZ, 4.6f, 0.2f, 4.2f, LivingGreen);
            }
            // forecourt paving under the gate
            Box(0f, gy - 0.12f, GateZ, 34f, 0.3f, 14f, Concrete * 0.85f);

            // perimeter wall from the booths out to both shores
            int wallSegments = 0;
            for (int s = -1; s <= 1; s += 2)
            {
                for (float x = 17.5f; x < 200f; x += 2f)
                {
                    float wx = s * (x + 1f);
                    if (!Physics.Raycast(new Vector3(wx, 300f, GateZ), Vector3.down, out RaycastHit hit, 600f, ~0, QueryTriggerInteraction.Ignore)) break;
                    if (hit.point.y < SeaLevel + 0.35f) break;
                    float y = hit.point.y;
                    Box(wx, y + 0.8f, GateZ, 2.05f, 2.6f, 0.6f, Concrete);
                    Box(wx, y + 2.15f, GateZ, 2.05f, 0.15f, 0.8f, Timber);
                    if (Mathf.RoundToInt(x) % 10 == 7) Box(wx, y + 1.0f, GateZ, 0.8f, 3.0f, 0.9f, Concrete * 0.92f);   // pier every 10 m
                    wallSegments++;
                }
            }

            // street lamps down the park road
            int lamps = 0;
            foreach (Vector3 p in ctx.EntranceProfile)
            {
                if (Mathf.RoundToInt(p.z - HighwayZ) % 20 != 0 || p.z < HighwayZ + 16f || p.z > -84f || Mathf.Abs(p.z - GateZ) < 9f) continue;
                for (int s = -1; s <= 1; s += 2)
                {
                    float lx = s * (ParkRoadHalfWidth + 1.6f);
                    Box(lx, p.y + 2.8f, p.z, 0.22f, 5.6f, 0.22f, Steel);
                    Box(lx - s * 0.6f, p.y + 5.55f, p.z, 1.3f, 0.12f, 0.16f, Steel);
                    Box(lx - s * 1.15f, p.y + 5.4f, p.z, 0.5f, 0.22f, 0.4f, Amber);
                    lamps++;
                }
            }

            var mesh = new Mesh { indexFormat = IndexFormat.UInt32 };
            mesh.SetVertices(v);
            mesh.SetColors(c);
            mesh.SetTriangles(t, 0);
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            Material mat = Mat("M_Entrance", LitShader, m =>
            {
                Opaque(m, Color.white, 0.18f);
                RockDetail(m, 0.18f, 0f, 0f);
                m.SetFloat("_DetailTiling", 0.5f);
                m.SetFloat("_Cull", (float)CullMode.Back);
            });
            MeshObject("Gate", gate, SaveMesh(mesh, "Entrance_Gate"), new[] { mat }, true);

            // sign lettering, both faces
            Font font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            for (int s = -1; s <= 1; s += 2)
            {
                var go = new GameObject(s < 0 ? "Sign_South" : "Sign_North");
                go.transform.SetParent(gate, false);
                go.transform.SetPositionAndRotation(new Vector3(0f, gy + 6.75f, GateZ + s * 0.17f), Quaternion.Euler(0f, s < 0 ? 0f : 180f, 0f));
                var tm = go.AddComponent<TextMesh>();
                tm.text = "DINO PARK";
                tm.font = font;
                tm.fontSize = 128;
                tm.characterSize = 0.13f;
                tm.fontStyle = FontStyle.Bold;
                tm.anchor = TextAnchor.MiddleCenter;
                tm.alignment = TextAlignment.Center;
                tm.color = Steel;
                var r = go.GetComponent<MeshRenderer>();
                r.sharedMaterial = font.material;
                r.shadowCastingMode = ShadowCastingMode.Off;
            }

            // nothing from the island may stand in the gate, the forecourt or the wall line
            int hidden = 0;
            foreach (string g in new[] { "Plants", "Props" })
            {
                Transform group = ctx.Island.Find(g);
                if (group == null) continue;
                foreach (Transform child in group)
                {
                    var r = child.GetComponent<Renderer>();
                    if (r == null || !child.gameObject.activeSelf) continue;
                    Vector3 p = r.bounds.center;
                    float dz = Mathf.Abs(p.z - GateZ);
                    if ((Mathf.Abs(p.x) < 22f && dz < 10f) || dz < 2.5f + Mathf.Min(r.bounds.extents.x, r.bounds.extents.z) * 0.5f)
                    {
                        child.gameObject.SetActive(false);
                        hidden++;
                    }
                }
            }
            ctx.Log.Add($"Entrance: gate at z {GateZ} (y {gy:F2}), {wallSegments} wall segments, {lamps} lamps, {hidden} island plants/props cleared");
        }

        private static void AddBox(List<Vector3> v, List<Color> c, List<int> t, Vector3 centre, Vector3 size, Quaternion rot, Color col)
        {
            Vector3 h = size * 0.5f;
            Vector3[] corners =
            {
                new Vector3(-h.x, -h.y, -h.z), new Vector3(h.x, -h.y, -h.z), new Vector3(h.x, h.y, -h.z), new Vector3(-h.x, h.y, -h.z),
                new Vector3(-h.x, -h.y, h.z), new Vector3(h.x, -h.y, h.z), new Vector3(h.x, h.y, h.z), new Vector3(-h.x, h.y, h.z),
            };
            int[][] faces = { new[] { 0, 3, 2, 1 }, new[] { 4, 5, 6, 7 }, new[] { 0, 4, 7, 3 }, new[] { 1, 2, 6, 5 }, new[] { 3, 7, 6, 2 }, new[] { 0, 1, 5, 4 } };
            col.a = 1f;
            foreach (int[] f in faces)
            {
                int s = v.Count;
                foreach (int k in f) { v.Add(centre + rot * corners[k]); c.Add(col); }
                t.AddRange(new[] { s, s + 1, s + 2, s, s + 2, s + 3 });
            }
        }

        // ------------------------------------------------------------------ traffic
        /// <summary>
        /// Through traffic both ways on the highway (two loops: outer and inner lanes, U-turning far
        /// off screen), and visitor cars that leave the eastbound lane, drive to the plaza, turn and
        /// head back west. Right-hand traffic.
        /// </summary>
        private static void BuildTraffic(Ctx ctx)
        {
            List<Vector3> path = ctx.EntranceProfile;
            if (path == null) return;
            var cars = AssetDatabase.FindAssets("t:Model", new[] { CarFolder })
                .Select(g => AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(g)))
                .Where(g => g != null).ToArray();
            if (cars.Length == 0) { ctx.Log.Add("Traffic: no car models"); return; }
            Transform root = Group(ctx.Polish, "Traffic");
            float hy = LandLevel + 0.1f;

            List<Vector3> HighwayLoop(float lane)
            {
                var loop = new List<Vector3>();
                for (float x = -HighwayReach; x <= HighwayReach; x += 20f) loop.Add(new Vector3(x, hy, HighwayZ - lane));   // eastbound (south side)
                for (float x = HighwayReach; x >= -HighwayReach; x -= 20f) loop.Add(new Vector3(x, hy, HighwayZ + lane));   // westbound (north side)
                return loop;
            }
            Add("Highway Traffic Outer", HighwayLoop(5.25f), 22, 17f, 11);
            Add("Highway Traffic Inner", HighwayLoop(1.75f), 16, 13.5f, 23);

            // visitors: eastbound inner lane -> left turn -> park road -> plaza loop -> back -> right turn -> westbound
            float RoadY(Vector3 p) => p.y + 0.1f;
            var visit = new List<Vector3>();
            const float rIn = 6f, rOut = 5f;
            for (float x = -HighwayReach; x < 1.75f - rIn; x += 20f) visit.Add(new Vector3(x, hy, HighwayZ - 1.75f));
            for (int k = 0; k <= 8; k++)
            {
                float a = Mathf.Lerp(-90f, 0f, k / 8f) * Mathf.Deg2Rad;
                visit.Add(new Vector3(1.75f - rIn + Mathf.Cos(a) * rIn, hy, HighwayZ - 1.75f + rIn + Mathf.Sin(a) * rIn));
            }
            var inbound = path.Where(p => p.z > HighwayZ + 6f && p.z < -76f).ToList();
            foreach (Vector3 p in inbound) visit.Add(new Vector3(1.75f, RoadY(p), p.z));
            float PlazaY(float x, float z) => GroundY(ctx, x, z, path[path.Count - 1].y) + 0.05f;
            foreach (Vector2 q in new[] { new Vector2(1.75f, -74f), new Vector2(4.8f, -70f), new Vector2(5.6f, -66f), new Vector2(3.2f, -62.5f),
                         new Vector2(0f, -61.5f), new Vector2(-3.2f, -62.5f), new Vector2(-5.6f, -66f), new Vector2(-4.8f, -70f), new Vector2(-1.75f, -74f) })
                visit.Add(new Vector3(q.x, PlazaY(q.x, q.y), q.y));
            float turnZ = HighwayZ + 1.75f + rOut;
            for (int i = inbound.Count - 1; i >= 0; i--)
                if (inbound[i].z > turnZ) visit.Add(new Vector3(-1.75f, RoadY(inbound[i]), inbound[i].z));
            for (int k = 0; k <= 8; k++)
            {
                float a = Mathf.Lerp(0f, -90f, k / 8f) * Mathf.Deg2Rad;
                visit.Add(new Vector3(-1.75f - rOut + Mathf.Cos(a) * rOut, hy, turnZ + Mathf.Sin(a) * rOut));
            }
            for (float x = -1.75f - rOut - 20f; x >= -HighwayReach; x -= 20f) visit.Add(new Vector3(x, hy, HighwayZ + 1.75f));
            Add("Visitor Traffic", visit, 12, 11f, 7);

            void Add(string name, List<Vector3> loop, int count, float speed, int seed)
            {
                var go = new GameObject(name);
                go.transform.SetParent(root, false);
                go.AddComponent<VehicleTraffic>().Configure(loop.ToArray(), cars, 0f, count, speed, seed);
            }
            ctx.Log.Add($"Traffic: {cars.Length} car models; highway both ways (38 cars), 12 visitor cars turning into the park");
        }

        // ------------------------------------------------------------------ camera + render settings
        private static void ConfigureCamera(Ctx ctx)
        {
            var config = AssetDatabase.LoadAssetAtPath<IslandCameraConfig>(CameraConfigPath);
            if (config != null)
            {
                var so = new SerializedObject(config);
                so.FindProperty("yawDegrees").floatValue = -90f;        // from the east side, looking west
                so.FindProperty("pitchDegrees").floatValue = 52f;
                so.FindProperty("absoluteMaxDistance").floatValue = 215f;
                so.FindProperty("minDistance").floatValue = 18f;
                so.ApplyModifiedPropertiesWithoutUndo();
                EditorUtility.SetDirty(config);
            }

            // Let the camera reach the gate and the highway south of the headland.
            IslandBounds bounds = Object.FindAnyObjectByType<IslandBounds>();
            if (bounds != null)
            {
                Rect r = bounds.IslandRect;
                float zMin = Mathf.Min(r.yMin, HighwayZ - HighwayHalfWidth - 12f);
                var so = new SerializedObject(bounds);
                so.FindProperty("islandSize").vector2Value = new Vector2(r.width, r.yMax - zMin);
                so.ApplyModifiedPropertiesWithoutUndo();
                Vector3 p = bounds.transform.position;
                bounds.transform.position = new Vector3(p.x, p.y, (r.yMax + zMin) * 0.5f);
                EditorUtility.SetDirty(bounds);
            }

            // Water foam and soft particles read the camera depth texture.
            foreach (string guid in AssetDatabase.FindAssets("t:UniversalRenderPipelineAsset", new[] { "Assets/Settings" }))
            {
                var urp = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(AssetDatabase.GUIDToAssetPath(guid));
                if (urp == null || urp.supportsCameraDepthTexture) continue;
                urp.supportsCameraDepthTexture = true;
                EditorUtility.SetDirty(urp);
            }
            ctx.Log.Add("Camera: east side (yaw -90), pitch 52, max distance 215 m; depth texture on");
        }
    }
}
