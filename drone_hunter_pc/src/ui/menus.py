import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON,
    COLOR_EMERALD, COLOR_WHITE, COLOR_BG, COLOR_HUD
)
from src.data.game_data import (
    DIFFICULTY_MODIFIERS, DIFFICULTY_NAMES, SECTORS
)
from src.ui.font_manager import font_title, font_banner, font_card, font_hud, font_gameover
from src.data.mission_data import SECTORS_PHASE5, get_missions_for_sector

COLOR_TEXT_DIM = (120, 140, 160)

def draw_exit_button(canvas: pygame.Surface) -> pygame.Rect:
    vw, vh = canvas.get_size()
    btn_rect = pygame.Rect(vw - 140, vh - 55, 120, 38)
    mx, my = pygame.mouse.get_pos()
    hov = btn_rect.collidepoint(mx, my)

    pygame.draw.rect(canvas, (40, 20, 25) if hov else (25, 15, 20), btn_rect, border_radius=6)
    pygame.draw.rect(canvas, COLOR_CRIMSON if hov else (150, 40, 50), btn_rect, 2, border_radius=6)
    
    lbl = font_card.render("[Q] QUIT", True, COLOR_CRIMSON if hov else (200, 100, 100))
    canvas.blit(lbl, lbl.get_rect(center=btn_rect.center))
    return btn_rect

