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
    COLOR_WHITE, COLOR_HUD
)
from src.data.game_data import UPGRADE_COSTS, MAX_UPGRADE_LEVEL
from src.ui.font_manager import font_title, font_banner, font_card
from src.ui.menus import draw_exit_button

def draw_hangar_shop_ui(canvas: pygame.Surface, scrap: int, current_sector_idx: int, upgrade_levels: dict[str, int]) -> tuple[pygame.Rect, pygame.Rect, dict]:
    canvas.fill((10, 15, 26))

    header_rect = pygame.Rect(30, 16, SCREEN_WIDTH - 60, 52)
    pygame.draw.rect(canvas, (15, 23, 42), header_rect, border_radius=6)
    pygame.draw.rect(canvas, COLOR_CYAN, header_rect, 2, border_radius=6)
    
    t_hdr = font_title.render("DRONE HANGAR & UPGRADE BAY", True, COLOR_CYAN)
    scrap_hdr = font_banner.render(f"SCRAP: {scrap:,}", True, COLOR_GOLD)
    canvas.blit(t_hdr, (48, 18))
    canvas.blit(scrap_hdr, (SCREEN_WIDTH - 300, 28))

    items = [
        ("1", "hull", "HULL: Max Integrity", COLOR_EMERALD, lambda lvl: f"+25 HP -> {225 + (lvl)*25} HP"),
        ("2", "energy", "ENERGY: Core Output", COLOR_CYAN, lambda lvl: f"+15 NRG -> {100 + (lvl)*15} NRG"),
        ("3", "weapon", "WEAPONS: Effectiveness", COLOR_GOLD, lambda lvl: f"+5% DMG -> {100 + (lvl)*5}%"),
        ("4", "mobility", "MOBILITY: Thrust Agility", COLOR_WHITE, lambda lvl: f"+5% SPD -> {100 + (lvl)*5}%")
    ]

    card_w, card_h = 570, 90
    mx, my = pygame.mouse.get_pos()
    item_rects = {}

    for idx, (key_num, upg_id, upg_name, color, stat_func) in enumerate(items):
        col_idx = idx % 2
        row_idx = idx // 2
        
        cx = 35 + col_idx * 595
        cy = 100 + row_idx * 110
        
        lvl = upgrade_levels.get(upg_id, 1)
        max_lvl = MAX_UPGRADE_LEVEL
        cost = UPGRADE_COSTS.get(lvl, 999999)

        card_rect = pygame.Rect(cx, cy, card_w, card_h)
        is_hover = card_rect.collidepoint(mx, my)
        
        can_afford = (scrap >= cost) and (lvl < max_lvl)
        
        if not can_afford and lvl < max_lvl:
            # Insufficient scrap state
            bg_col = (20, 20, 20, 240) if is_hover else (10, 10, 10, 240)
            border_col = (100, 100, 100)
            txt_col = (150, 150, 150)
        else:
            bg_col = (20, 30, 52, 240) if is_hover else (15, 23, 42, 240)
            border_col = COLOR_WHITE if is_hover else color
            txt_col = COLOR_WHITE if is_hover else color

        pygame.draw.rect(canvas, bg_col, card_rect, border_radius=8)
        pygame.draw.rect(canvas, border_col, card_rect, 2, border_radius=8)
        item_rects[upg_id] = card_rect

        lbl = font_banner.render(f"[{key_num}] {upg_name}", True, txt_col)
        canvas.blit(lbl, (cx + 14, cy + 8))

        if lvl >= max_lvl:
            txt_lvl = font_card.render(f"LEVEL {lvl}/{max_lvl} (MAX LEVEL)", True, COLOR_EMERALD)
            txt_stat = font_card.render(f"CURRENT: {stat_func(lvl - 1).split('->')[1].strip()}", True, COLOR_EMERALD)
        else:
            txt_lvl = font_card.render(f"LV {lvl} -> LV {lvl+1}    Cost: {cost} SCRAP", True, txt_col if can_afford else (100, 100, 100))
            txt_stat = font_card.render(stat_func(lvl), True, txt_col)
            
        canvas.blit(txt_lvl, (cx + 14, cy + 38))
        canvas.blit(txt_stat, (cx + 14, cy + 58))

        # Progress bar
        bar_w = 200
        pygame.draw.rect(canvas, (30, 41, 59), (cx + card_w - bar_w - 14, cy + 42, bar_w, 12), border_radius=3)
        fill_w = int(bar_w * (lvl / max_lvl))
        if fill_w > 0:
            fill_col = COLOR_EMERALD if lvl >= max_lvl else color
            pygame.draw.rect(canvas, fill_col, (cx + card_w - bar_w - 14, cy + 42, fill_w, 12), border_radius=3)

    # Skin Theme Selector Button
    skin_btn_rect = pygame.Rect(SCREEN_WIDTH - 240, SCREEN_HEIGHT - 60, 220, 40)
    hov_s = skin_btn_rect.collidepoint(mx, my)
    pygame.draw.rect(canvas, (16, 185, 129) if hov_s else (30, 41, 59), skin_btn_rect, border_radius=8)
    pygame.draw.rect(canvas, COLOR_WHITE if hov_s else COLOR_EMERALD, skin_btn_rect, 2, border_radius=8)
    lbl_skin = font_card.render("[C] CHANGE SKIN", True, COLOR_WHITE)
    canvas.blit(lbl_skin, lbl_skin.get_rect(center=skin_btn_rect.center))

    exit_btn_rect = draw_exit_button(canvas)
    return exit_btn_rect, skin_btn_rect, item_rects
