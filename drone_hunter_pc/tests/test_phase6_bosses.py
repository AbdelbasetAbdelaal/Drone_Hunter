"""
================================================================================
                    DRONE HUNTER 2D - PHASE 6 TEST SUITE
================================================================================
Comprehensive verification of Phase 6 Boss Warfare & Endgame Combat:
- Boss creation & definition loading
- Boss stats, damage mitigation, and contact damage
- Multi-phase deterministic state transitions (100% -> 70% -> 35% / 25%)
- Attack patterns, cooldowns, and telegraph cues
- Projectile and reinforcement bounding
- Shield mechanics & counterplay
- Boss death sequence, rewards, and scoring
- Mission completion & sector unlock chaining
- Final Boss (Drone Overlord) 4-phase progression & campaign victory
- Replay safety (no duplicate one-time progression)
- Save / Load persistence & backwards compatibility with legacy saves
"""

import os
import unittest
import pygame

# Initialize headless pygame for testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
pygame.init()

from src.data.settings import WORLD_WIDTH, WORLD_HEIGHT
from src.core.game_context import GameContext
from src.core.game_state import (
    STATE_PLAYING, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, STATE_VICTORY
)
from src.entities.player import Player
from src.entities.boss import SectorBoss
from src.data.boss_data import (
    BossDefinition, get_boss_definition, get_boss_for_mission,
    BOSS_ASSEMBLY_WARDEN, BOSS_CORE_EXECUTOR, BOSS_REACTOR_TITAN,
    BOSS_DEFENSE_COMMANDER, BOSS_DRONE_OVERLORD,
    ASSEMBLY_WARDEN_CONFIG, CORE_EXECUTOR_CONFIG, REACTOR_TITAN_CONFIG,
    DEFENSE_COMMANDER_CONFIG, DRONE_OVERLORD_CONFIG,
    ATTACK_RADIAL_BURST, ATTACK_SPREAD_BARRAGE, ATTACK_TARGETED_SHOT,
    ATTACK_HOMING_VOLLEY, ATTACK_LASER_SWEEP, ATTACK_ENERGY_WAVE,
    ATTACK_MISSILE_SALVO
)
from src.systems.boss_system import (
    BossSystem, STATE_IDLE, STATE_INTRO, STATE_ACTIVE, STATE_DEFEATED, STATE_COMPLETE
)
from src.systems.mission_system import MissionSystem
from src.systems.combat_director import CombatDirector
from src.systems.encounter_system import EncounterSystem
from src.systems.save_system import SaveSystem
from src.systems.combat_system import CombatSystem


