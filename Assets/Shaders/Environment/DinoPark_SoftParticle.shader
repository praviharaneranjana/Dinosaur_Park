// Unlit alpha-blended particle for waterfall spray and mist: texture alpha * vertex colour,
// lit by the main light colour and ambient so spray does not glow at dusk. Soft fade where the
// particle meets geometry (camera depth texture) so mist never shows hard intersection lines.
Shader "DinoPark/Environment/SoftParticle"
{
    Properties
    {
        _BaseMap ("Sprite", 2D) = "white" {}
        _BaseColor ("Tint", Color) = (1, 1, 1, 1)
        _SoftDistance ("Soft Fade Distance (m)", Float) = 1.5
    }

    SubShader
    {
        Tags { "RenderType" = "Transparent" "RenderPipeline" = "UniversalPipeline" "Queue" = "Transparent+10" "IgnoreProjector" = "True" }

        Pass
        {
            Name "SoftParticle"
            Tags { "LightMode" = "UniversalForward" }
            Blend SrcAlpha OneMinusSrcAlpha
            ZWrite Off
            Cull Off

            HLSLPROGRAM
            #pragma target 3.0
            #pragma vertex Vert
            #pragma fragment Frag
            #pragma multi_compile_fog
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
            #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/DeclareDepthTexture.hlsl"

            CBUFFER_START(UnityPerMaterial)
                float4 _BaseMap_ST;
                half4 _BaseColor;
                float _SoftDistance;
            CBUFFER_END

            TEXTURE2D(_BaseMap); SAMPLER(sampler_BaseMap);

            struct Attributes
            {
                float4 positionOS : POSITION;
                float2 uv : TEXCOORD0;
                half4 color : COLOR;
            };

            struct Varyings
            {
                float4 positionCS : SV_POSITION;
                float2 uv : TEXCOORD0;
                float eyeDepth : TEXCOORD1;
                half fogFactor : TEXCOORD2;
                half4 color : COLOR;
            };

            Varyings Vert(Attributes input)
            {
                Varyings o;
                float3 p = TransformObjectToWorld(input.positionOS.xyz);
                o.positionCS = TransformWorldToHClip(p);
                o.eyeDepth = -TransformWorldToView(p).z;
                o.uv = TRANSFORM_TEX(input.uv, _BaseMap);
                o.color = input.color;
                o.fogFactor = ComputeFogFactor(o.positionCS.z);
                return o;
            }

            half4 Frag(Varyings input) : SV_Target
            {
                half4 tex = SAMPLE_TEXTURE2D(_BaseMap, sampler_BaseMap, input.uv);
                half4 c = tex * input.color * _BaseColor;
                float2 screenUV = GetNormalizedScreenSpaceUV(input.positionCS);
                float sceneEye = LinearEyeDepth(SampleSceneDepth(screenUV), _ZBufferParams);
                c.a *= saturate((sceneEye - input.eyeDepth) / max(_SoftDistance, 0.01));
                Light light = GetMainLight();
                c.rgb *= SampleSH(half3(0, 1, 0)) * 0.7 + light.color * 0.55;
                c.rgb = MixFog(c.rgb, input.fogFactor);
                return c;
            }
            ENDHLSL
        }
    }

    FallBack Off
}
