# Scene Hierarchy Styling and Organization Guidelines

This rule establishes technical standards for scene hierarchy readability and category organization using **Colorful Hierarchy Category GameObject** (`MStudio`).

## Core Directives

1. **Standardized Category Prefixes**:
   - Organize scene roots using standardized prefixes mapped in `ColorPalette.asset`:
     - `=== MANAGERS ===`: Global singletons, input systems, audio mixers.
     - `=== ENVIRONMENT ===`: Static level geometry, lighting, terrain, navmesh surfaces.
     - `=== GAMEPLAY ===`: Dynamic actors, spawners, interactable objects, hazards.
     - `=== UI ===`: Canvases, HUD elements, virtual joysticks, event systems.
     - `--- Subcategory ---`: Logical subsections within a major category.

2. **Clean Organizational Transform Standards**:
   - Header/category GameObjects must strictly serve as organizational containers:
     - Reset transform to position `(0, 0, 0)`, rotation `(0, 0, 0)`, and scale `(1, 1, 1)`.
     - Remove any default `Collider`, `MeshRenderer`, or `MeshFilter` components.
