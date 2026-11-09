using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;

namespace DinoPark.EditorTools
{
    /// <summary>
    /// Lets tools drive the open editor without clicking: write commands (one per line) to
    /// %TEMP%/DinoParkAutomation/command.txt and read results from result.txt and log.txt there.
    /// Commands: refresh | import | polish | play | stop |
    ///           shot &lt;png&gt; [x y z pitch yaw fov]  (no pose = the main camera as it is now).
    /// Editor-only; it never runs in a build.
    /// </summary>
    [InitializeOnLoad]
    public static class DinoParkAutomation
    {
        private const string IslandScene = "Assets/Scenes/Island.unity";
        private static readonly string Dir = Path.Combine(Path.GetTempPath(), "DinoParkAutomation");
        private static double nextPoll;

        static DinoParkAutomation()
        {
            Directory.CreateDirectory(Dir);
            EditorApplication.update += Poll;
            Application.logMessageReceived += OnLog;
            Result($"ready playing={EditorApplication.isPlaying}");
        }

        private static void OnLog(string message, string stack, LogType type)
        {
            if (type == LogType.Log && !message.StartsWith("[DinoPark]")) return;
            string extra = type == LogType.Exception || type == LogType.Error ? "\n" + stack : "";
            File.AppendAllText(Path.Combine(Dir, "log.txt"), $"{DateTime.Now:HH:mm:ss} {type}: {message}{extra}\n");
        }

        private static void Result(string line) =>
            File.AppendAllText(Path.Combine(Dir, "result.txt"), $"{DateTime.Now:HH:mm:ss} {line}\n");

        private static void Poll()
        {
            if (EditorApplication.timeSinceStartup < nextPoll) return;
            nextPoll = EditorApplication.timeSinceStartup + 0.5;
            string file = Path.Combine(Dir, "command.txt");
            if (!File.Exists(file)) return;
            string[] lines;
            try
            {
                lines = File.ReadAllLines(file);
                File.Delete(file);
            }
            catch (IOException) { return; }
            foreach (string raw in lines.Select(l => l.Trim()).Where(l => l.Length > 0)) Run(raw);
        }

