"""
================================================================================
                    DRONE HUNTER 2D - HANGAR & WEAPONS BAY
================================================================================
Hangar upgrade shop and drone skin customizer interface.
Phase 4: Simplified progression system.
"""

import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_EMERALD,
    COLOR_WHITE, COLOR_CRIMSON, COLOR_HUD, COLOR_MAGENTA
)
from src.data.game_data import UPGRADE_COSTS, MAX_UPGRADE_LEVEL, DRONE_SKINS, DRONE_SKIN_UNLOCKS, WEAPON_DEFS, WEAPON_UPGRADES, WEAPON_UNLOCK_COSTS
from src.ui.font_manager import font_header, font_banner, font_card, font_button, font_sub
from src.ui.menus import draw_button


def draw_hangar_shop_ui(canvas: pygame.Surface, scrap: int, current_sector_idx: int, upgrade_levels: dict[str, int], mouse_pos: tuple[int, int] = None, player=None, weapon_upgrades: dict = None, unlocked_weapons: list = None, unlocked_skins: list = None, total_score: int = 0) -> dict:
    canvas.fill((8, 12, 22))
    vw, vh = canvas.get_size()
    mx, my = mouse_pos if mouse_pos is not None else pygame.mouse.get_pos()

    # Top Header
    header_rect = pygame.Rect(30, 14, vw - 60, 52)
    pygame.draw.rect(canvas, (14, 22, 38), header_rect, border_radius=8)
    pygame.draw.rect(canvas, COLOR_CYAN, header_rect, 2, border_radius=8)
    
    t_hdr = font_header.render("DRONE HANGAR & UPGRADE BAY", True, COLOR_CYAN)
    scrap_hdr = font_banner.render(f"SCRAP: {scrap:,}", True, COLOR_GOLD)
    canvas.blit(t_hdr, (48, 18))
    canvas.blit(scrap_hdr, (vw - 250, 26))

    items = [
        ("1", "hull", "HULL INTEGRITY", COLOR_EMERALD, lambda lvl: f"+25 HP -> {225 + (lvl)*25} Max HP"),
        ("2", "energy", "ENERGY CORE OUTPUT", COLOR_CYAN, lambda lvl: f"+15 NRG -> {100 + (lvl)*15} Max Energy"),
        ("3", "weapon", "WEAPON SYSTEM BOOST", COLOR_GOLD, lambda lvl: f"+5% DMG -> {100 + (lvl)*5}% Effectiveness"),
        ("4", "mobility", "THRUSTER MOBILITY", COLOR_WHITE, lambda lvl: f"+5% SPD -> {100 + (lvl)*5}% Flight Speed")
    ]

    card_w, card_h = 590, 100
    item_rects = {}

    for idx, (key_num, upg_id, upg_name, color, stat_func) in enumerate(items):
        col_idx = idx % 2
        row_idx = idx // 2
        
        cx = 30 + col_idx * 610
        cy = 86 + row_idx * 118
        
        lvl = upgrade_levels.get(upg_id, 1)
        max_lvl = MAX_UPGRADE_LEVEL
        cost = UPGRADE_COSTS.get(lvl, 999999)

        card_rect = pygame.Rect(cx, cy, card_w, card_h)
        is_hover = card_rect.collidepoint(mx, my)
        
        can_afford = (scrap >= cost) and (lvl < max_lvl)
        
        if not can_afford and lvl < max_lvl:
            bg_col = (18, 22, 32) if is_hover else (12, 16, 24)
            border_col = (50, 60, 75)
            txt_col = (130, 145, 165)
        else:
            bg_col = (24, 40, 65) if is_hover else (15, 24, 40)
            border_col = COLOR_WHITE if is_hover else color
            txt_col = COLOR_WHITE if is_hover else color

        pygame.draw.rect(canvas, bg_col, card_rect, border_radius=8)
        pygame.draw.rect(canvas, border_col, card_rect, 2 if is_hover else 1, border_radius=8)
        item_rects[upg_id] = card_rect

        lbl = font_button.render(f"[{key_num}] {upg_name}", True, txt_col)
        canvas.blit(lbl, (cx + 16, cy + 12))

        if lvl >= max_lvl:
            txt_lvl = font_sub.render(f"LEVEL {lvl}/{max_lvl} (MAX LEVEL REACHED)", True, COLOR_EMERALD)
            txt_stat = font_sub.render(f"CURRENT: {stat_func(lvl - 1).split('->')[1].strip()}", True, COLOR_EMERALD)
        else:
            txt_lvl = font_sub.render(f"LV {lvl} -> LV {lvl+1}   |   Upgrade Cost: {cost:,} SCRAP", True, COLOR_GOLD if can_afford else (130, 140, 155))
            txt_stat = font_sub.render(stat_func(lvl), True, txt_col)
            
        canvas.blit(txt_lvl, (cx + 16, cy + 42))
        canvas.blit(txt_stat, (cx + 16, cy + 68))

        # Progress bar
        bar_w = 180
        bar_x = cx + card_w - bar_w - 18
        pygame.draw.rect(canvas, (25, 35, 50), (bar_x, cy + 44, bar_w, 14), border_radius=4)
        fill_w = int(bar_w * (lvl / max_lvl))
        if fill_w > 0:
            fill_col = COLOR_EMERALD if lvl >= max_lvl else color
            pygame.draw.rect(canvas, fill_col, (bar_x, cy + 44, fill_w, 14), border_radius=4)

    # -------------------------------------------------------------------------
    # Drone Combat Class Showcase Profile Card
    # -------------------------------------------------------------------------
    from src.data.game_data import get_drone_class_by_id, DRONE_SKINS
    class_id = getattr(player, "drone_class_id", "striker") if player else "striker"
    c_info = get_drone_class_by_id(class_id)

    profile_rect = pygame.Rect(30, 330, vw - 60, 260)
    pygame.draw.rect(canvas, (12, 18, 30), profile_rect, border_radius=8)
    pygame.draw.rect(canvas, (30, 48, 75), profile_rect, 1, border_radius=8)

    # Class Header
    t_class_hdr = font_card.render(f"ACTIVE CHASSIS: {c_info['name']} — {c_info['title']}", True, COLOR_CYAN)
    t_role = font_sub.render(f"COMBAT IDENTITY: {c_info['role']}", True, COLOR_GOLD)
    t_desc = font_sub.render(c_info['description'], True, (180, 195, 215))

    canvas.blit(t_class_hdr, (50, 346))
    canvas.blit(t_role, (50, 376))
    canvas.blit(t_desc, (50, 404))

    # Stats Summary
    spd_val = int(420.0 * c_info['speed_mult'])
    acc_val = int(3600.0 * c_info['accel_mult'])
    hp_val = c_info['max_health']
    arm_val = c_info.get('armor', 0)

    t_stats = font_sub.render(
        f"FLIGHT SPEED: {spd_val} px/s  |  ACCELERATION: {acc_val} px/s²  |  HULL: {hp_val} HP  |  ARMOR: {arm_val}",
        True, COLOR_WHITE
    )
    canvas.blit(t_stats, (50, 438))

    # Stats Summary
    spd_val = int(420.0 * c_info['speed_mult'])
    acc_val = int(3600.0 * c_info['accel_mult'])
    hp_val = c_info['max_health']
    arm_val = c_info.get('armor', 0)

    t_stats = font_sub.render(
        f"FLIGHT SPEED: {spd_val} px/s  |  ACCELERATION: {acc_val} px/s²  |  HULL: {hp_val} HP  |  ARMOR: {arm_val}",
        True, COLOR_WHITE
    )
    canvas.blit(t_stats, (50, 438))

    weapon_upgrades = weapon_upgrades or {}
    unlocked_weapons = unlocked_weapons or ["pulse", "scatter", "missile"]

    slot_names = ["PRIMARY", "SECONDARY", "HEAVY", "SPECIAL"]
    slot_colors = [COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_MAGENTA]
    weapon_slot_rects = {}

    for idx_w, w_id in enumerate(c_info.get("weapons", [])):
        if idx_w >= 4:
            break
        w_d = WEAPON_DEFS.get(w_id, {})
        w_upg = WEAPON_UPGRADES.get(w_id, {})
        w_lvl = weapon_upgrades.get(w_id, 0)
        is_unlocked = w_id in unlocked_weapons
        s_tag = slot_names[idx_w] if idx_w < len(slot_names) else f"SLOT {idx_w+1}"
        slot_color = slot_colors[idx_w] if idx_w < len(slot_colors) else COLOR_WHITE

        slot_y = 468 + idx_w * 38
        slot_rect = pygame.Rect(30, slot_y, vw - 60, 34)
        is_slot_hover = slot_rect.collidepoint(mx, my)
        weapon_slot_rects[idx_w] = slot_rect

        bg = (18, 24, 38) if is_unlocked else (12, 16, 24)
        border = slot_color if is_unlocked else (50, 60, 75)
        txt = slot_color if is_unlocked else (80, 90, 110)
        if is_slot_hover and is_unlocked:
            bg = (24, 36, 58)
            border = COLOR_WHITE
            txt = COLOR_WHITE

        pygame.draw.rect(canvas, bg, slot_rect, border_radius=6)
        pygame.draw.rect(canvas, border, slot_rect, 1, border_radius=6)

        name_txt = font_sub.render(f"[{idx_w+1}] {s_tag}: {w_d.get('name', w_id.upper())}", True, txt)
        canvas.blit(name_txt, (48, slot_y + 8))

        if is_unlocked:
            max_wlvl = w_upg.get("max_level", 5)
            cost = int(w_upg.get("cost_base", 200) * (w_upg.get("cost_mult", 1.6) ** w_lvl)) if w_lvl < max_wlvl else None
            upg_txt = f" LVL {w_lvl}/{max_wlvl}"
            if w_lvl < max_wlvl and cost is not None:
                upg_txt += f"  UPGRADE: {cost:,} SCRAP"
            elif w_lvl >= max_wlvl:
                upg_txt += "  (MAX)"
            t_upg = font_sub.render(upg_txt, True, COLOR_GOLD if (w_lvl < max_wlvl and scrap >= cost and cost is not None) else (130, 140, 155))
            canvas.blit(t_upg, (vw - 320, slot_y + 8))
        else:
            unlock_cost = WEAPON_UNLOCK_COSTS.get(w_id, 999999)
            t_lock = font_sub.render(f"UNLOCK: {unlock_cost:,} SCRAP", True, COLOR_CRIMSON if scrap < unlock_cost else COLOR_GOLD)
            canvas.blit(t_lock, (vw - 320, slot_y + 8))


    # Controls hint
    t_hint = font_sub.render("PRESS [C] CYCLE CHASSIS   •   PRESS [V] CYCLE VISUAL SKIN   •   PRESS [1-4] SELECT WEAPON", True, (130, 145, 165))
    canvas.blit(t_hint, (50, 508))
    
    # Skin Selection Row
    unlocked_skins = unlocked_skins if unlocked_skins is not None else [0]
    total_score = total_score if total_score is not None else 0
    skin_row_y = 468 + len(c_info.get("weapons", [])) * 38 + 16
    t_skin_hdr = font_sub.render("DRONE SKINS:", True, COLOR_CYAN)
    canvas.blit(t_skin_hdr, (30, skin_row_y))

    skin_btns = {}
    for idx, skin in enumerate(DRONE_SKINS):
        sx = 130 + idx * 118
        sy = skin_row_y - 2
        sr = pygame.Rect(sx, sy, 110, 30)
        is_unlocked = skin["id"] in unlocked_skins
        is_active = player and getattr(player, "skin_theme", 0) == skin["id"]
        req_score = DRONE_SKIN_UNLOCKS.get(skin["id"], {}).get("score", 0)
        has_met = total_score >= req_score

        if is_active:
            bg_col = skin["primary_color"]
            border_col = COLOR_WHITE
            txt_col = COLOR_WHITE
        elif is_unlocked:
            bg_col = (20, 30, 50)
            border_col = skin["primary_color"]
            txt_col = skin["primary_color"]
        else:
            bg_col = (12, 16, 24)
            border_col = (50, 60, 75)
            txt_col = (80, 90, 110)

        pygame.draw.rect(canvas, bg_col, sr, border_radius=5)
        pygame.draw.rect(canvas, border_col, sr, 1 if not is_active else 2, border_radius=5)
        skin_btns[skin["id"]] = sr

        if is_unlocked:
            label = "EQUIPPED" if is_active else skin["name"][:14]
            t_label = font_sub.render(label, True, txt_col)
            canvas.blit(t_label, (sx + 6, sy + 7))
            if not is_active:
                t_unlock = font_sub.render("UNLOCKED", True, COLOR_EMERALD)
                canvas.blit(t_unlock, (sx + 6, sy + 18))
        else:
            t_lock = font_sub.render("LOCKED", True, txt_col)
            canvas.blit(t_lock, (sx + 6, sy + 4))
            req_str = f"{req_score:,} PTS"
            t_req = font_sub.render(req_str, True, COLOR_CRIMSON if not has_met else COLOR_GOLD)
            canvas.blit(t_req, (sx + 6, sy + 18))
    
    # Render active visual skin info
    if player:
        skin_id = getattr(player, "skin_theme", 0)
        skin_data = DRONE_SKINS[skin_id] if skin_id < len(DRONE_SKINS) else DRONE_SKINS[0]
        t_skin = font_sub.render(f"ACTIVE SKIN: {skin_data['name']}", True, skin_data['primary_color'])
        canvas.blit(t_skin, (vw - 320, 346))

    # -------------------------------------------------------------------------
    # Bottom Universal Navigation Bar
    # -------------------------------------------------------------------------
    nav_y = vh - 60
    r_back = pygame.Rect(26, nav_y - 2, 175, 48)
    r_skin = pygame.Rect(215, nav_y - 2, 235, 48)
    r_settings = pygame.Rect(465, nav_y - 2, 150, 48)
    r_exit = pygame.Rect(vw - 160, nav_y - 2, 134, 48)

    draw_button(canvas, r_back, "[ESC] BACK TO MAP", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_skin, "[C] CYCLE DRONE CLASS", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)
    draw_button(canvas, r_settings, "[S] SETTINGS", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_exit, "[Q] QUIT", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON)

    return {
        "back": r_back,
        "skin": r_skin,
        "settings": r_settings,
        "exit": r_exit,
        "upgrades": item_rects,
        "weapon_slots": weapon_slot_rects
    }


