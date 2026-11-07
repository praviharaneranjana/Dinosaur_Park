// Stylised mobile water for the island.
//   _OCEAN on : Gerstner waves (amplitude fades in shallows), water depth baked in vertex colour R
//               (0..1 = 0.._VertexDepthMax m), surf bands that roll toward the beach.
//   _OCEAN off: rivers, streams, ponds, mud. Flow baked in vertex colour (RG = direction * 0.5 + 0.5,
//               B = speed 0..1, A = depth from the distance to the bank / _VertexDepthMax), flow-map
//               scrolling of normals and foam; bank foam from A.
// Both: foam where the surface meets geometry (shoreline, rocks, banks) from the camera depth texture,
// sun specular, sky fresnel and receive main-light shadows.
Shader "DinoPark/Environment/Water"
{
    Properties
    {
        [Toggle(_OCEAN)] _Ocean ("Ocean Mode", Float) = 0
        _ShallowColor ("Shallow Colour", Color) = (0.25, 0.85, 0.80, 1)
        _DeepColor ("Deep Colour", Color) = (0.03, 0.22, 0.42, 1)
        _DepthRange ("Depth For Deep Colour (m)", Float) = 6
        _AlphaShallow ("Alpha At Edge", Range(0, 1)) = 0.35
        _AlphaDepth ("Depth For Opaque (m)", Float) = 2.5
        _VertexDepthMax ("Vertex Depth Max (m)", Float) = 40

        _NormalMap ("Normal Map", 2D) = "bump" {}
        _NormalTiling ("Normal Tiling (per metre)", Float) = 0.12
        _NormalStrength ("Normal Strength", Range(0, 2)) = 0.6
        _DriftSpeed ("Still-Water Drift Speed", Float) = 0.04
        _FlowSpeed ("Flow Speed (m/s)", Float) = 1.2

        _FoamTex ("Foam Texture", 2D) = "white" {}
        _FoamColor ("Foam Colour", Color) = (0.95, 0.98, 1, 1)
        _FoamTiling ("Foam Tiling (per metre)", Float) = 0.25
        _EdgeFoamDistance ("Edge Foam Distance (m)", Float) = 0.6
        _FlowFoam ("Flow Foam Amount", Range(0, 1)) = 0.25

        _SurfRange ("Surf Range (m depth)", Float) = 3.5
        _SurfFrequency ("Surf Band Frequency", Float) = 2.2
        _SurfSpeed ("Surf Speed", Float) = 1.4
        _SurfStrength ("Surf Strength", Range(0, 1)) = 0.8

        _WaveAmp ("Wave Amount", Range(0, 2)) = 1
        _WaveSpeed ("Wave Speed", Float) = 1
        _WaveDir ("Wave Direction (xz)", Vector) = (0.3, 0, -1, 0)

        _SkyColor ("Sky Reflection", Color) = (0.55, 0.75, 0.95, 1)
        _HorizonColor ("Horizon Reflection", Color) = (0.82, 0.9, 0.95, 1)
        _Reflectivity ("Reflectivity", Range(0, 1)) = 0.55
        _SpecPower ("Sun Spec Power", Float) = 180
        _SpecIntensity ("Sun Spec Intensity", Float) = 2.5
        [HideInInspector] _DebugView ("Debug View (R depth, G foam, B alpha)", Float) = 0
    }

    SubShader
    {
        Tags { "RenderType" = "Transparent" "RenderPipeline" = "UniversalPipeline" "Queue" = "Transparent-10" }

        Pass
        {
            Name "Water"
            Tags { "LightMode" = "UniversalForward" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Back

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma shader_feature_local _OCEAN
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fog
            #pragma multi_compile_instancing
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"

            CBUFFER_START(UnityPerMaterial)
                half4 _ShallowColor;
                half4 _DeepColor;
                float _DepthRange;
                half _AlphaShallow;
                float _AlphaDepth;
                float _VertexDepthMax;
                float4 _NormalMap_ST;
                float _NormalTiling;
                half _NormalStrength;
                float _DriftSpeed;
                float _FlowSpeed;
                float4 _FoamTex_ST;
                half4 _FoamColor;
                float _FoamTiling;
                float _EdgeFoamDistance;
                half _FlowFoam;
                float _SurfRange;
                float _SurfFrequency;
                float _SurfSpeed;
                half _SurfStrength;
                half _WaveAmp;
                float _WaveSpeed;
                float4 _WaveDir;
                half4 _SkyColor;
                half4 _HorizonColor;
                half _Reflectivity;
                float _SpecPower;
                float _SpecIntensity;
                half _Ocean;
                half _DebugView;
            CBUFFER_END

            TEXTURE2D(_NormalMap); SAMPLER(sampler_NormalMap);
            TEXTURE2D(_FoamTex); SAMPLER(sampler_FoamTex);

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                half4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
                half4 color : TEXCOORD2;
                float eyeDepth : TEXCOORD3;
                half fogFactor : TEXCOORD4;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            float3 Gerstner(float2 dir, float steepness, float wavelength, float3 p, float t, inout float3 tangent, inout float3 binormal)
            {
                float k = TWO_PI / wavelength;
                float c = sqrt(9.8 / k);
                float2 d = normalize(dir);
                float f = k * (dot(d, p.xz) - c * t);
                float a = steepness / k;
                float s = sin(f), co = cos(f);
                tangent += float3(-d.x * d.x * steepness * s, d.x * steepness * co, -d.x * d.y * steepness * s);
                binormal += float3(-d.x * d.y * steepness * s, d.y * steepness * co, -d.y * d.y * steepness * s);
                return float3(d.x * a * co, a * s, d.y * a * co);
            }

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, o);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                float3 p = TransformObjectToWorld(input.positionOS.xyz);
                float3 n = TransformObjectToWorldNormal(input.normalOS);
                #if defined(_OCEAN)
                    float depth = input.color.r * _VertexDepthMax;
                    float amp = _WaveAmp * saturate(depth / 7.0) * input.color.a;
                    float t = _Time.y * _WaveSpeed;
                    float2 wd = normalize(_WaveDir.xz + 1e-4);
                    float2 wd2 = float2(wd.x * 0.8 - wd.y * 0.6, wd.x * 0.6 + wd.y * 0.8);
                    float2 wd3 = float2(wd.x * 0.7 + wd.y * 0.7, -wd.x * 0.7 + wd.y * 0.7);
                    float3 tangent = float3(1, 0, 0), binormal = float3(0, 0, 1);
                    float3 q = p;
                    q += Gerstner(wd, 0.16 * amp, 22.0, p, t, tangent, binormal);
                    q += Gerstner(wd2, 0.12 * amp, 11.0, p, t, tangent, binormal);
                    q += Gerstner(wd3, 0.08 * amp, 8.0, p, t, tangent, binormal);
                    p = q;
                    n = normalize(cross(binormal, tangent));
                #endif
                o.positionWS = p;
                o.normalWS = n;
                o.positionCS = TransformWorldToHClip(p);
                o.eyeDepth = -TransformWorldToView(p).z;
                o.color = input.color;
                o.fogFactor = ComputeFogFactor(o.positionCS.z);
                return o;
            }

            half3 SampleNormalTS(float2 uv)
            {
                return UnpackNormal(SAMPLE_TEXTURE2D(_NormalMap, sampler_NormalMap, uv));
            }

            half4 Frag(Varyings input) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                float t = _Time.y;
                float2 screenUV = GetNormalizedScreenSpaceUV(input.positionCS);
                float sceneEye = LinearEyeDepth(SampleSceneDepth(screenUV), _ZBufferParams);
                float edgeDepth = max(sceneEye - input.eyeDepth, 0.0);      // thickness along the view ray

                float2 world = input.positionWS.xz;
                half3 nTS;
                half flowFoam = 0;
                #if defined(_OCEAN)
                    float depth = input.color.r * _VertexDepthMax;
                    float2 drift = normalize(_WaveDir.xz + 1e-4) * _DriftSpeed * 4.0;
                    nTS = SampleNormalTS(world * _NormalTiling + drift * t) + SampleNormalTS(world * _NormalTiling * 2.3 - drift.yx * t * 1.3);
                #else
                    // A = depth estimate from the distance to the bank (baked), 0.._VertexDepthMax m
                    float depth = input.color.a * _VertexDepthMax;
                    float2 flow = (input.color.rg * 2.0 - 1.0) * input.color.b;
                    float2 drift = float2(0.7, 0.4) * _DriftSpeed;
                    float phase0 = frac(t * 0.35);
                    float phase1 = frac(t * 0.35 + 0.5);
                    float blend = abs(phase0 * 2.0 - 1.0);
                    float2 move = flow * _FlowSpeed / 0.35;
                    float2 uvA = world * _NormalTiling - move * phase0 * _NormalTiling + drift * t;
                    float2 uvB = world * _NormalTiling - move * phase1 * _NormalTiling + drift * t + 0.5;
                    nTS = lerp(SampleNormalTS(uvA), SampleNormalTS(uvB), blend);
                    nTS += SampleNormalTS(world * _NormalTiling * 2.7 + drift.yx * t * 2.0) * 0.5;
                    float2 fA = world * _FoamTiling - move * phase0 * _FoamTiling;
                    float2 fB = world * _FoamTiling - move * phase1 * _FoamTiling + 0.37;
                    half streak = lerp(SAMPLE_TEXTURE2D(_FoamTex, sampler_FoamTex, fA).r, SAMPLE_TEXTURE2D(_FoamTex, sampler_FoamTex, fB).r, blend);
                    flowFoam = smoothstep(0.55, 0.9, streak) * _FlowFoam * saturate(input.color.b * 1.5);
                #endif
                half3 geomN = normalize(input.normalWS);
                half3 N = normalize(geomN + half3(nTS.x, 0, nTS.y) * _NormalStrength);

                // colour by depth
                half deepT = saturate(depth / max(_DepthRange, 0.01));
                half3 waterCol = lerp(_ShallowColor.rgb, _DeepColor.rgb, deepT * (2.0 - deepT));
                // foam: shoreline/rock contact + flow streaks + surf bands
                half foamTex = SAMPLE_TEXTURE2D(_FoamTex, sampler_FoamTex, world * _FoamTiling + float2(t * 0.02, t * 0.013)).r;
                #if defined(_OCEAN)
                    half alpha = lerp(_AlphaShallow, 1.0, saturate(min(depth, edgeDepth * 1.5) / max(_AlphaDepth, 0.01)));
                    half edge = 1.0 - saturate(edgeDepth / max(_EdgeFoamDistance, 0.01));
                #else
                    half alpha = lerp(_AlphaShallow, 1.0, saturate(depth / max(_AlphaDepth, 0.01)));
                    half edge = 1.0 - saturate(depth / max(_EdgeFoamDistance, 0.01));
                #endif
                half foam = saturate(edge * (0.55 + foamTex)) ;
                foam = max(foam, flowFoam);
                #if defined(_OCEAN)
                    half surfZone = 1.0 - saturate(depth / max(_SurfRange, 0.01));
                    half band = pow(saturate(sin(depth * _SurfFrequency * TWO_PI / max(_SurfRange, 0.1) + t * _SurfSpeed) * 0.5 + 0.5), 6.0);
                    half surf = band * surfZone * smoothstep(0.25, 0.75, foamTex + surfZone * 0.4) * _SurfStrength;
                    foam = max(foam, surf);
                #endif
                foam = saturate(foam);

                // lighting
                float4 shadowCoord = TransformWorldToShadowCoord(input.positionWS);
                Light light = GetMainLight(shadowCoord);
                half shadow = lerp(0.55h, 1.0h, light.shadowAttenuation);
                half3 V = GetWorldSpaceNormalizeViewDir(input.positionWS);
                half NdotL = saturate(dot(N, light.direction));
                half3 ambient = SampleSH(N);
                // Kept at or below 1x so LDR (mobile, no HDR) does not clip water and foam to white.
                half3 lit = waterCol * min(ambient * 0.55 + light.color * (0.35 + 0.4 * NdotL) * shadow, 1.0h);
                half fresnel = 0.02 + 0.98 * pow(1.0 - saturate(dot(N, V)), 5.0);
                half3 R = reflect(-V, N);
                half3 sky = lerp(_HorizonColor.rgb, _SkyColor.rgb, saturate(R.y * 1.5));
                half3 col = lerp(lit, sky, fresnel * _Reflectivity);
                half3 H = normalize(light.direction + V);
                half spec = pow(saturate(dot(N, H)), _SpecPower) * _SpecIntensity * shadow;
                col += light.color * spec * (1.0 - foam);
                half3 foamLit = _FoamColor.rgb * min(ambient * 0.45 + light.color * (0.45 + 0.25 * NdotL) * shadow, 0.95h);
                col = lerp(col, foamLit, foam);
                alpha = saturate(max(alpha, foam) + fresnel * 0.3);
                #if defined(_OCEAN)
                    alpha *= input.color.a;
                #endif

                col = MixFog(col, input.fogFactor);
                if (_DebugView > 0.5) return half4(saturate(depth * 0.5), foam, alpha, 1);
                return half4(col, alpha);
            }
            ENDHLSL
        }
    }

    FallBack Off
}
