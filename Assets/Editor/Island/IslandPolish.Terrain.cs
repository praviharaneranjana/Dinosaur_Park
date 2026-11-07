using System.Collections.Generic;
using System.Linq;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

namespace DinoPark.EditorTools
{
    public static partial class IslandPolish
    {
        /// <summary>Plateau ramp road centre line (island_map_v02 shapes.ramp_road), Unity coords.</summary>
        private static readonly Vector3[] RampRoad =
        {
            B(-39.5f, 30.7f, 1.3f), B(-39.0f, 38.7f, 1.6f), B(-36.4f, 45.6f, 2.5f), B(-30.0f, 52.5f, 7.0f),
            B(-23.9f, 56.9f, 12.0f), B(-21.0f, 57.8f, 15.0f), B(-23.0f, 64.3f, 15.0f), B(-29.4f, 69.4f, 15.0f),
            B(-36.4f, 72.5f, 15.0f),
        };

        private const float RampHalfWidth = 3.0f;
        private const float RampShoulder = 5.0f;
        private const float RoadHalfWidth = 4.2f;
        private const float RoadShoulder = 7.0f;
        private const float EntranceStartZ = -72f;    // plaza edge
        private const float TunnelDepth = 80f;

        // ------------------------------------------------------------------ ramp + entrance road
        private static void FlattenPaths(Ctx ctx)
        {
            Mesh source = AssetDatabase.LoadAllAssetsAtPath(IslandImporter.Root + "/Meshes/ISL2_Ground.fbx").OfType<Mesh>().FirstOrDefault();
            if (source == null) { ctx.Log.Add("Ramp: ground FBX mesh not found"); return; }

            // Make sure the collider holds the original mesh before sampling heights.
            ctx.GroundCollider.sharedMesh = source;
            Physics.SyncTransforms();

            // Ramp: even grade from the river bank up to the plateau, flat across.
            var ramp = Resample(RampRoad, 0.75f);
            float total = 0f;
            var arcs = new List<float> { 0f };
            for (int i = 1; i < ramp.Count; i++) arcs.Add(total += Vector2.Distance(new Vector2(ramp[i - 1].x, ramp[i - 1].z), new Vector2(ramp[i].x, ramp[i].z)));
            float yBottom = GroundY(ctx, ramp[0].x, ramp[0].z, RampRoad[0].y);
            float topArc = arcs[ramp.FindIndex(p => p.y >= 14.99f)];
            float yTop = 15f;
            for (int i = 0; i < ramp.Count; i++)
            {
                float t = Mathf.Clamp01(arcs[i] / Mathf.Max(topArc, 1f));
                float y = Mathf.Lerp(yBottom, yTop, Mathf.SmoothStep(0f, 1f, Mathf.SmoothStep(0f, 1f, t) * 0.35f + t * 0.65f));
                ramp[i] = new Vector3(ramp[i].x, y, ramp[i].z);
            }
            SmoothHeights(ramp, 3, 2);

            // Entrance road: tunnel end -> plaza along x = 0 (island_map roads[0]).
            ctx.PortalZ = -152f;
            var road = new List<Vector3>();
            for (float z = ctx.PortalZ - TunnelDepth; z <= EntranceStartZ + 0.01f; z += 2f) road.Add(new Vector3(0f, 0f, z));
            float apronRaw = GroundY(ctx, 0f, -146f, 1f);
            for (int i = 0; i < road.Count; i++)
            {
                float z = road[i].z;
                float y = z <= -146f ? apronRaw : GroundY(ctx, 0f, z, apronRaw);
                road[i] = new Vector3(0f, y, z);
            }
            SmoothHeights(road, 8, 3);
            ctx.ApronY = road.First(p => p.z >= ctx.PortalZ).y;
            for (int i = 0; i < road.Count; i++)
                if (road[i].z < ctx.PortalZ + 6f) road[i] = new Vector3(0f, ctx.ApronY, road[i].z);
            ctx.EntranceProfile = road;

            // Edit a copy of the ground mesh in world space.
            Transform gt = ctx.Ground.transform;
            Mesh mesh = Object.Instantiate(source);
            Vector3[] v = mesh.vertices;
            int changed = 0;
            for (int i = 0; i < v.Length; i++)
            {
                Vector3 w = gt.TransformPoint(v[i]);
                float y0 = w.y, y = y0;
                y = Flatten(w, y, ramp, RampHalfWidth, RampShoulder);
                y = Flatten(w, y, road, RoadHalfWidth, RoadShoulder);
                if (!Mathf.Approximately(y, y0))
                {
                    w.y = y;
                    v[i] = gt.InverseTransformPoint(w);
                    changed++;
                }
            }
            mesh.vertices = v;
            mesh.RecalculateNormals();
            mesh.RecalculateBounds();
            mesh = SaveMesh(mesh, "ISL2_Ground_Polished");
            ctx.Ground.GetComponent<MeshFilter>().sharedMesh = mesh;
            ctx.GroundCollider.sharedMesh = mesh;
            Physics.SyncTransforms();

            // Nothing may stand on the ramp or the road.
            int hidden = 0;
            foreach (string group in new[] { "Props", "Plants" })
            {
                Transform g = ctx.Island.Find(group);
                if (g == null) continue;
                foreach (Transform child in g)
                {
                    var r = child.GetComponent<Renderer>();
                    if (r == null) continue;
                    Vector3 c = r.bounds.center;
                    float pad = Mathf.Min(r.bounds.extents.x, r.bounds.extents.z) * 0.5f;
                    if (DistToPath(c, ramp, out _, out _) < RampHalfWidth + 0.8f + pad ||
                        DistToPath(c, road, out _, out _) < RoadHalfWidth + 1.0f + pad)
                    {
                        child.gameObject.SetActive(false);
                        hidden++;
                    }
                }
            }
            ctx.Log.Add($"Ramp/road: ground {yBottom:F1}->{yTop:F1} m over {topArc:F0} m, {changed} ground vertices moved, {hidden} props/plants cleared");
        }

