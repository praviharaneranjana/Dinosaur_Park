# PlayerLoop Architecture & Custom Subsystem Injection

In `UnityCsReference` (`Runtime/Export/Scripting/PlayerLoop.cs` and `Runtime/Export/Scripting/PlayerLoopInternal.bindings.cs`), Unity exposes low-level control over the engine's main execution loop via `UnityEngine.LowLevel.PlayerLoop`.

Rather than relying on scattered `MonoBehaviour.Update()` calls across hundreds of GameObjects, high-performance engines and packages (such as UniTask, DOTS, and Netcode) inject custom systems directly into the native C++ **PlayerLoop**.

---

## 1. The Structure of the PlayerLoop

The PlayerLoop is organized as a recursive tree of `PlayerLoopSystem` structs:

```csharp
namespace UnityEngine.LowLevel
{
    public struct PlayerLoopSystem
    {
        public Type type;                           // Identifying type tag
        public PlayerLoopSystem[] subSystemList;    // Nested child systems
        public UpdateFunction updateDelegate;       // Managed C# callback delegate
        public IntPtr updateFunction;               // Unmanaged native C++ function pointer
        public IntPtr loopConditionFunction;        // Native execution condition check
    }
}
```

### The 7 Primary Top-Level Subsystem Phases:
1. **`Initialization`**: Resets frame timers, initializes low-level platform events.
2. **`EarlyUpdate`**: Polls input devices (`PollInputEvents`), updates touch/mouse/keyboard states, clears canvas batches.
3. **`FixedUpdate`**: Executes the physics simulation loop (NVIDIA PhysX / Box2D steps), calls `MonoBehaviour.FixedUpdate`.
4. **`PreUpdate`**: Updates AI/NavMesh path calculations, processes network streams and remote packets.
5. **`Update`**: Dispatches `MonoBehaviour.Update()`, dynamic coroutine resume passes.
6. **`PreLateUpdate`**: Evaluates animation state machines, IK constraint passes, timeline playback.
7. **`PostLateUpdate`**: Dispatches `MonoBehaviour.LateUpdate()`, camera matrices update, GUI rendering, frame buffer presentation (`Present`).

---

## 2. Inspecting the PlayerLoop

You can print the entire hierarchy of Unity's current player loop using this utility:

```csharp
using System.Text;
using UnityEngine;
using UnityEngine.LowLevel;

public static class PlayerLoopDiagnostics
{
    [ContextMenu("Log Player Loop")]
    public static void LogCurrentPlayerLoop()
    {
        var loop = PlayerLoop.GetCurrentPlayerLoop();
        var sb = new StringBuilder();
        sb.AppendLine("=== Unity Player Loop Hierarchy ===");
        PrintSubsystems(loop, sb, 0);
        Debug.Log(sb.ToString());
    }

    private static void PrintSubsystems(PlayerLoopSystem system, StringBuilder sb, int depth)
    {
        string indent = new string(' ', depth * 2);
        string typeName = system.type != null ? system.type.Name : "(Root)";
        sb.AppendLine($"{indent}- {typeName}");

        if (system.subSystemList != null)
        {
            foreach (var sub in system.subSystemList)
            {
                PrintSubsystems(sub, sb, depth + 1);
            }
        }
    }
}
```

---

## 3. Injecting a Custom Loop Phase

Suppose you need a custom **`NetworkSimulationTick`** that runs immediately after network packets are received in `PreUpdate`, but strictly before `Update()`:

```csharp
using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.LowLevel;
using UnityEngine.PlayerLoop;

public static class CustomNetworkLoopInjector
{
    public struct NetworkTickSystemMarker { }

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    public static void InjectNetworkTick()
    {
        PlayerLoopSystem defaultLoop = PlayerLoop.GetDefaultPlayerLoop();
        
        var customSystem = new PlayerLoopSystem
        {
            type = typeof(NetworkTickSystemMarker),
            updateDelegate = RunNetworkTick
        };

        // Inject into PreUpdate phase
        if (InsertSystem(ref defaultLoop, typeof(PreUpdate), customSystem))
        {
            PlayerLoop.SetPlayerLoop(defaultLoop);
            Debug.Log("Successfully injected NetworkTickSystem into PreUpdate.");
        }
    }

    private static void RunNetworkTick()
    {
        // Custom deterministic network loop logic
        // This runs without needing a GameObject or MonoBehaviour!
    }

    private static bool InsertSystem(ref PlayerLoopSystem root, Type targetPhase, PlayerLoopSystem newSystem)
    {
        if (root.subSystemList == null) return false;

        for (int i = 0; i < root.subSystemList.Length; i++)
        {
            if (root.subSystemList[i].type == targetPhase)
            {
                // Found target phase! Append or insert our system
                var list = new List<PlayerLoopSystem>(root.subSystemList[i].subSystemList);
                list.Add(newSystem);
                root.subSystemList[i].subSystemList = list.ToArray();
                return true;
            }

            if (InsertSystem(ref root.subSystemList[i], targetPhase, newSystem))
                return true;
        }

        return false;
    }
}
```

### Safety & Best Practices
- **Never Throw Exceptions**: Exceptions thrown inside an `updateDelegate` will break the PlayerLoop and cause Unity's internal native loop to crash or skip remaining phases.
- **Always Wrap with Try-Catch**: Encapsulate custom callbacks in `try ... catch (Exception ex) { Debug.LogException(ex); }`.
- **Domain Reload Resilience**: Clear or reset the player loop when unloading domain or entering edit mode via `PlayerLoop.SetPlayerLoop(PlayerLoop.GetDefaultPlayerLoop())`.