def draw_main_menu(canvas: pygame.Surface) -> list[pygame.Rect]:
    canvas.fill((5, 10, 15))
    vw, vh = canvas.get_size()

    title = font_title.render("DRONE HUNTER", True, COLOR_CYAN)
    canvas.blit(title, title.get_rect(center=(vw // 2, vh // 2 - 80)))
    
    sub = font_banner.render("PRESS SPACE TO DEPLOY", True, COLOR_EMERALD)
    canvas.blit(sub, sub.get_rect(center=(vw // 2, vh // 2 - 20)))

    btn_labels = ["DEPLOY", "HANGAR", "QUIT"]
    buttons = []
    by = vh // 2 + 50
    mx, my = pygame.mouse.get_pos()

    for idx, label in enumerate(btn_labels):
        r = pygame.Rect(vw // 2 - 100, by + idx * 46, 200, 38)
        hov = r.collidepoint(mx, my)
        pygame.draw.rect(canvas, (20, 30, 50) if hov else (10, 15, 26), r, border_radius=6)
        pygame.draw.rect(canvas, COLOR_CYAN if hov else (30, 45, 65), r, 2, border_radius=6)
        
        lbl_surf = font_card.render(label, True, COLOR_WHITE if hov else (180, 200, 220))
        canvas.blit(lbl_surf, lbl_surf.get_rect(center=r.center))
        buttons.append(r)
        
    return {
        'play': buttons[0],
        'hangar': buttons[1],
        'exit': buttons[2]
    }

def draw_mission_select_ui(canvas: pygame.Surface, ctx, scrap: int) -> dict:
    """Renders the combined Phase 5 Sector and Mission selection UI."""
    canvas.fill(COLOR_BG)
    vw, vh = canvas.get_size()
    mx, my = pygame.mouse.get_pos()
    
    # Header
    header_rect = pygame.Rect(30, 16, vw - 60, 52)
    pygame.draw.rect(canvas, (15, 23, 42), header_rect, border_radius=6)
    pygame.draw.rect(canvas, COLOR_CYAN, header_rect, 2, border_radius=6)
    
    t_hdr = font_title.render("COMBAT SECTOR MAP", True, COLOR_CYAN)
    coin_hdr = font_banner.render(f"SCRAP: {scrap:,}", True, COLOR_GOLD)
    canvas.blit(t_hdr, (48, 18))
    canvas.blit(coin_hdr, (vw - 260, 28))

    # Difficulty Badge Button
    diff_name = DIFFICULTY_NAMES[ctx.difficulty_mode]
    diff_col = DIFFICULTY_MODIFIERS[ctx.difficulty_mode]["badge_color"]
    diff_rect = pygame.Rect(vw - 500, 28, 220, 36)
    pygame.draw.rect(canvas, (20, 30, 50), diff_rect, border_radius=6)
    pygame.draw.rect(canvas, diff_col, diff_rect, 2, border_radius=6)
    t_diff = font_card.render(f"DIFFICULTY: {diff_name}", True, diff_col)
    canvas.blit(t_diff, t_diff.get_rect(center=diff_rect.center))
    
    interactive_rects = {"diff_rect": diff_rect, "exit": draw_exit_button(canvas), "sectors": {}, "missions": {}}
    
    # Sectors List (Left side)
    left_pane = pygame.Rect(30, 90, 350, vh - 110)
    pygame.draw.rect(canvas, (15, 20, 30), left_pane, border_radius=8)
    pygame.draw.rect(canvas, (35, 45, 60), left_pane, 2, border_radius=8)
    
    s_lbl = font_banner.render("SECTORS", True, COLOR_WHITE)
    canvas.blit(s_lbl, (50, 105))
    
    current_selected_sector = ctx.missions["current_sector"]
    
    sy = 145
    for sec in SECTORS_PHASE5:
        s_id = sec["id"]
        is_unlocked = s_id in ctx.sector_progress["unlocked"]
        is_completed = s_id in ctx.sector_progress["completed"]
        is_selected = (s_id == current_selected_sector)
        
        s_rect = pygame.Rect(45, sy, 320, 50)
        hov = s_rect.collidepoint(mx, my) and is_unlocked
        
        bg_c = (30, 58, 138) if is_selected else ((40, 50, 70) if hov else (20, 30, 45))
        pygame.draw.rect(canvas, bg_c, s_rect, border_radius=6)
        if is_selected:
            pygame.draw.rect(canvas, COLOR_CYAN, s_rect, 2, border_radius=6)
            
        t_col = COLOR_WHITE if is_unlocked else (75, 85, 99)
        t_mark = "> " if is_selected else "  "
        s_text = font_card.render(f"{t_mark}SECTOR {s_id}: {sec['name']}", True, t_col)
        canvas.blit(s_text, (55, sy + 15))
        
        if is_completed:
            lk = font_card.render("[COMPLETED]", True, COLOR_EMERALD)
            canvas.blit(lk, (s_rect.right - lk.get_width() - 10, sy + 15))
        elif is_unlocked:
            lk = font_card.render("[AVAILABLE]", True, COLOR_CYAN)
            canvas.blit(lk, (s_rect.right - lk.get_width() - 10, sy + 15))
        else:
            lk = font_card.render("[LOCKED]", True, (150, 50, 50))
            canvas.blit(lk, (s_rect.right - lk.get_width() - 10, sy + 15))
            
        if is_unlocked:
            interactive_rects["sectors"][s_id] = s_rect
            
        sy += 60
        
    # Missions List (Right side)
    right_pane = pygame.Rect(400, 90, vw - 430, vh - 110)
    pygame.draw.rect(canvas, (15, 20, 30), right_pane, border_radius=8)
    pygame.draw.rect(canvas, (35, 45, 60), right_pane, 2, border_radius=8)
    
    sel_sec_data = next((s for s in SECTORS_PHASE5 if s["id"] == current_selected_sector), SECTORS_PHASE5[0])
    m_lbl = font_banner.render(f"SECTOR {current_selected_sector} MISSIONS", True, COLOR_CYAN)
    m_theme = font_card.render(sel_sec_data["theme"], True, COLOR_TEXT_DIM)
    canvas.blit(m_lbl, (420, 105))
    canvas.blit(m_theme, (420, 135))
    
    missions = get_missions_for_sector(current_selected_sector)
    my_y = 170
    
    for m in missions:
        m_id = m["id"]
        is_unlocked = m_id in ctx.missions["unlocked"]
        is_completed = m_id in ctx.missions["completed"]
        
        m_rect = pygame.Rect(420, my_y, vw - 470, 70)
        hov = m_rect.collidepoint(mx, my) and is_unlocked
        
        bg_c = (30, 45, 65) if hov else (20, 25, 40)
        pygame.draw.rect(canvas, bg_c, m_rect, border_radius=6)
        
        if is_completed:
            pygame.draw.rect(canvas, COLOR_EMERALD, m_rect, 1, border_radius=6)
        elif is_unlocked:
            pygame.draw.rect(canvas, COLOR_CYAN, m_rect, 1, border_radius=6)
            
        t_col = COLOR_WHITE if is_unlocked else (75, 85, 99)
        m_num = f"[{m['mission_number']:02d}] "
        m_name_surf = font_banner.render(f"{m_num}{m['name']}", True, t_col)
        canvas.blit(m_name_surf, (440, my_y + 15))
        
        if is_completed:
            st = font_card.render("[COMPLETED]", True, COLOR_EMERALD)
            canvas.blit(st, (m_rect.right - st.get_width() - 20, my_y + 25))
        elif is_unlocked:
            st = font_card.render("[AVAILABLE]", True, COLOR_CYAN)
            canvas.blit(st, (m_rect.right - st.get_width() - 20, my_y + 25))
            interactive_rects["missions"][m_id] = m_rect
        else:
            st = font_card.render("[LOCKED]", True, (150, 50, 50))
            canvas.blit(st, (m_rect.right - st.get_width() - 20, my_y + 25))
            
        my_y += 85

    return interactive_rects

def draw_mission_briefing(canvas: pygame.Surface, mission_data: dict, scrap: int) -> dict:
    canvas.fill(COLOR_BG)
    vw, vh = canvas.get_size()
    mx, my = pygame.mouse.get_pos()

    box_w, box_h = 600, 400
    box_rect = pygame.Rect(vw // 2 - box_w // 2, vh // 2 - box_h // 2, box_w, box_h)
    pygame.draw.rect(canvas, (15, 23, 42), box_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_CYAN, box_rect, 2, border_radius=10)

    t_hdr = font_title.render("MISSION BRIEFING", True, COLOR_CYAN)
    canvas.blit(t_hdr, t_hdr.get_rect(center=(vw // 2, box_rect.top + 30)))
    
    s_text = font_banner.render(f"SECTOR {mission_data['sector_id']}", True, COLOR_GOLD)
    m_text = font_banner.render(f"MISSION {mission_data['mission_number']}: {mission_data['name']}", True, COLOR_WHITE)
    canvas.blit(s_text, s_text.get_rect(center=(vw // 2, box_rect.top + 80)))
    canvas.blit(m_text, m_text.get_rect(center=(vw // 2, box_rect.top + 115)))
    
    diff_val = mission_data.get("difficulty", 1)
    diff_stars = "* " * diff_val
    d_text = font_card.render(f"DIFFICULTY: {diff_stars.strip()}", True, COLOR_CRIMSON)
    canvas.blit(d_text, d_text.get_rect(center=(vw // 2, box_rect.top + 160)))
    
    obj_str = mission_data["objective"].replace("_", " ").upper()
    if obj_str == "SURVIVE": obj_str += f" FOR {mission_data.get('duration', 60)} SECONDS"
    o_text = font_card.render(f"OBJECTIVE: {obj_str}", True, COLOR_WHITE)
    canvas.blit(o_text, o_text.get_rect(center=(vw // 2, box_rect.top + 200)))
    
    from src.data.mission_data import MISSION_REWARDS
    rew = MISSION_REWARDS.get(mission_data.get("difficulty", 1), 150)
    r_text = font_card.render(f"REWARD: {rew} SCRAP", True, COLOR_GOLD)
    canvas.blit(r_text, r_text.get_rect(center=(vw // 2, box_rect.top + 240)))

    btn_rect = pygame.Rect(vw // 2 - 100, box_rect.bottom - 60, 200, 40)
    hov = btn_rect.collidepoint(mx, my)
    pygame.draw.rect(canvas, (30, 41, 59) if not hov else (51, 65, 85), btn_rect, border_radius=6)
    pygame.draw.rect(canvas, COLOR_EMERALD if hov else (71, 85, 105), btn_rect, 2, border_radius=6)
    
    start_lbl = font_card.render("[SPACE] START", True, COLOR_EMERALD)
    canvas.blit(start_lbl, start_lbl.get_rect(center=btn_rect.center))
    
    exit_btn = draw_exit_button(canvas)
    
    return {"start": btn_rect, "exit": exit_btn}

def draw_mission_complete(canvas: pygame.Surface, mission_data: dict, was_first_clear: bool, is_sector_clear: bool):
    vw, vh = canvas.get_size()
    overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
    overlay.fill((5, 15, 10, 220) if was_first_clear else (10, 10, 15, 220))
    canvas.blit(overlay, (0, 0))

    t_clear = font_title.render("SECTOR COMPLETE" if is_sector_clear else "MISSION COMPLETE", True, COLOR_EMERALD)
    canvas.blit(t_clear, t_clear.get_rect(center=(vw // 2, vh // 2 - 80)))
    
    if was_first_clear:
        from src.data.mission_data import MISSION_REWARDS, SECTOR_BONUS
        diff = mission_data.get("difficulty", 1)
        rew = MISSION_REWARDS.get(diff, 150)
        txt = f"Mission Reward: +{rew} Scrap"
        if is_sector_clear:
            txt += f"  |  Sector Bonus: +{SECTOR_BONUS.get(mission_data['sector_id'], 0)} Scrap"
            
        t_rew = font_banner.render(txt, True, COLOR_GOLD)
        canvas.blit(t_rew, t_rew.get_rect(center=(vw // 2, vh // 2 - 20)))
        
        t_nxt = font_banner.render("Next Mission: UNLOCKED", True, COLOR_CYAN)
        canvas.blit(t_nxt, t_nxt.get_rect(center=(vw // 2, vh // 2 + 20)))
    else:
        t_rep = font_banner.render("Replay Complete (Gameplay Only - No Duplicate Reward)", True, COLOR_TEXT_DIM)
        canvas.blit(t_rep, t_rep.get_rect(center=(vw // 2, vh // 2 - 20)))

    t_cont = font_hud.render("PRESS [SPACE / ENTER] TO CONTINUE", True, COLOR_WHITE)
    canvas.blit(t_cont, t_cont.get_rect(center=(vw // 2, vh // 2 + 80)))

def draw_mission_failed(canvas: pygame.Surface, scrap: int):
    vw, vh = canvas.get_size()
    overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
    overlay.fill((15, 5, 8, 220))
    canvas.blit(overlay, (0, 0))

    t_go = font_gameover.render("MISSION FAILED", True, COLOR_CRIMSON)
    t_re = font_hud.render("PRESS [SPACE] TO RETRY  |  [M] SECTOR MAP  |  [Q] QUIT", True, COLOR_GOLD)

    canvas.blit(t_go, t_go.get_rect(center=(vw // 2, vh // 2 - 40)))
    canvas.blit(t_re, t_re.get_rect(center=(vw // 2, vh // 2 + 40)))

def draw_pause_settings_ui(canvas: pygame.Surface, difficulty_mode: int, show_crt: bool, sound_enabled: bool) -> dict:
    vw, vh = canvas.get_size()
    pause_overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
    pause_overlay.fill((5, 8, 15, 210))
    canvas.blit(pause_overlay, (0, 0))

    box_w, box_h = 440, 360
    box_rect = pygame.Rect(vw // 2 - box_w // 2, vh // 2 - box_h // 2, box_w, box_h)
    pygame.draw.rect(canvas, (15, 23, 42), box_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_CYAN, box_rect, 2, border_radius=10)

    t_pause = font_title.render("SYSTEM PAUSED", True, COLOR_CYAN)
    canvas.blit(t_pause, t_pause.get_rect(center=(vw // 2, box_rect.top + 38)))

    btn_w, btn_h = 320, 36
    bx = vw // 2 - btn_w // 2
    by = box_rect.top + 80
    
    r_resume = pygame.Rect(bx, by, btn_w, btn_h)
    r_diff = pygame.Rect(bx, by + 46, btn_w, btn_h)
    r_crt = pygame.Rect(bx, by + 92, btn_w, btn_h)
    r_sfx = pygame.Rect(bx, by + 138, btn_w, btn_h)
    r_hangar = pygame.Rect(bx, by + 184, btn_w, btn_h)
    r_map = pygame.Rect(bx, by + 230, btn_w, btn_h)

    def _draw_btn(r: pygame.Rect, txt: str, col=COLOR_WHITE):
        mx, my = pygame.mouse.get_pos()
        hov = r.collidepoint(mx, my)
        pygame.draw.rect(canvas, (30, 41, 59) if not hov else (51, 65, 85), r, border_radius=6)
        pygame.draw.rect(canvas, COLOR_CYAN if hov else (71, 85, 105), r, 1, border_radius=6)
        lbl = font_card.render(txt, True, col)
        canvas.blit(lbl, lbl.get_rect(center=r.center))

    _draw_btn(r_resume, "RESUME COMBAT [ESC/P]", COLOR_EMERALD)
    _draw_btn(r_diff, f"DIFFICULTY: {DIFFICULTY_NAMES[difficulty_mode]}", COLOR_GOLD)
    _draw_btn(r_crt, f"CRT SCANLINES: {'ON' if show_crt else 'OFF'}", COLOR_CYAN)
    _draw_btn(r_sfx, f"AUDIO SFX: {'ENABLED' if sound_enabled else 'MUTED'}", COLOR_CYAN)
    _draw_btn(r_hangar, "HANGAR ARMORY [H]", COLOR_GOLD)
    _draw_btn(r_map, "SECTOR MAP [M]", COLOR_CYAN)

    draw_exit_button(canvas)

    return {
        "resume": r_resume,
        "diff": r_diff,
        "crt": r_crt,
        "sfx": r_sfx,
        "hangar": r_hangar,
        "map": r_map,
        "exit": pygame.Rect(vw - 140, vh - 55, 120, 38)
    }

# Keep these empty or refactor legacy tests out if they call them
def draw_sector_select_ui(*args, **kwargs): return {}, pygame.Rect(0,0,0,0), []
def draw_level_clear_ui(*args, **kwargs): pass
def draw_game_over_ui(*args, **kwargs): pass
def draw_campaign_victory_ui(*args, **kwargs): pass
