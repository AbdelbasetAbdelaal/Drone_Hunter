"""
================================================================================
                DRONE HUNTER 2D - PLAYER MOVEMENT & KINEMATICS
================================================================================
Manages 2D kinematic flight physics, boundary clamping, lateral banking,
and mouse/analog orientation for the player combat drone.
"""

import math
import pygame
from src.data.settings import WORLD_WIDTH, WORLD_HEIGHT
from src.data.game_data import (
    HORIZONTAL_SPEED, ACCELERATION, FRICTION,
    get_drone_class_by_id, DRONE_MOUNT_PROFILES
)


class MovementController:
    """Encapsulates 2D kinematic flight physics, boundary clamping, and aiming."""

    def __init__(self, pos: tuple[float, float] = (WORLD_WIDTH // 2, WORLD_HEIGHT // 2)):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(0, 0)
        self.acceleration = 6400.0
        self.drag = 5.0
        self.max_speed = HORIZONTAL_SPEED
        self.is_accelerating = False

        self.aim_angle = 0.0
        self.facing_angle_deg = 0.0
        self.tilt_y = 0.0

        self.arena_width = float(WORLD_WIDTH)
        self.arena_height = float(WORLD_HEIGHT)

    def configure_drone_class(self, class_data: dict):
        """Applies movement multipliers from drone class definitions."""
        self.max_speed = HORIZONTAL_SPEED * class_data.get("speed_mult", 1.0)
        self.acceleration = 6400.0 * class_data.get("accel_mult", 1.0)
        self.drag = 5.0

    def get_mount_world_pos(self, drone_class_id: str, mount_name: str = "primary") -> tuple[float, float]:
        """Calculates rotated world coordinates for a local-space weapon mount point."""
        drone_class = get_drone_class_by_id(drone_class_id)
        class_id = drone_class.get("class_id", "striker")

        profile = DRONE_MOUNT_PROFILES.get(class_id, drone_class.get("mounts", {}))
        fallback = profile.get("primary", (38.0, 0.0))
        fwd_off, lat_off = profile.get(mount_name, fallback)

        cos_a = math.cos(self.aim_angle)
        sin_a = math.sin(self.aim_angle)
        world_x = self.pos.x + (cos_a * fwd_off) + (-sin_a * lat_off)
        world_y = self.pos.y + (sin_a * fwd_off) + (cos_a * lat_off)
        return (world_x, world_y)

    def handle_input(
        self,
        keys,
        dt: float,
        mouse_pos: tuple[float, float] = None,
        input_state: dict = None,
        agility_mult: float = 1.0,
        current_max_speed: float = None
    ):
        """Processes 360-degree vector flight kinematics, lateral banking, and aiming."""
        move_x = 0.0
        move_y = 0.0

        if input_state:
            move_x = input_state.get("move_x", 0.0)
            move_y = input_state.get("move_y", 0.0)
            aim_angle_override = input_state.get("aim_angle", None)
            if aim_angle_override is not None:
                self.aim_angle = aim_angle_override
        else:
            def _is_pressed(k):
                if isinstance(keys, dict):
                    return keys.get(k, False)
                try:
                    return bool(keys[k])
                except (IndexError, KeyError):
                    return False

            if _is_pressed(pygame.K_w) or _is_pressed(pygame.K_UP): move_y -= 1.0
            if _is_pressed(pygame.K_s) or _is_pressed(pygame.K_DOWN): move_y += 1.0
            if _is_pressed(pygame.K_a) or _is_pressed(pygame.K_LEFT): move_x -= 1.0
            if _is_pressed(pygame.K_d) or _is_pressed(pygame.K_RIGHT): move_x += 1.0

        move_vec = pygame.Vector2(move_x, move_y)
        if move_vec.length_squared() > 0.0:
            if not input_state and move_vec.length_squared() > 1.0:
                move_vec = move_vec.normalize()
            self.is_accelerating = True
            self.velocity += move_vec * (self.acceleration * agility_mult) * dt
        else:
            self.is_accelerating = False

        # Linear Inertial Drag & Smooth Deceleration
        drag_damping = max(0.0, 1.0 - (self.drag * dt))
        self.velocity *= drag_damping

        # Clamp Max Speed
        current_max = current_max_speed if current_max_speed is not None else self.max_speed * agility_mult
        if self.velocity.length() > current_max:
            self.velocity.scale_to_length(current_max)

        # Update Aim Direction from Mouse (World Coordinates) if right stick aim is inactive
        if mouse_pos and (not input_state or input_state.get("aim_angle") is None):
            self.aim_angle = math.atan2(mouse_pos[1] - self.pos.y, mouse_pos[0] - self.pos.x)

        # Smooth Lateral Velocity Banking relative to Aim Angle
        cos_a = math.cos(self.aim_angle)
        sin_a = math.sin(self.aim_angle)
        lateral_speed = (-sin_a * self.velocity.x) + (cos_a * self.velocity.y)
        target_tilt = max(-26.0, min(26.0, (lateral_speed / max(1.0, current_max)) * 32.0))
        self.tilt_y += (target_tilt - self.tilt_y) * min(1.0, 12.0 * dt)

    def update(self, dt: float):
        """Integrates position and enforces arena boundary clamping."""
        self.pos += self.velocity * dt

        # Smooth World Arena Boundary Clamping
        pad = 36.0
        self.pos.x = max(pad, min(self.arena_width - pad, self.pos.x))
        self.pos.y = max(pad, min(self.arena_height - pad, self.pos.y))
