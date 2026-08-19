import re

with open('src/core/game.py', 'r', encoding='utf-8') as f:
    content = f.read()

events_logic = """
                if ctx.state == STATE_MENU:
                    if event.key == pygame.K_SPACE:
                        ctx.state = GameState.SECTOR_SELECT.value
                        self.audio_manager.play_powerup()
                elif ctx.state == GameState.SECTOR_SELECT.value:
                    if event.key == pygame.K_ESCAPE:
                        ctx.state = STATE_MENU
                elif ctx.state == GameState.MISSION_BRIEFING.value:
                    if event.key == pygame.K_SPACE:
                        self.start_phase5_mission(self.pending_mission_id)
                    elif event.key == pygame.K_ESCAPE:
                        ctx.state = GameState.SECTOR_SELECT.value
                elif ctx.state == STATE_HANGAR:
"""

if 'GameState.MISSION_BRIEFING.value' not in content:
    content = re.sub(
        r'if ctx\.state == STATE_MENU:.*?elif ctx\.state == STATE_HANGAR:',
        events_logic.strip() + '\n',
        content,
        flags=re.DOTALL
    )

mouse_logic = """
                if ctx.state == STATE_MENU:
                    buttons = draw_main_menu(self.renderer.canvas)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        if buttons[0].collidepoint(mx, my): # DEPLOY
                            ctx.state = GameState.SECTOR_SELECT.value
                        elif buttons[1].collidepoint(mx, my): # HANGAR
                            ctx.state = STATE_HANGAR
                        elif buttons[3].collidepoint(mx, my): # QUIT
                            self.running = False
                elif ctx.state == GameState.SECTOR_SELECT.value:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        if hasattr(self, 'ui_rects_cache'):
                            if self.ui_rects_cache["exit"].collidepoint(mx, my):
                                ctx.state = STATE_MENU
                            for s_id, rect in self.ui_rects_cache["sectors"].items():
                                if rect.collidepoint(mx, my):
                                    ctx.missions["current_sector"] = s_id
                            for m_id, rect in self.ui_rects_cache["missions"].items():
                                if rect.collidepoint(mx, my):
                                    self.pending_mission_id = m_id
                                    ctx.state = GameState.MISSION_BRIEFING.value
                elif ctx.state == GameState.MISSION_BRIEFING.value:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mx, my = pygame.mouse.get_pos()
                        if hasattr(self, 'ui_rects_cache'):
                            if self.ui_rects_cache["exit"].collidepoint(mx, my):
                                ctx.state = GameState.SECTOR_SELECT.value
                            elif self.ui_rects_cache["start"].collidepoint(mx, my):
                                self.start_phase5_mission(self.pending_mission_id)
                elif ctx.state == STATE_HANGAR:
"""

if 'self.start_phase5_mission' not in content:
    content = re.sub(
        r'if ctx\.state == STATE_MENU:.*?buttons = draw_main_menu.*?elif ctx\.state == STATE_HANGAR:',
        mouse_logic.strip() + '\n',
        content,
        flags=re.DOTALL
    )

retry_logic = """
                elif ctx.state in (STATE_GAME_OVER, STATE_LEVEL_CLEAR, GameState.MISSION_COMPLETE.value, GameState.MISSION_FAILED.value):
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        if ctx.state == STATE_LEVEL_CLEAR: self.start_next_stage()
                        elif ctx.state == GameState.MISSION_COMPLETE.value: ctx.state = GameState.SECTOR_SELECT.value
                        elif ctx.state == GameState.MISSION_FAILED.value: self.start_phase5_mission(self.mission_system.active_mission_id)
                        else: self.reset_game()
                    elif event.key == pygame.K_m: ctx.state = GameState.SECTOR_SELECT.value
                    elif event.key == pygame.K_q: self.running = False
"""

if 'GameState.MISSION_COMPLETE.value' not in content:
    content = re.sub(
        r'elif ctx\.state in \(STATE_GAME_OVER, STATE_LEVEL_CLEAR\):.*?self\.running = False',
        retry_logic.strip(),
        content,
        flags=re.DOTALL
    )
    
start_phase5_method = """
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
            self.context.player.velocity.update(0,0)
"""

if 'def start_phase5_mission' not in content:
    content = content.replace('def reset_game(self):', start_phase5_method + '\n    def reset_game(self):')


with open('src/core/game.py', 'w', encoding='utf-8') as f:
    f.write(content)
