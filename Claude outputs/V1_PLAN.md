# Dino Park Tycoon: V1 Plan

Version 2.1 (4 Nov 2026). V1 = friends-and-family playable test build, not the full game.

## 1. Success statement

A player opens the game, understands the park in two minutes, cares for a dinosaur, earns visitor income, and wants to return tomorrow.

## 2. In V1

- One island, ocean border, bounded camera
- Nine species (below), babies for three
- Essential visitor, food, care and staff buildings
- Background vehicles
- One scripted random event
- Economy, visitor rating, needs, care
- Cloud save
- Optional rewarded ads, one remove-ads purchase
- Neutral age screen, child-safe ads, parental gate for purchases

## 3. Postponed

Multiple islands; full sea park and sky park; Velociraptor; Spinosaurus; genetics lab and hybrids; marketplace; global chat; friend visits; contracts, seasons, live-ops; photo mode; first-person walk; Founder's Legacy; 19-incident system.

## 4. Roster

| Animal | Babies | Home |
|---|---|---|
| Triceratops | Yes | Standard paddock |
| Stegosaurus | Yes | Standard paddock |
| Brachiosaurus | Yes | Open range |
| Ankylosaurus | No | Standard paddock |
| Maiasaura | No | Standard paddock |
| Diplodocus | No | Open range |
| Tyrannosaurus rex | No | Heavy paddock |
| Pteranodon | No | Aviary |
| Mosasaurus | No | Deep tank |

## 5. Buildings

Must have: entrance gate and ticket booth; paths and plazas; benches, bins, lamps; restroom; souvenir shop; ice-cream kiosk or cafe; viewing deck; standard paddock; open range; heavy predator paddock; feeder and trough; shelter; hospital/vet; hatchery; Mosasaurus tank; Pteranodon aviary; bus stop.

If time allows: hotel, admin, research center, power station, vehicle depot (hangar).
Deferred: helipad, feeding-show stadium, genetics lab, landmark tower.

## 6. Vehicles

Must: safari bus, supply truck, vet jeep. Strong addition: arrival bus or ferry. Deferred: helicopter, plane, rescue truck, boat tour. Background life only, no schedules, fuel or repairs.

## 7. The one event: T. rex fence stress

Not in first 10 minutes. Telegraphed. Never deletes progress. Visitors scared, never harmed.

Flow: warning, fence integrity drops, alert with map marker and timer, player picks vet jeep (calm), repair fence, or distract with food, then resolution and a report card (what happened, cost, how to prevent).

| Response | Result |
|---|---|
| Quick correct | Calms, small cost, visitors impressed |
| Slow | Fence damaged, repair cost, rating dips |
| Ignored | Staff fix it at higher cost, no permanent loss |
| Long-term fix | Better fence, space, food, shelter lower future risk |

## 8. Schedule

Original assumption: 5 to 6 focused hours per day, 12 weeks. At 3 to 4 hours per day, plan 16 to 19 weeks, or cut earlier.

| Weeks (at 5-6 h/day) | Goal |
|---|---|
| 1-2 | Island, ocean border, camera bounds, tiles, paths, save |
| 3-4 | Triceratops full loop: paddock, food, water, needs, care, visitor income |
| 5-6 | Stegosaurus, Brachiosaurus, open range, safari bus, babies, hatching |
| 7-8 | T. rex, heavy paddock, event, vet/hospital loop |
| 9-10 | Mosasaurus tank, Pteranodon aviary |
| 11-12 | Shops, UI polish, onboarding, performance, friend testing |

Hotel moved out of weeks 11-12 into the first update (see open questions).

Build order: terrain and camera; one animal and enclosure; needs and care; visitors and money; more herbivores and range; babies and hatchery; predator and event; sea and sky; shops, polish, testing.

## 9. Cut order

1 Hotel, 2 Pteranodon aviary, 3 Mosasaurus tank, 4 safari route, 5 extra visitor types, 6 advanced decoration, 7 research center, 8 admin building.

Never cut: cloud save, animal needs, visitor income, onboarding, performance, Triceratops core loop.

## 10. Testing

5 to 10 Android devices including one low-end and one old phone, different screens and connections. 10-minute unassisted play. Track: understood first two minutes; first animal placed quickly; understood needs; returned next day; smooth; no lost progress; watched a rewarded ad voluntarily; tried things the game did not allow; identified buildings instantly; favourite animals.

Strong signals: loop understood without long tutorial, day-1 return, acceptable low-end performance, buildings identifiable by silhouette, voluntary care actions, requests for more content.

Stop adding content if: first session confusing, weak day-1 retention, stutter/heat on mid-range phones, lost progress, buildings indistinguishable, care feels like chores.

## 11. Monetization

Rewarded ads only, plus one remove-ads purchase. No interstitials in emergencies, no forced ads, no loot boxes, no paid power or stability. Placements: double offline income, skip a clearing job, speed one hospital stage, temporary visitor boost, free enrichment item, last minutes of an egg hatch. Reward granted immediately; hide the button if the ad fails to load; cap frequency; never during events or right after a purchase; rewarded ads stay after remove-ads.

## 12. Compliance

Neutral age screen, child-safe ad config, no behavioural profiling of children, no location tracking, no open chat, no public user text, parental gate on purchases, privacy policy, account deletion route, accurate age-rating and data-safety forms. Mixed-audience, child-safe by default. Have a compliance specialist review before public launch.

## 13. Decisions and recommendations on open questions

| Question | Recommendation (not yet decided by you) |
|---|---|
| Hotel in test build? | First update. It is the first cut and needs night-cycle work. |
| Mosasaurus feeding show? | Viewing tank only. Show adds animation, scheduling, stadium. |
| Aviary walk-in or viewing? | Viewing-only in V1; walk-in later. |
| Admin building functional? | Visual only in V1. |
| First post-V1 update | Spinosaurus, since the water tech from Mosasaurus is reusable; Velociraptor needs new roof/escape AI. Your call. |
