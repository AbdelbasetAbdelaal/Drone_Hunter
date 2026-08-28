import math
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON,
    COLOR_EMERALD, COLOR_WHITE, COLOR_BG, COLOR_HUD, COLOR_TEXT_DIM
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


def draw_button(canvas: pygame.Surface, rect: pygame.Rect, text: str,
                mouse_pos: tuple[int, int] = (0, 0),
                base_color=COLOR_CYAN, bg_color=(15, 23, 42),
                hover_bg=(30, 41, 59),
                text_color=COLOR_WHITE, font=font_button, is_selected: bool = False) -> bool:
    """Helper to draw a styled cyberpunk button and return whether it is hovered or selected."""
    is_hover = rect.collidepoint(mouse_pos) or is_selected
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


def draw_main_menu(canvas: pygame.Surface, mouse_pos: tuple[int, int] = None, selected_index: int = None) -> dict[str, pygame.Rect]:
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

    draw_button(canvas, r_play, "[SPACE] DEPLOY COMBAT", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD, is_selected=(selected_index == 0))
    draw_button(canvas, r_hangar, "[H] HANGAR ARMORY", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD, is_selected=(selected_index == 1))
    draw_button(canvas, r_settings, "[S] SYSTEM SETTINGS", (mx, my), base_color=COLOR_CYAN, text_color=COLOR_CYAN, is_selected=(selected_index == 2))
    draw_button(canvas, r_exit, "[Q] QUIT GAME", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON, is_selected=(selected_index == 3))

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
    
    current_selected_sector = ctx.campaign_state.current_sector_idx + 1
    
    sy = 126
    card_h = 66
    for sec in SECTORS_PHASE5:
        s_id = sec["id"]
        is_unlocked = ctx.campaign_state.is_sector_unlocked(s_id)
        is_completed = ctx.campaign_state.is_sector_completed(s_id)
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
        is_unlocked = ctx.campaign_state.is_mission_unlocked(m_id)
        is_completed = ctx.campaign_state.is_mission_completed(m_id)
        
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


