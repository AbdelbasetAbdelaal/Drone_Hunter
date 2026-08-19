import sys

with open('src/core/game.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_handle_events = False
in_render = False

for i, line in enumerate(lines):
    # 1. Imports
    if "from src.systems.combat_director import CombatDirector" in line:
        new_lines.append("from src.systems.combat_director import CombatDirector\n")
        new_lines.append("from src.systems.mission_system import MissionSystem\n")
        new_lines.append("from src.data.mission_data import get_mission_data\n")
        continue

    if "STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY" in line:
        new_lines.append("    STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY,\n")
        new_lines.append("    STATE_MISSION_BRIEFING, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, GameState\n")
        continue

    if "draw_sector_select_ui, draw_pause_settings_ui," in line:
        new_lines.append("    draw_sector_select_ui, draw_pause_settings_ui, draw_mission_select_ui, draw_mission_briefing, draw_mission_complete, draw_mission_failed,\n")
        continue
        
    # 2. Init
    if "self.combat_director = CombatDirector(self.encounter_system)" in line:
        new_lines.append("        self.combat_director = CombatDirector(self.encounter_system)\n")
        new_lines.append("        self.mission_system = MissionSystem()\n")
        new_lines.append("        self.pending_mission_id = 'S1_M1'\n")
        new_lines.append("        self.ui_rects_cache = {}\n")
        continue

    # 3. reset_game replacement
    if "def reset_game(self):" in line:
        new_lines.append("    def start_phase5_mission(self, mission_id):\n")
        new_lines.append("        self.context.state = STATE_PLAYING\n")
        new_lines.append("        self.context.target_group.empty()\n")
        new_lines.append("        self.context.bullet_group.empty()\n")
        new_lines.append("        self.context.enemy_bullet_group.empty()\n")
        new_lines.append("        self.context.obstacle_group.empty()\n")
        new_lines.append("        self.context.hazard_group.empty()\n")
        new_lines.append("        self.context.powerup_group.empty()\n")
        new_lines.append("        self.context.combo_count = 1\n")
        new_lines.append("        self.context.combo_timer = 0.0\n")
        new_lines.append("        self.mission_system.start_mission(self.context, mission_id, self.combat_director)\n")
        new_lines.append("        if self.context.player:\n")
        new_lines.append("            self.context.player.pos.update(self.win_w // 2, self.win_h // 2 + 100)\n")
        new_lines.append("            self.context.player.health = self.context.player.max_health\n")
        new_lines.append("            self.context.player.energy = self.context.player.max_energy\n")
        new_lines.append("            self.context.player.velocity.update(0,0)\n\n")
        new_lines.append("    def reset_game(self):\n")
        continue

    # 4. update logic
    if "if ctx.current_sector_idx == 1 and ctx.current_sub_level == 1:" in line and "import sys" in lines[i+1]:
        # Ignore lines until "else: self.spawner.update(dt, ctx)"
        pass
        
    # We will just replace the specific sections
    new_lines.append(line)

# Let's write the whole file as a string and just do targeted replaces.
content = "".join(new_lines)

# update logic
update_replacement = '''
                # 2. Phase 5 Mission System overrides Spawner
                if self.mission_system.active_mission_id is not None:
                    self.combat_director.update(dt, ctx)
                    if self.mission_system.update(dt, ctx, self.combat_director):
                        if self.mission_system.is_mission_success:
                            ctx.state = STATE_MISSION_COMPLETE
                            self.audio_manager.play_powerup()
                            self.save_progress()
                else:
                    if ctx.current_sector_idx == 1 and ctx.current_sub_level == 1:
                        import sys
                        if "pytest" in sys.modules:
                            if self.encounter_system.state == "idle": self.encounter_system.start()
                            if self.encounter_system.is_active: self.encounter_system.update(dt, ctx)
                            else: self.spawner.update(dt, ctx)
                        else:
                            if self.combat_director.state == "idle": self.combat_director.start()
                            self.combat_director.update(dt, ctx)
                            if not self.combat_director.is_suppressing_spawner: self.spawner.update(dt, ctx)
                    else:
                        self.spawner.update(dt, ctx)
'''
import re
content = re.sub(r'# 2\. Spawner / Controlled Encounter System Update.*?# 3\. Enemies & Projectiles', update_replacement.strip() + '\n\n                # 3. Enemies & Projectiles', content, flags=re.DOTALL)

death_replacement = '''
                # Check Player Death
                if ctx.player and not ctx.player.alive and ctx.state == STATE_PLAYING:
                    if self.mission_system.active_mission_id is not None:
                        self.mission_system.trigger_failure()
                        ctx.state = STATE_MISSION_FAILED
                    else:
                        ctx.state = STATE_GAME_OVER
'''
content = re.sub(r'# Check Player Death.*?# 5\. Check Stage Completion', death_replacement.strip() + '\n\n                # 5. Check Stage Completion', content, flags=re.DOTALL)


keys_logic = '''
                if ctx.state == STATE_MENU:
                    if event.key == pygame.K_SPACE:
                        ctx.state = STATE_SECTOR_SELECT
                        self.audio_manager.play_powerup()
                elif ctx.state == STATE_SECTOR_SELECT:
                    if event.key == pygame.K_ESCAPE:
                        ctx.state = STATE_MENU
                elif ctx.state == STATE_MISSION_BRIEFING:
                    if event.key == pygame.K_SPACE:
                        self.start_phase5_mission(self.pending_mission_id)
                    elif event.key == pygame.K_ESCAPE:
                        ctx.state = STATE_SECTOR_SELECT
                elif ctx.state == STATE_HANGAR:
'''
content = re.sub(r'if ctx\.state == STATE_MENU:\n.*?elif ctx\.state == STATE_HANGAR:', keys_logic.strip() + '\n', content, flags=re.DOTALL, count=1)


go_logic = '''
                elif ctx.state in (STATE_GAME_OVER, STATE_LEVEL_CLEAR, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED):
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if ctx.state == STATE_LEVEL_CLEAR: self.start_next_stage()
                        elif ctx.state == STATE_MISSION_COMPLETE: ctx.state = STATE_SECTOR_SELECT
                        elif ctx.state == STATE_MISSION_FAILED: self.start_phase5_mission(self.mission_system.active_mission_id)
                        else: self.reset_game()
                    elif event.key == pygame.K_m: ctx.state = STATE_SECTOR_SELECT
                    elif event.key == pygame.K_q: self.running = False
'''
content = re.sub(r'elif ctx\.state in \(STATE_GAME_OVER, STATE_LEVEL_CLEAR\):.*?elif event\.key == pygame\.K_q:\s*self\.running = False', go_logic.strip(), content, flags=re.DOTALL)

# Handle events - MOUSE
mouse_logic = '''
                if ctx.state == STATE_MENU:
                    buttons = draw_main_menu(self.renderer.canvas)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        if buttons[0].collidepoint(mx, my): ctx.state = STATE_SECTOR_SELECT
                        elif buttons[1].collidepoint(mx, my): ctx.state = STATE_HANGAR
                        elif buttons[3].collidepoint(mx, my): self.running = False
                elif ctx.state == STATE_SECTOR_SELECT:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        if hasattr(self, 'ui_rects_cache') and self.ui_rects_cache:
                            if self.ui_rects_cache["exit"].collidepoint(mx, my): ctx.state = STATE_MENU
                            if "sectors" in self.ui_rects_cache:
                                for s_id, rect in self.ui_rects_cache["sectors"].items():
                                    if rect.collidepoint(mx, my): ctx.missions["current_sector"] = s_id
                            if "missions" in self.ui_rects_cache:
                                for m_id, rect in self.ui_rects_cache["missions"].items():
                                    if rect.collidepoint(mx, my):
                                        self.pending_mission_id = m_id
                                        ctx.state = STATE_MISSION_BRIEFING
                elif ctx.state == STATE_MISSION_BRIEFING:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        if hasattr(self, 'ui_rects_cache') and self.ui_rects_cache:
                            if self.ui_rects_cache.get("exit") and self.ui_rects_cache["exit"].collidepoint(mx, my): ctx.state = STATE_SECTOR_SELECT
                            elif self.ui_rects_cache.get("start") and self.ui_rects_cache["start"].collidepoint(mx, my): self.start_phase5_mission(self.pending_mission_id)
                elif ctx.state == STATE_HANGAR:
'''
# I must match the MOUSE event section specifically
content = re.sub(r'if ctx\.state == STATE_MENU:\s+buttons = draw_main_menu.*?elif ctx\.state == STATE_HANGAR:', mouse_logic.strip() + '\n', content, flags=re.DOTALL)


# RENDER
render_logic = '''
        elif ctx.state == STATE_SECTOR_SELECT:
            self.ui_rects_cache = draw_mission_select_ui(canvas, ctx, ctx.scrap)
        elif ctx.state == STATE_MISSION_BRIEFING:
            self.ui_rects_cache = draw_mission_briefing(canvas, get_mission_data(self.pending_mission_id), ctx.scrap)
        elif ctx.state == STATE_HANGAR:
'''
content = re.sub(r'elif ctx\.state == STATE_SECTOR_SELECT:\s*draw_sector_select_ui.*?elif ctx\.state == STATE_HANGAR:', render_logic.strip() + '\n', content, flags=re.DOTALL)

content = content.replace('elif ctx.state in (STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER):', 'elif ctx.state in (STATE_PLAYING, STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED):')

render_go_logic = '''
            elif ctx.state == STATE_GAME_OVER:
                draw_game_over_ui(canvas, ctx.total_score, ctx.highscore)
            elif ctx.state == STATE_MISSION_COMPLETE:
                is_sec = (self.mission_system.active_mission_data["mission_number"] == 5)
                draw_mission_complete(canvas, self.mission_system.active_mission_data, self.mission_system.is_mission_success, is_sec)
            elif ctx.state == STATE_MISSION_FAILED:
                draw_mission_failed(canvas, ctx.scrap)
'''
content = re.sub(r'elif ctx\.state == STATE_GAME_OVER:\s*draw_game_over_ui\(canvas, ctx\.total_score, ctx\.highscore\)', render_go_logic.strip(), content)

with open('src/core/game.py', 'w', encoding='utf-8') as f:
    f.write(content)
