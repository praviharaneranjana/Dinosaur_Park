using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using DinoPark.CameraControl;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using Object = UnityEngine.Object;

namespace DinoPark.EditorTools
{
    /// <summary>
    /// Builds the Blender island (ISL_Main_v05) into Assets/Scenes/Island.unity from the export
    /// written by _Source/Blender/00_Shared/Tools/export_island_unity.py:
    /// materials (baked vertex colour shader), one prefab per unique mesh, and one prefab instance
    /// per Blender object. Re-running replaces the "--- Island ---" group, so it is safe to repeat
    /// after a new export. Placeholders from IslandSceneBuilder are disabled, not deleted.
    /// </summary>
    public static class IslandImporter
    {
        public const string Root = "Assets/Models/Environment/Island";
        private const string LayoutFile = Root + "/island_layout.json";
        private const string MaterialFolder = "Assets/Materials/Environment/Island";
        private const string PrefabFolder = "Assets/Prefabs/Environment/Island";
        private const string ScenePath = "Assets/Scenes/Island.unity";
        private const string ShaderName = "DinoPark/Environment/VertexColorLit";
        private const string GroupName = "--- Island ---";
        private const string CameraConfigPath = "Assets/Data/Camera/IslandCameraConfig.asset";
        private const float WorldYawDegrees = 180f;
        private static readonly Color DeepOcean = new Color(0.10f, 0.30f, 0.52f);

        [Serializable] private class SunInfo { public float[] dir; public float[] color; public float strength; }
        [Serializable] private class MeshInfo { public string key; public string group; public string file; public string[] materials; public int tris; }
        [Serializable] private class MatInfo { public string name; public string kind; public string texture; public float alpha; public float smoothness; public bool doubleSided; }
        [Serializable] private class ObjInfo { public string n; public string k; public string g; public float[] m; }
        [Serializable] private class Layout { public string source; public string exported; public SunInfo sun; public MeshInfo[] meshes; public MatInfo[] materials; public ObjInfo[] objects; }

        /// <summary>Menu entry: (re)build the island in the Island scene from the latest export.</summary>
        [MenuItem("Dino Park/Island/Import Island From Blender Export")]
        public static void ImportIsland()
        {
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            AssetDatabase.Refresh();

            string layoutPath = Path.Combine(Directory.GetCurrentDirectory(), LayoutFile);
            if (!File.Exists(layoutPath))
            {
                Debug.LogError($"[DinoPark] No island export at {LayoutFile}. Run export_island_unity.py first.");
                return;
            }
            var layout = JsonUtility.FromJson<Layout>(File.ReadAllText(layoutPath));

            Matrix4x4 conv = ReadAxisConversion();
            // FBX puts Blender north (+Y) on Unity -Z. Turn the island so north is +Z and the
            // default camera (yaw 0, looking +Z) sees it like the Blender reference camera.
            Matrix4x4 world = Matrix4x4.Rotate(Quaternion.Euler(0f, WorldYawDegrees, 0f));
            EnsureFolder(MaterialFolder);
            EnsureFolder(PrefabFolder);

            try
            {
                AssetDatabase.StartAssetEditing();
                foreach (MatInfo mi in layout.materials) CreateOrUpdateMaterial(mi);
            }
            finally
            {
                AssetDatabase.StopAssetEditing();
                AssetDatabase.SaveAssets();
            }

            var prefabs = new Dictionary<string, GameObject>();
            var matByName = layout.materials.ToDictionary(m => m.name, m => m);
            for (int i = 0; i < layout.meshes.Length; i++)
            {
                MeshInfo mesh = layout.meshes[i];
                EditorUtility.DisplayProgressBar("Island import", "Prefab " + mesh.key, (float)i / layout.meshes.Length);
                GameObject prefab = BuildPrefab(mesh, matByName);
                if (prefab != null) prefabs[mesh.key] = prefab;
            }

            Scene scene = EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            Transform env = FindOrCreateRoot(scene, "=== Environment ===");
            Transform old = env.Find(GroupName);
            if (old != null) Object.DestroyImmediate(old.gameObject);
            foreach (string placeholder in new[] { "Island_Placeholder", "Ocean_Placeholder" })
            {
                Transform t = env.Find(placeholder);
                if (t != null) t.gameObject.SetActive(false);
            }

            Transform group = new GameObject(GroupName).transform;
            group.SetParent(env, false);
            var sub = new Dictionary<string, Transform>();
            Transform Sub(string name)
            {
                if (sub.TryGetValue(name, out Transform t)) return t;
                t = new GameObject(name).transform;
                t.SetParent(group, false);
                sub[name] = t;
                return t;
            }

            int placed = 0, missing = 0;
            for (int i = 0; i < layout.objects.Length; i++)
            {
                ObjInfo o = layout.objects[i];
                if (i % 100 == 0) EditorUtility.DisplayProgressBar("Island import", "Placing " + o.n, (float)i / layout.objects.Length);
                if (!prefabs.TryGetValue(o.k, out GameObject prefab)) { missing++; continue; }

                Matrix4x4 b = Matrix4x4.identity;
                for (int r = 0; r < 4; r++)
                    for (int c = 0; c < 4; c++)
                        b[r, c] = o.m[r * 4 + c];
                Matrix4x4 u = world * conv * b * conv.inverse;

                var go = (GameObject)PrefabUtility.InstantiatePrefab(prefab, Sub(SubGroup(o.g)));
                go.name = o.n;
                go.transform.SetPositionAndRotation(u.GetColumn(3), u.rotation);
                go.transform.localScale = u.lossyScale;
                placed++;
            }
            EditorUtility.ClearProgressBar();

            FitBoundsAndSun(scene, group, layout, world * conv);
            IslandPolish.Apply(scene);
            EditorSceneManager.MarkSceneDirty(scene);
            EditorSceneManager.SaveScene(scene);
            Debug.Log($"[DinoPark] Island imported from {layout.source} (exported {layout.exported}): " +
                      $"{placed} objects, {prefabs.Count} prefabs, {layout.materials.Length} materials, {missing} missing.");
        }

