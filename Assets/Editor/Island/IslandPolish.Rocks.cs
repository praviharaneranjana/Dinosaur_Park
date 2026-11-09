using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace DinoPark.EditorTools
{
    public static partial class IslandPolish
    {
        private const string RockModelFolder = "Assets/Models/Environment/Rocks";
        private const string RockTexFolder = "Assets/Textures/Environment/Rocks";
        private const string RockPrefabFolder = "Assets/Prefabs/Environment/Rocks";
        private const string RockLodFolder = "Assets/Models/Environment/Rocks/Lod";
        private const string CliffDetailPath = "Assets/Textures/Environment/Island/T_RiverbedRock_Detail.png";
        private const int CliffRows = 18;   // must match BuildCliff

        /// <summary>
        /// Rocks from the supplied sculpted stones (build_stones_kit.py: ~3k tris each, baked albedo + normal
        /// atlas): a rock apron along the whole plateau cliff foot (hides the jagged foot, real 3D rocks
        /// instead of flat cards), replacements for the flat coastal sea stacks and the low-poly boulders
        /// near the cliff, and the riverbed rock photo as the cliff face detail.
        /// </summary>
        private static void BuildRocks(Ctx ctx)
        {
            var kit = RockKit();
            if (kit.Count == 0) { ctx.Log.Add("Rocks: kit not found in " + RockModelFolder + ", skipped (run build_stones_kit.py)"); return; }

            // cliff face: real rock photo as detail
            var detail = AssetDatabase.LoadAssetAtPath<Texture2D>(CliffDetailPath);
            if (detail != null)
            {
                var ti = (TextureImporter)AssetImporter.GetAtPath(CliffDetailPath);
                if (ti.sRGBTexture || ti.maxTextureSize != 1024)
                {
                    ti.sRGBTexture = false;
                    ti.maxTextureSize = 1024;
                    var android = ti.GetPlatformTextureSettings("Android");
                    android.overridden = true; android.maxTextureSize = 512; android.format = TextureImporterFormat.ASTC_6x6;
                    ti.SetPlatformTextureSettings(android);
                    ti.SaveAndReimport();
                }
                var cliffMat = AssetDatabase.LoadAssetAtPath<Material>($"{MaterialFolder}/M_Cliff_Rock.mat");
                if (cliffMat != null)
                {
                    cliffMat.SetTexture("_DetailMap", detail);
                    cliffMat.SetFloat("_DetailTiling", 0.28f);
                    cliffMat.SetFloat("_DetailStrength", 1.1f);
                    cliffMat.SetFloat("_MossAmount", 0.4f);
                    EditorUtility.SetDirty(cliffMat);
                }
            }

            Transform root = Group(ctx.Polish, "Rocks");
            var rng = new System.Random(919);
            int apron = 0, stacks = 0, boulders = 0;

            // ---- cliff foot apron
            Transform cliffT = ctx.Polish.Find("Terrain/Cliff_Plateau");
            var foot = new List<(Vector3 at, Vector3 outward)>();
            if (cliffT != null)
            {
                Mesh cm = cliffT.GetComponent<MeshFilter>().sharedMesh;
                Vector3[] v = cm.vertices;
                int stride = CliffRows + 1;
                for (int c = 0; c + stride <= v.Length; c += stride)
                {
                    Vector3 top = cliffT.TransformPoint(v[c]), bottom = cliffT.TransformPoint(v[c + CliffRows]);
                    if (top.y - bottom.y < 3f) continue;                                         // low lip, no rocks
                    Vector3 o = bottom - top; o.y = 0f;
                    foot.Add((bottom, o.sqrMagnitude > 1e-4f ? o.normalized : Vector3.forward));
                }
            }
            Vector3 fallAt = Vector3.positiveInfinity;
            Transform falls = ctx.Polish.Find("Waterfalls");
            if (falls != null)
                foreach (Transform f in falls) if (f.name.Contains("Main")) fallAt = f.GetComponentInChildren<Renderer>().bounds.center;
            Vector3 last = Vector3.positiveInfinity;
            foreach (var (at, outward) in foot)
            {
                if ((at - last).sqrMagnitude < 5.5f * 5.5f) continue;
                Vector2 a2 = new Vector2(at.x, at.z);
                if (!float.IsInfinity(fallAt.x) && Vector2.Distance(a2, new Vector2(fallAt.x, fallAt.z)) < 9f) continue;   // keep the plunge clear
                if (DistToPath(at, RampRoad, out _, out _) < RampHalfWidth + 3f) continue;
                if (DistToPath(at, RiverLine, out float ra, out _) < SampleWidths(RiverWidths, Mathf.Clamp01(ra / 180f)) * 0.5f + 1f) continue;
                last = at;
                int n = 1 + rng.Next(3);                                                        // 1-3 rocks per spot
                for (int k = 0; k < n; k++)
                {
                    Vector3 side = Vector3.Cross(Vector3.up, outward);
                    Vector3 p = at + outward * (0.4f + (float)rng.NextDouble() * 2.2f) + side * ((float)rng.NextDouble() - 0.5f) * 4f;
                    float g = GroundY(ctx, p.x, p.z, at.y);
                    float h = k == 0 ? 2.6f + (float)rng.NextDouble() * 2.6f : 1.0f + (float)rng.NextDouble() * 1.4f;
                    PlaceRock(kit, root, rng, new Vector3(p.x, Mathf.Min(g, at.y + 0.5f), p.z), h, 0.3f);
                    apron++;
                }
            }

            // ---- coastal sea stacks (flat low-poly Rock_Coast mounds) -> clusters of real rocks
            // ---- low-poly boulders near the cliff foot -> single rocks
            Transform props = ctx.Island.Find("Props");
            if (props != null)
            {
                foreach (Transform t in props.Cast<Transform>().ToList())
                {
                    var r = t.GetComponent<Renderer>();
                    if (r == null || !t.gameObject.activeSelf) continue;
                    Bounds b = r.bounds;
                    bool coastStack = t.name.Contains("RockyHill") && r.sharedMaterial != null && r.sharedMaterial.name.Contains("Coast");
                    bool cliffBoulder = t.name.Contains("Boulder") && foot.Any(f => (new Vector2(f.at.x, f.at.z) - new Vector2(b.center.x, b.center.z)).sqrMagnitude < 14f * 14f);
                    if (!coastStack && !cliffBoulder) continue;
                    t.gameObject.SetActive(false);
                    float height = Mathf.Max(b.size.y, 0.8f);
                    Vector3 basePt = new Vector3(b.center.x, b.min.y, b.center.z);
                    if (coastStack)
                    {
                        PlaceRock(kit, root, rng, basePt, height * 1.05f, 0.2f, Mathf.Max(b.size.x, b.size.z) * 0.75f);
                        int extra = 1 + rng.Next(3);
                        for (int k = 0; k < extra; k++)
                        {
                            float ang = (float)rng.NextDouble() * Mathf.PI * 2f;
                            Vector3 off = new Vector3(Mathf.Cos(ang), 0f, Mathf.Sin(ang)) * Mathf.Max(b.extents.x, b.extents.z) * (0.5f + (float)rng.NextDouble() * 0.5f);
                            PlaceRock(kit, root, rng, basePt + off, height * (0.3f + (float)rng.NextDouble() * 0.35f), 0.25f);
                        }
                        stacks++;
                    }
                    else
                    {
                        PlaceRock(kit, root, rng, basePt, height * 1.1f, 0.25f);
                        boulders++;
                    }
                }
            }
            ctx.Log.Add($"Rocks: {kit.Count} kit rocks; {apron} along the cliff foot ({foot.Count} foot columns), {stacks} sea stacks and {boulders} boulders replaced; cliff detail {(detail != null ? "riverbed photo" : "missing")}");
        }

        /// <summary>One rock: random kit piece and yaw, a little tilt, scaled to <paramref name="height"/>, sunk by <paramref name="sink"/> of its height.</summary>
        private static void PlaceRock(List<(GameObject prefab, Vector3 size)> kit, Transform parent, System.Random rng, Vector3 basePt, float height, float sink, float maxWidth = 0f)
        {
            var pick = kit[rng.Next(kit.Count)];
            float s = height / Mathf.Max(pick.size.y, 0.1f);
            if (maxWidth > 0f) s = Mathf.Min(s, maxWidth * 2f / Mathf.Max(pick.size.x, pick.size.z));
            var go = (GameObject)PrefabUtility.InstantiatePrefab(pick.prefab, parent);
            go.transform.SetPositionAndRotation(basePt - Vector3.up * (pick.size.y * s * sink),
                Quaternion.Euler(((float)rng.NextDouble() - 0.5f) * 16f, (float)rng.NextDouble() * 360f, ((float)rng.NextDouble() - 0.5f) * 16f));
            go.transform.localScale = Vector3.one * s * (0.9f + (float)rng.NextDouble() * 0.2f);
        }

        /// <summary>Prefabs for the exported rocks (material, LOD1 at ~30%, cull when tiny), built once per polish run.</summary>
        private static List<(GameObject prefab, Vector3 size)> RockKit()
        {
            var list = new List<(GameObject, Vector3)>();
            string[] fbx = AssetDatabase.FindAssets("ENV_Stone_ t:Model", new[] { RockModelFolder }).Select(AssetDatabase.GUIDToAssetPath).OrderBy(p => p).ToArray();
            if (fbx.Length == 0) return list;
            ProceduralTextures.EnsureFolder(RockPrefabFolder);
            ProceduralTextures.EnsureFolder(RockLodFolder);

            string normalPath = RockTexFolder + "/T_Stones_Normal.png", albedoPath = RockTexFolder + "/T_Stones_Albedo.png";
            foreach (string p in new[] { normalPath, albedoPath })
            {
                var ti = AssetImporter.GetAtPath(p) as TextureImporter;
                if (ti == null) continue;
                bool isNormal = p == normalPath;
                var android = ti.GetPlatformTextureSettings("Android");
                if (ti.textureType == (isNormal ? TextureImporterType.NormalMap : TextureImporterType.Default) && android.overridden) continue;
                ti.textureType = isNormal ? TextureImporterType.NormalMap : TextureImporterType.Default;
                ti.maxTextureSize = 2048;
                android.overridden = true; android.maxTextureSize = 1024; android.format = TextureImporterFormat.ASTC_6x6;
                ti.SetPlatformTextureSettings(android);
                ti.SaveAndReimport();
            }
            Material mat = Mat("M_Stones", "Universal Render Pipeline/Lit", m =>
            {
                m.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>(albedoPath));
                m.SetColor("_BaseColor", new Color(0.92f, 0.9f, 0.86f));
                m.SetTexture("_BumpMap", AssetDatabase.LoadAssetAtPath<Texture2D>(normalPath));
                m.SetFloat("_BumpScale", 1.2f);
                m.EnableKeyword("_NORMALMAP");
                m.SetFloat("_Smoothness", 0.12f);
                m.SetFloat("_Metallic", 0f);
            });

            foreach (string path in fbx)
            {
                Mesh mesh = AssetDatabase.LoadAllAssetsAtPath(path).OfType<Mesh>().FirstOrDefault();
                if (mesh == null) continue;
                string key = System.IO.Path.GetFileNameWithoutExtension(path);
                Mesh work = Object.Instantiate(mesh);
                MeshLodUtility.GenerateMeshLods(work, 0, -1);
                Mesh lod1 = work.lodCount > 2 ? RockLevel(work, Mathf.Min(2, work.lodCount - 1), key + "_LOD1") : null;
                Object.DestroyImmediate(work);

                var go = new GameObject(key);
                go.AddComponent<MeshFilter>().sharedMesh = mesh;
                var mr = go.AddComponent<MeshRenderer>();
                mr.sharedMaterial = mat;
                var lods = new List<LOD>();
                if (lod1 != null)
                {
                    var c = new GameObject("LOD1");
                    c.transform.SetParent(go.transform, false);
                    c.AddComponent<MeshFilter>().sharedMesh = lod1;
                    var r1 = c.AddComponent<MeshRenderer>();
                    r1.sharedMaterial = mat;
                    r1.shadowCastingMode = ShadowCastingMode.Off;
                    lods.Add(new LOD(0.18f, new Renderer[] { mr }));
                    lods.Add(new LOD(0.012f, new Renderer[] { r1 }));
                }
                else lods.Add(new LOD(0.012f, new Renderer[] { mr }));
                var group = go.AddComponent<LODGroup>();
                group.SetLODs(lods.ToArray());
                group.RecalculateBounds();
                GameObject prefab = PrefabUtility.SaveAsPrefabAsset(go, $"{RockPrefabFolder}/{key}.prefab");
                Object.DestroyImmediate(go);
                list.Add((prefab, mesh.bounds.size));
            }
            return list;
        }

        /// <summary>Plain mesh holding one generated LOD level (copies the vertex streams the rock material needs).</summary>
        private static Mesh RockLevel(Mesh src, int level, string name)
        {
            var m = new Mesh { name = name, indexFormat = src.indexFormat };
            m.vertices = src.vertices;
            m.normals = src.normals;
            m.tangents = src.tangents;
            var uv = new List<Vector2>();
            src.GetUVs(0, uv);
            m.SetUVs(0, uv);
            m.SetIndices(src.GetIndices(0, level, true), MeshTopology.Triangles, 0);
            m.RecalculateBounds();
            string path = $"{RockLodFolder}/{name}.asset";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(m, path);
            return m;
        }
    }
}
