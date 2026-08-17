"""
================================================================================
                    DRONE HUNTER 2D - MENUS & SCREEN FLOWS
================================================================================
Screen overlays and interfaces: Main Menu, Sector Select Map, Pause Settings,
Stage Clear, Game Over, and Grand Campaign Victory Champion screens.
"""

import math
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_CYAN, COLOR_GOLD, COLOR_EMERALD,
    COLOR_CRIMSON, COLOR_MAGENTA, COLOR_HUD, COLOR_WHITE, COLOR_TEXT_DIM
)
from src.data.game_data import SECTORS, DIFFICULTY_NAMES, DIFFICULTY_MODIFIERS
from src.ui.font_manager import font_title, font_banner, font_card, font_hud, font_gameover

def draw_exit_button(canvas: pygame.Surface) -> pygame.Rect:
    exit_rect = pygame.Rect(SCREEN_WIDTH - 140, SCREEN_HEIGHT - 55, 120, 40)
    mx, my = pygame.mouse.get_pos()
    hov = exit_rect.collidepoint(mx, my)
    pygame.draw.rect(canvas, (225, 29, 72) if hov else (30, 41, 59), exit_rect, border_radius=8)
    pygame.draw.rect(canvas, COLOR_WHITE if hov else COLOR_CRIMSON, exit_rect, 2, border_radius=8)
    t = font_card.render("EXIT [Q]", True, COLOR_WHITE)
    canvas.blit(t, t.get_rect(center=exit_rect.center))
    return exit_rect


