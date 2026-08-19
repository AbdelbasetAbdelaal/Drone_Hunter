import os
import math
import pygame
from src.data.settings import COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_EMERALD, COLOR_WHITE

class SpriteManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SpriteManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, assets_dir: str = 'drone_hunter_pc/assets/sprites'):
        if getattr(self, '_initialized', False):
            return

        self.base_dir = assets_dir
        if not os.path.exists(self.base_dir):
            alt = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'sprites')
            if os.path.exists(alt):
                self.base_dir = alt

        self._raw_cache: dict[str, pygame.Surface] = {}
        self._scaled_cache: dict[tuple, pygame.Surface] = {}
        self._rotated_cache: dict[tuple, pygame.Surface] = {}
        self._skin_cache: dict[tuple, pygame.Surface] = {}
        self._shadow_cache: dict[tuple, pygame.Surface] = {}

        self._initialized = True
        self._preload_player_assets()

    def _load_raw_image(self, rel_path: str) -> pygame.Surface | None:
        if rel_path in self._raw_cache:
            return self._raw_cache[rel_path]

        full_path = os.path.join(self.base_dir, rel_path)
        if not os.path.exists(full_path):
            return None

        try:
            if not pygame.get_init() or not pygame.display.get_init():
                surf = pygame.image.load(full_path).convert_alpha()
            else:
                surf = pygame.image.load(full_path)
                if pygame.display.get_surface():
                    surf = surf.convert_alpha()
            self._raw_cache[rel_path] = surf
            return surf
        except Exception:
            return None

    def _preload_player_assets(self):
        for state in ['idle', 'move', 'fire', 'hit', 'destroy', 'bank_left', 'bank_right']:
            self._load_raw_image(f'player/player_{state}.png')
        self._load_raw_image('shadows/player_shadow.png')
        self._load_raw_image('vfx/engine_flame.png')

    def get_player_sprite(self, state: str = 'idle', skin_idx: int = 0, target_size: tuple[int, int] = (64, 56)) -> pygame.Surface:
        cache_key = (state, skin_idx, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        raw = self._load_raw_image(f'player/player_{state}.png')
        if raw is None:
            raw = self._load_raw_image('player/player_idle.png')

        if raw is None:
            fallback = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.polygon(fallback, (36, 48, 68), [
                (target_size[0] - 4, target_size[1] // 2),
                (4, 4),
                (12, target_size[1] // 2),
                (4, target_size[1] - 4)
            ])
            self._skin_cache[cache_key] = fallback
            return fallback

        scaled = pygame.transform.smoothscale(raw, target_size)

        if skin_idx > 0:
            tinted = scaled.copy()
            tint_color = COLOR_CRIMSON if skin_idx == 1 else (
                COLOR_GOLD if skin_idx == 2 else COLOR_EMERALD
            )
            overlay = pygame.Surface(target_size, pygame.SRCALPHA)
            overlay.fill((tint_color[0], tint_color[1], tint_color[2], 90))
            tinted.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
            scaled = tinted

        self._skin_cache[cache_key] = scaled
        return scaled

    def get_player_shadow(self, target_size: tuple[int, int] = (64, 56)) -> pygame.Surface:
        if target_size in self._shadow_cache:
            return self._shadow_cache[target_size]

        raw = self._load_raw_image('shadows/player_shadow.png')
        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[target_size] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(110)
        self._shadow_cache[target_size] = shadow
        return shadow

    def get_rotated_surface(self, surf: pygame.Surface, angle_deg: float) -> pygame.Surface:
        quantized_angle = int(round(angle_deg / 2.0)) * 2 % 360
        surf_id = id(surf)
        cache_key = (surf_id, quantized_angle)

        if cache_key in self._rotated_cache:
            return self._rotated_cache[cache_key]

        rotated = pygame.transform.rotate(surf, quantized_angle)
        self._rotated_cache[cache_key] = rotated
        return rotated

    def get_rotated_player_sprite(self, state: str = 'idle', skin_idx: int = 0, angle_deg: float = 0.0, target_size: tuple[int, int] = (68, 58)) -> pygame.Surface:
        """Returns pre-cached, rotated, skin-tinted player sprite (quantized to 2 deg)."""
        quantized_angle = int(round(angle_deg / 2.0)) * 2 % 360
        cache_key = (state, skin_idx, target_size, quantized_angle)

        if cache_key in self._rotated_cache:
            return self._rotated_cache[cache_key]

        base_sprite = self.get_player_sprite(state=state, skin_idx=skin_idx, target_size=target_size)
        rotated = pygame.transform.rotate(base_sprite, quantized_angle)
        self._rotated_cache[cache_key] = rotated
        return rotated


_sprite_manager = None

def get_sprite_manager() -> SpriteManager:
    global _sprite_manager
    if _sprite_manager is None:
        _sprite_manager = SpriteManager()
    return _sprite_manager
