using UnityEngine;

namespace DinoPark.Debugging
{
    /// <summary>
    /// Development builds only: small FPS / frame-time readout in the top-right corner, and a
    /// "[DinoPark] perf" line in the device log every 5 s (read with adb logcat -s Unity).
    /// Creates itself at startup; never exists in release builds.
    /// </summary>
    public sealed class DevFpsCounter : MonoBehaviour
    {
        private const float ReportInterval = 5f;

        private float windowTime;
        private int windowFrames;
        private float worstFrame;
        private float shownFps;
        private float shownMs;
        private float reportTime;
        private int reportFrames;
        private float reportWorst;
        private GUIStyle style;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
        private static void Create()
        {
            if (!Debug.isDebugBuild || Application.isEditor) return;
            Application.targetFrameRate = 60;   // Android defaults to 30; measure the real headroom
            var go = new GameObject("DevFpsCounter");
            DontDestroyOnLoad(go);
            go.AddComponent<DevFpsCounter>();
        }

        private void Update()
        {
            float dt = Time.unscaledDeltaTime;
            windowTime += dt; windowFrames++; worstFrame = Mathf.Max(worstFrame, dt);
            reportTime += dt; reportFrames++; reportWorst = Mathf.Max(reportWorst, dt);
            if (windowTime >= 0.5f)
            {
                shownFps = windowFrames / windowTime;
                shownMs = 1000f * windowTime / windowFrames;
                windowTime = 0f; windowFrames = 0; worstFrame = 0f;
            }
            if (reportTime >= ReportInterval)
            {
                Debug.Log($"[DinoPark] perf avg {reportFrames / reportTime:F1} fps, {1000f * reportTime / reportFrames:F1} ms, worst {reportWorst * 1000f:F0} ms, screen {Screen.width}x{Screen.height}, target {Application.targetFrameRate}");
                reportTime = 0f; reportFrames = 0; reportWorst = 0f;
            }
        }

        private void OnGUI()
        {
            if (style == null)
                style = new GUIStyle(GUI.skin.label) { fontSize = Mathf.Max(18, Screen.height / 40), alignment = TextAnchor.UpperRight, normal = { textColor = Color.white } };
            var r = new Rect(Screen.width - 420, 10, 400, 60);
            GUI.color = new Color(0f, 0f, 0f, 0.5f);
            GUI.DrawTexture(new Rect(r.x + 200, r.y, 200, style.fontSize * 1.5f), Texture2D.whiteTexture);
            GUI.color = shownFps < 25f ? new Color(1f, 0.45f, 0.4f) : shownFps < 45f ? new Color(1f, 0.85f, 0.4f) : new Color(0.6f, 1f, 0.6f);
            GUI.Label(r, $"{shownFps:F0} fps  {shownMs:F1} ms", style);
        }
    }
}