        private static string SubGroup(string g)
        {
            switch (g)
            {
                case "Ground":
                case "Cliffs": return "Terrain";
                case "Ocean":
                case "Water": return "Water";
                default: return g;
            }
        }

        /// <summary>
        /// Blender -> Unity basis from the three exported axis probes (Blender points (10,0,0),
        /// (0,20,0), (0,0,30)). Covers the FBX axis swap, handedness and unit scale in one matrix.
        /// </summary>
        private static Matrix4x4 ReadAxisConversion()
        {
            Vector3 Probe(string axis, float len)
            {
                string path = $"{Root}/_Probe/AxisProbe_{axis}.fbx";
                Mesh mesh = AssetDatabase.LoadAllAssetsAtPath(path).OfType<Mesh>().FirstOrDefault();
                if (mesh == null) throw new InvalidOperationException("Missing axis probe " + path);
                return mesh.bounds.center / len;
            }

            var m = Matrix4x4.identity;
            m.SetColumn(0, Probe("X", 10f));
            m.SetColumn(1, Probe("Y", 20f));
            m.SetColumn(2, Probe("Z", 30f));
            m.SetColumn(3, new Vector4(0, 0, 0, 1));
            return m;
        }

        private static void CreateOrUpdateMaterial(MatInfo mi)
        {
            string path = $"{MaterialFolder}/M_{Sanitize(mi.name)}.mat";
            var mat = AssetDatabase.LoadAssetAtPath<Material>(path);
            Shader shader = Shader.Find(ShaderName);
            if (shader == null) throw new InvalidOperationException("Shader not found: " + ShaderName);
            if (mat == null)
            {
                mat = new Material(shader);
                AssetDatabase.CreateAsset(mat, path);
            }
            mat.shader = shader;
            mat.enableInstancing = true;

            Texture2D tex = string.IsNullOrEmpty(mi.texture) ? null : AssetDatabase.LoadAssetAtPath<Texture2D>($"{Root}/{mi.texture}");
            mat.SetTexture("_BaseMap", tex);
            mat.SetFloat("_Smoothness", mi.smoothness);
            mat.SetFloat("_Cull", mi.doubleSided ? (float)CullMode.Off : (float)CullMode.Back);
            Color tint = Color.white;

            bool transparent = mi.kind == "water" || mi.kind == "mist";
            bool cutout = mi.kind == "cutout";
            // Ground: the texture carries the colour. Leaf cards: vertex colour carries it, the atlas only cuts the shape.
            mat.SetFloat("_UseMapColor", mi.kind == "ground" ? 1f : 0f);

            mat.SetFloat("_AlphaClip", cutout ? 1f : 0f);
            mat.SetFloat("_Cutoff", 0.4f);
            mat.SetFloat("_Transparent", transparent ? 1f : 0f);
            SetKeyword(mat, "_ALPHATEST_ON", cutout);
            SetKeyword(mat, "_SURFACE_TYPE_TRANSPARENT", transparent);
            if (transparent)
            {
                tint.a = mi.alpha;
                mat.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
                mat.SetFloat("_DstBlend", (float)BlendMode.OneMinusSrcAlpha);
                mat.SetFloat("_ZWrite", 0f);
                mat.SetOverrideTag("RenderType", "Transparent");
                mat.renderQueue = (int)RenderQueue.Transparent;
            }
            else
            {
                mat.SetFloat("_SrcBlend", (float)BlendMode.One);
                mat.SetFloat("_DstBlend", (float)BlendMode.Zero);
                mat.SetFloat("_ZWrite", 1f);
                mat.SetOverrideTag("RenderType", cutout ? "TransparentCutout" : "Opaque");
                mat.renderQueue = cutout ? (int)RenderQueue.AlphaTest : (int)RenderQueue.Geometry;
            }
            mat.SetColor("_BaseColor", tint);
            EditorUtility.SetDirty(mat);
        }

