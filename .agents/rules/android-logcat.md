# Android Debugging and Logcat Guidelines

This project utilizes `com.unity.mobile.android-logcat` for real-time device logging, crash diagnostics, memory tracing, and remote automation.

## Core Directives

1. **Tag Filtering**:
   - Filter logs using `package:mine` or the specific bundle identifier to eliminate OS noise.
   - Core Unity logs are tagged `Unity`. Native crash tombstones are tagged `DEBUG` or `CRASH`. Java/Android exceptions are tagged `AndroidRuntime`.
   - Never print sensitive credentials, tokens, or PII in `Debug.Log` statements on Android builds.

2. **Crash Dumps & IL2CPP Symbolication**:
   - For all release/staging Android builds, ensure **Create symbols.zip** is enabled in Build Settings (`File > Build Settings > Android`).
   - Store the generated `<Project>-<version>-v8a.symbols.zip` alongside the build artifacts.
   - When debugging native crash stacktraces (`SIGSEGV` / `SIGABRT`), feed the symbols file directly to the **Stacktrace Utility** (`Window > Analysis > Android Logcat > Stacktrace`) to resolve hex addresses into C# methods and source lines.

3. **Memory Diagnostics**:
   - Inspect PSS (Proportional Set Size) rather than RSS or VSS to determine actual application memory footprints.
   - Always implement `Application.lowMemory` event handlers to purge unreferenced textures, clear object pools, and call `Resources.UnloadUnusedAssets()`.
   - Test low-memory resilience before shipping by sending `TRIM_MEMORY_RUNNING_CRITICAL` from the Logcat Memory window.

4. **Remote ADB & Input Emulation**:
   - For automated smoke tests, prefer injecting inputs via `AndroidLogcatUtilities` or `adb shell input tap/swipe` over manual touch testing.
   - Use wireless ADB (`adb tcpip 5555`) for prolonged playtests to prevent device battery charging thermal throttling from skewing frame rate analysis.
