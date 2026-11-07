using System;
using System.IO;
using UnityEditor;
using UnityEngine;

namespace DinoPark.EditorTools
{
    /// <summary>
    /// Generates the tileable textures the island shaders use (no third-party images):
    /// water normal, foam, waterfall streaks, soft mist sprite, rock detail and the road.
    /// Written once as PNG under <see cref="Folder"/>; delete a file to regenerate it.
    /// </summary>
    public static class ProceduralTextures
    {
        public const string Folder = "Assets/Textures/Environment/Island";

        public static Texture2D WaterNormal => Get("T_WaterNormal", 256, 256, true, (w, h) => NormalFromHeight(w, h, (x, y) => Fbm(x, y, 4, 4, 0.5f, 11), 3.0f));
        public static Texture2D Foam => Get("T_Foam", 256, 256, false, (w, h) => Grey(w, h, (x, y) =>
        {
            float r = 1f - Mathf.Abs(Fbm(x, y, 6, 3, 0.55f, 23) * 2f - 1f);
            float blobs = Fbm(x, y, 3, 3, 0.5f, 31);
            return Mathf.Clamp01(Mathf.Pow(r, 5f) * 1.3f + Mathf.SmoothStep(0.55f, 0.8f, blobs) * 0.6f);
        }));
        public static Texture2D Streaks => Get("T_FallStreaks", 128, 256, false, (w, h) => Grey(w, h, (x, y) =>
        {
            float n = Noise2(x * 16f, y * 3f, 16, 3, 41) * 0.65f + Noise2(x * 32f, y * 6f, 32, 6, 43) * 0.35f;
            return Mathf.Clamp01(Mathf.SmoothStep(0.35f, 0.8f, n) * 1.1f);
        }));
        public static Texture2D Mist => Get("T_MistSprite", 128, 128, false, (w, h) =>
        {
            var px = new Color[w * h];
            for (int j = 0; j < h; j++)
            for (int i = 0; i < w; i++)
            {
                float u = (i + 0.5f) / w, v = (j + 0.5f) / h;
                float d = Vector2.Distance(new Vector2(u, v), new Vector2(0.5f, 0.5f)) * 2f;
                float n = Fbm(u, v, 4, 4, 0.55f, 53);
                float a = Mathf.Clamp01((1f - d) * 1.4f) * Mathf.SmoothStep(0.25f, 0.75f, n + (1f - d) * 0.35f);
                px[j * w + i] = new Color(1f, 1f, 1f, a * a);
            }
            return px;
        }, alpha: true, clamp: true);
        public static Texture2D RockDetail => Get("T_RockDetail", 512, 512, false, (w, h) => Grey(w, h, (x, y) =>
        {
            float n = Fbm(x, y, 8, 5, 0.55f, 61);
            float cracks = 1f - Mathf.Abs(Fbm(x, y, 5, 3, 0.5f, 67) * 2f - 1f);
            float c = Mathf.SmoothStep(0.88f, 1f, cracks);
            return Mathf.Clamp01(0.5f + (n - 0.5f) * 0.9f - c * 0.35f);
        }));
        public static Texture2D Road => Get("T_Road", 128, 512, false, (w, h) =>
        {
            var px = new Color[w * h];
            for (int j = 0; j < h; j++)
            for (int i = 0; i < w; i++)
            {
                float u = (i + 0.5f) / w, v = (j + 0.5f) / h;
                float n = Fbm(u * 4f, v, 8, 32, 0.6f, 71);
                Color asphalt = Color.Lerp(new Color(0.20f, 0.21f, 0.22f), new Color(0.32f, 0.32f, 0.31f), n);
                bool edge = (u > 0.035f && u < 0.06f) || (u > 0.94f && u < 0.965f);
                bool centre = Mathf.Abs(u - 0.5f) < 0.018f && Mathf.Repeat(v * 4f, 1f) < 0.55f;
                bool kerb = u < 0.025f || u > 0.975f;
                Color c = asphalt;
                if (edge) c = new Color(0.93f, 0.91f, 0.85f);
                if (centre) c = new Color(0.95f, 0.72f, 0.29f);   // brass gold #F2B84B
                if (kerb) c = new Color(0.86f, 0.83f, 0.76f);
                px[j * w + i] = c;
            }
            return px;
        });

