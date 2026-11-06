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
        private const float OpeningHalfWidth = 4.6f;
        private const float OpeningWallHeight = 4.4f;
        private const float HeadwallHalfWidth = 13f;
        private const float HeadwallHeight = 13f;
        private const float HeadwallThickness = 2.8f;

        private static readonly Color Concrete = new Color(0.93f, 0.90f, 0.82f);   // off-white concrete #F4EDD8 (slightly darker)
        private static readonly Color Brass = new Color(0.95f, 0.72f, 0.29f);      // brass gold #F2B84B

        // ------------------------------------------------------------------ mountain
        /// <summary>
        /// The land side: a forested mountain range along the south edge with the visitor tunnel.
        /// Hides the straight cut of the Blender ground and drops into the sea at both ends.
        /// </summary>
        private static void BuildMountainAndTunnel(Ctx ctx)
        {
            Transform land = Group(ctx.Polish, "Land Side");
            const float x0 = -320f, x1 = 320f, z0 = -360f, z1 = -118f, step = 2.5f;
            int nx = Mathf.RoundToInt((x1 - x0) / step) + 1, nz = Mathf.RoundToInt((z1 - z0) / step) + 1;
            var verts = new Vector3[nx * nz];
            for (int j = 0; j < nz; j++)
            for (int i = 0; i < nx; i++)
            {
                float x = x0 + i * step, z = z0 + j * step;
                verts[j * nx + i] = new Vector3(x, MountainHeight(ctx, x, z), z);
            }
            var tris = new List<int>((nx - 1) * (nz - 1) * 6);
            for (int j = 0; j < nz - 1; j++)
            for (int i = 0; i < nx - 1; i++)
            {
                int a = j * nx + i, b = a + 1, c = a + nx, d = c + 1;
                Vector3 mid = (verts[a] + verts[b] + verts[c] + verts[d]) * 0.25f;
                // leave a hole where the headwall and the tunnel mouth stand
                // the step from the apron up onto the headwall would stand in front of it
                bool portalSlot = Mathf.Abs(mid.x) < HeadwallHalfWidth + 1f && mid.z > ctx.PortalZ - 0.6f && mid.z < ctx.PortalZ + 2.6f
                                  && mid.y < ctx.ApronY + HeadwallHeight - 1f;
                if (portalSlot) continue;
                tris.AddRange(new[] { a, c, b, b, c, d });
            }
            var mesh = new Mesh { indexFormat = IndexFormat.UInt32 };
            mesh.vertices = verts;
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            Vector3[] nrm = mesh.normals;
            var colors = new Color[verts.Length];
            for (int i = 0; i < verts.Length; i++)
            {
                Vector3 p = verts[i];
                float slope = 1f - nrm[i].y;
                float n = ProceduralTextures.WorldFbm(p.x * 0.03f, p.z * 0.03f, 3, 1f, 23);
                Color grass = Color.Lerp(new Color(0.36f, 0.54f, 0.21f), new Color(0.52f, 0.66f, 0.30f), n);
                Color rock = Color.Lerp(new Color(0.50f, 0.46f, 0.40f), new Color(0.64f, 0.58f, 0.50f), n);
                float rocky = Mathf.Clamp01(Mathf.SmoothStep(0.34f, 0.62f, slope + (n - 0.5f) * 0.25f) + Mathf.SmoothStep(70f, 110f, p.y) * 0.5f);
                Color c = Color.Lerp(grass, rock, rocky);
                if (p.y < 1.2f) c = Color.Lerp(new Color(0.80f, 0.73f, 0.56f), c, Mathf.Clamp01((p.y - SeaLevel) / 1.6f));
                if (p.y < SeaLevel - 0.3f) c *= 0.7f;
                c.a = 1f;
                colors[i] = c;
            }
            mesh.colors = colors;
            mesh.RecalculateBounds();
            mesh = SaveMesh(mesh, "Mountain_South");
            Material rockMat = Mat("M_Mountain", LitShader, m =>
            {
                Opaque(m, Color.white, 0.08f);
                RockDetail(m, 0.75f, 0.22f, 0.15f);
                m.SetFloat("_DetailTiling", 0.12f);
                m.SetFloat("_StrataHeight", 3.2f);
                m.SetColor("_MossColor", new Color(0.33f, 0.48f, 0.2f));
                m.SetFloat("_Cull", (float)CullMode.Back);
            });
            GameObject mountain = MeshObject("Mountain_South", land, mesh, new[] { rockMat }, true);
            Physics.SyncTransforms();

            int trees = ScatterMountainTrees(ctx, land, mountain.GetComponent<MeshCollider>());

            // keep the portal and its approach clear of island plants and rocks
            foreach (string g in new[] { "Plants", "Props" })
            {
                Transform group = ctx.Island.Find(g);
                if (group == null) continue;
                foreach (Transform c in group)
                {
                    var r = c.GetComponent<Renderer>();
                    if (r == null) continue;
                    Vector3 p = r.bounds.center;
                    if (Mathf.Abs(p.x) < HeadwallHalfWidth + 6f && p.z < ctx.PortalZ + 16f) c.gameObject.SetActive(false);
                }
            }
            BuildPortal(ctx, land);
            ctx.Log.Add($"Mountain: {nx}x{nz} grid, {trees} trees, tunnel portal at z {ctx.PortalZ:F0}, apron y {ctx.ApronY:F2}");
        }

        private static float MountainHeight(Ctx ctx, float x, float z)
        {
            float footZ = -136f - 10f * ProceduralTextures.WorldFbm(x * 0.012f, 0.37f, 2, 1f, 7);
            float t = Mathf.Clamp01((footZ - z) / 100f);
            float rise = Mathf.Pow(t * t * (3f - 2f * t), 0.8f);
            float ridge = 1f - Mathf.Abs(ProceduralTextures.WorldFbm(x * 0.011f, z * 0.011f, 4, 1f, 11) * 2f - 1f);
            float massif = ProceduralTextures.WorldFbm(x * 0.0045f, z * 0.0045f, 2, 1f, 13);
            float peak = 50f + 36f * ridge + 26f * (massif - 0.5f);
            float detail = (ProceduralTextures.WorldFbm(x * 0.025f, z * 0.025f, 3, 1f, 19) - 0.5f) * 5f;
            float h = -5f + rise * peak + detail * Mathf.Clamp01(rise * 2f);

            // ends drop into the sea
            float ax = Mathf.Abs(x);
            float keep = 1f - Mathf.SmoothStep(0f, 1f, (ax - 185f) / 95f);
            h = Mathf.Lerp(-16f, h, keep);

            // cut for the road in front of the portal, solid rock face behind it
            if (z > ctx.PortalZ + 0.5f)
            {
                // flat apron in front of the portal (also fills any low beach there so no sea shows)
                float cut = (1f - Mathf.SmoothStep(0f, 1f, (ax - HeadwallHalfWidth) / 16f)) * (1f - Mathf.SmoothStep(0f, 1f, (z - ctx.PortalZ - 18f) / 12f));
                h = Mathf.Lerp(h, ctx.ApronY - 0.3f, cut);
            }
            else if (z > ctx.PortalZ - HeadwallThickness)
            {
                // rock sits on top of the headwall slab
                float w = 1f - Mathf.SmoothStep(0f, 1f, (ax - HeadwallHalfWidth) / 6f);
                h = Mathf.Lerp(h, ctx.ApronY + HeadwallHeight - 0.3f, w);
            }
            else
            {
                float face = (1f - Mathf.SmoothStep(0f, 1f, (ax - 15f) / 16f)) * (1f - Mathf.SmoothStep(0f, 1f, (ctx.PortalZ - z - 18f) / 30f));
                h = Mathf.Max(h, Mathf.Lerp(h, ctx.ApronY + HeadwallHeight + 4f, face));
            }
            return h;
        }

        private static int ScatterMountainTrees(Ctx ctx, Transform land, MeshCollider mountain)
        {
            string[] kinds = { "PLN_Broadleaf_Round", "PLN_Broadleaf_Tall", "PLN_Broadleaf_Wide", "PLN_Conifer_Mature", "PLN_Conifer_TallOld", "PLN_Conifer_Young", "PLN_Bush_Round" };
            var prefabs = new List<(GameObject prefab, float scale)>();
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
                prefabs.Add((prefab, s));
            }
            if (prefabs.Count == 0) return 0;

            Transform group = Group(land, "Mountain Trees");
            var rng = new System.Random(4242);
            int placed = 0;
            for (int tries = 0; tries < 12000 && placed < 520; tries++)
            {
                float x = (float)(rng.NextDouble() * 440.0 - 220.0);
                float z = (float)(rng.NextDouble() * 140.0 - 280.0);
                if (Mathf.Abs(x) < 20f && z > ctx.PortalZ - 22f) continue;
                if (ProceduralTextures.WorldFbm(x * 0.025f, z * 0.025f, 2, 1f, 31) < 0.40f) continue;
                if (!mountain.Raycast(new Ray(new Vector3(x, 400f, z), Vector3.down), out RaycastHit hit, 800f)) continue;
                if (hit.normal.y < 0.62f || hit.point.y < 1.5f || hit.point.y > 85f) continue;
                var pick = prefabs[rng.Next(prefabs.Count)];
                var go = (GameObject)PrefabUtility.InstantiatePrefab(pick.prefab, group);
                go.transform.SetPositionAndRotation(hit.point - Vector3.up * 0.2f, Quaternion.Euler(0f, (float)rng.NextDouble() * 360f, 0f));
                go.transform.localScale = Vector3.one * pick.scale * (0.8f + (float)rng.NextDouble() * 0.45f);
                placed++;
            }
            return placed;
        }

        // ------------------------------------------------------------------ tunnel portal
        private static void BuildPortal(Ctx ctx, Transform land)
        {
            Transform portal = Group(land, "Tunnel Portal");
            float apron = ctx.ApronY, fz = ctx.PortalZ;
            var centre = new Vector2(0f, apron + OpeningWallHeight);

            // headwall with the arched opening (ring between the opening outline and the wall outline)
            const int n = 144;
            var verts = new List<Vector3>();
            var cols = new List<Color>();
            var tris = new List<int>();
            for (int layer = 0; layer < 2; layer++)
            {
                float z = layer == 0 ? fz : fz - HeadwallThickness;
                for (int k = 0; k <= n; k++)
                {
                    float a = k / (float)n * Mathf.PI * 2f;
                    Vector2 inner = centre + OpeningDir(a) * OpeningReach(a);
                    Vector2 outer = centre + OpeningDir(a) * WallReach(a);
                    verts.Add(new Vector3(inner.x, inner.y, z)); cols.Add(Concrete);
                    verts.Add(new Vector3(outer.x, outer.y, z)); cols.Add(Concrete);
                }
            }
            int stride = (n + 1) * 2;
            for (int layer = 0; layer < 2; layer++)
            for (int k = 0; k < n; k++)
            {
                int i0 = layer * stride + k * 2, o0 = i0 + 1, i1 = i0 + 2, o1 = i0 + 3;
                tris.AddRange(new[] { i0, o0, o1, i0, o1, i1 });
            }
            for (int k = 0; k < n; k++)   // outer rim (top and sides of the slab)
            {
                int a = k * 2 + 1, b = a + 2, c = stride + k * 2 + 1, d = c + 2;
                tris.AddRange(new[] { a, c, d, a, d, b });
            }
            AddBox(verts, cols, tris, new Vector3(0f, apron + HeadwallHeight - 0.35f, fz - HeadwallThickness * 0.5f + 0.25f),
                new Vector3(HeadwallHalfWidth * 2f + 1.2f, 0.9f, HeadwallThickness + 0.8f), Quaternion.identity, Concrete);
            AddBox(verts, cols, tris, new Vector3(0f, apron + HeadwallHeight - 1.15f, fz + 0.18f),
                new Vector3(HeadwallHalfWidth * 2f, 0.35f, 0.2f), Quaternion.identity, Brass);
            // concrete apron slab in front of the portal (the road runs on top of it)
            AddBox(verts, cols, tris, new Vector3(0f, apron - 0.25f, fz + 4f), new Vector3(HeadwallHalfWidth * 2f + 2f, 0.4f, 8.5f), Quaternion.identity, Concrete * 0.92f);
            for (int s = -1; s <= 1; s += 2)
            {
                // tapered wing wall: full headwall height at the portal, sloping down along the cut bank
                Vector3 start = new Vector3(s * (HeadwallHalfWidth - 0.4f), apron - 0.6f, fz - 0.3f);
                Vector3 dir = Quaternion.Euler(0f, s * -38f, 0f) * new Vector3(s, 0f, 0f);
                AddWedge(verts, cols, tris, start, dir, 15f, HeadwallHeight + 0.6f, 1.6f, 1.0f, Concrete);
            }
            var wall = new Mesh();
            wall.SetVertices(verts);
            wall.SetColors(cols);
            wall.SetTriangles(tris, 0);
            wall.RecalculateNormals();
            wall.RecalculateBounds();
            Material concrete = Mat("M_Tunnel_Concrete", LitShader, m =>
            {
                Opaque(m, Color.white, 0.15f);
                RockDetail(m, 0.3f, 0f, 0.12f);
                m.SetFloat("_DetailTiling", 0.35f);
                m.SetFloat("_Cull", (float)CullMode.Off);
            });
            MeshObject("Headwall", portal, SaveMesh(wall, "Tunnel_Headwall"), new[] { concrete }, true);

            // tube: the opening outline (without the floor) pushed into the mountain, fading to black
            var outline = new List<Vector2>();
            outline.Add(new Vector2(OpeningHalfWidth, apron - 0.2f));
            for (int k = 0; k <= 24; k++)
            {
                float a = k / 24f * Mathf.PI;
                outline.Add(centre + new Vector2(Mathf.Cos(a), Mathf.Sin(a)) * OpeningHalfWidth);
            }
            outline.Add(new Vector2(-OpeningHalfWidth, apron - 0.2f));
            var tv = new List<Vector3>();
            var tc = new List<Color>();
            var tt = new List<int>();
            const int rings = 24;
            for (int r = 0; r <= rings; r++)
            {
                float depth = r / (float)rings * TunnelDepth;
                float dark = Mathf.Clamp01(depth / 34f);
                Color c = Color.Lerp(Concrete * 0.65f, new Color(0.02f, 0.02f, 0.025f), dark);
                c.a = 1f;
                foreach (Vector2 o in outline)
                {
                    tv.Add(new Vector3(o.x, o.y, fz - HeadwallThickness * 0.5f - depth));
                    tc.Add(c);
                }
            }
            int m2 = outline.Count;
            for (int r = 0; r < rings; r++)
            for (int k = 0; k < m2 - 1; k++)
            {
                int a = r * m2 + k, b = a + 1, c = a + m2, d = c + 1;
                tt.AddRange(new[] { a, b, d, a, d, c });
            }
            int cap = tv.Count;   // black end cap
            float zc = fz - HeadwallThickness * 0.5f - TunnelDepth;
            tv.Add(new Vector3(-OpeningHalfWidth, apron - 0.3f, zc)); tv.Add(new Vector3(OpeningHalfWidth, apron - 0.3f, zc));
            tv.Add(new Vector3(OpeningHalfWidth, centre.y + OpeningHalfWidth, zc)); tv.Add(new Vector3(-OpeningHalfWidth, centre.y + OpeningHalfWidth, zc));
            for (int k = 0; k < 4; k++) tc.Add(Color.black);
            tt.AddRange(new[] { cap, cap + 2, cap + 1, cap, cap + 3, cap + 2 });
            var tube = new Mesh();
            tube.SetVertices(tv);
            tube.SetColors(tc);
            tube.SetTriangles(tt, 0);
            tube.RecalculateNormals();
            tube.RecalculateBounds();
            Material inside = Mat("M_Tunnel_Inside", LitShader, m =>
            {
                Opaque(m, Color.white, 0.05f);
                m.DisableKeyword("_TRIPLANAR");
                m.SetFloat("_Triplanar", 0f);
                m.SetFloat("_Cull", (float)CullMode.Off);
            });
            MeshObject("Tunnel", portal, SaveMesh(tube, "Tunnel_Tube"), new[] { inside }, false, ShadowCastingMode.Off);
        }

        private static Vector2 OpeningDir(float a) => new Vector2(Mathf.Cos(a), Mathf.Sin(a));

        /// <summary>Distance from the opening centre to the arch outline (semicircle over straight walls).</summary>
        private static float OpeningReach(float a)
        {
            float c = Mathf.Cos(a), s = Mathf.Sin(a);
            if (s >= 0f) return OpeningHalfWidth;
            float tx = Mathf.Abs(c) > 1e-4f ? OpeningHalfWidth / Mathf.Abs(c) : float.MaxValue;
            float ty = OpeningWallHeight / Mathf.Max(-s, 1e-4f);
            return Mathf.Min(tx, ty);
        }

        /// <summary>Distance from the opening centre to the headwall outline (rectangle).</summary>
        private static float WallReach(float a)
        {
            float c = Mathf.Cos(a), s = Mathf.Sin(a);
            float tx = Mathf.Abs(c) > 1e-4f ? HeadwallHalfWidth / Mathf.Abs(c) : float.MaxValue;
            float ty = s >= 0f ? (HeadwallHeight - OpeningWallHeight) / Mathf.Max(s, 1e-4f) : OpeningWallHeight / Mathf.Max(-s, 1e-4f);
            return Mathf.Min(tx, ty);
        }

        /// <summary>Wall running from <paramref name="start"/> along <paramref name="dir"/>, top sloping from h0 to h1.</summary>
        private static void AddWedge(List<Vector3> v, List<Color> c, List<int> t, Vector3 start, Vector3 dir, float length, float h0, float h1, float thick, Color col)
        {
            dir.y = 0f;
            dir.Normalize();
            Vector3 side = Vector3.Cross(Vector3.up, dir) * (thick * 0.5f);
            Vector3 end = start + dir * length;
            Vector3[] p =
            {
                start - side, start + side, end + side, end - side,                                   // base
                start - side + Vector3.up * h0, start + side + Vector3.up * h0,
                end + side + Vector3.up * h1, end - side + Vector3.up * h1,                           // top
            };
            int[][] faces = { new[] { 0, 1, 2, 3 }, new[] { 4, 7, 6, 5 }, new[] { 0, 4, 5, 1 }, new[] { 1, 5, 6, 2 }, new[] { 2, 6, 7, 3 }, new[] { 3, 7, 4, 0 } };
            foreach (int[] f in faces)
            {
                int s = v.Count;
                foreach (int k in f) { v.Add(p[k]); c.Add(col); }
                t.AddRange(new[] { s, s + 1, s + 2, s, s + 2, s + 3 });
            }
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
            foreach (int[] f in faces)
            {
                int s = v.Count;
                foreach (int k in f) { v.Add(centre + rot * corners[k]); c.Add(col); }
                t.AddRange(new[] { s, s + 1, s + 2, s, s + 2, s + 3 });
            }
        }

        // ------------------------------------------------------------------ road
        private static void BuildRoad(Ctx ctx)
        {
            List<Vector3> path = ctx.EntranceProfile;
            if (path == null || path.Count < 2) return;
            var v = new List<Vector3>();
            var uv = new List<Vector2>();
            var tris = new List<int>();
            float arc = 0f;
            for (int i = 0; i < path.Count; i++)
            {
                if (i > 0) arc += Vector3.Distance(path[i - 1], path[i]);
                Vector3 p = path[i];
                bool inside = p.z < ctx.PortalZ;
                float y = inside ? ctx.ApronY + 0.03f : p.y + 0.08f;
                v.Add(new Vector3(-3.5f, y, p.z));
                v.Add(new Vector3(3.5f, y, p.z));
                uv.Add(new Vector2(0f, arc / 8f));
                uv.Add(new Vector2(1f, arc / 8f));
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
            mesh.RecalculateBounds();
            Material road = Mat("M_Road_Asphalt", LitShader, m =>
            {
                Opaque(m, Color.white, 0.2f);
                m.DisableKeyword("_TRIPLANAR");
                m.SetFloat("_Triplanar", 0f);
                m.SetTexture("_BaseMap", ProceduralTextures.Road);
                m.SetFloat("_UseMapColor", 1f);
                m.SetFloat("_Cull", (float)CullMode.Back);
            });
            MeshObject("Entrance_Road", Group(ctx.Polish, "Roads"), SaveMesh(mesh, "Entrance_Road"), new[] { road }, true, ShadowCastingMode.Off);
            ctx.Log.Add($"Road: {arc:F0} m asphalt from the tunnel to the plaza");
        }

        // ------------------------------------------------------------------ traffic
        private static void BuildTraffic(Ctx ctx)
        {
            List<Vector3> path = ctx.EntranceProfile;
            if (path == null) return;
            var cars = AssetDatabase.FindAssets("t:Model", new[] { CarFolder })
                .Select(g => AssetDatabase.LoadAssetAtPath<GameObject>(AssetDatabase.GUIDToAssetPath(g)))
                .Where(g => g != null).ToArray();
            if (cars.Length == 0) { ctx.Log.Add("Traffic: no car models"); return; }

            float RoadY(Vector3 p) => (p.z < ctx.PortalZ ? ctx.ApronY + 0.03f : p.y + 0.08f);
            var inbound = path.Where(p => p.z > ctx.PortalZ - 60f && p.z < -76f).ToList();
            var loop = new List<Vector3>();
            foreach (Vector3 p in inbound) loop.Add(new Vector3(1.75f, RoadY(p), p.z));
            float PlazaY(float x, float z) => GroundY(ctx, x, z, path[path.Count - 1].y) + 0.05f;
            foreach (Vector2 q in new[] { new Vector2(1.75f, -74f), new Vector2(4.8f, -70f), new Vector2(5.6f, -66f), new Vector2(3.2f, -62.5f),
                         new Vector2(0f, -61.5f), new Vector2(-3.2f, -62.5f), new Vector2(-5.6f, -66f), new Vector2(-4.8f, -70f), new Vector2(-1.75f, -74f) })
                loop.Add(new Vector3(q.x, PlazaY(q.x, q.y), q.y));
            for (int i = inbound.Count - 1; i >= 0; i--) loop.Add(new Vector3(-1.75f, RoadY(inbound[i]), inbound[i].z));

            var go = new GameObject("Visitor Traffic");
            go.transform.SetParent(Group(ctx.Polish, "Traffic"), false);
            var traffic = go.AddComponent<VehicleTraffic>();
            traffic.Configure(loop.ToArray(), cars, 0f);
            ctx.Log.Add($"Traffic: {cars.Length} car models, loop of {loop.Count} points");
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
