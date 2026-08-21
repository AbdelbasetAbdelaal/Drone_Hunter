import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON,
    COLOR_EMERALD, COLOR_WHITE, COLOR_BG, COLOR_HUD
)
from src.data.game_data import (
    DIFFICULTY_MODIFIERS, DIFFICULTY_NAMES, SECTORS
)
from src.ui.font_manager import (
    font_title, font_header, font_banner, font_card, font_hud,
    font_gameover, font_button, font_sub
)
from src.data.mission_data import SECTORS_PHASE5, get_missions_for_sector

COLOR_TEXT_DIM = (120, 140, 160)


def draw_button(canvas: pygame.Surface, rect: pygame.Rect, text: str,
                mouse_pos: tuple[int, int], base_color=COLOR_CYAN,
                bg_color=(20, 30, 48), hover_bg=(30, 50, 80),
                text_color=COLOR_WHITE, font=font_button) -> bool:
    """Helper to draw a styled cyberpunk button and return whether it is hovered."""
    is_hover = rect.collidepoint(mouse_pos)
    draw_bg = hover_bg if is_hover else bg_color
    border_col = COLOR_WHITE if is_hover else base_color
    
    pygame.draw.rect(canvas, draw_bg, rect, border_radius=6)
    pygame.draw.rect(canvas, border_col, rect, 2 if is_hover else 1, border_radius=6)
    
    lbl = font.render(text, True, COLOR_WHITE if is_hover else text_color)
    canvas.blit(lbl, lbl.get_rect(center=rect.center))
    return is_hover


def _get_safe_mouse_pos(mouse_pos: tuple[int, int] | None = None) -> tuple[int, int]:
    if mouse_pos is not None:
        return mouse_pos
    try:
        if pygame.display.get_init():
            return pygame.mouse.get_pos()
    except Exception:
        pass
    return (0, 0)


def draw_exit_button(canvas: pygame.Surface, mouse_pos: tuple[int, int] = None, rect: pygame.Rect = None) -> pygame.Rect:
    vw, vh = canvas.get_size()
    btn_rect = rect if rect is not None else pygame.Rect(vw - 150, vh - 55, 120, 38)
    mx, my = _get_safe_mouse_pos(mouse_pos)
    
    draw_button(
        canvas, btn_rect, "[Q] QUIT", (mx, my),
        base_color=COLOR_CRIMSON, bg_color=(35, 15, 20),
        hover_bg=(60, 20, 30), text_color=COLOR_CRIMSON
    )
    return btn_rect


