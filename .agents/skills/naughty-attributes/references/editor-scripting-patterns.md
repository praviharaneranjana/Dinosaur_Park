# Advanced Inspector Patterns with NaughtyAttributes

This reference demonstrates organizing complex modular components and ScriptableObjects with NaughtyAttributes.

---

## 1. Modular Ability / Item ScriptableObject

```csharp
using UnityEngine;
using NaughtyAttributes;

[CreateAssetMenu(fileName = "NewAbility", menuName = "Game/Ability")]
public class AbilityConfig : ScriptableObject
{
    [BoxGroup("Identity")]
    [ShowAssetPreview(64, 64)]
    public Sprite Icon;

    [BoxGroup("Identity")]
    [Required]
    public string AbilityName;

    [BoxGroup("Identity")]
    [ResizableTextArea]
    public string Description;

    [BoxGroup("Costs & Cooldowns")]
    [MinValue(0f)]
    public float ManaCost = 25f;

    [BoxGroup("Costs & Cooldowns")]
    [MinValue(0.1f)]
    public float Cooldown = 5f;

    [BoxGroup("Targeting")]
    public bool IsAreaOfEffect;

    [BoxGroup("Targeting")]
    [ShowIf("IsAreaOfEffect")]
    [Range(1f, 20f)]
    public float Radius = 5f;

    [BoxGroup("Audio / VFX")]
    public AudioClip CastSound;

    [BoxGroup("Audio / VFX")]
    public GameObject ImpactVFX;
}
```
