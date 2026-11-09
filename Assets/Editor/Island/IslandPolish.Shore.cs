using System.Collections.Generic;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;

namespace DinoPark.EditorTools
{
    public static partial class IslandPolish
    {
        private const string SwashShader = "DinoPark/Environment/Swash";
        private const float ShoreCell = 1f;
        private const float SwashHeightRange = 1.8f, SwashHeightOffset = 0.3f;

        /// <summary>
        /// Moving water on every shore that touches the open sea: a 1 m sheet draped 4 cm over the ground
        /// from just under sea level up the beach, which the Swash shader animates (waves run up the sand
        /// and drain back, foam at the front, wet sand behind). Where the coast is a cliff, breaking-wave
        /// spray bursts against the rock. Inland water (river banks, ponds, swamp) is left alone.
        /// </summary>
        private static void BuildShore(Ctx ctx)
        {
            var ground = new List<Collider> { ctx.GroundCollider };
            foreach (string path in new[] { "Land Side/Mainland", "Terrain/Cliff_Plateau" })
            {
                Transform t = ctx.Polish.Find(path);
                if (t != null && t.GetComponent<Collider>() != null) ground.Add(t.GetComponent<Collider>());
            }
            float Height(float x, float z, out Vector3 normal)
            {
                float best = float.NegativeInfinity;
                normal = Vector3.up;
                var ray = new Ray(new Vector3(x, 300f, z), Vector3.down);
                foreach (Collider c in ground)
                    if (c.Raycast(ray, out RaycastHit hit, 600f) && hit.point.y > best) { best = hit.point.y; normal = hit.normal; }
                return float.IsNegativeInfinity(best) ? -40f : best;
            }

            const float x0 = -300f, x1 = 300f, z0 = -260f, z1 = 230f;
            int nx = Mathf.RoundToInt((x1 - x0) / ShoreCell) + 1, nz = Mathf.RoundToInt((z1 - z0) / ShoreCell) + 1;
            var h = new float[nx * nz];
            var nrm = new Vector3[nx * nz];
            for (int j = 0; j < nz; j++)
            for (int i = 0; i < nx; i++)
            {
                int id = j * nx + i;
                h[id] = Height(x0 + i * ShoreCell, z0 + j * ShoreCell, out nrm[id]) - SeaLevel;
            }

            // open sea: water cells connected to the border
            var sea = new bool[nx * nz];
            var q = new Queue<int>();
            void Seed(int id) { if (!sea[id] && h[id] < -0.05f) { sea[id] = true; q.Enqueue(id); } }
            for (int i = 0; i < nx; i++) { Seed(i); Seed((nz - 1) * nx + i); }
            for (int j = 0; j < nz; j++) { Seed(j * nx); Seed(j * nx + nx - 1); }
            while (q.Count > 0)
            {
                int id = q.Dequeue(), i = id % nx, j = id / nx;
                if (i > 0) Seed(id - 1);
                if (i < nx - 1) Seed(id + 1);
                if (j > 0) Seed(id - nx);
                if (j < nz - 1) Seed(id + nx);
            }

            // steps inland from the open sea (breadth first over land below 1.6 m), capped at 9 cells
            var dist = new int[nx * nz];
            for (int id = 0; id < dist.Length; id++) dist[id] = sea[id] ? 0 : int.MaxValue;
            for (int id = 0; id < dist.Length; id++) if (sea[id]) q.Enqueue(id);
            while (q.Count > 0)
            {
                int id = q.Dequeue(), i = id % nx, j = id / nx;
                if (dist[id] >= 9) continue;
                foreach (int nb in new[] { i > 0 ? id - 1 : -1, i < nx - 1 ? id + 1 : -1, j > 0 ? id - nx : -1, j < nz - 1 ? id + nx : -1 })
                {
                    if (nb < 0 || dist[nb] != int.MaxValue || h[nb] > 1.6f) continue;
                    dist[nb] = dist[id] + 1;
                    q.Enqueue(nb);
                }
            }

            // the river is fresh water: no surf up its channel
            var riverEnd = RiverLine[RiverLine.Length - 1];
            bool InRiver(float x, float z)
            {
                var p = new Vector3(x, 0f, z);
                float d = DistToPath(p, RiverLine, out float arc, out _);
                return d < 14f && Vector2.Distance(new Vector2(x, z), new Vector2(riverEnd.x, riverEnd.z)) > 22f;
            }

            var index = new int[nx * nz];
            var verts = new List<Vector3>();
            var cols = new List<Color>();
            var normals = new List<Vector3>();
            for (int j = 0; j < nz; j++)
            for (int i = 0; i < nx; i++)
            {
                int id = j * nx + i;
                index[id] = -1;
                bool keep = (sea[id] && h[id] > -1.6f) || (!sea[id] && dist[id] <= 9);
                float x = x0 + i * ShoreCell, z = z0 + j * ShoreCell;
                if (!keep || InRiver(x, z)) continue;
                float edge = sea[id] ? 1f : 1f - Mathf.SmoothStep(0f, 1f, (dist[id] - 6f) / 3f);
                index[id] = verts.Count;
                verts.Add(new Vector3(x, h[id] + SeaLevel + 0.04f, z));
                normals.Add(nrm[id]);
                cols.Add(new Color(Mathf.Clamp01((h[id] + SwashHeightOffset) / SwashHeightRange), 0f, 0f, edge));
            }
            var tris = new List<int>();
            for (int j = 0; j < nz - 1; j++)
            for (int i = 0; i < nx - 1; i++)
            {
                int a = index[j * nx + i], b = index[j * nx + i + 1], c = index[(j + 1) * nx + i], d = index[(j + 1) * nx + i + 1];
                if (a >= 0 && b >= 0 && c >= 0) tris.AddRange(new[] { a, c, b });
                if (b >= 0 && c >= 0 && d >= 0) tris.AddRange(new[] { b, c, d });
            }
            var mesh = new Mesh { indexFormat = IndexFormat.UInt32 };
            mesh.SetVertices(verts);
            mesh.SetNormals(normals);
            mesh.SetColors(cols);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateBounds();
            Material swash = Mat("M_Water_Swash", SwashShader, m =>
            {
                m.SetTexture("_FoamTex", ProceduralTextures.Foam);
                m.SetFloat("_HeightRange", SwashHeightRange);
                m.SetFloat("_HeightOffset", SwashHeightOffset);
                m.SetFloat("_RunUp", 0.5f);
                m.SetFloat("_Period", 7f);
                m.renderQueue = (int)RenderQueue.Transparent - 15;
            });
            Transform water = ctx.Polish.Find("Water") ?? Group(ctx.Polish, "Water");
            MeshObject("Beach_Swash", water, SaveMesh(mesh, "Beach_Swash"), new[] { swash }, false, ShadowCastingMode.Off)
                .GetComponent<MeshRenderer>().receiveShadows = false;

            int surf = BuildCliffSurf(ctx, water, h, sea, nx, nz, x0, z0);
            ctx.Log.Add($"Shore: swash sheet {verts.Count} verts / {tris.Count / 3} tris on sea-facing shores, {surf} cliff surf points");
        }

