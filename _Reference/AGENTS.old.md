# Antigravity & AI Agent Directives for Dinosaur Park Project

Welcome to the **Dinosaur Park** project. This project is built on **Unity 6 (6000.6.7f1)** and the **Universal Render Pipeline (URP 17.6.0)**.

---

## 1. Customization Architecture

All agent behaviors, runbooks, and domain guidelines are organized in `.agents/`:

```text
Dinosaur_Park/
├── AGENTS.md                                    # This project-level rule file
└── .agents/
    ├── plugins.json                             # Registered agent plugins
    ├── marketplace.json                         # Workspace plugin marketplace catalog
    ├── rules/                                   # 24 Domain-specific coding & architectural rules
    │   ├── 2d-tilemaps.md                       # Tilemaps, Rule Tiles, PixelPerfect, SpriteAtlas
    │   ├── agent-plugins.md                     # Agent plugin lifecycle & progressive disclosure
    │   ├── android-logcat.md                    # Android logcat, memory profiling, crash symbolication
    │   ├── audio-architecture.md                # AudioMixer hierarchy, ducking, load types
    │   ├── autodesk-fbx.md                      # FbxManager memory lifecycle, ModelExporter, Maya roundtrip
    │   ├── character-controllers.md             # StarterAssets FirstPerson & ThirdPerson controllers
    │   ├── dreamteck-splines.md                 # SplineComputer, SplineFollower physics, SplineMesh
    │   ├── entities-graphics.md                 # Entities Graphics, RenderMeshArray, skinning
    │   ├── kinematic-character-controller.md    # KCC Motor, ICharacterController, PhysicsMover
    │   ├── lean-touch.md                        # LeanFinger, multi-touch gestures, touch camera
    │   ├── mobile-notifications.md              # Android channels, iOS badges, local scheduling
    │   ├── monetization-liveops.md              # Unity IAP, LevelPlay mediation, UGS LiveOps
    │   ├── multiplayer-netcode.md               # Authoritative FPS networking, client prediction
    │   ├── naughty-attributes.md                # [Button], [ShowIf], [Dropdown], [Required]
    │   ├── netcode-gameobjects.md               # NGO 2.0 RPCs, NetworkVariable, Distributed Authority
    │   ├── physics.md                           # PhysX 3D & Unity.Physics DOTS simulation
    │   ├── postprocessing.md                    # URP Volume framework & RenderGraph features
    │   ├── scene-hierarchy-styling.md           # Colorful Hierarchy headers (===, ---, ###)
    │   ├── toon-shading.md                      # UTS3 anime shading, 3-color steps, outlines
    │   ├── ui-frameworks.md                     # UI Toolkit vs uGUI vs IMGUI standards
    │   ├── unity-cli-pipeline.md                # Unity CLI, Pipeline commands, UPM resolution
    │   ├── unity-engine-internals.md            # C++/C# lifecycle traps, fake nulls, PlayerLoop
    │   ├── version-control.md                   # UVCS (Plastic SCM) CLI & lock rules
    │   └── virtual-joysticks.md                 # Virtual Joystick Pack (Fixed, Floating, Dynamic)
    ├── skills/                                  # 52 Active Specialized Skills
    └── plugins/
        └── unity-agent-plugin/                  # Official Unity Technologies Agent Plugin (32 skills)
```

---

## 2. Core Operational Principles

1. **Unity 6 & URP First**: Always target modern Unity 6 APIs. Do not introduce deprecated Built-in Render Pipeline calls.
2. **Character Controller Strategy**:
   - For rapid prototyping, use **Starter Assets** (`FirstPersonController` / `ThirdPersonController`).
   - For complex multi-state physics, moving platforms, and tight collision handling, use **Kinematic Character Controller** (`KinematicCharacterMotor` + `ICharacterController`).
3. **Inspector Ergonomics & Validation**:
   - Use **NaughtyAttributes** (`[Required]`, `[ShowIf]`, `[Button]`) instead of writing repetitive custom editor classes.
4. **Touch & Mobile Controls**:
   - Combine **Virtual Joystick Pack** for directional locomotion with **Lean Touch** for multi-finger gestures and pinch camera navigation. Always suppress gameplay touch events when `finger.IsOverGui == true`.
5. **Hierarchy Cleanliness**:
   - Group scene elements under category GameObjects styled with `=== Category ===` and `--- Subcategory ---` prefixes.
6. **Zero Memory Leaks in Native Interops**:
   - Wrap low-level FBX SDK contexts (`FbxManager`) in `using` blocks or explicit `Destroy()`.
7. **Spline Consistency**:
   - For constant-speed followers or procedural extrusion in Dreamteck Splines, always enforce `SampleMode.Uniform`.

---

## 3. Modern Eco-Park 3D Asset & Architecture Standards

1. **Unified Color Palette**:
   - Off-White Concrete: `#F4EDD8`
   - Light Timber Slats: `#C79A63`
   - Charcoal Steel Framing: `#3B4743`
   - Solid Tinted Teal Glass: `#8FCBCB`
   - Living Roof Foliage: `#5E9B4A`
   - Brass Gold Accents & Beacons: `#F2B84B`
   - Amber Glow Trim / Egg Skylights: `#FFAA33`

2. **Strict Metric Scale & Ratio Consistency**:
   - **Grid Cell**: `1 cell = 2.0 meters`.
   - **Standard Modular Solar Panel**: Exactly `1.6m x 1.0m` across all buildings (small and large alike).
   - **Door Openings**: Standard height `2.2m` - `2.4m`, single leaf `0.9m` - `1.0m`, double sliding `1.8m` - `2.8m`.
   - **Road Kit**: Modular `4.0m` width (2 cells) with asphalt deck, concrete curbs, yellow center divider, and zebra crosswalks.

3. **Articulation & Interactive Hierarchy**:
   - All interactive doors, gates, and turnstiles MUST be modeled as separate child objects with correct hinge or slide pivots.
   - Attach [InteractiveDoor.cs](file:///d:/Unity%20Projects/Dinosaur_Park/Assets/Scripts/Interactions/InteractiveDoor.cs) supporting `DoubleSlide`, `SingleSlide`, and `HingeSwing` with proximity trigger detection.

