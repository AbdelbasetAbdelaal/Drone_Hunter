"""
================================================================================
                    DRONE HUNTER 2D - HANGAR & WEAPONS BAY
================================================================================
Hangar upgrade shop and drone skin customizer interface.
"""

import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_EMERALD,
    COLOR_PURPLE, COLOR_MISSILE, COLOR_BEAM, COLOR_TESLA, COLOR_CLUSTER,
    COLOR_WHITE, COLOR_HUD
)
from src.data.game_data import UPGRADES
from src.ui.font_manager import font_title, font_banner, font_card
from src.ui.menus import draw_exit_button

def draw_hangar_shop_ui(canvas: pygame.Surface, coins: int, current_sector_idx: int, upgrade_levels: dict[str, int]) -> tuple[pygame.Rect, pygame.Rect]:
    canvas.fill((10, 15, 26))

    header_rect = pygame.Rect(30, 20, SCREEN_WIDTH - 60, 56)
    pygame.draw.rect(canvas, (15, 23, 42), header_rect, border_radius=6)
    pygame.draw.rect(canvas, COLOR_CYAN, header_rect, 2, border_radius=6)
    
    t_hdr = font_title.render("DRONE HANGAR & WEAPONS BAY", True, COLOR_CYAN)
    coin_hdr = font_banner.render(f"GOLD SCRAP: ${coins}", True, COLOR_GOLD)
    canvas.blit(t_hdr, (48, 24))
    canvas.blit(coin_hdr, (SCREEN_WIDTH - 300, 32))

    items = [
        ("1", "battery", "Max Battery Capacity", COLOR_EMERALD),
        ("2", "speed", "Thruster Agility", COLOR_CYAN),
        ("3", "fire_rate", "Cannon Fire-Rate", COLOR_GOLD),
        ("4", "emp_recharge", "EMP Shockwave Charger", COLOR_PURPLE),
        ("5", "wingman", "Wingman Support Minidrones", COLOR_EMERALD),
        ("6", "cloak", "Tactical Cloaking Unit", COLOR_CYAN),
        ("7", "missiles", "Homing Missile Ordnance", COLOR_MISSILE),
        ("8", "beam", "Plasma Laser Beam Cannon", COLOR_BEAM),
        ("9", "tesla", "Arc Lightning Tesla Cannon", COLOR_TESLA),
        ("0", "cluster", "Cluster Torpedo Warhead", COLOR_CLUSTER)
    ]

    card_w, card_h = 560, 94
    mx, my = pygame.mouse.get_pos()

    for idx, (key_num, upg_id, upg_name, color) in enumerate(items):
        col_idx = idx % 2
        row_idx = idx // 2
        
        cx = 40 + col_idx * 600
        cy = 90 + row_idx * 102
        
        upg_def = UPGRADES.get(upg_id, {})
        lvl = upgrade_levels.get(upg_id, 0)
        max_lvl = upg_def.get("max_lvl", 5)
        base_cost = upg_def.get("base_cost", 50)
        cost_mult = upg_def.get("cost_mult", 1.5)
        cost = int(base_cost * (cost_mult ** lvl))

        card_rect = pygame.Rect(cx, cy, card_w, card_h)
        is_hover = card_rect.collidepoint(mx, my)

        bg_col = (20, 30, 52, 240) if is_hover else (15, 23, 42, 240)
        pygame.draw.rect(canvas, bg_col, card_rect, border_radius=8)
        pygame.draw.rect(canvas, COLOR_WHITE if is_hover else color, card_rect, 3 if is_hover else 2, border_radius=8)

        lbl = font_banner.render(f"[{key_num}] {upg_name}", True, COLOR_WHITE if is_hover else color)
        canvas.blit(lbl, (cx + 18, cy + 10))

        if lvl >= max_lvl:
            txt_lvl = font_card.render(f"LEVEL {lvl}/{max_lvl} - MAX LEVEL", True, COLOR_EMERALD)
        else:
            txt_lvl = font_card.render(f"LEVEL {lvl}/{max_lvl} - Upgrade Cost: ${cost}", True, COLOR_HUD)
        canvas.blit(txt_lvl, (cx + 18, cy + 38))

        pygame.draw.rect(canvas, (30, 41, 59), (cx + 18, cy + 64, 500, 10), border_radius=3)
        fill_w = int(500 * (lvl / max_lvl))
        if fill_w > 0:
            pygame.draw.rect(canvas, color, (cx + 18, cy + 64, fill_w, 10), border_radius=3)

    # Skin Theme Selector Button
    skin_btn_rect = pygame.Rect(SCREEN_WIDTH - 580, 28, 220, 40)
    hov_s = skin_btn_rect.collidepoint(mx, my)
    pygame.draw.rect(canvas, (16, 185, 129) if hov_s else (30, 41, 59), skin_btn_rect, border_radius=8)
    pygame.draw.rect(canvas, COLOR_WHITE if hov_s else COLOR_EMERALD, skin_btn_rect, 2, border_radius=8)
    lbl_skin = font_card.render("🎨 CHANGE SKIN [C]", True, COLOR_WHITE)
    canvas.blit(lbl_skin, lbl_skin.get_rect(center=skin_btn_rect.center))

    exit_btn_rect = draw_exit_button(canvas)
    return exit_btn_rect, skin_btn_rect
