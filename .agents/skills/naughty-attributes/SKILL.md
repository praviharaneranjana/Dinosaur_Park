---
name: naughty-attributes
description: Enhances Unity inspector workflows, property drawers, and validation using NaughtyAttributes. Covers [Button], [ShowIf]/[HideIf], [Dropdown], [ReorderableList], [BoxGroup], [ProgressBar], [CurveRange], [MinMaxSlider], and [Required] without writing custom Editor scripts.
---

# NaughtyAttributes Skill

This skill guides designing clean, expressive, and interactive Unity inspector inspectors without writing boilerplate `CustomEditor` classes, using **NaughtyAttributes** (`NaughtyAttributes` by Denis Rizov).

## Core Attribute Categories

| Category | Primary Attributes | Use Case |
| :--- | :--- | :--- |
| **Action & Methods** | `[Button("Label")]` | Exposes C# methods directly in the inspector as clickable buttons. |
| **Conditional Visibility** | `[ShowIf("boolField")]`, `[HideIf]`, `[EnableIf]`, `[DisableIf]` | Dynamically displays or grays out inspector fields based on state. |
| **Organization & Grouping**| `[BoxGroup("Title")]`, `[Foldground]`, `[HorizontalLine]` | Groups related fields into styled visual boxes or foldable sections. |
| **Specialized Drawers** | `[Dropdown("optionsList")]`, `[ReorderableList]`, `[ProgressBar]`, `[MinMaxSlider]`, `[ShowAssetPreview]` | Enhanced UI controls for collections, ranges, health bars, and asset thumbnails. |
| **Validation & Meta** | `[Required]`, `[ValidateInput]`, `[InfoBox]`, `[ReadOnly]`, `[OnValueChanged]` | Prevents missing asset references, validates ranges, and invokes callbacks on change. |

---

## 1. Practical Usage Example

```csharp
using UnityEngine;
using NaughtyAttributes;
using System.Collections.Generic;

public class BossEntity : MonoBehaviour
{
    [BoxGroup("Configuration")]
    [Required("Every boss must have a display name.")]
    public string BossName;

    [BoxGroup("Configuration")]
    [Dropdown("GetFactions")]
    public string Faction;

    [BoxGroup("Stats")]
    [ProgressBar("Health", 1000, ProgressBarColor.Green)]
    public float CurrentHealth = 1000f;

    [BoxGroup("Stats")]
    [MinMaxSlider(0f, 100f)]
    public Vector2 DamageRange = new Vector2(25f, 65f);

    [BoxGroup("Special Abilities")]
    public bool HasRagePhase;

    [BoxGroup("Special Abilities")]
    [ShowIf("HasRagePhase")]
    [CurveRange(0, 0, 1, 3, EColor.Red)]
    public AnimationCurve RageDamageMultiplier;

    [BoxGroup("Actions")]
    [Button("Trigger Enrage Mode", EButtonEnableMode.Playmode)]
    private void TriggerEnrage()
    {
        Debug.Log($"{BossName} enters rage mode!");
    }

    private List<string> GetFactions() => new List<string> { "Undead", "Demon", "Elemental", "Celestial" };
}
```

---

## Detailed References
- [NaughtyAttributes Complete Cheatsheet & Parameter Guide](file:///d:/Unity%20Projects/mini_game/.agents/skills/naughty-attributes/references/attributes-cheatsheet.md)
- [Advanced Inspector Patterns & Validation Scripts](file:///d:/Unity%20Projects/mini_game/.agents/skills/naughty-attributes/references/editor-scripting-patterns.md)