        private static void Run(string cmd)
        {
            string[] a = cmd.Split(' ');
            try
            {
                switch (a[0])
                {
                    case "refresh":
                        AssetDatabase.Refresh();
                        break;
                    case "import":
                        SaveIfDirty();
                        IslandImporter.ImportIsland();
                        break;
                    case "polish":
                        SaveIfDirty();
                        Scene scene = SceneManager.GetActiveScene().path == IslandScene
                            ? SceneManager.GetActiveScene()
                            : EditorSceneManager.OpenScene(IslandScene, OpenSceneMode.Single);
                        IslandPolish.Apply(scene);
                        EditorSceneManager.MarkSceneDirty(scene);
                        EditorSceneManager.SaveScene(scene);
                        break;
                    case "play":
                        SaveIfDirty();
                        EditorApplication.isPlaying = true;
                        break;
                    case "stop":
                        EditorApplication.isPlaying = false;
                        break;
                    case "shot":
                        Shot(a);
                        break;
                    case "stats":
                        Stats();
                        break;
                    case "matfloat":   // matfloat <material asset path> <property> <value>
                    {
                        var mat = AssetDatabase.LoadAssetAtPath<Material>(a[1]);
                        if (mat == null) throw new InvalidOperationException("No material " + a[1]);
                        mat.SetFloat(a[2], F(a[3]));
                        EditorUtility.SetDirty(mat);
                        AssetDatabase.SaveAssets();
                        break;
                    }
                    case "pick":   // pick x y z pitch yaw fov px py: renderers whose bounds the ray through pixel (px,py) of a 1600x900 shot hits, nearest first
                    {
                        Quaternion rot = Quaternion.Euler(F(a[4]), F(a[5]), 0f);
                        float fov = F(a[6]) * Mathf.Deg2Rad, aspect = 1600f / 900f;
                        float nx = (F(a[7]) / 1600f) * 2f - 1f, ny = 1f - (F(a[8]) / 900f) * 2f;
                        float th = Mathf.Tan(fov * 0.5f);
                        var ray = new Ray(new Vector3(F(a[1]), F(a[2]), F(a[3])), rot * new Vector3(nx * th * aspect, ny * th, 1f).normalized);
                        var hits = new List<(float d, Renderer r)>();
                        foreach (Renderer r in UnityEngine.Object.FindObjectsByType<Renderer>())
                            if (r.enabled && r.gameObject.activeInHierarchy && r.bounds.IntersectRay(ray, out float d)) hits.Add((d, r));
                        foreach (var h in hits.OrderBy(h => h.d).Take(8))
                            Result($"  hit {h.r.name} parent={h.r.transform.parent?.name} d={h.d:F1} bounds={h.r.bounds.center} size={h.r.bounds.size} mat={h.r.sharedMaterial?.name}");
                        break;
                    }
                    case "active":   // active <exact object name> <0|1>: show/hide every scene object with that name (not saved)
                        foreach (Transform t in UnityEngine.Object.FindObjectsByType<Transform>(FindObjectsInactive.Include))
                            if (t.name == a[1]) t.gameObject.SetActive(a[2] == "1");
                        break;
                    case "inspect":   // inspect <name part>: renderers, materials, shaders, queues
                        foreach (Renderer r in UnityEngine.Object.FindObjectsByType<Renderer>(FindObjectsInactive.Include))
                        {
                            if (!r.name.Contains(a[1])) continue;
                            string mats = string.Join(", ", r.sharedMaterials.Select(m => m == null ? "null" : $"{m.name}[{m.shader.name} q{m.renderQueue}]"));
                            var mf = r.GetComponent<MeshFilter>();
                            Result($"  {r.name} active={r.gameObject.activeInHierarchy} enabled={r.enabled} mesh={(mf ? mf.sharedMesh?.name : "-")} pos={r.bounds.center} mats={mats}");
                        }
                        break;
                    case "ray":   // ray <x> <z>: every collider / renderer bounds hit straight down
                    {
                        float x = F(a[1]), z = F(a[2]);
                        foreach (RaycastHit h in Physics.RaycastAll(new Vector3(x, 300f, z), Vector3.down, 600f).OrderBy(h => -h.point.y))
                            Result($"  collider {h.collider.name} y={h.point.y:F3}");
                        foreach (MeshRenderer r in UnityEngine.Object.FindObjectsByType<MeshRenderer>())
                        {
                            Bounds b = r.bounds;
                            if (x < b.min.x || x > b.max.x || z < b.min.z || z > b.max.z || b.size.y > 3f) continue;
                            if (!r.name.StartsWith("ISL") && !r.name.StartsWith("Water")) continue;
                            Result($"  flat renderer {r.name} y {b.min.y:F3}..{b.max.y:F3}");
                        }
                        break;
                    }
                    case "meshinfo":   // meshinfo <name part>: winding vs normals of meshes on scene renderers
                        foreach (MeshFilter f in UnityEngine.Object.FindObjectsByType<MeshFilter>(FindObjectsInactive.Include))
                        {
                            if (!f.name.Contains(a[1]) || f.sharedMesh == null) continue;
                            Mesh m = f.sharedMesh;
                            Vector3[] v = m.vertices, n = m.normals;
                            int[] t = m.triangles;
                            float up = 0f, windingUp = 0f;
                            for (int i = 0; i < t.Length; i += 3)
                            {
                                Vector3 fn = f.transform.TransformDirection(Vector3.Cross(v[t[i + 1]] - v[t[i]], v[t[i + 2]] - v[t[i]]));
                                windingUp += Mathf.Sign(fn.y);
                            }
                            foreach (Vector3 nn in n) up += Mathf.Sign(f.transform.TransformDirection(nn).y);
                            var c = m.colors;
                            Result($"  {f.name} tris={t.Length / 3} normalsUp={up / Mathf.Max(n.Length, 1):F2} windingUp={windingUp / Mathf.Max(t.Length / 3, 1):F2} colorA avg={(c.Length > 0 ? c.Average(cc => cc.a) : -1):F3} readable={m.isReadable}");
                        }
                        break;
                    case "quality":
                        QualitySettings.SetQualityLevel(Array.IndexOf(QualitySettings.names, a[1]), true);
                        Result("quality now " + QualitySettings.names[QualitySettings.GetQualityLevel()] + " (" + GraphicsSettings.currentRenderPipeline?.name + ")");
                        break;
                    case "build":
                        BuildAndroid(a.Length > 1 && a[1] == "norun");
                        break;
                    case "buildrelease":   // buildrelease <apk path, may contain spaces>
                        BuildAndroid(true, string.Join(" ", a.Skip(1)));
                        break;
                    default:
                        Result("unknown " + cmd);
                        return;
                }
                Result("done " + cmd);
            }
            catch (Exception e)
            {
                Result("fail " + cmd + " :: " + e);
            }
        }