        private static float Flatten(Vector3 w, float y, List<Vector3> path, float halfWidth, float shoulder)
        {
            float d = DistToPath(w, path, out _, out float target);
            if (d >= halfWidth + shoulder) return y;
            if (d <= halfWidth) return target;
            float k = Mathf.SmoothStep(0f, 1f, (d - halfWidth) / shoulder);
            return Mathf.Lerp(target, y, k);
        }

        // ------------------------------------------------------------------ plateau cliff
        private const float CliffIso = 11f;
        private const float CliffRes = 1f;

        /// <summary>
        /// Replaces the Blender cliff skirt with a layered rock wall that follows the real plateau rim:
        /// the rim is the iso-height contour of the ground, every column of the wall hugs the ground
        /// slope just outside it, with sandstone-like beds, ledges and vertical joint blocks.
        /// </summary>
        private static void BuildCliff(Ctx ctx)
        {
            GameObject oldCliff = Find(ctx.Island, "Terrain/TRN5_CliffFace_Plateau");

            // Height grid over the plateau.
            float x0 = -128f, z0 = 36f;
            int nx = 176, nz = 94;
            var h = new float[nx * nz];
            for (int j = 0; j < nz; j++)
            for (int i = 0; i < nx; i++)
                h[j * nx + i] = GroundY(ctx, x0 + i * CliffRes, z0 + j * CliffRes, -12f);

            float H(float x, float z)
            {
                float fi = (x - x0) / CliffRes, fj = (z - z0) / CliffRes;
                if (fi < 0 || fj < 0 || fi >= nx - 1 || fj >= nz - 1) return GroundY(ctx, x, z, -12f);
                int i = (int)fi, j = (int)fj;
                float u = fi - i, w = fj - j;
                float a = h[j * nx + i], b = h[j * nx + i + 1], c = h[(j + 1) * nx + i], d = h[(j + 1) * nx + i + 1];
                return Mathf.Lerp(Mathf.Lerp(a, b, u), Mathf.Lerp(c, d, u), w);
            }

            var chains = Contour(h, nx, nz, x0, z0, CliffRes, CliffIso);
            var verts = new List<Vector3>();
            var cols = new List<Color>();
            var tris = new List<int>();
            const int rows = 18;
            int columns = 0;
            float chainSeed = 0f;
            foreach (List<Vector2> raw in chains)
            {
                List<Vector2> chain = ResampleXZ(raw, 1.4f);
                if (PathLength(chain) < 14f) continue;
                for (int s = 0; s < 2; s++) chain = SmoothXZ(chain);
                bool closed = Vector2.Distance(raw[0], raw[raw.Count - 1]) < 2f;

                int startVert = -1, prevVert = -1;
                float arc = chainSeed;
                for (int k = 0; k < chain.Count; k++)
                {
                    Vector2 p = chain[k];
                    Vector2 tan = (chain[Mathf.Min(k + 1, chain.Count - 1)] - chain[Mathf.Max(k - 1, 0)]).normalized;
                    Vector2 n = new Vector2(tan.y, -tan.x);
                    if (H(p.x + n.x * 2f, p.y + n.y * 2f) > H(p.x - n.x * 2f, p.y - n.y * 2f)) n = -n;   // n points downhill
                    if (k > 0) arc += Vector2.Distance(chain[k - 1], p);

                    bool gap = DistToPath(new Vector3(p.x, 0, p.y), RampRoad, out _, out _) < RampHalfWidth + 0.6f;
                    float topY = H(p.x - n.x * 3f, p.y - n.y * 3f) + 0.3f;
                    if (topY < CliffIso + 1.5f) gap = true;
                    if (gap) { prevVert = -1; continue; }

                    // foot: where the slope flattens out, the sea floor starts, or the ramp road begins
                    float foot = 2f, last = H(p.x, p.y);
                    bool onRoad = false;
                    for (float sd = 0.5f; sd <= 30f; sd += 0.5f)
                    {
                        float qx = p.x + n.x * sd, qz = p.y + n.y * sd;
                        float hs = H(qx, qz);
                        if (DistToPath(new Vector3(qx, 0, qz), RampRoad, out _, out _) < RampHalfWidth + 0.4f) { onRoad = true; break; }
                        foot = sd;
                        if (hs < SeaLevel - 2.5f) break;
                        if (hs < topY - 6f && last - hs < 0.15f) break;
                        last = hs;
                    }
                    float footY = H(p.x + n.x * foot, p.y + n.y * foot) - (onRoad ? 0.15f : 1.5f);

                    float block = (Hash(Mathf.FloorToInt(arc / 3.6f), 17) - 0.5f) * 0.9f;
                    float bedShift = Hash(Mathf.FloorToInt(arc / 11f), 29) * 0.8f;
                    int colStart = verts.Count;
                    float prevOut = -1f;
                    for (int r = 0; r <= rows; r++)
                    {
                        float t = r / (float)rows;
                        float y = Mathf.Lerp(topY, footY, t);
                        // first distance outward where the ground is below this height
                        float xg = foot;
                        for (float sd = -3f; sd <= foot; sd += 0.25f)
                            if (H(p.x + n.x * sd, p.y + n.y * sd) < y) { xg = sd; break; }
                        float band = Mathf.Repeat(y / 1.8f + bedShift, 1f);
                        float ledge = Mathf.SmoothStep(0.72f, 0.95f, band) * 0.6f;
                        float grain = (ProceduralTextures.WorldFbm(arc * 0.35f, y * 0.5f, 3, 1f, 3) - 0.5f) * 0.6f;
                        float outward = xg + 0.55f + Mathf.Max(ledge + block + grain, -0.25f);
                        if (r == rows) outward = onRoad ? foot - 0.1f : foot + 0.8f;
                        if (onRoad) outward = Mathf.Min(outward, foot);
                        if (prevOut >= 0f) outward = Mathf.Max(outward, prevOut - 0.45f);
                        prevOut = outward;
                        verts.Add(new Vector3(p.x + n.x * outward, y, p.y + n.y * outward));

                        float relief = Mathf.Clamp01((ledge + block + grain + 0.4f) / 1.4f);
                        var rock = new Color(0.60f, 0.54f, 0.45f) * (0.72f + 0.42f * relief);
                        if (r <= 1) rock = Color.Lerp(rock, new Color(0.42f, 0.50f, 0.28f), 0.55f);
                        if (y < SeaLevel + 1.2f) rock *= 0.62f;                      // wet foot
                        rock.a = 1f;
                        cols.Add(rock);
                    }
                    if (prevVert >= 0)
                    {
                        for (int r = 0; r < rows; r++)
                        {
                            int a = prevVert + r, b = colStart + r, c = colStart + r + 1, d = prevVert + r + 1;
                            tris.AddRange(new[] { a, c, b, a, d, c });
                        }
                    }
                    if (startVert < 0) startVert = colStart;
                    prevVert = colStart;
                    columns++;
                }
                if (closed && prevVert >= 0 && startVert >= 0 && prevVert != startVert)
                {
                    for (int r = 0; r < rows; r++)
                    {
                        int a = prevVert + r, b = startVert + r, c = startVert + r + 1, d = prevVert + r + 1;
                        tris.AddRange(new[] { a, c, b, a, d, c });
                    }
                }
                chainSeed += 1000f;
            }

            if (tris.Count == 0)
            {
                ctx.Log.Add("Cliff: no rim found, kept the Blender cliff");
                return;
            }

            var mesh = new Mesh { indexFormat = IndexFormat.UInt32 };
            mesh.SetVertices(verts);
            mesh.SetColors(cols);
            mesh.SetTriangles(tris, 0);
            mesh.RecalculateNormals();
            // Faces must point away from the plateau: flip if the first face points uphill.
            Vector3[] nrm = mesh.normals;
            float outwardVotes = 0f;
            for (int i = 0; i < Mathf.Min(verts.Count, 4000); i += 7)
            {
                Vector3 nn = nrm[i];
                float up = H(verts[i].x + nn.x, verts[i].z + nn.z) - H(verts[i].x - nn.x, verts[i].z - nn.z);
                outwardVotes += up < 0 ? 1 : -1;
            }
            if (outwardVotes < 0)
            {
                for (int i = 0; i < tris.Count; i += 3) (tris[i + 1], tris[i + 2]) = (tris[i + 2], tris[i + 1]);
                mesh.SetTriangles(tris, 0);
                mesh.RecalculateNormals();
            }
            mesh.RecalculateBounds();
            mesh = SaveMesh(mesh, "Cliff_Plateau");

            Material rockMat = Mat("M_Cliff_Rock", LitShader, m =>
            {
                Opaque(m, Color.white, 0.12f);
                RockDetail(m, 0.9f, 0.4f, 0.55f);
                m.SetFloat("_DetailTiling", 0.22f);
                m.SetFloat("_StrataHeight", 1.8f);
                m.SetColor("_MossColor", new Color(0.30f, 0.45f, 0.17f));
                m.SetFloat("_Cull", (float)CullMode.Off);
            });
            MeshObject("Cliff_Plateau", Group(ctx.Polish, "Terrain"), mesh, new[] { rockMat }, true);
            if (oldCliff != null) oldCliff.SetActive(false);
            ctx.Log.Add($"Cliff: {chains.Count} rim chains, {columns} columns, {mesh.vertexCount} verts (Blender cliff disabled)");
        }

