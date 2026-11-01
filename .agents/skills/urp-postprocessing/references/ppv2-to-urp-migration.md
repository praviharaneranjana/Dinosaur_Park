# Post-Processing Stack v2 (PPv2) to URP Migration Reference

This document provides a complete mapping, architectural breakdown, and migration guide from the legacy **Post-Processing Stack v2 (`com.unity.postprocessing`)** used in the Built-in Render Pipeline (BiRP) to the **Universal Render Pipeline (URP 14+ / Unity 6 URP 17+)** Volume Framework and Render Graph architecture.

---

## 1. Architectural Evolution: PPv2 vs URP

| Architecture Layer | Legacy PPv2 (`com.unity.postprocessing`) | Modern URP (Unity 2022+ / Unity 6) |
|---|---|---|
| **Package Dependency** | `com.unity.postprocessing` (3.x) | Built directly into `com.unity.render-pipelines.universal` & `com.unity.render-pipelines.core` |
| **Pipeline Compatibility** | Built-in Render Pipeline (BiRP) only | Universal Render Pipeline (URP) & HDRP |
| **Profile Asset** | `PostProcessProfile` (`.asset`) | `VolumeProfile` (`.asset`) |
| **Scene Volume** | `PostProcessVolume` (Global or Trigger Collider) | `Volume` (from `UnityEngine.Rendering`) |
| **Effect Base Class** | `PostProcessEffectSettings` | `VolumeComponent` (from `UnityEngine.Rendering`) |
| **Effect Parameter** | `FloatParameter`, `ColorParameter`, etc. (from `UnityEngine.Rendering.PostProcessing`) | `ClampedFloatParameter`, `ColorParameter`, etc. (from `UnityEngine.Rendering`) |
| **Camera Controller** | `PostProcessLayer` component on Camera | `UniversalAdditionalCameraData` on Camera (`renderPostProcessing = true`) |
| **Antialiasing** | Configured on `PostProcessLayer` (FXAA, SMAA, TAA) | Configured on `UniversalAdditionalCameraData.antialiasing` (`AntialiasingMode`) |
| **Custom Effect Rendering** | Subclass `PostProcessEffectRenderer<T>` | `ScriptableRendererFeature` + `ScriptableRenderPass` (Render Graph in Unity 6) or `FullScreenPassRendererFeature` |
| **Screen Blitting** | `context.command.BlitFullscreenTriangle()` | `Blitter.BlitCameraTexture()` / `Blitter.BlitTexture()` with `RTHandle` |

> [!WARNING]
> **Never install `com.unity.postprocessing` into a URP project!**
> URP has its own native post-processing pipeline. Adding `com.unity.postprocessing` into a URP project causes namespace collisions, shader duplicate definitions, and breaks the Render Graph execution pipeline.

---

## 2. Complete Effect Mapping Table

