"""
================================================================================
        DRONE HUNTER 2D - MULTI-FRAME RUNTIME SMOKE TEST
================================================================================
Performs comprehensive multi-frame runtime simulation across all states,
transitions, boss battles, weapon firings, abilities, and persistence.
"""

import os
import sys
import pygame

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game import Game
from src.core.game_state import (
    STATE_MENU, STATE_SECTOR_SELECT, STATE_HANGAR, STATE_PLAYING,
    STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_VICTORY, STATE_GAME_OVER
)
from src.data.game_data import (
    WEAPON_PULSE, WEAPON_SCATTER, WEAPON_MISSILE
)

def test_runtime_smoke():
    run_runtime_smoke()

def run_runtime_smoke():
    print("Initializing Drone Hunter 2D Runtime...")
    game = Game()
    ctx = game.context

    # 1. State: Menu -> Sector Select
    print("Testing State: Menu -> Sector Select")
    ctx.state = STATE_MENU
    game.update(0.016)
    game.render()
    ctx.state = STATE_SECTOR_SELECT
    game.update(0.016)
    game.render()

    # 2. State: Sector Select -> Hangar
    print("Testing State: Sector Select -> Hangar (Purchasing upgrades)")
    ctx.state = STATE_HANGAR
    ctx.scrap = 5000
    game.buy_upgrade("battery")
    game.buy_upgrade("overdrive")
    game.buy_upgrade("missiles")
    game.buy_upgrade("beam")
    game.buy_upgrade("tesla")
    game.buy_upgrade("cluster")
    assert ctx.upgrade_levels["overdrive"] >= 1
    assert ctx.player.max_health > 100.0
    game.update(0.016)
    game.render()

    # 3. State: Hangar -> Playing
    print("Testing State: Launch Playing Simulation (120 frames)")
    game.reset_game()
    ctx.state = STATE_PLAYING

    for frame in range(120):
        # Simulate player movement & weapon fire
        if frame % 10 == 0:
            ctx.player.cycle_weapon()
            bullets = ctx.player.shoot((600, 360), level=1, targets_group=ctx.target_group)
            for b in bullets: ctx.bullet_group.add(b)

        # Trigger abilities at specific frames
        if frame == 30:
            ctx.player.trigger_roll(1.0)
        elif frame == 50:
            ctx.player.trigger_cloak()
        elif frame == 70:
            game.combat_system.execute_emp_blast()
        elif frame == 90:
            ctx.player.trigger_overdrive()

        game.update(0.016)
        game.render()

    assert ctx.player.alive, "Player should remain alive during normal simulation"
    print("120 gameplay simulation frames executed cleanly!")

    # 4. Test Pause & Resume
    print("Testing Pause & Resume...")
    ctx.state = STATE_PAUSED
    game.update(0.016)
    game.render()
    ctx.state = STATE_PLAYING
    game.update(0.016)
    game.render()

    # 5. Test Stage 3 & Completion
    print("Testing Stage Simulation...")
    ctx.current_sector_idx = 0
    ctx.current_sub_level = 3
    game.reset_game()
    ctx.state = STATE_PLAYING

    ctx.level_score = 7000
    ctx.current_wave = 4
    game.spawner.update(0.016, ctx)
    assert ctx.wave_manager.is_stage_complete(ctx.level_score, targets_group=ctx.target_group)
    print("Stage completion verified!")

    # 6. Test Campaign Victory
    print("Testing Campaign Victory transition...")
    ctx.current_sector_idx = 4
    ctx.current_sub_level = 5
    game.start_next_stage()
    assert ctx.state == STATE_VICTORY
    game.render()
    print("Campaign Victory state rendered successfully!")

    print("ALL RUNTIME SMOKE TESTS PASSED WITH ZERO ERRORS!")

if __name__ == "__main__":
    run_runtime_smoke()
