using System.Text;
using UnityEditor;
using UnityEngine;

namespace MiniGame.Editor
{
    [InitializeOnLoad]
    public static class InspectDinoAssets
    {
        static InspectDinoAssets()
        {
            EditorApplication.delayCall += Inspect;
        }

        [MenuItem("Tools/MiniGame/Inspect Dino Assets")]
        public static void Inspect()
        {
            string[] dinos = new string[]
            {
                "Apatosaurus.fbx", "Parasaurolophus.fbx", "Stegosaurus.fbx", "Trex.fbx", "Triceratops.fbx", "Velociraptor.fbx"
            };

            StringBuilder sb = new StringBuilder();
            sb.AppendLine("=== DINO ASSETS INSPECTION ===");

            foreach (var dinoName in dinos)
            {
                string path = $"Assets/Models/Dinosaurs/{dinoName}";
                var objs = AssetDatabase.LoadAllAssetsAtPath(path);
                sb.AppendLine($"\n--- {dinoName} ---");
                int animCount = 0;
                int meshCount = 0;
                int matCount = 0;

                foreach (var obj in objs)
                {
                    if (obj is AnimationClip clip)
                    {
                        animCount++;
                        sb.AppendLine($"  AnimationClip: '{clip.name}', length: {clip.length:F2}s, wrapMode: {clip.wrapMode}");
                    }
                    else if (obj is Mesh mesh)
                    {
                        meshCount++;
                        sb.AppendLine($"  Mesh: '{mesh.name}', submeshes: {mesh.subMeshCount}, vertices: {mesh.vertexCount}");
                    }
                    else if (obj is Material mat)
                    {
                        matCount++;
                        sb.AppendLine($"  Material: '{mat.name}', shader: '{mat.shader?.name}'");
                    }
                }
                sb.AppendLine($"  Summary: {animCount} clips, {meshCount} meshes, {matCount} materials");
            }

            string logPath = "Assets/Editor/dino_inspection.txt";
            System.IO.File.WriteAllText(logPath, sb.ToString());
            Debug.Log(sb.ToString());
        }
    }
}