class TestPhase6Bosses(unittest.TestCase):

    def setUp(self):
        self.ctx = GameContext()
        self.player = Player((500, 360))
        self.ctx.player = self.player
        self.encounter_sys = EncounterSystem()
        self.director = CombatDirector(self.encounter_sys)
        self.mission_sys = MissionSystem()
        self.boss_sys = BossSystem()
        self.ctx.boss_system = self.boss_sys
        self.combat_sys = CombatSystem(self.ctx)

    # -------------------------------------------------------------------------
    # 1. Boss Creation
    # -------------------------------------------------------------------------
    def test_boss_creation(self):
        """Verify SectorBoss instantiates with correct definition and sprite properties."""
        boss = SectorBoss(ASSEMBLY_WARDEN_CONFIG, pos=(1000, 500))
        self.assertEqual(boss.boss_id, BOSS_ASSEMBLY_WARDEN)
        self.assertEqual(boss.boss_name, "ASSEMBLY WARDEN")
        self.assertTrue(boss.is_boss)
        self.assertTrue(boss.alive)
        self.assertEqual(boss.hp, 450)
        self.assertEqual(boss.max_hp, 450)
        self.assertEqual(boss.rect.center, (1000, 500))
        self.assertIsNotNone(boss.image)

    # -------------------------------------------------------------------------
    # 2. Boss Definition Loading
    # -------------------------------------------------------------------------
    def test_boss_definition_loading(self):
        """Verify all 5 Sector Boss definitions load from catalog and mission mappings."""
        boss_ids = [
            BOSS_ASSEMBLY_WARDEN, BOSS_CORE_EXECUTOR, BOSS_REACTOR_TITAN,
            BOSS_DEFENSE_COMMANDER, BOSS_DRONE_OVERLORD
        ]
        for b_id in boss_ids:
            b_def = get_boss_definition(b_id)
            self.assertIsNotNone(b_def, f"Boss definition {b_id} must be registered!")
            self.assertGreater(b_def.max_hp, 0)
            self.assertGreater(len(b_def.phases), 0)

        # Verify mission mappings (S1_M5 -> S5_M5)
        for s_idx in range(1, 6):
            m_id = f"S{s_idx}_M5"
            m_boss = get_boss_for_mission(m_id)
            self.assertIsNotNone(m_boss, f"Mission {m_id} must map to a boss definition!")
            self.assertEqual(m_boss.sector_id, s_idx)

    # -------------------------------------------------------------------------
    # 3. Boss HP
    # -------------------------------------------------------------------------
    def test_boss_hp_scaling(self):
        """Verify distinct HP pools and attributes for each Sector Boss."""
        b1 = SectorBoss(ASSEMBLY_WARDEN_CONFIG)
        b2 = SectorBoss(CORE_EXECUTOR_CONFIG)
        b3 = SectorBoss(REACTOR_TITAN_CONFIG)
        b4 = SectorBoss(DEFENSE_COMMANDER_CONFIG)
        b5 = SectorBoss(DRONE_OVERLORD_CONFIG)

        self.assertEqual(b1.max_hp, 450)
        self.assertEqual(b2.max_hp, 750)
        self.assertEqual(b3.max_hp, 1100)
        self.assertEqual(b4.max_hp, 1500)
        self.assertEqual(b5.max_hp, 2200)

        # Verify increasing threat progression
        self.assertLess(b1.max_hp, b2.max_hp)
        self.assertLess(b2.max_hp, b3.max_hp)
        self.assertLess(b3.max_hp, b4.max_hp)
        self.assertLess(b4.max_hp, b5.max_hp)

    # -------------------------------------------------------------------------
    # 4. Boss Damage
    # -------------------------------------------------------------------------
    def test_boss_damage_and_armor(self):
        """Verify boss takes damage properly and applies phase armor reductions."""
        boss = SectorBoss(ASSEMBLY_WARDEN_CONFIG)
        boss.armor = 0.0
        boss.take_damage(50)
        self.assertEqual(boss.hp, 400)

        # With 20% armor, 50 damage -> 40 effective damage
        boss.armor = 0.20
        boss.take_damage(50)
        self.assertEqual(boss.hp, 360)

    # -------------------------------------------------------------------------
    # 5. Boss Phase Transition
    # -------------------------------------------------------------------------
    def test_boss_phase_transition(self):
        """Verify boss transitions through Phase 1 -> Phase 2 -> Phase 3 on HP threshold."""
        boss = SectorBoss(ASSEMBLY_WARDEN_CONFIG)
        self.assertEqual(boss.current_phase_number, 1)

        # Drop HP to 65% (below 70% threshold)
        boss.take_damage(int(boss.max_hp * 0.35))
        self.assertEqual(boss.current_phase_number, 2)
        self.assertEqual(boss.current_phase_name, "PHASE 2")

        # Drop HP to 30% (below 35% threshold)
        boss.take_damage(int(boss.max_hp * 0.40))
        self.assertEqual(boss.current_phase_number, 3)
        self.assertEqual(boss.current_phase_name, "PHASE 3")

    # -------------------------------------------------------------------------
    # 6. Phase Transition Occurs Once
    # -------------------------------------------------------------------------
    def test_phase_transition_occurs_once(self):
        """Verify phase transitions occur deterministically without repeat triggers."""
        boss = SectorBoss(ASSEMBLY_WARDEN_CONFIG)
        boss.take_damage(int(boss.max_hp * 0.35))
        self.assertEqual(boss.current_phase_idx, 1)

        # Repeated small hits stay in Phase 2
        for _ in range(5):
            boss.take_damage(5)
            self.assertEqual(boss.current_phase_idx, 1)

    # -------------------------------------------------------------------------
    # 7. Boss Attacks Have Cooldowns
    # -------------------------------------------------------------------------
    def test_boss_attacks_have_cooldowns(self):
        """Verify boss attacks respect cooldowns and do not spam every frame."""
        boss = SectorBoss(ASSEMBLY_WARDEN_CONFIG)
        # First frame update - cooldowns are active
        bullets = boss.update(0.016, player_pos=(500, 360))
        self.assertEqual(len(bullets), 0, "No bullets should spawn immediately on first frame!")

        # Advance time past attack cooldown
        bullets = boss.update(2.5, player_pos=(500, 360))
        self.assertGreater(len(bullets), 0, "Boss must fire bullets once cooldown expires!")

        # Immediate next frame should have 0 bullets due to fresh cooldown
        bullets_next = boss.update(0.016, player_pos=(500, 360))
        self.assertEqual(len(bullets_next), 0, "Boss must reset attack cooldown after firing!")

    # -------------------------------------------------------------------------
    # 8. Boss Projectile Limits
    # -------------------------------------------------------------------------
    def test_boss_projectile_limits(self):
        """Verify boss attack patterns emit a bounded number of projectiles."""
        for b_def in [ASSEMBLY_WARDEN_CONFIG, CORE_EXECUTOR_CONFIG, DRONE_OVERLORD_CONFIG]:
            boss = SectorBoss(b_def)
            for phase_idx in range(len(b_def.phases)):
                boss._apply_phase(phase_idx)
                for atk in b_def.phases[phase_idx].attacks:
                    bullets = boss._execute_attack_pattern(atk, (1000, 500), (500, 360))
                    self.assertLessEqual(
                        len(bullets), b_def.max_projectiles,
                        f"Attack {atk.attack_type} exceeded max_projectiles limit {b_def.max_projectiles}!"
                    )

    # -------------------------------------------------------------------------
    # 9. Reinforcement Limits
    # -------------------------------------------------------------------------
    def test_reinforcement_limits(self):
        """Verify BossSystem strictly enforces max reinforcement counts."""
        boss = SectorBoss(ASSEMBLY_WARDEN_CONFIG)
        boss._apply_phase(1)  # Phase 2 has reinforcements (max_active: 2)

        # Zero active reinforcements -> allowed to spawn
        reinf1 = boss.should_spawn_reinforcements(10.0, current_active_reinforcements=0)
        self.assertIsNotNone(reinf1)
        self.assertLessEqual(len(reinf1), 2)

        # At max active reinforcements (2) -> no spawn allowed
        reinf2 = boss.should_spawn_reinforcements(10.0, current_active_reinforcements=2)
        self.assertIsNone(reinf2, "Cannot spawn reinforcements when active count is at limit!")

    # -------------------------------------------------------------------------
    # 10. Boss Shield Behavior
    # -------------------------------------------------------------------------
    def test_boss_shield_behavior(self):
        """Verify boss shield absorbs damage and expires after duration."""
        boss = SectorBoss(DEFENSE_COMMANDER_CONFIG)
        boss._apply_phase(1)  # Phase 2 has shield
        self.assertTrue(boss.is_shielded)

        initial_hp = boss.hp
        boss.take_damage(100)
        self.assertEqual(boss.hp, initial_hp, "Shield must deflect incoming damage!")

        # Update boss past shield duration
        boss.update(5.0, player_pos=(500, 360))
        self.assertFalse(boss.is_shielded, "Temporary shield must expire after duration!")

        # Now vulnerable
        boss.take_damage(100)
        self.assertLess(boss.hp, initial_hp, "Boss must take damage once shield is down!")

    # -------------------------------------------------------------------------
    # 11. Boss Death
    # -------------------------------------------------------------------------
    def test_boss_death(self):
        """Verify boss dies when HP reaches 0 and triggers alive=False."""
        boss = SectorBoss(ASSEMBLY_WARDEN_CONFIG)
        is_dead = boss.take_damage(boss.max_hp + 100)
        self.assertTrue(is_dead)
        self.assertFalse(boss.alive)
        self.assertEqual(boss.hp, 0)

    # -------------------------------------------------------------------------
    # 12. Boss Reward
    # -------------------------------------------------------------------------
    def test_boss_rewards(self):
        """Verify defeating a boss awards configured scrap and score."""
        self.boss_sys.start_boss_for_mission("S1_M5", self.ctx)
        self.boss_sys.intro_timer = 0.0
        self.boss_sys.update(0.016, self.ctx)  # Spawns boss

        initial_scrap = self.ctx.scrap
        initial_score = self.ctx.total_score

        # Kill boss
        boss = self.boss_sys.active_boss
        boss.take_damage(boss.max_hp + 50)
        self.boss_sys.update(0.016, self.ctx)

        self.assertEqual(self.ctx.scrap, initial_scrap + ASSEMBLY_WARDEN_CONFIG.reward_scrap)
        self.assertEqual(self.ctx.total_score, initial_score + ASSEMBLY_WARDEN_CONFIG.reward_score)
        self.assertIn(BOSS_ASSEMBLY_WARDEN, self.ctx.bosses_defeated)

    # -------------------------------------------------------------------------
    # 13. Mission Completion After Boss Death
    # -------------------------------------------------------------------------
    def test_mission_completion_after_boss_death(self):
        """Verify Mission 5 completes once Boss is defeated."""
        self.mission_sys.start_mission(self.ctx, "S1_M5", self.director, self.boss_sys)
        self.director.state = "complete"

        # Update mission system -> triggers boss intro
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)
        self.assertEqual(self.boss_sys.state, STATE_INTRO)

        # Complete intro -> boss active
        self.boss_sys.intro_timer = 0.0
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)
        self.assertEqual(self.boss_sys.state, STATE_ACTIVE)

        # Defeat boss
        boss = self.boss_sys.active_boss
        boss.take_damage(boss.max_hp + 50)

        # Update through defeat timer
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)
        self.assertEqual(self.boss_sys.state, STATE_DEFEATED)

        self.boss_sys.death_timer = 0.0
        completed = self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)
        self.assertTrue(completed, "Mission must complete after boss death sequence finishes!")
        self.assertTrue(self.mission_sys.is_mission_success)
        self.assertIn("S1_M5", self.ctx.missions["completed"])

    # -------------------------------------------------------------------------
    # 14. Mission Failure Resets Boss
    # -------------------------------------------------------------------------
    def test_mission_failure_resets_boss(self):
        """Verify player death or mission reset completely resets boss state and HP."""
        self.boss_sys.start_boss_for_mission("S1_M5", self.ctx)
        self.boss_sys.intro_timer = 0.0
        self.boss_sys.update(0.016, self.ctx)

        # Damage boss to 50%
        self.boss_sys.active_boss.take_damage(int(self.boss_sys.active_boss.max_hp * 0.50))
        self.assertEqual(self.boss_sys.active_boss.hp, 225)

        # Reset boss system
        self.boss_sys.reset()
        self.assertEqual(self.boss_sys.state, STATE_IDLE)
        self.assertIsNone(self.boss_sys.active_boss)

        # Re-start boss
        self.boss_sys.start_boss_for_mission("S1_M5", self.ctx)
        self.boss_sys.intro_timer = 0.0
        self.boss_sys.update(0.016, self.ctx)
        self.assertEqual(self.boss_sys.active_boss.hp, self.boss_sys.active_boss.max_hp, "Boss HP must reset to full on restart!")

    # -------------------------------------------------------------------------
    # 15. Boss Replay
    # -------------------------------------------------------------------------
    def test_boss_replay_functionality(self):
        """Verify completed boss missions can be replayed cleanly."""
        self.ctx.missions["completed"].append("S1_M5")
        self.ctx.bosses_defeated.append(BOSS_ASSEMBLY_WARDEN)

        # Start replay
        self.mission_sys.start_mission(self.ctx, "S1_M5", self.director, self.boss_sys)
        self.director.state = "complete"
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)
        self.assertEqual(self.boss_sys.state, STATE_INTRO)

        self.boss_sys.intro_timer = 0.0
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)
        self.assertIsNotNone(self.boss_sys.active_boss)
        self.assertTrue(self.boss_sys.active_boss.alive)

    # -------------------------------------------------------------------------
    # 16. Sector Unlock After Boss
    # -------------------------------------------------------------------------
    def test_sector_unlock_after_boss(self):
        """Verify defeating Sector 1 Boss unlocks Sector 2 and S2_M1."""
        self.ctx.missions["unlocked"] = ["S1_M1", "S1_M2", "S1_M3", "S1_M4", "S1_M5"]
        self.ctx.sector_progress["unlocked"] = [1]
        self.ctx.sector_progress["completed"] = []

        self.mission_sys.start_mission(self.ctx, "S1_M5", self.director, self.boss_sys)
        self.director.state = "complete"
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)
        self.boss_sys.intro_timer = 0.0
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)

        # Defeat boss
        self.boss_sys.active_boss.take_damage(self.boss_sys.active_boss.max_hp + 10)
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)
        self.assertEqual(self.boss_sys.state, STATE_DEFEATED)
        self.boss_sys.death_timer = 0.0
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)

        self.assertIn(1, self.ctx.sector_progress["completed"])
        self.assertIn(2, self.ctx.sector_progress["unlocked"], "Sector 2 must unlock after Boss 1 is defeated!")
        self.assertIn("S2_M1", self.ctx.missions["unlocked"], "Mission S2_M1 must unlock after Boss 1 is defeated!")

    # -------------------------------------------------------------------------
    # 17. Final Boss Campaign Completion
    # -------------------------------------------------------------------------
    def test_final_boss_campaign_completion(self):
        """Verify defeating Drone Overlord (Sector 5 Boss) marks campaign complete."""
        self.ctx.missions["unlocked"] = ["S5_M5"]
        self.ctx.sector_progress["unlocked"] = [1, 2, 3, 4, 5]
        self.ctx.sector_progress["completed"] = [1, 2, 3, 4]
        self.ctx.campaign_completed = False

        self.mission_sys.start_mission(self.ctx, "S5_M5", self.director, self.boss_sys)
        self.director.state = "complete"
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)
        self.boss_sys.intro_timer = 0.0
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)

        self.assertEqual(self.boss_sys.active_boss.boss_id, BOSS_DRONE_OVERLORD)
        self.assertEqual(self.boss_sys.active_boss.total_phases, 4, "Final Boss must have 4 phases!")

        # Defeat Drone Overlord
        self.boss_sys.active_boss.take_damage(5000)
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)
        self.assertEqual(self.boss_sys.state, STATE_DEFEATED)
        self.boss_sys.death_timer = 0.0
        self.mission_sys.update(0.016, self.ctx, self.director, self.boss_sys)

        self.assertTrue(self.ctx.campaign_completed, "Campaign must be marked complete after defeating Drone Overlord!")
        self.assertIn(BOSS_DRONE_OVERLORD, self.ctx.bosses_defeated)

    # -------------------------------------------------------------------------
    # 18. Save/Load Boss Progression
    # -------------------------------------------------------------------------
    def test_save_load_boss_progression(self):
        """Verify bosses_defeated and campaign_completed are saved and loaded correctly."""
        save_file = "test_phase6_save.json"
        save_sys = SaveSystem(save_filename=save_file)
        try:
            # Save data with bosses defeated
            save_sys.save(
                scrap=2500, coins=0, highscore=15000,
                upgrades={"hull": 2, "energy": 2, "weapon": 2, "mobility": 2},
                sectors=[True, True, True, False, False],
                bosses_defeated=[BOSS_ASSEMBLY_WARDEN, BOSS_CORE_EXECUTOR],
                campaign_completed=False
            )

            loaded = save_sys.load()
            self.assertEqual(loaded["bosses_defeated"], [BOSS_ASSEMBLY_WARDEN, BOSS_CORE_EXECUTOR])
            self.assertFalse(loaded["campaign_completed"])
            self.assertEqual(loaded["scrap"], 2500)
        finally:
            if os.path.exists(save_sys.save_path):
                os.remove(save_sys.save_path)

    # -------------------------------------------------------------------------
    # 19. Existing Save Compatibility
    # -------------------------------------------------------------------------
    def test_existing_save_compatibility(self):
        """Verify legacy saves without Phase 6 fields load safely with default fallbacks."""
        save_file = "test_legacy_save.json"
        save_sys = SaveSystem(save_filename=save_file)
        try:
            # Write old-format save file without bosses_defeated
            import json
            legacy_data = {
                "scrap": 1200,
                "highscore": 5000,
                "upgrades": {"hull": 1},
                "sectors": [True, False, False, False, False],
                "missions": {"current_sector": 1, "completed": ["S1_M1"], "unlocked": ["S1_M1", "S1_M2"]}
            }
            with open(save_sys.save_path, "w", encoding="utf-8") as f:
                json.dump(legacy_data, f)

            loaded = save_sys.load()
            self.assertEqual(loaded["scrap"], 1200)
            self.assertEqual(loaded["bosses_defeated"], [])
            self.assertFalse(loaded["campaign_completed"])
        finally:
            if os.path.exists(save_sys.save_path):
                os.remove(save_sys.save_path)

    # -------------------------------------------------------------------------
    # 20. No Duplicate Permanent Progression Reward
    # -------------------------------------------------------------------------
    def test_no_duplicate_permanent_progression_reward(self):
        """Verify replaying an already-completed boss mission does not grant one-time completion bonus."""
        self.ctx.missions["completed"] = ["S1_M5"]
        self.ctx.sector_progress["completed"] = [1]
        self.ctx.scrap = 1000

        # Run mission completion again on already completed mission
        self.mission_sys.active_mission_id = "S1_M5"
        self.mission_sys.active_mission_data = {"id": "S1_M5", "sector_id": 1, "mission_number": 5, "difficulty": 3}
        self.mission_sys._trigger_success(self.ctx)

        # Scrap should not duplicate the sector bonus
        self.assertEqual(self.ctx.scrap, 1000, "One-time mission and sector bonuses must not be granted repeatedly on replay!")


if __name__ == "__main__":
    unittest.main()
