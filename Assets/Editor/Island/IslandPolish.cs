using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using DinoPark.Environment;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace DinoPark.EditorTools
{
    /// <summary>
    /// Unity-side polish of the imported Blender island (runs after IslandImporter, or from the menu):
    /// wind on plants, flat walkable ramp and entrance road, rebuilt plateau cliff, animated river /
    /// pond / mud water, rebuilt waterfalls with spray and mist, wave ocean with surf, the land side
    /// (mountain, tunnel portal, asphalt road, visitor cars) and the east-side camera.
    /// Everything it creates lives under "--- Island Polish ---" and in Generated/Polish asset folders,
    /// and Blender objects it replaces are only disabled, so it is safe to run again.
    /// All positions are Unity world metres: Unity (x, y, z) = Blender (x, z, y) after the importer's
    /// 180-degree turn, so values copied from island_map_v02.json are written with B(x, y, z).
    /// </summary>
    public static partial class IslandPolish
    {
        private const string ScenePath = "Assets/Scenes/Island.unity";
        private const string GroupName = "--- Island Polish ---";
        private const string GeneratedFolder = "Assets/Models/Environment/Island/Generated";
        private const string MaterialFolder = "Assets/Materials/Environment/Island/Polish";
        private const string IslandMaterialFolder = "Assets/Materials/Environment/Island";
        private const string PrefabFolder = "Assets/Prefabs/Environment/Island";
        private const string LitShader = "DinoPark/Environment/VertexColorLit";

        /// <summary>Sea level of the island map (Blender sea_level_m).</summary>
        public const float SeaLevel = -0.45f;

        private static Vector3 B(float x, float y, float z) => new Vector3(x, z, y);

        /// <summary>Scene objects the steps share.</summary>
        private sealed class Ctx
        {
            public Transform Island;
            public Transform Polish;
            public GameObject Ground;
            public MeshCollider GroundCollider;
            public readonly List<string> Log = new List<string>();
            public List<Vector3> EntranceProfile;   // road centre line from tunnel end to plaza, y = road height
            public float ApronY;
            public float PortalZ;
        }

        [MenuItem("Dino Park/Island/Apply Polish Pass")]
        public static void ApplyMenu()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Apply(scene);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
        }

        /// <summary>Runs every polish step on an open Island scene (does not save it).</summary>
        public static void Apply(Scene scene)
        {
            GameObject envRoot = scene.GetRootGameObjects().FirstOrDefault(g => g.name == "=== Environment ===");
            Transform island = envRoot != null ? envRoot.transform.Find("--- Island ---") : null;
            if (island == null)
            {
                Debug.LogError("[DinoPark] Polish: no '--- Island ---' group. Run the island import first.");
                return;
            }

            Transform old = envRoot.transform.Find(GroupName);
            if (old != null) Object.DestroyImmediate(old.gameObject);
            var polish = new GameObject(GroupName).transform;
            polish.SetParent(envRoot.transform, false);

            // Start from the imported state every time: re-enable what an earlier run hid.
            foreach (Transform group in island)
                foreach (Transform child in group)
                    child.gameObject.SetActive(true);

            var ctx = new Ctx { Island = island, Polish = polish };
            ctx.Ground = Find(island, "Terrain/ISL2_Ground");
            ctx.GroundCollider = ctx.Ground != null ? ctx.Ground.GetComponent<MeshCollider>() : null;
            if (ctx.GroundCollider == null)
            {
                Debug.LogError("[DinoPark] Polish: ISL2_Ground with a MeshCollider not found.");
                return;
            }

            ProceduralTextures.EnsureFolder(GeneratedFolder);
            ProceduralTextures.EnsureFolder(MaterialFolder);
            var steps = new (string name, Action<Ctx> run)[]
            {
                ("Wind", ConfigureWind),
                ("Ramp and entrance road", FlattenPaths),
                ("Plateau cliff", BuildCliff),
                ("Mountain and tunnel", BuildMountainAndTunnel),
                ("Road", BuildRoad),
                ("River, ponds and waterfalls", RestyleWater),
                ("Ocean", BuildOcean),
                ("Traffic", BuildTraffic),
                ("Camera", ConfigureCamera),
                ("Mobile optimization", OptimizeForMobile),
            };
            try
            {
                for (int i = 0; i < steps.Length; i++)
                {
                    EditorUtility.DisplayProgressBar("Island polish", steps[i].name, (float)i / steps.Length);
                    Physics.SyncTransforms();
                    steps[i].run(ctx);
                }
            }
            finally
            {
                EditorUtility.ClearProgressBar();
                AssetDatabase.SaveAssets();
            }
            Debug.Log("[DinoPark] Island polish done:\n" + string.Join("\n", ctx.Log));
        }

        // ------------------------------------------------------------------ wind
        private static void ConfigureWind(Ctx ctx)
        {
            int n = 0;
            foreach (string guid in AssetDatabase.FindAssets("t:Material", new[] { IslandMaterialFolder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (path.StartsWith(MaterialFolder)) continue;
                var m = AssetDatabase.LoadAssetAtPath<Material>(path);
                if (m == null || !m.HasProperty("_WindSway")) continue;
                string name = m.name;
                float sway = 0f, flutter = 0f;
                if (name.Contains("PLN"))
                {
                    if (Has(name, "Log", "Stump", "Water_", "LilyPad", "Lotus")) { sway = 0f; flutter = 0f; }
                    else if (Has(name, "Grass", "Clover", "Reed", "Cattail", "Horsetail", "Flower", "Toxic", "Fern_")) { sway = 0.35f; flutter = 1.1f; }
                    else if (Has(name, "Leaf", "Frond", "Needle", "Petal")) { sway = 1f; flutter = 0.55f; }
                    else { sway = 1f; flutter = 0f; }   // bark, trunks, cones, cores: bend with their leaves
                }
                m.SetFloat("_WindSway", sway);
                m.SetFloat("_WindFlutter", flutter);
                EditorUtility.SetDirty(m);
                if (sway + flutter > 0f) n++;
            }
            var wind = new GameObject("Wind").AddComponent<WindSettings>();
            wind.transform.SetParent(ctx.Polish, false);
            ctx.Log.Add($"Wind: {n} plant materials sway");
        }

        // ------------------------------------------------------------------ shared helpers
        private static bool Has(string s, params string[] parts) => parts.Any(s.Contains);

        private static GameObject Find(Transform root, string path)
        {
            Transform t = root.Find(path);
            return t != null ? t.gameObject : null;
        }

        private static float GroundY(Ctx ctx, float x, float z, float fallback = float.NaN)
        {
            var ray = new Ray(new Vector3(x, 400f, z), Vector3.down);
            return ctx.GroundCollider.Raycast(ray, out RaycastHit hit, 800f) ? hit.point.y : fallback;
        }

        private static Material Mat(string name, string shader, Action<Material> setup)
        {
            string path = $"{MaterialFolder}/{name}.mat";
            var m = AssetDatabase.LoadAssetAtPath<Material>(path);
            Shader s = Shader.Find(shader);
            if (s == null) throw new InvalidOperationException("Shader not found: " + shader);
            if (m == null)
            {
                m = new Material(s);
                AssetDatabase.CreateAsset(m, path);
            }
            m.shader = s;
            m.enableInstancing = true;
            setup(m);
            EditorUtility.SetDirty(m);
            return m;
        }

        private static void Opaque(Material m, Color tint, float smoothness = 0.1f)
        {
            m.SetColor("_BaseColor", tint);
            m.SetFloat("_Smoothness", smoothness);
            m.SetFloat("_SrcBlend", (float)BlendMode.One);
            m.SetFloat("_DstBlend", (float)BlendMode.Zero);
            m.SetFloat("_ZWrite", 1f);
            m.renderQueue = (int)RenderQueue.Geometry;
        }

        private static void RockDetail(Material m, float strength, float strata, float moss)
        {
            m.EnableKeyword("_TRIPLANAR");
            m.SetFloat("_Triplanar", 1f);
            m.SetTexture("_DetailMap", ProceduralTextures.RockDetail);
            m.SetFloat("_DetailStrength", strength);
            m.SetFloat("_StrataStrength", strata);
            m.SetFloat("_MossAmount", moss);
        }

        private static Mesh SaveMesh(Mesh mesh, string name)
        {
            string path = $"{GeneratedFolder}/{name}.asset";
            var existing = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            mesh.name = name;
            if (existing == null)
            {
                AssetDatabase.CreateAsset(mesh, path);
                return mesh;
            }
            existing.Clear();
            EditorUtility.CopySerialized(mesh, existing);
            Object.DestroyImmediate(mesh);
            return existing;
        }

        private static GameObject MeshObject(string name, Transform parent, Mesh mesh, Material[] mats, bool collider, ShadowCastingMode shadows = ShadowCastingMode.On)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var r = go.AddComponent<MeshRenderer>();
            r.sharedMaterials = mats;
            r.shadowCastingMode = shadows;
            if (collider) go.AddComponent<MeshCollider>().sharedMesh = mesh;
            return go;
        }

        private static Transform Group(Transform parent, string name)
        {
            var t = new GameObject(name).transform;
            t.SetParent(parent, false);
            return t;
        }

        /// <summary>Distance in XZ from p to a polyline, with arc length and interpolated height of the closest point.</summary>
        private static float DistToPath(Vector3 p, IReadOnlyList<Vector3> path, out float arc, out float y)
        {
            float best = float.MaxValue, run = 0f;
            arc = 0f; y = path[0].y;
            for (int i = 0; i < path.Count - 1; i++)
            {
                Vector2 a = new Vector2(path[i].x, path[i].z), b = new Vector2(path[i + 1].x, path[i + 1].z);
                Vector2 ab = b - a, q = new Vector2(p.x, p.z);
                float len2 = Mathf.Max(ab.sqrMagnitude, 1e-6f);
                float t = Mathf.Clamp01(Vector2.Dot(q - a, ab) / len2);
                float d = Vector2.Distance(q, a + ab * t);
                if (d < best)
                {
                    best = d;
                    arc = run + Mathf.Sqrt(len2) * t;
                    y = Mathf.Lerp(path[i].y, path[i + 1].y, t);
                }
                run += Mathf.Sqrt(len2);
            }
            return best;
        }

        /// <summary>Resamples a polyline every <paramref name="step"/> metres (keeps y interpolated).</summary>
        private static List<Vector3> Resample(IReadOnlyList<Vector3> pts, float step)
        {
            var outPts = new List<Vector3> { pts[0] };
            float carry = 0f;
            for (int i = 0; i < pts.Count - 1; i++)
            {
                Vector3 a = pts[i], b = pts[i + 1];
                float len = Vector2.Distance(new Vector2(a.x, a.z), new Vector2(b.x, b.z));
                float d = step - carry;
                while (d <= len)
                {
                    outPts.Add(Vector3.Lerp(a, b, d / Mathf.Max(len, 1e-5f)));
                    d += step;
                }
                carry = len - (d - step);
            }
            if (Vector3.Distance(outPts[outPts.Count - 1], pts[pts.Count - 1]) > step * 0.3f) outPts.Add(pts[pts.Count - 1]);
            return outPts;
        }

        private static void SmoothHeights(List<Vector3> pts, int radius, int iterations = 1)
        {
            for (int it = 0; it < iterations; it++)
            {
                var ys = pts.Select(p => p.y).ToArray();
                for (int i = 1; i < pts.Count - 1; i++)
                {
                    float sum = 0f; int n = 0;
                    for (int k = -radius; k <= radius; k++)
                    {
                        int j = Mathf.Clamp(i + k, 0, pts.Count - 1);
                        sum += ys[j]; n++;
                    }
                    pts[i] = new Vector3(pts[i].x, sum / n, pts[i].z);
                }
            }
        }

        private static float Hash(int i, int seed)
        {
            uint h = (uint)(i * 374761393 + seed * 668265263);
            h = (h ^ (h >> 13)) * 1274126177u;
            return (h & 0xffff) / 65535f;
        }
    }
}