| PPv2 Effect (`PostProcessEffectSettings`) | Modern URP Equivalent (`VolumeComponent` / Feature) | Key Parameter Mapping & Notes |
|---|---|---|
| **Ambient Occlusion** (`AmbientOcclusion`) | **Screen Space Ambient Occlusion (SSAO)** | **NOT in VolumeProfile!** Implemented as a `ScreenSpaceAmbientOcclusion` `ScriptableRendererFeature` added to the `UniversalRendererData` asset. |
| **Auto Exposure** (`AutoExposure`) | `ColorAdjustments.postExposure` / Custom Feature | PPv2 eye-adaptation histogram is native in HDRP (`Exposure`), but not in basic URP. Use static `postExposure` or a custom exposure renderer feature. |
| **Bloom** (`Bloom`) | `Bloom` (`UnityEngine.Rendering.Universal.Bloom`) | • `intensity` $\rightarrow$ `intensity`<br>• `threshold` $\rightarrow$ `threshold`<br>• `diffusion` $\rightarrow$ `scatter` (0–1)<br>• `softKnee` $\rightarrow$ built into threshold response curve<br>• `anamorphicRatio` $\rightarrow$ not supported in URP (isotropic blur only)<br>• `color` $\rightarrow$ `tint`<br>• `dirtTexture` / `dirtIntensity` $\rightarrow$ identical |
| **Chromatic Aberration** (`ChromaticAberration`) | `ChromaticAberration` | • `intensity` $\rightarrow$ `intensity`<br>• `spectralLut` $\rightarrow$ `spectralLut`<br>• `fastMode` $\rightarrow$ obsolete (automatic mobile optimization) |
| **Color Grading** (`ColorGrading`) | Split across **8 modular components**: | In PPv2, Color Grading was a monolithic block. In URP, it is split: |
| ↳ *Tonemapping* | `Tonemapping` | • `mode` $\rightarrow$ `Neutral` or `ACES` |
| ↳ *Basic Tone* | `ColorAdjustments` | • `postExposure` $\rightarrow$ `postExposure` (EV)<br>• `contrast` $\rightarrow$ `contrast`<br>• `colorFilter` $\rightarrow$ `colorFilter`<br>• `hueShift` $\rightarrow$ `hueShift`<br>• `saturation` $\rightarrow$ `saturation` |
| ↳ *White Balance* | `WhiteBalance` | • `temperature` $\rightarrow$ `temperature`<br>• `tint` $\rightarrow$ `tint` |
| ↳ *Trackballs (Wheels)* | `LiftGammaGain` | • `lift`, `gamma`, `gain` Vector4 parameters |
| ↳ *Shadows / Midtones / Highlights* | `ShadowsMidtonesHighlights` | • Direct 1:1 match with range boundary sliders |
| ↳ *Curves* | `ColorCurves` | • `master`, `red`, `green`, `blue`, `hueVsHue`, `hueVsSat`, `satVsSat`, `lumVsSat` |
| ↳ *Mixer* | `ChannelMixer` | • `redOutRedIn`, `greenOutGreenIn`, `blueOutBlueIn`, etc. |
| ↳ *Split Toning* | `SplitToning` | • `shadows`, `highlights`, `balance` |
| **Depth of Field** (`DepthOfField`) | `DepthOfField` | • PPv2 Aperture/FocalLength $\rightarrow$ URP `mode = DepthOfFieldMode.Bokeh` (`focusDistance`, `focalLength`, `aperture`, `bladeCount`).<br>• Fast Gaussian distance mode $\rightarrow$ `mode = DepthOfFieldMode.Gaussian` (`gaussianStart`, `gaussianEnd`, `gaussianMaxRadius`). |
| **Dithering** (PPv2 layer toggle) | URP Asset / Camera setting | Configured on URP Asset (`dithering` toggle) or camera post-processing pass. |
| **Grain** (`Grain`) | `FilmGrain` (`FilmGrain`) | • PPv2 procedurally generated grain $\rightarrow$ URP pre-baked lookup table textures: `FilmGrainLookup.Thin1`, `Medium1`-`Medium6`, `Large01`, or `Custom`. |
| **Lens Distortion** (`LensDistortion`) | `LensDistortion` | Direct 1:1 parameter match: `intensity`, `xMultiplier`, `yMultiplier`, `center`, `scale`. |
| **Motion Blur** (`MotionBlur`) | `MotionBlur` | • PPv2 shutter angle $\rightarrow$ URP `intensity` & `quality`.<br>• URP supports `CameraOnly` and `CameraAndObjects` (requires motion vectors pass). |
| **Screen Space Reflections** (`ScreenSpaceReflections`) | HDRP native / URP Custom Feature | Not standard in stock URP Volume. Unity 6 adds Screen Space Reflections passes or custom renderer features. |
| **Subpixel Morphological Antialiasing (SMAA)** | Camera Antialiasing setting | Configured on Camera: `camData.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing`. Quality presets: Low, Medium, High. |
| **Fast Approximate Antialiasing (FXAA)** | Camera Antialiasing setting | Configured on Camera: `camData.antialiasing = AntialiasingMode.FastApproximateAntialiasing`. |
| **Temporal Antialiasing (TAA)** | Camera Antialiasing setting | Configured on Camera: `camData.antialiasing = AntialiasingMode.TemporalAntiAliasing` (Unity 2022.2+ / Unity 6). Requires HDR and depth/motion vectors. |
| **Vignette** (`Vignette`) | `Vignette` | Direct 1:1 match: `color`, `center`, `intensity`, `smoothness`, `rounded`. (Mask mode requires custom shader/texture pass). |

