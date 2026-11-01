# NaughtyAttributes Inspector Guidelines

This rule establishes technical standards for using **NaughtyAttributes** (`NaughtyAttributes`) to design clean, validated, and interactive inspectors.

## Core Directives

1. **Avoid Boilerplate Custom Editors**:
   - Prefer using NaughtyAttributes (`[Button]`, `[ShowIf]`, `[BoxGroup]`, `[Dropdown]`, `[ReorderableList]`) instead of writing dedicated `Editor/CustomEditor` scripts whenever simple layout or method triggering is required.

2. **Mandatory Validation Attributes**:
   - Use `[Required]` on all public reference fields (Prefabs, Materials, AudioClips, Transforms) whose omission would trigger runtime `NullReferenceException`.
   - Use `[MinValue]` and `[MaxValue]` (or `[Range]`) on numeric fields to prevent invalid physics mass, speeds, or negative timers.

3. **Performance in Play Mode**:
   - For `[Button]` attributes that trigger expensive operations (e.g. rebuilding navmeshes, respawning pools), restrict execution mode via `EButtonEnableMode.Editor` or `EButtonEnableMode.Playmode` to prevent accidental clicks in wrong contexts.