        // ------------------------------------------------------------------ texture asset plumbing
        private static Texture2D Get(string name, int w, int h, bool normalMap, Func<int, int, Color[]> make, bool alpha = false, bool clamp = false)
        {
            string path = $"{Folder}/{name}.png";
            var tex = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (tex != null) return tex;

            EnsureFolder(Folder);
            var t = new Texture2D(w, h, TextureFormat.RGBA32, false, true);
            t.SetPixels(make(w, h));
            t.Apply();
            File.WriteAllBytes(Path.Combine(Directory.GetCurrentDirectory(), path), t.EncodeToPNG());
            UnityEngine.Object.DestroyImmediate(t);
            AssetDatabase.ImportAsset(path, ImportAssetOptions.ForceSynchronousImport);
            var ti = (TextureImporter)AssetImporter.GetAtPath(path);
            ti.textureType = normalMap ? TextureImporterType.NormalMap : TextureImporterType.Default;
            ti.sRGBTexture = !normalMap && name == "T_Road";
            ti.alphaSource = alpha ? TextureImporterAlphaSource.FromInput : TextureImporterAlphaSource.None;
            ti.alphaIsTransparency = alpha;
            ti.wrapMode = clamp ? TextureWrapMode.Clamp : TextureWrapMode.Repeat;
            ti.mipmapEnabled = true;
            ti.maxTextureSize = 512;
            ti.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        private static Color[] Grey(int w, int h, Func<float, float, float> f)
        {
            var px = new Color[w * h];
            for (int j = 0; j < h; j++)
            for (int i = 0; i < w; i++)
            {
                float g = f((i + 0.5f) / w, (j + 0.5f) / h);
                px[j * w + i] = new Color(g, g, g, 1f);
            }
            return px;
        }

        private static Color[] NormalFromHeight(int w, int h, Func<float, float, float> height, float strength)
        {
            var hs = new float[w * h];
            for (int j = 0; j < h; j++)
            for (int i = 0; i < w; i++)
                hs[j * w + i] = height((i + 0.5f) / w, (j + 0.5f) / h);
            var px = new Color[w * h];
            for (int j = 0; j < h; j++)
            for (int i = 0; i < w; i++)
            {
                float dx = hs[j * w + (i + 1) % w] - hs[j * w + (i - 1 + w) % w];
                float dy = hs[((j + 1) % h) * w + i] - hs[((j - 1 + h) % h) * w + i];
                var n = new Vector3(-dx * strength * w / 64f, -dy * strength * h / 64f, 1f).normalized;
                px[j * w + i] = new Color(n.x * 0.5f + 0.5f, n.y * 0.5f + 0.5f, n.z * 0.5f + 0.5f, 1f);
            }
            return px;
        }

        // ------------------------------------------------------------------ periodic gradient noise
        /// <summary>Tileable fBm in 0..1 over the unit square; base period = cells per tile.</summary>
        public static float Fbm(float x, float y, int octaves, int period, float gain, int seed)
        {
            float sum = 0f, amp = 0.5f, norm = 0f;
            int p = period;
            for (int o = 0; o < octaves; o++)
            {
                sum += amp * Noise2(x * p, y * p, p, p, seed + o * 17);
                norm += amp;
                amp *= gain;
                p *= 2;
            }
            return sum / norm;
        }

        /// <summary>Periodic gradient noise in 0..1 with periods px, py (in lattice cells).</summary>
        public static float Noise2(float x, float y, int px, int py, int seed)
        {
            int x0 = Mathf.FloorToInt(x), y0 = Mathf.FloorToInt(y);
            float fx = x - x0, fy = y - y0;
            float u = fx * fx * fx * (fx * (fx * 6f - 15f) + 10f);
            float v = fy * fy * fy * (fy * (fy * 6f - 15f) + 10f);
            float n00 = Grad(x0, y0, px, py, seed, fx, fy);
            float n10 = Grad(x0 + 1, y0, px, py, seed, fx - 1f, fy);
            float n01 = Grad(x0, y0 + 1, px, py, seed, fx, fy - 1f);
            float n11 = Grad(x0 + 1, y0 + 1, px, py, seed, fx - 1f, fy - 1f);
            float n = Mathf.Lerp(Mathf.Lerp(n00, n10, u), Mathf.Lerp(n01, n11, u), v);
            return Mathf.Clamp01(n * 0.75f + 0.5f);
        }

        private static float Grad(int ix, int iy, int px, int py, int seed, float dx, float dy)
        {
            ix = ((ix % px) + px) % px;
            iy = ((iy % py) + py) % py;
            uint hsh = (uint)(ix * 374761393 + iy * 668265263 + seed * 982451653);
            hsh = (hsh ^ (hsh >> 13)) * 1274126177u;
            float a = (hsh & 0xffff) / 65535f * Mathf.PI * 2f;
            return Mathf.Cos(a) * dx + Mathf.Sin(a) * dy;
        }

        /// <summary>Non-periodic value in 0..1 for world-space shapes (mountains, cliffs).</summary>
        public static float WorldFbm(float x, float y, int octaves, float scale, int seed)
        {
            float sum = 0f, amp = 0.5f, norm = 0f, f = scale;
            for (int o = 0; o < octaves; o++)
            {
                sum += amp * Noise2(x * f + seed * 13.7f, y * f - seed * 7.3f, 1 << 20, 1 << 20, seed + o * 5);
                norm += amp;
                amp *= 0.5f;
                f *= 2f;
            }
            return sum / norm;
        }

        internal static void EnsureFolder(string path)
        {
            if (AssetDatabase.IsValidFolder(path)) return;
            string parent = Path.GetDirectoryName(path)?.Replace('\\', '/');
            if (!string.IsNullOrEmpty(parent)) EnsureFolder(parent);
            AssetDatabase.CreateFolder(parent, Path.GetFileName(path));
        }
    }
}
