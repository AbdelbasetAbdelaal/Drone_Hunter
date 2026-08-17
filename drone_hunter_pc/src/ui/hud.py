"""
================================================================================
                    DRONE HUNTER 2D - HOLOGRAPHIC HUD & RADAR
================================================================================
Renders in-game tactical heads-up display, energy/shield status bars, ability
cooldown pills, dynamic radar minimap, boss health bars, and combo streaks.
"""

import math
import pygame
from src.data.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, COLOR_HUD, COLOR_CYAN, COLOR_GOLD,
    COLOR_CRIMSON, COLOR_EMERALD, COLOR_SHIELD, COLOR_OVERCLOCK, COLOR_WHITE
)
from src.data.game_data import WEAPON_DEFS, SECTORS
from src.ui.font_manager import font_hud, font_card, font_banner

def draw_hud(canvas: pygame.Surface, player, sector_idx: int, level_score: int, total_score: int,
             coins: int, difficulty_name: str, combo_mult: int = 1, show_crt: bool = False,
             current_wave: int = 1, sub_level: int = 1):
    """Renders top holographic status ribbon and ability indicators."""
    bar_w, bar_h = SCREEN_WIDTH - 60, 52
    bar_x, bar_y = 30, 10
    
    # Backdrop
    hud_bg = pygame.Surface((bar_w, bar_h), pygame.SRCALPHA)
    hud_bg.fill((15, 23, 42, 235))
    canvas.blit(hud_bg, (bar_x, bar_y))
    pygame.draw.rect(canvas, COLOR_CYAN, (bar_x, bar_y, bar_w, bar_h), 2, border_radius=8)

    # Health & Energy
    if player:
        # HP Bar
        hp_pct = max(0.0, min(1.0, player.energy / player.max_energy))
        hp_bar_w = 170
        pygame.draw.rect(canvas, (30, 41, 59), (bar_x + 15, bar_y + 12, hp_bar_w, 14), border_radius=4)
        if hp_pct > 0:
            fill_w = int(hp_bar_w * hp_pct)
            hp_col = COLOR_EMERALD if hp_pct > 0.5 else (COLOR_GOLD if hp_pct > 0.25 else COLOR_CRIMSON)
            pygame.draw.rect(canvas, hp_col, (bar_x + 15, bar_y + 12, fill_w, 14), border_radius=4)
        pygame.draw.rect(canvas, COLOR_WHITE, (bar_x + 15, bar_y + 12, hp_bar_w, 14), 1, border_radius=4)
        
        txt_hp = font_card.render(f"HULL: {int(player.energy)}/{int(player.max_energy)}", True, COLOR_WHITE)
        canvas.blit(txt_hp, (bar_x + 15, bar_y + 30))

        # Shield Hit Charges (Fixes Bug 1)
        if player.shield_hits > 0:
            for s_i in range(min(5, player.shield_hits)):
                pygame.draw.circle(canvas, COLOR_SHIELD, (bar_x + 200 + s_i * 14, bar_y + 18), 5)
            txt_sh = font_card.render(f"SHIELD ({player.shield_hits})", True, COLOR_SHIELD)
            canvas.blit(txt_sh, (bar_x + 200, bar_y + 30))

    # Stage / Sector Information
    sec_name = SECTORS[sector_idx]["name"] if 0 <= sector_idx < len(SECTORS) else "Sector"
    stg_text = f"SEC {sector_idx+1}-{sub_level} | {sec_name.upper()}"
    lbl_stg = font_hud.render(stg_text, True, COLOR_GOLD)
    canvas.blit(lbl_stg, (bar_x + 320, bar_y + 8))

    # Score & Currency
    score_text = f"SCORE: {level_score}  |  TOTAL: {total_score}  |  SCRAP: ${coins}"
    lbl_score = font_card.render(score_text, True, COLOR_HUD)
    canvas.blit(lbl_score, (bar_x + 320, bar_y + 28))

    # Tactical Pills Helper
    def _pill(px: int, tag: str, val: str, ready: bool, color: tuple[int, int, int]):
        pill_rect = pygame.Rect(px, bar_y + 10, 92, 32)
        pygame.draw.rect(canvas, (10, 15, 26, 220), pill_rect, border_radius=6)
        pygame.draw.rect(canvas, color if ready else (60, 70, 90), pill_rect, 1, border_radius=6)
        t1 = font_card.render(tag, True, (148, 163, 184))
        t2 = font_card.render(val, True, color if ready else (100, 115, 135))
        canvas.blit(t1, (px + 6, bar_y + 12))
        canvas.blit(t2, (px + 6, bar_y + 24))

    if player:
        # Weapon Pill
        w_def = WEAPON_DEFS.get(player.active_weapon, {})
        w_name = w_def.get("name", "Pulse").split()[0]
        w_col = w_def.get("color", COLOR_GOLD)
        _pill(bar_x + 720, "WPN", w_name.upper()[:6], True, w_col)

        # EMP Pill
        emp_ready = player.emp_cooldown <= 0.0 and not player.is_jammed
        emp_lbl = "READY" if emp_ready else (f"{player.emp_cooldown:.1f}s" if not player.is_jammed else "LOCK")
        _pill(bar_x + 820, "EMP [E]", emp_lbl, emp_ready, COLOR_CYAN)

        # Roll Pill
        roll_ready = player.roll_cooldown <= 0.0 and not player.is_jammed
        _pill(bar_x + 920, "ROLL", "READY" if roll_ready else "WAIT", roll_ready, COLOR_EMERALD)

        # Overdrive Pill
        od_active = player.overdrive_timer > 0.0
        od_ready = player.overdrive_cooldown <= 0.0 and not player.is_jammed
        od_label = f"{player.overdrive_timer:.1f}s" if od_active else ("READY" if od_ready else f"{player.overdrive_cooldown:.0f}s")
        _pill(bar_x + 1020, "ULT [F]", od_label, od_active or od_ready, COLOR_GOLD if od_ready else (COLOR_OVERCLOCK if od_active else (239, 68, 68)))

        # EMP Jammed Warning Banner (Fixes Bug 4)
        if player.is_jammed:
            jam_banner = font_banner.render(f"⚡ SYSTEM JAMMED: {player.emp_jammed_timer:.1f}s", True, COLOR_NEON_RED)
            canvas.blit(jam_banner, (bar_x + 480, bar_y + 60))


