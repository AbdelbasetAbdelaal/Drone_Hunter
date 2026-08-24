"""
================================================================================
                    DRONE HUNTER 2D - HANGAR & WEAPONS BAY
================================================================================
Hangar upgrade shop, active chassis showcase, and loadout interface.
Provides clean 2-column responsive layout, live animated chassis preview,
weapon loadout status, and controller-aware navigation.
"""

import math
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_EMERALD,
    COLOR_WHITE, COLOR_CRIMSON, COLOR_HUD, COLOR_MAGENTA, COLOR_TEXT_DIM
)
from src.data.game_data import (
    UPGRADE_COSTS, MAX_UPGRADE_LEVEL,
    WEAPON_DEFS, WEAPON_UPGRADES, WEAPON_UNLOCK_COSTS, get_drone_class_by_id
)
from src.ui.font_manager import font_header, font_banner, font_card, font_button, font_sub
from src.ui.menus import draw_button


def draw_hangar_shop_ui(
    canvas: pygame.Surface, scrap: int, current_sector_idx: int,
    upgrade_levels: dict[str, int], mouse_pos: tuple[int, int] = None,
    player=None, weapon_upgrades: dict = None, unlocked_weapons: list = None,
    total_score: int = 0, selected_index: int = None,
    input_manager=None
) -> dict:
    """Renders polished, responsive 2-column Hangar & Upgrade Bay."""
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = mouse_pos if mouse_pos is not None else pygame.mouse.get_pos()

    is_controller = False
    if input_manager and getattr(input_manager, "active_device", "") in ("gamepad", "joystick"):
        is_controller = True

    # 1. Safe layout margins
    pad_x = max(24, int(vw * 0.025))
    pad_y = max(14, int(vh * 0.02))
    content_w = vw - pad_x * 2
    footer_h = 44
    header_h = 46

    # 2. Header Bar
    header_rect = pygame.Rect(pad_x, pad_y, content_w, header_h)
    pygame.draw.rect(canvas, (14, 22, 38), header_rect, border_radius=8)
    pygame.draw.rect(canvas, COLOR_CYAN, header_rect, 2, border_radius=8)

    t_hdr = font_header.render("DRONE HANGAR & UPGRADE BAY", True, COLOR_CYAN)
    canvas.blit(t_hdr, (pad_x + 18, pad_y + 10))

    # Scrap pill on top right
    scrap_txt = font_banner.render(f"SCRAP: {scrap:,}", True, COLOR_GOLD)
    scrap_rect = pygame.Rect(header_rect.right - scrap_txt.get_width() - 32, pad_y + 8, scrap_txt.get_width() + 24, 30)
    pygame.draw.rect(canvas, (30, 41, 59), scrap_rect, border_radius=6)
    pygame.draw.rect(canvas, COLOR_GOLD, scrap_rect, 1, border_radius=6)
    canvas.blit(scrap_txt, (scrap_rect.left + 12, scrap_rect.top + 3))

    # 3. Two-Column Layout Calculations
    col_gap = 20
    col_w = (content_w - col_gap) // 2
    top_y = header_rect.bottom + 12
    avail_h = vh - top_y - footer_h - pad_y - 12

    # =========================================================================
    # LEFT COLUMN: SYSTEM UPGRADES GRID (4 Vertical Cards)
    # =========================================================================
    left_x = pad_x
    upg_title = font_card.render("CYBERNETIC SYSTEMS UPGRADES", True, COLOR_CYAN)
    canvas.blit(upg_title, (left_x + 4, top_y))

    items = [
        ("1", "hull", "HULL INTEGRITY", "HP", COLOR_EMERALD, lambda lvl: f"+25 HP ({225 + (lvl-1)*25} → {225 + (lvl)*25} HP)"),
        ("2", "energy", "ENERGY CORE OUTPUT", "NRG", COLOR_CYAN, lambda lvl: f"+15 NRG ({100 + (lvl-1)*15} → {100 + (lvl)*15} NRG)"),
        ("3", "weapon", "WEAPON SYSTEM BOOST", "DMG", COLOR_GOLD, lambda lvl: f"+5% DMG ({100 + (lvl-1)*5}% → {100 + (lvl)*5}%)"),
        ("4", "mobility", "THRUSTER MOBILITY", "SPD", COLOR_WHITE, lambda lvl: f"+5% SPD ({100 + (lvl-1)*5}% → {100 + (lvl)*5}%)")
    ]

    card_y_start = top_y + 26
    card_spacing = 8
    card_h = max(70, min(86, (avail_h - 26 - card_spacing * 3) // 4))
    item_rects = {}

    for idx, (key_num, upg_id, upg_name, tag, color, stat_func) in enumerate(items):
        cy = card_y_start + idx * (card_h + card_spacing)
        lvl = upgrade_levels.get(upg_id, 1)
        max_lvl = MAX_UPGRADE_LEVEL
        cost = UPGRADE_COSTS.get(lvl, 999999)

        card_rect = pygame.Rect(left_x, cy, col_w, card_h)
        is_hover = card_rect.collidepoint(mx, my) or (selected_index == idx)
        can_afford = (scrap >= cost) and (lvl < max_lvl)

        bg_col = (26, 42, 68) if is_hover else ((18, 26, 42) if can_afford else (12, 16, 26))
        border_col = COLOR_WHITE if is_hover else (color if can_afford else (45, 58, 78))
        pygame.draw.rect(canvas, bg_col, card_rect, border_radius=6)
        pygame.draw.rect(canvas, border_col, card_rect, 2 if is_hover else 1, border_radius=6)
        item_rects[upg_id] = card_rect

        # Left system tag icon box
        tag_w = 44
        tag_rect = pygame.Rect(left_x + 8, cy + 8, tag_w, card_h - 16)
        pygame.draw.rect(canvas, (20, 30, 48), tag_rect, border_radius=4)
        pygame.draw.rect(canvas, color, tag_rect, 1, border_radius=4)
        tag_lbl = font_sub.render(tag, True, color)
        canvas.blit(tag_lbl, tag_lbl.get_rect(center=tag_rect.center))

        # Title & Key Prompt
        name_x = tag_rect.right + 12
        lbl_key = f"[{key_num}]" if not is_controller else f"[D-PAD {idx+1}]"
        lbl_title = font_card.render(f"{lbl_key} {upg_name}", True, COLOR_WHITE if is_hover else color)
        canvas.blit(lbl_title, (name_x, cy + 8))

        # Level & Cost / Stat
        if lvl >= max_lvl:
            txt_lvl = font_sub.render(f"LEVEL {lvl}/{max_lvl} (MAX LEVEL REACHED)", True, COLOR_EMERALD)
            canvas.blit(txt_lvl, (name_x, cy + 30))
        else:
            txt_stat = font_sub.render(stat_func(lvl), True, (190, 205, 225))
            canvas.blit(txt_stat, (name_x, cy + 30))

            cost_lbl = font_sub.render(f"COST: {cost:,} SCRAP", True, COLOR_GOLD if can_afford else (148, 163, 184))
            canvas.blit(cost_lbl, (name_x, cy + 48))

        # Progress bar on the right
        bar_w = 110
        bar_h = 8
        bar_x = card_rect.right - bar_w - 14
        bar_y = cy + (card_h - bar_h) // 2
        pygame.draw.rect(canvas, (25, 35, 52), (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        fill_w = int(bar_w * (lvl / max_lvl))
        if fill_w > 0:
            fill_col = COLOR_EMERALD if lvl >= max_lvl else color
            pygame.draw.rect(canvas, fill_col, (bar_x, bar_y, fill_w, bar_h), border_radius=3)
        pygame.draw.rect(canvas, (51, 65, 85), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

    # =========================================================================
    # RIGHT COLUMN: ACTIVE CHASSIS SHOWCASE + WEAPONS
    # =========================================================================
    right_x = pad_x + col_w + col_gap
    class_id = getattr(player, "drone_class_id", "striker") if player else "striker"
    c_info = get_drone_class_by_id(class_id)

    # 1. Active Chassis Profile Card (Large Prominent Preview)
    chassis_h = 168
    chassis_rect = pygame.Rect(right_x, top_y, col_w, chassis_h)
    pygame.draw.rect(canvas, (14, 22, 36), chassis_rect, border_radius=8)
    pygame.draw.rect(canvas, (40, 60, 90), chassis_rect, 1, border_radius=8)

    # Substantially Larger Live Emissive Drone Preview Box
    preview_box_w = 140
    preview_rect = pygame.Rect(right_x + 10, top_y + 10, preview_box_w, chassis_h - 20)
    pygame.draw.rect(canvas, (10, 16, 28), preview_rect, border_radius=6)
    pygame.draw.rect(canvas, COLOR_CYAN, preview_rect, 1, border_radius=6)

    # Ambient animated radar rings in preview box
    p_cx, p_cy = preview_rect.center
    t_now = pygame.time.get_ticks() * 0.003 if pygame.get_init() else 0.0
    radar_r = int(36 + 8 * math.sin(t_now))
    pygame.draw.circle(canvas, (30, 70, 110, 90), (p_cx, p_cy), max(15, radar_r), 1)
    pygame.draw.circle(canvas, (20, 45, 80, 60), (p_cx, p_cy), max(25, radar_r + 15), 1)

    # Corner tactical reticles in preview
    ret_len = 8
    pygame.draw.line(canvas, COLOR_CYAN, (preview_rect.left + 4, preview_rect.top + 4), (preview_rect.left + 4 + ret_len, preview_rect.top + 4), 1)
    pygame.draw.line(canvas, COLOR_CYAN, (preview_rect.left + 4, preview_rect.top + 4), (preview_rect.left + 4, preview_rect.top + 4 + ret_len), 1)
    pygame.draw.line(canvas, COLOR_CYAN, (preview_rect.right - 5, preview_rect.bottom - 5), (preview_rect.right - 5 - ret_len, preview_rect.bottom - 5), 1)
    pygame.draw.line(canvas, COLOR_CYAN, (preview_rect.right - 5, preview_rect.bottom - 5), (preview_rect.right - 5, preview_rect.bottom - 5 - ret_len), 1)

    # Draw player chassis sprite at large scale
    try:
        from src.rendering.sprite_manager import get_sprite_manager
        sm = get_sprite_manager()
        class_idx_map = {
            "striker": 0, "01_striker": 0,
            "interceptor": 1, "phantom": 1, "02_phantom": 1,
            "assault": 2, "titan": 2, "03_titan": 2,
            "arc": 3, "specter": 3, "velocity": 3, "04_velocity": 3,
            "command": 4, "tempest": 4, "aegis_quad": 4, "05_aegis_quad": 4,
        }
        skin_idx = class_idx_map.get(class_id, 0)
        drone_surf = sm.get_player_sprite(skin_idx=skin_idx, target_size=(114, 100))
        canvas.blit(drone_surf, drone_surf.get_rect(center=(p_cx, p_cy)))
    except Exception:
        pygame.draw.circle(canvas, COLOR_CYAN, (p_cx, p_cy), 28)

    # Chassis Info & Tactical Telemetry
    info_x = preview_rect.right + 14
    t_class_name = font_card.render(f"{c_info['name'].upper()} — {c_info['title']}", True, COLOR_CYAN)
    t_role_txt = font_sub.render(f"ROLE: {c_info['role'].upper()}", True, COLOR_GOLD)
    canvas.blit(t_class_name, (info_x, top_y + 10))
    canvas.blit(t_role_txt, (info_x, top_y + 32))

    # Core Stats Grid Chips
    spd_val = int(420.0 * c_info['speed_mult'])
    acc_val = int(3600.0 * c_info['accel_mult'])
    hp_val = c_info['max_health']
    arm_val = c_info.get('armor', 0)

    stat_chips = [
        f"SPEED: {spd_val} px/s",
        f"ACCEL: {acc_val} px/s²",
        f"HULL: {hp_val} HP",
        f"ARMOR: {arm_val}"
    ]
    for s_i, stat_str in enumerate(stat_chips):
        sc_x = info_x + (s_i % 2) * 155
        sc_y = top_y + 58 + (s_i // 2) * 22
        s_lbl = font_sub.render(stat_str, True, (170, 185, 205))
        canvas.blit(s_lbl, (sc_x, sc_y))

    # 2. Weapon Loadout Panel
    weap_y = chassis_rect.bottom + 10
    weap_title = font_card.render("TACTICAL WEAPONS LOADOUT", True, COLOR_CYAN)
    canvas.blit(weap_title, (right_x + 4, weap_y))

    weapon_upgrades = weapon_upgrades or {}
    unlocked_weapons = unlocked_weapons or ["pulse", "scatter", "missile"]
    slot_names = ["PRIMARY", "SECONDARY", "HEAVY", "SPECIAL"]
    slot_colors = [COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_MAGENTA]
    weapon_slot_rects = {}

    w_card_y = weap_y + 22
    w_row_h = 30
    w_row_gap = 4

    for idx_w, w_id in enumerate(c_info.get("weapons", [])):
        if idx_w >= 4:
            break
        w_d = WEAPON_DEFS.get(w_id, {})
        w_upg = WEAPON_UPGRADES.get(w_id, {})
        w_lvl = weapon_upgrades.get(w_id, 0)
        is_unlocked = w_id in unlocked_weapons
        s_tag = slot_names[idx_w] if idx_w < len(slot_names) else f"SLOT {idx_w+1}"
        slot_color = slot_colors[idx_w] if idx_w < len(slot_colors) else COLOR_WHITE

        slot_y = w_card_y + idx_w * (w_row_h + w_row_gap)
        slot_rect = pygame.Rect(right_x, slot_y, col_w, w_row_h)
        weapon_slot_rects[idx_w] = slot_rect

        bg = (18, 28, 44) if is_unlocked else (12, 16, 24)
        border = slot_color if is_unlocked else (45, 55, 75)
        txt = slot_color if is_unlocked else (100, 115, 135)

        pygame.draw.rect(canvas, bg, slot_rect, border_radius=5)
        pygame.draw.rect(canvas, border, slot_rect, 1, border_radius=5)

        name_txt = font_sub.render(f"[{s_tag}] {w_d.get('name', w_id.upper())}", True, txt)
        canvas.blit(name_txt, (right_x + 10, slot_y + 6))

        if is_unlocked:
            max_wlvl = w_upg.get("max_level", 5)
            cost = int(w_upg.get("cost_base", 200) * (w_upg.get("cost_mult", 1.6) ** w_lvl)) if w_lvl < max_wlvl else None
            upg_txt = f"LVL {w_lvl}/{max_wlvl}"
            if w_lvl < max_wlvl and cost is not None:
                upg_txt += f"  (UPGRADE: {cost:,} SCRAP)"
            elif w_lvl >= max_wlvl:
                upg_txt += "  (MAX)"
            t_upg = font_sub.render(upg_txt, True, COLOR_GOLD if (w_lvl < max_wlvl and scrap >= cost and cost is not None) else (148, 163, 184))
            canvas.blit(t_upg, (slot_rect.right - t_upg.get_width() - 10, slot_y + 6))
        else:
            unlock_cost = WEAPON_UNLOCK_COSTS.get(w_id, 999999)
            t_lock = font_sub.render(f"UNLOCK: {unlock_cost:,} SCRAP", True, COLOR_CRIMSON if scrap < unlock_cost else COLOR_GOLD)
            canvas.blit(t_lock, (slot_rect.right - t_lock.get_width() - 10, slot_y + 6))

    # =========================================================================
    # FOOTER: DEVICE-AWARE NAVIGATION BAR
    # =========================================================================
    nav_y = vh - footer_h - pad_y
    n_nav_btns = 4
    nav_gap = 10
    btn_w = (content_w - (n_nav_btns - 1) * nav_gap) // n_nav_btns

    r_back = pygame.Rect(pad_x, nav_y, btn_w, footer_h)
    r_drone = pygame.Rect(pad_x + btn_w + nav_gap, nav_y, btn_w, footer_h)
    r_settings = pygame.Rect(pad_x + 2 * (btn_w + nav_gap), nav_y, btn_w, footer_h)
    r_exit = pygame.Rect(pad_x + 3 * (btn_w + nav_gap), nav_y, btn_w, footer_h)

    lbl_back = "[O] BACK" if is_controller else "[ESC] BACK"
    lbl_drone = "[FRONT BOTTOM] CHASSIS" if is_controller else "[C] CHASSIS"
    lbl_settings = "[START] SETTINGS" if is_controller else "[S] SETTINGS"
    lbl_exit = "[SELECT] QUIT" if is_controller else "[Q] QUIT"

    draw_button(canvas, r_back, lbl_back, (mx, my), base_color=COLOR_CYAN, is_selected=(selected_index == 4))
    draw_button(canvas, r_drone, lbl_drone, (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD, is_selected=(selected_index == 5))
    draw_button(canvas, r_settings, lbl_settings, (mx, my), base_color=COLOR_GOLD, text_color=COLOR_GOLD, is_selected=(selected_index == 6))
    draw_button(canvas, r_exit, lbl_exit, (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON, is_selected=(selected_index == 7))

    return {
        "back": r_back,
        "drone": r_drone,
        "chassis": r_drone,
        "chassis_card": chassis_rect,
        "preview_box": preview_rect,
        "settings": r_settings,
        "exit": r_exit,
        "upgrades": item_rects,
        "weapon_slots": weapon_slot_rects,
    }