        private static void SaveIfDirty()
        {
            if (EditorApplication.isPlaying) return;
            Scene s = SceneManager.GetActiveScene();
            if (s.isDirty && !string.IsNullOrEmpty(s.path)) EditorSceneManager.SaveScene(s);
        }

        private static void Shot(string[] a)
        {
            string path = a[1];
            Camera cam;
            GameObject temp = null;
            if (a.Length >= 8)
            {
                temp = new GameObject("AutomationCamera") { hideFlags = HideFlags.HideAndDontSave };
                cam = temp.AddComponent<Camera>();
                Camera main = Camera.main;
                if (main != null) { cam.CopyFrom(main); }
                cam.transform.SetPositionAndRotation(
                    new Vector3(F(a[2]), F(a[3]), F(a[4])),
                    Quaternion.Euler(F(a[5]), F(a[6]), 0f));
                cam.fieldOfView = F(a[7]);
                cam.nearClipPlane = 0.3f;
                cam.farClipPlane = 2000f;
            }
            else
            {
                cam = Camera.main;
                if (cam == null) throw new InvalidOperationException("No main camera");
            }

            var rt = new RenderTexture(1600, 900, 24, RenderTextureFormat.ARGB32) { antiAliasing = 4 };
            RenderTexture prevTarget = cam.targetTexture;
            cam.targetTexture = rt;
            cam.Render();
            cam.targetTexture = prevTarget;
            RenderTexture prev = RenderTexture.active;
            RenderTexture.active = rt;
            var tex = new Texture2D(rt.width, rt.height, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, rt.width, rt.height), 0, 0);
            tex.Apply();
            RenderTexture.active = prev;
            Directory.CreateDirectory(Path.GetDirectoryName(path) ?? Dir);
            File.WriteAllBytes(path, tex.EncodeToJPG(88));
            UnityEngine.Object.DestroyImmediate(tex);
            rt.Release();
            UnityEngine.Object.DestroyImmediate(rt);
            if (temp != null) UnityEngine.Object.DestroyImmediate(temp);
        }

        /// <summary>
        /// Rendering cost of what the main camera sees: triangles and renderers inside its frustum, split by
        /// group, counted at the mesh LOD that Unity would pick (distance-culled LODGroups skipped), plus
        /// the editor's own last-frame stats.
        /// </summary>
        private static void Stats()
        {
            Camera cam = Camera.main;
            if (cam == null) throw new InvalidOperationException("No main camera");
            Plane[] planes = GeometryUtility.CalculateFrustumPlanes(cam);
            var byGroup = new System.Collections.Generic.Dictionary<string, (int n, long tris, long full)>();
            long total = 0, totalFull = 0;
            int renderers = 0;
            foreach (MeshRenderer r in UnityEngine.Object.FindObjectsByType<MeshRenderer>())
            {
                if (!r.enabled || !r.gameObject.activeInHierarchy) continue;
                if (!GeometryUtility.TestPlanesAABB(planes, r.bounds)) continue;
                var mf = r.GetComponent<MeshFilter>();
                if (mf == null || mf.sharedMesh == null) continue;
                Mesh m = mf.sharedMesh;
                long full = m.triangles.Length / 3;
                long tris = full;
                // culled by a LODGroup?
                var lg = r.GetComponentInParent<LODGroup>();
                float dist = Vector3.Distance(cam.transform.position, r.bounds.center);
                float size = r.bounds.size.magnitude * 0.5f;
                float screen = size / (Mathf.Tan(cam.fieldOfView * 0.5f * Mathf.Deg2Rad) * 2f * Mathf.Max(dist, 0.1f));
                if (lg != null && lg.lodCount > 0)
                {
                    // only the renderers of the LOD level that would be active count; below the last level = culled
                    LOD[] lods = lg.GetLODs();
                    float s = lg.size * Mathf.Max(lg.transform.lossyScale.x, lg.transform.lossyScale.y, lg.transform.lossyScale.z);
                    float gd = Vector3.Distance(cam.transform.position, lg.transform.TransformPoint(lg.localReferencePoint));
                    float gscreen = s / (2f * Mathf.Tan(cam.fieldOfView * 0.5f * Mathf.Deg2Rad) * Mathf.Max(gd, 0.1f));
                    int active = -1;
                    for (int l = 0; l < lods.Length; l++) if (gscreen >= lods[l].screenRelativeTransitionHeight) { active = l; break; }
                    if (active < 0 || !lods[active].renderers.Contains(r)) continue;
                }
                tris = m.triangles.Length / 3;
                string g = r.transform.parent != null ? r.transform.parent.name : "root";
                if (r.transform.parent != null && r.transform.parent.parent != null && r.transform.parent.parent.name.StartsWith("--- Island")) g = r.transform.parent.name;
                byGroup.TryGetValue(g, out var cur);
                byGroup[g] = (cur.n + 1, cur.tris + tris, cur.full + full);
                total += tris; totalFull += full; renderers++;
            }
            string lines = string.Join("\n", byGroup.OrderByDescending(kv => kv.Value.tris)
                .Select(kv => $"  {kv.Key,-18} {kv.Value.n,5} renderers  {kv.Value.tris / 1000f,8:F0}k tris (full {kv.Value.full / 1000f:F0}k)"));
            Result($"stats visible: {renderers} renderers, {total / 1000f:F0}k tris after LOD/cull (full detail {totalFull / 1000f:F0}k)\n{lines}\n" +
                   $"  editor stats: {UnityEditor.UnityStats.triangles / 1000f:F0}k tris, {UnityEditor.UnityStats.drawCalls} draw calls, {UnityEditor.UnityStats.setPassCalls} setpass");
        }

