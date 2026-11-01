# NaughtyAttributes Complete Cheatsheet & Parameter Guide

This reference provides syntax patterns and parameters for all major NaughtyAttributes drawers.

---

## 1. Action Attributes

### `[Button]`
Renders a button that invokes the decorated method:
```csharp
[Button] // Button text defaults to method name
private void ResetStats() { }

[Button("Custom Button Text", EButtonEnableMode.Playmode)] // Active only in Play Mode
public void SpawnWave() { }

[Button("Editor Only Reset", EButtonEnableMode.Editor)] // Active only when NOT playing
private void RebuildNavMesh() { }
```

---

## 2. Condition Attributes

### `[ShowIf]` / `[HideIf]`
Takes field names, property names, or method names returning `bool`:
```csharp
public bool UseCustomPhysics;

[ShowIf("UseCustomPhysics")]
public float CustomFriction = 0.5f;

// Condition operator support
public enum AttackType { Melee, Ranged, Magic }
public AttackType AttackMode;

[ShowIf(EConditionOperator.And, "UseCustomPhysics", "IsRangedAttack")]
public float ProjectileSpeed;

private bool IsRangedAttack() => AttackMode == AttackType.Ranged;
```

---

## 3. Drawers & Visual Styling

### `[Dropdown]`
Select from a list or dictionary:
```csharp
[Dropdown("WeaponIDs")]
public int SelectedWeaponId;

private DropdownList<int> WeaponIDs()
{
    return new DropdownList<int>()
    {
        { "Broadsword", 101 },
        { "Compound Bow", 204 },
        { "Staff of Flames", 309 }
    };
}
```

### `[ProgressBar]`
Visual meter with color thresholds:
```csharp
[ProgressBar("Stamina", 100, ProgressBarColor.Blue)]
public float Stamina = 100;
```

### `[ReorderableList]`
Enables dragging to reorder elements in `List<T>` or `T[]`:
```csharp
[ReorderableList]
public List<Transform> PatrolWaypoints;
```

---

## 4. Validation Attributes

### `[Required]`
Highlights null object references in red:
```csharp
[Required("Player prefab must be assigned!")]
public GameObject PlayerPrefab;
```

### `[ValidateInput]`
Validates field values using a custom boolean method:
```csharp
[ValidateInput("ValidateNonZero", "Value cannot be zero!")]
public int Multiplier = 1;

private bool ValidateNonZero(int val) => val != 0;
```
