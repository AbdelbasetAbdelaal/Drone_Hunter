"""
================================================================================
          DRONE HUNTER 2D - ENCOUNTER SYSTEM (Phase 2A–2D & Phase 8)
================================================================================
Lightweight data-driven encounter director managing structured combat tests
and sequential enemy wave introductions with safe world-space spawn placement.

Supports:
  - Phase 2A: Scout Recon Encounter (legacy dict config)
  - Phase 2B: Shooter Positioning Encounter (legacy dict config)
  - Phase 2C: Heavy Target Priority Encounter (legacy dict config)
  - Phase 2D: Mixed 2-4 enemy compositions (list-based)
  - Phase 8:  9 expanded tactical wave compositions used across all 25 missions

Config formats:
  dict  (_is_legacy = True)  → single enemy_type with count, spawn/respawn delay
  list  (_is_legacy = False) → ordered sequence of TARGET_TYPE strings, 1 per spawn slot
"""

import math
import random
import pygame
from src.data.settings import WORLD_WIDTH, WORLD_HEIGHT
from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE,
    SCOUT_SCORE, SHOOTER_SCORE, HEAVY_SCORE
)
from src.entities.enemy import Enemy

# =============================================================================
# LEGACY DICT-BASED ENCOUNTERS (Phase 2A / 2B / 2C intro encounters)
# Used by: CombatDirector default fallback, save_system, progression_system
# =============================================================================
SCOUT_INTRO_ENCOUNTER = {
    "name": "Scout Recon Encounter",
    "enemy_type": TARGET_TYPE_SCOUT,
    "count": 3,
    "spawn_delay": 0.5,
    "respawn_delay": 1.0,
}

SHOOTER_INTRO_ENCOUNTER = {
    "name": "Shooter Positioning Encounter",
    "enemy_type": TARGET_TYPE_SHOOTER,
    "count": 1,
    "spawn_delay": 1.5,
    "respawn_delay": 1.0,
}

HEAVY_INTRO_ENCOUNTER = {
    "name": "Heavy Target Priority Encounter",
    "enemy_type": TARGET_TYPE_HEAVY,
    "count": 1,
    "spawn_delay": 1.5,
    "respawn_delay": 1.0,
}

# =============================================================================
# PHASE 2D LIST-BASED COMPOSITIONS (mixed 2–4 enemy encounters)
# Used by: CombatDirector default sequence, test_phase2d_encounters,
#          test_phase2e_combat_director, test_phase4_progression
# =============================================================================
SCOUT_SHOOTER_ENCOUNTER = [
    TARGET_TYPE_SCOUT,
    TARGET_TYPE_SHOOTER
]

SCOUT_HEAVY_ENCOUNTER = [
    TARGET_TYPE_HEAVY,
    TARGET_TYPE_SCOUT
]

SHOOTER_HEAVY_ENCOUNTER = [
    TARGET_TYPE_HEAVY,
    TARGET_TYPE_SHOOTER
]

SCOUT_SHOOTER_HEAVY_ENCOUNTER = [
    TARGET_TYPE_HEAVY,
    TARGET_TYPE_SHOOTER,
    TARGET_TYPE_SCOUT
]

# =============================================================================
# PHASE 8 EXPANDED TACTICAL WAVE COMPOSITIONS
# Used by: all 25 campaign missions in mission_data.py
# Each list entry is spawned sequentially (1 enemy per second)
# =============================================================================
WAVE_SCOUTS_PATROL      = [TARGET_TYPE_SCOUT, TARGET_TYPE_SCOUT, TARGET_TYPE_SCOUT]
WAVE_SCOUTS_ASSAULT     = [TARGET_TYPE_SCOUT, TARGET_TYPE_SCOUT, TARGET_TYPE_SCOUT, TARGET_TYPE_SCOUT]
WAVE_SCOUTS_SWARM       = [TARGET_TYPE_SCOUT, TARGET_TYPE_SCOUT, TARGET_TYPE_SCOUT, TARGET_TYPE_SCOUT, TARGET_TYPE_SCOUT]

WAVE_SHOOTERS_PAIR      = [TARGET_TYPE_SHOOTER, TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER]
WAVE_SHOOTERS_SQUAD     = [TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_SCOUT]

WAVE_HEAVY_ESCORT       = [TARGET_TYPE_SCOUT, TARGET_TYPE_HEAVY, TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER]
WAVE_HEAVY_BATTLEGROUP  = [TARGET_TYPE_SCOUT, TARGET_TYPE_HEAVY, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_SCOUT]

