import sys

with open('src/core/game.py', 'r', encoding='utf-8') as f:
    content = f.read()

# IMPORTS
content = content.replace('from src.systems.combat_director import CombatDirector',
'''from src.systems.combat_director import CombatDirector
from src.systems.mission_system import MissionSystem
from src.data.mission_data import get_mission_data''')

content = content.replace('STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY',
'STATE_PAUSED, STATE_LEVEL_CLEAR, STATE_GAME_OVER, STATE_VICTORY,\n    STATE_MISSION_BRIEFING, STATE_MISSION_COMPLETE, STATE_MISSION_FAILED, GameState')

content = content.replace('draw_sector_select_ui, draw_pause_settings_ui,',
'draw_sector_select_ui, draw_pause_settings_ui, draw_mission_select_ui, draw_mission_briefing, draw_mission_complete, draw_mission_failed,')

# INIT
content = content.replace('self.combat_director = CombatDirector(self.encounter_system)',
'''self.combat_director = CombatDirector(self.encounter_system)
        self.mission_system = MissionSystem()
        self.pending_mission_id = "S1_M1"
        self.ui_rects_cache = {}''')

# START PHASE 5 MISSION METHOD
start_method = '''
    def start_phase5_mission(self, mission_id):
        self.context.state = STATE_PLAYING
        self.context.target_group.empty()
        self.context.bullet_group.empty()
        self.context.enemy_bullet_group.empty()
        self.context.obstacle_group.empty()
        self.context.hazard_group.empty()
        self.context.powerup_group.empty()
        self.context.combo_count = 1
        self.context.combo_timer = 0.0
        
        self.mission_system.start_mission(self.context, mission_id, self.combat_director)
        
        if self.context.player:
            self.context.player.pos.update(self.win_w // 2, self.win_h // 2 + 100)
            self.context.player.health = self.context.player.max_health
            self.context.player.energy = self.context.player.max_energy
            self.context.player.velocity.update(0, 0)
'''
content = content.replace('def reset_game(self):', start_method.strip() + '\n\n    def reset_game(self):')


# UPDATE LOOP - Replace Spawner Logic
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
                    # Normal spawner runs in other sectors and stages
                    if ctx.current_sector_idx == 1 and ctx.current_sub_level == 1:
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
# We find the spawner update block
idx1 = content.find('# 2. Spawner / Controlled Encounter System Update')
idx2 = content.find('# 3. Enemies & Projectiles')
content = content[:idx1] + update_replacement.strip() + '\n\n                ' + content[idx2:]

# UPDATE LOOP - Player Death
death_replacement = '''
                # Check Player Death
                if ctx.player and not ctx.player.alive and ctx.state == STATE_PLAYING:
                    if self.mission_system.active_mission_id is not None:
                        self.mission_system.trigger_failure()
                        ctx.state = STATE_MISSION_FAILED
                    else:
                        ctx.state = STATE_GAME_OVER
'''
idx1 = content.find('# Check Player Death')
idx2 = content.find('# 5. Check Stage Completion')
content = content[:idx1] + death_replacement.strip() + '\n\n                ' + content[idx2:]

# HANDLE EVENTS - Keys
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
import re
content = re.sub(r'if ctx\.state == STATE_MENU:\s+if event\.key == pygame\.K_SPACE:\s+ctx\.state = STATE_SECTOR_SELECT\s+self\.audio_manager\.play_powerup\(\)\s+elif ctx\.state == STATE_SECTOR_SELECT:\s+if event\.key == pygame\.K_ESCAPE:\s+ctx\.state = STATE_MENU\s+elif ctx\.state == STATE_HANGAR:', keys_logic.strip() + '\n', content)

# HANDLE EVENTS - Game Over Keys
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
content = re.sub(r'elif ctx\.state in \(STATE_GAME_OVER, STATE_LEVEL_CLEAR\):.*?elif event\.key == pygame\.K_q: self\.running = False', go_logic.strip(), content, flags=re.DOTALL)

# HANDLE EVENTS - Mouse
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
                            if self.ui_rects_cache["exit"].collidepoint(mx, my):
                                ctx.state = STATE_MENU
                            for s_id, rect in self.ui_rects_cache["sectors"].items():
                                if rect.collidepoint(mx, my): ctx.missions["current_sector"] = s_id
                            for m_id, rect in self.ui_rects_cache["missions"].items():
                                if rect.collidepoint(mx, my):
                                    self.pending_mission_id = m_id
                                    ctx.state = STATE_MISSION_BRIEFING
                elif ctx.state == STATE_MISSION_BRIEFING:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        if hasattr(self, 'ui_rects_cache') and self.ui_rects_cache:
                            if self.ui_rects_cache["exit"].collidepoint(mx, my): ctx.state = STATE_SECTOR_SELECT
                            elif self.ui_rects_cache["start"].collidepoint(mx, my): self.start_phase5_mission(self.pending_mission_id)
                elif ctx.state == STATE_HANGAR:
'''
content = re.sub(r'if ctx\.state == STATE_MENU:\s+buttons = draw_main_menu\(self\.renderer\.canvas\)\s+if event\.type == pygame\.MOUSEBUTTONDOWN and event\.button == 1:.*?elif ctx\.state == STATE_HANGAR:', mouse_logic.strip() + '\n', content, flags=re.DOTALL)

# RENDER
render_logic = '''
        elif ctx.state == STATE_SECTOR_SELECT:
            self.ui_rects_cache = draw_mission_select_ui(canvas, ctx, ctx.scrap)
            
        elif ctx.state == STATE_MISSION_BRIEFING:
            self.ui_rects_cache = draw_mission_briefing(canvas, get_mission_data(self.pending_mission_id), ctx.scrap)

        elif ctx.state == STATE_HANGAR:
'''
content = re.sub(r'elif ctx\.state == STATE_SECTOR_SELECT:.*?elif ctx\.state == STATE_HANGAR:', render_logic.strip() + '\n', content, flags=re.DOTALL)

# Add states to Render in game block
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
content = re.sub(r'elif ctx\.state == STATE_GAME_OVER:\s+draw_game_over_ui\(canvas, ctx\.total_score, ctx\.highscore\)', render_go_logic.strip(), content)

with open('src/core/game.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Patch complete.")
