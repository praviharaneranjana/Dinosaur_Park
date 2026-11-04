# V2 to V2.1 Changelog (4 Nov 2026)

## Research changes (Dino-Park-Tycoon-Updated-Research-V2.1.md)

1. Building-identity rules split into Tier A (landmarks: unique roofline + material + silhouette) and Tier B (small services: unique silhouette + roofline). The V2 rule was unachievable and V2's own table broke it.
2. Table fixes: restroom now mono-pitch roof; hospital L-shaped, pale sage panels, helipad ring; admin stepped roof + tower; souvenir shop primary is honey timber; kiosk pastel painted panels; hatchery low dome with amber-cream plaster; genetics lab tall tower with domed crown (so it no longer clashes with hatchery or the barrel-vault hangar).
3. Vehicle depot (Hangar) added to "if time allows" buildings, since it is already built and gives bus, truck and jeep a home.
4. Schedule note: 12 weeks assumes 5 to 6 h/day; at 3 to 4 h/day expect 16 to 19 weeks.
5. New section 17a: risks and recommendations on the five open questions.

## New files

| File | Purpose |
|---|---|
| DESIGN_BIBLE.md | Single source of truth for art, scale and rules |
| BUILDING_IDENTITY.md | Tier matrix, kit parts, silhouette test, Gemini template |
| V1_PLAN.md | Scope, roster, buildings, event, schedule, cut order, tests, ads, compliance |
| V2_CHANGELOG.md | This file |
| skills/dino-park-art-bible/SKILL.md | Claude skill for art work |
| skills/dino-park-building-identity/SKILL.md | Claude skill for building concepts |
| skills/dino-park-v1-scope/SKILL.md | Claude skill for scope decisions |

## Memory changes

- V1 scope entry replaced: the old "everything is V1 / sea park, sky animals and hybrids in V1 / Triceratops Valley" is superseded by the V2 test-build scope.
- Added: art bible and tier rule, kit and built-building status (Souvenir shop, Hangar), list of new docs.

## My view

Strong: cutting to one island, nine animals, one predator and one event is the right call. The care-first loop is the product; content can follow.

Concerns:
- 17 must-have buildings each needing unique architecture is the biggest hidden cost. Budget about 1 to 2 days per Tier B shell and 3 to 4 per Tier A.
- Mosasaurus tank and Pteranodon aviary are cheap to cut and should stay early in the cut order.
- Hospital + vet jeep + fence event + care loop is a lot of coupled systems in weeks 7 to 8. Protect that time.
- Test with the silhouette test on real people (3 testers, 3 seconds) before modelling Tier A.

Next steps: export Souvenir shop and Hangar to Unity and check them on a low-end phone to validate the triangle budget; do silhouette tests on the Tier A concepts; copy these docs into _Source/ in the Unity repo.
