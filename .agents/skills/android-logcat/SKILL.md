---
name: android-logcat
description: Diagnoses, debugs, and profiles Android builds and runtime devices using Unity Android Logcat (com.unity.mobile.android-logcat). Covers ADB device connections, tag filtering, stacktrace symbolication, memory footprints (PSS, Dalvik, Native), screen capture/recording, and input event injection.
---

# Android Logcat Skill

This skill guides the inspection, real-time logging, crash debugging, memory profiling, and remote device control for Android builds in Unity using `com.unity.mobile.android-logcat`.

## Quick Reference & Entry Points

| Tool / Window | Unity Editor Path | Core Purpose |
| :--- | :--- | :--- |
| **Android Logcat Console** | `Window > Analysis > Android Logcat` (`Ctrl+G` / `Cmd+G`) | Live logcat stream, process filtering, regex search, color tags. |
| **Memory Viewer** | `Window > Analysis > Android Logcat > Memory` | PSS, Native Heap, Dalvik/ART Heap, Graphics, and Trim Memory signals. |
| **Stacktrace Utility** | `Window > Analysis > Android Logcat > Stacktrace` | Symbolicates crash dumps using `symbols.zip` or `libil2cpp.so.debug`. |
| **Screen Capture & Video** | `Android Logcat > Tools > Capture Screenshot / Record Video` | Captures high-res screenshots and MP4 video recordings directly from device. |
| **Input Injection** | `Android Logcat > Tools > Input` | Emulates touch inputs, tap coordinates, key codes (`AndroidKeyCode`), and swipe gestures. |

---

## Core Workflows

### 1. Device Connection & Multi-Device Setup
- **USB ADB**: Ensure Developer Options and USB Debugging are enabled on device.
- **Wireless ADB (IP Window)**:
  1. Connect device via USB first: `adb tcpip 5555`.
  2. In Unity, open `Android Logcat > Select Device > Connect by IP...`.
  3. Enter `192.168.x.x:5555`. Disconnect USB cord.

### 2. Filtering Log Messages
- **Filter by Process**: Select `com.Company.MyGame` from the process dropdown. Only messages emitted by the game PID are displayed.
- **Filter by Tags**:
  - `Unity`: Core engine logs (`Debug.Log`, physics, graphics).
  - `CRASH`: Native segfaults, signal 11 (SIGSEGV), signal 6 (SIGABRT).
  - `AndroidRuntime`: Java/Kotlin exceptions, unhandled RuntimeExceptions.
  - `DEBUG`: Native crash tombstone dumps and backtraces.
- **Filter Expressions**:
  - `tag:Unity priority:Error`
  - `package:mine tag:Unity | tag:CRASH`
  - Regex filter: `(?i)exception|fatal|segv`

### 3. Crash Diagnostics & Stacktrace Symbolication
When a native crash occurs (`SIGSEGV`, `SIGABRT`, `DEBUG` tombstone):
1. In Android Logcat, click the crash entry or open **Stacktrace Utility**.
2. Specify the path to the project's build symbols:
   - For IL2CPP: `symbols.zip` generated alongside the APK/AAB during build (when **Create symbols.zip** is checked in Build Settings).
   - Alternatively point to `Temp/StagingArea/symbols` or `Library/Bee/artifacts/Android/`.
3. Click **Symbolicate**. Raw memory offsets like `libil2cpp.so + 0x12a4b0` resolve into exact C# method names and line numbers.

### 4. Memory Profiling & Low-Memory Signals
- **PSS (Proportional Set Size)**: Real memory footprint attributed to the game process.
- **Track Categories**:
  - `Native Heap`: C++ engine allocations, textures, meshes, FMOD/audio buffers.
  - `Dalvik/ART Heap`: Android JVM allocations, plugins, activity lifecycle.
  - `Graphics`: OpenGL ES / Vulkan driver allocations.
- **Simulate Low Memory**:
  - Use `Android Logcat > Send Low Memory Signal` (`TRIM_MEMORY_RUNNING_CRITICAL`).
  - Verify your game handles `Application.lowMemory` callbacks and unloads unused asset bundles.

---

## Detailed References
- [Logcat Workflows & Filter Syntax](file:///d:/Unity%20Projects/mini_game/.agents/skills/android-logcat/references/logcat-workflows.md)
- [Memory Profiling & Crash Symbolication](file:///d:/Unity%20Projects/mini_game/.agents/skills/android-logcat/references/memory-and-crash-analysis.md)