        /// <summary>Spray bursts where open sea meets ground that rises 3.5 m within 5 m: waves breaking on rock.</summary>
        private static int BuildCliffSurf(Ctx ctx, Transform parent, float[] h, bool[] sea, int nx, int nz, float x0, float z0)
        {
            var spots = new List<(Vector3 at, Vector3 outward)>();
            for (int j = 5; j < nz - 5; j++)
            for (int i = 5; i < nx - 5; i++)
            {
                int id = j * nx + i;
                if (spots.Count >= 16 || !sea[id] || h[id] < -1.2f) continue;
                // shallow sea cell next to land
                float maxNear = float.NegativeInfinity;
                Vector2 toHigh = Vector2.zero;
                for (int dj = -5; dj <= 5; dj++)
                for (int di = -5; di <= 5; di++)
                {
                    float hh = h[(j + dj) * nx + i + di];
                    if (hh > maxNear) { maxNear = hh; toHigh = new Vector2(di, dj); }
                }
                if (maxNear < 3.5f) continue;
                Vector3 at = new Vector3(x0 + i * ShoreCell, SeaLevel + 0.1f, z0 + j * ShoreCell);
                if (spots.Any(s => (s.at - at).sqrMagnitude < 24f * 24f)) continue;
                Vector3 outward = -new Vector3(toHigh.x, 0f, toHigh.y).normalized;
                spots.Add((at, outward));
            }
            if (spots.Count == 0) return 0;

            Material spray = Mat("M_Surf_Spray", ParticleShader, m =>
            {
                m.SetTexture("_BaseMap", ProceduralTextures.Mist);
                m.SetColor("_BaseColor", new Color(1f, 1f, 1f, 0.75f));
                m.SetFloat("_SoftDistance", 1.0f);
                m.renderQueue = (int)RenderQueue.Transparent + 10;
            });
            Transform group = Group(parent, "Cliff Surf");
            var rng = new System.Random(77);
            foreach (var s in spots)
            {
                var go = new GameObject("Surf");
                go.transform.SetParent(group, false);
                go.transform.position = s.at - s.outward * 0.5f;
                go.transform.rotation = Quaternion.LookRotation(s.outward, Vector3.up);
                var ps = go.AddComponent<ParticleSystem>();
                ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);
                var main = ps.main;
                main.loop = true;
                main.playOnAwake = true;
                main.duration = 4f + (float)rng.NextDouble() * 3f;           // a wave every 4-7 s, out of step
                main.startDelay = (float)rng.NextDouble() * 4f;
                main.simulationSpace = ParticleSystemSimulationSpace.World;
                main.startLifetime = new ParticleSystem.MinMaxCurve(1.2f, 2.2f);
                main.startSpeed = new ParticleSystem.MinMaxCurve(4f, 8.5f);
                main.startSize = new ParticleSystem.MinMaxCurve(1.6f, 4f);
                main.startRotation = new ParticleSystem.MinMaxCurve(0f, Mathf.PI * 2f);
                main.gravityModifier = 0.9f;
                main.maxParticles = 40;
                var emission = ps.emission;
                emission.rateOverTime = 0f;
                emission.SetBursts(new[] { new ParticleSystem.Burst(0f, new ParticleSystem.MinMaxCurve(14f, 24f)) });
                var shape = ps.shape;
                shape.shapeType = ParticleSystemShapeType.Cone;
                shape.angle = 28f;
                shape.radius = 2.5f;
                shape.rotation = new Vector3(-62f, 0f, 0f);                    // up and a little out to sea
                var col = ps.colorOverLifetime;
                col.enabled = true;
                var g = new Gradient();
                g.SetKeys(new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) },
                    new[] { new GradientAlphaKey(0f, 0f), new GradientAlphaKey(1f, 0.1f), new GradientAlphaKey(0.5f, 0.6f), new GradientAlphaKey(0f, 1f) });
                col.color = g;
                var size = ps.sizeOverLifetime;
                size.enabled = true;
                size.size = new ParticleSystem.MinMaxCurve(1f, AnimationCurve.Linear(0f, 0.5f, 1f, 1.8f));
                var r = go.GetComponent<ParticleSystemRenderer>();
                r.sharedMaterial = spray;
                r.renderMode = ParticleSystemRenderMode.Billboard;
                r.shadowCastingMode = ShadowCastingMode.Off;
                r.receiveShadows = false;
                ps.Play();
            }
            return spots.Count;
        }
    }
}
