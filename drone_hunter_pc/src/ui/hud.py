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
    COLOR_SHIELD, COLOR_OVERCLOCK, COLOR_WHITE, COLOR_NEON_RED, COLOR_TEXT_DIM
)
from src.data.game_data import WEAPON_DEFS
from src.data.mission_data import get_mission_data
from src.ui.font_manager import font_hud, font_card, font_banner, font_sub

def draw_hud(canvas: pygame.Surface, player, sector_idx: int = 0, level_score: int = 0, total_score: int = 0,
             scrap: int = 0, difficulty_name: str = "NORMAL", combo_mult: int = 1, show_crt: bool = False,
             current_wave: int = 1, sub_level: int = 1, mission_id: str | None = None, input_manager=None,
             objective_text: str | None = None, side_objectives: list | None = None, new_game_plus_count: int = 0,
             achievement_popups: list = None, objective_system=None):
    """Renders clean, responsive screen-space tactical HUD with dynamic device-aware action prompts."""
    vw, vh = canvas.get_size()
    margin_x = 24
    margin_y = 20

    # Low-health warning state (shared by HP bar and vignette)
    low_health = False
    if player:
        hp_pct = max(0.0, min(1.0, player.health / max(1.0, player.max_health)))
        low_health = hp_pct < 0.30

    # =========================================================================
    # 0.5 LOW-HEALTH VIGNETTE (red edge darkening when Hull < 30%)
    # =========================================================================
    if low_health:
        vignette_alpha = int(90 + 50 * math.sin(pygame.time.get_ticks() * 0.008))
        vignette = pygame.Surface((vw, vh), pygame.SRCALPHA)
        bar_h = max(1, int(vh * 0.22))
        pygame.draw.rect(vignette, (185, 28, 28, min(255, vignette_alpha // 2)), (0, 0, vw, bar_h))
        pygame.draw.rect(vignette, (185, 28, 28, min(255, vignette_alpha // 2)), (0, vh - bar_h, vw, bar_h))
        bar_w = max(1, int(vw * 0.18))
        pygame.draw.rect(vignette, (185, 28, 28, min(255, vignette_alpha // 3)), (0, 0, bar_w, vh))
        pygame.draw.rect(vignette, (185, 28, 28, min(255, vignette_alpha // 3)), (vw - bar_w, 0, bar_w, vh))
        canvas.blit(vignette, (0, 0))

    # Overdrive Vignette (golden edge glow when Overdrive is active)
    if player and getattr(player, "overdrive_timer", 0.0) > 0.0:
        od_alpha = int(60 + 30 * math.sin(pygame.time.get_ticks() * 0.02))
        od_vig = pygame.Surface((vw, vh), pygame.SRCALPHA)
        bar_h = max(1, int(vh * 0.18))
        pygame.draw.rect(od_vig, (245, 158, 11, min(255, od_alpha // 3)), (0, 0, vw, bar_h))
        pygame.draw.rect(od_vig, (245, 158, 11, min(255, od_alpha // 3)), (0, vh - bar_h, vw, bar_h))
        bar_w = max(1, int(vw * 0.15))
        pygame.draw.rect(od_vig, (245, 158, 11, min(255, od_alpha // 4)), (0, 0, bar_w, vh))
        pygame.draw.rect(od_vig, (245, 158, 11, min(255, od_alpha // 4)), (vw - bar_w, 0, bar_w, vh))
        canvas.blit(od_vig, (0, 0))

    # =========================================================================
    # 1. TOP-LEFT: Hull Integrity, Energy Status & Shield Pips
    # =========================================================================
    if player:
        # HP Hull Bar
        hp_pct = max(0.0, min(1.0, player.health / max(1.0, player.max_health)))
        hp_w = 160
        hp_h = 16
        
        hp_col = COLOR_EMERALD if hp_pct > 0.5 else (COLOR_GOLD if hp_pct > 0.25 else COLOR_CRIMSON)
        
        # Pulsing warning when critical
        if hp_pct < 0.25:
            pulse = int(30 * math.sin(pygame.time.get_ticks() * 0.012))
            hp_col = (
                min(255, max(0, hp_col[0] + pulse)),
                min(255, max(0, hp_col[1] + pulse // 3)),
                min(255, max(0, hp_col[2] + pulse // 3))
            )
        
        pygame.draw.rect(canvas, (15, 23, 42, 230), (margin_x, margin_y, hp_w, hp_h), border_radius=4)
        if hp_pct > 0:
            fill_w = int(round(hp_w * hp_pct))
            pygame.draw.rect(canvas, hp_col, (margin_x, margin_y, fill_w, hp_h), border_radius=4)
        pygame.draw.rect(canvas, (51, 65, 85), (margin_x, margin_y, hp_w, hp_h), 1, border_radius=4)
        
        txt_hp = font_card.render(f"HULL {int(player.health)} / {int(player.max_health)}", True, COLOR_WHITE)
        canvas.blit(txt_hp, (margin_x + hp_w + 12, margin_y - 1))

        # NRG Bar (Stacked right below Hull readout)
        nrg_y = margin_y + hp_h + 10
        nrg_pct = max(0.0, min(1.0, player.energy / max(1.0, player.max_energy)))
        nrg_w = 160
        nrg_h = 10
        
        pygame.draw.rect(canvas, (15, 23, 42, 230), (margin_x, nrg_y, nrg_w, nrg_h), border_radius=3)
        if nrg_pct > 0:
            fill_nrg = int(round(nrg_w * nrg_pct))
            pygame.draw.rect(canvas, COLOR_CYAN, (margin_x, nrg_y, fill_nrg, nrg_h), border_radius=3)
        pygame.draw.rect(canvas, (30, 58, 85), (margin_x, nrg_y, nrg_w, nrg_h), 1, border_radius=3)
        
        txt_nrg = font_card.render(f"NRG {int(player.energy)}%", True, COLOR_CYAN)
        canvas.blit(txt_nrg, (margin_x + nrg_w + 12, nrg_y - 3))

        # Shield Hit Charge Indicators
        if player.shield_hits > 0:
            sh_x = margin_x + hp_w + txt_hp.get_width() + 24
            for s_i in range(min(5, player.shield_hits)):
                pygame.draw.circle(canvas, COLOR_SHIELD, (sh_x + s_i * 12, margin_y + 8), 4)
                pygame.draw.circle(canvas, COLOR_WHITE, (sh_x + s_i * 12, margin_y + 8), 1)
            txt_sh = font_card.render(f"SHIELD x{player.shield_hits}", True, COLOR_SHIELD)
            canvas.blit(txt_sh, (sh_x + min(5, player.shield_hits) * 12 + 6, margin_y - 1))

        # EMP Jammed Alert Banner (Centered on screen)
        if player.is_jammed:
            jam_banner = font_banner.render(f"SYSTEM JAMMED: {player.emp_jammed_timer:.1f}s", True, COLOR_NEON_RED)
            canvas.blit(jam_banner, (vw // 2 - jam_banner.get_width() // 2, 70))

    # =========================================================================
    # 2. TOP-RIGHT: Level Telemetry & Clean Score Card
    # =========================================================================
    if mission_id:
        m_data = get_mission_data(mission_id) if isinstance(mission_id, str) else None
        if m_data:
            sec_num = m_data.get("sector_id", sector_idx + 1)
            m_num = m_data.get("mission_number", sub_level)
            level_str = f"SECTOR {sec_num}  |  STAGE {m_num}"
        else:
            level_str = f"SECTOR {sector_idx + 1}  |  STAGE {sub_level}"
    else:
        level_str = f"SECTOR {sector_idx + 1}  |  STAGE {sub_level}"
    lbl_level = font_card.render(level_str, True, COLOR_CYAN)
    
    score_str = f"SCORE: {level_score:,}"
    lbl_score = font_hud.render(score_str, True, COLOR_GOLD)
    
    max_w = max(lbl_level.get_width(), lbl_score.get_width()) + 28
    card_h = 52
    card_x = vw - margin_x - max_w
    card_rect = pygame.Rect(card_x, margin_y, max_w, card_h)
    
    pygame.draw.rect(canvas, (15, 23, 42, 220), card_rect, border_radius=6)
    pygame.draw.rect(canvas, (45, 65, 95), card_rect, 1, border_radius=6)
    
    canvas.blit(lbl_level, (card_x + 14, margin_y + 7))
    canvas.blit(lbl_score, (card_x + 14, margin_y + 26))

    # Compact Combo Streak Badge (stacked to the left of score card)
    if combo_mult > 1:
        combo_txt = f"COMBO x{combo_mult}"
        lbl_combo = font_card.render(combo_txt, True, COLOR_GOLD)
        combo_w = lbl_combo.get_width() + 16
        combo_rect = pygame.Rect(card_x - combo_w - 10, margin_y + 12, combo_w, 28)
        pygame.draw.rect(canvas, (245, 158, 11, 40), combo_rect, border_radius=4)
        pygame.draw.rect(canvas, COLOR_GOLD, combo_rect, 1, border_radius=4)
        canvas.blit(lbl_combo, (combo_rect.left + 8, combo_rect.top + 5))

    # =========================================================================
    # 2.5 GROUND OBJECTIVE ASSAULT TELEMETRY & RADAR ALERTS
    # =========================================================================
    if objective_system and getattr(objective_system, "is_active", False) and objective_system.active_objective:
        obj = objective_system.active_objective
        if obj.alive:
            # Top-Center Tactical Objective Card
            top_w = 360
            top_h = 44
            top_x = (vw - top_w) // 2
            top_y = margin_y
            top_rect = pygame.Rect(top_x, top_y, top_w, top_h)

            pygame.draw.rect(canvas, (15, 23, 42, 225), top_rect, border_radius=6)
            card_border = COLOR_SHIELD if obj.is_shielded else COLOR_GOLD
            pygame.draw.rect(canvas, card_border, top_rect, 1, border_radius=6)

            # Objective Name & Distance
            p_pos = (player.pos.x, player.pos.y) if player else (0, 0)
            dist_m = int(math.hypot(obj.pos.x - p_pos[0], obj.pos.y - p_pos[1]))
            t_obj_title = font_card.render(f"TARGET: {obj.title}  [{dist_m}m]", True, COLOR_WHITE)
            canvas.blit(t_obj_title, (top_x + 12, top_y + 5))

            # Shield Badge
            if obj.is_shielded:
                gens_alive = objective_system.active_shield_generators_count
                sh_txt = f"SHIELD ACTIVE ({gens_alive} GENS)"
                sh_lbl = font_sub.render(sh_txt, True, COLOR_SHIELD)
            else:
                sh_lbl = font_sub.render("SHIELD EXPOSED - VULNERABLE", True, COLOR_GOLD)
            canvas.blit(sh_lbl, (top_x + top_w - sh_lbl.get_width() - 12, top_y + 6))

            # Objective Health Bar
            hp_w = top_w - 24
            hp_h = 8
            hp_x = top_x + 12
            hp_y = top_y + 26
            pygame.draw.rect(canvas, (30, 41, 59), (hp_x, hp_y, hp_w, hp_h), border_radius=3)
            fill_w = max(0, int(hp_w * obj.hp_percent))
            bar_col = COLOR_SHIELD if obj.is_shielded else (COLOR_CRIMSON if obj.hp_percent < 0.3 else COLOR_GOLD)
            if fill_w > 0:
                pygame.draw.rect(canvas, bar_col, (hp_x, hp_y, fill_w, hp_h), border_radius=3)
            pygame.draw.rect(canvas, (51, 65, 85), (hp_x, hp_y, hp_w, hp_h), 1, border_radius=3)

            # Direction Navigation Arrow Indicator
            if player:
                dx = obj.pos.x - player.pos.x
                dy = obj.pos.y - player.pos.y
                nav_angle = math.atan2(dy, dx)
                nav_center_x = top_x - 22
                nav_center_y = top_y + top_h // 2
                arrow_len = 12
                ax = nav_center_x + math.cos(nav_angle) * arrow_len
                ay = nav_center_y + math.sin(nav_angle) * arrow_len
                lx = nav_center_x + math.cos(nav_angle + 2.5) * (arrow_len * 0.6)
                ly = nav_center_y + math.sin(nav_angle + 2.5) * (arrow_len * 0.6)
                rx = nav_center_x + math.cos(nav_angle - 2.5) * (arrow_len * 0.6)
                ry = nav_center_y + math.sin(nav_angle - 2.5) * (arrow_len * 0.6)
                pygame.draw.polygon(canvas, card_border, [(ax, ay), (lx, ly), (rx, ry)])

        # Radar Alert Warning Banner (when detected)
        if getattr(objective_system, "is_radar_alert_active", False):
            pulse_a = int(180 + 75 * math.sin(pygame.time.get_ticks() * 0.012))
            alert_lbl = font_card.render("⚠ RADAR ALERT: DEFENSE NETWORK ACTIVE ⚠", True, (239, 68, 68, pulse_a))
            alert_w = alert_lbl.get_width() + 20
            alert_h = 24
            alert_rect = pygame.Rect((vw - alert_w) // 2, margin_y + 48, alert_w, alert_h)
            pygame.draw.rect(canvas, (185, 28, 28, 45), alert_rect, border_radius=4)
            pygame.draw.rect(canvas, COLOR_NEON_RED, alert_rect, 1, border_radius=4)
            canvas.blit(alert_lbl, (alert_rect.left + 10, alert_rect.top + 4))

    # Objective Tracker
    elif objective_text:
        obj_txt = font_card.render(objective_text, True, COLOR_EMERALD)
        obj_rect = pygame.Rect(margin_x, margin_y + 45, obj_txt.get_width() + 16, 26)
        pygame.draw.rect(canvas, (15, 23, 42, 200), obj_rect, border_radius=4)
        pygame.draw.rect(canvas, COLOR_EMERALD, obj_rect, 1, border_radius=4)
        canvas.blit(obj_txt, (obj_rect.left + 8, obj_rect.top + 5))

    # Side Objectives Tracker
    if side_objectives:
        so_start_y = margin_y + 76
        for so in side_objectives:
            so_text = so.get("progress_text", so.get("description", ""))
            is_completed = so.get("completed", False)
            so_col = COLOR_EMERALD if is_completed else COLOR_TEXT_DIM
            prefix = "[x]" if is_completed else "[ ]"
            so_lbl = font_sub.render(f"{prefix} {so_text}", True, so_col)
            so_bg_w = so_lbl.get_width() + 14
            so_bg_h = 20
            so_bg_rect = pygame.Rect(margin_x, so_start_y, so_bg_w, so_bg_h)
            pygame.draw.rect(canvas, (15, 23, 42, 180), so_bg_rect, border_radius=3)
            pygame.draw.rect(canvas, so_col, so_bg_rect, 1, border_radius=3)
            canvas.blit(so_lbl, (so_bg_rect.left + 7, so_bg_rect.top + 3))
            so_start_y += 22

    # NG+ Cycle Indicator
    if new_game_plus_count > 0:
        ng_label = f"NEW GAME+ x{new_game_plus_count}"
        ng_lbl = font_banner.render(ng_label, True, COLOR_EMERALD)
        ng_w = ng_lbl.get_width() + 18
        ng_h = 28
        ng_x = margin_x
        ng_y = margin_y + 45 + (22 if side_objectives else 0) + 5
        ng_rect = pygame.Rect(ng_x, ng_y, ng_w, ng_h)
        pygame.draw.rect(canvas, (16, 185, 129, 50), ng_rect, border_radius=4)
        pygame.draw.rect(canvas, COLOR_EMERALD, ng_rect, 1, border_radius=4)
        canvas.blit(ng_lbl, (ng_rect.left + 9, ng_rect.top + 5))

    # =========================================================================
    # 3. BOTTOM-CENTER: Screen-Space Ability Indicators
    # =========================================================================
    if player:
        cloak_ready = (player.cloak_cooldown <= 0.0) or player.is_cloaked
        cloak_status = f"{player.cloak_timer:.1f}s" if player.is_cloaked else ("READY" if player.cloak_cooldown <= 0 else f"{player.cloak_cooldown:.1f}s")
        cloak_col = (168, 85, 247) if player.is_cloaked else ((147, 51, 234) if player.cloak_cooldown <= 0 else (75, 85, 99))

        roll_p = input_manager.get_prompt_for_action("ROLL") if input_manager else "SHIFT"
        cloak_p = input_manager.get_prompt_for_action("CLOAK") if input_manager else "C"
        emp_p = input_manager.get_prompt_for_action("EMP") if input_manager else "E"
        ult_p = input_manager.get_prompt_for_action("ULTIMATE") if input_manager else "F"

        abilities = [
            (f"[{roll_p}] ROLL", player.roll_cooldown <= 0.0, COLOR_EMERALD, f"{player.roll_cooldown:.1f}s" if player.roll_cooldown > 0 else "READY"),
            (f"[{cloak_p}] CLOAK", cloak_ready, cloak_col, cloak_status),
            (f"[{emp_p}] EMP", player.emp_cooldown <= 0.0, COLOR_CYAN, f"{player.emp_cooldown:.1f}s" if player.emp_cooldown > 0 else "READY"),
            (f"[{ult_p}] ULT", player.overdrive_cooldown <= 0.0 or player.overdrive_timer > 0, COLOR_GOLD if player.overdrive_cooldown <= 0 else COLOR_OVERCLOCK,
             f"{player.overdrive_timer:.1f}s" if player.overdrive_timer > 0 else ("READY" if player.overdrive_cooldown <= 0 else f"{player.overdrive_cooldown:.0f}s")),
        ]
        
        pill_w = 95
        pill_h = 28
        gap = 8
        total_w = len(abilities) * pill_w + (len(abilities) - 1) * gap
        start_x = (vw - total_w) // 2
        p_y = vh - margin_y - pill_h - 6

        for idx, (name, ready, col, status_str) in enumerate(abilities):
            px = start_x + idx * (pill_w + gap)
            p_rect = pygame.Rect(px, p_y, pill_w, pill_h)
            pygame.draw.rect(canvas, (15, 23, 42, 220), p_rect, border_radius=5)
            pygame.draw.rect(canvas, col if ready else (45, 55, 75), p_rect, 1, border_radius=5)
            
            lbl_str = f"{name} {status_str}" if status_str != "READY" else name
            txt_name = font_card.render(lbl_str, True, col if ready else (120, 135, 155))
            canvas.blit(txt_name, txt_name.get_rect(center=p_rect.center))

    # =========================================================================
    # 4. BOTTOM-RIGHT: Clean Weapon Slot Indicator List
    # =========================================================================
    if player:
        wpn_h = 26
        start_y = vh - margin_y - wpn_h - 6
        slot_names = ["PRIMARY", "SECONDARY", "HEAVY", "SPECIAL"]
        now_ms = pygame.time.get_ticks()
        
        for idx, w_id in reversed(list(enumerate(player.available_weapons))):
            w_def = WEAPON_DEFS.get(w_id, {})
            w_name = w_def.get("name", "Unknown").upper()
            w_col = w_def.get("color", COLOR_CYAN)
            slot_tag = slot_names[idx] if idx < len(slot_names) else f"SLOT {idx+1}"
            
            is_active = (player.active_weapon == w_id)
            cd = player.weapon_cooldowns.get(w_id, 0.0)
            
            if cd > 0:
                lbl_text = f"[{idx+1}] {slot_tag}: {w_name} ({cd:.1f}s)"
                text_col = (120, 135, 155)
                box_border = (45, 55, 75)
                bg_col = (15, 23, 42, 220)
            else:
                lbl_text = f"[{idx+1}] {slot_tag}: {w_name}"
                text_col = w_col if is_active else (200, 200, 200)
                box_border = w_col if is_active else (70, 80, 100)
                bg_col = (30, 40, 60, 240) if is_active else (15, 23, 42, 220)

            lbl_wpn = font_card.render(lbl_text, True, text_col)
            wpn_w = lbl_wpn.get_width() + 18
            wpn_x = vw - margin_x - wpn_w
            
            wpn_rect = pygame.Rect(wpn_x, start_y, wpn_w, wpn_h)
            pygame.draw.rect(canvas, bg_col, wpn_rect, border_radius=5)
            
            # Active weapon: stronger left-edge glow bar + subtle pulse
            if is_active:
                pulse = int(40 + 30 * math.sin(now_ms * 0.01))
                glow_bar = pygame.Rect(wpn_x, start_y + 3, 4, wpn_h - 6)
                pygame.draw.rect(canvas, w_col, glow_bar, border_radius=2)
                # Outer glow halo
                halo_alpha = min(255, 100 + pulse)
                halo_surf = pygame.Surface((wpn_w, wpn_h), pygame.SRCALPHA)
                pygame.draw.rect(halo_surf, (*w_col, halo_alpha // 4), (0, 0, wpn_w, wpn_h), border_radius=5)
                canvas.blit(halo_surf, (wpn_x, start_y))
                border_width = 2
            else:
                border_width = 1
            
            pygame.draw.rect(canvas, box_border, wpn_rect, border_width, border_radius=5)
            canvas.blit(lbl_wpn, (wpn_x + 9, start_y + 5))
            
            start_y -= (wpn_h + 5)

    # Achievement Popup Notifications
    if achievement_popups:
        popup_y = vh - 120
        for popup in achievement_popups:
            if popup.get("timer", 0) <= 0:
                continue
            icon = popup.get("icon", "")
            name = popup.get("name", "")
            desc = popup.get("description", "")
            pct = max(0.0, min(1.0, popup["timer"] / 3.0))
            alpha = int(255 * pct)
            popup_w = 320
            popup_h = 56
            popup_rect = pygame.Rect(margin_x, popup_y, popup_w, popup_h)
            bg_surf = pygame.Surface((popup_w, popup_h), pygame.SRCALPHA)
            bg_surf.fill((15, 23, 42, min(255, alpha * 220 // 255)))
            canvas.blit(bg_surf, (margin_x, popup_y))
            pygame.draw.rect(canvas, (245, 158, 11, min(255, alpha * 180 // 255)), popup_rect, 2, border_radius=6)
            t_icon = font_card.render(icon, True, COLOR_GOLD)
            t_name = font_card.render(name, True, COLOR_WHITE)
            t_desc = font_card.render(desc, True, COLOR_TEXT_DIM)
            canvas.blit(t_icon, (popup_rect.left + 10, popup_rect.top + 8))
            canvas.blit(t_name, (popup_rect.left + 36, popup_rect.top + 6))
            canvas.blit(t_desc, (popup_rect.left + 36, popup_rect.top + 28))
            popup_y -= (popup_h + 6)



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
    """Renders animated combo streak banner when combo_count > 1."""
    if combo_count <= 1 or combo_timer <= 0:
        return
    vw, vh = canvas.get_size()
    pct = max(0.0, min(1.0, combo_timer / 2.5))
    alpha = int(255 * pct)
    scale = 1.0 + (1.0 - pct) * 0.3
    txt = f"x{combo_count} COMBO!"
    rendered = font_banner.render(txt, True, COLOR_GOLD)
    w, h = rendered.get_size()
    scaled_w, scaled_h = int(w * scale), int(h * scale)
    surf = pygame.transform.smoothscale(rendered, (scaled_w, scaled_h))
    surf.set_alpha(alpha)
    rect = surf.get_rect(center=(vw // 2, vh // 3))
    canvas.blit(surf, rect)


def draw_wave_announcement(canvas: pygame.Surface, wave_number: int, announcement_timer: float):
    """Renders wave incoming announcement banner with fade-out."""
    if announcement_timer <= 0 or wave_number <= 0:
        return
    vw, vh = canvas.get_size()
    pct = max(0.0, min(1.0, announcement_timer / 2.0))
    alpha = int(255 * pct)
    scale = 1.0 + (1.0 - pct) * 0.15
    txt = f"WAVE {wave_number}"
    rendered = font_banner.render(txt, True, COLOR_CRIMSON)
    w, h = rendered.get_size()
    scaled_w, scaled_h = int(w * scale), int(h * scale)
    surf = pygame.transform.smoothscale(rendered, (scaled_w, scaled_h))
    surf.set_alpha(alpha)
    rect = surf.get_rect(center=(vw // 2, vh // 3))
    canvas.blit(surf, rect)


RATING_COLORS = {
    "S": (245, 158, 11),
    "A": (16, 185, 129),
    "B": (59, 130, 246),
    "C": (239, 68, 68),
}


def draw_boss_rating(canvas: pygame.Surface, rating_data: dict):
    """Renders animated boss performance rating popup (S/A/B/C)."""
    if not rating_data:
        return

    rating = rating_data.get("rating", "B")
    boss_name = rating_data.get("boss_name", "BOSS")
    duration = rating_data.get("duration", 0.0)
    dmg_taken = rating_data.get("damage_taken", 0)
    col = RATING_COLORS.get(rating, (255, 255, 255))

    vw, vh = canvas.get_size()
    cx, cy = vw // 2, vh // 2 - 20

    bg_w, bg_h = 340, 150
    bg_rect = pygame.Rect(cx - bg_w // 2, cy - bg_h // 2, bg_w, bg_h)
    pygame.draw.rect(canvas, (8, 12, 24, 220), bg_rect, border_radius=10)
    pygame.draw.rect(canvas, col, bg_rect, 2, border_radius=10)

    t_rank = font_banner.render(rating, True, col)
    canvas.blit(t_rank, t_rank.get_rect(center=(cx, cy - 30)))

    t_name = font_card.render(boss_name.upper(), True, COLOR_WHITE)
    canvas.blit(t_name, t_name.get_rect(center=(cx, cy + 5)))

    t_stats = font_sub.render(f"TIME: {duration:.1f}s  |  DMG: {int(dmg_taken)}", True, (180, 195, 215))
    canvas.blit(t_stats, t_stats.get_rect(center=(cx, cy + 38)))




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