WAVE_SHIELD_VANGUARD    = [TARGET_TYPE_SCOUT, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SHOOTER, TARGET_TYPE_SCOUT]
WAVE_ELITE_STRIKE_FORCE = [TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_HEAVY, TARGET_TYPE_SHOOTER, TARGET_TYPE_SHOOTER, TARGET_TYPE_SCOUT]

# =============================================================================
# MEANINGFUL DETERMINISTIC ENEMY FORMATIONS
# =============================================================================
FORMATION_V         = "FORMATION_V"
FORMATION_WEDGE     = "FORMATION_WEDGE"
FORMATION_LINE      = "FORMATION_LINE"
FORMATION_STAGGERED = "FORMATION_STAGGERED"
FORMATION_FLANK     = "FORMATION_FLANK"
FORMATION_ESCORT    = "FORMATION_ESCORT"

FORMATION_OFFSETS = {
    FORMATION_V: [
        (0.0, 0.0),
        (-90.0, -70.0),
        (90.0, -70.0),
        (-180.0, -140.0),
        (180.0, -140.0),
        (-270.0, -210.0),
        (270.0, -210.0),
    ],
    FORMATION_WEDGE: [
        (0.0, -80.0),
        (-80.0, 50.0),
        (80.0, 50.0),
        (-160.0, 100.0),
        (160.0, 100.0),
    ],
    FORMATION_LINE: [
        (-180.0, 0.0),
        (-90.0, 0.0),
        (0.0, 0.0),
        (90.0, 0.0),
        (180.0, 0.0),
    ],
    FORMATION_STAGGERED: [
        (0.0, 0.0),
        (-110.0, 60.0),
        (110.0, -60.0),
        (-220.0, 120.0),
        (220.0, -120.0),
    ],
    FORMATION_FLANK: [
        (-160.0, -40.0),
        (160.0, -40.0),
        (-240.0, 60.0),
        (240.0, 60.0),
        (0.0, -120.0),
    ],
    FORMATION_ESCORT: [
        (0.0, 0.0),        # Center priority vessel (Heavy / Shield)
        (-120.0, 50.0),    # Left flank escort
        (120.0, 50.0),     # Right flank escort
        (-200.0, -40.0),   # Forward scout
        (200.0, -40.0),    # Forward scout
    ],
}