        private static GameObject BuildPrefab(MeshInfo info, Dictionary<string, MatInfo> mats)
        {
            string fbx = $"{Root}/{info.file}";
            var model = AssetDatabase.LoadAssetAtPath<GameObject>(fbx);
            if (model == null)
            {
                Debug.LogWarning("[DinoPark] Missing model " + fbx);
                return null;
            }
            MeshFilter srcFilter = model.GetComponentInChildren<MeshFilter>();
            MeshRenderer srcRenderer = model.GetComponentInChildren<MeshRenderer>();
            if (srcFilter == null || srcRenderer == null) return null;

            // Map the imported (embedded) material slots to our materials by Blender name.
            Material[] embedded = srcRenderer.sharedMaterials;
            var slots = new Material[embedded.Length];
            for (int i = 0; i < embedded.Length; i++)
            {
                string name = embedded[i] != null ? embedded[i].name : null;
                if (name == null || !mats.ContainsKey(name))
                    name = info.materials != null && i < info.materials.Length ? info.materials[i] : null;
                slots[i] = name != null ? AssetDatabase.LoadAssetAtPath<Material>($"{MaterialFolder}/M_{Sanitize(name)}.mat") : null;
            }

            var go = new GameObject(info.key);
            go.AddComponent<MeshFilter>().sharedMesh = srcFilter.sharedMesh;
            var renderer = go.AddComponent<MeshRenderer>();
            renderer.sharedMaterials = slots;

            bool water = info.group == "Water" || info.group == "Ocean";
            bool smallPlant = info.group == "Plants" && (info.key.Contains("Grass") || info.key.Contains("Clover") || info.key.Contains("Duckweed"));
            renderer.shadowCastingMode = water || smallPlant ? ShadowCastingMode.Off : ShadowCastingMode.On;

            bool collider = info.group == "Ground" || info.group == "Cliffs" || info.group == "Props";
            if (collider) go.AddComponent<MeshCollider>().sharedMesh = srcFilter.sharedMesh;

            string path = $"{PrefabFolder}/{info.key}.prefab";
            GameObject prefab = PrefabUtility.SaveAsPrefabAsset(go, path);
            Object.DestroyImmediate(go);
            return prefab;
        }

