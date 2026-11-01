# Zero-Allocation Performance Patterns (Source-Derived)

By inspecting `UnityCsReference` implementations in `Runtime/Export/`, we can identify exactly where managed GC heap allocations occur inside the engine and how to eliminate them.

---

## 1. Tag Comparisons: `CompareTag` vs `tag ==`

In `Runtime/Export/Scripting/GameObject.bindings.cs`:

```csharp
// Source excerpt from UnityCsReference: GameObject.bindings.cs
public string tag
{
    get { return GetTag(); } // Native call that creates a NEW managed string instance!
    set { SetTag(value); }
}

[FreeFunction("GameObjectBindings::CompareTag", HasExplicitThis = true)]
public extern bool CompareTag(string tag);
```

### The Mechanism
- `gameObject.tag`: Calls native C++ `GetTag()`, which copies native characters and **allocates a brand new `System.String` on the GC heap** every time it is accessed!
- `gameObject.CompareTag(string)`: Passes the string pointer to C++, which hashes it and compares it against the GameObject's internal tag ID without allocating any memory.

```csharp
// SLOW (Allocates ~40-60 bytes per call):
if (collision.gameObject.tag == "Enemy") { }

// FAST (Zero GC allocation):
if (collision.gameObject.CompareTag("Enemy")) { }
```

---

## 2. Non-Alloc Physics Queries

In `Modules/Physics/Physics.bindings.cs`:

```csharp
// Allocates a new RaycastHit[] array on the heap every single call:
public static RaycastHit[] RaycastAll(Ray ray, float maxDistance);

// Zero allocation: writes into pre-allocated user buffer and returns count:
public static int RaycastNonAlloc(Ray ray, RaycastHit[] results, float maxDistance);
```

### Production Pattern
```csharp
public class LaserSensor : MonoBehaviour
{
    private static readonly RaycastHit[] HitBuffer = new RaycastHit[16];

    public void Scan(Ray ray, float distance)
    {
        int hitCount = Physics.RaycastNonAlloc(ray, HitBuffer, distance);
        for (int i = 0; i < hitCount; i++)
        {
            ProcessHit(HitBuffer[i]);
        }
    }
}
```

---

## 3. Component Queries: Array vs List

In `Runtime/Export/Scripting/GameObject.bindings.cs`:

```csharp
// Allocates a new T[] array on the heap:
public T[] GetComponents<T>();

// Reuses the passed List<T> without heap allocation (clears and populates):
public void GetComponents<T>(List<T> results);
```

### Production Pattern
```csharp
public class AggregationManager : MonoBehaviour
{
    private readonly List<Collider> colliderCache = new List<Collider>(32);

    public void RefreshColliders()
    {
        GetComponentsInChildren(colliderCache);
        for (int i = 0; i < colliderCache.Count; i++)
        {
            colliderCache[i].enabled = true;
        }
    }
}
```

---

## 4. Coroutine Yield Instruction Caching

In `Runtime/Export/Scripting/YieldInstructions.cs`:
`WaitForSeconds` is a managed class. Writing `yield return new WaitForSeconds(0.5f);` inside a loop or recurring method instantiates a new object every time.

```csharp
public class HeartbeatPulse : MonoBehaviour
{
    private readonly WaitForSeconds waitHalfSecond = new WaitForSeconds(0.5f);

    private IEnumerator PulseLoop()
    {
        while (true)
        {
            DoPulse();
            yield return waitHalfSecond; // Zero GC allocation!
        }
    }
}
```

---

## 5. Material Instances vs MaterialPropertyBlock

In `Runtime/Export/Graphics/Renderer.bindings.cs`:
Accessing `renderer.material` triggers the native engine to **clone** the shared material and instantiate a unique material instance on the heap:

```csharp
// DANGEROUS: If called in Update(), creates thousands of cloned Material instances!
renderer.material.color = Color.red;

// OPTIMAL: Uses GPU instancing without cloning materials or causing leaks:
private static MaterialPropertyBlock propBlock;

public void SetColor(Color col)
{
    if (propBlock == null) propBlock = new MaterialPropertyBlock();
    renderer.GetPropertyBlock(propBlock);
    propBlock.SetColor("_BaseColor", col);
    renderer.SetPropertyBlock(propBlock);
}
```

---

## 6. Summary Comparison Table

| Common Pattern | Heap Allocation (GC) | Optimal Pattern | Heap Allocation (GC) |
|---|---|---|---|
| `go.tag == "Player"` | Allocates string | `go.CompareTag("Player")` | **0 bytes** |
| `Physics.RaycastAll()` | Allocates `RaycastHit[]` | `Physics.RaycastNonAlloc()` | **0 bytes** |
| `go.GetComponents<T>()` | Allocates `T[]` | `go.GetComponents<T>(list)` | **0 bytes** |
| `new WaitForSeconds(1f)` in loop | Allocates class instance | Cache `WaitForSeconds` in field | **0 bytes** |
| `renderer.material.color` | Clones Material instance | `renderer.SetPropertyBlock()` | **0 bytes** |
| `$"Damage: {amount}"` | Allocates string + boxing | Fixed string or custom buffer | **0 bytes** |
| `FindObjectsByType<T>()` in loop | Traverses scene & allocates array | Cache references on start | **0 bytes** |
