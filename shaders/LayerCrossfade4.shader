Shader "MGShader/LayerCrossfade4"
{
	Properties
	{
		_Secondary ("Secondary", 2D) = "white" { }
		_Primary ("Primary", 2D) = "white" { }
		_Range ("Range", Range(0,1)) = 1
		_Alpha ("Alpha", Range(0,1)) = 1
	}
	SubShader
	{
		Tags { "QUEUE"="Transparent" "IGNOREPROJECTOR"="true" "RenderType"="Transparent" }
		Pass
		{
			Name "FORWARDBASE"
			Tags { "LIGHTMODE"="ForwardBase" "QUEUE"="Transparent" "IGNOREPROJECTOR"="true" "SHADOWSUPPORT"="true" "RenderType"="Transparent" }
			ZWrite Off
			Blend SrcAlpha OneMinusSrcAlpha

			CGPROGRAM
			#pragma vertex vert
			#pragma fragment frag
			
			#include "UnityCG.cginc"

			struct appdata
			{
				float4 vertex : POSITION;
				float2 uv : TEXCOORD0;
			};

			struct v2f
			{
				float2 uv : TEXCOORD0;
				float4 vertex : SV_POSITION;
			};

			v2f vert (appdata v)
			{
				v2f o;
				o.vertex = mul(UNITY_MATRIX_MVP, v.vertex);
				o.uv = v.uv;
				return o;
			}
			
			sampler2D _Primary;
			sampler2D _Secondary;
			float _Alpha;
			float _Range;

			fixed4 frag (v2f i) : SV_Target
			{
				fixed4 primary = tex2D(_Primary, i.uv);
				fixed4 secondary = tex2D(_Secondary, i.uv);
				float alphaMix = lerp(primary.w, secondary.w, _Range);
				float newRange = secondary.w * _Range / alphaMix;
				fixed3 mixed = lerp(primary, secondary, float3(newRange, newRange, newRange));
				float4 col;
				col.w = _Alpha * alphaMix;
				col.xyz = mixed;
				return col;
			}
			ENDCG
		}
	}
	Fallback "Diffuse"
}