        private static void FitBoundsAndSun(Scene scene, Transform group, Layout layout, Matrix4x4 conv)
        {
            Transform terrain = group.Find("Terrain");
            Renderer ground = terrain != null ? terrain.GetComponentsInChildren<Renderer>().FirstOrDefault(r => r.name.Contains("Ground")) : null;
            IslandBounds bounds = Object.FindAnyObjectByType<IslandBounds>();
            if (ground != null && bounds != null)
            {
                Bounds b = ground.bounds;
                var so = new SerializedObject(bounds);
                so.FindProperty("islandSize").vector2Value = new Vector2(b.size.x, b.size.z);
                so.ApplyModifiedPropertiesWithoutUndo();
                Vector3 p = bounds.transform.position;
                bounds.transform.position = new Vector3(b.center.x, p.y, b.center.z);
            }

            // Past the exported ocean the camera sees its clear colour: make it deep ocean.
            Camera cam = Object.FindAnyObjectByType<Camera>(FindObjectsInactive.Include);
            if (cam != null)
            {
                cam.clearFlags = CameraClearFlags.SolidColor;
                cam.backgroundColor = DeepOcean;
                EditorUtility.SetDirty(cam);
            }

            // The rig needs its config asset; re-link it if the scene reference went missing.
            IslandCameraRig rig = Object.FindAnyObjectByType<IslandCameraRig>(FindObjectsInactive.Include);
            if (rig == null)
            {
                Debug.LogWarning("[DinoPark] No IslandCameraRig in the scene; camera config not linked.");
            }
            else
            {
                var so = new SerializedObject(rig);
                SerializedProperty config = so.FindProperty("config");
                if (config != null && config.objectReferenceValue == null)
                {
                    var asset = AssetDatabase.LoadAssetAtPath<IslandCameraConfig>(CameraConfigPath);
                    if (asset == null)
                        Debug.LogError($"[DinoPark] Could not load {CameraConfigPath}; assign the camera config on CameraRig by hand.");
                    config.objectReferenceValue = asset;
                    so.ApplyModifiedPropertiesWithoutUndo();
                    EditorUtility.SetDirty(rig);
                    Debug.Log($"[DinoPark] Linked camera config: {(config.objectReferenceValue != null)}");
                }
            }

            if (layout.sun != null && layout.sun.dir != null && layout.sun.dir.Length == 3)
            {
                Light sun = Object.FindObjectsByType<Light>().FirstOrDefault(l => l.type == LightType.Directional);
                if (sun != null)
                {
                    Vector3 d = conv.MultiplyVector(new Vector3(layout.sun.dir[0], layout.sun.dir[1], layout.sun.dir[2])).normalized;
                    sun.transform.rotation = Quaternion.LookRotation(d);
                    if (layout.sun.color != null && layout.sun.color.Length >= 3)
                        sun.color = new Color(layout.sun.color[0], layout.sun.color[1], layout.sun.color[2]);
                }
            }
        }

        private static Transform FindOrCreateRoot(Scene scene, string name)
        {
            GameObject root = scene.GetRootGameObjects().FirstOrDefault(g => g.name == name);
            return root != null ? root.transform : new GameObject(name).transform;
        }

        private static void SetKeyword(Material m, string keyword, bool on)
        {
            if (on) m.EnableKeyword(keyword);
            else m.DisableKeyword(keyword);
        }

        private static string Sanitize(string s)
        {
            foreach (char c in Path.GetInvalidFileNameChars()) s = s.Replace(c, '_');
            return s.Replace('.', '_');
        }

        private static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = Path.GetDirectoryName(path)?.Replace('\\', '/');
            if (!string.IsNullOrEmpty(parent)) EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }
    }

    /// <summary>Import settings for everything under Assets/Models/Environment/Island.</summary>
    public sealed class IslandAssetPostprocessor : AssetPostprocessor
    {
        private void OnPreprocessModel()
        {
            if (!assetPath.StartsWith(IslandImporter.Root)) return;
            var mi = (ModelImporter)assetImporter;
            string file = Path.GetFileNameWithoutExtension(assetPath);
            mi.globalScale = 1f;
            mi.useFileScale = true;
            mi.importAnimation = false;
            mi.animationType = ModelImporterAnimationType.None;
            mi.importCameras = false;
            mi.importLights = false;
            mi.importBlendShapes = false;
            mi.importVisibility = false;
            mi.meshCompression = ModelImporterMeshCompression.Off;
            mi.importNormals = ModelImporterNormals.Import;
            mi.importTangents = ModelImporterTangents.None;
            mi.addCollider = false;
            mi.generateSecondaryUV = false;
            mi.materialImportMode = ModelImporterMaterialImportMode.ImportStandard;
            // Mesh colliders on scaled rocks and terrain need CPU-readable meshes in player builds.
            mi.isReadable = !file.StartsWith("PLN_") || file.StartsWith("PLN_Log");
        }

        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(IslandImporter.Root + "/Textures")) return;
            var ti = (TextureImporter)assetImporter;
            ti.sRGBTexture = true;
            ti.mipmapEnabled = true;
            bool ground = assetPath.Contains("Ground");
            if (ground)
            {
                ti.maxTextureSize = 4096;
                ti.wrapMode = TextureWrapMode.Clamp;
                ti.alphaSource = TextureImporterAlphaSource.None;
            }
            else
            {
                ti.alphaIsTransparency = true;
                ti.mipMapsPreserveCoverage = true;
                ti.alphaTestReferenceValue = 0.4f;
            }

            // Phones: ASTC 6x6 (about 3.6 bits per pixel), ground halved to 2048.
            TextureImporterPlatformSettings android = ti.GetPlatformTextureSettings("Android");
            android.overridden = true;
            android.maxTextureSize = ground ? 2048 : 512;
            android.format = TextureImporterFormat.ASTC_6x6;
            android.textureCompression = TextureImporterCompression.Compressed;
            ti.SetPlatformTextureSettings(android);
        }
    }
}
