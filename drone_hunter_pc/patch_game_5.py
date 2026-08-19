import re

with open('src/core/game.py', 'r', encoding='utf-8') as f:
    content = f.read()

mouse_logic = '''
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = self.get_canvas_mouse_pos(getattr(event, "pos", None))
                if ctx.state == STATE_MENU:
                    buttons = draw_main_menu(self.renderer.canvas)
                    if buttons['play'].collidepoint(mx, my): ctx.state = STATE_SECTOR_SELECT
                    elif buttons['hangar'].collidepoint(mx, my): ctx.state = STATE_HANGAR
                    elif buttons['exit'].collidepoint(mx, my): self.running = False
                elif ctx.state == STATE_SECTOR_SELECT:
                    if hasattr(self, 'ui_rects_cache') and self.ui_rects_cache:
                        if self.ui_rects_cache.get("exit") and self.ui_rects_cache["exit"].collidepoint(mx, my): ctx.state = STATE_MENU
                        if self.ui_rects_cache.get("diff_rect") and self.ui_rects_cache["diff_rect"].collidepoint(mx, my): ctx.difficulty_mode = (ctx.difficulty_mode + 1) % 4
                        if "sectors" in self.ui_rects_cache:
                            for s_id, rect in self.ui_rects_cache["sectors"].items():
                                if rect.collidepoint(mx, my): ctx.missions["current_sector"] = s_id
                        if "missions" in self.ui_rects_cache:
                            for m_id, rect in self.ui_rects_cache["missions"].items():
                                if rect.collidepoint(mx, my):
                                    self.pending_mission_id = m_id
                                    ctx.state = STATE_MISSION_BRIEFING
                elif ctx.state == STATE_MISSION_BRIEFING:
                    if hasattr(self, 'ui_rects_cache') and self.ui_rects_cache:
                        if self.ui_rects_cache.get("exit") and self.ui_rects_cache["exit"].collidepoint(mx, my): ctx.state = STATE_SECTOR_SELECT
                        elif self.ui_rects_cache.get("start") and self.ui_rects_cache["start"].collidepoint(mx, my): self.start_phase5_mission(self.pending_mission_id)
                elif ctx.state == STATE_HANGAR:
'''

content = re.sub(r'elif event\.type == pygame\.MOUSEBUTTONDOWN:.*?elif ctx\.state == STATE_HANGAR:', mouse_logic.strip() + '\n', content, flags=re.DOTALL)

with open('src/core/game.py', 'w', encoding='utf-8') as f:
    f.write(content)
