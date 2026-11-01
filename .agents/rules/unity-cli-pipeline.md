# Unity CLI and Pipeline Automation Guidelines

This rule establishes technical standards for driving the Unity Editor from the command line (`unity-cli`), managing UPM packages (`unity-package-management`), and executing batch jobs via the Pipeline package (`unity-pipeline`).

## 1. Running Editor vs Headless Execution
- **Prefer Active Editor Connection**:
  - When a Unity Editor instance is running and healthy (`unity status` reports `ready`), route automation commands via `unity command` (e.g. `unity command package add`, `unity command eval`).
  - Specify `--project-path "<path>"` when multiple Editor instances are open to target the exact project port.
- **Handling Domain Reloads**:
  - Package additions and code imports trigger C# domain reloads.
  - Do not hammer the Editor port synchronously during a reload; check `unity status` or poll `unity command package status` asynchronously until `completed`.

## 2. Package Management Protocol
- **Do Not Manually Edit Manifest Files Blindly**:
  - Use `unity command package add --identifier <pkg>@<ver> --confirm true` to ensure the UPM resolver verifies transitive dependency versions and compatibility locks in `packages-lock.json`.
- **Search Before Installing**:
  - Always verify package existence in the registry using `unity command package search --query <term>` before issuing an `add` command.

## 3. Headless Script Invocation (-batchmode)
- When running headless CI scripts:
  - Do not use `-quit` when invoking asynchronous APIs (`Client.Add`, `Client.SearchAll`); let the C# method poll `IsCompleted` and invoke `EditorApplication.Exit(code)`.
  - Stream logs to stdout using `-logFile -` to observe asset import and compilation errors immediately.
