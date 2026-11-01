---
trigger: "When working with post-processing, camera effects, volume profiles, tone mapping, visual effects, shaders, or rendering features in Unity."
---

# Unity Post-Processing & Visual Fidelity Rules

## 1. Pipeline & Architectural Integrity
- **Volume Framework Exclusivity**: In URP (and HDRP), post-processing is driven exclusively by the Core Volume Framework (`UnityEngine.Rendering.Volume`, `VolumeProfile`, `VolumeComponent`).
- **Strictly Prohibit Legacy PPv2**: Never install or import the legacy `com.unity.postprocessing` package in URP or Unity 6 projects. It creates severe shader conflicts, namespace collisions, and breaks Render Graph execution.
- **Migration Policy**: If legacy PPv2 (`PostProcessVolume`, `PostProcessLayer`, `PostProcessProfile`) is detected, convert profiles to URP `VolumeProfile` assets using the Render Pipeline Converter, enable `renderPostProcessing` on `UniversalAdditionalCameraData`, and remove the legacy package.

## 2. Volume Scripting & Modification
- **Override State Requirement**: Always set `parameter.overrideState = true` when assigning values to any `VolumeParameter` via script. Setting `parameter.value` without enabling `overrideState` causes the Volume system to silently ignore the change.
- **Runtime vs Asset Safety**:
  - Use `volume.profile` when modifying effects at runtime (automatically clones the profile to prevent mutating project assets on disk).
  - Use `volume.sharedProfile` only when building persistent Editor tools or asset baking scripts (call `EditorUtility.SetDirty(profile)` and `AssetDatabase.SaveAssets()`).
- **Layer Mask Validation**: Always verify that the Volume's `GameObject.layer` matches the `UniversalAdditionalCameraData.volumeLayerMask` of the rendering camera (defaults to Layer 0 "Default").

## 3. Color Management & HDR
- **HDR Prerequisite**: Ensure `supportsHDR = true` on the active `UniversalRenderPipelineAsset`. Bloom and Tonemapping require HDR to produce mathematically correct luminance distributions.
- **Tonemapper Selection**:
  - **ACES**: Standard for realistic, cinematic, and PBR projects. Preserves highlight detail with a filmic S-curve roll-off.
  - **Neutral**: Standard for stylized, anime, or UI-heavy rendering where strict color hue preservation is required without filmic color shifting.
  - **Avoid Un-Tonemapped HDR**: Never leave an HDR scene without a `Tonemapping` override, as high-intensity specular highlights will clamp harshly to pure white.

## 4. Screen-Space Features & Renderer Architecture
- **Ambient Occlusion (SSAO)**: SSAO in URP is NOT an override in `VolumeProfile`. It must be configured as a `ScreenSpaceAmbientOcclusion` `ScriptableRendererFeature` on the active `UniversalRendererData` asset.
- **Unity 6 Render Graph Custom Passes**:
  - Custom fullscreen post-processing passes must implement the Render Graph API (`RecordRenderGraph(RenderGraph, ContextContainer)`).
  - Use `Blitter.BlitTexture()` and `builder.UseTexture()` / `builder.SetRenderAttachment()`.
  - Never use legacy `OnRenderImage`, `Graphics.Blit`, or obsolete `CommandBuffer.BlitFullscreenTriangle`.

## 5. Performance Budgets & Tiered Configurations
- **Mobile / Low-End**:
  - Prefer FXAA (`AntialiasingMode.FastApproximateAntialiasing`).
  - Bloom: Use `threshold >= 1.0`, `downscale = BloomDownscaleMode.Half`, and max iterations $\le 4$.
  - Omit Depth of Field (Bokeh), Motion Blur, and high-intensity Film Grain.
- **PC / Console / High-End**:
  - Prefer TAA (`AntialiasingMode.TemporalAntiAliasing`) or SMAA (`AntialiasingMode.SubpixelMorphologicalAntiAliasing`).
  - Bloom: Enable `highQualityFiltering = true` (bicubic upsampling).
  - Depth of Field: Use `Bokeh` mode with physical aperture and blade curvature settings.