---

## 3. Code Migration: C# API Comparison

### 3.1 Volume and Camera Setup

#### Legacy PPv2 (Built-in Pipeline)
```csharp
using UnityEngine.Rendering.PostProcessing;

// Add PostProcessLayer to Camera
var layer = camera.gameObject.AddComponent<PostProcessLayer>();
layer.volumeLayer = LayerMask.GetMask("PostProcessing");
layer.antialiasingMode = PostProcessLayer.Antialiasing.SubpixelMorphologicalAntialiasing;

// Create Volume
var volumeGO = new GameObject("Global PostProcess Volume");
var volume = volumeGO.AddComponent<PostProcessVolume>();
volume.isGlobal = true;
volume.priority = 1f;

var profile = ScriptableObject.CreateInstance<PostProcessProfile>();
volume.profile = profile;

// Add Bloom in PPv2
var bloom = profile.AddSettings<Bloom>();
bloom.intensity.value = 1.5f;
bloom.intensity.overrideState = true;
```

#### Modern URP (Unity 6 / URP 17+)
```csharp
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

// Configure Camera
var camData = camera.GetUniversalAdditionalCameraData();
camData.renderPostProcessing = true;
camData.volumeLayerMask = LayerMask.GetMask("Default", "PostProcessing");
camData.antialiasing = AntialiasingMode.SubpixelMorphologicalAntiAliasing;
camData.antialiasingQuality = AntialiasingQuality.High;

// Create Volume
var volumeGO = new GameObject("Global Volume");
var volume = volumeGO.AddComponent<Volume>();
volume.isGlobal = true;
volume.priority = 1f;

var profile = ScriptableObject.CreateInstance<VolumeProfile>();
volume.profile = profile;

// Add Bloom in URP
var bloom = profile.Add<Bloom>(true); // 'true' sets overrideState = true on all properties!
bloom.intensity.value = 1.5f;
bloom.threshold.value = 0.9f;
bloom.scatter.value = 0.7f;
```

---

## 4. Custom Post-Processing Effects: PPv2 vs Unity 6 Render Graph

### 4.1 The Legacy PPv2 Way
In PPv2, creating a custom effect required subclassing `PostProcessEffectSettings` and `PostProcessEffectRenderer<T>`:

```csharp
// PPv2 Legacy Custom Effect
using System;
using UnityEngine;
using UnityEngine.Rendering.PostProcessing;

[Serializable]
[PostProcess(typeof(GrayscaleRenderer), PostProcessEvent.AfterStack, "Custom/Grayscale")]
public sealed class Grayscale : PostProcessEffectSettings
{
    [Range(0f, 1f), Tooltip("Grayscale intensity")]
    public FloatParameter blend = new FloatParameter { value = 0.5f };
}

public sealed class GrayscaleRenderer : PostProcessEffectRenderer<Grayscale>
{
    public override void Render(PostProcessRenderContext context)
    {
        var sheet = context.propertySheets.Get(Shader.Find("Hidden/Custom/Grayscale"));
        sheet.properties.SetFloat("_Blend", settings.blend);
        context.command.BlitFullscreenTriangle(context.source, context.destination, sheet, 0);
    }
}
```

### 4.2 The Modern Unity 6 URP Way (Render Graph API)
In Unity 6 / URP 17+, custom post-processing combines a `VolumeComponent` (data) and a `ScriptableRendererFeature` using the **Render Graph API**:

