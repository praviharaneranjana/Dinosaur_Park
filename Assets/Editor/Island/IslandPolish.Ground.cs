using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace DinoPark.EditorTools
{
    public static partial class IslandPolish
    {
        private const string GroundSource = IslandImporter.Root + "/Textures/ISL_Ground_Albedo.png";
        private const string GroundPolished = IslandImporter.Root + "/Textures/ISL_Ground_Albedo_Polished.png";
        private const int MaskRes = 1024;

        /// <summary>Mud wallow (one big pond replacing the four puddles): centre and radii in metres, Unity XZ.</summary>
        private static Vector2 wallowCentre;
        private static readonly Vector2 WallowRadii = new Vector2(19f, 12f);
        private static float wallowAngle;

        /// <summary>
        /// Ground repaint and mud wallow. The Blender ground texture painted the river strip, the mud puddles
        /// and the paths in the same flat brown. Here wide brown areas become grass (thin brown lines stay as
        /// packed-earth paths), the four puddles merge into one big mud wallow with a carved basin, and the
        /// ground gets a fine grass-blade detail so it reads as grass, not paint. Rock mounds get grassy tops.
        /// Reads the original texture every run, writes ISL_Ground_Albedo_Polished.png.
        /// </summary>
        private static void RepaintGround(Ctx ctx)
        {
            var mr = ctx.Ground.GetComponent<MeshRenderer>();
            Mesh gm = ctx.Ground.GetComponent<MeshFilter>().sharedMesh;
            if (!FitGroundUv(gm, ctx.Ground.transform, out Vector3 au, out Vector3 av, out float residual))
            {
                ctx.Log.Add("Ground: could not fit the texture mapping, skipped");
                return;
            }
            // inverse: world xz from uv
            float det = au.x * av.y - au.y * av.x;
            Vector2 World(float u, float v)
            {
                float du = u - au.z, dv = v - av.z;
                return new Vector2((du * av.y - dv * au.y) / det, (au.x * dv - av.x * du) / det);
            }
            float pxMetres = 1f / (Mathf.Abs(au.x) * MaskRes);

            PlaceWallow();
            CarveWallow(ctx);

            // ---- source texture
            var src = new Texture2D(2, 2, TextureFormat.RGBA32, false);
            src.LoadImage(File.ReadAllBytes(GroundSource));
            int W = src.width, H = src.height;
            Color32[] px = src.GetPixels32();

            // ---- masks at MaskRes
            int n = MaskRes;
            var brown = new bool[n * n];
            var keepPath = new bool[n * n];
            Vector3 grassSum = Vector3.zero; int grassN = 0;
            for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++)
            {
                Color32 c = px[(j * H / n) * W + i * W / n];
                Color.RGBToHSV(c, out float hh, out float s, out float v);
                bool b = hh > 0.025f && hh < 0.14f && s > 0.22f && v < 0.66f && v > 0.18f;
                brown[j * n + i] = b;
                if (hh > 0.17f && hh < 0.33f && s > 0.35f && v > 0.35f) { grassSum += new Vector3(c.r, c.g, c.b) / 255f; grassN++; }
                Vector2 w = World((i + 0.5f) / n, (j + 0.5f) / n);
                var p = new Vector3(w.x, 0f, w.y);
                keepPath[j * n + i] = DistToPath(p, RampRoad, out _, out _) < RampHalfWidth + 6f                       // plateau ramp
                                      || (Mathf.Abs(w.x) < 17f && w.y > -82f && w.y < -48f);                          // plaza
            }
            Color grass = grassN > 0 ? new Color(grassSum.x / grassN, grassSum.y / grassN, grassSum.z / grassN) : new Color(0.45f, 0.6f, 0.2f);

            // morphological opening: brown areas wider than 2*R become grass, thinner lines are paths
            int R = Mathf.Max(3, Mathf.RoundToInt(3.2f / pxMetres));
            float[] dIn = Chamfer(brown, n, true);                     // distance to the nearest non-brown texel
            var core = new bool[n * n];
            for (int k = 0; k < core.Length; k++) core[k] = dIn[k] > R;
            float[] dCore = Chamfer(core, n, false);                   // distance to the nearest core texel
            var area = new float[n * n];
            var path = new float[n * n];
            for (int k = 0; k < area.Length; k++)
            {
                if (!brown[k]) continue;
                if (keepPath[k]) { path[k] = 1f; continue; }
                if (dCore[k] <= R + 1.5f) area[k] = 1f; else path[k] = 1f;
            }
            area = Blur(area, n, 2);
            path = Blur(path, n, 1);

            // ---- write the full-resolution texture
            var outPx = new Color32[px.Length];
            Color pathCol = new Color(0.56f, 0.43f, 0.30f), mudWet = new Color(0.25f, 0.19f, 0.13f), mudDry = new Color(0.46f, 0.37f, 0.26f);
            for (int j = 0; j < H; j++)
            {
                float v = (j + 0.5f) / H, mj = v * n - 0.5f;
                for (int i = 0; i < W; i++)
                {
                    float u = (i + 0.5f) / W, mi = u * n - 0.5f;
                    Color c = px[j * W + i];
                    Vector2 w = World(u, v);
                    float a = Bilinear(area, n, mi, mj), pa = Bilinear(path, n, mi, mj);
                    float nz = ProceduralTextures.WorldFbm(w.x * 0.08f, w.y * 0.08f, 3, 1f, 91);
                    if (a > 0.003f)
                    {
                        float big = ProceduralTextures.WorldFbm(w.x * 0.015f, w.y * 0.015f, 2, 1f, 93);
                        Color g = grass * (0.82f + 0.3f * nz) * (0.92f + 0.16f * big);
                        g.a = 1f;
                        c = Color.Lerp(c, g, a);
                    }
                    if (pa > 0.003f)
                    {
                        Color pc = pathCol * (0.86f + 0.26f * nz);
                        pc.a = 1f;
                        c = Color.Lerp(c, pc, pa * 0.75f);
                    }
                    float e = WallowEllipse(w);                       // <1 inside
                    if (e < 1.45f)
                    {
                        float wet = 1f - Mathf.SmoothStep(0.55f, 1.0f, e);
                        float rim = 1f - Mathf.SmoothStep(1.0f, 1.45f, e);
                        Color m = Color.Lerp(mudDry * (0.85f + 0.3f * nz), mudWet * (0.85f + 0.3f * nz), wet);
                        m.a = 1f;
                        c = Color.Lerp(c, m, Mathf.Max(wet, rim * 0.85f));
                    }
                    outPx[j * W + i] = c;
                }
            }
            var dst = new Texture2D(W, H, TextureFormat.RGBA32, false);
            dst.SetPixels32(outPx);
            File.WriteAllBytes(Path.Combine(Directory.GetCurrentDirectory(), GroundPolished), dst.EncodeToPNG());
            Object.DestroyImmediate(src);
            Object.DestroyImmediate(dst);
            AssetDatabase.ImportAsset(GroundPolished, ImportAssetOptions.ForceUpdate);
            var tex = AssetDatabase.LoadAssetAtPath<Texture2D>(GroundPolished);

            // ---- material: polished texture + grass blade detail
            Material[] mats = mr.sharedMaterials;
            int slot = System.Array.FindIndex(mats, m => m != null && m.name.Contains("Ground"));
            if (slot < 0) slot = 0;
            Material baseMat = mats[slot];
            Material ground = Mat("M_Ground_Polished", LitShader, m =>
            {
                if (baseMat != null && baseMat != m) m.CopyPropertiesFromMaterial(baseMat);
                m.SetTexture("_BaseMap", tex);
                m.SetFloat("_UseMapColor", 1f);
                m.EnableKeyword("_TRIPLANAR");
                m.SetFloat("_Triplanar", 1f);
                m.SetTexture("_DetailMap", ProceduralTextures.GrassDetail);
                m.SetFloat("_DetailTiling", 0.9f);
                m.SetFloat("_DetailStrength", 0.55f);
                m.SetFloat("_StrataStrength", 0f);
                m.SetFloat("_MossAmount", 0f);
            });
            mats[slot] = ground;
            mr.sharedMaterials = mats;

            // ---- rock mounds: grassy tops
            int mossy = 0;
            foreach (string name in new[] { "M_TRN2_Rock_Ground", "M_TRN2_Rock_Mud", "M_TRN2_Rock_High" })
            {
                var m = AssetDatabase.LoadAssetAtPath<Material>($"{IslandMaterialFolder}/{name}.mat");
                if (m == null) continue;
                RockDetail(m, m.GetFloat("_DetailStrength") > 0f ? m.GetFloat("_DetailStrength") : 0.8f, m.GetFloat("_StrataStrength"), 0.9f);
                m.SetColor("_MossColor", grass * 0.95f);
                EditorUtility.SetDirty(m);
                mossy++;
            }

            int wallowParts = BuildWallow(ctx);
            ctx.Log.Add($"Ground: uv fit residual {residual:F4}, {pxMetres:F2} m per mask texel, opening radius {R} px; grass {grass}; " +
                        $"wallow at ({wallowCentre.x:F0},{wallowCentre.y:F0}) {WallowRadii.x * 2:F0}x{WallowRadii.y * 2:F0} m, {wallowParts} wallow props; {mossy} rock materials get grassy tops");
        }

        // ------------------------------------------------------------------ wallow
        /// <summary>Centre the wallow on the old puddles, then push it away from the river until it clears the bank.</summary>
        private static void PlaceWallow()
        {
            var puddles = new[] { new Vector2(-49.1f, -15.4f), new Vector2(-34.3f, 3.3f), new Vector2(-58.7f, -23.5f), new Vector2(-41.6f, -6.9f) };
            Vector2 c = puddles.Aggregate(Vector2.zero, (s, p) => s + p) / puddles.Length;
            // along the river so it fits the strip
            DistToPath(new Vector3(c.x, 0f, c.y), RiverLine, out float arc, out _);
            float run = 0f; Vector2 tan = Vector2.right;
            for (int i = 0; i < RiverLine.Length - 1; i++)
            {
                Vector2 a = new Vector2(RiverLine[i].x, RiverLine[i].z), b = new Vector2(RiverLine[i + 1].x, RiverLine[i + 1].z);
                float len = Vector2.Distance(a, b);
                if (run + len >= arc) { tan = (b - a).normalized; break; }
                run += len;
            }
            wallowAngle = Mathf.Atan2(tan.y, tan.x);
            Vector2 away = new Vector2(tan.y, -tan.x);
            for (int k = 0; k < 80; k++)
            {
                float d = DistToPath(new Vector3(c.x, 0f, c.y), RiverLine, out float a2, out _);
                float need = SampleWidths(RiverWidths, Mathf.Clamp01(a2 / 180f)) * 0.5f + 7f + WallowRadii.y;
                if (d >= need) break;
                // step away from the nearest river point
                Vector2 best = c; float bd = float.MaxValue;
                foreach (Vector3 rp in Resample(RiverLine, 2f))
                {
                    float dd = Vector2.Distance(new Vector2(rp.x, rp.z), c);
                    if (dd < bd) { bd = dd; best = new Vector2(rp.x, rp.z); }
                }
                Vector2 dir = (c - best).sqrMagnitude > 1e-4f ? (c - best).normalized : away;
                c += dir * 1f;
            }
            wallowCentre = c;
        }

        /// <summary>Elliptic distance: 0 at the centre, 1 on the wallow's waterline.</summary>
        private static float WallowEllipse(Vector2 w)
        {
            Vector2 d = w - wallowCentre;
            float ca = Mathf.Cos(-wallowAngle), sa = Mathf.Sin(-wallowAngle);
            Vector2 l = new Vector2(d.x * ca - d.y * sa, d.x * sa + d.y * ca);
            float wob = 1f + 0.12f * (ProceduralTextures.WorldFbm(w.x * 0.06f, w.y * 0.06f, 2, 1f, 97) - 0.5f) * 2f;
            return Mathf.Sqrt(l.x * l.x / (WallowRadii.x * WallowRadii.x) + l.y * l.y / (WallowRadii.y * WallowRadii.y)) / wob;
        }

        private static float wallowLevel;

        /// <summary>Lowers the ground into a shallow basin (deepest 0.9 m) with a gentle lip.</summary>
        private static void CarveWallow(Ctx ctx)
        {
            MeshFilter mf = ctx.Ground.GetComponent<MeshFilter>();
            Mesh mesh = Object.Instantiate(mf.sharedMesh);
            Transform gt = ctx.Ground.transform;
            Vector3[] v = mesh.vertices;
            // water level: the lowest ground on the rim, minus a little
            float rimMin = float.MaxValue;
            for (int k = 0; k < 64; k++)
            {
                float a = k / 64f * Mathf.PI * 2f;
                float ca = Mathf.Cos(wallowAngle), sa = Mathf.Sin(wallowAngle);
                Vector2 l = new Vector2(Mathf.Cos(a) * WallowRadii.x, Mathf.Sin(a) * WallowRadii.y);
                Vector2 w = wallowCentre + new Vector2(l.x * ca - l.y * sa, l.x * sa + l.y * ca);
                rimMin = Mathf.Min(rimMin, GroundY(ctx, w.x, w.y, 0.5f));
            }
            wallowLevel = Mathf.Max(rimMin - 0.12f, SeaLevel + 0.4f);
            int changed = 0;
            for (int i = 0; i < v.Length; i++)
            {
                Vector3 w = gt.TransformPoint(v[i]);
                float e = WallowEllipse(new Vector2(w.x, w.z));
                if (e > 1.35f) continue;
                float basin = wallowLevel - 0.9f * (1f - e * e);                 // bowl under the waterline
                float target = e < 1f ? basin : Mathf.Lerp(wallowLevel + 0.05f, w.y, Mathf.SmoothStep(1f, 1.35f, e));
                float y = e < 1f ? Mathf.Min(w.y, basin) : Mathf.Min(w.y, target);
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
            Physics.SyncTransforms();
            ctx.Log.Add($"Wallow basin: {changed} ground vertices lowered, mud level {wallowLevel:F2} m");
        }

        /// <summary>Mud surface over the basin, old puddles hidden, logs and stumps around the edge.</summary>
        private static int BuildWallow(Ctx ctx)
        {
            Transform water = ctx.Island.Find("Water");
            if (water != null)
                foreach (Transform t in water)
                    if (t.name.StartsWith("ISL2_MudPuddle")) t.gameObject.SetActive(false);
            // rocks and plants that would stand in the mud
            foreach (string g in new[] { "Plants", "Props" })
            {
                Transform group = ctx.Island.Find(g);
                if (group == null) continue;
                foreach (Transform child in group)
                {
                    var r = child.GetComponent<Renderer>();
                    if (r != null && WallowEllipse(new Vector2(r.bounds.center.x, r.bounds.center.z)) < 1.1f) child.gameObject.SetActive(false);
                }
            }

            // surface: ellipse grid, depth in vertex alpha for the water shader
            const int rings = 14, seg = 64;
            var verts = new List<Vector3>();
            var cols = new List<Color>();
            var tris = new List<int>();
            float ca = Mathf.Cos(wallowAngle), sa = Mathf.Sin(wallowAngle);
            verts.Add(new Vector3(wallowCentre.x, wallowLevel, wallowCentre.y));
            cols.Add(new Color(0.5f, 0.5f, 0.02f, 0.9f / RiverDepthMax));
            for (int r = 1; r <= rings; r++)
            for (int s = 0; s < seg; s++)
            {
                float rr = r / (float)rings * 1.08f, a = s / (float)seg * Mathf.PI * 2f;
                Vector2 l = new Vector2(Mathf.Cos(a) * WallowRadii.x * rr, Mathf.Sin(a) * WallowRadii.y * rr);
                Vector2 w = wallowCentre + new Vector2(l.x * ca - l.y * sa, l.x * sa + l.y * ca);
                float g = GroundY(ctx, w.x, w.y, wallowLevel - 0.5f);
                verts.Add(new Vector3(w.x, wallowLevel, w.y));
                cols.Add(new Color(0.5f, 0.5f, 0.02f, Mathf.Clamp(wallowLevel - g, 0f, RiverDepthMax) / RiverDepthMax));
            }
            for (int s = 0; s < seg; s++) tris.AddRange(new[] { 0, 1 + (s + 1) % seg, 1 + s });
            for (int r = 1; r < rings; r++)
            for (int s = 0; s < seg; s++)
            {
                int a = 1 + (r - 1) * seg + s, b = 1 + (r - 1) * seg + (s + 1) % seg, c = a + seg, d = b + seg;
                tris.AddRange(new[] { a, b, c, b, d, c });
            }
            var mesh = new Mesh();
            mesh.SetVertices(verts);
            mesh.SetColors(cols);
            mesh.SetTriangles(tris, 0);
            mesh.SetNormals(Enumerable.Repeat(Vector3.up, verts.Count).ToList());
            mesh.RecalculateBounds();
            if (mesh.normals.Length > 0 && Vector3.Cross(verts[tris[1]] - verts[tris[0]], verts[tris[2]] - verts[tris[0]]).y < 0f)
            {
                for (int i = 0; i < tris.Count; i += 3) (tris[i + 1], tris[i + 2]) = (tris[i + 2], tris[i + 1]);
                mesh.SetTriangles(tris, 0);
            }
            Material mud = Mat("M_Water_Mud", WaterShader, m => { });
            mud.SetColor("_ShallowColor", new Color(0.36f, 0.28f, 0.19f));
            mud.SetColor("_DeepColor", new Color(0.20f, 0.15f, 0.10f));
            mud.SetFloat("_AlphaShallow", 0.85f);
            mud.SetFloat("_AlphaDepth", 0.25f);
            mud.SetFloat("_Reflectivity", 0.12f);
            mud.SetFloat("_SpecIntensity", 0.35f);
            mud.SetFloat("_SpecPower", 60f);
            mud.SetFloat("_NormalStrength", 0.2f);
            mud.SetFloat("_FlowSpeed", 0.05f);
            mud.SetFloat("_EdgeFoamDistance", 0.12f);
            mud.SetColor("_FoamColor", new Color(0.30f, 0.23f, 0.16f));
            EditorUtility.SetDirty(mud);
            Transform group2 = Group(ctx.Polish, "Mud Wallow");
            MeshObject("Mud", group2, SaveMesh(mesh, "Mud_Wallow"), new[] { mud }, false, ShadowCastingMode.Off);

            // logs, stumps and a few boulders on the rim
            string[] kinds = { "PLN_Log_Mossy", "PLN_Log_Hollow", "PLN_Stump_Short", "TRN_Boulder_Round", "PLN_Horsetails_Small", "PLN_Reeds" };
            var rng = new System.Random(515);
            int placed = 0;
            for (int k = 0; k < 14; k++)
            {
                string kind = kinds[rng.Next(kinds.Length)];
                var prefab = AssetDatabase.LoadAssetAtPath<GameObject>($"{PrefabFolder}/{kind}.prefab");
                if (prefab == null) continue;
                float a = (k + (float)rng.NextDouble() * 0.6f) / 14f * Mathf.PI * 2f;
                float rr = 1.05f + (float)rng.NextDouble() * 0.25f;
                Vector2 l = new Vector2(Mathf.Cos(a) * WallowRadii.x * rr, Mathf.Sin(a) * WallowRadii.y * rr);
                Vector2 w = wallowCentre + new Vector2(l.x * ca - l.y * sa, l.x * sa + l.y * ca);
                float g = GroundY(ctx, w.x, w.y, float.NaN);
                if (float.IsNaN(g)) continue;
                var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, group2);
                go.transform.SetPositionAndRotation(new Vector3(w.x, g - 0.1f, w.y), Quaternion.Euler(0f, (float)rng.NextDouble() * 360f, 0f));
                float s = kind.StartsWith("TRN") ? 0.6f + (float)rng.NextDouble() * 0.5f : 1.6f + (float)rng.NextDouble() * 0.8f;
                go.transform.localScale = Vector3.one * s;
                placed++;
            }
            return placed;
        }

        // ------------------------------------------------------------------ helpers
        /// <summary>Least-squares affine fit uv = A * (x, z, 1) over every 40th ground vertex (the ground is planar-mapped).</summary>
        private static bool FitGroundUv(Mesh mesh, Transform t, out Vector3 au, out Vector3 av, out float residual)
        {
            var uv = new List<Vector2>();
            mesh.GetUVs(0, uv);
            Vector3[] v = mesh.vertices;
            au = av = Vector3.zero; residual = float.MaxValue;
            if (uv.Count != v.Length || v.Length == 0) return false;
            double sxx = 0, sxz = 0, szz = 0, sx = 0, sz = 0, s1 = 0, ux = 0, uz = 0, u1 = 0, vx = 0, vz = 0, v1 = 0;
            for (int i = 0; i < v.Length; i += 40)
            {
                Vector3 w = t.TransformPoint(v[i]);
                double x = w.x, z = w.z;
                sxx += x * x; sxz += x * z; szz += z * z; sx += x; sz += z; s1 += 1;
                ux += uv[i].x * x; uz += uv[i].x * z; u1 += uv[i].x;
                vx += uv[i].y * x; vz += uv[i].y * z; v1 += uv[i].y;
            }
            var m = new double[3, 3] { { sxx, sxz, sx }, { sxz, szz, sz }, { sx, sz, s1 } };
            double[] Solve(double a, double b, double c)
            {
                double D = Det3(m);
                if (System.Math.Abs(D) < 1e-9) return null;
                var r = new double[3];
                for (int col = 0; col < 3; col++)
                {
                    var mm = (double[,])m.Clone();
                    mm[0, col] = a; mm[1, col] = b; mm[2, col] = c;
                    r[col] = Det3(mm) / D;
                }
                return r;
            }
            double[] pu = Solve(ux, uz, u1), pv = Solve(vx, vz, v1);
            if (pu == null || pv == null) return false;
            au = new Vector3((float)pu[0], (float)pu[1], (float)pu[2]);
            av = new Vector3((float)pv[0], (float)pv[1], (float)pv[2]);
            float worst = 0f;
            for (int i = 0; i < v.Length; i += 97)
            {
                Vector3 w = t.TransformPoint(v[i]);
                float du = au.x * w.x + au.y * w.z + au.z - uv[i].x, dv = av.x * w.x + av.y * w.z + av.z - uv[i].y;
                worst = Mathf.Max(worst, Mathf.Abs(du), Mathf.Abs(dv));
            }
            residual = worst;
            return worst < 0.01f;
        }

        private static double Det3(double[,] m) =>
            m[0, 0] * (m[1, 1] * m[2, 2] - m[1, 2] * m[2, 1]) - m[0, 1] * (m[1, 0] * m[2, 2] - m[1, 2] * m[2, 0]) + m[0, 2] * (m[1, 0] * m[2, 1] - m[1, 1] * m[2, 0]);

        /// <summary>Two-pass chamfer distance (texels). inside = true: distance from each set texel to the nearest unset one; false: to the nearest set one.</summary>
        private static float[] Chamfer(bool[] mask, int n, bool inside)
        {
            var d = new float[n * n];
            for (int k = 0; k < d.Length; k++) d[k] = (mask[k] == inside) ? 1e6f : 0f;
            const float a = 1f, b = 1.4142f;
            for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++)
            {
                int k = j * n + i;
                if (d[k] == 0f) continue;
                if (i > 0) d[k] = Mathf.Min(d[k], d[k - 1] + a);
                if (j > 0)
                {
                    d[k] = Mathf.Min(d[k], d[k - n] + a);
                    if (i > 0) d[k] = Mathf.Min(d[k], d[k - n - 1] + b);
                    if (i < n - 1) d[k] = Mathf.Min(d[k], d[k - n + 1] + b);
                }
            }
            for (int j = n - 1; j >= 0; j--)
            for (int i = n - 1; i >= 0; i--)
            {
                int k = j * n + i;
                if (d[k] == 0f) continue;
                if (i < n - 1) d[k] = Mathf.Min(d[k], d[k + 1] + a);
                if (j < n - 1)
                {
                    d[k] = Mathf.Min(d[k], d[k + n] + a);
                    if (i < n - 1) d[k] = Mathf.Min(d[k], d[k + n + 1] + b);
                    if (i > 0) d[k] = Mathf.Min(d[k], d[k + n - 1] + b);
                }
            }
            return d;
        }

        private static float[] Blur(float[] src, int n, int radius)
        {
            var tmp = new float[src.Length];
            var dst = new float[src.Length];
            int c = radius * 2 + 1;
            for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++)
            {
                float s = 0f;
                for (int k = -radius; k <= radius; k++) s += src[j * n + Mathf.Clamp(i + k, 0, n - 1)];
                tmp[j * n + i] = s / c;
            }
            for (int j = 0; j < n; j++)
            for (int i = 0; i < n; i++)
            {
                float s = 0f;
                for (int k = -radius; k <= radius; k++) s += tmp[Mathf.Clamp(j + k, 0, n - 1) * n + i];
                dst[j * n + i] = s / c;
            }
            return dst;
        }

        private static float Bilinear(float[] m, int n, float x, float y)
        {
            x = Mathf.Clamp(x, 0f, n - 1.001f); y = Mathf.Clamp(y, 0f, n - 1.001f);
            int i = (int)x, j = (int)y;
            float fx = x - i, fy = y - j;
            float a = m[j * n + i], b = m[j * n + i + 1], c = m[(j + 1) * n + i], d = m[(j + 1) * n + i + 1];
            return Mathf.Lerp(Mathf.Lerp(a, b, fx), Mathf.Lerp(c, d, fx), fy);
        }
    }
}
