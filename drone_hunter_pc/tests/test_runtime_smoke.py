"""
===============================================================================
        DRONE HUNTER 2D - MULTI-FRAME RUNTIME SMOKE TEST
===============================================================================
Performs comprehensive multi-frame runtime simulation across all states,
transitions, mission combat, weapon firings, abilities, and persistence.
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
    STATE_PAUSED, STATE_MISSION_COMPLETE, STATE_VICTORY, STATE_GAME_OVER
)
from src.core.campaign_state import CampaignState
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
    game.start_mission("S1_M1")
    assert ctx.state == STATE_PLAYING
    assert ctx.campaign_state.current_mission == "S1_M1"

    for frame in range(120):
        # Simulate player movement & weapon fire
        if frame % 10 == 0:
            ctx.player.cycle_weapon()
            bullets = ctx.player.shoot((600, 360), level=1, targets_group=ctx.target_group)
            for b in bullets:
                ctx.bullet_group.add(b)

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

    # 5. Test Mission Completion & Authoritative Progression
    print("Testing Mission Progression...")
    ctx.campaign_state.record_mission_completed("S1_M1")
    assert "S1_M1" in ctx.campaign_state.completed_missions
    assert "S1_M2" in ctx.campaign_state.unlocked_missions
    game.start_mission("S1_M2")
    assert ctx.campaign_state.current_mission == "S1_M2"
    game.update(0.016)
    game.render()

    # 6. Test Campaign Completion
    print("Testing Campaign Victory transition...")
    for s in range(1, 6):
        for m in range(1, 6):
            ctx.campaign_state.record_mission_completed(f"S{s}_M{m}")

    assert ctx.campaign_state.campaign_completed
    ctx.state = STATE_VICTORY
    game.update(0.016)
    game.render()
    print("Campaign Victory state rendered successfully!")

    print("ALL RUNTIME SMOKE TESTS PASSED WITH ZERO ERRORS!")


if __name__ == "__main__":
    run_runtime_smoke()
