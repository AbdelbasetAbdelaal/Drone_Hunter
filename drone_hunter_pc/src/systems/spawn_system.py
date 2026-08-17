"""
================================================================================
                    DRONE HUNTER 2D - SPAWN & WAVE MANAGER
================================================================================
Coordinates tactical wave progressions, regular enemy group formations,
and multi-phase Boss Dreadnought introductions.
"""

import math
import random
import pygame
from src.data.settings import SCREEN_WIDTH, SCREEN_HEIGHT
from src.data.game_data import (
    TARGET_TYPE_STANDARD, TARGET_TYPE_FAST, TARGET_TYPE_ARMORED, TARGET_TYPE_SHOOTER,
    TARGET_TYPE_TURRET, TARGET_TYPE_VEHICLE, TARGET_TYPE_CHASER, TARGET_TYPE_SWARM,
    TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SNIPER, TARGET_TYPE_BOSS,
    TARGET_TYPE_STEALTH_MIRAGE, TARGET_TYPE_EMP_DISRUPTER, TARGET_TYPE_TITAN_MECH,
    SECTORS
)
from src.entities.enemy import Enemy
from src.entities.boss import (
    SkyDreadnoughtBoss, StealthMirageBoss, EMPDisrupterBoss, ColossusTitanMechBoss
)

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

    def is_stage_complete(self, current_score: int) -> bool:
        return current_score >= self.target_score


class Spawner:
    def __init__(self, base_min_interval: float = 1.2, base_max_interval: float = 2.6):
        self.base_min_interval = base_min_interval
        self.base_max_interval = base_max_interval
        self.timer = 0.0
        self.next_interval = random.uniform(base_min_interval, base_max_interval)
        self.level = 1
        self.sector_idx = 0
        self.boss_spawned = False

    def reset_for_stage(self, level: int, sector_idx: int):
        self.level = level
        self.sector_idx = sector_idx
        self.timer = 0.0
        self.next_interval = random.uniform(self.base_min_interval, self.base_max_interval)
        self.boss_spawned = False

    def update(self, dt: float, context):
        """Spawns enemies, environmental obstacles, and hazards based on stage progress."""
        self.timer += dt
        current_wave = context.current_wave
        diff_data = context.difficulty_data
        hp_mult = diff_data.get("hp_mult", 1.0)
        spd_mult = diff_data.get("speed_mult", 1.0)

        # Stage 3 Boss Spawn (Wave 4)
        if context.current_sub_level == 3 and current_wave == 4 and not self.boss_spawned:
            self.boss_spawned = True
            boss = self._create_sector_boss(self.sector_idx, hp_mult, spd_mult)
            if boss:
                context.target_group.add(boss)

        if self.timer >= self.next_interval:
            self.timer = 0.0
            interval_reduction = min(0.6, (self.level - 1) * 0.06 + (current_wave - 1) * 0.12)
            cur_min = max(0.5, self.base_min_interval - interval_reduction)
            cur_max = max(1.0, self.base_max_interval - interval_reduction)
            self.next_interval = random.uniform(cur_min, cur_max)

            # Spawn 1-2 enemies
            spawn_count = 2 if (current_wave >= 3 and random.random() < 0.40) else 1
            for _ in range(spawn_count):
                e_type = self._select_enemy_type(current_wave)
                spd_bonus = (self.level - 1) * 6.0
                enemy = Enemy(
                    enemy_type=e_type,
                    speed_bonus=spd_bonus,
                    level=self.level,
                    sector_idx=self.sector_idx,
                    hp_multiplier=hp_mult,
                    speed_multiplier=spd_mult
                )
                context.target_group.add(enemy)

    def _select_enemy_type(self, current_wave: int) -> str:
        r = random.random()
        if self.sector_idx == 0:
            if current_wave == 1: return random.choice([TARGET_TYPE_STANDARD, TARGET_TYPE_FAST, TARGET_TYPE_SWARM])
            elif current_wave == 2: return random.choice([TARGET_TYPE_STANDARD, TARGET_TYPE_FAST, TARGET_TYPE_SHOOTER, TARGET_TYPE_SWARM])
            else: return random.choice([TARGET_TYPE_FAST, TARGET_TYPE_SHOOTER, TARGET_TYPE_ARMORED, TARGET_TYPE_SWARM])

        elif self.sector_idx == 1:
            if current_wave <= 2: return random.choice([TARGET_TYPE_STANDARD, TARGET_TYPE_ARMORED, TARGET_TYPE_TURRET, TARGET_TYPE_SHIELD_DRONE])
            else: return random.choice([TARGET_TYPE_ARMORED, TARGET_TYPE_TURRET, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_CHASER])

        elif self.sector_idx == 2:
            if current_wave <= 2: return random.choice([TARGET_TYPE_FAST, TARGET_TYPE_SHOOTER, TARGET_TYPE_SNIPER, TARGET_TYPE_SHIELD_DRONE])
            else: return random.choice([TARGET_TYPE_SNIPER, TARGET_TYPE_CHASER, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_ARMORED])

        else: # Sectors 3 & 4
            return random.choice([
                TARGET_TYPE_FAST, TARGET_TYPE_ARMORED, TARGET_TYPE_SHOOTER,
                TARGET_TYPE_CHASER, TARGET_TYPE_SWARM, TARGET_TYPE_SHIELD_DRONE, TARGET_TYPE_SNIPER
            ])

    def _create_sector_boss(self, sector_idx: int, hp_mult: float, spd_mult: float):
        if sector_idx == 0:
            return SkyDreadnoughtBoss(level=self.level, sector_idx=0, hp_multiplier=hp_mult, speed_multiplier=spd_mult)
        elif sector_idx == 1:
            return StealthMirageBoss(level=self.level, sector_idx=1, hp_multiplier=hp_mult, speed_multiplier=spd_mult)
        elif sector_idx == 2:
            return EMPDisrupterBoss(level=self.level, sector_idx=2, hp_multiplier=hp_mult, speed_multiplier=spd_mult)
        elif sector_idx == 3:
            return SkyDreadnoughtBoss(level=self.level, sector_idx=3, hp_multiplier=hp_mult, speed_multiplier=spd_mult)
        else: # Sector 4: Final Colossus Titan
            return ColossusTitanMechBoss(level=self.level, sector_idx=4, hp_multiplier=hp_mult, speed_multiplier=spd_mult)
