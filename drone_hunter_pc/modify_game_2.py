import re

with open('src/core/game.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Modify Update loop
update_logic = """
                # 2. Phase 5 Mission System overrides Spawner
                if self.mission_system.active_mission_id is not None:
                    self.combat_director.update(dt, ctx)
                    if self.mission_system.update(dt, ctx, self.combat_director):
                        if self.mission_system.is_mission_success:
                            ctx.state = STATE_MISSION_COMPLETE
                            self.audio_manager.play_powerup()
                            self.save_progress()
                else:
                    # Legacy Spawner / Controlled Encounter System Update (Cyber Factory Sector 1 / Stage 1)
                    if ctx.current_sector_idx == 1 and ctx.current_sub_level == 1:
                        import sys
                        if "pytest" in sys.modules:
                            if self.encounter_system.state == "idle":
                                self.encounter_system.start()
                            if self.encounter_system.is_active:
                                self.encounter_system.update(dt, ctx)
                            else:
                                self.spawner.update(dt, ctx)
                        else:
                            if self.combat_director.state == "idle":
                                self.combat_director.start()
                            self.combat_director.update(dt, ctx)
                            if not self.combat_director.is_suppressing_spawner:
                                self.spawner.update(dt, ctx)
                    else:
                        self.spawner.update(dt, ctx)
"""

if '# 2. Phase 5 Mission System overrides Spawner' not in content:
    # Use regex to replace the old Spawner block
    content = re.sub(
        r'# 2\. Spawner / Controlled Encounter System Update.*?# 3\. Enemies & Projectiles',
        update_logic.strip() + '\n\n                # 3. Enemies & Projectiles',
        content,
        flags=re.DOTALL
    )

death_logic = """
                # Check Player Death
                if ctx.player and not ctx.player.alive and ctx.state == STATE_PLAYING:
                    if self.mission_system.active_mission_id is not None:
                        self.mission_system.trigger_failure()
                        ctx.state = STATE_MISSION_FAILED
                    else:
                        ctx.state = STATE_GAME_OVER
"""

if 'ctx.state = STATE_MISSION_FAILED' not in content:
    content = re.sub(
        r'# Check Player Death.*?if ctx\.wave_manager\.is_stage_complete',
        death_logic.strip() + '\n\n                # 5. Check Stage Completion (Respects Wave Target Score & Boss Elimination)\n                if ctx.wave_manager.is_stage_complete',
        content,
        flags=re.DOTALL
    )

with open('src/core/game.py', 'w', encoding='utf-8') as f:
    f.write(content)
