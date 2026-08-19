"""
================================================================================
                    DRONE HUNTER 2D - MENUS & SCREEN FLOWS
================================================================================
Clean screen overlays and interfaces: Main Menu, Sector Select Map, Pause Settings,
Stage Clear, Game Over, and Grand Campaign Victory screens.
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
    vw, vh = canvas.get_size()
    exit_rect = pygame.Rect(vw - 140, vh - 55, 120, 38)
    mx, my = pygame.mouse.get_pos()
    hov = exit_rect.collidepoint(mx, my)
    pygame.draw.rect(canvas, (225, 29, 72) if hov else (25, 33, 50), exit_rect, border_radius=6)
    pygame.draw.rect(canvas, COLOR_WHITE if hov else (180, 40, 60), exit_rect, 1, border_radius=6)
    t = font_card.render("EXIT [Q]", True, COLOR_WHITE)
    canvas.blit(t, t.get_rect(center=exit_rect.center))
    return exit_rect


def draw_main_menu(canvas: pygame.Surface) -> dict[str, pygame.Rect]:
    """Renders pure, clean main title menu with prominent hierarchy and navigation buttons."""
    vw, vh = canvas.get_size()
    mx, my = pygame.mouse.get_pos()
    
    # 1. Ambient Backdrop Fill
    canvas.fill((10, 14, 23))

    # Subtle ambient gradient & decorative horizontal horizon line
    pygame.draw.line(canvas, (24, 38, 62), (vw // 4, vh // 2 - 40), (3 * vw // 4, vh // 2 - 40), 1)

    # 2. Prominent Game Title & Subtitle
    title_surf = font_title.render("DRONE HUNTER 2D", True, COLOR_CYAN)
    sub_surf = font_banner.render("ULTIMATE SCI-FI ARCADE", True, COLOR_GOLD)
    
    canvas.blit(title_surf, title_surf.get_rect(center=(vw // 2, vh // 2 - 130)))
    canvas.blit(sub_surf, sub_surf.get_rect(center=(vw // 2, vh // 2 - 75)))

    # 3. Clean Menu Action Buttons
    btn_w, btn_h = 240, 44
    cx = vw // 2 - btn_w // 2
    btn_y_start = vh // 2 - 10
    gap = 14

    btn_play = pygame.Rect(cx, btn_y_start, btn_w, btn_h)
    btn_sectors = pygame.Rect(cx, btn_y_start + (btn_h + gap), btn_w, btn_h)
    btn_hangar = pygame.Rect(cx, btn_y_start + 2 * (btn_h + gap), btn_w, btn_h)
    btn_exit = pygame.Rect(cx, btn_y_start + 3 * (btn_h + gap), btn_w, btn_h)

    buttons = {
        "play": btn_play,
        "sectors": btn_sectors,
        "hangar": btn_hangar,
        "exit": btn_exit
    }

    button_configs = [
        (btn_play, "PLAY [SPACE]", COLOR_CYAN),
        (btn_sectors, "SECTOR MAP [M]", (56, 189, 248)),
        (btn_hangar, "HANGAR SHOP [H]", COLOR_GOLD),
        (btn_exit, "EXIT GAME [Q]", COLOR_CRIMSON),
    ]

    for rect, label, col in button_configs:
        hov = rect.collidepoint(mx, my)
        bg_col = (25, 38, 62) if hov else (15, 23, 40)
        border_col = COLOR_WHITE if hov else col
        
        pygame.draw.rect(canvas, bg_col, rect, border_radius=6)
        pygame.draw.rect(canvas, border_col, rect, 2 if hov else 1, border_radius=6)
        
        lbl_surf = font_hud.render(label, True, COLOR_WHITE if hov else col)
        canvas.blit(lbl_surf, lbl_surf.get_rect(center=rect.center))

    # Version watermark
    v_txt = font_card.render("v2.0 PC EDITION", True, (80, 95, 120))
    canvas.blit(v_txt, (20, vh - 30))

    return buttons


def draw_sector_select_ui(canvas: pygame.Surface, unlocked_sectors: list[bool], scrap: int,
                          difficulty_mode: int = 1, unlocked_stages: list[bool] = None):
    """Renders sector campaign select map with difficulty toggles."""
    if unlocked_stages is None:
        unlocked_stages = [True] + [False] * 14

    vw, vh = canvas.get_size()
    canvas.fill((10, 15, 26))
    
    # Header bar
    header_rect = pygame.Rect(30, 20, vw - 60, 52)
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

    coin_hdr = font_banner.render(f"SCRAP: ${scrap}", True, COLOR_GOLD)
    canvas.blit(coin_hdr, (vw - 240, 32))

    # Sector Cards
    card_w = min(226, (vw - 80) // len(SECTORS) - 10)
    start_x = (vw - (card_w * len(SECTORS) + 14 * (len(SECTORS) - 1))) // 2
    gap = 14
    mx, my = pygame.mouse.get_pos()

    stage_buttons = []

    for idx, sec in enumerate(SECTORS):
        is_sec_unlocked = unlocked_sectors[idx] if idx < len(unlocked_sectors) else False
        cx = start_x + idx * (card_w + gap)
        card_r = pygame.Rect(cx, 85, card_w, vh - 160)
        hov = card_r.collidepoint(mx, my)

        bg_col = (20, 30, 50) if is_sec_unlocked else (12, 16, 26)
        border_col = COLOR_WHITE if (hov and is_sec_unlocked) else (sec["theme_color"] if is_sec_unlocked else (40, 50, 70))

        pygame.draw.rect(canvas, bg_col, card_r, border_radius=10)
        pygame.draw.rect(canvas, border_col, card_r, 3 if (hov and is_sec_unlocked) else 2, border_radius=10)

        # Sector Title
        s_title = font_banner.render(f"SECTOR {idx+1}", True, border_col)
        s_name = font_card.render(sec["name"], True, COLOR_WHITE if is_sec_unlocked else COLOR_TEXT_DIM)
        canvas.blit(s_title, (cx + 12, 98))
        canvas.blit(s_name, (cx + 12, 126))

        # Sub-level Stage Buttons
        stages = sec.get("stages", [])
        stage_y = vh - 280
        for stg_i, stg in enumerate(stages):
            flat_idx = idx * 3 + stg_i
            stg_unlocked = unlocked_stages[flat_idx] if flat_idx < len(unlocked_stages) else (flat_idx == 0)
            
            stg_rect = pygame.Rect(cx + 10, stage_y + stg_i * 38, card_w - 20, 34)
            stage_buttons.append((stg_rect, idx, stg_i + 1, stg_unlocked))
            stg_hov = stg_rect.collidepoint(mx, my)

            stg_bg = (30, 58, 138) if (stg_hov and stg_unlocked) else ((20, 30, 50) if stg_unlocked else (15, 20, 30))
            stg_border = COLOR_CYAN if (stg_hov and stg_unlocked) else ((56, 189, 248) if stg_unlocked else (35, 45, 60))

            pygame.draw.rect(canvas, stg_bg, stg_rect, border_radius=6)
            pygame.draw.rect(canvas, stg_border, stg_rect, 1, border_radius=6)

            stg_label = f"Stage {stg['num']}" + (" [BOSS]" if stg.get("hazard") == "boss_dreadnought" else "")
            stg_col = COLOR_WHITE if stg_unlocked else (75, 85, 99)
            txt_stg = font_card.render(stg_label, True, stg_col)
            canvas.blit(txt_stg, txt_stg.get_rect(center=stg_rect.center))

    exit_rect = draw_exit_button(canvas)
    return diff_rect, exit_rect, stage_buttons


def draw_pause_settings_ui(canvas: pygame.Surface, difficulty_mode: int, show_crt: bool, sound_enabled: bool) -> dict:
    """Renders pause overlay in screen space."""
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

    # Buttons
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
    _draw_btn(r_map, "SECTOR SELECT [M]", COLOR_CYAN)

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


def draw_level_clear_ui(canvas: pygame.Surface, sector_idx: int, sub_level: int):
    """Renders stage victory screen."""
    vw, vh = canvas.get_size()
    overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
    overlay.fill((5, 8, 15, 180))
    canvas.blit(overlay, (0, 0))

    t_clear = font_title.render("STAGE CLEAR", True, COLOR_EMERALD)
    t_sec = font_banner.render(f"SECTOR {sector_idx+1} - STAGE {sub_level} SECURED", True, COLOR_GOLD)
    t_cont = font_hud.render("PRESS [SPACE / ENTER] TO ENGAGE NEXT STAGE", True, COLOR_WHITE)

    canvas.blit(t_clear, t_clear.get_rect(center=(vw // 2, vh // 2 - 60)))
    canvas.blit(t_sec, t_sec.get_rect(center=(vw // 2, vh // 2)))
    canvas.blit(t_cont, t_cont.get_rect(center=(vw // 2, vh // 2 + 70)))


def draw_game_over_ui(canvas: pygame.Surface, score: int, highscore: int):
    """Renders game over defeat screen."""
    vw, vh = canvas.get_size()
    overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
    overlay.fill((15, 5, 8, 220))
    canvas.blit(overlay, (0, 0))

    t_go = font_gameover.render("MISSION FAILED", True, COLOR_CRIMSON)
    t_sc = font_banner.render(f"FINAL SCORE: {score:,}  |  HIGHSCORE: {highscore:,}", True, COLOR_WHITE)
    t_re = font_hud.render("PRESS [SPACE] TO RETRY  |  [M] SECTOR MAP  |  [Q] QUIT", True, COLOR_GOLD)

    canvas.blit(t_go, t_go.get_rect(center=(vw // 2, vh // 2 - 60)))
    canvas.blit(t_sc, t_sc.get_rect(center=(vw // 2, vh // 2 + 10)))
    canvas.blit(t_re, t_re.get_rect(center=(vw // 2, vh // 2 + 70)))


def draw_campaign_victory_ui(canvas: pygame.Surface, score: int, highscore: int, scrap: int):
    """Renders full campaign champion victory screen."""
    vw, vh = canvas.get_size()
    canvas.fill((10, 15, 26))

    t_vic = font_title.render("CAMPAIGN COMPLETE", True, COLOR_GOLD)
    t_sub = font_banner.render("SUPREME CITADEL LIBERATED - DRONE HUNTER CHAMPION", True, COLOR_CYAN)
    t_stats = font_hud.render(f"TOTAL SCORE: {score:,}  |  HIGHSCORE: {highscore:,}  |  SCRAP: ${scrap}", True, COLOR_WHITE)
    t_re = font_hud.render("PRESS [SPACE / ENTER] FOR SECTOR MAP  |  [Q] EXIT", True, COLOR_EMERALD)

    canvas.blit(t_vic, t_vic.get_rect(center=(vw // 2, vh // 2 - 80)))
    canvas.blit(t_sub, t_sub.get_rect(center=(vw // 2, vh // 2 - 20)))
    canvas.blit(t_stats, t_stats.get_rect(center=(vw // 2, vh // 2 + 40)))
    canvas.blit(t_re, t_re.get_rect(center=(vw // 2, vh // 2 + 100)))
    draw_exit_button(canvas)