class EncounterSystem:
    """Manages deterministic sequential and simultaneous tactical formations and encounters."""
    def __init__(self, config=None, enabled: bool = True):
        self.config = config if config is not None else SCOUT_INTRO_ENCOUNTER
        self.enabled = enabled
        self.state = "idle" # idle, waiting, active, complete
        
        self.active_enemies = []
        self.active_enemy = None # Legacy reference
        
        self.spawned_count = 0
        self.eliminated_count = 0
        self.timer = 0.0
        self.min_spawn_distance = 500.0
        self.current_formation = FORMATION_V
        self._spawn_anchor = (WORLD_WIDTH // 2, 200.0)

        self._setup_config(self.config)

    def _setup_config(self, config):
        self.config = config
        if isinstance(config, list):
            self.total_count = len(config)
            self._is_legacy = False
        else:
            self.total_count = config.get("count", 1)
            self._is_legacy = True
        self.current_formation = self._determine_formation(config)

    def _determine_formation(self, config) -> str:
        """Selects a deterministic formation structure based on composition archetype."""
        if isinstance(config, list):
            if any(t in (TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE) for t in config):
                return FORMATION_ESCORT
            elif len(config) >= 4:
                return FORMATION_WEDGE
            elif len(config) == 3:
                return FORMATION_V
            elif len(config) == 2:
                return FORMATION_FLANK
            return FORMATION_STAGGERED
        else:
            enemy_type = config.get("enemy_type", TARGET_TYPE_SCOUT) if isinstance(config, dict) else TARGET_TYPE_SCOUT
            if enemy_type == TARGET_TYPE_SCOUT:
                return FORMATION_V
            elif enemy_type == TARGET_TYPE_SHOOTER:
                return FORMATION_LINE
            elif enemy_type == TARGET_TYPE_HEAVY:
                return FORMATION_ESCORT
            return FORMATION_STAGGERED

    def set_encounter(self, config):
        """Swaps the active encounter configuration and resets state."""
        self._setup_config(config)
        self.reset()

    def start(self, config=None):
        """Explicitly starts the encounter into WAITING state with deterministic formation anchor."""
        if config is not None:
            self.set_encounter(config)
            
        self.state = "waiting"
        self.spawned_count = 0
        self.eliminated_count = 0
        self.active_enemy = None
        self.active_enemies = []
        self.current_formation = self._determine_formation(self.config)
        self._spawn_anchor = None
        
        if self._is_legacy:
            self.timer = self.config.get("spawn_delay", 0.5)
        else:
            self.timer = 0.5 # fixed 0.5s initial delay for compositions

    def reset(self):
        """Resets the encounter back to IDLE state."""
        self.state = "idle"
        self.spawned_count = 0
        self.eliminated_count = 0
        self.active_enemy = None
        self.active_enemies.clear()
        self.timer = 0.0
        self._spawn_anchor = None

    @property
    def is_active(self) -> bool:
        """True while the encounter is actively running and not yet complete."""
        return self.enabled and (self.state in ("waiting", "active"))

    @property
    def is_complete(self) -> bool:
        """True when all encounter enemies have been eliminated."""
        return self.state == "complete"

    @property
    def is_suppressing_spawner(self) -> bool:
        """Suppresses legacy random spawns while encounter is active."""
        return self.is_active

    def _find_spawn_position(self, player_pos: tuple[float, float], slot_idx: int = 0) -> tuple[float, float]:
        """Calculates a safe spawn position using deterministic formation offsets from anchor."""
        px, py = player_pos
        if self._spawn_anchor is None:
            # Establish primary anchor
            for _ in range(25):
                angle = random.uniform(0, 2 * math.pi)
                dist = random.uniform(self.min_spawn_distance, self.min_spawn_distance + 240.0)
                ax = px + math.cos(angle) * dist
                ay = py + math.sin(angle) * dist
                ax = max(180.0, min(WORLD_WIDTH - 180.0, ax))
                ay = max(180.0, min(WORLD_HEIGHT - 180.0, ay))
                if math.hypot(ax - px, ay - py) >= self.min_spawn_distance:
                    self._spawn_anchor = (ax, ay)
                    break
            if self._spawn_anchor is None:
                self._spawn_anchor = (120.0 if px > WORLD_WIDTH // 2 else WORLD_WIDTH - 120.0,
                                      120.0 if py > WORLD_HEIGHT // 2 else WORLD_HEIGHT - 120.0)

        # Apply deterministic formation offset
        offsets = FORMATION_OFFSETS.get(self.current_formation, FORMATION_OFFSETS[FORMATION_V])
        off_x, off_y = offsets[slot_idx % len(offsets)]
        sx = max(80.0, min(WORLD_WIDTH - 80.0, self._spawn_anchor[0] + off_x))
        sy = max(80.0, min(WORLD_HEIGHT - 80.0, self._spawn_anchor[1] + off_y))
        return (sx, sy)

    def _clean_active_enemies(self, ctx):
        """Removes dead enemies from active_enemies tracking array."""
        alive = []
        for e in self.active_enemies:
            if e.alive and e in ctx.target_group:
                alive.append(e)
            else:
                self.eliminated_count += 1
                if self.active_enemy == e:
                    self.active_enemy = None
        self.active_enemies = alive

    def update(self, dt: float, ctx) -> bool:
        """Updates encounter progression timer and triggers enemy spawns."""
        if not self.enabled or self.state not in ("waiting", "active"):
            return False

        p_pos = (ctx.player.pos.x, ctx.player.pos.y) if ctx.player else (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

        self._clean_active_enemies(ctx)

        if self.state == "waiting":
            self.timer -= dt
            if self.timer <= 0:
                if self.spawned_count < self.total_count:
                    spawn_pos = self._find_spawn_position(p_pos, slot_idx=self.spawned_count)
                    
                    if self._is_legacy:
                        enemy_type = self.config.get("enemy_type", TARGET_TYPE_SHOOTER)
                    else:
                        enemy_type = self.config[self.spawned_count]
                        
                    enemy = Enemy(enemy_type=enemy_type, pos=spawn_pos, sector_idx=ctx.current_sector_idx,
                                  hp_multiplier=getattr(ctx, "ng_plus_enemy_hp_mult", 1.0))
                    ctx.target_group.add(enemy)
                    
                    self.active_enemies.append(enemy)
                    self.active_enemy = enemy # Legacy fallback
                    self.spawned_count += 1
                    
                    if self._is_legacy:
                        self.state = "active"
                    else:
                        if self.spawned_count < self.total_count:
                            self.timer = 0.85 # Snappy 0.85s between_spawn_delay for readable unit arrival
                        else:
                            self.state = "active"
                else:
                    self.state = "active"

        elif self.state == "active":
            if self._is_legacy:
                if self.active_enemy is None:
                    if self.spawned_count < self.total_count:
                        self.state = "waiting"
                        self.timer = self.config.get("respawn_delay", 1.0)
                    else:
                        self.state = "complete"
            else:
                if self.spawned_count >= self.total_count and len(self.active_enemies) == 0:
                    self.state = "complete"

        return self.is_complete
