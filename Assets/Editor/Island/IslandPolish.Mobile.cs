using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace DinoPark.EditorTools
{
    public static partial class IslandPolish
    {
        private const string LodFolder = "Assets/Models/Environment/Island/Lod";

        /// <summary>Prefab names that are terrain / water / generated pieces: never LOD'd or culled.</summary>
        private static bool SkipLod(string name) =>
            name.StartsWith("ISL") || name.StartsWith("TRN5_Cliff") || name.StartsWith("TRN4_") || name.StartsWith("TRN2_Waterfall") ||
            name.StartsWith("TRN2_Bridge") || name.StartsWith("TRN2_Pier");

        /// <summary>
        /// Mobile pass, run last: every plant and rock prefab gets automatic Mesh LODs (Unity picks the level
        /// from screen size), small plants and rocks are culled at distance through a LODGroup and stop casting
        /// shadows, island textures get Android compression, and the mobile URP asset drops HDR.
        /// Colliders keep the full-detail mesh.
        /// </summary>
        private static void OptimizeForMobile(Ctx ctx)
        {
            PlazaTextureReimport();
            PreferMobileRenderSettings();

            PlazaEnsureFolder(LodFolder);
            long fullTris = 0, lod1Tris = 0;
            int meshes = 0, culled = 0, noShadow = 0, lodLevels = 0;
            var done = new HashSet<string>();
            foreach (string guid in AssetDatabase.FindAssets("t:Prefab", new[] { PrefabFolder }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                string key = System.IO.Path.GetFileNameWithoutExtension(path);
                if (SkipLod(key) || !done.Add(key)) continue;

                Mesh original = AssetDatabase.LoadAllAssetsAtPath($"{IslandImporter.Root}/Meshes/{key}.fbx").OfType<Mesh>().FirstOrDefault();
                if (original == null) continue;

                // Simplify with Unity's Mesh LOD generator, then copy two of its levels out into plain meshes:
                // runtime Mesh LOD selection does not draw these multi-material meshes outside a LODGroup.
                Mesh work = Object.Instantiate(original);
                MeshLodUtility.GenerateMeshLods(work, 0, -1);
                AssetDatabase.DeleteAsset($"{LodFolder}/{key}.asset");     // old runtime-LOD asset
                // Palms, tree ferns and cycads are a few big frond cards: simplifying drops whole fronds,
                // so the trees go bald when zoomed out. They keep the full mesh at every distance.
                bool keepFronds = Has(key, "Palm", "FernTree", "Cycad");
                Mesh lod1 = !keepFronds && work.lodCount > 1 ? LevelMesh(work, 1, key + "_LOD1") : null;
                Mesh lod2 = !keepFronds && work.lodCount > 2 ? LevelMesh(work, Mathf.Min(3, work.lodCount - 1), key + "_LOD2") : null;
                if (keepFronds)
                {
                    AssetDatabase.DeleteAsset($"{LodFolder}/{key}_LOD1.asset");
                    AssetDatabase.DeleteAsset($"{LodFolder}/{key}_LOD2.asset");
                }
                Object.DestroyImmediate(work);

                GameObject root = PrefabUtility.LoadPrefabContents(path);
                var mf = root.GetComponent<MeshFilter>();
                var mr = root.GetComponent<MeshRenderer>();
                if (mf != null && mr != null)
                {
                    mf.sharedMesh = original;
                    foreach (LODGroup old in root.GetComponents<LODGroup>()) Object.DestroyImmediate(old);
                    foreach (Transform child in root.transform.Cast<Transform>().ToList())
                        if (child.name.StartsWith("LOD")) Object.DestroyImmediate(child.gameObject);

                    // Island instances are scaled up (trees 2-5x); use a typical 2x to judge size.
                    float h = original.bounds.size.y * 2f;
                    bool tiny = h < 1.6f, small = h < 3.5f;
                    if (small) { mr.shadowCastingMode = ShadowCastingMode.Off; noShadow++; }
                    float cull = tiny ? 0.014f : small ? 0.007f : 0f;

                    var lods = new List<LOD>();
                    Renderer r1 = lod1 != null ? LevelChild(root.transform, "LOD1", lod1, mr, mr.shadowCastingMode) : null;
                    Renderer r2 = lod2 != null ? LevelChild(root.transform, "LOD2", lod2, mr, ShadowCastingMode.Off) : null;
                    if (r1 != null) lods.Add(new LOD(r2 != null ? 0.30f : Mathf.Max(cull, 0.12f), new Renderer[] { mr }));
                    if (r1 != null && r2 != null) lods.Add(new LOD(0.10f, new[] { r1 }));
                    if (r2 != null) lods.Add(new LOD(cull, new[] { r2 }));
                    else if (r1 != null) lods.Add(new LOD(cull, new[] { r1 }));
                    else if (cull > 0f) lods.Add(new LOD(cull, new Renderer[] { mr }));
                    if (lods.Count > 0)
                    {
                        var group = root.AddComponent<LODGroup>();
                        group.SetLODs(lods.ToArray());
                        group.fadeMode = LODFadeMode.None;
                        group.RecalculateBounds();
                    }
                    if (cull > 0f) culled++;
                    PrefabUtility.SaveAsPrefabAsset(root, path);
                }
                PrefabUtility.UnloadPrefabContents(root);

                meshes++;
                lodLevels += 1 + (lod1 != null ? 1 : 0) + (lod2 != null ? 1 : 0);
                fullTris += original.triangles.Length / 3;
                lod1Tris += lod1 != null ? lod1.triangles.Length / 3 : original.triangles.Length / 3;
            }
            AssetDatabase.SaveAssets();
            ctx.Log.Add($"Mobile: {meshes} prefab meshes got Mesh LODs (avg {(meshes > 0 ? (float)lodLevels / meshes : 0):F1} levels, LOD1 ~{(fullTris > 0 ? 100f * lod1Tris / fullTris : 0):F0}% of LOD0 triangles), {culled} small ones culled at distance, {noShadow} stop casting shadows");
        }

        private static void PlazaEnsureFolder(string path) => ProceduralTextures.EnsureFolder(path);

        /// <summary>Plain mesh holding one generated LOD level (shared vertex data, that level's indices).</summary>
        private static Mesh LevelMesh(Mesh src, int level, string name)
        {
            var m = new Mesh { name = name, indexFormat = src.indexFormat };
            m.vertices = src.vertices;
            m.normals = src.normals;
            if (src.colors32.Length > 0) m.colors32 = src.colors32;
            var uv = new List<Vector2>();
            src.GetUVs(0, uv);
            if (uv.Count > 0) m.SetUVs(0, uv);
            m.subMeshCount = src.subMeshCount;
            for (int s = 0; s < src.subMeshCount; s++)
                m.SetIndices(src.GetIndices(s, level, true), MeshTopology.Triangles, s);
            m.RecalculateBounds();
            string path = $"{LodFolder}/{name}.asset";
            AssetDatabase.DeleteAsset(path);
            AssetDatabase.CreateAsset(m, path);
            return m;
        }

        private static Renderer LevelChild(Transform root, string name, Mesh mesh, MeshRenderer like, ShadowCastingMode shadows)
        {
            var go = new GameObject(name);
            go.transform.SetParent(root, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var r = go.AddComponent<MeshRenderer>();
            r.sharedMaterials = like.sharedMaterials;
            r.shadowCastingMode = shadows;
            return r;
        }

        /// <summary>Re-import island textures so the Android compression override in the importer is applied.</summary>
        private static void PlazaTextureReimport()
        {
            foreach (string guid in AssetDatabase.FindAssets("t:Texture2D", new[] { IslandImporter.Root + "/Textures" }))
                AssetDatabase.ImportAsset(AssetDatabase.GUIDToAssetPath(guid), ImportAssetOptions.ForceUpdate);
        }

        private static void PreferMobileRenderSettings()
        {
            foreach (string guid in AssetDatabase.FindAssets("t:UniversalRenderPipelineAsset", new[] { "Assets/Settings" }))
            {
                string path = AssetDatabase.GUIDToAssetPath(guid);
                if (!path.Contains("Mobile")) continue;
                var urp = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(path);
                if (urp == null) continue;
                urp.supportsHDR = false;          // saves a full-resolution 16-bit buffer
                urp.msaaSampleCount = 1;
                EditorUtility.SetDirty(urp);
            }
        }
    }
}
