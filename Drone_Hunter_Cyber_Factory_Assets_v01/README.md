# Drone Hunter 2D — Cyber Factory Asset Pack v0.1

This pack was extracted from the generated **Cyber Factory master sheet** for the
Drone Hunter 2D PC project.

## Structure

- `floor/` — floor panels, grates, hazard floor pieces
- `reactors/` — reactor and power-core concepts
- `machinery/` — turbine, generator, cooling unit, fabricator
- `structures/` — walls, doors, gates, platforms
- `pipes/` — modular pipes and conduits
- `barriers/` — energy barriers, pillars, fences, shield generator
- `props/` — crates, barrels, cables, scrap, toolbox
- `vents/` — vents, fans, grilles
- `hazards/` — hazard stripes, arrows, warning signs
- `effects/` — steam, sparks, energy effects
- `lights/` — warning lights and indicators
- `reference/` — original master sheet

## Important production note

These files are **source-sheet extraction crops**, not final hand-cleaned transparent
sprites. The source artwork was generated as a visual asset sheet, so some crops
retain the sheet's backdrop/halo.

Use this pack first for:
1. visual integration,
2. level composition,
3. sizing,
4. art-direction validation.

Before shipping the game, selected assets should be individually alpha-cleaned or
regenerated as standalone transparent PNGs.

## Recommended first integration set

1. `floor/floor_01.png`
2. `floor/floor_grate.png`
3. `reactors/reactor_01.png`
4. `machinery/turbine_01.png`
5. `machinery/generator_01.png`
6. `structures/wall_01.png`
7. `pipes/pipe_straight.png`
8. `pipes/pipe_corner.png`
9. `barriers/energy_barrier_blue.png`
10. `props/crate_01.png`
11. `vents/vent_01.png`
12. `hazards/hazard_stripe_01.png`
13. `lights/warning_beacon.png`

## Next engineering step

Do not put the entire master sheet into the game.

The intended architecture is:

`EnvironmentRenderer -> individual environment PNG assets -> Camera -> World`

The existing player, camera, HUD, and gameplay systems should remain unchanged.
