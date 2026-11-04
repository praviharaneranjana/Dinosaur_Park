# Dino Park Tycoon: Claude Code context

@AGENTS.md
@GAME_DESIGN.md

## Claude Code Game Studios (installed 4 Nov 2026)
Studio framework from Donchitos/Claude-Code-Game-Studios (MIT): 49 agents, ~74 skills, hooks and rules in `.claude/`. Config lives in `project.yaml` (engine: Unity 6000.6.7f1, C#, URP). Start Claude Code in this folder (hooks and deny rules only load from the project root), then run `/start` or `/help`.
- Collaboration protocol: Question -> Options -> Decision -> Draft -> Approval. Agents ask "May I write this to [path]?" before writing. No commits unless asked.
- Code root is `Assets/` (not `src/`). Scripts go in `Assets/Scripts/<System>/`, tests in `Assets/Tests/EditMode` and `PlayMode`.
- Path mapping: framework `docs/` = our `Docs/` (same folder on Windows; always write `Docs/`). Framework `assets/` = our `Assets/`. Design docs for systems go in `design/gdd/`, ADRs in `Docs/architecture/`, sprints and session state in `production/`.
- Existing art/scope docs stay the source of truth: `Docs/DESIGN_BIBLE.md` (do NOT regenerate with `/art-bible`; point it here), `Docs/BUILDING_IDENTITY.md`, `Docs/V1_PLAN.md` (use as input to `/scope-check`, `/sprint-plan`, `/gate-check`).
- Project skills (`dino-park-art-bible`, `dino-park-building-identity`, `dino-park-v1-scope`) live in `.agents/skills` and are mirrored in `.claude/skills`. Edit both together.
- Who to ask: `art-director` (style, silhouettes), `technical-artist` (Blender/FBX/URP, budgets), `unity-specialist` (C#/Unity APIs), `unity-ui-specialist` (mobile UI), `economy-designer` (ads, visitor income), `producer` (scope/schedule), `qa-lead` (device testing).
- Engine reference: `Docs/engine-reference/unity/` (pinned 6.3 LTS; we run 6000.6.7f1, so verify 6.4+ APIs).

@.claude/docs/coordination-rules.md
@.claude/docs/coding-standards.md
@Docs/engine-reference/unity/VERSION.md

## Where things live (save everything here)
This folder is the whole project. Anything Claude produces for the game is saved inside it, never only in chat:
- Code: `Assets/Scripts`
- Art source (Blender files, renders, component notes): `_Source/Blender`
- Design decisions: `GAME_DESIGN.md` (update it when a decision changes)
- Asset licenses: `ASSET_LICENSES.md` (log every new pack)
- Reference images and prompts: `Assets/Concepts`
- Rules and skills for agents: `.agents/rules`, `.agents/skills`; studio agents/skills/hooks in `.claude/` (do not hand-edit hooks)
- Never edit generated folders: `Library`, `Temp`, `Logs`, `UserSettings`.
- `_Reference` is read-only.

## Working rules
- Small tasks. End each task with "How to test".
- Building component kit: list is in `_Source/Blender/COMPONENTS.md`. Add new components there and in `AGENTS.md`.
- Same-size common parts across buildings (e.g. solar panel 1.6 x 1.0 m) so building sizes read clearly.
- Commit work to git in small commits; remote is `praviharaneranjana/Dinosaur_Park` on GitHub.
