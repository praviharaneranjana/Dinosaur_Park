using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
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

        private static float F(string s) => float.Parse(s, System.Globalization.CultureInfo.InvariantCulture);
    }
}
