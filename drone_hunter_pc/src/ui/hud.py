"""
================================================================================
                DRONE HUNTER 2D - MINIMAL RESPONSIVE COMBAT HUD
================================================================================
Streamlined, non-cluttering tactical HUD providing dynamic resolution scaling,
crisp Hull/Energy bars, score telemetry, compact combo streaks, and active weapon.
"""

import math
import pygame
from src.data.settings import (
    COLOR_HUD, COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_EMERALD,
    COLOR_SHIELD, COLOR_OVERCLOCK, COLOR_WHITE, COLOR_NEON_RED
)
from src.data.game_data import WEAPON_DEFS
from src.ui.font_manager import font_hud, font_card, font_banner

def draw_hud(canvas: pygame.Surface, player, sector_idx: int = 0, level_score: int = 0, total_score: int = 0,
             coins: int = 0, difficulty_name: str = "NORMAL", combo_mult: int = 1, show_crt: bool = False,
             current_wave: int = 1, sub_level: int = 1):
    """Renders clean, responsive tactical HUD that adapts dynamically to viewport dimensions."""
    vw, vh = canvas.get_size()
    margin_x = 24
    margin_y = 16

    # =========================================================================
    # 1. TOP-LEFT: Hull Integrity & Energy Status
    # =========================================================================
    if player:
        # HP Hull Bar
        hp_pct = max(0.0, min(1.0, player.health / max(1.0, player.max_health)))
        hp_w = 160
        hp_h = 16
        
        # Hull Background & Fill
        pygame.draw.rect(canvas, (15, 23, 42, 220), (margin_x, margin_y, hp_w, hp_h), border_radius=4)
        if hp_pct > 0:
            fill_w = int(round(hp_w * hp_pct))
            hp_col = COLOR_EMERALD if hp_pct > 0.5 else (COLOR_GOLD if hp_pct > 0.25 else COLOR_CRIMSON)
            pygame.draw.rect(canvas, hp_col, (margin_x, margin_y, fill_w, hp_h), border_radius=4)
        pygame.draw.rect(canvas, (51, 65, 85), (margin_x, margin_y, hp_w, hp_h), 1, border_radius=4)
        
        txt_hp = font_card.render(f"HULL  {int(player.health)}/{int(player.max_health)}", True, COLOR_WHITE)
        canvas.blit(txt_hp, (margin_x, margin_y + hp_h + 4))

        # NRG Bar (Stacked right below Hull readout)
        nrg_y = margin_y + hp_h + 24
        nrg_pct = max(0.0, min(1.0, player.energy / max(1.0, player.max_energy)))
        nrg_w = 120
        nrg_h = 10
        
        pygame.draw.rect(canvas, (15, 23, 42, 220), (margin_x, nrg_y, nrg_w, nrg_h), border_radius=3)
        if nrg_pct > 0:
            fill_nrg = int(round(nrg_w * nrg_pct))
            pygame.draw.rect(canvas, COLOR_CYAN, (margin_x, nrg_y, fill_nrg, nrg_h), border_radius=3)
        pygame.draw.rect(canvas, (30, 58, 85), (margin_x, nrg_y, nrg_w, nrg_h), 1, border_radius=3)
        
        txt_nrg = font_card.render(f"NRG  {int(player.energy)}%", True, COLOR_CYAN)
        canvas.blit(txt_nrg, (margin_x + nrg_w + 8, nrg_y - 2))

        # Shield Hit Charge Indicators
        if player.shield_hits > 0:
            sh_x = margin_x + hp_w + 14
            for s_i in range(min(5, player.shield_hits)):
                pygame.draw.circle(canvas, COLOR_SHIELD, (sh_x + s_i * 14, margin_y + 8), 5)
                pygame.draw.circle(canvas, COLOR_WHITE, (sh_x + s_i * 14, margin_y + 8), 2)
            txt_sh = font_card.render(f"SHIELD x{player.shield_hits}", True, COLOR_SHIELD)
            canvas.blit(txt_sh, (sh_x + player.shield_hits * 14 + 6, margin_y + 2))

        # EMP Jammed Alert Banner
        if player.is_jammed:
            jam_banner = font_banner.render(f"⚡ SYSTEM JAMMED: {player.emp_jammed_timer:.1f}s", True, COLOR_NEON_RED)
            canvas.blit(jam_banner, (vw // 2 - jam_banner.get_width() // 2, 70))

    # =========================================================================
    # 2. TOP-RIGHT: Score & Compact Combo Indicator
    # =========================================================================
    score_str = f"SCORE: {level_score:,}"
    lbl_score = font_hud.render(score_str, True, COLOR_WHITE)
    score_x = vw - margin_x - lbl_score.get_width()
    canvas.blit(lbl_score, (score_x, margin_y))

    # Compact Combo Streak Pill (Adjacent to Score)
    if combo_mult > 1:
        combo_txt = f"COMBO x{combo_mult}"
        lbl_combo = font_card.render(combo_txt, True, COLOR_GOLD)
        combo_w = lbl_combo.get_width() + 14
        combo_rect = pygame.Rect(score_x - combo_w - 12, margin_y + 2, combo_w, 22)
        pygame.draw.rect(canvas, (245, 158, 11, 40), combo_rect, border_radius=4)
        pygame.draw.rect(canvas, COLOR_GOLD, combo_rect, 1, border_radius=4)
        canvas.blit(lbl_combo, (combo_rect.left + 7, combo_rect.top + 4))

    # =========================================================================
    # 3. BOTTOM-RIGHT: Active Weapon Indicator
    # =========================================================================
    if player:
        w_def = WEAPON_DEFS.get(player.active_weapon, {})
        w_name = w_def.get("name", "Pulse Laser").upper()
        w_col = w_def.get("color", COLOR_CYAN)
        w_icon = w_def.get("icon", "⚡")
        
        lbl_wpn = font_hud.render(f"{w_icon} {w_name}", True, w_col)
        wpn_w = lbl_wpn.get_width() + 20
        wpn_h = 32
        wpn_x = vw - margin_x - wpn_w
        wpn_y = vh - margin_y - wpn_h
        
        wpn_rect = pygame.Rect(wpn_x, wpn_y, wpn_w, wpn_h)
        pygame.draw.rect(canvas, (15, 23, 42, 220), wpn_rect, border_radius=6)
        pygame.draw.rect(canvas, w_col, wpn_rect, 1, border_radius=6)
        canvas.blit(lbl_wpn, (wpn_x + 10, wpn_y + 6))


def draw_boss_health_bar(canvas: pygame.Surface, boss_target):
    """Renders Boss Health Bar centered dynamically at top of viewport."""
    if not boss_target or not boss_target.alive:
        return
    vw, vh = canvas.get_size()
    hp_pct = max(0.0, min(1.0, boss_target.hp / max(1, boss_target.max_hp)))
    bar_w = min(480, vw - 120)
    bar_rect = pygame.Rect(vw // 2 - bar_w // 2, 54, bar_w, 20)
    
    pygame.draw.rect(canvas, (15, 23, 42, 240), bar_rect, border_radius=5)
    fill_w = int(round(bar_w * hp_pct))
    if fill_w > 0:
        pygame.draw.rect(canvas, COLOR_CRIMSON, (bar_rect.left, bar_rect.top, fill_w, 20), border_radius=5)
    pygame.draw.rect(canvas, COLOR_WHITE, bar_rect, 1, border_radius=5)
    
    boss_name = getattr(boss_target, "enemy_type", "BOSS").replace("_", " ").upper()
    lbl = font_card.render(f"⚠️ {boss_name}: {int(hp_pct * 100)}%", True, COLOR_WHITE)
    canvas.blit(lbl, lbl.get_rect(center=bar_rect.center))


def draw_combo_banner(canvas: pygame.Surface, combo_count: int, combo_timer: float):
    """Minimal compact combo indicator (kept for backwards compatibility)."""
    # Redundant with top-right compact combo tag in Phase 1.5
    pass

def draw_radar_minimap(canvas: pygame.Surface, player, targets_group, wingmen_group=None):
    """Radar minimap stub (kept for backwards compatibility)."""
    pass