def draw_mission_briefing(canvas: pygame.Surface, mission_data: dict, scrap: int, mouse_pos: tuple[int, int] = None, input_manager=None) -> dict:
    """Renders structured, responsive Mission Briefing with separated primary/side objectives and zero text overlap."""
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    is_controller = False
    if input_manager and getattr(input_manager, "active_device", "") in ("gamepad", "joystick"):
        is_controller = True

    sec_id = mission_data.get("sector_id", 1)
    sec_colors = {
        1: COLOR_CYAN,
        2: COLOR_GOLD,
        3: COLOR_EMERALD,
        4: (168, 85, 247), # Violet
        5: COLOR_CRIMSON
    }
    accent_col = sec_colors.get(sec_id, COLOR_CYAN)

    panel_w = min(820, vw - 48)
    panel_h = min(610, vh - 48)
    panel_rect = pygame.Rect((vw - panel_w) // 2, (vh - panel_h) // 2, panel_w, panel_h)

    pygame.draw.rect(canvas, (14, 22, 38), panel_rect, border_radius=10)
    pygame.draw.rect(canvas, accent_col, panel_rect, 2, border_radius=10)

    # 1. Header Bar
    t_hdr = font_header.render("TACTICAL MISSION BRIEFING", True, accent_col)
    canvas.blit(t_hdr, t_hdr.get_rect(center=(vw // 2, panel_rect.top + 26)))

    sec_txt = f"SECTOR {sec_id} — MISSION {mission_data.get('mission_number', 1)}: {mission_data.get('name', 'Operation')}"
    t_sec = font_card.render(sec_txt, True, COLOR_WHITE)
    canvas.blit(t_sec, t_sec.get_rect(center=(vw // 2, panel_rect.top + 54)))

    # 2. Primary Objective Card
    obj_box_w = panel_w - 48
    obj_box_h = 76
    obj_box_y = panel_rect.top + 78
    obj_rect = pygame.Rect(panel_rect.left + 24, obj_box_y, obj_box_w, obj_box_h)

    pygame.draw.rect(canvas, (20, 30, 50), obj_rect, border_radius=6)
    pygame.draw.rect(canvas, COLOR_GOLD, obj_rect, 1, border_radius=6)

    # Tag Badge
    tag_rect = pygame.Rect(obj_rect.left + 10, obj_rect.top + 10, 110, 24)
    pygame.draw.rect(canvas, (245, 158, 11, 40), tag_rect, border_radius=4)
    pygame.draw.rect(canvas, COLOR_GOLD, tag_rect, 1, border_radius=4)
    t_tag = font_sub.render("PRIMARY TARGET", True, COLOR_GOLD)
    canvas.blit(t_tag, t_tag.get_rect(center=tag_rect.center))

    # Target description
    obj_str = mission_data.get("objective", "ELIMINATE THREATS").replace("_", " ").upper()
    if obj_str == "SURVIVE":
        obj_str += f" FOR {mission_data.get('duration', 60)} SECONDS"
    t_obj = font_card.render(f"DESTROY / OVERCOME: {obj_str}", True, COLOR_WHITE)
    canvas.blit(t_obj, (tag_rect.right + 14, obj_rect.top + 12))

    # Difficulty and Reward Chips
    diff_val = mission_data.get("difficulty", 1)
    diff_names = {1: "EASY", 2: "NORMAL", 3: "HARD", 4: "VERY HARD", 5: "EXTREME"}
    diff_label = diff_names.get(diff_val, "NORMAL")
    from src.data.mission_data import MISSION_REWARDS
    rew = MISSION_REWARDS.get(diff_val, 150)

    t_diff = font_sub.render(f"DIFFICULTY: {diff_label} [{diff_val}/5]", True, COLOR_CRIMSON if diff_val >= 4 else COLOR_GOLD)
    t_rew = font_sub.render(f"OPERATION REWARD: +{rew:,} SCRAP", True, COLOR_EMERALD)
    canvas.blit(t_diff, (obj_rect.left + 14, obj_rect.top + 46))
    canvas.blit(t_rew, (obj_rect.left + 260, obj_rect.top + 46))

    # 3. Tactical Intel Briefing Box
    intel_y = obj_rect.bottom + 12
    intel_h = 104
    intel_rect = pygame.Rect(panel_rect.left + 24, intel_y, obj_box_w, intel_h)
    pygame.draw.rect(canvas, (16, 24, 40), intel_rect, border_radius=6)
    pygame.draw.rect(canvas, (40, 58, 85), intel_rect, 1, border_radius=6)

    lbl_intel = font_card.render("INTEL BRIEFING:", True, COLOR_CYAN)
    canvas.blit(lbl_intel, (intel_rect.left + 14, intel_y + 10))

    lore_text = mission_data.get("lore", "Hostile drones detected in operational grid. Neutralize enemy forces and complete primary mission parameters.")
    words = lore_text.split()
    lines = []
    curr = []
    max_c = max(55, int(obj_box_w // 9.5))
    for w in words:
        test = " ".join(curr + [w])
        if len(test) <= max_c:
            curr.append(w)
        else:
            lines.append(" ".join(curr))
            curr = [w]
    if curr:
        lines.append(" ".join(curr))

    line_y = intel_y + 36
    for l_str in lines[:3]:
        s_surf = font_sub.render(l_str, True, (170, 185, 205))
        canvas.blit(s_surf, (intel_rect.left + 14, line_y))
        line_y += 20

    # 4. Side Objectives Dedicated Box (Guaranteed non-overlapping)
    side_y = intel_rect.bottom + 12
    side_h = 120
    side_rect = pygame.Rect(panel_rect.left + 24, side_y, obj_box_w, side_h)
    pygame.draw.rect(canvas, (16, 24, 40), side_rect, border_radius=6)
    pygame.draw.rect(canvas, (35, 60, 50), side_rect, 1, border_radius=6)

    lbl_side = font_card.render("TACTICAL SIDE OBJECTIVES:", True, COLOR_EMERALD)
    canvas.blit(lbl_side, (side_rect.left + 14, side_y + 10))

    side_objs = mission_data.get("side_objectives", [])
    if side_objs:
        from src.systems.mission_system import SIDE_OBJ_TYPE_NAMES
        so_y = side_y + 36
        for so in side_objs[:3]:
            so_type = so.get("type", "")
            so_value = so.get("value", 0)
            type_name = SIDE_OBJ_TYPE_NAMES.get(so_type, so_type.upper())
            if so_type == "collect_data_cores":
                so_desc = f"[ ] Collect {so_value} Data Cores"
                so_b = "+50 SCRAP"
            elif so_type == "no_damage_taken":
                so_desc = "[ ] Flawless Run: Take No Hull Damage"
                so_b = "+100 SCRAP"
            elif so_type == "time_limit":
                so_desc = f"[ ] Blitzkrieg: Complete within {so_value}s"
                so_b = "+75 SCRAP"
            elif so_type == "precision_strikes":
                so_desc = f"[ ] Execute {so_value} Precision Strikes"
                so_b = "+60 SCRAP"
            else:
                so_desc = f"[ ] {type_name}"
                so_b = "+50 SCRAP"

            so_surf = font_sub.render(so_desc, True, (180, 210, 195))
            b_surf = font_sub.render(so_b, True, COLOR_GOLD)
            canvas.blit(so_surf, (side_rect.left + 16, so_y))
            canvas.blit(b_surf, (side_rect.right - b_surf.get_width() - 16, so_y))
            so_y += 24
    else:
        no_so = font_sub.render("No tactical side objectives for this operation.", True, COLOR_TEXT_DIM)
        canvas.blit(no_so, (side_rect.left + 16, side_y + 40))

    # 5. Briefing Navigation Buttons (Device-Aware)
    btn_w = (obj_box_w - 24) // 3
    btn_h = 42
    by = panel_rect.bottom - btn_h - 16

    r_back = pygame.Rect(panel_rect.left + 24, by, btn_w, btn_h)
    r_start = pygame.Rect(panel_rect.left + 24 + btn_w + 12, by, btn_w, btn_h)
    r_exit = pygame.Rect(panel_rect.left + 24 + 2 * (btn_w + 12), by, btn_w, btn_h)

    lbl_back = "[O] BACK" if is_controller else "[ESC] BACK"
    lbl_deploy = "[X] DEPLOY NOW" if is_controller else "[SPACE] DEPLOY"
    lbl_quit = "[SELECT] QUIT" if is_controller else "[Q] QUIT"

    draw_button(canvas, r_back, lbl_back, (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_start, lbl_deploy, (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)
    draw_button(canvas, r_exit, lbl_quit, (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON)

    return {"back": r_back, "start": r_start, "exit": r_exit}


def draw_settings_menu_ui(canvas: pygame.Surface, difficulty_mode: int, show_crt: bool, sound_enabled: bool, mouse_pos: tuple[int, int] = None, input_manager=None, selected_index: int = None, is_fullscreen: bool = False) -> dict:
    """Renders clean, categorized System & Audio Settings with clear visual focus and controller navigation."""
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    is_controller = False
    if input_manager and getattr(input_manager, "active_device", "") in ("gamepad", "joystick"):
        is_controller = True

    panel_w = min(660, vw - 40)
    panel_h = min(620, vh - 40)
    panel_rect = pygame.Rect((vw - panel_w) // 2, (vh - panel_h) // 2, panel_w, panel_h)
    pygame.draw.rect(canvas, (14, 22, 38), panel_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_CYAN, panel_rect, 2, border_radius=10)

    # Title
    t_hdr = font_header.render("SYSTEM & AUDIO SETTINGS", True, COLOR_CYAN)
    canvas.blit(t_hdr, t_hdr.get_rect(center=(vw // 2, panel_rect.top + 28)))

    # Menu Options Defs (with category headers)
    btn_w = panel_w - 56
    btn_h = 36
    bx = panel_rect.left + 28
    by_start = panel_rect.top + 64
    spacing = 6

    diff_name = DIFFICULTY_NAMES[difficulty_mode]
    diff_col = DIFFICULTY_MODIFIERS[difficulty_mode]["badge_color"]
    disp_mode_str = "FULLSCREEN" if is_fullscreen else "WINDOWED"

    buttons_def = [
        # (key, text, base_col, text_col, category_header)
        ("fullscreen", f"DISPLAY: {disp_mode_str} [F11]" if not is_controller else f"DISPLAY: {disp_mode_str}  [X]", COLOR_CYAN, COLOR_WHITE, "DISPLAY & VISUALS"),
        ("crt", f"CRT SCANLINES: {'ENABLED' if show_crt else 'DISABLED'} [F2]" if not is_controller else f"CRT SCANLINES: {'ENABLED' if show_crt else 'DISABLED'}  [X]", COLOR_CYAN, COLOR_CYAN, None),
        ("sfx", f"AUDIO SFX: {'ENABLED' if sound_enabled else 'MUTED'}" if not is_controller else f"AUDIO SFX: {'ENABLED' if sound_enabled else 'MUTED'}  [X]", COLOR_GOLD, COLOR_GOLD, "AUDIO & SOUND"),
        ("diff", f"COMBAT DIFFICULTY: {diff_name}" if not is_controller else f"COMBAT DIFFICULTY: {diff_name}  [D-PAD ◀ / ▶]", diff_col, diff_col, "GAMEPLAY & BALANCE"),
        ("controller", "CONTROLLER SETTINGS (DEADZONE / SENSITIVITY)", COLOR_CYAN, COLOR_WHITE, "HARDWARE & INPUT"),
        ("config", "CONFIGURE BUTTON MAPPINGS", COLOR_GOLD, COLOR_GOLD, None),
        ("test", "TEST CONTROLLER HARDWARE", COLOR_EMERALD, COLOR_EMERALD, None),
        ("reset", "RESET ALL PROGRESS & SAVE DATA", COLOR_CRIMSON, COLOR_CRIMSON, "DATA & SAVE MANAGEMENT"),
    ]

    ret_rects = {}
    cur_y = by_start

    for idx, (b_key, b_text, b_base_col, b_text_col, cat_hdr) in enumerate(buttons_def):
        if cat_hdr:
            cat_surf = font_sub.render(cat_hdr, True, (148, 163, 184))
            canvas.blit(cat_surf, (bx + 4, cur_y))
            cur_y += 18

        r = pygame.Rect(bx, cur_y, btn_w, btn_h)
        is_sel = (selected_index == idx)
        draw_button(canvas, r, b_text, (mx, my), base_color=b_base_col, text_color=b_text_col, is_selected=is_sel)
        ret_rects[b_key] = r
        cur_y += btn_h + spacing

    # Back button at bottom
    r_back = pygame.Rect(bx, panel_rect.bottom - 46, btn_w, 38)
    lbl_back = "[O] BACK TO PREVIOUS SCREEN" if is_controller else "[ESC] BACK TO PREVIOUS SCREEN"
    draw_button(canvas, r_back, lbl_back, (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD, is_selected=(selected_index == len(buttons_def)))
    ret_rects["back"] = r_back

    return ret_rects


def draw_mission_complete(canvas: pygame.Surface, mission_data: dict, was_first_clear: bool, is_sector_clear: bool, mouse_pos: tuple[int, int] = None, selected_index: int = None) -> dict:
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
        base_rew = MISSION_REWARDS.get(diff, 150)
        sec_id = mission_data.get("sector_id", 1)
        sec_bon = SECTOR_BONUS.get(sec_id, 500) if is_sector_clear else 0
        tot_rew = base_rew + sec_bon

        t_rew = font_banner.render(f"FIRST CLEAR REWARD: +{tot_rew} SCRAP", True, COLOR_GOLD)
        canvas.blit(t_rew, t_rew.get_rect(center=(vw // 2, vh // 2 - 40)))
        
        if is_sector_clear:
            t_sec = font_card.render(f"SECTOR BONUS APPLIED (+{sec_bon} SCRAP)", True, COLOR_CYAN)
            canvas.blit(t_sec, t_sec.get_rect(center=(vw // 2, vh // 2 - 10)))
    else:
        t_rep = font_banner.render("REPEAT CLEAR: +25 SCRAP", True, COLOR_WHITE)
        canvas.blit(t_rep, t_rep.get_rect(center=(vw // 2, vh // 2 - 30)))

    btn_w, btn_h = 240, 44
    bx = vw // 2 - btn_w // 2
    by = vh // 2 + 40

    r_next = pygame.Rect(bx, by, btn_w, btn_h)
    r_hangar = pygame.Rect(bx, by + 54, btn_w, btn_h)

    draw_button(canvas, r_next, "[SPACE] SECTOR MAP", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD, is_selected=(selected_index == 0))
    draw_button(canvas, r_hangar, "[H] HANGAR ARMORY", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD, is_selected=(selected_index == 1))

    return {"next": r_next, "hangar": r_hangar}


def draw_mission_failed(canvas: pygame.Surface, scrap: int, mouse_pos: tuple[int, int] = None, selected_index: int = None) -> dict:
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

    draw_button(canvas, r_retry, "[SPACE] RETRY MISSION", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD, is_selected=(selected_index == 0))
    draw_button(canvas, r_map, "[M] SECTOR MAP", (mx, my), base_color=COLOR_CYAN, text_color=COLOR_CYAN, is_selected=(selected_index == 1))
    draw_button(canvas, r_exit, "[Q] QUIT TO MENU", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON, is_selected=(selected_index == 2))

    return {"retry": r_retry, "map": r_map, "exit": r_exit}


def draw_pause_settings_ui(canvas: pygame.Surface, difficulty_mode: int, show_crt: bool, sound_enabled: bool, mouse_pos: tuple[int, int] = None, selected_index: int = None) -> dict:
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

    draw_button(canvas, r_resume, "RESUME COMBAT [ESC/P]", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD, is_selected=(selected_index == 0))
    draw_button(canvas, r_diff, f"DIFFICULTY: {DIFFICULTY_NAMES[difficulty_mode]}", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD, is_selected=(selected_index == 1))
    draw_button(canvas, r_crt, f"CRT SCANLINES: {'ON' if show_crt else 'OFF'}", (mx, my), base_color=COLOR_CYAN, is_selected=(selected_index == 2))
    draw_button(canvas, r_sfx, f"AUDIO SFX: {'ENABLED' if sound_enabled else 'MUTED'}", (mx, my), base_color=COLOR_CYAN, is_selected=(selected_index == 3))
    draw_button(canvas, r_hangar, "HANGAR ARMORY [H]", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD, is_selected=(selected_index == 4))
    draw_button(canvas, r_map, "SECTOR MAP [M]", (mx, my), base_color=COLOR_CYAN, is_selected=(selected_index == 5))
    draw_button(canvas, r_exit, "QUIT TO MENU [Q]", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON, is_selected=(selected_index == 6))

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

def draw_level_clear_ui(canvas: pygame.Surface, sector_idx: int = 0, sub_level: int = 1, score: int = 0, scrap: int = 0, mouse_pos: tuple[int, int] = None, selected_index: int = None) -> dict:
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
    hov_next = b_next.collidepoint(m_pos) or (selected_index == 0)
    pygame.draw.rect(canvas, (16, 185, 129, 80) if hov_next else (15, 23, 42), b_next, border_radius=6)
    pygame.draw.rect(canvas, COLOR_EMERALD if hov_next else (50, 120, 90), b_next, 2 if hov_next else 1, border_radius=6)
    t_next = font_card.render("NEXT STAGE [SPACE]", True, COLOR_WHITE if hov_next else COLOR_EMERALD)
    canvas.blit(t_next, t_next.get_rect(center=b_next.center))
    buttons["next"] = b_next

    # 2. Hangar
    b_hangar = pygame.Rect(btn_start_x + btn_w + gap, btn_y, btn_w, btn_h)
    hov_hangar = b_hangar.collidepoint(m_pos) or (selected_index == 1)
    pygame.draw.rect(canvas, (245, 158, 11, 80) if hov_hangar else (15, 23, 42), b_hangar, border_radius=6)
    pygame.draw.rect(canvas, COLOR_GOLD if hov_hangar else (120, 90, 40), b_hangar, 2 if hov_hangar else 1, border_radius=6)
    t_hangar = font_card.render("HANGAR [H]", True, COLOR_WHITE if hov_hangar else COLOR_GOLD)
    canvas.blit(t_hangar, t_hangar.get_rect(center=b_hangar.center))
    buttons["hangar"] = b_hangar

    # 3. Map / Menu
    b_map = pygame.Rect(btn_start_x + 2 * (btn_w + gap), btn_y, btn_w, btn_h)
    hov_map = b_map.collidepoint(m_pos) or (selected_index == 2)
    pygame.draw.rect(canvas, (14, 165, 233, 80) if hov_map else (15, 23, 42), b_map, border_radius=6)
    pygame.draw.rect(canvas, COLOR_CYAN if hov_map else (40, 80, 110), b_map, 2 if hov_map else 1, border_radius=6)
    t_map = font_card.render("MAP [M]", True, COLOR_WHITE if hov_map else COLOR_CYAN)
    canvas.blit(t_map, t_map.get_rect(center=b_map.center))
    buttons["map"] = b_map

    return buttons


def draw_game_over_ui(canvas: pygame.Surface, sector_idx: int = 0, sub_level: int = 1, score: int = 0, mouse_pos: tuple[int, int] = None, selected_index: int = None) -> dict:
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
    hov_retry = b_retry.collidepoint(m_pos) or (selected_index == 0)
    pygame.draw.rect(canvas, (239, 68, 68, 80) if hov_retry else (24, 10, 15), b_retry, border_radius=6)
    pygame.draw.rect(canvas, COLOR_CRIMSON if hov_retry else (120, 40, 50), b_retry, 2 if hov_retry else 1, border_radius=6)
    t_retry = font_card.render("RETRY [SPACE]", True, COLOR_WHITE if hov_retry else COLOR_CRIMSON)
    canvas.blit(t_retry, t_retry.get_rect(center=b_retry.center))
    buttons["retry"] = b_retry

    # 2. Hangar
    b_hangar = pygame.Rect(btn_start_x + btn_w + gap, btn_y, btn_w, btn_h)
    hov_hangar = b_hangar.collidepoint(m_pos) or (selected_index == 1)
    pygame.draw.rect(canvas, (245, 158, 11, 80) if hov_hangar else (24, 10, 15), b_hangar, border_radius=6)
    pygame.draw.rect(canvas, COLOR_GOLD if hov_hangar else (120, 90, 40), b_hangar, 2 if hov_hangar else 1, border_radius=6)
    t_hangar = font_card.render("HANGAR [H]", True, COLOR_WHITE if hov_hangar else COLOR_GOLD)
    canvas.blit(t_hangar, t_hangar.get_rect(center=b_hangar.center))
    buttons["hangar"] = b_hangar

    # 3. Quit
    b_quit = pygame.Rect(btn_start_x + 2 * (btn_w + gap), btn_y, btn_w, btn_h)
    hov_quit = b_quit.collidepoint(m_pos) or (selected_index == 2)
    pygame.draw.rect(canvas, (100, 116, 139, 80) if hov_quit else (24, 10, 15), b_quit, border_radius=6)
    pygame.draw.rect(canvas, (148, 163, 184) if hov_quit else (70, 80, 95), b_quit, 2 if hov_quit else 1, border_radius=6)
    t_quit = font_card.render("MENU [Q]", True, COLOR_WHITE if hov_quit else (148, 163, 184))
    canvas.blit(t_quit, t_quit.get_rect(center=b_quit.center))
    buttons["menu"] = b_quit

    return buttons


def draw_save_slot_select_ui(canvas: pygame.Surface, save_system, mouse_pos: tuple[int, int] = None, input_manager=None, selected_index: int = None) -> dict:
    """Renders save slot selection screen with 3 slots + legacy save detection and controller support."""
    canvas.fill((6, 10, 18))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    is_controller = False
    if input_manager and getattr(input_manager, "active_device", "") in ("gamepad", "joystick"):
        is_controller = True

    title = font_title.render("SELECT SAVE SLOT", True, COLOR_CYAN)
    canvas.blit(title, title.get_rect(center=(vw // 2, 60)))

    sub_text = "CHOOSE A SLOT TO LOAD OR START A NEW GAME  •  [X] SELECT  [O] BACK" if is_controller else "CHOOSE A SLOT OR START A NEW GAME"
    sub = font_banner.render(sub_text, True, COLOR_TEXT_DIM)
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

        is_hover = card_rect.collidepoint(mx, my) or (selected_index == i)
        bg_c = (26, 44, 70) if is_hover else (14, 22, 38)
        border_c = COLOR_WHITE if is_hover else (COLOR_GOLD if slot_meta["exists"] else COLOR_CYAN)
        border_w = 3 if is_hover else 1

        pygame.draw.rect(canvas, bg_c, card_rect, border_radius=8)
        pygame.draw.rect(canvas, border_c, card_rect, border_w, border_radius=8)

        slot_label = font_header.render(f"SLOT {i + 1}", True, COLOR_CYAN if not slot_meta["exists"] else COLOR_GOLD)
        canvas.blit(slot_label, (cx + 20, cy + 14))

        if is_hover and is_controller:
            prompt_chip = font_sub.render("[X] LOAD" if slot_meta["exists"] else "[X] NEW GAME", True, COLOR_EMERALD)
            canvas.blit(prompt_chip, (cx + 120, cy + 18))

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

            del_btn_w, del_btn_h = 110, 32
            del_btn = pygame.Rect(cx + card_w - del_btn_w - 20, cy + card_h - del_btn_h - 12, del_btn_w, del_btn_h)
            del_hover = del_btn.collidepoint(mx, my)
            pygame.draw.rect(canvas, (60, 20, 25) if del_hover else (35, 15, 20), del_btn, border_radius=5)
            pygame.draw.rect(canvas, COLOR_CRIMSON, del_btn, 2 if del_hover else 1, border_radius=5)
            del_txt_str = "[SEL] DELETE" if is_controller else "DELETE"
            del_txt = font_sub.render(del_txt_str, True, COLOR_CRIMSON if del_hover else (180, 80, 90))
            canvas.blit(del_txt, del_txt.get_rect(center=del_btn.center))
            slot_rects[f"del_{i}"] = del_btn
        else:
            empty_txt = font_card.render("EMPTY SLOT — SELECT TO START CAMPAIGN", True, (100, 120, 145) if is_hover else (80, 95, 115))
            canvas.blit(empty_txt, (cx + 20, cy + 55))

        slot_rects[f"slot_{i}"] = card_rect

    btn_w, btn_h = 220, 40
    bx = vw // 2 - btn_w // 2
    by = start_y + 3 * (card_h + gap) + 10

    r_back = pygame.Rect(bx, by, btn_w, btn_h)
    lbl_b = "[O] BACK" if is_controller else "[ESC] BACK"
    draw_button(canvas, r_back, lbl_b, (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON, is_selected=(selected_index == 3))
    slot_rects["back"] = r_back

    return slot_rects


def draw_custom_difficulty_ui(canvas: pygame.Surface, custom_settings: dict, mouse_pos: tuple[int, int] = None, dragging: int = -1, input_manager=None, selected_index: int = None) -> dict:
    """Renders custom difficulty configuration with sliders for all multipliers and clear controller hints."""
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    is_controller = False
    if input_manager and getattr(input_manager, "active_device", "") in ("gamepad", "joystick"):
        is_controller = True

    panel_w, panel_h = 640, 530
    panel_rect = pygame.Rect(vw // 2 - panel_w // 2, vh // 2 - panel_h // 2, panel_w, panel_h)
    pygame.draw.rect(canvas, (14, 22, 38), panel_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_CYAN, panel_rect, 2, border_radius=10)

    t_hdr = font_header.render("CUSTOM DIFFICULTY", True, COLOR_CYAN)
    canvas.blit(t_hdr, t_hdr.get_rect(center=(vw // 2, panel_rect.top + 34)))

    sub_txt = "Adjust multipliers below • [D-PAD ◀ / ▶] To Adjust Value" if is_controller else "Adjust multipliers below (0.5x - 3.0x)"
    sub = font_card.render(sub_txt, True, COLOR_TEXT_DIM)
    canvas.blit(sub, sub.get_rect(center=(vw // 2, panel_rect.top + 64)))

    sliders = {
        "hp_mult": {"label": "HP Multiplier", "min": 0.5, "max": 3.0, "step": 0.05},
        "speed_mult": {"label": "Speed Multiplier", "min": 0.5, "max": 3.0, "step": 0.05},
        "damage_mult": {"label": "Damage Multiplier", "min": 0.5, "max": 3.0, "step": 0.05},
        "powerup_drop_rate": {"label": "Powerup Drop Rate", "min": 0.5, "max": 3.0, "step": 0.05},
        "score_mult": {"label": "Score Multiplier", "min": 0.5, "max": 3.0, "step": 0.05},
    }

    slider_rects = {}
    by = panel_rect.top + 94
    slider_h = 14
    track_h = 8
    handle_w = 18
    handle_h = 22

    for s_idx, (key, cfg) in enumerate(sliders.items()):
        val = float(custom_settings.get(key, CUSTOM_DIFFICULTY_DEFAULTS.get(key, 1.0)))
        val = max(cfg["min"], min(cfg["max"], val))

        is_focused = (selected_index == s_idx)
        lbl_col = COLOR_CYAN if is_focused else COLOR_WHITE
        label_surf = font_card.render(cfg["label"], True, lbl_col)
        canvas.blit(label_surf, (panel_rect.left + 40, by))

        val_str = f"{val:.2f}x"
        if is_focused and is_controller:
            val_str += "  [◀ / ▶]"
        val_surf = font_card.render(val_str, True, COLOR_GOLD if is_focused else (245, 158, 11))
        canvas.blit(val_surf, (panel_rect.right - 140, by))

        track_rect = pygame.Rect(panel_rect.left + 40, by + 28, panel_w - 160, track_h)
        pygame.draw.rect(canvas, (30, 42, 62), track_rect, border_radius=4)

        ratio = (val - cfg["min"]) / (cfg["max"] - cfg["min"])
        fill_w = int(track_rect.width * ratio)
        fill_rect = pygame.Rect(track_rect.left, track_rect.top, fill_w, track_rect.height)
        pygame.draw.rect(canvas, COLOR_EMERALD if is_focused else COLOR_CYAN, fill_rect, border_radius=4)

        handle_x = track_rect.left + fill_w - handle_w // 2
        handle_rect = pygame.Rect(handle_x, track_rect.top - (handle_h - track_h) // 2, handle_w, handle_h)
        handle_col = COLOR_WHITE if (dragging == key or is_focused) else COLOR_CYAN
        pygame.draw.rect(canvas, handle_col, handle_rect, border_radius=3)

        slider_rects[key] = {
            "track": track_rect,
            "handle": handle_rect,
            "value": val,
            "min": cfg["min"],
            "max": cfg["max"],
            "step": cfg["step"]
        }

        by += 68

    btn_w, btn_h = 180, 40
    bx = vw // 2 - btn_w // 2
    by = panel_rect.bottom - 54

    r_back = pygame.Rect(bx - 120, by, btn_w, btn_h)
    r_reset = pygame.Rect(bx + 120, by, btn_w, btn_h)

    lbl_back = "[O] CANCEL" if is_controller else "[ESC] BACK"
    lbl_save = "[X] SAVE & EXIT" if is_controller else "[ENTER] SAVE"
    draw_button(canvas, r_back, lbl_back, (mx, my), base_color=COLOR_CRIMSON, is_selected=(selected_index == 5))
    draw_button(canvas, r_reset, lbl_save, (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD, is_selected=(selected_index == 6))

    slider_rects["back"] = r_back
    slider_rects["save"] = r_reset
    slider_rects["reset"] = r_reset

    return slider_rects


def get_button_label(base_label: str, action: str, input_manager=None) -> str:
    """Appends controller prompt to button label when a gamepad is active."""
    if input_manager and input_manager.active_device in ("gamepad", "joystick"):
        prompt = input_manager.get_prompt_for_action(action)
        if prompt and prompt != action:
            return f"{base_label} [{prompt}]"
    return base_label


def draw_controller_binding_ui(canvas: pygame.Surface, mapping_manager, mouse_pos: tuple[int, int] = None, binding_action: str = None, waiting: bool = False) -> dict:
    """Categorized controller button binding wizard with clear grouping, shared control telemetry, and zero overflow."""
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    from src.input.controller_mapping import (
        get_physical_button_name, GAMEPLAY_ACTIONS, MENU_ACTIONS, CONTEXTUAL_ACTIONS
    )

    panel_w = min(920, vw - 40)
    panel_h = min(620, vh - 40)
    panel_rect = pygame.Rect((vw - panel_w) // 2, (vh - panel_h) // 2, panel_w, panel_h)
    pygame.draw.rect(canvas, (14, 22, 38), panel_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_GOLD, panel_rect, 2, border_radius=10)

    # 1. Header Title
    t_hdr = font_header.render("CONTROLLER BINDING WIZARD", True, COLOR_GOLD)
    canvas.blit(t_hdr, t_hdr.get_rect(center=(vw // 2, panel_rect.top + 24)))

    # Active Device Name & Type
    profile = None
    if mapping_manager.profiles:
        profile = next(iter(mapping_manager.profiles.values()), None)

    dev_name = profile.device_name if profile else "Generic USB Gamepad"
    dev_type = profile.controller_type.upper() if profile else "GENERIC"
    name_surf = font_sub.render(f"ACTIVE HARDWARE: {dev_name}  [{dev_type}]", True, COLOR_CYAN)
    canvas.blit(name_surf, (panel_rect.left + 24, panel_rect.top + 50))

    # 2. Categorized 2-Column Balanced Layout
    col_w = (panel_w - 64) // 2
    row_h = 32
    row_gap = 4
    start_y = panel_rect.top + 78
    action_rows = []

    # COLUMN 1: GAMEPLAY ACTIONS
    c1_x = panel_rect.left + 24
    lbl_c1 = font_card.render("GAMEPLAY ACTIONS", True, COLOR_CYAN)
    canvas.blit(lbl_c1, (c1_x + 4, start_y))

    cur_y1 = start_y + 22
    for action in GAMEPLAY_ACTIONS:
        r_rect = pygame.Rect(c1_x, cur_y1, col_w, row_h)
        action_rows.append((action, r_rect, False))
        cur_y1 += row_h + row_gap

    # COLUMN 2 TOP: MENU ACTIONS
    c2_x = panel_rect.left + 24 + col_w + 16
    lbl_c2_menu = font_card.render("MENU & SYSTEM ACTIONS", True, COLOR_GOLD)
    canvas.blit(lbl_c2_menu, (c2_x + 4, start_y))

    cur_y2 = start_y + 22
    for action in MENU_ACTIONS:
        r_rect = pygame.Rect(c2_x, cur_y2, col_w, row_h)
        action_rows.append((action, r_rect, False))
        cur_y2 += row_h + row_gap

    # COLUMN 2 BOTTOM: CONTEXTUAL & SHARED CONTROLS
    cur_y2 += 8
    lbl_c2_ctx = font_card.render("CONTEXTUAL & SHARED CONTROLS", True, (168, 85, 247))
    canvas.blit(lbl_c2_ctx, (c2_x + 4, cur_y2))

    cur_y2 += 22
    for action in CONTEXTUAL_ACTIONS:
        r_rect = pygame.Rect(c2_x, cur_y2, col_w, row_h)
        action_rows.append((action, r_rect, True))
        cur_y2 += row_h + row_gap

    # 3. Render Action Cards
    for action, row_rect, is_contextual in action_rows:
        is_selected = (action == binding_action)
        is_hovered = row_rect.collidepoint(mx, my)

        bg_c = (35, 52, 80) if is_selected else ((24, 36, 56) if is_hovered else (16, 24, 38))
        border_c = COLOR_GOLD if is_selected else (COLOR_CYAN if is_hovered else (45, 62, 88))
        pygame.draw.rect(canvas, bg_c, row_rect, border_radius=4)
        pygame.draw.rect(canvas, border_c, row_rect, 2 if (is_selected or is_hovered) else 1, border_radius=4)

        # Action Display Name
        act_display_names = {
            "fire_primary": "Primary Fire",
            "emp": "EMP Attack",
            "ultimate": "Overdrive / Ultimate",
            "roll": "Barrel Roll",
            "weapon_next": "Weapon Next",
            "cloak": "Tactical Cloak",
            "confirm": "Menu Confirm",
            "cancel": "Menu Cancel / Back",
            "pause": "Pause Menu",
            "sector_map": "Sector Map",
            "hangar_bay": "Hangar Bay",
            "weapon_prev": "Weapon Previous",
            "cycle_class": "Cycle Drone Class",
            "fullscreen": "Toggle Fullscreen",
        }
        act_name = act_display_names.get(action, action.replace("_", " ").title())
        label_col = COLOR_WHITE if (is_selected or is_hovered) else (190, 205, 225)
        label = font_sub.render(act_name, True, label_col)
        canvas.blit(label, (row_rect.left + 10, row_rect.top + 7))

        # Current Bound Badge
        if is_selected and waiting:
            btn_text = "PRESS BUTTON..."
            btn_col = COLOR_CYAN
        elif is_contextual:
            ctx_badges = {
                "weapon_prev": "FRONT TOP [HOLD]",
                "cycle_class": "FRONT BTM [HOLD]",
                "fullscreen": "START [HOLD]",
            }
            btn_text = ctx_badges.get(action, "SHARED INPUT")
            btn_col = (192, 132, 252) # Soft Purple
        elif profile and action in getattr(profile, "button_map", {}):
            btn_idx = profile.button_map[action]
            p_name = get_physical_button_name(btn_idx, profile.controller_type if profile else "generic_ps2")
            btn_text = f"{p_name} / BTN {btn_idx}" if btn_idx >= 0 else "NONE"
            btn_col = COLOR_GOLD if is_hovered else COLOR_CYAN
        else:
            btn_text = "NONE"
            btn_col = COLOR_TEXT_DIM

        badge_surf = font_sub.render(btn_text, True, btn_col)
        badge_rect = badge_surf.get_rect(right=row_rect.right - 10, centery=row_rect.centery)
        canvas.blit(badge_surf, badge_rect)

    # 4. Status / Hint Notice Bar
    hint_y = panel_rect.bottom - 66
    if waiting and binding_action:
        pulse_a = int(200 + 55 * math.sin(pygame.time.get_ticks() * 0.015)) if pygame.get_init() else 255
        wait_txt = font_banner.render(f"⚡ PRESS CONTROLLER BUTTON FOR: [{binding_action.replace('_', ' ').upper()}] ⚡", True, (*COLOR_CYAN[:3], pulse_a))
        canvas.blit(wait_txt, wait_txt.get_rect(center=(vw // 2, hint_y)))
    else:
        hint = font_sub.render("Click an action row to rebind • Contextual actions share physical buttons via Hold/Context", True, COLOR_TEXT_DIM)
        canvas.blit(hint, hint.get_rect(center=(vw // 2, hint_y)))

    # 5. Navigation Buttons
    btn_w, btn_h = 180, 36
    by = panel_rect.bottom - 44
    r_back = pygame.Rect(vw // 2 - btn_w - 12, by, btn_w, btn_h)
    r_reset = pygame.Rect(vw // 2 + 12, by, btn_w, btn_h)
    draw_button(canvas, r_back, "[ESC / O] BACK", (mx, my), base_color=COLOR_CRIMSON)
    draw_button(canvas, r_reset, "RESET DEFAULTS", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD)

    result = {
        "back": r_back,
        "reset": r_reset,
        "action_rows": {a: r for a, r, _ in action_rows}
    }
    return result


def draw_controller_test_ui(canvas: pygame.Surface, joystick, mapping_manager, mouse_pos: tuple[int, int] = None) -> dict:
    """Real-time controller test screen displaying canonical bindings synchronized with Gameplay & Binding Wizard."""
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    from src.input.controller_mapping import get_physical_button_name

    profile = mapping_manager.get_profile_for_joystick(joystick) if joystick else None
    if not profile and mapping_manager.profiles:
        profile = next(iter(mapping_manager.profiles.values()), None)

    # 1. Header
    header_rect = pygame.Rect(32, 16, vw - 64, 46)
    pygame.draw.rect(canvas, (14, 22, 38), header_rect, border_radius=8)
    pygame.draw.rect(canvas, COLOR_CYAN, header_rect, 2, border_radius=8)
    t_hdr = font_header.render("CONTROLLER HARDWARE TEST & DIAGNOSTICS", True, COLOR_CYAN)
    canvas.blit(t_hdr, (48, 24))

    if not joystick:
        no_js = font_banner.render("NO CONTROLLER DETECTED — CONNECT USB GAMEPAD", True, COLOR_CRIMSON)
        canvas.blit(no_js, (48, 90))
        r_back = pygame.Rect(32, vh - 55, 180, 40)
        draw_button(canvas, r_back, "[ESC / O] BACK", (mx, my), base_color=COLOR_CRIMSON)
        return {"back": r_back}

    name = getattr(joystick, "get_name", lambda: "Unknown")()
    guid = getattr(joystick, "get_guid", lambda: "")()
    c_type = profile.controller_type.upper() if profile else "GENERIC"
    
    info_str = f"DEVICE: {name}  |  TYPE: {c_type}  |  GUID: {guid[:16]}...  |  STATUS: CONNECTED"
    s_info = font_sub.render(info_str, True, COLOR_TEXT_DIM)
    canvas.blit(s_info, (36, 70))

    # Helper function to check button states
    def is_action_pressed(action_key: str) -> bool:
        if not profile or not joystick:
            return False
        raw_idx = profile.button_map.get(action_key, -1)
        if raw_idx >= 0:
            try:
                return bool(joystick.get_button(raw_idx))
            except Exception:
                return False
        return False

    def is_raw_pressed(btn_idx: int) -> bool:
        if not joystick or btn_idx < 0:
            return False
        try:
            return bool(joystick.get_button(btn_idx))
        except Exception:
            return False

    dpad = mapping_manager.get_dpad_input(joystick) if joystick else {"up": False, "down": False, "left": False, "right": False}

    # 2. Layout Dimensions (2 Main Panels: Diagram Left, Logical Telemetry Right)
    panel_y = 96
    panel_h = vh - panel_y - 100
    left_w = min(500, (vw - 84) // 2)
    right_w = (vw - 64) - left_w - 20
    diag_x = 32
    tele_x = diag_x + left_w + 20

    # =========================================================================
    # LEFT PANEL: INTERACTIVE VISUAL GAMEPAD DIAGRAM
    # =========================================================================
    diag_rect = pygame.Rect(diag_x, panel_y, left_w, panel_h)
    pygame.draw.rect(canvas, (14, 20, 32), diag_rect, border_radius=8)
    pygame.draw.rect(canvas, (35, 52, 78), diag_rect, 1, border_radius=8)

    diag_title = font_card.render("INTERACTIVE HARDWARE LAYOUT", True, COLOR_CYAN)
    canvas.blit(diag_title, (diag_x + 16, panel_y + 12))

    cx = diag_x + left_w // 2
    cy = panel_y + panel_h // 2 + 10

    # Controller chassis silhouette
    chassis_pts = [
        (cx - 190, cy - 60), (cx - 120, cy - 85), (cx + 120, cy - 85), (cx + 190, cy - 60),
        (cx + 210, cy + 50), (cx + 160, cy + 95), (cx + 80, cy + 60), (cx - 80, cy + 60),
        (cx - 160, cy + 95), (cx - 210, cy + 50)
    ]
    pygame.draw.polygon(canvas, (20, 28, 44), chassis_pts)
    pygame.draw.polygon(canvas, (45, 65, 95), chassis_pts, 2)

    # 1. Shoulder Buttons [L1] (FRONT BOTTOM) & [R1] (FRONT TOP)
    l1_idx = profile.button_map.get("front_bottom", 4) if profile else 4
    r1_idx = profile.button_map.get("front_top", 5) if profile else 5
    l1_pressed = is_raw_pressed(l1_idx) or is_action_pressed("cloak")
    r1_pressed = is_raw_pressed(r1_idx) or is_action_pressed("weapon_next")
    l1_col = COLOR_EMERALD if l1_pressed else (50, 70, 95)
    r1_col = COLOR_EMERALD if r1_pressed else (50, 70, 95)

    l1_rect = pygame.Rect(cx - 160, cy - 105, 80, 22)
    r1_rect = pygame.Rect(cx + 80, cy - 105, 80, 22)
    pygame.draw.rect(canvas, (30, 60, 45) if l1_pressed else (24, 34, 50), l1_rect, border_radius=5)
    pygame.draw.rect(canvas, l1_col, l1_rect, 2 if l1_pressed else 1, border_radius=5)
    pygame.draw.rect(canvas, (30, 60, 45) if r1_pressed else (24, 34, 50), r1_rect, border_radius=5)
    pygame.draw.rect(canvas, r1_col, r1_rect, 2 if r1_pressed else 1, border_radius=5)

    lbl_l1 = font_sub.render(f"L1 [B{l1_idx}]", True, l1_col)
    lbl_r1 = font_sub.render(f"R1 [B{r1_idx}]", True, r1_col)
    canvas.blit(lbl_l1, lbl_l1.get_rect(center=l1_rect.center))
    canvas.blit(lbl_r1, lbl_r1.get_rect(center=r1_rect.center))

    # 2. D-PAD Cross
    dpad_cx, dpad_cy = cx - 110, cy - 10
    d_arm = 24
    d_thickness = 18

    dpad_rects = {
        "up": (pygame.Rect(dpad_cx - d_thickness // 2, dpad_cy - d_arm - 8, d_thickness, d_arm), dpad["up"], "▲"),
        "down": (pygame.Rect(dpad_cx - d_thickness // 2, dpad_cy + 8, d_thickness, d_arm), dpad["down"], "▼"),
        "left": (pygame.Rect(dpad_cx - d_arm - 8, dpad_cy - d_thickness // 2, d_arm, d_thickness), dpad["left"], "◀"),
        "right": (pygame.Rect(dpad_cx + 8, dpad_cy - d_thickness // 2, d_arm, d_thickness), dpad["right"], "▶"),
    }
    pygame.draw.circle(canvas, (30, 42, 60), (dpad_cx, dpad_cy), 10)

    for d_dir, (dr, d_active, glyph) in dpad_rects.items():
        d_col = COLOR_EMERALD if d_active else (55, 75, 100)
        d_bg = (30, 60, 45) if d_active else (22, 32, 48)
        pygame.draw.rect(canvas, d_bg, dr, border_radius=3)
        pygame.draw.rect(canvas, d_col, dr, 2 if d_active else 1, border_radius=3)
        g_s = font_sub.render(glyph, True, d_col)
        canvas.blit(g_s, g_s.get_rect(center=dr.center))

    # 3. Center SELECT & START Buttons
    sel_idx = profile.button_map.get("sector_map", 8) if profile else 8
    sta_idx = profile.button_map.get("pause", 9) if profile else 9
    sel_pressed = is_raw_pressed(sel_idx) or is_action_pressed("sector_map")
    sta_pressed = is_raw_pressed(sta_idx) or is_action_pressed("pause")
    sel_col = COLOR_EMERALD if sel_pressed else (55, 75, 100)
    sta_col = COLOR_EMERALD if sta_pressed else (55, 75, 100)

    sel_rect = pygame.Rect(cx - 52, cy - 20, 46, 18)
    sta_rect = pygame.Rect(cx + 6, cy - 20, 46, 18)
    pygame.draw.rect(canvas, (30, 60, 45) if sel_pressed else (22, 32, 48), sel_rect, border_radius=4)
    pygame.draw.rect(canvas, sel_col, sel_rect, 2 if sel_pressed else 1, border_radius=4)
    pygame.draw.rect(canvas, (30, 60, 45) if sta_pressed else (22, 32, 48), sta_rect, border_radius=4)
    pygame.draw.rect(canvas, sta_col, sta_rect, 2 if sta_pressed else 1, border_radius=4)

    s_sel = font_sub.render("SELECT", True, sel_col)
    s_sta = font_sub.render("START", True, sta_col)
    canvas.blit(s_sel, s_sel.get_rect(center=sel_rect.center))
    canvas.blit(s_sta, s_sta.get_rect(center=sta_rect.center))

    # 4. Face Buttons Cluster
    face_cx, face_cy = cx + 110, cy - 10
    face_radius = 16
    offset = 32

    tri_idx = profile.button_map.get("ultimate", 0) if profile else 0
    cro_idx = profile.button_map.get("fire_primary", 2) if profile else 2
    cir_idx = profile.button_map.get("emp", 1) if profile else 1
    squ_idx = profile.button_map.get("roll", 3) if profile else 3

    tri_pressed = is_raw_pressed(tri_idx) or is_action_pressed("ultimate")
    cro_pressed = is_raw_pressed(cro_idx) or is_action_pressed("fire_primary")
    cir_pressed = is_raw_pressed(cir_idx) or is_action_pressed("emp")
    squ_pressed = is_raw_pressed(squ_idx) or is_action_pressed("roll")

    face_buttons = [
        ("▲", (face_cx, face_cy - offset), tri_pressed, COLOR_EMERALD, f"TRIANGLE [B{tri_idx}]"),
        ("■", (face_cx - offset, face_cy), squ_pressed, (244, 114, 182), f"SQUARE [B{squ_idx}]"),
        ("●", (face_cx + offset, face_cy), cir_pressed, COLOR_CRIMSON, f"CIRCLE [B{cir_idx}]"),
        ("✕", (face_cx, face_cy + offset), cro_pressed, COLOR_CYAN, f"CROSS [B{cro_idx}]"),
    ]

    for glyph, (bx, by), pressed, col, b_name in face_buttons:
        draw_col = COLOR_WHITE if pressed else col
        bg_col = col if pressed else (22, 32, 48)
        pygame.draw.circle(canvas, bg_col, (bx, by), face_radius)
        pygame.draw.circle(canvas, draw_col, (bx, by), face_radius, 2 if pressed else 1)
        lbl = font_card.render(glyph, True, (15, 23, 42) if pressed else col)
        canvas.blit(lbl, lbl.get_rect(center=(bx, by)))

    # =========================================================================
    # RIGHT PANEL: LOGICAL ACTION TELEMETRY & AXES (100% Matched to Profile)
    # =========================================================================
    tele_rect = pygame.Rect(tele_x, panel_y, right_w, panel_h)
    pygame.draw.rect(canvas, (14, 20, 32), tele_rect, border_radius=8)
    pygame.draw.rect(canvas, (35, 52, 78), tele_rect, 1, border_radius=8)

    tele_title = font_card.render("CANONICAL ACTIONS & TELEMETRY", True, COLOR_CYAN)
    canvas.blit(tele_title, (tele_x + 16, panel_y + 12))

    tele_items = [
        ("fire_primary", "PRIMARY FIRE (CONFIRM)"),
        ("emp", "EMP ATTACK (CANCEL / BACK)"),
        ("ultimate", "OVERDRIVE / ULTIMATE"),
        ("roll", "BARREL ROLL"),
        ("weapon_next", "WEAPON NEXT (TAP) / PREV (HOLD)"),
        ("cloak", "CLOAK (TAP) / DRONE CLASS (HOLD)"),
        ("sector_map", "SECTOR MAP / HANGAR BAY"),
        ("pause", "PAUSE MENU / FULLSCREEN (HOLD)"),
    ]

    card_y = panel_y + 38
    card_h = 34
    card_gap = 5

    for i, (action_key, desc) in enumerate(tele_items):
        cy_row = card_y + i * (card_h + card_gap)
        row_r = pygame.Rect(tele_x + 14, cy_row, right_w - 28, card_h)

        raw_idx = profile.button_map.get(action_key, -1) if profile else -1
        btn_pname = get_physical_button_name(raw_idx, profile.controller_type if profile else "generic_ps2")
        is_active = is_raw_pressed(raw_idx) or is_action_pressed(action_key)

        bg_col = (28, 48, 38) if is_active else (18, 24, 38)
        border_col = COLOR_EMERALD if is_active else (40, 55, 78)
        status_text = "PRESSED" if is_active else "RELEASED"
        status_color = COLOR_EMERALD if is_active else COLOR_TEXT_DIM

        pygame.draw.rect(canvas, bg_col, row_r, border_radius=5)
        pygame.draw.rect(canvas, border_col, row_r, 2 if is_active else 1, border_radius=5)

        lbl = font_sub.render(f"{btn_pname} [BTN {raw_idx}]", True, COLOR_WHITE if is_active else COLOR_CYAN)
        canvas.blit(lbl, (row_r.left + 10, row_r.top + 7))

        lbl_desc = font_sub.render(f"→ {desc}", True, (170, 185, 205))
        canvas.blit(lbl_desc, (row_r.left + 160, row_r.top + 7))

        s_stat = font_sub.render(status_text, True, status_color)
        canvas.blit(s_stat, (row_r.right - s_stat.get_width() - 10, row_r.top + 7))

    # =========================================================================
    # BOTTOM DIAGNOSTICS: RAW DETECTED BUTTON INDICES
    # =========================================================================
    raw_y = vh - 96
    lbl_raw = font_sub.render("RAW DETECTED BUTTON INDICES:", True, (148, 163, 184))
    canvas.blit(lbl_raw, (36, raw_y))

    try:
        n_btns = joystick.get_numbuttons()
    except Exception:
        n_btns = 0

    rx = 36
    for b_idx in range(min(n_btns, 16)):
        b_pressed = is_raw_pressed(b_idx)
        b_col = COLOR_EMERALD if b_pressed else (45, 58, 78)
        b_bg = (30, 60, 42) if b_pressed else (18, 24, 36)
        b_box = pygame.Rect(rx, raw_y + 20, 36, 26)
        pygame.draw.rect(canvas, b_bg, b_box, border_radius=4)
        pygame.draw.rect(canvas, b_col, b_box, 2 if b_pressed else 1, border_radius=4)
        s_idx = font_sub.render(str(b_idx), True, COLOR_WHITE if b_pressed else b_col)
        canvas.blit(s_idx, s_idx.get_rect(center=b_box.center))
        rx += 42

    # Back Navigation Button
    r_back = pygame.Rect(vw - 200, vh - 52, 168, 38)
    draw_button(canvas, r_back, "[ESC / O] BACK", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON)
    return {"back": r_back}


def draw_controller_settings_menu_ui(canvas: pygame.Surface, input_manager, mouse_pos: tuple[int, int] = None) -> dict:
    """Renders dedicated Controller Configuration screen (Deadzone, Sensitivity, Vibration, Rebind, Test)."""
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = _get_safe_mouse_pos(mouse_pos)

    panel_w, panel_h = 620, 560
    panel_rect = pygame.Rect(vw // 2 - panel_w // 2, vh // 2 - panel_h // 2, panel_w, panel_h)
    pygame.draw.rect(canvas, (14, 22, 38), panel_rect, border_radius=10)
    pygame.draw.rect(canvas, COLOR_CYAN, panel_rect, 2, border_radius=10)

    t_hdr = font_header.render("CONTROLLER CONFIGURATION", True, COLOR_CYAN)
    canvas.blit(t_hdr, t_hdr.get_rect(center=(vw // 2, panel_rect.top + 36)))

    js = input_manager.active_joystick if input_manager else None
    js_name = js.get_name() if js else "None Connected"
    conn_text = f"ACTIVE: {js_name} ({'CONNECTED' if js else 'DISCONNECTED'})"
    s_conn = font_card.render(conn_text, True, COLOR_EMERALD if js else COLOR_TEXT_DIM)
    canvas.blit(s_conn, s_conn.get_rect(center=(vw // 2, panel_rect.top + 70)))

    btn_w, btn_h = 460, 38
    bx = vw // 2 - btn_w // 2
    by = panel_rect.top + 100

    r_toggle = pygame.Rect(bx, by, btn_w, btn_h)
    r_deadzone = pygame.Rect(bx, by + 46, btn_w, btn_h)
    r_move_sens = pygame.Rect(bx, by + 92, btn_w, btn_h)
    r_aim_sens = pygame.Rect(bx, by + 138, btn_w, btn_h)
    r_vib = pygame.Rect(bx, by + 184, btn_w, btn_h)
    r_bind = pygame.Rect(bx, by + 230, btn_w, btn_h)
    r_test = pygame.Rect(bx, by + 276, btn_w, btn_h)
    r_reset = pygame.Rect(bx, by + 322, btn_w, btn_h)
    r_back = pygame.Rect(bx, panel_rect.bottom - 50, btn_w, 40)

    enabled_str = "ENABLED" if input_manager and input_manager.enabled else "DISABLED"
    dz_val = f"{int(input_manager.deadzone * 100)}%" if input_manager else "12%"
    move_sens_val = f"{input_manager.move_sensitivity:.1f}x" if input_manager else "1.0x"
    aim_sens_val = f"{input_manager.aim_sensitivity:.1f}x" if input_manager else "1.0x"
    vib_str = "ENABLED" if input_manager and input_manager.vibration_enabled else "DISABLED"

    draw_button(canvas, r_toggle, f"CONTROLLER INPUT: {enabled_str}", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_deadzone, f"ANALOG DEADZONE: {dz_val}  [← / →]", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD)
    draw_button(canvas, r_move_sens, f"MOVE SENSITIVITY: {move_sens_val}  [← / →]", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_aim_sens, f"AIM SENSITIVITY: {aim_sens_val}  [← / →]", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_vib, f"HAPTIC VIBRATION: {vib_str}", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)
    draw_button(canvas, r_bind, "CUSTOMIZE BUTTON MAPPINGS", (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD)
    draw_button(canvas, r_test, "TEST CONTROLLER INPUTS", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)
    draw_button(canvas, r_reset, "RESET CONTROLLER DEFAULTS", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON)
    draw_button(canvas, r_back, "[ESC / O] BACK TO SETTINGS", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)

    return {
        "toggle": r_toggle,
        "deadzone": r_deadzone,
        "move_sens": r_move_sens,
        "aim_sens": r_aim_sens,
        "vibration": r_vib,
        "bind": r_bind,
        "test": r_test,
        "reset": r_reset,
        "back": r_back
    }