def draw_boss_health_bar(canvas: pygame.Surface, boss_target):
    """Renders Boss Health Bar with flashing alarm border."""
    if not boss_target or not boss_target.alive:
        return
    hp_pct = max(0.0, min(1.0, boss_target.hp / boss_target.max_hp))
    bar_w = 440
    bar_rect = pygame.Rect(SCREEN_WIDTH // 2 - bar_w // 2, 70, bar_w, 24)
    
    pygame.draw.rect(canvas, (15, 23, 42, 240), bar_rect, border_radius=6)
    fill_w = int(bar_w * hp_pct)
    if fill_w > 0:
        pygame.draw.rect(canvas, COLOR_CRIMSON, (bar_rect.left, bar_rect.top, fill_w, 24), border_radius=6)
    pygame.draw.rect(canvas, COLOR_WHITE, bar_rect, 2, border_radius=6)
    
    boss_name = getattr(boss_target, "enemy_type", "BOSS").replace("_", " ").upper()
    lbl = font_hud.render(f"⚠️ {boss_name}: {int(hp_pct * 100)}%", True, COLOR_WHITE)
    canvas.blit(lbl, lbl.get_rect(center=bar_rect.center))


def draw_radar_minimap(canvas: pygame.Surface, player, targets_group, wingmen_group=None):
    """Renders dynamic radar scanner in top right."""
    radar_w, radar_h = 175, 56
    radar_rect = pygame.Rect(SCREEN_WIDTH - 185, 10, radar_w, radar_h)
    
    pygame.draw.rect(canvas, (15, 23, 42, 235), radar_rect, border_radius=8)
    pygame.draw.rect(canvas, COLOR_CYAN, radar_rect, 2, border_radius=8)
    pygame.draw.line(canvas, (30, 41, 59), (radar_rect.centerx, radar_rect.top), (radar_rect.centerx, radar_rect.bottom), 1)
    pygame.draw.line(canvas, (30, 41, 59), (radar_rect.left, radar_rect.centery), (radar_rect.right, radar_rect.centery), 1)

    if player:
        px = radar_rect.left + int((player.pos.x / SCREEN_WIDTH) * radar_w)
        py = radar_rect.top + int((player.pos.y / SCREEN_HEIGHT) * radar_h)
        pygame.draw.circle(canvas, COLOR_CYAN, (px, py), 3)

    if targets_group:
        for t in targets_group:
            tx = radar_rect.left + int((t.rect.centerx / SCREEN_WIDTH) * radar_w)
            ty = radar_rect.top + int((t.rect.centery / SCREEN_HEIGHT) * radar_h)
            if radar_rect.collidepoint(tx, ty):
                col = COLOR_CRIMSON if not getattr(t, "is_boss", False) else COLOR_GOLD
                r = 2 if not getattr(t, "is_boss", False) else 4
                pygame.draw.circle(canvas, col, (tx, ty), r)


def draw_combo_banner(canvas: pygame.Surface, combo_count: int, combo_timer: float):
    """Draws multi-kill combo streak banner."""
    if combo_count > 1 and combo_timer > 0:
        c_text = f"🔥 {combo_count}X COMBO STREAK!"
        lbl = font_banner.render(c_text, True, COLOR_GOLD)
        canvas.blit(lbl, (SCREEN_WIDTH // 2 - lbl.get_width() // 2, SCREEN_HEIGHT - 65))