def draw_main_menu(canvas: pygame.Surface, mouse_pos: tuple[int, int] = None) -> dict[str, pygame.Rect]:
    canvas.fill((6, 10, 18))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    # Title & Subtitle
    title = font_title.render("DRONE HUNTER 2D", True, COLOR_CYAN)
    canvas.blit(title, title.get_rect(center=(vw // 2, vh // 2 - 120)))

    
    edition = font_card.render("PC EDITION  |  v1.0.0", True, COLOR_TEXT_DIM)
    canvas.blit(edition, edition.get_rect(center=(vw // 2, vh // 2 - 78)))

    sub = font_banner.render("TACTICAL TOP-DOWN SCI-FI COMBAT", True, COLOR_EMERALD)
    canvas.blit(sub, sub.get_rect(center=(vw // 2, vh // 2 - 35)))

    # Menu Buttons
    btn_w, btn_h = 240, 42
    bx = vw // 2 - btn_w // 2
    by = vh // 2 + 20

    r_play = pygame.Rect(bx, by, btn_w, btn_h)
    r_hangar = pygame.Rect(bx, by + 52, btn_w, btn_h)
    r_settings = pygame.Rect(bx, by + 104, btn_w, btn_h)
    r_exit = pygame.Rect(bx, by + 156, btn_w, btn_h)

    draw_button(canvas, r_play, "[SPACE] DEPLOY COMBAT", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)
    draw_button(canvas, r_hangar, "[H] HANGAR ARMORY", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD)
    draw_button(canvas, r_settings, "[S] SYSTEM SETTINGS", (mx, my), base_color=COLOR_CYAN, text_color=COLOR_CYAN)
    draw_button(canvas, r_exit, "[Q] QUIT GAME", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON)

    return {
        'play': r_play,
        'hangar': r_hangar,
        'settings': r_settings,
        'exit': r_exit
    }


def draw_mission_select_ui(canvas: pygame.Surface, ctx, scrap: int, mouse_pos: tuple[int, int] = None) -> dict:
    """Renders the overhauled, clean Phase 5 Sector and Mission selection UI."""
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)
    
    # -------------------------------------------------------------------------
    # 1. Top Header Bar
    # -------------------------------------------------------------------------
    header_rect = pygame.Rect(30, 14, vw - 60, 52)
    pygame.draw.rect(canvas, (14, 22, 38), header_rect, border_radius=8)
    pygame.draw.rect(canvas, COLOR_CYAN, header_rect, 2, border_radius=8)
    
    t_hdr = font_header.render("COMBAT SECTOR MAP", True, COLOR_CYAN)
    canvas.blit(t_hdr, (48, 18))
    
    coin_hdr = font_banner.render(f"SCRAP: {scrap:,}", True, COLOR_GOLD)
    canvas.blit(coin_hdr, (vw - 250, 26))

    # Difficulty Quick-Toggle Button
    diff_name = DIFFICULTY_NAMES[ctx.difficulty_mode]
    diff_col = DIFFICULTY_MODIFIERS[ctx.difficulty_mode]["badge_color"]
    diff_rect = pygame.Rect(vw - 490, 22, 210, 36)
    draw_button(canvas, diff_rect, f"DIFF: {diff_name}", (mx, my), base_color=diff_col, text_color=diff_col)

    interactive_rects = {
        "diff_rect": diff_rect,
        "sectors": {},
        "missions": {},
        "back": None,
        "hangar": None,
        "settings": None,
        "exit": None
    }
    
    # -------------------------------------------------------------------------
    # 2. Sectors List (Left side) — Fully legible 2-line layout (0% Truncation)
    # -------------------------------------------------------------------------
    left_w = 380
    left_pane = pygame.Rect(30, 78, left_w, vh - 150)
    pygame.draw.rect(canvas, (12, 18, 30), left_pane, border_radius=8)
    pygame.draw.rect(canvas, (30, 42, 62), left_pane, 2, border_radius=8)
    
    s_lbl = font_banner.render("CAMPAIGN SECTORS", True, COLOR_WHITE)
    canvas.blit(s_lbl, (48, 90))
    
    current_selected_sector = ctx.missions.get("current_sector", 1)
    
    sy = 126
    card_h = 66
    for sec in SECTORS_PHASE5:
        s_id = sec["id"]
        is_unlocked = s_id in ctx.sector_progress["unlocked"]
        is_completed = s_id in ctx.sector_progress["completed"]
        is_selected = (s_id == current_selected_sector)
        
        s_rect = pygame.Rect(44, sy, left_w - 28, card_h)
        hov = s_rect.collidepoint(mx, my) and is_unlocked
        
        # Background & border styling
        if is_selected:
            bg_c = (24, 48, 90)
            border_c = COLOR_CYAN
            border_w = 2
        elif hov:
            bg_c = (22, 36, 60)
            border_c = COLOR_WHITE
            border_w = 2
        else:
            bg_c = (15, 23, 38) if is_unlocked else (12, 16, 24)
            border_c = (40, 55, 80) if is_unlocked else (25, 32, 45)
            border_w = 1

        pygame.draw.rect(canvas, bg_c, s_rect, border_radius=6)
        pygame.draw.rect(canvas, border_c, s_rect, border_w, border_radius=6)
        
        # Line 1: Sector Number & Full Name
        t_col = COLOR_WHITE if is_unlocked else (80, 95, 115)
        prefix = "> " if is_selected else "  "
        title_text = f"{prefix}SECTOR {s_id}: {sec['name'].upper()}"
        s_title_surf = font_button.render(title_text, True, COLOR_CYAN if is_selected else t_col)
        canvas.blit(s_title_surf, (54, sy + 10))
        
        # Line 2: Status Badge
        if is_completed:
            status_text = "[COMPLETED]"
            status_col = COLOR_EMERALD
        elif is_unlocked:
            status_text = "[AVAILABLE]"
            status_col = COLOR_CYAN
        else:
            status_text = "[LOCKED]"
            status_col = (180, 60, 60)
            
        badge_surf = font_sub.render(status_text, True, status_col)
        canvas.blit(badge_surf, (68, sy + 36))
            
        if is_unlocked:
            interactive_rects["sectors"][s_id] = s_rect
            
        sy += card_h + 8
        
    # -------------------------------------------------------------------------
    # 3. Missions List (Right side)
    # -------------------------------------------------------------------------
    right_x = left_pane.right + 20
    right_w = vw - right_x - 30
    right_pane = pygame.Rect(right_x, 78, right_w, vh - 150)
    pygame.draw.rect(canvas, (12, 18, 30), right_pane, border_radius=8)
    pygame.draw.rect(canvas, (30, 42, 62), right_pane, 2, border_radius=8)
    
    sel_sec_data = next((s for s in SECTORS_PHASE5 if s["id"] == current_selected_sector), SECTORS_PHASE5[0])
    m_lbl = font_banner.render(f"SECTOR {current_selected_sector}: {sel_sec_data['name'].upper()}", True, COLOR_CYAN)
    m_theme = font_sub.render(sel_sec_data["theme"], True, COLOR_TEXT_DIM)
    canvas.blit(m_lbl, (right_x + 20, 90))
    canvas.blit(m_theme, (right_x + 20, 116))
    
    missions = get_missions_for_sector(current_selected_sector)
    my_y = 142
    m_card_h = 62
    
    for m in missions:
        m_id = m["id"]
        is_unlocked = m_id in ctx.missions["unlocked"]
        is_completed = m_id in ctx.missions["completed"]
        
        m_rect = pygame.Rect(right_x + 20, my_y, right_w - 40, m_card_h)
        hov = m_rect.collidepoint(mx, my) and is_unlocked
        
        if is_completed:
            bg_c = (18, 38, 30) if hov else (12, 26, 20)
            border_c = COLOR_EMERALD
        elif is_unlocked:
            bg_c = (22, 38, 62) if hov else (15, 24, 42)
            border_c = COLOR_CYAN if hov else (45, 65, 95)
        else:
            bg_c = (12, 16, 24)
            border_c = (30, 36, 48)

        pygame.draw.rect(canvas, bg_c, m_rect, border_radius=6)
        pygame.draw.rect(canvas, border_c, m_rect, 2 if hov else 1, border_radius=6)
        
        # Mission Name & Number
        t_col = COLOR_WHITE if is_unlocked else (80, 95, 115)
        m_num = f"[{m['mission_number']:02d}] "
        m_name_surf = font_button.render(f"{m_num}{m['name']}", True, t_col)
        canvas.blit(m_name_surf, (m_rect.left + 16, my_y + 10))

        # Objective & Diff summary on line 2
        obj_txt = m['objective'].replace('_', ' ').title()
        info_surf = font_sub.render(f"Type: {obj_txt}  |  Diff: {m.get('difficulty', 1)}/5", True, COLOR_TEXT_DIM if is_unlocked else (60, 75, 90))
        canvas.blit(info_surf, (m_rect.left + 16, my_y + 34))
        
        # Status Label on Right
        if is_completed:
            st = font_button.render("[COMPLETED]", True, COLOR_EMERALD)
        elif is_unlocked:
            st = font_button.render("[AVAILABLE]", True, COLOR_CYAN)
            interactive_rects["missions"][m_id] = m_rect
        else:
            st = font_button.render("[LOCKED]", True, (160, 50, 50))
            
        canvas.blit(st, (m_rect.right - st.get_width() - 16, my_y + 20))
        my_y += m_card_h + 8

    # -------------------------------------------------------------------------
    # 4. Bottom Universal Navigation Bar (Never truncated, guaranteed visible)
    # -------------------------------------------------------------------------
    nav_y = vh - 58
    r_back = pygame.Rect(30, nav_y, 160, 42)
    r_hangar = pygame.Rect(205, nav_y, 165, 42)
    r_settings = pygame.Rect(385, nav_y, 150, 42)
    r_exit = pygame.Rect(vw - 160, nav_y, 130, 42)

    draw_button(canvas, r_back, "[ESC] MAIN MENU", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_hangar, "[H] HANGAR ARMORY", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD)
    draw_button(canvas, r_settings, "[S] SETTINGS", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_exit, "[Q] QUIT", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON)

    interactive_rects["back"] = r_back
    interactive_rects["hangar"] = r_hangar
    interactive_rects["settings"] = r_settings
    interactive_rects["exit"] = r_exit

    return interactive_rects


def draw_mission_briefing(canvas: pygame.Surface, mission_data: dict, scrap: int, mouse_pos: tuple[int, int] = None) -> dict:
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    box_w, box_h = 640, 420
    box_rect = pygame.Rect(vw // 2 - box_w // 2, vh // 2 - box_h // 2, box_w, box_h)
    pygame.draw.rect(canvas, (14, 22, 38), box_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_CYAN, box_rect, 2, border_radius=10)

    t_hdr = font_header.render("MISSION BRIEFING", True, COLOR_CYAN)
    canvas.blit(t_hdr, t_hdr.get_rect(center=(vw // 2, box_rect.top + 32)))
    
    s_text = font_banner.render(f"SECTOR {mission_data['sector_id']}", True, COLOR_GOLD)
    m_text = font_banner.render(f"MISSION {mission_data['mission_number']}: {mission_data['name']}", True, COLOR_WHITE)
    canvas.blit(s_text, s_text.get_rect(center=(vw // 2, box_rect.top + 80)))
    canvas.blit(m_text, m_text.get_rect(center=(vw // 2, box_rect.top + 115)))
    
    diff_val = mission_data.get("difficulty", 1)
    diff_names = {1: "EASY", 2: "NORMAL", 3: "HARD", 4: "VERY HARD", 5: "EXTREME"}
    diff_label = diff_names.get(diff_val, "NORMAL")
    d_text = font_card.render(f"DIFFICULTY: {diff_label} [{diff_val}/5]", True, COLOR_CRIMSON)
    canvas.blit(d_text, d_text.get_rect(center=(vw // 2, box_rect.top + 160)))
    
    obj_str = mission_data["objective"].replace("_", " ").upper()
    if obj_str == "SURVIVE": obj_str += f" FOR {mission_data.get('duration', 60)} SECONDS"
    o_text = font_card.render(f"OBJECTIVE: {obj_str}", True, COLOR_WHITE)
    canvas.blit(o_text, o_text.get_rect(center=(vw // 2, box_rect.top + 200)))
    
    from src.data.mission_data import MISSION_REWARDS
    rew = MISSION_REWARDS.get(mission_data.get("difficulty", 1), 150)
    r_text = font_card.render(f"REWARD: {rew} SCRAP", True, COLOR_GOLD)
    canvas.blit(r_text, r_text.get_rect(center=(vw // 2, box_rect.top + 240)))

    # Briefing Buttons
    r_back = pygame.Rect(box_rect.left + 30, box_rect.bottom - 60, 160, 42)
    r_start = pygame.Rect(box_rect.centerx - 90, box_rect.bottom - 60, 180, 42)
    r_exit = pygame.Rect(box_rect.right - 150, box_rect.bottom - 60, 120, 42)

    draw_button(canvas, r_back, "[ESC] BACK", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_start, "[SPACE] DEPLOY", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)
    draw_button(canvas, r_exit, "[Q] QUIT", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON)
    
    return {"back": r_back, "start": r_start, "exit": r_exit}


def draw_settings_menu_ui(canvas: pygame.Surface, difficulty_mode: int, show_crt: bool, sound_enabled: bool, mouse_pos: tuple[int, int] = None) -> dict:
    """Renders the dedicated Fullscreen/Audio/Difficulty settings menu."""
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    panel_w, panel_h = 580, 440
    panel_rect = pygame.Rect(vw // 2 - panel_w // 2, vh // 2 - panel_h // 2, panel_w, panel_h)
    pygame.draw.rect(canvas, (14, 22, 38), panel_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_CYAN, panel_rect, 2, border_radius=10)

    t_hdr = font_header.render("SYSTEM & AUDIO SETTINGS", True, COLOR_CYAN)
    canvas.blit(t_hdr, t_hdr.get_rect(center=(vw // 2, panel_rect.top + 36)))

    btn_w, btn_h = 440, 44
    bx = vw // 2 - btn_w // 2
    by = panel_rect.top + 90

    r_full = pygame.Rect(bx, by, btn_w, btn_h)
    r_crt = pygame.Rect(bx, by + 56, btn_w, btn_h)
    r_sfx = pygame.Rect(bx, by + 112, btn_w, btn_h)
    r_diff = pygame.Rect(bx, by + 168, btn_w, btn_h)
    r_reset = pygame.Rect(bx, by + 224, btn_w, btn_h)
    r_back = pygame.Rect(bx, panel_rect.bottom - 60, btn_w, 42)

    diff_name = DIFFICULTY_NAMES[difficulty_mode]
    diff_col = DIFFICULTY_MODIFIERS[difficulty_mode]["badge_color"]

    draw_button(canvas, r_full, "DISPLAY: FULLSCREEN TOGGLE [F11]", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_crt, f"CRT SCANLINES: {'ENABLED' if show_crt else 'DISABLED'} [F2]", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_sfx, f"AUDIO SFX: {'ENABLED' if sound_enabled else 'MUTED'}", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD)
    draw_button(canvas, r_diff, f"COMBAT DIFFICULTY: {diff_name}", (mx, my), base_color=diff_col, text_color=diff_col)
    draw_button(canvas, r_reset, "RESET PROGRESS & SAVE DATA", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON)
    draw_button(canvas, r_back, "[ESC] BACK TO PREVIOUS SCREEN", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)

    return {
        "fullscreen": r_full,
        "crt": r_crt,
        "sfx": r_sfx,
        "diff": r_diff,
        "reset": r_reset,
        "back": r_back
    }


def draw_mission_complete(canvas: pygame.Surface, mission_data: dict, was_first_clear: bool, is_sector_clear: bool, mouse_pos: tuple[int, int] = None) -> dict:
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)
    
    overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
    overlay.fill((5, 15, 10, 220) if was_first_clear else (10, 10, 15, 220))
    canvas.blit(overlay, (0, 0))

    t_clear = font_title.render("SECTOR COMPLETE" if is_sector_clear else "MISSION COMPLETE", True, COLOR_EMERALD)
    canvas.blit(t_clear, t_clear.get_rect(center=(vw // 2, vh // 2 - 100)))
    
    if was_first_clear:
        from src.data.mission_data import MISSION_REWARDS, SECTOR_BONUS
        diff = mission_data.get("difficulty", 1)
        rew = MISSION_REWARDS.get(diff, 150)
        txt = f"Mission Reward: +{rew} Scrap"
        if is_sector_clear:
            txt += f"  |  Sector Bonus: +{SECTOR_BONUS.get(mission_data['sector_id'], 0)} Scrap"
            
        t_rew = font_banner.render(txt, True, COLOR_GOLD)
        canvas.blit(t_rew, t_rew.get_rect(center=(vw // 2, vh // 2 - 40)))
        
        t_nxt = font_banner.render("Next Mission: UNLOCKED", True, COLOR_CYAN)
        canvas.blit(t_nxt, t_nxt.get_rect(center=(vw // 2, vh // 2)))
    else:
        t_rep = font_banner.render("Replay Complete (Gameplay Only - No Duplicate Reward)", True, COLOR_TEXT_DIM)
        canvas.blit(t_rep, t_rep.get_rect(center=(vw // 2, vh // 2 - 40)))

    btn_w, btn_h = 240, 44
    bx = vw // 2 - btn_w // 2
    by = vh // 2 + 50

    r_next = pygame.Rect(bx, by, btn_w, btn_h)
    r_hangar = pygame.Rect(bx, by + 54, btn_w, btn_h)

    draw_button(canvas, r_next, "[SPACE] SECTOR MAP", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)
    draw_button(canvas, r_hangar, "[H] HANGAR ARMORY", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD)

    return {"next": r_next, "hangar": r_hangar}


def draw_mission_failed(canvas: pygame.Surface, scrap: int, mouse_pos: tuple[int, int] = None) -> dict:
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)
    
    overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
    overlay.fill((15, 5, 8, 225))
    canvas.blit(overlay, (0, 0))

    t_go = font_gameover.render("MISSION FAILED", True, COLOR_CRIMSON)
    canvas.blit(t_go, t_go.get_rect(center=(vw // 2, vh // 2 - 90)))

    t_hint = font_banner.render("TACTICAL DRONE DESTROYED IN COMBAT", True, (160, 175, 195))
    canvas.blit(t_hint, t_hint.get_rect(center=(vw // 2, vh // 2 - 35)))

    btn_w, btn_h = 240, 44
    bx = vw // 2 - btn_w // 2
    by = vh // 2 + 25

    r_retry = pygame.Rect(bx, by, btn_w, btn_h)
    r_map = pygame.Rect(bx, by + 54, btn_w, btn_h)
    r_exit = pygame.Rect(bx, by + 108, btn_w, btn_h)

    draw_button(canvas, r_retry, "[SPACE] RETRY MISSION", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)
    draw_button(canvas, r_map, "[M] SECTOR MAP", (mx, my), base_color=COLOR_CYAN, text_color=COLOR_CYAN)
    draw_button(canvas, r_exit, "[Q] QUIT TO MENU", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON)

    return {"retry": r_retry, "map": r_map, "exit": r_exit}


def draw_pause_settings_ui(canvas: pygame.Surface, difficulty_mode: int, show_crt: bool, sound_enabled: bool, mouse_pos: tuple[int, int] = None) -> dict:
    vw, vh = canvas.get_size()
    pause_overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
    pause_overlay.fill((5, 8, 15, 210))
    canvas.blit(pause_overlay, (0, 0))

    box_w, box_h = 460, 390
    box_rect = pygame.Rect(vw // 2 - box_w // 2, vh // 2 - box_h // 2, box_w, box_h)
    pygame.draw.rect(canvas, (14, 22, 38), box_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_CYAN, box_rect, 2, border_radius=10)

    t_pause = font_header.render("SYSTEM PAUSED", True, COLOR_CYAN)
    canvas.blit(t_pause, t_pause.get_rect(center=(vw // 2, box_rect.top + 34)))

    btn_w, btn_h = 340, 38
    bx = vw // 2 - btn_w // 2
    by = box_rect.top + 76
    
    r_resume = pygame.Rect(bx, by, btn_w, btn_h)
    r_diff = pygame.Rect(bx, by + 46, btn_w, btn_h)
    r_crt = pygame.Rect(bx, by + 92, btn_w, btn_h)
    r_sfx = pygame.Rect(bx, by + 138, btn_w, btn_h)
    r_hangar = pygame.Rect(bx, by + 184, btn_w, btn_h)
    r_map = pygame.Rect(bx, by + 230, btn_w, btn_h)
    r_exit = pygame.Rect(bx, by + 276, btn_w, btn_h)

    mx, my = _get_safe_mouse_pos(mouse_pos)

    draw_button(canvas, r_resume, "RESUME COMBAT [ESC/P]", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)
    draw_button(canvas, r_diff, f"DIFFICULTY: {DIFFICULTY_NAMES[difficulty_mode]}", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD)
    draw_button(canvas, r_crt, f"CRT SCANLINES: {'ON' if show_crt else 'OFF'}", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_sfx, f"AUDIO SFX: {'ENABLED' if sound_enabled else 'MUTED'}", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_hangar, "HANGAR ARMORY [H]", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD)
    draw_button(canvas, r_map, "SECTOR MAP [M]", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_exit, "QUIT TO MENU [Q]", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON)

    return {
        "resume": r_resume,
        "diff": r_diff,
        "crt": r_crt,
        "sfx": r_sfx,
        "hangar": r_hangar,
        "map": r_map,
        "exit": r_exit
    }


def draw_campaign_victory_ui(canvas: pygame.Surface, total_score: int = 0, highscore: int = 0, scrap: int = 0, bosses_count: int = 5, missions_count: int = 25):
    """Renders Phase 6 Campaign Complete end-game screen."""
    vw, vh = canvas.get_size()
    canvas.fill((5, 10, 20))
    
    frame_rect = pygame.Rect(60, 40, vw - 120, vh - 80)
    pygame.draw.rect(canvas, (15, 23, 42), frame_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_GOLD, frame_rect, 2, border_radius=10)
    
    t_title = font_title.render("CAMPAIGN COMPLETE", True, COLOR_GOLD)
    t_sub = font_banner.render("DRONE HUNTER - ALL SECTORS CLEARED", True, COLOR_CYAN)
    canvas.blit(t_title, t_title.get_rect(center=(vw // 2, frame_rect.top + 50)))
    canvas.blit(t_sub, t_sub.get_rect(center=(vw // 2, frame_rect.top + 95)))
    
    sy = frame_rect.top + 160
    stats = [
        ("FINAL SCORE:", f"{total_score:,}", COLOR_WHITE),
        ("SCRAP EARNED:", f"{scrap:,} SCRAP", COLOR_GOLD),
        ("BOSSES DEFEATED:", f"{bosses_count} / 5 MAJOR COMMAND UNITS", COLOR_CRIMSON),
        ("MISSIONS COMPLETED:", f"{missions_count} / 25 SECTOR MISSIONS", COLOR_EMERALD),
    ]
    for label, val, col in stats:
        t_lbl = font_banner.render(label, True, (148, 163, 184))
        t_val = font_banner.render(val, True, col)
        canvas.blit(t_lbl, (vw // 2 - 240, sy))
        canvas.blit(t_val, (vw // 2 + 30, sy))
        sy += 45
        
    t_nav = font_hud.render("PRESS [SPACE / ENTER] TO RETURN TO SECTOR MAP  |  [H] HANGAR  |  [Q] QUIT", True, COLOR_WHITE)
    canvas.blit(t_nav, t_nav.get_rect(center=(vw // 2, frame_rect.bottom - 45)))


def draw_sector_select_ui(*args, **kwargs): return {}, pygame.Rect(0,0,0,0), []
def draw_level_clear_ui(*args, **kwargs): pass
def draw_game_over_ui(*args, **kwargs): pass
