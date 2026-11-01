# Autodesk FBX and Model Export Guidelines

This project utilizes `com.autodesk.fbx` (Autodesk FBX SDK C# Bindings) and `com.unity.formats.fbx` (Unity FBX Exporter) for model export, scene serialization, procedural mesh generation, and DCC tool roundtripping.

## Core Directives

1. **Unmanaged Memory & Pointer Lifecycle**:
   - `FbxManager` owns the native memory pool for all attached scenes, nodes, and meshes.
   - Always wrap `FbxManager.Create()` in a `using` statement or explicitly call `manager.Destroy()` in a `finally` block to prevent unmanaged C++ memory leaks.
   - Never retain C# references to `FbxNode`, `FbxMesh`, or `FbxScene` after their owning `FbxManager` is destroyed.

2. **Coordinate & Unit System Standards**:
   - Unity uses a **Left-Handed Y-up** coordinate system with metric meters.
   - When importing or exporting via raw `FbxSdk`, always convert scene axis conventions using `FbxAxisSystem.MayaYUp.ConvertScene(scene)` and verify unit scaling via `FbxSystemUnit.m.ConvertScene(scene)`.
   - When using `ModelExporter.ExportObject()`, axis conversion is handled automatically.

3. **Mesh Topology & Winding Order**:
   - Unity standard winding order is clockwise for front faces.
   - For custom procedural FBX mesh generation, define polygon vertices in counter-clockwise order if exporting to standard OpenGL/Maya conventions, or conform to Unity's clockwise winding before export.
   - Ensure mesh polygons are triangulated or convex quads; avoid n-gons with >4 vertices.

4. **DCC Tool Roundtripping**:
   - Use `ModelExporter.ExportObject` with `ExportOptions.Include.ModelAndAnimation` when exporting models intended for editing in Maya or 3ds Max.
   - Do not delete Unity components attached to imported FBX instances; the FBX Exporter preserves Unity component metadata across roundtrip re-imports.
