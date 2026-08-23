import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON,
    COLOR_EMERALD, COLOR_WHITE, COLOR_BG, COLOR_HUD
)
from src.data.game_data import (
    DIFFICULTY_MODIFIERS, DIFFICULTY_NAMES, SECTORS, DIFFICULTY_CUSTOM,
    CUSTOM_DIFFICULTY_DEFAULTS, get_custom_difficulty
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

    box_w, box_h = 640, 460
    box_rect = pygame.Rect(vw // 2 - box_w // 2, vh // 2 - box_h // 2, box_w, box_h)
    pygame.draw.rect(canvas, (14, 22, 38), box_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_CYAN, box_rect, 2, border_radius=10)

    t_hdr = font_header.render("MISSION BRIEFING", True, COLOR_CYAN)
    canvas.blit(t_hdr, t_hdr.get_rect(center=(vw // 2, box_rect.top + 28)))

    s_text = font_banner.render(f"SECTOR {mission_data['sector_id']}", True, COLOR_GOLD)
    m_text = font_banner.render(f"MISSION {mission_data['mission_number']}: {mission_data['name']}", True, COLOR_WHITE)
    canvas.blit(s_text, s_text.get_rect(center=(vw // 2, box_rect.top + 72)))
    canvas.blit(m_text, m_text.get_rect(center=(vw // 2, box_rect.top + 108)))

    diff_val = mission_data.get("difficulty", 1)
    diff_names = {1: "EASY", 2: "NORMAL", 3: "HARD", 4: "VERY HARD", 5: "EXTREME"}
    diff_label = diff_names.get(diff_val, "NORMAL")
    d_text = font_card.render(f"DIFFICULTY: {diff_label} [{diff_val}/5]", True, COLOR_CRIMSON)
    canvas.blit(d_text, d_text.get_rect(center=(vw // 2, box_rect.top + 150)))

    obj_str = mission_data["objective"].replace("_", " ").upper()
    if obj_str == "SURVIVE": obj_str += f" FOR {mission_data.get('duration', 60)} SECONDS"
    o_text = font_card.render(f"OBJECTIVE: {obj_str}", True, COLOR_WHITE)
    canvas.blit(o_text, o_text.get_rect(center=(vw // 2, box_rect.top + 188)))

    from src.data.mission_data import MISSION_REWARDS
    rew = MISSION_REWARDS.get(mission_data.get("difficulty", 1), 150)
    r_text = font_card.render(f"REWARD: {rew} SCRAP", True, COLOR_GOLD)
    canvas.blit(r_text, r_text.get_rect(center=(vw // 2, box_rect.top + 224)))

    lore_text = mission_data.get("lore", "")
    if lore_text:
        lore_y = box_rect.top + 264
        l_label = font_card.render("INTEL BRIEF:", True, COLOR_CYAN)
        canvas.blit(l_label, (box_rect.left + 36, lore_y))

        words = lore_text.split()
        lines = []
        current_line = []
        max_chars = 85
        for word in words:
            test = " ".join(current_line + [word])
            if len(test) <= max_chars:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        if current_line:
            lines.append(" ".join(current_line))

        line_y = lore_y + 22
        for line in lines:
            l_surf = font_sub.render(line, True, COLOR_TEXT_DIM)
            canvas.blit(l_surf, (box_rect.left + 36, line_y))
            line_y += 18

    side_objs = mission_data.get("side_objectives", [])
    if side_objs:
        so_start_y = box_rect.top + (264 + (len(lore_text.split()) // 85 + 1) * 20 + 20) if lore_text else box_rect + 300
        so_label = font_card.render("SIDE OBJECTIVES:", True, COLOR_EMERALD)
        canvas.blit(so_label, (box_rect.left + 36, so_start_y))

        so_y = so_start_y + 24
        from src.systems.mission_system import SIDE_OBJ_TYPE_NAMES
        for so in side_objs:
            so_type = so.get("type", "")
            so_value = so.get("value", 0)
            type_name = SIDE_OBJ_TYPE_NAMES.get(so_type, so_type.upper())
            if so_type == "collect_data_cores":
                so_desc = f"  [ ] Collect {so_value} Data Cores  (+{50} SCRAP)"
            elif so_type == "no_damage_taken":
                so_desc = f"  [ ] Take No Damage  (+{100} SCRAP)"
            elif so_type == "time_limit":
                so_desc = f"  [ ] Complete within {so_value}s  (+{75} SCRAP)"
            elif so_type == "precision_strikes":
                so_desc = f"  [ ] {so_value} Precision Strikes  (+{60} SCRAP)"
            else:
                so_desc = f"  [ ] {type_name}"
            so_surf = font_sub.render(so_desc, True, COLOR_TEXT_DIM)
            canvas.blit(so_surf, (box_rect.left + 36, so_y))
            so_y += 20

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


def draw_campaign_victory_ui(canvas: pygame.Surface, total_score: int = 0, highscore: int = 0, scrap: int = 0, bosses_count: int = 5, missions_count: int = 25, ng_plus_count: int = 0):
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

    if ng_plus_count > 0:
        ng_txt = font_banner.render(f"NEW GAME+ CYCLE: {ng_plus_count}", True, COLOR_EMERALD)
        canvas.blit(ng_txt, ng_txt.get_rect(center=(vw // 2, frame_rect.top + 140)))
        
    t_nav = font_hud.render("PRESS [SPACE / ENTER] TO RETURN TO SECTOR MAP  |  [H] HANGAR  |  [Q] QUIT", True, COLOR_WHITE)
    canvas.blit(t_nav, t_nav.get_rect(center=(vw // 2, frame_rect.bottom - 45)))

    ng_rect = None
    if ng_plus_count >= 0:
        btn_w, btn_h = 280, 44
        ng_rect = pygame.Rect(vw // 2 - btn_w // 2, frame_rect.bottom - 95, btn_w, btn_h)
        m_pos = pygame.mouse.get_pos() if pygame.display.get_init() else (0, 0)
        draw_button(canvas, ng_rect, f"[N] NEW GAME+  (CYCLE {ng_plus_count + 1})", m_pos,
                    base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)

    return {"new_game_plus": ng_rect}


def draw_sector_select_ui(*args, **kwargs): return {}, pygame.Rect(0,0,0,0), []

def draw_level_clear_ui(canvas: pygame.Surface, sector_idx: int = 0, sub_level: int = 1, score: int = 0, scrap: int = 0, mouse_pos: tuple[int, int] = None) -> dict:
    """Renders sleek, sci-fi stage clear completion screen with stats and interactive buttons."""
    vw, vh = canvas.get_size()
    m_pos = mouse_pos or (0, 0)
    buttons = {}

    dim_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
    dim_surf.fill((10, 15, 26, 210))
    canvas.blit(dim_surf, (0, 0))

    frame_w = 640
    frame_h = 420
    frame_rect = pygame.Rect((vw - frame_w) // 2, (vh - frame_h) // 2, frame_w, frame_h)

    pygame.draw.rect(canvas, (15, 23, 42), frame_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_EMERALD, frame_rect, 2, border_radius=10)

    t_title = font_title.render("STAGE CLEARED", True, COLOR_EMERALD)
    t_sub = font_banner.render(f"SECTOR {sector_idx + 1}  •  STAGE {sub_level} COMPLETE", True, COLOR_CYAN)
    canvas.blit(t_title, t_title.get_rect(center=(vw // 2, frame_rect.top + 45)))
    canvas.blit(t_sub, t_sub.get_rect(center=(vw // 2, frame_rect.top + 90)))

    sy = frame_rect.top + 145
    stats = [
        ("STAGE SCORE:", f"{score:,} PTS", COLOR_GOLD),
        ("SCRAP SALVAGED:", f"+{scrap:,} SCRAP", COLOR_EMERALD),
        ("SECTOR STATUS:", "AIRSPACE SECURED", COLOR_WHITE),
        ("COMBAT RATING:", "S-RANK TACTICAL VICTORY", COLOR_CYAN),
    ]
    for lbl, val, col in stats:
        t_l = font_card.render(lbl, True, (148, 163, 184))
        t_v = font_card.render(val, True, col)
        canvas.blit(t_l, (frame_rect.left + 50, sy))
        canvas.blit(t_v, (frame_rect.right - 50 - t_v.get_width(), sy))
        sy += 36

    btn_y = frame_rect.bottom - 75
    btn_w = 170
    btn_h = 44
    gap = 20
    total_btn_w = 3 * btn_w + 2 * gap
    btn_start_x = (vw - total_btn_w) // 2

    # 1. Next Stage
    b_next = pygame.Rect(btn_start_x, btn_y, btn_w, btn_h)
    hov_next = b_next.collidepoint(m_pos)
    pygame.draw.rect(canvas, (16, 185, 129, 80) if hov_next else (15, 23, 42), b_next, border_radius=6)
    pygame.draw.rect(canvas, COLOR_EMERALD if hov_next else (50, 120, 90), b_next, 2 if hov_next else 1, border_radius=6)
    t_next = font_card.render("NEXT STAGE [SPACE]", True, COLOR_WHITE if hov_next else COLOR_EMERALD)
    canvas.blit(t_next, t_next.get_rect(center=b_next.center))
    buttons["next"] = b_next

    # 2. Hangar
    b_hangar = pygame.Rect(btn_start_x + btn_w + gap, btn_y, btn_w, btn_h)
    hov_hangar = b_hangar.collidepoint(m_pos)
    pygame.draw.rect(canvas, (245, 158, 11, 80) if hov_hangar else (15, 23, 42), b_hangar, border_radius=6)
    pygame.draw.rect(canvas, COLOR_GOLD if hov_hangar else (120, 90, 40), b_hangar, 2 if hov_hangar else 1, border_radius=6)
    t_hangar = font_card.render("HANGAR [H]", True, COLOR_WHITE if hov_hangar else COLOR_GOLD)
    canvas.blit(t_hangar, t_hangar.get_rect(center=b_hangar.center))
    buttons["hangar"] = b_hangar

    # 3. Map / Menu
    b_map = pygame.Rect(btn_start_x + 2 * (btn_w + gap), btn_y, btn_w, btn_h)
    hov_map = b_map.collidepoint(m_pos)
    pygame.draw.rect(canvas, (14, 165, 233, 80) if hov_map else (15, 23, 42), b_map, border_radius=6)
    pygame.draw.rect(canvas, COLOR_CYAN if hov_map else (40, 80, 110), b_map, 2 if hov_map else 1, border_radius=6)
    t_map = font_card.render("MAP [M]", True, COLOR_WHITE if hov_map else COLOR_CYAN)
    canvas.blit(t_map, t_map.get_rect(center=b_map.center))
    buttons["map"] = b_map

    return buttons


def draw_game_over_ui(canvas: pygame.Surface, sector_idx: int = 0, sub_level: int = 1, score: int = 0, mouse_pos: tuple[int, int] = None) -> dict:
    """Renders atmospheric tactical Game Over screen with retry and navigation."""
    vw, vh = canvas.get_size()
    m_pos = mouse_pos or (0, 0)
    buttons = {}

    dim_surf = pygame.Surface((vw, vh), pygame.SRCALPHA)
    dim_surf.fill((18, 5, 10, 220))
    canvas.blit(dim_surf, (0, 0))

    frame_w = 640
    frame_h = 400
    frame_rect = pygame.Rect((vw - frame_w) // 2, (vh - frame_h) // 2, frame_w, frame_h)

    pygame.draw.rect(canvas, (24, 10, 15), frame_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_CRIMSON, frame_rect, 2, border_radius=10)

    t_title = font_title.render("MISSION FAILED", True, COLOR_CRIMSON)
    t_sub = font_banner.render("DRONE CHASSIS DESTROYED — SIGNAL LOST", True, (248, 113, 113))
    canvas.blit(t_title, t_title.get_rect(center=(vw // 2, frame_rect.top + 45)))
    canvas.blit(t_sub, t_sub.get_rect(center=(vw // 2, frame_rect.top + 90)))

    sy = frame_rect.top + 145
    stats = [
        ("SECTOR / STAGE:", f"SECTOR {sector_idx + 1} - STAGE {sub_level}", COLOR_WHITE),
        ("SCORE ATTAINED:", f"{score:,} PTS", COLOR_GOLD),
        ("CAUSE OF FAILURE:", "CRITICAL HULL INTEGRITY COMPROMISE", COLOR_CRIMSON),
    ]
    for lbl, val, col in stats:
        t_l = font_card.render(lbl, True, (148, 163, 184))
        t_v = font_card.render(val, True, col)
        canvas.blit(t_l, (frame_rect.left + 50, sy))
        canvas.blit(t_v, (frame_rect.right - 50 - t_v.get_width(), sy))
        sy += 36

    btn_y = frame_rect.bottom - 75
    btn_w = 170
    btn_h = 44
    gap = 20
    total_btn_w = 3 * btn_w + 2 * gap
    btn_start_x = (vw - total_btn_w) // 2

    # 1. Retry
    b_retry = pygame.Rect(btn_start_x, btn_y, btn_w, btn_h)
    hov_retry = b_retry.collidepoint(m_pos)
    pygame.draw.rect(canvas, (239, 68, 68, 80) if hov_retry else (24, 10, 15), b_retry, border_radius=6)
    pygame.draw.rect(canvas, COLOR_CRIMSON if hov_retry else (120, 40, 50), b_retry, 2 if hov_retry else 1, border_radius=6)
    t_retry = font_card.render("RETRY [SPACE]", True, COLOR_WHITE if hov_retry else COLOR_CRIMSON)
    canvas.blit(t_retry, t_retry.get_rect(center=b_retry.center))
    buttons["retry"] = b_retry

    # 2. Hangar
    b_hangar = pygame.Rect(btn_start_x + btn_w + gap, btn_y, btn_w, btn_h)
    hov_hangar = b_hangar.collidepoint(m_pos)
    pygame.draw.rect(canvas, (245, 158, 11, 80) if hov_hangar else (24, 10, 15), b_hangar, border_radius=6)
    pygame.draw.rect(canvas, COLOR_GOLD if hov_hangar else (120, 90, 40), b_hangar, 2 if hov_hangar else 1, border_radius=6)
    t_hangar = font_card.render("HANGAR [H]", True, COLOR_WHITE if hov_hangar else COLOR_GOLD)
    canvas.blit(t_hangar, t_hangar.get_rect(center=b_hangar.center))
    buttons["hangar"] = b_hangar

    # 3. Quit
    b_quit = pygame.Rect(btn_start_x + 2 * (btn_w + gap), btn_y, btn_w, btn_h)
    hov_quit = b_quit.collidepoint(m_pos)
    pygame.draw.rect(canvas, (100, 116, 139, 80) if hov_quit else (24, 10, 15), b_quit, border_radius=6)
    pygame.draw.rect(canvas, (148, 163, 184) if hov_quit else (70, 80, 95), b_quit, 2 if hov_quit else 1, border_radius=6)
    t_quit = font_card.render("MENU [Q]", True, COLOR_WHITE if hov_quit else (148, 163, 184))
    canvas.blit(t_quit, t_quit.get_rect(center=b_quit.center))
    buttons["menu"] = b_quit

    return buttons


def draw_save_slot_select_ui(canvas: pygame.Surface, save_system, mouse_pos: tuple[int, int] = None) -> dict:
    """Renders save slot selection screen with 3 slots + legacy save detection."""
    canvas.fill((6, 10, 18))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    title = font_title.render("SELECT SAVE SLOT", True, COLOR_CYAN)
    canvas.blit(title, title.get_rect(center=(vw // 2, 60)))

    sub = font_banner.render("CHOOSE A SLOT OR START A NEW GAME", True, COLOR_TEXT_DIM)
    canvas.blit(sub, sub.get_rect(center=(vw // 2, 105)))

    slots = save_system.get_save_slot_list()
    slot_rects = {}
    card_w, card_h = 520, 130
    gap = 20
    start_y = 150

    for i, slot_meta in enumerate(slots[:3]):
        cx = vw // 2 - card_w // 2
        cy = start_y + i * (card_h + gap)
        card_rect = pygame.Rect(cx, cy, card_w, card_h)

        is_hover = card_rect.collidepoint(mx, my)
        bg_c = (22, 36, 58) if is_hover else (14, 22, 38)
        border_c = COLOR_WHITE if is_hover else COLOR_CYAN
        border_w = 2 if is_hover else 1

        pygame.draw.rect(canvas, bg_c, card_rect, border_radius=8)
        pygame.draw.rect(canvas, border_c, card_rect, border_w, border_radius=8)

        slot_label = font_header.render(f"SLOT {i + 1}", True, COLOR_CYAN if not slot_meta["exists"] else COLOR_GOLD)
        canvas.blit(slot_label, (cx + 20, cy + 14))

        if slot_meta["exists"]:
            diff_name = DIFFICULTY_NAMES[slot_meta["difficulty_mode"]] if slot_meta["difficulty_mode"] < len(DIFFICULTY_NAMES) else "UNKNOWN"
            info_lines = [
                f"Sector: {slot_meta['sector']}  |  Difficulty: {diff_name}",
                f"Scrap: {slot_meta['scrap']:,}  |  High Score: {slot_meta['highscore']:,}",
                f"Play Time: {slot_meta['play_time'] // 60}m {slot_meta['play_time'] % 60}s",
            ]
            if slot_meta["last_played"]:
                info_lines.append(f"Last Played: {slot_meta['last_played']}")

            line_y = cy + 50
            for line in info_lines:
                info_surf = font_card.render(line, True, COLOR_TEXT_DIM)
                canvas.blit(info_surf, (cx + 20, line_y))
                line_y += 26

            del_btn_w, del_btn_h = 100, 32
            del_btn = pygame.Rect(cx + card_w - del_btn_w - 20, cy + card_h - del_btn_h - 12, del_btn_w, del_btn_h)
            del_hover = del_btn.collidepoint(mx, my)
            pygame.draw.rect(canvas, (60, 20, 25) if del_hover else (35, 15, 20), del_btn, border_radius=5)
            pygame.draw.rect(canvas, COLOR_CRIMSON, del_btn, 2 if del_hover else 1, border_radius=5)
            del_txt = font_sub.render("DELETE", True, COLOR_CRIMSON if del_hover else (180, 80, 90))
            canvas.blit(del_txt, del_txt.get_rect(center=del_btn.center))
            slot_rects[f"del_{i}"] = del_btn
        else:
            empty_txt = font_card.render("EMPTY SLOT", True, (80, 95, 115))
            canvas.blit(empty_txt, (cx + 20, cy + 55))

        slot_rects[f"slot_{i}"] = card_rect

    btn_w, btn_h = 200, 40
    bx = vw // 2 - btn_w // 2
    by = start_y + 3 * (card_h + gap) + 10

    r_back = pygame.Rect(bx, by, btn_w, btn_h)
    draw_button(canvas, r_back, "[ESC] BACK", (mx, my), base_color=COLOR_CRIMSON)
    slot_rects["back"] = r_back

    return slot_rects


def draw_custom_difficulty_ui(canvas: pygame.Surface, custom_settings: dict, mouse_pos: tuple[int, int] = None, dragging: int = -1) -> dict:
    """Renders custom difficulty configuration with sliders for all multipliers."""
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    panel_w, panel_h = 620, 520
    panel_rect = pygame.Rect(vw // 2 - panel_w // 2, vh // 2 - panel_h // 2, panel_w, panel_h)
    pygame.draw.rect(canvas, (14, 22, 38), panel_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_CYAN, panel_rect, 2, border_radius=10)

    t_hdr = font_header.render("CUSTOM DIFFICULTY", True, COLOR_CYAN)
    canvas.blit(t_hdr, t_hdr.get_rect(center=(vw // 2, panel_rect.top + 36)))

    sub = font_card.render("Adjust multipliers below (0.5x - 3.0x)", True, COLOR_TEXT_DIM)
    canvas.blit(sub, sub.get_rect(center=(vw // 2, panel_rect.top + 68)))

    sliders = {
        "hp_mult": {"label": "HP Multiplier", "min": 0.5, "max": 3.0, "step": 0.05},
        "speed_mult": {"label": "Speed Multiplier", "min": 0.5, "max": 3.0, "step": 0.05},
        "damage_mult": {"label": "Damage Multiplier", "min": 0.5, "max": 3.0, "step": 0.05},
        "powerup_drop_rate": {"label": "Powerup Drop Rate", "min": 0.5, "max": 3.0, "step": 0.05},
        "score_mult": {"label": "Score Multiplier", "min": 0.5, "max": 3.0, "step": 0.05},
    }

    slider_rects = {}
    by = panel_rect.top + 100
    slider_h = 14
    track_h = 8
    handle_w = 18
    handle_h = 22

    for key, cfg in sliders.items():
        val = float(custom_settings.get(key, CUSTOM_DIFFICULTY_DEFAULTS.get(key, 1.0)))
        val = max(cfg["min"], min(cfg["max"], val))

        label_surf = font_card.render(cfg["label"], True, COLOR_WHITE)
        canvas.blit(label_surf, (panel_rect.left + 40, by))

        val_surf = font_card.render(f"{val:.2f}x", True, COLOR_GOLD)
        canvas.blit(val_surf, (panel_rect.right - 90, by))

        track_rect = pygame.Rect(panel_rect.left + 40, by + 28, panel_w - 160, track_h)
        pygame.draw.rect(canvas, (30, 42, 62), track_rect, border_radius=4)

        ratio = (val - cfg["min"]) / (cfg["max"] - cfg["min"])
        fill_w = int(track_rect.width * ratio)
        fill_rect = pygame.Rect(track_rect.left, track_rect.top, fill_w, track_rect.height)
        pygame.draw.rect(canvas, COLOR_CYAN, fill_rect, border_radius=4)

        handle_x = track_rect.left + fill_w - handle_w // 2
        handle_rect = pygame.Rect(handle_x, track_rect.top - (handle_h - track_h) // 2, handle_w, handle_h)
        handle_col = COLOR_WHITE if dragging == key else COLOR_CYAN
        pygame.draw.rect(canvas, handle_col, handle_rect, border_radius=3)

        slider_rects[key] = {
            "track": track_rect,
            "handle": handle_rect,
            "value": val,
            "min": cfg["min"],
            "max": cfg["max"],
            "step": cfg["step"]
        }

        by += 70

    btn_w, btn_h = 200, 42
    bx = vw // 2 - btn_w // 2
    by = panel_rect.bottom - 60

    r_back = pygame.Rect(bx - 110, by, btn_w, btn_h)
    r_reset = pygame.Rect(bx, by, btn_w, btn_h)
    r_save = pygame.Rect(bx + 110, by, btn_w, btn_h)

    draw_button(canvas, r_back, "[ESC] BACK", (mx, my), base_color=COLOR_CRIMSON)
    draw_button(canvas, r_reset, "RESET DEFAULTS", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD)
    draw_button(canvas, r_save, "[ENTER] SAVE", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)

    slider_rects["back"] = r_back
    slider_rects["reset"] = r_reset
    slider_rects["save"] = r_save

    return slider_rects

