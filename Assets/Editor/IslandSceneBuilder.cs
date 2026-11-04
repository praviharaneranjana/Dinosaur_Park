using System.Collections.Generic;
using System.IO;
using DinoPark.CameraControl;
using Lean.Touch;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.InputSystem.UI;
using UnityEngine.SceneManagement;

namespace DinoPark.EditorTools
{
    /// <summary>
    /// One-click builder for the starter Island scene: placeholder island and ocean, light, the
    /// locked touch camera and the touch/UI plumbing. Run from the menu, or in batch mode with
    /// -executeMethod DinoPark.EditorTools.IslandSceneBuilder.BuildIslandScene.
    /// Everything here is a placeholder to be replaced by the real Blender island.
    /// </summary>
    public static class IslandSceneBuilder
    {
        private const string ScenePath = "Assets/Scenes/Island.unity";
        private const string ConfigPath = "Assets/Data/Camera/IslandCameraConfig.asset";
        private const string MaterialFolder = "Assets/Materials/Placeholder";

        // Palette from AGENTS.md
        private static readonly Color IslandGreen = new Color32(0x5E, 0x9B, 0x4A, 0xFF);
        private static readonly Color OceanTeal = new Color32(0x8F, 0xCB, 0xCB, 0xFF);
        private static readonly Color SunAmber = new Color32(0xFF, 0xF1, 0xD6, 0xFF);

        /// <summary>Creates (or recreates) Assets/Scenes/Island.unity and adds it to Build Settings.</summary>
        [MenuItem("Dino Park/Setup/Build Island Scene")]
        public static void BuildIslandScene()
        {
            EnsureFolder("Assets/Scenes");
            EnsureFolder("Assets/Data");
            EnsureFolder("Assets/Data/Camera");
            EnsureFolder("Assets/Materials");
            EnsureFolder(MaterialFolder);

            IslandCameraConfig config = LoadOrCreateConfig();
            Material islandMaterial = LoadOrCreateMaterial("M_Placeholder_Island", IslandGreen);
            Material oceanMaterial = LoadOrCreateMaterial("M_Placeholder_Ocean", OceanTeal);

            Scene scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            Transform environment = Group("=== Environment ===");
            Transform lighting = Group("=== Lighting ===");
            Transform cameraGroup = Group("=== Camera ===");
            Transform systems = Group("=== Systems ===");

            // --- Island bounds + placeholder meshes (island size comes from IslandBounds) ---
            var boundsObject = new GameObject("IslandBounds");
            boundsObject.transform.SetParent(environment, false);
            IslandBounds bounds = boundsObject.AddComponent<IslandBounds>();
            Vector2 size = bounds.IslandSize;

            GameObject island = GameObject.CreatePrimitive(PrimitiveType.Cube);
            island.name = "Island_Placeholder";
            island.transform.SetParent(environment, false);
            island.transform.localScale = new Vector3(size.x, 2f, size.y);
            island.transform.position = new Vector3(0f, -1f, 0f); // top face at y = 0
            island.GetComponent<Renderer>().sharedMaterial = islandMaterial;

            GameObject ocean = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ocean.name = "Ocean_Placeholder";
            ocean.transform.SetParent(environment, false);
            ocean.transform.position = new Vector3(0f, -0.4f, 0f);
            ocean.transform.localScale = new Vector3(120f, 1f, 120f); // 1200 m square
            Object.DestroyImmediate(ocean.GetComponent<Collider>());
            ocean.GetComponent<Renderer>().sharedMaterial = oceanMaterial;

            // --- Light ---
            var sun = new GameObject("Sun");
            sun.transform.SetParent(lighting, false);
            sun.transform.rotation = Quaternion.Euler(50f, -30f, 0f);
            Light light = sun.AddComponent<Light>();
            light.type = LightType.Directional;
            light.color = SunAmber;
            light.intensity = 1.1f;
            light.shadows = LightShadows.Soft;
            RenderSettings.ambientMode = UnityEngine.Rendering.AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.62f, 0.66f, 0.66f);

            // --- Camera rig ---
            var rigObject = new GameObject("CameraRig");
            rigObject.transform.SetParent(cameraGroup, false);

            var cameraObject = new GameObject("Main Camera") { tag = "MainCamera" };
            cameraObject.transform.SetParent(rigObject.transform, false);
            Camera camera = cameraObject.AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = OceanTeal;
            camera.nearClipPlane = 0.5f;
            camera.farClipPlane = 800f;
            cameraObject.AddComponent<AudioListener>();

            IslandCameraRig rig = rigObject.AddComponent<IslandCameraRig>();
            var rigSerialized = new SerializedObject(rig);
            rigSerialized.FindProperty("config").objectReferenceValue = config;
            rigSerialized.FindProperty("bounds").objectReferenceValue = bounds;
            rigSerialized.FindProperty("targetCamera").objectReferenceValue = camera;
            rigSerialized.ApplyModifiedPropertiesWithoutUndo();

            // --- Touch + UI plumbing (Lean Touch needs an EventSystem to test "finger over UI") ---
            var leanTouch = new GameObject("LeanTouch");
            leanTouch.transform.SetParent(systems, false);
            leanTouch.AddComponent<LeanTouch>();

            var eventSystem = new GameObject("EventSystem");
            eventSystem.transform.SetParent(systems, false);
            eventSystem.AddComponent<EventSystem>();
            eventSystem.AddComponent<InputSystemUIInputModule>();

            EditorSceneManager.SaveScene(scene, ScenePath);
            AddSceneToBuildSettings(ScenePath);
            AssetDatabase.SaveAssets();
            AssetDatabase.Refresh();

            Debug.Log($"[DinoPark] Island scene built at {ScenePath}");
        }

        private static Transform Group(string name)
        {
            return new GameObject(name).transform;
        }

        private static IslandCameraConfig LoadOrCreateConfig()
        {
            var config = AssetDatabase.LoadAssetAtPath<IslandCameraConfig>(ConfigPath);
            if (config != null) return config;

            config = ScriptableObject.CreateInstance<IslandCameraConfig>();
            AssetDatabase.CreateAsset(config, ConfigPath);
            return config;
        }

        private static Material LoadOrCreateMaterial(string name, Color color)
        {
            string path = $"{MaterialFolder}/{name}.mat";
            var existing = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (existing != null) return existing;

            Shader shader = Shader.Find("Universal Render Pipeline/Lit");
            var material = new Material(shader) { name = name };
            material.SetColor("_BaseColor", color);
            material.SetFloat("_Smoothness", 0.1f);
            AssetDatabase.CreateAsset(material, path);
            return material;
        }

        private static void AddSceneToBuildSettings(string path)
        {
            var scenes = new List<EditorBuildSettingsScene>(EditorBuildSettings.scenes);
            foreach (EditorBuildSettingsScene s in scenes)
            {
                if (s.path == path) return;
            }

            scenes.Add(new EditorBuildSettingsScene(path, true));
            EditorBuildSettings.scenes = scenes.ToArray();
        }

        private static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;

            string parent = Path.GetDirectoryName(path)?.Replace('\\', '/');
            string leaf = Path.GetFileName(path);
            AssetDatabase.CreateFolder(parent, leaf);
        }
    }
}
