# 🛠️ Contributing to Drone Hunter 2D

Thank you for your interest in contributing to **Drone Hunter 2D**!

---

## 🔒 Golden Rules & Architecture Constraints

1. **100% 2D Constraint (Strict)**:
   - All rendering must strictly use Pygame Surfaces, 2D transparent PNGs, and 2D trigonometry.
   - 3D engines (OpenGL 3D, Blender meshes, Unity) are **strictly forbidden**.

2. **Frozen Gameplay Contract**:
   - Do **NOT** modify existing hitboxes, physics constants, weapon stats, enemy AI timings, or mission structures without explicit alignment.
   - The 25-mission progression and 5 Boss encounters must remain stable.

3. **Production Asset Standards**:
   - Sprites must have 100% clean alpha transparency (no concept sheet borders, annotations, white boxes, or gray backgrounds).
   - Sprites are managed exclusively through SpriteManager with 2-degree rotation caching.
   - Shadows must remain unrotated on Layer 1.

4. **Zero-Disk I/O During Gameplay**:
   - All asset loading and surface creation must happen at startup or level transition — never inside the per-frame update() or ender() loops.

---

## 🧪 Testing & Verification

Before submitting any code changes, ensure all tests pass:

`ash
# 1. Compile check all modules
python -m compileall drone_hunter_pc

# 2. Run the complete automated test suite (314 tests)
pytest drone_hunter_pc/tests -v
`

All 314 tests must pass green with zero regressions.

---

## 📁 Repository Organization

- drone_hunter_pc/src/core/: Game state, central game context container, engine loop.
- drone_hunter_pc/src/data/: Authoritative catalogs (gameplay constants, 25 missions, bosses).
- drone_hunter_pc/src/entities/: Player, enemies, bosses, projectiles, obstacles.
- drone_hunter_pc/src/rendering/: SpriteManager, player renderer, camera, particle engine.
- drone_hunter_pc/src/systems/: Combat director, encounter waves, mission lifecycle, progression, save system.
- drone_hunter_pc/src/ui/: In-game HUD, menus, hangar upgrade store.
- drone_hunter_pc/tests/: Automated unit, integration, and performance regression tests.
