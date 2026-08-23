import pygame
from src.data.settings import COLOR_CYAN, COLOR_CRIMSON, COLOR_EMERALD, COLOR_GOLD, COLOR_WHITE, SCREEN_WIDTH, SCREEN_HEIGHT
from src.ui.font_manager import font_header, font_card, font_sub
from src.data.game_data import DRONE_CLASSES, DRONE_CLASS_STRIKER, DRONE_CLASS_INTERCEPTOR, DRONE_CLASS_ASSAULT, DRONE_CLASS_ARC, DRONE_CLASS_COMMAND, WEAPON_DEFS

def draw_drone_select_ui(canvas: pygame.Surface, mouse_pos: tuple[int, int], sprite_manager, selected_index: int = None) -> dict:
    """Renders the Drone Selection Screen with visually clickable drone options."""
    vw, vh = canvas.get_size()
    mx, my = mouse_pos
    cache = {'drones': {}}

    # Semi-transparent background overlay
    overlay = pygame.Surface((vw, vh), pygame.SRCALPHA)
    overlay.fill((10, 15, 25, 230))
    canvas.blit(overlay, (0, 0))

    # Header
    title = font_header.render("SELECT COMBAT CHASSIS", True, COLOR_CYAN)
    title_rect = title.get_rect(center=(vw // 2, 65))
    canvas.blit(title, title_rect)

    subtitle = font_sub.render("CHOOSE YOUR FLIGHT PROFILE AND WEAPON LOADOUT BEFORE DEPLOYMENT", True, COLOR_GOLD)
    subtitle_rect = subtitle.get_rect(center=(vw // 2, 110))
    canvas.blit(subtitle, subtitle_rect)

    classes_list = [
        DRONE_CLASS_STRIKER,
        DRONE_CLASS_INTERCEPTOR,
        DRONE_CLASS_ASSAULT,
        DRONE_CLASS_ARC,
        DRONE_CLASS_COMMAND
    ]

    # Calculate layout
    card_w = 230
    card_h = 440
    gap = 20
    total_w = (card_w * len(classes_list)) + (gap * (len(classes_list) - 1))
    start_x = (vw - total_w) // 2
    start_y = 150

    for idx, class_id in enumerate(classes_list):
        c_info = DRONE_CLASSES[class_id]
        cx = start_x + (idx * (card_w + gap))
        cy = start_y
        rect = pygame.Rect(cx, cy, card_w, card_h)
        
        is_hover = rect.collidepoint(mx, my) or (selected_index == idx)
        
        # Draw Card Background
        bg_col = (28, 48, 78) if is_hover else (15, 24, 40)
        border_col = COLOR_WHITE if is_hover else COLOR_CYAN
        
        pygame.draw.rect(canvas, bg_col, rect, border_radius=12)
        pygame.draw.rect(canvas, border_col, rect, 3 if is_hover else 1, border_radius=12)
        
        cache['drones'][idx] = rect

        # Title & Role
        t_name = font_card.render(c_info['name'], True, COLOR_WHITE if is_hover else COLOR_CYAN)
        n_rect = t_name.get_rect(center=(cx + card_w // 2, cy + 22))
        canvas.blit(t_name, n_rect)
        
        role_text = c_info['role'].upper()
        # Truncate clean role if too long for card
        if len(role_text) > 24:
            role_text = role_text.split('/')[0].strip()
        t_role = font_sub.render(role_text, True, COLOR_GOLD)
        r_rect = t_role.get_rect(center=(cx + card_w // 2, cy + 45))
        canvas.blit(t_role, r_rect)

        # Draw Drone Sprite Preview
        preview_sprite = sprite_manager.get_rotated_player_sprite(state='idle', skin_idx=idx, angle_deg=270.0, target_size=(100, 100))
        s_rect = preview_sprite.get_rect(center=(cx + card_w // 2, cy + 120))
        canvas.blit(preview_sprite, s_rect)

        # Stats
        spd_val = int(420.0 * c_info['speed_mult'])
        hp_val = c_info['max_health']
        
        pygame.draw.line(canvas, (40, 60, 90), (cx + 20, cy + 195), (cx + card_w - 20, cy + 195), 1)
        
        t_spd = font_sub.render(f"SPEED: {spd_val}", True, COLOR_WHITE)
        canvas.blit(t_spd, (cx + 20, cy + 205))
        
        t_hp = font_sub.render(f"HULL: {hp_val} HP", True, COLOR_WHITE)
        canvas.blit(t_hp, (cx + 20, cy + 225))

        # Weapons
        pygame.draw.line(canvas, (40, 60, 90), (cx + 20, cy + 255), (cx + card_w - 20, cy + 255), 1)
        t_wpns_hdr = font_sub.render("LOADOUT:", True, COLOR_EMERALD)
        canvas.blit(t_wpns_hdr, (cx + 20, cy + 265))
        
        wy = cy + 290
        for w_idx, w_id in enumerate(c_info.get("weapons", [])[:4]):
            w_d = WEAPON_DEFS.get(w_id, {})
            w_name = w_d.get('name', w_id).upper()
            t_w = font_sub.render(f"• {w_name}", True, (180, 195, 215))
            canvas.blit(t_w, (cx + 25, wy))
            wy += 22

    # Back Button
    back_rect = pygame.Rect(30, vh - 60, 150, 42)
    b_hover = back_rect.collidepoint(mx, my) or (selected_index == 5)
    pygame.draw.rect(canvas, (60, 20, 25) if b_hover else (20, 10, 10), back_rect, border_radius=6)
    pygame.draw.rect(canvas, COLOR_WHITE if b_hover else COLOR_CRIMSON, back_rect, 2 if b_hover else 1, border_radius=6)
    t_back = font_card.render("[ESC] BACK", True, COLOR_WHITE if b_hover else COLOR_CRIMSON)
    canvas.blit(t_back, t_back.get_rect(center=back_rect.center))
    cache['back'] = back_rect

    return cache