def draw_main_menu(canvas: pygame.Surface):
    """Renders main title screen."""
    title_surf = font_title.render("DRONE HUNTER 2D", True, COLOR_CYAN)
    sub_surf = font_banner.render("ULTIMATE SCI-FI ARCADE EDITION [PC]", True, COLOR_GOLD)
    start_surf = font_hud.render("PRESS [SPACE] TO ENTER SECTOR MAP  |  [Q] EXIT", True, COLOR_HUD)
    canvas.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 260)))
    canvas.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 330)))
    canvas.blit(start_surf, start_surf.get_rect(center=(SCREEN_WIDTH // 2, 440)))
    draw_exit_button(canvas)


def draw_sector_select_ui(canvas: pygame.Surface, unlocked_sectors: list[bool], coins: int,
                          difficulty_mode: int = 1, unlocked_stages: list[bool] = None):
    """Renders high-tech sector campaign select map with difficulty toggles."""
    if unlocked_stages is None:
        unlocked_stages = [True] + [False] * 14

    canvas.fill((10, 15, 26))
    
    # Header bar
    header_rect = pygame.Rect(30, 20, SCREEN_WIDTH - 60, 52)
    pygame.draw.rect(canvas, (15, 23, 42), header_rect, border_radius=8)
    pygame.draw.rect(canvas, COLOR_CYAN, header_rect, 2, border_radius=8)
    
    t_hdr = font_title.render("CAMPAIGN SECTORS", True, COLOR_CYAN)
    canvas.blit(t_hdr, (48, 22))

    # Difficulty Badge Button
    diff_name = DIFFICULTY_NAMES[difficulty_mode]
    diff_col = DIFFICULTY_MODIFIERS[difficulty_mode]["badge_color"]
    diff_rect = pygame.Rect(480, 28, 220, 36)
    pygame.draw.rect(canvas, (20, 30, 50), diff_rect, border_radius=6)
    pygame.draw.rect(canvas, diff_col, diff_rect, 2, border_radius=6)
    t_diff = font_card.render(f"DIFFICULTY: {diff_name}", True, diff_col)
    canvas.blit(t_diff, t_diff.get_rect(center=diff_rect.center))

    coin_hdr = font_banner.render(f"SCRAP: ${coins}", True, COLOR_GOLD)
    canvas.blit(coin_hdr, (SCREEN_WIDTH - 240, 32))

    # Sector Cards
    card_w = 226
    start_x = 44
    gap = 18
    mx, my = pygame.mouse.get_pos()

    for idx, sec in enumerate(SECTORS):
        is_sec_unlocked = unlocked_sectors[idx] if idx < len(unlocked_sectors) else False
        cx = start_x + idx * (card_w + gap)
        card_r = pygame.Rect(cx, 85, card_w, 530)
        hov = card_r.collidepoint(mx, my)

        bg_col = (20, 30, 50) if is_sec_unlocked else (12, 16, 26)
        border_col = COLOR_WHITE if (hov and is_sec_unlocked) else (sec["theme_color"] if is_sec_unlocked else (40, 50, 70))

        pygame.draw.rect(canvas, bg_col, card_r, border_radius=10)
        pygame.draw.rect(canvas, border_col, card_r, 3 if (hov and is_sec_unlocked) else 2, border_radius=10)

        # Sector Title
        s_title = font_banner.render(f"SECTOR {idx+1}", True, border_col)
        s_name = font_card.render(sec["name"], True, COLOR_WHITE if is_sec_unlocked else COLOR_TEXT_DIM)
        canvas.blit(s_title, (cx + 14, 100))
        canvas.blit(s_name, (cx + 14, 130))

        # Sub-level Stage Buttons
        stages = sec.get("stages", [])
        stage_y = 390
        for stg_i, stg in enumerate(stages):
            flat_idx = idx * 3 + stg_i
            stg_unlocked = unlocked_stages[flat_idx] if flat_idx < len(unlocked_stages) else (flat_idx == 0)
            
            stg_rect = pygame.Rect(cx + 10, stage_y + stg_i * 38, card_w - 20, 34)
            stg_hov = stg_rect.collidepoint(mx, my)

            s_bg = (16, 185, 129, 180) if stg_unlocked else (25, 30, 42)
            pygame.draw.rect(canvas, s_bg, stg_rect, border_radius=6)
            pygame.draw.rect(canvas, COLOR_WHITE if (stg_hov and stg_unlocked) else (COLOR_EMERALD if stg_unlocked else (50, 60, 80)), stg_rect, 1, border_radius=6)

            stg_txt = font_card.render(f"{idx+1}-{stg_i+1}: {stg['name'][:14]}", True, COLOR_WHITE if stg_unlocked else COLOR_TEXT_DIM)
            canvas.blit(stg_txt, (stg_rect.x + 8, stg_rect.y + 7))

    draw_exit_button(canvas)


def draw_pause_settings_ui(canvas: pygame.Surface, difficulty_mode: int, show_crt: bool, sound_enabled: bool, is_diff_open: bool = False) -> dict:
    """Renders Pause overlay with settings controls."""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 15, 26, 210))
    canvas.blit(overlay, (0, 0))

    box_w, box_h = 440, 420
    box_rect = pygame.Rect(SCREEN_WIDTH // 2 - box_w // 2, SCREEN_HEIGHT // 2 - box_h // 2, box_w, box_h)
    pygame.draw.rect(canvas, (15, 23, 42), box_rect, border_radius=12)
    pygame.draw.rect(canvas, COLOR_CYAN, box_rect, 2, border_radius=12)

    title = font_title.render("SYSTEM PAUSED", True, COLOR_CYAN)
    canvas.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, box_rect.top + 45)))

    btn_w, btn_h = 320, 38
    start_y = box_rect.top + 95
    mx, my = pygame.mouse.get_pos()

    buttons = {}
    items = [
        ("resume", "▶ RESUME MISSION [P]"),
        ("diff", f"DIFFICULTY: {DIFFICULTY_NAMES[difficulty_mode]} [D]"),
        ("sfx", f"AUDIO SFX: {'ON' if sound_enabled else 'OFF'} [S]"),
        ("crt", f"CRT SCANLINES: {'ON' if show_crt else 'OFF'} [F2]"),
        ("hangar", "🛠️ WEAPONS HANGAR [H]"),
        ("map", "🗺️ SECTOR MAP [M]"),
        ("exit", "❌ ABORT MISSION [Q]")
    ]

    for i, (key, label) in enumerate(items):
        by = start_y + i * 44
        b_rect = pygame.Rect(SCREEN_WIDTH // 2 - btn_w // 2, by, btn_w, btn_h)
        hov = b_rect.collidepoint(mx, my)
        pygame.draw.rect(canvas, (30, 41, 59) if not hov else (14, 165, 233), b_rect, border_radius=6)
        pygame.draw.rect(canvas, COLOR_CYAN, b_rect, 1, border_radius=6)
        t = font_card.render(label, True, COLOR_WHITE)
        canvas.blit(t, t.get_rect(center=b_rect.center))
        buttons[key] = b_rect

    return buttons


def draw_campaign_victory_ui(canvas: pygame.Surface, total_score: int, highscore: int, coins: int):
    """Renders Grand Campaign Victory Screen (Fixes Bug 3)."""
    canvas.fill((10, 15, 26))
    
    card_rect = pygame.Rect(140, 80, SCREEN_WIDTH - 280, 560)
    pygame.draw.rect(canvas, (15, 23, 42, 245), card_rect, border_radius=16)
    pygame.draw.rect(canvas, COLOR_GOLD, card_rect, 3, border_radius=16)

    t_vic = font_title.render("🏆 GRAND CAMPAIGN VICTORY 🏆", True, COLOR_GOLD)
    sub = font_banner.render("ALL SECTORS LIBERATED — SUPREME DRONE HUNTER", True, COLOR_CYAN)
    canvas.blit(t_vic, t_vic.get_rect(center=(SCREEN_WIDTH // 2, 160)))
    canvas.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 220)))

    # Stats Summary
    stats_y = 300
    s1 = font_hud.render(f"FINAL CAMPAIGN SCORE: {total_score:,}", True, COLOR_WHITE)
    s2 = font_hud.render(f"LIFETIME HIGHSCORE: {highscore:,}", True, COLOR_GOLD)
    s3 = font_hud.render(f"GOLD SCRAP HARVESTED: ${coins:,}", True, COLOR_EMERALD)
    canvas.blit(s1, s1.get_rect(center=(SCREEN_WIDTH // 2, stats_y)))
    canvas.blit(s2, s2.get_rect(center=(SCREEN_WIDTH // 2, stats_y + 40)))
    canvas.blit(s3, s3.get_rect(center=(SCREEN_WIDTH // 2, stats_y + 80)))

    # Action Banner
    act = font_card.render("Press [SPACE] for NIGHTMARE MODE | [M] Sector Map | [Q] Quit", True, COLOR_HUD)
    canvas.blit(act, act.get_rect(center=(SCREEN_WIDTH // 2, 530)))
    draw_exit_button(canvas)


def draw_level_clear_ui(canvas: pygame.Surface, sector_idx: int, sub_level: int):
    clear_surf = font_title.render(f"STAGE {sector_idx+1}-{sub_level} CLEARED!", True, COLOR_GOLD)
    sub_surf = font_hud.render("Press [SPACE] to Launch Next Stage", True, COLOR_CYAN)
    canvas.blit(clear_surf, clear_surf.get_rect(center=(SCREEN_WIDTH // 2, 300)))
    canvas.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 370)))


def draw_game_over_ui(canvas: pygame.Surface, total_score: int, highscore: int):
    go_surf = font_gameover.render("MISSION FAILED", True, COLOR_CRIMSON)
    score_surf = font_banner.render(f"FINAL SCORE: {total_score}  |  HIGHSCORE: {highscore}", True, COLOR_GOLD)
    sub_surf = font_hud.render("Press [SPACE] to Restart Mission", True, COLOR_HUD)
    canvas.blit(go_surf, go_surf.get_rect(center=(SCREEN_WIDTH // 2, 280)))
    canvas.blit(score_surf, score_surf.get_rect(center=(SCREEN_WIDTH // 2, 350)))
    canvas.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 420)))
