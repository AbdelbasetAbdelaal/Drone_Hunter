"""
================================================================================
                    DRONE HUNTER 2D - BOSS SYSTEM
================================================================================
Phase 6: Central manager orchestrating Major Sector Boss encounters, intro warnings,
reinforcement pools, phase transitions, death explosions, and completion payouts.
Integrates cleanly with Game, MissionSystem, CombatDirector, and SaveSystem.
"""

from typing import Optional, List
import math
import random
import pygame
import logging

from src.core.game_context import GameContext
from src.data.settings import (
    WORLD_WIDTH, WORLD_HEIGHT, COLOR_GOLD, COLOR_CRIMSON, COLOR_CYAN,
    COLOR_WHITE, COLOR_SHIELD
)
from src.data.boss_data import (
    BossDefinition, get_boss_for_mission, get_boss_definition,
    BOSS_REGISTRY, MISSION_BOSS_MAP
)
from src.entities.boss import SectorBoss
from src.entities.enemy import Enemy
from src.data.game_data import (
    TARGET_TYPE_SCOUT, TARGET_TYPE_SHOOTER, TARGET_TYPE_HEAVY,
    TARGET_TYPE_SHIELD_DRONE
)

STATE_IDLE = "idle"
STATE_INTRO = "intro"
STATE_ACTIVE = "active"
STATE_DEFEATED = "defeated"
STATE_COMPLETE = "complete"


