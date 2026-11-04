---
name: dino-park-v1-scope
description: Scope guard for Dino Park Tycoon V1 (friends-and-family test build). Use when deciding whether a feature, animal, building or vehicle belongs in V1, planning the schedule, or choosing what to cut.
---

# Dino Park Tycoon: V1 Scope Guard

V1 is a friends-and-family test build. Goal: a player understands the park in two minutes, cares for a dinosaur, earns visitor income, and wants to return tomorrow.

## In
One island with ocean border and bounded camera. Nine species: Triceratops, Stegosaurus, Brachiosaurus, Ankylosaurus, Maiasaura, Diplodocus, T. rex (only predator), Pteranodon (aviary), Mosasaurus (tank). Babies only for Triceratops, Stegosaurus, Brachiosaurus. Vehicles: safari bus, supply truck, vet jeep (+ arrival bus/ferry if time). One event: T. rex fence stress. Cloud save, needs, economy, rewarded ads, one remove-ads purchase, age screen, parental gate.

## Out (postponed)
Multiple islands, full sea/sky parks, Velociraptor, Spinosaurus, genetics lab and hybrids, marketplace, chat, friend visits, seasons/contracts, photo mode, first-person walk, Founder's Legacy, 19-incident system, helicopter, plane, rescue truck, boat tour.

## Buildings
Must: entrance and ticket booth, paths, benches/bins/lamps, restroom, souvenir shop, kiosk or cafe, viewing deck, standard paddock, open range, heavy paddock, feeder/trough, shelter, hospital/vet, hatchery, Mosasaurus tank, Pteranodon aviary, bus stop.
If time: hotel, admin, research center, power station, vehicle depot. Deferred: helipad, stadium, genetics lab, landmark tower.

## Decision test for a new idea
1. Does it serve the two-minute loop or day-1 return? If no, postpone.
2. Does it need new systems (AI, water, flight, scheduling)? If yes, postpone.
3. Is it already in the cut list? Respect the order.

## Cut order
Hotel, Pteranodon aviary, Mosasaurus tank, safari route, extra visitor types, advanced decoration, research center, admin building.
Never cut: cloud save, animal needs, visitor income, onboarding, performance, Triceratops loop.

## Schedule
12 weeks at 5 to 6 h/day (terrain/save; Triceratops loop; more herbivores + babies; T. rex + event; sea and sky; polish + testing). At 3 to 4 h/day, plan 16 to 19 weeks.

## Event rules
Not in first 10 minutes, telegraphed, never deletes progress, visitors never harmed, report card explains cause and fix.

## Ads and safety
Rewarded only, immediate reward, hide button if ad fails, never in emergencies or right after purchase. Child-safe by default; legal review before public launch.

Full details: V1_PLAN.md.

## Studio framework hooks
- Run `/scope-check` on any new feature against this list, and `/gate-check` before changing stage. `producer` owns cut decisions; the developer approves.
- Plan work with `/sprint-plan` and `/estimate` using 3 to 4 h/day (16 to 19 weeks), not 5 to 6. Check done work with `/story-done`.
- Pre-test: `/perf-profile` on a low-end Android, `/playtest-report` after each friend session, `/qa-plan` before the test build. Ads and child safety: ask `economy-designer` and `security-engineer`, then a compliance specialist before public launch.
