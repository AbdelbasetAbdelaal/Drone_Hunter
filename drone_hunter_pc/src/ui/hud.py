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
             scrap: int = 0, difficulty_name: str = "NORMAL", combo_mult: int = 1, show_crt: bool = False,
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
    # 4. BOTTOM-RIGHT: Compact Weapon Indicator List
    # =========================================================================
    if player:
        wpn_h = 26
        # Draw from bottom up
        start_y = vh - margin_y - wpn_h
        
        for idx, w_id in reversed(list(enumerate(player.available_weapons))):
            w_def = WEAPON_DEFS.get(w_id, {})
            w_name = w_def.get("name", "Unknown").upper()
            w_col = w_def.get("color", COLOR_CYAN)
            w_icon = w_def.get("icon", "⚡")
            
            is_active = (player.active_weapon == w_id)
            cd = player.weapon_cooldowns.get(w_id, 0.0)
            
            if cd > 0:
                lbl_text = f"[{idx+1}] {w_name} ({cd:.1f}s)"
                text_col = (120, 135, 155)
                box_border = (45, 55, 75)
                bg_col = (15, 23, 42, 220)
            else:
                lbl_text = f"[{idx+1}] {w_name}"
                text_col = w_col if is_active else (200, 200, 200)
                box_border = w_col if is_active else (80, 90, 110)
                bg_col = (30, 40, 60, 240) if is_active else (15, 23, 42, 220)

            lbl_wpn = font_card.render(f"{w_icon} {lbl_text}", True, text_col)
            wpn_w = lbl_wpn.get_width() + 16
            wpn_x = vw - margin_x - wpn_w
            
            wpn_rect = pygame.Rect(wpn_x, start_y, wpn_w, wpn_h)
            pygame.draw.rect(canvas, bg_col, wpn_rect, border_radius=5)
            pygame.draw.rect(canvas, box_border, wpn_rect, 1, border_radius=5)
            canvas.blit(lbl_wpn, (wpn_x + 8, start_y + 5))
            
            start_y -= (wpn_h + 4)


def draw_boss_intro_warning(canvas: pygame.Surface, boss_name: str, timer: float = 2.0):
    """Renders high-visibility tactical warning banner when a Boss enters arena."""
    vw, vh = canvas.get_size()
    
    # Flashing warning alpha
    pulse = math.sin(pygame.time.get_ticks() * 0.015)
    banner_alpha = int(180 + 75 * pulse)
    
    banner_w = min(680, vw - 80)
    banner_h = 100
    banner_rect = pygame.Rect(vw // 2 - banner_w // 2, vh // 3 - banner_h // 2, banner_w, banner_h)
    
    # Dark panel with crimson border
    pygame.draw.rect(canvas, (15, 5, 10, banner_alpha), banner_rect, border_radius=8)
    pygame.draw.rect(canvas, COLOR_CRIMSON, banner_rect, 2, border_radius=8)
    
    # Text readouts (ASCII-safe)
    t_warn = font_card.render(">>> WARNING: HOSTILE COMMAND UNIT DETECTED <<<", True, COLOR_CRIMSON)
    t_name = font_banner.render(f"[ {boss_name.upper()} ]", True, COLOR_GOLD)
    t_sub = font_card.render("TACTICAL ENGAGEMENT IMMINENT", True, COLOR_WHITE)
    
    canvas.blit(t_warn, t_warn.get_rect(center=(vw // 2, banner_rect.top + 22)))
    canvas.blit(t_name, t_name.get_rect(center=(vw // 2, banner_rect.top + 50)))
    canvas.blit(t_sub, t_sub.get_rect(center=(vw // 2, banner_rect.top + 78)))


def draw_boss_health_bar(canvas: pygame.Surface, boss_target):
    """Renders Phase 6 Boss Health Bar with phase badge and shield status."""
    if not boss_target or not getattr(boss_target, "alive", False):
        return
    vw, vh = canvas.get_size()
    max_hp = max(1, getattr(boss_target, "max_hp", 100))
    hp = max(0, getattr(boss_target, "hp", 0))
    hp_pct = max(0.0, min(1.0, hp / max_hp))
    
    bar_w = min(500, vw - 120)
    bar_h = 18
    bx = vw // 2 - bar_w // 2
    by = 48
    bar_rect = pygame.Rect(bx, by, bar_w, bar_h)
    
    # Boss Name Header
    boss_name = getattr(boss_target, "boss_name", getattr(boss_target, "enemy_type", "BOSS")).replace("_", " ").upper()
    phase_str = getattr(boss_target, "current_phase_name", f"PHASE {getattr(boss_target, 'current_phase_number', 1)}")
    
    # Outer Background
    pygame.draw.rect(canvas, (10, 15, 26, 230), (bx - 10, by - 24, bar_w + 20, bar_h + 32), border_radius=6)
    pygame.draw.rect(canvas, (30, 45, 65), (bx - 10, by - 24, bar_w + 20, bar_h + 32), 1, border_radius=6)
    
    # Title & Phase text
    t_hdr = font_card.render(boss_name, True, COLOR_CRIMSON)
    t_phase = font_card.render(f"[{phase_str}]", True, COLOR_GOLD)
    canvas.blit(t_hdr, (bx, by - 21))
    canvas.blit(t_phase, (bx + bar_w - t_phase.get_width(), by - 21))
    
    # Health Fill
    pygame.draw.rect(canvas, (20, 25, 35), bar_rect, border_radius=4)
    fill_w = int(round(bar_w * hp_pct))
    if fill_w > 0:
        bar_col = COLOR_CRIMSON if hp_pct <= 0.35 else (COLOR_GOLD if hp_pct <= 0.70 else COLOR_EMERALD)
        pygame.draw.rect(canvas, bar_col, (bx, by, fill_w, bar_h), border_radius=4)
    pygame.draw.rect(canvas, COLOR_WHITE, bar_rect, 1, border_radius=4)
    
    # Numeric Readout & Shield Status
    hp_text = f"{int(hp)} / {int(max_hp)}"
    if getattr(boss_target, "is_shielded", False):
        hp_text += " [SHIELD ACTIVE]"
    t_hp = font_card.render(hp_text, True, COLOR_WHITE)
    canvas.blit(t_hp, t_hp.get_rect(center=bar_rect.center))


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
    radar_y = 120 + radar_radius
    
    if not hasattr(draw_radar_minimap, "_radar_bg"):
        draw_radar_minimap._radar_bg = pygame.Surface((radar_radius * 2, radar_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(draw_radar_minimap._radar_bg, (15, 23, 42, 180), (radar_radius, radar_radius), radar_radius)
        pygame.draw.circle(draw_radar_minimap._radar_bg, COLOR_CYAN, (radar_radius, radar_radius), radar_radius, 1)
        pygame.draw.line(draw_radar_minimap._radar_bg, (51, 65, 85, 150), (0, radar_radius), (radar_radius * 2, radar_radius))
        pygame.draw.line(draw_radar_minimap._radar_bg, (51, 65, 85, 150), (radar_radius, 0), (radar_radius, radar_radius * 2))
        pygame.draw.circle(draw_radar_minimap._radar_bg, COLOR_EMERALD, (radar_radius, radar_radius), 3)
    
    radar_surface = draw_radar_minimap._radar_bg.copy()
    
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
