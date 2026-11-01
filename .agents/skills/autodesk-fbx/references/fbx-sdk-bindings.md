# Autodesk FBX SDK C# Bindings: Memory Architecture & Core Classes

This reference details the low-level C# wrapper architecture of `com.autodesk.fbx` (FbxSharp) and native pointer management.

---

## 1. Unmanaged Memory & Lifecycle Management

`com.autodesk.fbx` wraps the native C++ Autodesk FBX SDK via SWIG bindings.

### The Lifetime Rule
- Every object instantiated in the FBX SDK (`FbxScene`, `FbxNode`, `FbxMesh`, `FbxIOSettings`, `FbxExporter`) is owned by an **`FbxManager`**.
- When `FbxManager.Destroy()` is invoked, all scenes, nodes, and mesh attributes allocated under that manager are freed in unmanaged native memory.
- **NEVER** keep C# references to FBX objects after their parent `FbxManager` has been destroyed, or unmanaged access violation exceptions (`NullReferenceException` / AccessViolation) will occur.

```csharp
// Recommended Pattern: using statement for FbxManager
using (var manager = FbxManager.Create())
{
    var scene = FbxScene.Create(manager, "Scene");
    var node = FbxNode.Create(manager, "MyNode");
    scene.GetRootNode().AddChild(node);

    // Perform work...
} // Manager and all attached unmanaged memory released safely
```

---

## 2. Coordinate System & Unit System Conversion

Unity uses a **Left-Handed Y-up** coordinate system with meters as units. FBX files can be authored in various coordinate and unit conventions:
- **Maya**: Right-Handed Y-up, centimeters.
- **3ds Max**: Right-Handed Z-up, inches or centimeters.
- **Blender**: Right-Handed Z-up, meters.

```csharp
using Autodesk.Fbx;

public static class AxisConversionHelper
{
    public static void ConformToUnityCoordinateSystem(FbxScene scene)
    {
        // Unity is Left-Handed, Y-Up
        // Maya is Right-Handed, Y-Up
        // Max is Right-Handed, Z-Up

        // Convert scene axis system to Maya/Unity compatible Y-up
        FbxAxisSystem.MayaYUp.ConvertScene(scene);

        // Convert units to Meters
        if (scene.GetGlobalSettings().GetSystemUnit() != FbxSystemUnit.m)
        {
            FbxSystemUnit.m.ConvertScene(scene);
        }
    }
}
```

---

## 3. Authoring Geometry, Normals, and UVs

FBX represents mesh topology through:
- **Control Points**: Unique 3D vertex positions (`FbxVector4`).
- **Polygon Vertices**: Polygon face indices into control points (`AddPolygon(index)`).
- **Layer Elements**: Normals, tangents, UV coordinates, and vertex colors mapped via:
  - `eByControlPoint`: One normal/UV per control point (shared).
  - `eByPolygonVertex`: One normal/UV per face-vertex (supports hard edges / UV seams).

```csharp
using Autodesk.Fbx;

public static void AddNormalsAndUVs(FbxMesh mesh, int vertexCount)
{
    // 1. Add Normal Layer
    var elementNormal = mesh.CreateElementNormal();
    elementNormal.SetMappingMode(FbxLayerElement.EMappingMode.eByPolygonVertex);
    elementNormal.SetReferenceMode(FbxLayerElement.EReferenceMode.eDirect);

    // 2. Add UV Layer
    var elementUV = mesh.CreateElementUV("DiffuseUV");
    elementUV.SetMappingMode(FbxLayerElement.EMappingMode.eByPolygonVertex);
    elementUV.SetReferenceMode(FbxLayerElement.EReferenceMode.eIndexToDirect);
}
```