```csharp
using System;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;
using UnityEngine.Rendering.RenderGraphModule;

// 1. Data Component (VolumeComponent)
[Serializable, VolumeComponentMenu("Custom/Grayscale")]
public class GrayscaleVolumeComponent : VolumeComponent, IPostProcessComponent
{
    public ClampedFloatParameter blend = new ClampedFloatParameter(0f, 0f, 1f);

    public bool IsActive() => blend.value > 0f;
    public bool IsTileCompatible() => false;
}

// 2. Render Graph Renderer Feature
public class GrayscaleRenderFeature : ScriptableRendererFeature
{
    [SerializeField] private Shader shader;
    private Material material;
    private GrayscalePass pass;

    public override void Create()
    {
        if (shader == null) shader = Shader.Find("Hidden/Custom/Grayscale");
        if (shader != null) material = CoreUtils.CreateEngineMaterial(shader);
        pass = new GrayscalePass(material);
        pass.renderPassEvent = RenderPassEvent.BeforeRenderingPostProcessing;
    }

    public override void AddRenderPasses(ScriptableRenderer renderer, ref RenderingData renderingData)
    {
        var stack = VolumeManager.instance.stack;
        var customEffect = stack.GetComponent<GrayscaleVolumeComponent>();
        if (customEffect != null && customEffect.IsActive())
        {
            pass.Setup(customEffect);
            renderer.EnqueuePass(pass);
        }
    }

    protected override void Dispose(bool disposing)
    {
        CoreUtils.Destroy(material);
    }

    private class GrayscalePass : ScriptableRenderPass
    {
        private Material mat;
        private GrayscaleVolumeComponent settings;

        public GrayscalePass(Material mat) { this.mat = mat; }
        public void Setup(GrayscaleVolumeComponent comp) { this.settings = comp; }

        private class PassData
        {
            public TextureHandle source;
            public TextureHandle destination;
            public Material material;
            public float blend;
        }

        public override void RecordRenderGraph(RenderGraph renderGraph, ContextContainer frameData)
        {
            if (mat == null || settings == null) return;

            var universalResourceData = frameData.Get<UniversalResourceData>();
            var cameraData = frameData.Get<UniversalCameraData>();

            TextureHandle activeColor = universalResourceData.activeColorTexture;
            var desc = cameraData.cameraTargetDescriptor;
            desc.depthBufferBits = 0;

            TextureHandle tempTarget = UniversalRenderer.CreateRenderGraphTexture(
                renderGraph, desc, "_TempGrayscaleTarget", false);

            using (var builder = renderGraph.AddRasterRenderPass<PassData>("Grayscale Pass", out var passData))
            {
                passData.source = activeColor;
                passData.destination = tempTarget;
                passData.material = mat;
                passData.blend = settings.blend.value;

                builder.UseTexture(passData.source, AccessFlags.Read);
                builder.SetRenderAttachment(passData.destination, 0, AccessFlags.Write);

                builder.SetRenderFunc((PassData data, RasterGraphContext context) =>
                {
                    data.material.SetFloat("_Blend", data.blend);
                    Blitter.BlitTexture(context.cmd, data.source, new Vector4(1, 1, 0, 0), data.material, 0);
                });
            }

            // Blit back to camera target
            using (var builder = renderGraph.AddRasterRenderPass<PassData>("Grayscale Blit Back", out var passData))
            {
                passData.source = tempTarget;
                passData.destination = activeColor;
                passData.material = mat;

                builder.UseTexture(passData.source, AccessFlags.Read);
                builder.SetRenderAttachment(passData.destination, 0, AccessFlags.Write);

                builder.SetRenderFunc((PassData data, RasterGraphContext context) =>
                {
                    Blitter.BlitTexture(context.cmd, data.source, new Vector4(1, 1, 0, 0), 0.0f, false);
                });
            }
        }
    }
}
```

---

## 5. Built-in Render Pipeline Converter

When migrating a project that currently uses PPv2 to URP:

1. Open **Window > Rendering > Render Pipeline Converter**.
2. Select **Built-in to URP**.
3. Check **Post-processing Stack v2 Converter**.
4. Click **Initialize Converters**, inspect candidates, and click **Convert Assets**.

### Post-Conversion Audit Checklist:
- [ ] Confirm all `PostProcessProfile` assets were converted into valid `VolumeProfile` assets.
- [ ] Verify that converted profiles do NOT have dangling null overrides (`components: []`).
- [ ] In scenes, replace any remaining `PostProcessVolume` components with `Volume`.
- [ ] Remove `PostProcessLayer` components from Cameras; ensure `UniversalAdditionalCameraData.renderPostProcessing = true`.
- [ ] In `Packages/manifest.json`, remove `"com.unity.postprocessing"`.
- [ ] For Ambient Occlusion: Ensure SSAO (`ScreenSpaceAmbientOcclusion`) is added as a Renderer Feature on the Universal Renderer Data asset.
- [ ] Ensure `HDR` is enabled on the `UniversalRenderPipelineAsset` if Tonemapping or Bloom is active.
