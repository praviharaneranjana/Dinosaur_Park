// Falling-water curtain and plunge foam. Mesh UV: x across the strand (0..1), y along the flow
// (0 = lip, 1 = bottom). The generator writes uv2.x = curtain length in metres so streak tiling is
// in world units. Streaks scroll down fast; the top stays glassy, the bottom turns to white foam,
// sides break up. _Radial: the plunge disc (uv.x = angle 0..1, uv.y = radius 0..1), foam rolls outward.
Shader "DinoPark/Environment/Waterfall"
{
    Properties
    {
        _StreakTex ("Streak Texture", 2D) = "white" {}
        _FoamTex ("Foam Texture", 2D) = "white" {}
        _TopColor ("Lip Colour", Color) = (0.42, 0.78, 0.80, 1)
        _MidColor ("Fall Colour", Color) = (0.70, 0.90, 0.93, 1)
        _FoamColor ("Foam Colour", Color) = (0.97, 0.99, 1, 1)
        _FallSpeed ("Fall Speed (m/s)", Float) = 7
        _StreakTiling ("Streak Tiling (across, per metre down)", Vector) = (3, 0.12, 0, 0)
        _Alpha ("Opacity", Range(0, 1)) = 0.9
        _FoamStart ("Foam Starts At (0..1 down)", Range(0, 1)) = 0.55
        _EdgeSoftness ("Edge Softness", Range(0.01, 0.5)) = 0.14
        [Toggle(_RADIAL)] _Radial ("Radial Plunge Foam", Float) = 0
        _Wobble ("Vertex Wobble (m)", Float) = 0.08
    }

    SubShader
    {
        Tags { "RenderType" = "Transparent" "RenderPipeline" = "UniversalPipeline" "Queue" = "Transparent" }

        Pass
        {
            Name "Waterfall"
            Tags { "LightMode" = "UniversalForward" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Off

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma shader_feature_local _RADIAL
            #pragma multi_compile_fog
            #pragma multi_compile_instancing
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _StreakTex_ST;
                float4 _FoamTex_ST;
                half4 _TopColor;
                half4 _MidColor;
                half4 _FoamColor;
                float _FallSpeed;
                float4 _StreakTiling;
                half _Alpha;
                half _FoamStart;
                half _EdgeSoftness;
                half _Radial;
                float _Wobble;
            CBUFFER_END

            TEXTURE2D(_StreakTex); SAMPLER(sampler_StreakTex);
            TEXTURE2D(_FoamTex); SAMPLER(sampler_FoamTex);

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                float2 uv : TEXCOORD0;
                float2 uv2 : TEXCOORD1;
                half4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float len : TEXCOORD1;
                float3 positionWS : TEXCOORD2;
                half3 normalWS : TEXCOORD3;
                half fogFactor : TEXCOORD4;
                half4 color : COLOR;
                UNITY_VERTEX_INPUT_INSTANCE_ID
            };

            Varyings Vert(Attributes input)
            {
                Varyings o = (Varyings)0;
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_TRANSFER_INSTANCE_ID(input, o);
                float3 p = TransformObjectToWorld(input.positionOS.xyz);
                float3 n = TransformObjectToWorldNormal(input.normalOS);
                float t = _Time.y;
                p += n * _Wobble * sin(t * 6.0 + input.uv.y * 9.0 + input.uv.x * 5.0) * input.uv.y;
                o.positionWS = p;
                o.normalWS = n;
                o.positionCS = TransformWorldToHClip(p);
                o.uv = input.uv;
                o.len = max(input.uv2.x, 1.0);
                o.color = input.color;
                o.fogFactor = ComputeFogFactor(o.positionCS.z);
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float t = _Time.y;
                float2 uv = input.uv;
                half3 col;
                half alpha;
                #if defined(_RADIAL)
                    float r = uv.y;
                    float ang = uv.x;
                    float2 fuv = float2(ang * 6.0, r * input.len * 0.25 - t * 0.6);
                    half f1 = SAMPLE_TEXTURE2D(_FoamTex, sampler_FoamTex, fuv).r;
                    half f2 = SAMPLE_TEXTURE2D(_FoamTex, sampler_FoamTex, fuv * 1.7 + float2(0.31, -t * 0.25)).r;
                    half foam = saturate((f1 * 0.6 + f2 * 0.6) * 1.3 - r * 0.9);
                    col = lerp(_MidColor.rgb, _FoamColor.rgb, saturate(foam * 1.4));
                    alpha = saturate(foam * 1.5) * (1.0 - smoothstep(0.55, 1.0, r)) * _Alpha;
                #else
                    float down = uv.y * input.len;                      // metres from the lip
                    float2 s1uv = float2(uv.x * _StreakTiling.x, down * _StreakTiling.y - t * _FallSpeed * _StreakTiling.y);
                    float2 s2uv = float2(uv.x * _StreakTiling.x * 1.73 + 0.37, down * _StreakTiling.y * 0.62 - t * _FallSpeed * 1.3 * _StreakTiling.y * 0.62);
                    half s1 = SAMPLE_TEXTURE2D(_StreakTex, sampler_StreakTex, s1uv).r;
                    half s2 = SAMPLE_TEXTURE2D(_StreakTex, sampler_StreakTex, s2uv).r;
                    half streak = s1 * 0.55 + s2 * 0.45;
                    half fall = saturate(uv.y * 3.0);
                    half3 base = lerp(_TopColor.rgb, _MidColor.rgb, fall);
                    half foamT = saturate((uv.y - _FoamStart) / max(1.0 - _FoamStart, 0.01));
                    half white = saturate(streak * (0.35 + fall * 0.8) + foamT * foamT * 1.2 - 0.15);
                    col = lerp(base, _FoamColor.rgb, white);
                    half edge = smoothstep(0.0, _EdgeSoftness, uv.x) * smoothstep(0.0, _EdgeSoftness, 1.0 - uv.x);
                    half breakup = saturate(edge * 1.6 - (1.0 - streak) * (1.0 - edge) * 1.4);
                    alpha = saturate((0.55 + streak * 0.55 + foamT * 0.4) * breakup) * _Alpha;
                    alpha *= smoothstep(0.0, 0.03, uv.y + 0.01);
                #endif
                Light light = GetMainLight();
                half3 ambient = SampleSH(half3(0, 1, 0));
                col *= ambient * 0.75 + light.color * 0.6;
                col = MixFog(col, input.fogFactor);
                return half4(col, alpha * input.color.a);
            }
            ENDHLSL
        }
    }

    FallBack Off
}
