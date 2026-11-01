# ModelExporter & DCC Roundtripping Workflows

This reference covers the high-level `ModelExporter` API provided by `com.unity.formats.fbx`, roundtripping between Unity, Maya, and 3ds Max, and batch exporting.

---

## 1. High-Level `ModelExporter` Options

`ModelExporter` wraps the complex `FbxManager` and `FbxScene` conversions into single-method calls with configurable export settings:

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.Formats.Fbx.Exporter;
using UnityEngine;

public static class BatchMeshExporter
{
    [MenuItem("Tools/FBX/Export Selection with Custom Settings")]
    public static void ExportSelection()
    {
        var selected = Selection.activeGameObject;
        if (selected == null)
        {
            EditorUtility.DisplayDialog("FBX Exporter", "Please select a GameObject in hierarchy.", "OK");
            return;
        }

        string path = EditorUtility.SaveFilePanel("Export FBX", "Assets", selected.name, "fbx");
        if (string.IsNullOrEmpty(path)) return;

        // Configure Export Options
        var exportOptions = new ExportOptions
        {
            exportFormat = ExportOptions.ExportFormat.Binary,
            include = ExportOptions.Include.ModelAndAnimation,
            lod = ExportOptions.Lod.All,
            objectPosition = ExportOptions.ObjectPosition.LocalCentered,
            animatedSkinnedMesh = true,
            bakeAnimation = true
        };

        ModelExporter.ExportObject(path, selected, exportOptions);
        AssetDatabase.Refresh();
        Debug.Log($"[FBX Exporter] Exported {selected.name} to {path}");
    }
}
#endif
```

---

## 2. Maya & 3ds Max Roundtripping

The FBX Exporter integration enables non-destructive round-tripping:
1. **Send to Maya**:
   - Right click a GameObject or Prefab $\rightarrow$ `Export To FBX...`
   - Check **Export Unmatched Material Slots** and **Preserve FBX Material Definitions**.
2. **Edit in Maya / Max**:
   - Maya/Max opens the temporary or target FBX.
   - Adjust topology, UV seams, bone weights, or blend shapes.
   - Save directly back to the FBX file.
3. **Unity Auto-Sync**:
   - Unity detects the modified FBX, re-imports geometry, and preserves all Unity-specific components (`MonoBehaviour`, `Rigidbody`, `AudioSource`) attached to the hierarchy.

---

## 3. Animation Clip Exporting

You can export standalone `AnimationClip` assets directly from Timeline or Animator into FBX format:

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEditor.Formats.Fbx.Exporter;
using UnityEngine;

public static class AnimationExportHelper
{
    public static void ExportClipWithRig(GameObject rig, AnimationClip clip, string outputPath)
    {
        // Sample animation clip onto target rig hierarchy and bake keyframes
        ModelExporter.ExportObject(outputPath, rig, new ExportOptions
        {
            include = ExportOptions.Include.AnimationOnly,
            bakeAnimation = true
        });

        Debug.Log($"Exported baked animation clip {clip.name} to {outputPath}");
    }
}
#endif
```