class BossSystem:
    """
    Authoritative controller for Phase 6 Boss encounters.
    Manages boss spawn, intro presentation, reinforcement limits,
    death sequences, rewards, and mission completion synchronization.
    """
    def __init__(self):
        self.state: str = STATE_IDLE
        self.active_boss_def: Optional[BossDefinition] = None
        self.active_boss: Optional[SectorBoss] = None
        self.active_reinforcements: List[Enemy] = []
        
        # Timers
        self.intro_timer: float = 0.0
        self.intro_duration: float = 2.0
        self.death_timer: float = 0.0
        self.death_duration: float = 2.0
        self.death_explosion_timer: float = 0.0
        
        # Death Reward flags
        self.rewards_granted: bool = False
        self.is_final_boss: bool = False

    @property
    def is_intro_active(self) -> bool:
        return self.state == STATE_INTRO

    @property
    def is_boss_active(self) -> bool:
        return self.state in (STATE_INTRO, STATE_ACTIVE, STATE_DEFEATED)

    @property
    def is_complete(self) -> bool:
        return self.state == STATE_COMPLETE

    def has_boss_for_mission(self, mission_id: str) -> bool:
        """Returns True if the mission has an assigned Sector Boss."""
        return mission_id in MISSION_BOSS_MAP

    def start_boss_for_mission(self, mission_id: str, ctx: GameContext) -> bool:
        """
        Initializes a Boss encounter for the given mission.
        Transitions state to INTRO with warning presentation.
        """
        boss_def = get_boss_for_mission(mission_id)
        if not boss_def:
            logging.info(f"BossSystem: No boss defined for mission {mission_id}")
            return False

        self.reset()
        self.active_boss_def = boss_def
        self.is_final_boss = (boss_def.id == "drone_overlord")
        self.state = STATE_INTRO
        self.intro_timer = self.intro_duration
        self.rewards_granted = False

        if ctx.audio_manager:
            ctx.audio_manager.play_boss_alert()

        logging.info(f"BossSystem: Started Boss encounter for {boss_def.name} in mission {mission_id}")
        return True

    def spawn_boss_direct(self, boss_def: BossDefinition, ctx: GameContext, pos: Optional[tuple[float, float]] = None) -> SectorBoss:
        """Instantiates and adds SectorBoss to active target group."""
        if pos is None:
            # Spawn in right side of arena
            p_pos = (ctx.player.pos.x, ctx.player.pos.y) if ctx.player else (1200, 700)
            spawn_x = min(WORLD_WIDTH - 200.0, max(WORLD_WIDTH // 2 + 100.0, p_pos[0] + 500.0))
            spawn_y = p_pos[1]
            pos = (spawn_x, spawn_y)

        boss = SectorBoss(boss_def, pos=pos)
        self.active_boss = boss
        ctx.target_group.add(boss)
        return boss

    def update(self, dt: float, ctx: GameContext) -> bool:
        """
        Updates active boss state, reinforcements, and death sequence.
        Returns True if the boss encounter just completed.
        """
        if self.state == STATE_IDLE or self.state == STATE_COMPLETE:
            return False

        # ---------------------------------------------------------------------
        # 1. BOSS INTRO WARNING
        # ---------------------------------------------------------------------
        if self.state == STATE_INTRO:
            self.intro_timer -= dt
            if self.intro_timer <= 0:
                self.state = STATE_ACTIVE
                self.spawn_boss_direct(self.active_boss_def, ctx)
                if ctx.particle_manager and self.active_boss:
                    ctx.particle_manager.spawn_shockwave(self.active_boss.pos, max_r=600, color=self.active_boss_def.color_inner)
            return False

        # ---------------------------------------------------------------------
        # 2. ACTIVE BOSS FIGHT
        # ---------------------------------------------------------------------
        if self.state == STATE_ACTIVE:
            if not self.active_boss or not self.active_boss.alive or self.active_boss not in ctx.target_group:
                # Boss has been defeated!
                self.state = STATE_DEFEATED
                self.death_timer = self.death_duration
                self._trigger_boss_defeat(ctx)
                return False

            # Boss Phase Transition Audio Hook (Triggers ONCE per phase change)
            if ctx.audio_manager and getattr(self.active_boss, "phase_audio_pending", 0) > 0:
                ctx.audio_manager.play_boss_phase(self.active_boss.phase_audio_pending)
                self.active_boss.phase_audio_pending = 0

            # Manage Reinforcements
            self._clean_active_reinforcements(ctx)
            current_active = len(self.active_reinforcements)
            types_to_spawn = self.active_boss.should_spawn_reinforcements(dt, current_active)
            if types_to_spawn:
                self._spawn_reinforcements(types_to_spawn, ctx)

            return False


        # ---------------------------------------------------------------------
        # 3. BOSS DEFEATED DEATH SEQUENCE
        # ---------------------------------------------------------------------
        if self.state == STATE_DEFEATED:
            self.death_timer -= dt
            self.death_explosion_timer -= dt
            
            # Rate-limited death explosions (prevent particle runaway)
            if self.death_explosion_timer <= 0:
                self.death_explosion_timer = 0.15
                if ctx.particle_manager and self.active_boss:
                    bx = self.active_boss.pos.x + random.uniform(-40, 40)
                    by = self.active_boss.pos.y + random.uniform(-40, 40)
                    ctx.particle_manager.spawn_explosion((bx, by), count=8, color=self.active_boss_def.color_inner)
                    ctx.trigger_shake(5.0, 0.1)

            if self.death_timer <= 0:
                self.state = STATE_COMPLETE
                # Clean up any leftover reinforcements
                for reinf in self.active_reinforcements:
                    if reinf.alive and reinf in ctx.target_group:
                        reinf.kill()
                        if ctx.particle_manager:
                            ctx.particle_manager.spawn_enemy_death(reinf.rect.center, reinf.color)
                self.active_reinforcements.clear()
                return True

        return False

    def _trigger_boss_defeat(self, ctx: GameContext):
        """Processes rewards, score, sound, and big explosion upon boss destruction."""
        if self.rewards_granted or not self.active_boss_def:
            return
        self.rewards_granted = True

        boss_def = self.active_boss_def
        pos = self.active_boss.pos if self.active_boss else (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)

        # Bounded explosion FX
        if ctx.particle_manager:
            ctx.particle_manager.spawn_boss_explosion(pos)
            ctx.particle_manager.spawn_floating_text(pos, f"BOSS DEFEATED! +{boss_def.reward_score}", COLOR_GOLD, 28)
            ctx.trigger_shake(16.0, 0.8)

        if ctx.audio_manager:
            ctx.audio_manager.play_boss_death()

        # Award Score & Scrap
        ctx.add_score(boss_def.reward_score)
        ctx.scrap += boss_def.reward_scrap

        # Record defeated boss in context progression
        if not hasattr(ctx, "bosses_defeated"):
            ctx.bosses_defeated = []
        if boss_def.id not in ctx.bosses_defeated:
            ctx.bosses_defeated.append(boss_def.id)

        if self.is_final_boss:
            ctx.campaign_completed = True

        logging.info(f"BossSystem: Boss {boss_def.name} defeated! Awarded {boss_def.reward_scrap} Scrap.")

    def _clean_active_reinforcements(self, ctx: GameContext):
        """Removes eliminated reinforcement drones from tracking."""
        self.active_reinforcements = [e for e in self.active_reinforcements if e.alive and e in ctx.target_group]

    def _spawn_reinforcements(self, enemy_types: List[str], ctx: GameContext):
        """Spawns reinforcement enemies around the boss within arena limits."""
        if not self.active_boss or not self.active_boss_def:
            return

        max_limit = self.active_boss_def.max_reinforcements
        available_slots = max(0, max_limit - len(self.active_reinforcements))
        if available_slots <= 0:
            return

        for etype in enemy_types[:available_slots]:
            ang = random.uniform(0, 2 * math.pi)
            dist = random.uniform(120.0, 220.0)
            sx = max(100.0, min(WORLD_WIDTH - 100.0, self.active_boss.pos.x + math.cos(ang) * dist))
            sy = max(100.0, min(WORLD_HEIGHT - 100.0, self.active_boss.pos.y + math.sin(ang) * dist))

            enemy = Enemy(enemy_type=etype, pos=(sx, sy), sector_idx=ctx.current_sector_idx)
            ctx.target_group.add(enemy)
            self.active_reinforcements.append(enemy)

            if ctx.particle_manager:
                ctx.particle_manager.spawn_spark((sx, sy), count=8, color=COLOR_CYAN)

    def reset(self):
        """Resets the BossSystem completely back to IDLE."""
        self.state = STATE_IDLE
        self.active_boss_def = None
        self.active_boss = None
        self.active_reinforcements.clear()
        self.intro_timer = 0.0
        self.death_timer = 0.0
        self.death_explosion_timer = 0.0
        self.rewards_granted = False
        self.is_final_boss = False
