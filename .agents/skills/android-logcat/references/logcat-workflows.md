# Android Logcat: Workflows, Filter Syntax & Remote Automation

This reference covers deep filtering, automated log capture, and remote device operations with `com.unity.mobile.android-logcat`.

---

## 1. Filter Syntax & Query Operators

Unity Android Logcat provides advanced querying capabilities in the filter search bar:

| Filter Token | Description | Example |
| :--- | :--- | :--- |
| `tag:<tag>` | Matches exact log tag | `tag:Unity` or `tag:AndroidRuntime` |
| `priority:<level>` | Minimum priority level (`Verbose`, `Debug`, `Info`, `Warn`, `Error`, `Fatal`) | `priority:Error` |
| `package:<name>` | Matches application package ID or shortcut `package:mine` | `package:com.mycompany.game` |
| `pid:<id>` | Matches specific Linux process ID | `pid:28412` |
| `msg:<text>` | Matches substring within log message body | `msg:NullReferenceException` |
| `\|` (OR) | Matches either condition | `tag:Unity \| tag:DEBUG` |
| `&` (AND) | Matches both conditions (implicit space is also AND) | `tag:Unity priority:Warn` |
| `-` (NOT) | Negates expression | `-tag:OpenGLRenderer` |

---

## 2. Editor Scripting & Programmatic Logcat API

You can interact with Logcat programmatically from Editor scripts via `Unity.Mobile.AndroidLogcat.Editor`:

```csharp
#if UNITY_EDITOR
using UnityEditor;
using UnityEngine;
using Unity.Mobile.AndroidLogcat.Editor;

public static class LogcatAutomation
{
    [MenuItem("Tools/Android/Inspect Connected Devices")]
    public static void QueryDevices()
    {
        var runtime = AndroidLogcatManager.instance.Runtime;
        if (runtime == null)
        {
            Debug.LogWarning("Android Logcat Runtime is not initialized.");
            return;
        }

        var deviceQuery = runtime.DeviceQuery;
        var devices = deviceQuery.Devices;
        Debug.Log($"Connected Android devices: {devices.Count}");

        foreach (var device in devices)
        {
            Debug.Log($"Device: {device.DisplayName} | ID: {device.Id} | State: {device.State}");
        }
    }

    [MenuItem("Tools/Android/Capture Device Screenshot")]
    public static void TakeScreenshot()
    {
        var runtime = AndroidLogcatManager.instance.Runtime;
        var device = runtime?.DeviceQuery.SelectedDevice;
        if (device == null)
        {
            Debug.LogError("No Android device selected in Logcat!");
            return;
        }

        string savePath = "Screenshots/Android_" + System.DateTime.Now.ToString("yyyyMMdd_HHmmss") + ".png";
        AndroidLogcatUtilities.CaptureScreenshot(device, savePath);
        Debug.Log($"Captured device screenshot to: {savePath}");
    }
}
#endif
```

---

## 3. Remote Input Injection & Automated Testing

The Input utility allows sending key events, tap coordinates, and text without physically touching the device:

```powershell
# Send touch tap at (x=500, y=1000)
adb -s <device_id> shell input tap 500 1000

# Send swipe / drag from (300, 1200) to (300, 400) over 300ms
adb -s <device_id> shell input swipe 300 1200 300 400 300

# Inject back key press
adb -s <device_id> shell input keyevent 4

# Inject text entry into active text field
adb -s <device_id> shell input text "PlayerOne"
```

Inside Unity Editor:
- Open `Android Logcat > Tools > Input`.
- Click on screen preview or use the virtual keypad to trigger `AndroidKeyCode.Back`, `AndroidKeyCode.Home`, or touch points.
