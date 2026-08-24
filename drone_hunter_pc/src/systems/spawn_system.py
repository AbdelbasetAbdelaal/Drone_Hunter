"""
================================================================================
                    DRONE HUNTER 2D - SPAWN & WAVE MANAGER
================================================================================
Coordinates tactical wave progressions, regular enemy group formations,
and environmental hazards.
"""

import math
import random
import pygame
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT, WORLD_WIDTH, WORLD_HEIGHT
from src.data.game_data import (
    TARGET_TYPE_STANDARD, TARGET_TYPE_FAST, TARGET_TYPE_ARMORED, TARGET_TYPE_SHOOTER,
    TARGET_TYPE_TURRET, TARGET_TYPE_VEHICLE, TARGET_TYPE_CHASER, TARGET_TYPE_SWARM,
    TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SNIPER,
    TARGET_TYPE_SCOUT, TARGET_TYPE_HEAVY,
    SECTORS
)
from src.entities.enemy import Enemy

class WaveManager:
    def __init__(self, target_score: int = 5000):
        self.target_score = max(500, target_score)
        self.current_wave = 1

    def update_wave(self, current_score: int) -> int:
        ratio = current_score / self.target_score
        if ratio < 0.25: self.current_wave = 1
        elif ratio < 0.60: self.current_wave = 2
        elif ratio < 0.90: self.current_wave = 3
        else: self.current_wave = 4

        return self.current_wave

    def is_stage_complete(self, current_score: int, targets_group=None) -> bool:
        return current_score >= self.target_score


class Spawner:
    def __init__(self, base_min_interval: float = 0.7, base_max_interval: float = 1.5):
        self.base_min_interval = base_min_interval
        self.base_max_interval = base_max_interval
        self.timer = 0.0
        self.next_interval = random.uniform(base_min_interval, base_max_interval)
        self.level = 1
        self.sector_idx = 0

    def reset_for_stage(self, level: int, sector_idx: int):
        self.level = level
        self.sector_idx = sector_idx
        self.timer = 0.0
        self.next_interval = random.uniform(self.base_min_interval, self.base_max_interval)

    def update(self, dt: float, context):
        """Spawns enemies, environmental obstacles, and hazards based on stage progress."""
        self.timer += dt
        current_wave = context.current_wave
        diff_data = context.difficulty_data
        hp_mult = diff_data.get("hp_mult", 1.0) * getattr(context, "ng_plus_enemy_hp_mult", 1.0)
        spd_mult = diff_data.get("speed_mult", 1.0)

        if self.timer >= self.next_interval:
            self.timer = 0.0
            interval_reduction = min(0.5, (self.level - 1) * 0.08 + (current_wave - 1) * 0.10)
            cur_min = max(0.4, self.base_min_interval - interval_reduction)
            cur_max = max(0.8, self.base_max_interval - interval_reduction)
            self.next_interval = random.uniform(cur_min, cur_max)

            # Spawn 1-3 enemies with formation support
            spawn_count = min(3, 1 + (current_wave >= 3 and random.random() < 0.50) + (current_wave >= 4 and random.random() < 0.30))
            formation = random.choice(["v_formation", "line", "wedge", "random"])
            base_pos = self._get_edge_spawn(formation if formation != "random" else "random")
            
            for i in range(spawn_count):
                e_type = self._select_enemy_type(current_wave)
                spd_bonus = (self.level - 1) * 6.0
                spawn_pos = self._apply_formation_offset(base_pos, i, spawn_count, formation)
                # Clamp spawn position to world bounds
                spawn_pos = (max(60.0, min(WORLD_WIDTH - 60.0, spawn_pos[0])), max(60.0, min(WORLD_HEIGHT - 60.0, spawn_pos[1])))
                enemy = Enemy(
                    enemy_type=e_type,
                    speed_bonus=spd_bonus,
                    level=self.level,
                    sector_idx=self.sector_idx,
                    hp_multiplier=hp_mult,
                    speed_multiplier=spd_mult,
                    pos=spawn_pos
                )
                context.target_group.add(enemy)

    def _select_enemy_type(self, current_wave: int) -> str:
        if self.sector_idx == 0:
            if current_wave == 1: return random.choice([TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER])
            elif current_wave == 2: return random.choice([TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY])
            else: return random.choice([TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE])

        elif self.sector_idx == 1:
            if current_wave <= 2: return random.choice([TARGET_TYPE_SCOUT, TARGET_TYPE_ARMORED, TARGET_TYPE_SHOOTER, TARGET_TYPE_SHIELD_DRONE])
            else: return random.choice([TARGET_TYPE_ARMORED, TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SHOOTER])

        elif self.sector_idx == 2:
            if current_wave <= 2: return random.choice([TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_SNIPER, TARGET_TYPE_SHIELD_DRONE])
            else: return random.choice([TARGET_TYPE_SNIPER, TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_ARMORED])

        else: # Sectors 3 & 4
            return random.choice([
                TARGET_TYPE_SCOUT, TARGET_TYPE_ARMORED, TARGET_TYPE_SHOOTER,
                TARGET_TYPE_HEAVY, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SNIPER
            ])

    def _get_edge_spawn(self, formation: str = "random") -> tuple[float, float]:
        """Returns a deterministic edge spawn position based on formation type."""
        margin = 80.0
        if formation == "left":
            return (margin, random.uniform(margin, WORLD_HEIGHT - margin))
        elif formation == "right":
            return (WORLD_WIDTH - margin, random.uniform(margin, WORLD_HEIGHT - margin))
        elif formation == "top":
            return (random.uniform(margin, WORLD_WIDTH - margin), margin)
        elif formation == "bottom":
            return (random.uniform(margin, WORLD_WIDTH - margin), WORLD_HEIGHT - margin)
        elif formation == "v_formation":
            # V-formation spawn point (top center)
            return (WORLD_WIDTH / 2.0, margin)
        elif formation == "line_left":
            return (margin, WORLD_HEIGHT / 2.0)
        elif formation == "line_right":
            return (WORLD_WIDTH - margin, WORLD_HEIGHT / 2.0)
        else:
            # Random edge
            edge = random.choice(["left", "right", "top", "bottom"])
            return self._get_edge_spawn(edge)

    def _apply_formation_offset(self, base_pos: tuple[float, float], index: int, total: int, formation: str = "v_formation") -> tuple[float, float]:
        """Calculates offset from base spawn position for formation placement."""
        bx, by = base_pos
        spacing = 90.0
        if formation == "v_formation":
            # V-shape: left wing goes down-left, right wing goes down-right
            if index == 0:
                return (bx, by)
            elif index % 2 == 1:
                return (bx - spacing * (index + 1) // 2, by + spacing * (index + 1) // 2)
            else:
                return (bx + spacing * (index // 2), by + spacing * (index // 2))
        elif formation == "line":
            # Horizontal line
            start_x = max(100.0, bx - (total - 1) * spacing / 2.0)
            return (start_x + index * spacing, by)
        elif formation == "wedge":
            # Wedge: narrow at top, wide at bottom
            width = spacing * index
            return (bx - width, by + index * spacing * 0.7)
        else:
            # No formation, random scatter
            return (bx + random.uniform(-40, 40), by + random.uniform(-40, 40))
