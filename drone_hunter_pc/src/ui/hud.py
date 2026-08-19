"""
================================================================================
                DRONE HUNTER 2D - MINIMAL RESPONSIVE COMBAT HUD
================================================================================
Strict screen-space tactical HUD providing dynamic resolution scaling,
compact Hull/Energy readouts, score telemetry, compact ability indicators,
and minimal weapon badge. Never transforms through camera.
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
    """Renders clean, responsive screen-space tactical HUD."""
    vw, vh = canvas.get_size()
    margin_x = 24
    margin_y = 16

    # =========================================================================
    # 1. TOP-LEFT: Hull Integrity, Energy Status & Shield Pips
    # =========================================================================
    if player:
        # HP Hull Bar
        hp_pct = max(0.0, min(1.0, player.health / max(1.0, player.max_health)))
        hp_w = 150
        hp_h = 14
        
        pygame.draw.rect(canvas, (15, 23, 42, 220), (margin_x, margin_y, hp_w, hp_h), border_radius=4)
        if hp_pct > 0:
            fill_w = int(round(hp_w * hp_pct))
            hp_col = COLOR_EMERALD if hp_pct > 0.5 else (COLOR_GOLD if hp_pct > 0.25 else COLOR_CRIMSON)
            pygame.draw.rect(canvas, hp_col, (margin_x, margin_y, fill_w, hp_h), border_radius=4)
        pygame.draw.rect(canvas, (51, 65, 85), (margin_x, margin_y, hp_w, hp_h), 1, border_radius=4)
        
        txt_hp = font_card.render(f"HULL  {int(player.health)}/{int(player.max_health)}", True, COLOR_WHITE)
        canvas.blit(txt_hp, (margin_x, margin_y + hp_h + 3))

        # NRG Bar (Stacked right below Hull readout)
        nrg_y = margin_y + hp_h + 20
        nrg_pct = max(0.0, min(1.0, player.energy / max(1.0, player.max_energy)))
        nrg_w = 110
        nrg_h = 8
        
        pygame.draw.rect(canvas, (15, 23, 42, 220), (margin_x, nrg_y, nrg_w, nrg_h), border_radius=3)
        if nrg_pct > 0:
            fill_nrg = int(round(nrg_w * nrg_pct))
            pygame.draw.rect(canvas, COLOR_CYAN, (margin_x, nrg_y, fill_nrg, nrg_h), border_radius=3)
        pygame.draw.rect(canvas, (30, 58, 85), (margin_x, nrg_y, nrg_w, nrg_h), 1, border_radius=3)
        
        txt_nrg = font_card.render(f"NRG  {int(player.energy)}%", True, COLOR_CYAN)
        canvas.blit(txt_nrg, (margin_x + nrg_w + 8, nrg_y - 3))

        # Shield Hit Charge Indicators
        if player.shield_hits > 0:
            sh_x = margin_x + hp_w + 14
            for s_i in range(min(5, player.shield_hits)):
                pygame.draw.circle(canvas, COLOR_SHIELD, (sh_x + s_i * 12, margin_y + 7), 4)
                pygame.draw.circle(canvas, COLOR_WHITE, (sh_x + s_i * 12, margin_y + 7), 1)
            txt_sh = font_card.render(f"SHIELD x{player.shield_hits}", True, COLOR_SHIELD)
            canvas.blit(txt_sh, (sh_x + player.shield_hits * 12 + 6, margin_y + 1))

        # EMP Jammed Alert Banner (Centered on screen)
        if player.is_jammed:
            jam_banner = font_banner.render(f"⚡ SYSTEM JAMMED: {player.emp_jammed_timer:.1f}s", True, COLOR_NEON_RED)
            canvas.blit(jam_banner, (vw // 2 - jam_banner.get_width() // 2, 70))

    # =========================================================================
    # 2. TOP-RIGHT: Level, Score & Compact Combo Tag
    # =========================================================================
    level_str = f"SECTOR {sector_idx + 1} - LEVEL {sub_level}"
    lbl_level = font_card.render(level_str, True, COLOR_CYAN)
    level_x = vw - margin_x - lbl_level.get_width()
    canvas.blit(lbl_level, (level_x, margin_y))

    score_str = f"SCORE: {level_score:,}"
    lbl_score = font_hud.render(score_str, True, COLOR_WHITE)
    score_x = vw - margin_x - lbl_score.get_width()
    canvas.blit(lbl_score, (score_x, margin_y + 20))

    # Compact Combo Streak Badge
    if combo_mult > 1:
        combo_txt = f"COMBO x{combo_mult}"
        lbl_combo = font_card.render(combo_txt, True, COLOR_GOLD)
        combo_w = lbl_combo.get_width() + 12
        combo_rect = pygame.Rect(score_x - combo_w - 10, margin_y + 22, combo_w, 20)
        pygame.draw.rect(canvas, (245, 158, 11, 40), combo_rect, border_radius=4)
        pygame.draw.rect(canvas, COLOR_GOLD, combo_rect, 1, border_radius=4)
        canvas.blit(lbl_combo, (combo_rect.left + 6, combo_rect.top + 3))

    # =========================================================================
    # 3. BOTTOM-CENTER: Screen-Space Ability Indicators
    # =========================================================================
    if player:
        abilities = [
            ("ROLL", player.roll_cooldown <= 0.0, COLOR_EMERALD, f"{player.roll_cooldown:.1f}s" if player.roll_cooldown > 0 else "READY"),
            ("EMP [E]", player.emp_cooldown <= 0.0, COLOR_CYAN, f"{player.emp_cooldown:.1f}s" if player.emp_cooldown > 0 else "READY"),
            ("ULT [F]", player.overdrive_cooldown <= 0.0 or player.overdrive_timer > 0, COLOR_GOLD if player.overdrive_cooldown <= 0 else COLOR_OVERCLOCK,
             f"{player.overdrive_timer:.1f}s" if player.overdrive_timer > 0 else ("READY" if player.overdrive_cooldown <= 0 else f"{player.overdrive_cooldown:.0f}s")),
        ]
        
        pill_w = 78
        pill_h = 24
        gap = 8
        total_w = len(abilities) * pill_w + (len(abilities) - 1) * gap
        start_x = (vw - total_w) // 2
        p_y = vh - margin_y - pill_h

        for idx, (name, ready, col, status_str) in enumerate(abilities):
            px = start_x + idx * (pill_w + gap)
            p_rect = pygame.Rect(px, p_y, pill_w, pill_h)
            pygame.draw.rect(canvas, (15, 23, 42, 210), p_rect, border_radius=4)
            pygame.draw.rect(canvas, col if ready else (45, 55, 75), p_rect, 1, border_radius=4)
            
            txt_name = font_card.render(name, True, col if ready else (120, 135, 155))
            canvas.blit(txt_name, (px + 6, p_y + 4))

    # =========================================================================
    # 4. BOTTOM-RIGHT: Compact Weapon Indicator
    # =========================================================================
    if player:
        w_def = WEAPON_DEFS.get(player.active_weapon, {})
        w_name = w_def.get("name", "Pulse Laser").upper()
        w_col = w_def.get("color", COLOR_CYAN)
        
        lbl_wpn = font_card.render(f"⚡ {w_name}", True, w_col)
        wpn_w = lbl_wpn.get_width() + 16
        wpn_h = 26
        wpn_x = vw - margin_x - wpn_w
        wpn_y = vh - margin_y - wpn_h
        
        wpn_rect = pygame.Rect(wpn_x, wpn_y, wpn_w, wpn_h)
        pygame.draw.rect(canvas, (15, 23, 42, 220), wpn_rect, border_radius=5)
        pygame.draw.rect(canvas, w_col, wpn_rect, 1, border_radius=5)
        canvas.blit(lbl_wpn, (wpn_x + 8, wpn_y + 5))


def draw_boss_health_bar(canvas: pygame.Surface, boss_target):
    """Renders Boss Health Bar centered dynamically at top of viewport."""
    if not boss_target or not boss_target.alive:
        return
    vw, vh = canvas.get_size()
    hp_pct = max(0.0, min(1.0, boss_target.hp / max(1, boss_target.max_hp)))
    bar_w = min(440, vw - 120)
    bar_rect = pygame.Rect(vw // 2 - bar_w // 2, 52, bar_w, 18)
    
    pygame.draw.rect(canvas, (15, 23, 42, 240), bar_rect, border_radius=4)
    fill_w = int(round(bar_w * hp_pct))
    if fill_w > 0:
        pygame.draw.rect(canvas, COLOR_CRIMSON, (bar_rect.left, bar_rect.top, fill_w, 18), border_radius=4)
    pygame.draw.rect(canvas, COLOR_WHITE, bar_rect, 1, border_radius=4)
    
    boss_name = getattr(boss_target, "enemy_type", "BOSS").replace("_", " ").upper()
    lbl = font_card.render(f"⚠️ {boss_name}: {int(hp_pct * 100)}%", True, COLOR_WHITE)
    canvas.blit(lbl, lbl.get_rect(center=bar_rect.center))


def draw_combo_banner(canvas: pygame.Surface, combo_count: int, combo_timer: float):
    """Stub for backwards compatibility."""
    pass


def draw_radar_minimap(canvas: pygame.Surface, player, targets_group, wingmen_group=None):
    """Draws a radar minimap showing the player and enemies."""
    if not player or not player.alive:
        return
        
    vw, vh = canvas.get_size()
    radar_radius = 60
    radar_x = vw - radar_radius - 24
    radar_y = 120 + radar_radius  # Below score
    
    # Draw radar background (using alpha surface for transparency)
    radar_surface = pygame.Surface((radar_radius * 2, radar_radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(radar_surface, (15, 23, 42, 180), (radar_radius, radar_radius), radar_radius)
    pygame.draw.circle(radar_surface, COLOR_CYAN, (radar_radius, radar_radius), radar_radius, 1)
    
    # Crosshairs
    pygame.draw.line(radar_surface, (51, 65, 85, 150), (0, radar_radius), (radar_radius * 2, radar_radius))
    pygame.draw.line(radar_surface, (51, 65, 85, 150), (radar_radius, 0), (radar_radius, radar_radius * 2))
    
    # Player dot
    pygame.draw.circle(radar_surface, COLOR_EMERALD, (radar_radius, radar_radius), 3)
    
    # Scale: 60 pixels = 1200 world units -> scale = 0.05
    radar_scale = 0.05
    max_dist = radar_radius / radar_scale
    
    for enemy in targets_group:
        if not getattr(enemy, 'alive', False):
            continue
            
        dx = enemy.pos.x - player.pos.x
        dy = enemy.pos.y - player.pos.y
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            if dist > max_dist:
                dx = (dx / dist) * max_dist
                dy = (dy / dist) * max_dist
                
            px = radar_radius + int(dx * radar_scale)
            py = radar_radius + int(dy * radar_scale)
            
            color = getattr(enemy, 'color_outer', COLOR_CRIMSON)
            if dist > max_dist:
                pygame.draw.circle(radar_surface, color, (px, py), 2)
            else:
                pygame.draw.circle(radar_surface, color, (px, py), 3)
                
    canvas.blit(radar_surface, (radar_x - radar_radius, radar_y - radar_radius))
