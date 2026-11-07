# TRN v02 Reference Analysis + Production Brief (blender-skills-pack: blender-director > reference-image-match)
Date 4 Nov 2026. Project docs win over the pack (DESIGN_BIBLE, BUILD_ORDER): tiles 2x2 m, 0.4 m thick, pivot top-centre, names TRN_*.

## Shared (all sets)
- Camera: orthographic 3/4 iso from front-left, ~35 deg above ground (true iso 54.74/-45) = DESIGN_BIBLE default camera. Locked for every set.
- Lighting in every reference: soft key from upper-left, light fill, no hard black; soft contact shadow under each object.
- Style: hand-painted stylized (hand-painted-style + stylized-style): values painted in albedo (lit tops pale, sides darker), broad brush strokes, soft bevels that catch light, thin dark outline (inverted hull, Unity-portable), matte except water/mud.
- Budget: these .blend files are LOD0 source (5k-30k tris). Game LODs baked later (lod-pipeline, texture-workflow). Texture 1024 per set atlas.
- Active skills: blender-director, environment-artist, hand-painted-style, stylized-style, isometric-style, materials, lighting, vfx-fx (water/mist/smoke), qa-review.

## TRN_LevelledPads
Palette: earth #B08850 / #8E6A3C / #C9A46B; curb cream #E2DCC8 / grime #8C8470; gravel #9A9A98 / #6E6E6C / #C4C4C0.
Hero: earth pad with long horizontal brush strokes and 2-3 shallow cracks, chipped edge; gravel bed of distinct pebbles inside a rounded cream curb with grime at the foot.
Gap vs v01: gravel was flat noise, curb too clean, no cracks or chips.

## TRN_Slopes
Palette: grass #6E9A2E / #86AE3A / #557A22; sand band #C9A46B; soil strata #8B5A2E / #A9743F / #6B4422; sleeper timber #3A3D34 / #55594B.
Hero: ramp with sandy lip; valley with green dip and sand floor; stairs with 6 chunky worn sleepers + two side stringers, grass tufts in every step, stepped soil sides with grass overhang.
Gap vs v01: flat soil sides, no strata depth, sleepers plain boxes, no grass overhang.

## TRN_VolcanoIsland
Palette: basalt #2A2826 / #3A3633 / #4A443F; ash #6B6763; char rim #5A2A14; lava core #FFD36A, mid #FF8A1E, edge #C9380E.
Hero: cracked plates each with own tone, domed tops, charred orange-brown edges, deep glowing cracks graded yellow>orange>red; lava rocks with glowing veins; mini volcano with ridged flanks, lava streams, crater glow and smoke.
Gap vs v01: plates uniform, cracks one colour, no charring, no smoke.

## TRN_SwampIsland
Palette: peat #1E1F18 / #2C2C22; moss #3F6A22 / #5C8A2E / #2C4A18; dry leaves #7A4A22 / #A0652C / #5A3418; pool algae #3E7A3A, water #2E5A3E; marsh mud #3A3328, marsh water #6F8FA8.
Hero: black wet soil, raised moss clumps, scattered curled dry leaves and twigs, ferns; pool with organic (not square) shoreline, mossy overhanging banks, algae rafts; marsh with glossy grey mud, blue sky-reflecting puddles, reeds and cattails.
Gap vs v01: square pool, flat moss, few leaves, matte mud.

## TRN_DesertIsland
Palette: sand #D9894A / #E6A35E / #C2703A; pink sand #D99A8A; sandstone bands #C46A3A / #E0A060 / #B85A50 / #F0C080.
Hero: wind ripples, dune crest with sharp slip face, layered sandstone mesas with stacked ledges, overhangs and cracks, arch.
Gap vs v01: mesas pale stacked pancakes, dunes smooth without slip-face shading.

## TRN_BeachShore
Palette: dry sand #E8D2A2 / #D9BE86; wet sand #B89A68; shallow water #6FD0CF, mid #2FA3B5, deep #1A7A95; foam #FFFFFF.
Hero: turquoise-to-blue depth gradient, white foam lines along shore and wave crests, darker wet-sand band, shells, water volume visible on tile side.
Gap vs v01: single flat cyan, one foam line, no wet band.

## TRN_Ponds
Palette: water shallow #4FB5A8, deep #1E6E6A; ripple strokes #BDEDE4; bank #8E6A3C / #B08850; moss #5C8A2E; stones #8E8C86.
Hero: organic kidney shapes, raised earthen rim with inner bank wall, white swirl ripple strokes, darker deep centre, flat stacked stones on rim, reed and cattail clumps, grass bits.
Gap vs v01: flat water, no ripples, thin rim, few stones.

## TRN_River
Palette: water #3AA6C0 / #1E7F9E / shallow #7BD3D6; flow strokes #E6F7F8; banks #A9743F / olive grass #7E8A3A.
Hero: channel with steep cut banks, water face visible on tile edges, white flow lines along current, foam at bends and junction, spring with rock pile mini-fall and ripple rings, river mouth fanning into beach with foam.
Gap vs v01: water single tone, no flow strokes, weak banks.

## TRN_Waterfalls
Palette: falling water #BFEFF0 / #7CC9CF / streak white; pool #3E9FAE; mist white 60 %; rocks #7A766E moss #4E7A2A; cliff soil #7A5A3C.
Hero: rock-pillar walls stacked from mossy boulders, layered fall sheets with vertical white streaks, central splitting rock (big fall), white splash foam and volumetric mist at the base, ripple rings in the pool, wet darker rocks.
Gap vs v01: two flat sheets, no mist, rocks generic.

## Visual match method
Render each set at the locked camera, place beside its reference, rate the visual-match-checklist categories; fix the top 5 gaps; max 3 passes per set; pass at 8/10.