        /// <summary>
        /// Development APK of the Island scene for a USB-connected phone: switches to Android if needed,
        /// IL2CPP + ARM64, package com.dinopark.tycoon, then installs and launches it (profiler attached)
        /// unless "norun". Output: Builds/Android/DinoPark.apk.
        /// </summary>
        private static void BuildAndroid(bool noRun, string releasePath = null)
        {
            bool release = !string.IsNullOrEmpty(releasePath);
            if (EditorApplication.isPlaying) throw new InvalidOperationException("Stop play mode first");
            SaveIfDirty();
            if (EditorUserBuildSettings.activeBuildTarget != BuildTarget.Android)
            {
                Result("switching platform to Android (re-imports assets)");
                EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.Android, BuildTarget.Android);
            }
            var android = UnityEditor.Build.NamedBuildTarget.Android;
            PlayerSettings.SetApplicationIdentifier(android, "com.dinopark.tycoon");
            PlayerSettings.SetScriptingBackend(android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            PlayerSettings.productName = "Dino Park";
            // Landscape only (Clash of Clans-style view); either way up.
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.AutoRotation;
            PlayerSettings.allowedAutorotateToPortrait = false;
            PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;
            PlayerSettings.allowedAutorotateToLandscapeLeft = true;
            PlayerSettings.allowedAutorotateToLandscapeRight = true;

            var options = new BuildPlayerOptions
            {
                scenes = new[] { IslandScene },
                locationPathName = release ? releasePath : "Builds/Android/DinoPark.apk",
                target = BuildTarget.Android,
                targetGroup = BuildTargetGroup.Android,
                // release: no dev console, profiler or FPS overlay (testers' build)
                options = release ? BuildOptions.None
                    : BuildOptions.Development | BuildOptions.ConnectWithProfiler | (noRun ? BuildOptions.None : BuildOptions.AutoRunPlayer),
            };
            Result("building Android APK...");
            var report = BuildPipeline.BuildPlayer(options);
            var s = report.summary;
            Result($"build {s.result}: {s.totalSize / (1024f * 1024f):F0} MB in {s.totalTime.TotalMinutes:F1} min, {s.totalErrors} errors -> {s.outputPath}");
            if (s.result != UnityEditor.Build.Reporting.BuildResult.Succeeded)
                foreach (var step in report.steps)
                    foreach (var msg in step.messages)
                        if (msg.type == LogType.Error || msg.type == LogType.Exception) Result("  error: " + msg.content);
        }

        private static float F(string s) => float.Parse(s, System.Globalization.CultureInfo.InvariantCulture);
    }
}