        // ------------------------------------------------------------------ contour helpers
        /// <summary>Marching squares on a height grid; returns polylines (XZ) of the iso contour.</summary>
        private static List<List<Vector2>> Contour(float[] h, int nx, int nz, float x0, float z0, float res, float iso)
        {
            long HId(int i, int j) => ((long)j * nx + i) * 2;
            long VId(int i, int j) => ((long)j * nx + i) * 2 + 1;
            var points = new Dictionary<long, Vector2>();
            Vector2 P(int ia, int ja, int ib, int jb)
            {
                float a = h[ja * nx + ia], b = h[jb * nx + ib];
                float t = Mathf.Clamp01((iso - a) / (b - a));
                return new Vector2(x0 + Mathf.Lerp(ia, ib, t) * res, z0 + Mathf.Lerp(ja, jb, t) * res);
            }
            var segs = new List<(long, long)>();
            for (int j = 0; j < nz - 1; j++)
            for (int i = 0; i < nx - 1; i++)
            {
                int c = 0;
                if (h[j * nx + i] > iso) c |= 1;
                if (h[j * nx + i + 1] > iso) c |= 2;
                if (h[(j + 1) * nx + i + 1] > iso) c |= 4;
                if (h[(j + 1) * nx + i] > iso) c |= 8;
                if (c == 0 || c == 15) continue;
                long e0 = HId(i, j), e1 = VId(i + 1, j), e2 = HId(i, j + 1), e3 = VId(i, j);
                void Seg(long a, long b) => segs.Add((a, b));
                switch (c)
                {
                    case 1: case 14: Seg(e3, e0); break;
                    case 2: case 13: Seg(e0, e1); break;
                    case 3: case 12: Seg(e3, e1); break;
                    case 4: case 11: Seg(e1, e2); break;
                    case 6: case 9: Seg(e0, e2); break;
                    case 7: case 8: Seg(e3, e2); break;
                    case 5: Seg(e3, e0); Seg(e1, e2); break;
                    case 10: Seg(e0, e1); Seg(e2, e3); break;
                }
                points[e0] = P(i, j, i + 1, j);
                points[e1] = P(i + 1, j, i + 1, j + 1);
                points[e2] = P(i, j + 1, i + 1, j + 1);
                points[e3] = P(i, j, i, j + 1);
            }

            var byEdge = new Dictionary<long, List<int>>();
            for (int s = 0; s < segs.Count; s++)
            {
                foreach (long e in new[] { segs[s].Item1, segs[s].Item2 })
                {
                    if (!byEdge.TryGetValue(e, out var l)) byEdge[e] = l = new List<int>();
                    l.Add(s);
                }
            }
            var used = new bool[segs.Count];
            var chains = new List<List<Vector2>>();
            IEnumerable<int> starts = Enumerable.Range(0, segs.Count)
                .OrderBy(s => (byEdge[segs[s].Item1].Count == 1 || byEdge[segs[s].Item2].Count == 1) ? 0 : 1);
            foreach (int s0 in starts)
            {
                if (used[s0]) continue;
                long startEdge = byEdge[segs[s0].Item1].Count == 1 ? segs[s0].Item1 : (byEdge[segs[s0].Item2].Count == 1 ? segs[s0].Item2 : segs[s0].Item1);
                var chain = new List<Vector2> { points[startEdge] };
                long cur = startEdge;
                int seg = s0;
                while (seg >= 0 && !used[seg])
                {
                    used[seg] = true;
                    long next = segs[seg].Item1 == cur ? segs[seg].Item2 : segs[seg].Item1;
                    chain.Add(points[next]);
                    cur = next;
                    seg = byEdge[cur].FirstOrDefault(x => !used[x]);
                    if (seg == 0 && used[0]) seg = -1;
                    if (byEdge[cur].All(x => used[x])) seg = -1;
                }
                if (chain.Count > 3) chains.Add(chain);
            }
            return chains;
        }

        private static float PathLength(List<Vector2> p)
        {
            float l = 0f;
            for (int i = 1; i < p.Count; i++) l += Vector2.Distance(p[i - 1], p[i]);
            return l;
        }

        private static List<Vector2> ResampleXZ(List<Vector2> p, float step)
        {
            var v3 = p.Select(q => new Vector3(q.x, 0, q.y)).ToList();
            return Resample(v3, step).Select(q => new Vector2(q.x, q.z)).ToList();
        }

        private static List<Vector2> SmoothXZ(List<Vector2> p)
        {
            var o = new List<Vector2>(p);
            for (int i = 1; i < p.Count - 1; i++) o[i] = (p[i - 1] + p[i] * 2f + p[i + 1]) * 0.25f;
            return o;
        }
    }
}
