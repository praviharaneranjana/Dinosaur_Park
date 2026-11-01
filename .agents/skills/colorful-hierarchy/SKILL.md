---
name: colorful-hierarchy
description: Organizes, styles, and categorizes scene hierarchies using Colorful Hierarchy Category GameObject (MStudio.ColorfulHierarchy). Covers ColorPalette configuration, header prefixes (---, ===, ###), text styling, and background color coding for complex scenes.
---

# Colorful Hierarchy Skill

This skill guides organizing, color-coding, and structuring Unity scene hierarchies using **Colorful Hierarchy Category GameObject** (`MStudio` namespace).

## Core Concepts & Header Formatting

In large scenes, finding cameras, lighting, managers, UI, and gameplay entities can be challenging. Colorful Hierarchy formats GameObjects in the Hierarchy window based on naming prefixes defined in `ColorPalette.asset`:

| Prefix Pattern | Hierarchy Style | Recommended Category | Example GameObject Name |
| :--- | :--- | :--- | :--- |
| `=== Name ===` | Bold center-aligned text, full background color band | Major Root Categories | `=== MANAGERS ===`, `=== ENVIRONMENT ===` |
| `--- Name ---` | Subheader style, dark contrasting background | Subcategories | `--- Lighting & Volumes ---`, `--- Audio Emitters ---` |
| `### Name ###` | Accent colored indicator | Critical Singletons / Debug Tools | `### GameDirector ###`, `### CheatConsole ###` |

---

## 1. Scene Organization Blueprint

```text
=== MANAGERS ===
├── GameManager
├── AudioManager
└── EventBroker
=== LIGHTING & ENVIRONMENT ===
├── Directional Light
├── Global PostProcessing Volume
└── Static Geometry
=== GAMEPLAY ACTORS ===
├── Player (KCC Rig)
├── EnemySpawner
└── LootContainers
=== UI & CANVAS ===
├── MainHUD_Canvas
└── VirtualJoystick_Canvas
```

---

## Detailed References
- [Hierarchy Organization Standards & Color Palette Customization](file:///d:/Unity%20Projects/mini_game/.agents/skills/colorful-hierarchy/references/hierarchy-organization-guide.md)
