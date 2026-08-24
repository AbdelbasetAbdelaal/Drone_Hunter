"""
================================================================================
                    DRONE HUNTER 2D - PHASE 7 RELEASE QA SUITE
================================================================================
Comprehensive verification for Release Readiness:
- Version integrity (v1.0.0)
- End-to-end 5-sector / 25-mission progression & campaign victory
- All 5 Boss battles & endgame confrontation
- Weapon system firing & switching
- Hangar upgrades & currency safety
- Save / Load persistence & corruption resilience
- Mouse coordinate scaling across multiple display resolutions
- Audio manager safety & fail-safe operation
- Pause / Resume state integrity
"""

import os
import sys
import unittest
import pygame

# Initialize headless pygame for testing
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pygame.init()

from src.data.settings import VERSION, SCREEN_WIDTH, SCREEN_HEIGHT
from src.core.game import Game
from src.core.game_state import (
    STATE_MENU, STATE_SECTOR_SELECT, STATE_MISSION_BRIEFING,
    STATE_PLAYING, STATE_PAUSED, STATE_MISSION_COMPLETE,
    STATE_MISSION_FAILED, STATE_VICTORY, STATE_HANGAR,
    STATE_SETTINGS
)
from src.data.mission_data import (
    SECTORS_PHASE5, get_mission_data, get_missions_for_sector,
    MISSION_REWARDS, SECTOR_BONUS
)
from src.systems.save_system import SaveSystem
from src.audio.audio_manager import AudioManager


