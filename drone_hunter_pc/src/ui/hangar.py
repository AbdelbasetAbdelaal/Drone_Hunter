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
    COLOR_WHITE, COLOR_CRIMSON, COLOR_HUD
)
from src.data.game_data import UPGRADE_COSTS, MAX_UPGRADE_LEVEL, DRONE_SKINS
from src.ui.font_manager import font_header, font_banner, font_card, font_button, font_sub
from src.ui.menus import draw_button


def draw_hangar_shop_ui(canvas: pygame.Surface, scrap: int, current_sector_idx: int, upgrade_levels: dict[str, int], mouse_pos: tuple[int, int] = None) -> dict:
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
    # Bottom Universal Navigation Bar
    # -------------------------------------------------------------------------
    nav_y = vh - 60
    r_back = pygame.Rect(26, nav_y - 2, 175, 48)
    r_skin = pygame.Rect(215, nav_y - 2, 220, 48)
    r_settings = pygame.Rect(450, nav_y - 2, 150, 48)
    r_exit = pygame.Rect(vw - 160, nav_y - 2, 134, 48)

    draw_button(canvas, r_back, "[ESC] BACK TO MAP", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_skin, "[C] CYCLE DRONE SKIN", (mx, my), base_color=COLOR_EMERALD, text_color=COLOR_EMERALD)
    draw_button(canvas, r_settings, "[S] SETTINGS", (mx, my), base_color=COLOR_CYAN)
    draw_button(canvas, r_exit, "[Q] QUIT", (mx, my), base_color=COLOR_CRIMSON, text_color=COLOR_CRIMSON)

    return {
        "back": r_back,
        "skin": r_skin,
        "settings": r_settings,
        "exit": r_exit,
        "upgrades": item_rects
    }

