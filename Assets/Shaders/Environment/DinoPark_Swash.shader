// Dino Park Tycoon - beach swash (URP forward, mobile).
// A thin sheet laid 4 cm over the beach. Vertex colour R = ground height above sea level
// ((R * _HeightRange) - _HeightOffset metres), A = fade at the sheet's inland edge.
// Each wave runs up the sand (fast) to _RunUp metres above sea level and drains back (slow), with
// a foam line at its front and darker wet sand left behind. Phase changes along the shore so the
// beach never moves in lockstep. Hidden below sea level, where the ocean surface takes over.
// Cost: 2 texture samples, no loops, no depth texture. Queue sits between the ocean and rivers.
Shader "DinoPark/Environment/Swash"
{
    Properties
    {
        [Header(Look)]
        _FoamTex ("Foam (R)", 2D) = "white" {}
        _FoamTiling ("Foam Tiling (per m)", Float) = 0.3
        _WaterColor ("Swash Water", Color) = (0.62, 0.90, 0.86, 1)
        _FoamColor ("Foam", Color) = (0.96, 0.98, 1, 1)
        _WetColor ("Wet Sand (rgb, a = strength)", Color) = (0.30, 0.24, 0.16, 0.35)
        [Header(Waves)]
        _RunUp ("Run Up (m above sea)", Float) = 0.5
        _Period ("Wave Period (s)", Float) = 7
        _PhaseScale ("Phase Variation Along Shore", Float) = 1.6
        [Header(Encoding)]
        _HeightRange ("Height Range In R (m)", Float) = 1.8
        _HeightOffset ("Height Offset In R (m)", Float) = 0.3
    }

    SubShader
    {
        Tags { "RenderType" = "Transparent" "RenderPipeline" = "UniversalPipeline" "Queue" = "Transparent-15" "IgnoreProjector" = "True" }

        Pass
        {
            Name "Swash"
            Tags { "LightMode" = "UniversalForward" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Back
            Offset -1, -1

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fog
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _FoamTex_ST;
                float _FoamTiling;
                half4 _WaterColor;
                half4 _FoamColor;
                half4 _WetColor;
                float _RunUp;
                float _Period;
                float _PhaseScale;
                float _HeightRange;
                float _HeightOffset;
            CBUFFER_END

            TEXTURE2D(_FoamTex); SAMPLER(sampler_FoamTex);

            struct Attributes
            {
                float4 positionOS : POSITION;
                float3 normalOS : NORMAL;
                half4 color : COLOR;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float3 positionWS : TEXCOORD0;
                half3 normalWS : TEXCOORD1;
                half4 color : TEXCOORD2;
                half fogFactor : TEXCOORD3;
            };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                o.positionWS = TransformObjectToWorld(input.positionOS.xyz);
                o.normalWS = TransformObjectToWorldNormal(input.normalOS);
                o.positionCS = TransformWorldToHClip(o.positionWS);
                o.color = input.color;
                o.fogFactor = ComputeFogFactor(o.positionCS.z);
                return o;
            }

            // 0 -> 1 quickly (run up, first 30% of the cycle), then back to 0 slowly (backwash).
            half Surge(float c)
            {
                return min(smoothstep(0.0, 0.3, c), 1.0 - smoothstep(0.3, 1.0, c));
            }

            half4 Frag(Varyings input) : SV_Target
            {
                float t = _Time.y;
                float2 w = input.positionWS.xz;
                float h = input.color.r * _HeightRange - _HeightOffset;      // metres above sea level

                // low-frequency phase along the shore, from the foam texture (no extra noise texture)
                half phase = SAMPLE_TEXTURE2D(_FoamTex, sampler_FoamTex, w * 0.004).r * _PhaseScale;
                float c1 = frac(t / max(_Period, 0.5) + phase);
                float c2 = frac(c1 + 0.47);
                // a big wave and a smaller one between them
                float front = _RunUp * max(Surge(c1), 0.55 * Surge(c2));

                half cover = 1.0 - smoothstep(front - 0.02, front + 0.02, h);           // 1 where the swash is
                half line = cover * smoothstep(front - 0.10, front, h);                 // foam at the front
                half foamTex = SAMPLE_TEXTURE2D(_FoamTex, sampler_FoamTex, w * _FoamTiling + float2(t * 0.03, t * 0.02)).r;
                half foam = saturate(line * (0.7 + foamTex) + cover * foamTex * 0.3);

                // wet sand: below the highest recent run-up, fading as it dries
                half wet = (1.0 - cover) * (1.0 - smoothstep(0.0, _RunUp, h)) * _WetColor.a;

                half3 water = lerp(_WaterColor.rgb, _FoamColor.rgb, foam);
                half3 col = lerp(_WetColor.rgb, water, cover);
                half alpha = max(cover * lerp(0.35h, 0.95h, foam), wet);
                alpha *= smoothstep(-0.12, 0.03, h) * input.color.a;                  // the ocean takes over below sea level

                Light light = GetMainLight();
                half NdotL = saturate(dot(normalize(input.normalWS), light.direction));
                col *= SampleSH(half3(0, 1, 0)) * 0.6 + light.color * (0.35 + 0.35 * NdotL);
                col = MixFog(col, input.fogFactor);
                return half4(col, alpha);
            }
            ENDHLSL
        }
    }

    FallBack Off
}
