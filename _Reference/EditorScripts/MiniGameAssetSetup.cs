using System.IO;
using UnityEditor;
using UnityEngine;

namespace MiniGame.Editor
{
    public static class MiniGameAssetSetup
    {
        private const string DinoPath = "Assets/Models/Dinosaurs";
        private const string CharPath = "Assets/Models/Characters";
        private const string EnvPath = "Assets/Models/Environment";
        private const string EnvTexturesPath = "Assets/Models/Environment/Textures";
        private const string EnvMaterialsPath = "Assets/Models/Environment/Materials";

        [MenuItem("Tools/MiniGame/1. Refresh Asset Database")]
        public static void RefreshDatabase()
        {
            AssetDatabase.Refresh(ImportAssetOptions.ForceUpdate);
            Debug.Log("[MiniGame] AssetDatabase refreshed successfully.");
        }

        [MenuItem("Tools/MiniGame/2. Setup Environment Textures & URP Materials")]
        public static void SetupEnvironmentMaterials()
        {
            Shader urpLitShader = Shader.Find("Universal Render Pipeline/Lit");
            if (urpLitShader == null)
            {
                Debug.LogError("[MiniGame] 'Universal Render Pipeline/Lit' shader not found.");
                return;
            }

            if (!AssetDatabase.IsValidFolder(EnvMaterialsPath))
            {
                AssetDatabase.CreateFolder(EnvPath, "Materials");
            }

            // 1. Mark normal maps as NormalMap type
            string[] normalMapFiles = new string[]
            {
                $"{EnvTexturesPath}/Bark_DeadTree_Normal.png",
                $"{EnvTexturesPath}/Bark_NormalTree_Normal.png",
                $"{EnvTexturesPath}/Bark_TwistedTree_Normal.png"
            };

            foreach (string normalPath in normalMapFiles)
            {
                var importer = AssetImporter.GetAtPath(normalPath) as TextureImporter;
                if (importer != null && importer.textureType != TextureImporterType.NormalMap)
                {
                    importer.textureType = TextureImporterType.NormalMap;
                    importer.SaveAndReimport();
                }
            }

            // 2. Setup bark & opaque materials
            CreateOrUpdateMaterial("M_Bark_NormalTree", $"{EnvTexturesPath}/Bark_NormalTree.png", $"{EnvTexturesPath}/Bark_NormalTree_Normal.png", urpLitShader);
            CreateOrUpdateMaterial("M_Bark_DeadTree", $"{EnvTexturesPath}/Bark_DeadTree.png", $"{EnvTexturesPath}/Bark_DeadTree_Normal.png", urpLitShader);
            CreateOrUpdateMaterial("M_Bark_TwistedTree", $"{EnvTexturesPath}/Bark_TwistedTree.png", $"{EnvTexturesPath}/Bark_TwistedTree_Normal.png", urpLitShader);
            CreateOrUpdateMaterial("M_Rocks", $"{EnvTexturesPath}/Rocks_Diffuse.png", null, urpLitShader);
            CreateOrUpdateMaterial("M_Rocks_Desert", $"{EnvTexturesPath}/Rocks_Desert_Diffuse.png", null, urpLitShader);
            CreateOrUpdateMaterial("M_PathRocks", $"{EnvTexturesPath}/PathRocks_Diffuse.png", null, urpLitShader);
            CreateOrUpdateMaterial("M_Mushrooms", $"{EnvTexturesPath}/Mushrooms.png", null, urpLitShader);

            // 3. Setup leaf & flora cutout materials with Alpha Clipping and Double-Sided rendering
            CreateOrUpdateMaterial("M_Leaves_NormalTree", $"{EnvTexturesPath}/Leaves_NormalTree_C.png", null, urpLitShader, cutoff: 0.35f);
            CreateOrUpdateMaterial("M_Leaves_TwistedTree", $"{EnvTexturesPath}/Leaves_TwistedTree_C.png", null, urpLitShader, cutoff: 0.35f);
            CreateOrUpdateMaterial("M_Pine", $"{EnvTexturesPath}/Leaf_Pine_C.png", null, urpLitShader, cutoff: 0.35f);
            CreateOrUpdateMaterial("M_Leaves", $"{EnvTexturesPath}/Leaves.png", null, urpLitShader, cutoff: 0.35f);
            CreateOrUpdateMaterial("M_Flowers", $"{EnvTexturesPath}/Flowers.png", null, urpLitShader, cutoff: 0.35f);
            CreateOrUpdateMaterial("M_Grass", $"{EnvTexturesPath}/Grass.png", null, urpLitShader, cutoff: 0.35f);

            AssetDatabase.SaveAssets();
            Debug.Log("[MiniGame] Environment URP Materials successfully created with alpha clipping!");
        }

        private static void CreateOrUpdateMaterial(string matName, string diffusePath, string normalPath, Shader shader, float cutoff = 0f)
        {
            string matAssetPath = $"{EnvMaterialsPath}/{matName}.mat";
            Material mat = AssetDatabase.LoadAssetAtPath<Material>(matAssetPath);
            if (mat == null)
            {
                mat = new Material(shader);
                AssetDatabase.CreateAsset(mat, matAssetPath);
            }
            else
            {
                mat.shader = shader;
            }

            Texture2D diffuse = AssetDatabase.LoadAssetAtPath<Texture2D>(diffusePath);
            if (diffuse != null)
            {
                mat.SetTexture("_BaseMap", diffuse);
                mat.SetColor("_BaseColor", Color.white);
            }

            if (!string.IsNullOrEmpty(normalPath))
            {
                Texture2D normal = AssetDatabase.LoadAssetAtPath<Texture2D>(normalPath);
                if (normal != null)
                {
                    mat.SetTexture("_BumpMap", normal);
                    mat.EnableKeyword("_NORMALMAP");
                }
            }

            if (cutoff > 0f)
            {
                mat.SetFloat("_AlphaClip", 1f);
                mat.SetFloat("_Cutoff", cutoff);
                mat.EnableKeyword("_ALPHATEST_ON");
                mat.SetInt("_Cull", (int)UnityEngine.Rendering.CullMode.Off); // double sided for foliage
                mat.SetOverrideTag("RenderType", "TransparentCutout");
                mat.renderQueue = (int)UnityEngine.Rendering.RenderQueue.AlphaTest;
            }
            else
            {
                mat.SetFloat("_AlphaClip", 0f);
                mat.DisableKeyword("_ALPHATEST_ON");
                mat.SetInt("_Cull", (int)UnityEngine.Rendering.CullMode.Back);
                mat.SetOverrideTag("RenderType", "Opaque");
                mat.renderQueue = (int)UnityEngine.Rendering.RenderQueue.Geometry;
            }

            mat.SetFloat("_Smoothness", 0.05f);
            mat.SetFloat("_Metallic", 0.0f);

            EditorUtility.SetDirty(mat);
        }
    }
}
