# Dino Park Tycoon: Claude Code context

@AGENTS.md
@GAME_DESIGN.md

## Where things live (save everything here)
This folder is the whole project. Anything Claude produces for the game is saved inside it, never only in chat:
- Code: `Assets/Scripts`
- Art source (Blender files, renders, component notes): `_Source/Blender`
- Design decisions: `GAME_DESIGN.md` (update it when a decision changes)
- Asset licenses: `ASSET_LICENSES.md` (log every new pack)
- Reference images and prompts: `Assets/Concepts`
- Rules and skills for agents: `.agents/rules`, `.agents/skills`
- Never edit generated folders: `Library`, `Temp`, `Logs`, `UserSettings`.
- `_Reference` is read-only.

## Working rules
- Small tasks. End each task with "How to test".
- Building component kit: list is in `_Source/Blender/COMPONENTS.md`. Add new components there and in `AGENTS.md`.
- Same-size common parts across buildings (e.g. solar panel 1.6 x 1.0 m) so building sizes read clearly.
- Commit work to git in small commits; remote is `praviharaneranjana/Dinosaur_Park` on GitHub.