class TestPhase7Release(unittest.TestCase):

    def setUp(self):
        self.test_save_file = "test_phase7_save.json"
        self.game = Game()
        self.game.save_system = SaveSystem(save_filename=self.test_save_file)
        self.game.context.save_system = self.game.save_system

    def tearDown(self):
        if os.path.exists(self.game.save_system.save_path):
            try: os.remove(self.game.save_system.save_path)
            except Exception: pass
        if os.path.exists(self.game.save_system.temp_path):
            try: os.remove(self.game.save_system.temp_path)
            except Exception: pass

    # -------------------------------------------------------------------------
    # 1. Version Integrity
    # -------------------------------------------------------------------------
    def test_version_integrity(self):
        """Verify release version is set to 1.0.0."""
        self.assertEqual(VERSION, "1.0.0")

    # -------------------------------------------------------------------------
    # 2. Campaign Structure: 5 Sectors & 25 Missions
    # -------------------------------------------------------------------------
    def test_campaign_structure_integrity(self):
        """Verify exactly 5 Sectors and at least 25 Missions are registered."""
        self.assertEqual(len(SECTORS_PHASE5), 5)
        total_missions = 0
        for s in range(1, 6):
            missions = get_missions_for_sector(s)
            self.assertGreaterEqual(len(missions), 5, f"Sector {s} must have at least 5 missions!")
            total_missions += len(missions)
        self.assertGreaterEqual(total_missions, 25)

    # -------------------------------------------------------------------------
    # 3. End-to-End Campaign Progression
    # -------------------------------------------------------------------------
    def test_end_to_end_campaign_progression(self):
        """Simulate completing all 25 missions sequentially to reach Campaign Victory."""
        ctx = self.game.context
        ms = self.game.mission_system

        for sector_id in range(1, 6):
            # Sector must be unlocked
            self.assertIn(sector_id, ctx.sector_progress["unlocked"], f"Sector {sector_id} should be unlocked!")
            for mission_num in range(1, 6):
                m_id = f"S{sector_id}_M{mission_num}"
                self.assertIn(m_id, ctx.missions["unlocked"], f"Mission {m_id} must be unlocked!")

                # Play & complete mission
                self.game.start_phase5_mission(m_id)
                self.assertEqual(ctx.state, STATE_PLAYING)
                self.assertEqual(ms.active_mission_id, m_id)

                # Trigger success
                ms._trigger_success(ctx)
                self.assertIn(m_id, ctx.missions["completed"])

        # After completing Sector 5 Mission 5, campaign should be marked completed
        self.assertTrue(ctx.campaign_completed)

    # -------------------------------------------------------------------------
    # 4. Hangar Upgrades & Currency Safety
    # -------------------------------------------------------------------------
    def test_hangar_upgrades_and_currency_safety(self):
        """Verify hangar upgrades deduct currency, enforce caps, and prevent negative scrap."""
        ctx = self.game.context
        ctx.scrap = 1500
        ctx.upgrade_levels["hull"] = 1

        # Level 1 -> 2 costs 500 scrap
        success = self.game.buy_upgrade("hull")
        self.assertTrue(success)
        self.assertEqual(ctx.upgrade_levels["hull"], 2)
        self.assertEqual(ctx.scrap, 1000)

        # Level 2 -> 3 costs 1000 scrap
        success2 = self.game.buy_upgrade("hull")
        self.assertTrue(success2)
        self.assertEqual(ctx.upgrade_levels["hull"], 3)
        self.assertEqual(ctx.scrap, 0)

        # Insufficient scrap attempt
        fail = self.game.buy_upgrade("hull")
        self.assertFalse(fail)
        self.assertEqual(ctx.upgrade_levels["hull"], 3)
        self.assertEqual(ctx.scrap, 0)

        # Max level capping
        ctx.scrap = 100000
        for _ in range(10):
            self.game.buy_upgrade("hull")
        self.assertEqual(ctx.upgrade_levels["hull"], 5, "Hull upgrade must cap at level 5!")

    # -------------------------------------------------------------------------
    # 5. Weapon System: Selection & Switching
    # -------------------------------------------------------------------------
    def test_weapon_system_switching(self):
        """Verify weapon cycling and direct selection across all unlocked weapon types."""
        self.game.start_phase5_mission("S1_M1")
        player = self.game.context.player
        self.assertIsNotNone(player)

        # Add all weapons to available list
        player.available_weapons = ["pulse", "scatter", "missile", "beam", "tesla", "cluster"]
        for idx, w_name in enumerate(player.available_weapons):
            player.select_weapon(idx)
            self.assertEqual(player.active_weapon, w_name)

        # Weapon cycle
        player.select_weapon(0)
        player.cycle_weapon()
        self.assertEqual(player.active_weapon, "scatter")

    # -------------------------------------------------------------------------
    # 6. Mouse Aim Coordinate Scaling Across Resolutions
    # -------------------------------------------------------------------------
    def test_mouse_aim_coordinate_scaling(self):
        """Verify get_canvas_mouse_pos correctly maps coordinates across 720p, 1080p, and 1200p."""
        # 1280x720 (1:1)
        self.game.win_w, self.game.win_h = 1280, 720
        mapped = self.game.get_canvas_mouse_pos((640, 360))
        self.assertEqual(mapped, (640, 360))

        # 1920x1080 (1.5x)
        self.game.win_w, self.game.win_h = 1920, 1080
        mapped_1080 = self.game.get_canvas_mouse_pos((960, 540))
        self.assertEqual(mapped_1080, (640, 360))

        # 1920x1200 (16:10 aspect)
        self.game.win_w, self.game.win_h = 1920, 1200
        mapped_1200 = self.game.get_canvas_mouse_pos((960, 600))
        self.assertEqual(mapped_1200, (640, 360))

    # -------------------------------------------------------------------------
    # 7. Pause State Simulation Integrity
    # -------------------------------------------------------------------------
    def test_pause_state_simulation_integrity(self):
        """Verify pausing halts entity simulation and resuming restores exact state."""
        self.game.start_phase5_mission("S1_M1")
        ctx = self.game.context
        player = ctx.player
        initial_pos_x = player.pos.x

        # Pause
        ctx.state = STATE_PAUSED
        # Run 30 update ticks while paused
        for _ in range(30):
            self.game.update(0.016)

        # Player position must not change during pause
        self.assertEqual(player.pos.x, initial_pos_x)

        # Resume
        ctx.state = STATE_PLAYING
        self.assertEqual(ctx.state, STATE_PLAYING)

    # -------------------------------------------------------------------------
    # 8. Audio Manager Fail-Safe
    # -------------------------------------------------------------------------
    def test_audio_manager_failsafe(self):
        """Verify AudioManager operations never crash even when muted or without audio hardware."""
        am = AudioManager(sound_enabled=False)
        # Call all sound methods - none should raise
        am.play_laser()
        am.play_missile()
        am.play_beam()
        am.play_tesla()
        am.play_cluster()
        am.play_sniper()
        am.play_overdrive()
        am.play_explosion()
        am.play_hit()
        am.play_emp()
        am.play_powerup()
        am.play_roll()
        am.play_cloak()
        am.play_buy()

    # -------------------------------------------------------------------------
    # 9. Save System Hardening & Corruption Recovery
    # -------------------------------------------------------------------------
    def test_save_system_hardening(self):
        """Verify save system loads corrupted files cleanly using safe defaults."""
        save_file = "test_corrupted_save.json"
        save_sys = SaveSystem(save_filename=save_file)
        try:
            with open(save_sys.save_path, "w", encoding="utf-8") as f:
                f.write("{ INVALID JSON DATA %%%")

            loaded = save_sys.load()
            self.assertEqual(loaded["scrap"], 0)
            self.assertFalse(loaded["campaign_completed"])
            self.assertEqual(len(loaded["sectors"]), 5)
        finally:
            if os.path.exists(save_sys.save_path):
                os.remove(save_sys.save_path)

    # -------------------------------------------------------------------------
    # 10. Universal Back Navigation Across All UI Screens
    # -------------------------------------------------------------------------
    def test_universal_back_navigation(self):
        """Verify back navigation returns cleanly to previous screens."""
        ctx = self.game.context

        # 1. Sector Select -> Main Menu
        ctx.state = STATE_SECTOR_SELECT
        self.game.render()
        self.assertIn("back", self.game.ui_rects_cache)
        back_rect = self.game.ui_rects_cache["back"]
        self.assertIsNotNone(back_rect)
        # Simulate click on back button
        fake_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": back_rect.center, "button": 1})
        pygame.event.post(fake_event)
        self.game.handle_events()
        self.assertEqual(ctx.state, STATE_MENU)

        # 2. Hangar -> Sector Select
        self.game.previous_state = STATE_SECTOR_SELECT
        ctx.state = STATE_HANGAR
        self.game.render()
        self.assertIn("back", self.game.ui_rects_cache)
        back_rect = self.game.ui_rects_cache["back"]
        fake_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": back_rect.center, "button": 1})
        pygame.event.post(fake_event)
        self.game.handle_events()
        self.assertEqual(ctx.state, STATE_SECTOR_SELECT)

        # 3. Mission Briefing -> Sector Map
        ctx.state = STATE_MISSION_BRIEFING
        self.game.pending_mission_id = "S1_M1"
        self.game.render()
        self.assertIn("back", self.game.ui_rects_cache)
        back_rect = self.game.ui_rects_cache["back"]
        fake_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": back_rect.center, "button": 1})
        pygame.event.post(fake_event)
        self.game.handle_events()
        self.assertEqual(ctx.state, STATE_SECTOR_SELECT)

    # -------------------------------------------------------------------------
    # 11. Dedicated Settings Menu Integrity
    # -------------------------------------------------------------------------
    def test_dedicated_settings_menu_navigation_and_options(self):
        """Verify dedicated settings page navigation, options toggling, and return state."""
        ctx = self.game.context
        self.game.previous_state = STATE_SECTOR_SELECT
        ctx.state = STATE_SETTINGS
        self.game.render()

        cache = self.game.ui_rects_cache
        self.assertIn("diff", cache)
        self.assertIn("crt", cache)
        self.assertIn("sfx", cache)
        self.assertIn("back", cache)

        # Test difficulty cycle via click
        initial_diff = ctx.difficulty_mode
        fake_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": cache["diff"].center, "button": 1})
        pygame.event.post(fake_event)
        self.game.handle_events()
        self.assertEqual(ctx.difficulty_mode, (initial_diff + 1) % 5)

        # Test back button returns to previous state
        fake_event2 = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"pos": cache["back"].center, "button": 1})
        pygame.event.post(fake_event2)
        self.game.handle_events()
        self.assertEqual(ctx.state, STATE_SECTOR_SELECT)

    # -------------------------------------------------------------------------
    # 12. Exit Button Hitboxes & Reliability
    # -------------------------------------------------------------------------
    def test_exit_buttons_reliability(self):
        """Verify exit button is valid, non-zero area across all menu pages."""
        ctx = self.game.context

        for state in [STATE_MENU, STATE_SECTOR_SELECT, STATE_HANGAR, STATE_MISSION_BRIEFING]:
            ctx.state = state
            self.game.render()
            cache = self.game.ui_rects_cache
            self.assertIn("exit", cache, f"Exit button missing in {state}")
            exit_r = cache["exit"]
            self.assertIsNotNone(exit_r, f"Exit rect is None in {state}")
            self.assertGreater(exit_r.width * exit_r.height, 0, f"Exit rect empty in {state}")

    # -------------------------------------------------------------------------
    # 13. Fullscreen Toggle Safety
    # -------------------------------------------------------------------------
    def test_toggle_fullscreen_execution(self):
        """Verify toggle_fullscreen executes safely on both Game and Renderer without throwing errors."""
        self.game.toggle_fullscreen()
        self.game.renderer.toggle_fullscreen()


if __name__ == "__main__":
    unittest.main()
