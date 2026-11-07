// Lit URP shader for the island (Blender procedural materials baked to vertex colour).
// albedo = vertexColour (sRGB) * tint * (map colour when _UseMapColor is on). The map alpha drives
// alpha clip (leaf cards). Opaque / cutout / transparent are set by the island importer through
// _SrcBlend, _DstBlend, _ZWrite, the _ALPHATEST_ON / _SURFACE_TYPE_TRANSPARENT keywords and the queue.
// Optional:
//   _TRIPLANAR  world-space rock detail, strata bands and moss on up-facing surfaces (cliffs, mountain).
//   Wind        _WindSway (whole plant bends with height above its pivot) and _WindFlutter (leaf/grass
//               jitter). Globals _DP_WindDir (xz dir, w strength) and _DP_WindParams (x speed) come
//               from WindSettings.cs; sensible defaults are used when it is missing.
Shader "DinoPark/Environment/VertexColorLit"
{
    Properties
    {
        _BaseMap ("Base Map", 2D) = "white" {}
        _BaseColor ("Tint", Color) = (1, 1, 1, 1)
        [Toggle] _UseMapColor ("Use Map Colour (off = map alpha only)", Float) = 1
        _Smoothness ("Smoothness", Range(0, 1)) = 0.1
        _Cutoff ("Alpha Cutoff", Range(0, 1)) = 0.5
        [Toggle(_ALPHATEST_ON)] _AlphaClip ("Alpha Clip", Float) = 0
        [Toggle(_SURFACE_TYPE_TRANSPARENT)] _Transparent ("Transparent", Float) = 0
        [Enum(UnityEngine.Rendering.CullMode)] _Cull ("Cull", Float) = 2

        [Header(Wind)]
        _WindSway ("Wind Sway (bend with height)", Range(0, 3)) = 0
        _WindFlutter ("Wind Flutter (leaves, grass)", Range(0, 3)) = 0

        [Header(Triplanar rock)]
        [Toggle(_TRIPLANAR)] _Triplanar ("Triplanar Rock Detail", Float) = 0
        _DetailMap ("Rock Detail (grey)", 2D) = "grey" {}
        _DetailTiling ("Detail Tiling (per metre)", Float) = 0.18
        _DetailStrength ("Detail Strength", Range(0, 2)) = 1
        _StrataHeight ("Strata Band Height (m)", Float) = 1.6
        _StrataStrength ("Strata Strength", Range(0, 1)) = 0.35
        _MossColor ("Moss Colour", Color) = (0.32, 0.47, 0.18, 1)
        _MossAmount ("Moss Amount", Range(0, 1)) = 0.5

        [HideInInspector] _SrcBlend ("Src Blend", Float) = 1
        [HideInInspector] _DstBlend ("Dst Blend", Float) = 0
        [HideInInspector] _ZWrite ("ZWrite", Float) = 1
    }

    SubShader
    {
        Tags { "RenderType" = "Opaque" "RenderPipeline" = "UniversalPipeline" "Queue" = "Geometry" }

        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"

        CBUFFER_START(UnityPerMaterial)
            float4 _BaseMap_ST;
            half4 _BaseColor;
            half _UseMapColor;
            half _Smoothness;
            half _Cutoff;
            half _AlphaClip;
            half _Transparent;
            half _Cull;
            half _WindSway;
            half _WindFlutter;
            half _Triplanar;
            float4 _DetailMap_ST;
            float _DetailTiling;
            half _DetailStrength;
            float _StrataHeight;
            half _StrataStrength;
            half4 _MossColor;
            half _MossAmount;
            half _SrcBlend;
            half _DstBlend;
            half _ZWrite;
        CBUFFER_END

        TEXTURE2D(_BaseMap);
        SAMPLER(sampler_BaseMap);
        TEXTURE2D(_DetailMap);
        SAMPLER(sampler_DetailMap);

        float4 _DP_WindDir;      // xz = direction, w = strength (0 = not set)
        float4 _DP_WindParams;   // x = speed

        // Vertex colours are stored sRGB in the FBX.
        half3 DecodeVertexColour(half3 c)
        {
            #if defined(UNITY_COLORSPACE_GAMMA)
                return c;
            #else
                half3 lo = c / 12.92h;
                half3 hi = pow(max((c + 0.055h) / 1.055h, 0.0h), 2.4h);
                return lerp(hi, lo, step(c, 0.04045h));
            #endif
        }

        half4 SampleBase(float2 uv)
        {
            return SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, uv);
        }

        // Bends the plant away from the wind in proportion to height above its pivot (base),
        // so trunk and leaves of one plant move together; flutter adds a small per-vertex jitter.
        float3 ApplyWind(float3 positionWS)
        {
            if (_WindSway + _WindFlutter <= 0.0) return positionWS;
            float3 origin = float3(UNITY_MATRIX_M._m03, UNITY_MATRIX_M._m13, UNITY_MATRIX_M._m23);
            float strength = _DP_WindDir.w > 0.0 ? _DP_WindDir.w : 1.0;
            float2 dir = dot(_DP_WindDir.xz, _DP_WindDir.xz) > 0.0001 ? normalize(_DP_WindDir.xz) : float2(0.96, 0.28);
            float speed = _DP_WindParams.x > 0.0 ? _DP_WindParams.x : 1.0;
            float t = _Time.y * speed;
            float h = max(positionWS.y - origin.y, 0.0);
            float phase = dot(origin.xz, float2(0.137, 0.091));
            float gust = 0.65 + 0.35 * sin(t * 0.37 + origin.x * 0.021) * sin(t * 0.23 + origin.z * 0.033);
            float sway = (0.55 * sin(t * 1.3 + phase) + 0.25 * sin(t * 2.1 + phase * 1.7) + 0.45) * gust;
            float bend = _WindSway * strength * 0.012 * h * h / (1.0 + 0.045 * h * h);
            float3 offset = float3(dir.x, 0, dir.y) * bend * sway;
            float flutterPhase = dot(positionWS, float3(1.7, 1.3, 2.1));
            float flutter = _WindFlutter * strength * 0.06 * saturate(h * 1.5) * gust;
            offset += float3(sin(t * 3.7 + flutterPhase), 0.35 * sin(t * 4.3 + flutterPhase * 1.3), cos(t * 3.1 + flutterPhase)) * flutter;
            offset.y -= length(offset.xz) * 0.15;
            return positionWS + offset;
        }

        half3 TriplanarDetail(float3 positionWS, half3 normalWS, half3 albedo)
        {
            #if defined(_TRIPLANAR)
                half3 w = pow(abs(normalWS), 4.0h);
                w /= max(w.x + w.y + w.z, 1e-3h);
                float s = _DetailTiling;
                half dx = SAMPLE_TEXTURE2D(_DetailMap, sampler_DetailMap, positionWS.zy * s).r;
                half dy = SAMPLE_TEXTURE2D(_DetailMap, sampler_DetailMap, positionWS.xz * s).r;
                half dz = SAMPLE_TEXTURE2D(_DetailMap, sampler_DetailMap, positionWS.xy * s).r;
                half d = dx * w.x + dy * w.y + dz * w.z;
                half big = SAMPLE_TEXTURE2D(_DetailMap, sampler_DetailMap, positionWS.xz * s * 0.07).r;
                albedo *= lerp(1.0h, d * 2.0h, _DetailStrength);
                float band = frac(positionWS.y / max(_StrataHeight, 0.1) + big * 1.7);
                half strata = smoothstep(0.0, 0.08, band) * (1.0 - smoothstep(0.82, 1.0, band));
                albedo *= lerp(1.0h, lerp(0.72h, 1.08h, strata), _StrataStrength);
                half moss = smoothstep(0.55h, 0.85h, normalWS.y + (d - 0.5h) * 0.6h) * _MossAmount;
                albedo = lerp(albedo, _MossColor.rgb * (0.7h + 0.6h * d), moss);
            #endif
            return albedo;
        }
        ENDHLSL

        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode" = "UniversalForward" }
            Blend [_SrcBlend] [_DstBlend]
            ZWrite [_ZWrite]
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma shader_feature_local_fragment _ALPHATEST_ON
            #pragma shader_feature_local_fragment _SURFACE_TYPE_TRANSPARENT
            #pragma shader_feature_local _TRIPLANAR
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE
            #pragma multi_compile_fragment _ _SHADOWS_SOFT
            #pragma multi_compile_fragment _ _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile_fog
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                half4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float3 positionWS : TEXCOORD1;
                half3 normalWS : TEXCOORD2;
                half fogFactor : TEXCOORD3;
                half4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, o);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                float3 positionWS = ApplyWind(TransformObjectToWorld(input.positionOS.xyz));
                o.positionWS = positionWS;
                o.positionCS = TransformWorldToHClip(positionWS);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                o.color = input.color;
                o.fogFactor = ComputeFogFactor(o.positionCS.z);
                return o;
            }

            half4 Frag(Varyings input, FRONT_FACE_TYPE face : FRONT_FACE_SEMANTIC) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);

                half4 map = SampleBase(input.uv);
                half alpha = map.a * _BaseColor.a;
                #if defined(_ALPHATEST_ON)
                    clip(alpha - _Cutoff);
                #endif

                half3 normalWS = NormalizeNormalPerPixel(input.normalWS);
                normalWS = IS_FRONT_VFACE(face, normalWS, -normalWS);   // two-sided leaves

                half3 albedo = DecodeVertexColour(input.color.rgb) * _BaseColor.rgb;
                albedo *= lerp(half3(1, 1, 1), map.rgb, _UseMapColor);
                albedo = TriplanarDetail(input.positionWS, normalWS, albedo);

                InputData inputData = (InputData)0;
                inputData.positionWS = input.positionWS;
                inputData.positionCS = input.positionCS;
                inputData.normalWS = normalWS;
                inputData.viewDirectionWS = GetWorldSpaceNormalizeViewDir(input.positionWS);
                #if defined(MAIN_LIGHT_CALCULATE_SHADOWS)
                    inputData.shadowCoord = TransformWorldToShadowCoord(input.positionWS);
                #endif
                inputData.fogCoord = input.fogFactor;
                inputData.bakedGI = SampleSH(normalWS);
                inputData.normalizedScreenSpaceUV = GetNormalizedScreenSpaceUV(input.positionCS);
                inputData.shadowMask = half4(1, 1, 1, 1);

                SurfaceData surface = (SurfaceData)0;
                surface.albedo = albedo;
                surface.metallic = 0;
                surface.specular = half3(0, 0, 0);
                surface.smoothness = _Smoothness;
                surface.occlusion = 1;
                surface.alpha = 1;
                #if defined(_SURFACE_TYPE_TRANSPARENT)
                    surface.alpha = alpha;
                #endif

                half4 colour = UniversalFragmentPBR(inputData, surface);
                colour.rgb = MixFog(colour.rgb, inputData.fogCoord);
                return colour;
            }
            ENDHLSL
        }

        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode" = "ShadowCaster" }
            ZWrite On
            ZTest LEqual
            ColorMask 0
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex ShadowVert
            #pragma fragment ShadowFrag
            #pragma shader_feature_local_fragment _ALPHATEST_ON
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            float3 _LightDirection;
            float3 _LightPosition;

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
            };

            Varyings ShadowVert(Attributes input)
            {
                Varyings o;
                UNITY_SETUP_INSTANCE_ID(input);
                float3 positionWS = ApplyWind(TransformObjectToWorld(input.positionOS.xyz));
                float3 normalWS = TransformObjectToWorldNormal(input.normalOS);
                #if defined(_CASTING_PUNCTUAL_LIGHT_SHADOW)
                    float3 lightDirectionWS = normalize(_LightPosition - positionWS);
                #else
                    float3 lightDirectionWS = _LightDirection;
                #endif
                o.positionCS = ApplyShadowClamping(TransformWorldToHClip(ApplyShadowBias(positionWS, normalWS, lightDirectionWS)));
                o.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                return o;
            }

            half4 ShadowFrag(Varyings input) : SV_Target
            {
                #if defined(_ALPHATEST_ON)
                    clip(SampleBase(input.uv).a * _BaseColor.a - _Cutoff);
                #endif
                return 0;
            }
            ENDHLSL
        }

        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode" = "DepthOnly" }
            ZWrite On
            ColorMask R
            Cull [_Cull]

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex DepthVert
            #pragma fragment DepthFrag
            #pragma shader_feature_local_fragment _ALPHATEST_ON
            #pragma multi_compile_instancing
            #include_with_pragmas "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DOTS.hlsl"

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                UNITY_VERTEX_OUTPUT_STEREO
            };

            Varyings DepthVert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(o);
                o.positionCS = TransformWorldToHClip(ApplyWind(TransformObjectToWorld(input.positionOS.xyz)));
                o.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                return o;
            }

            half DepthFrag(Varyings input) : SV_Target
            {
                #if defined(_ALPHATEST_ON)
                    clip(SampleBase(input.uv).a * _BaseColor.a - _Cutoff);
                #endif
                return input.positionCS.z;
            }
            ENDHLSL
        }
    }

    FallBack "Hidden/Universal Render Pipeline/FallbackError"
}
