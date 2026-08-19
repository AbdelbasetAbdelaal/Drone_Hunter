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
        for s_idx in range(5):
            self._load_raw_image(f'player/chassis_{s_idx}.png')
        self._load_raw_image('shadows/player_shadow.png')
        self._load_raw_image('vfx/engine_flame.png')

    def get_player_sprite(self, state: str = 'idle', skin_idx: int = 0, target_size: tuple[int, int] = (90, 78)) -> pygame.Surface:
        cache_key = (state, skin_idx, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        raw = self._load_raw_image(f'player/chassis_{skin_idx}.png')
        if raw is None:
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
        self._skin_cache[cache_key] = scaled
        return scaled

    def get_player_shadow(self, target_size: tuple[int, int] = (76, 48)) -> pygame.Surface:
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

    def get_rotated_player_sprite(self, state: str = 'idle', skin_idx: int = 0, angle_deg: float = 0.0, target_size: tuple[int, int] = (90, 78)) -> pygame.Surface:
        """Returns pre-cached, rotated, skin-tinted player sprite (quantized to 2 deg)."""
        quantized_angle = int(round(angle_deg / 2.0)) * 2 % 360
        cache_key = (state, skin_idx, target_size, quantized_angle)

        if cache_key in self._rotated_cache:
            return self._rotated_cache[cache_key]

        base_sprite = self.get_player_sprite(state=state, skin_idx=skin_idx, target_size=target_size)
        rotated = pygame.transform.rotate(base_sprite, quantized_angle)
        self._rotated_cache[cache_key] = rotated
        return rotated

    def get_scout_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (52, 46)) -> pygame.Surface:
        """Returns cached, scaled 2D Scout drone sprite."""
        cache_key = ('scout', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        raw = self._load_raw_image(f'enemies/scout/scout_{state}.png')
        if raw is None:
            raw = self._load_raw_image('enemies/scout/scout_idle.png')
        if raw is None:
            raw = self._load_raw_image('enemies/scout/scout_base.png')

        if raw is None:
            fallback = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.polygon(fallback, (244, 63, 94), [
                (target_size[0] - 2, target_size[1] // 2),
                (2, 2),
                (8, target_size[1] // 2),
                (2, target_size[1] - 2)
            ])
            self._skin_cache[cache_key] = fallback
            return fallback

        scaled = pygame.transform.smoothscale(raw, target_size)
        self._skin_cache[cache_key] = scaled
        return scaled

    def get_rotated_scout_sprite(self, state: str = 'idle', angle_deg: float = 0.0, target_size: tuple[int, int] = (44, 40)) -> pygame.Surface:
        """Returns pre-cached, rotated Scout sprite (quantized to 2 deg)."""
        quantized_angle = int(round(angle_deg / 2.0)) * 2 % 360
        cache_key = ('scout_rot', state, target_size, quantized_angle)

        if cache_key in self._rotated_cache:
            return self._rotated_cache[cache_key]

        base_sprite = self.get_scout_sprite(state=state, target_size=target_size)
        rotated = pygame.transform.rotate(base_sprite, quantized_angle)
        self._rotated_cache[cache_key] = rotated
        return rotated

    def get_scout_shadow(self, target_size: tuple[int, int] = (36, 22)) -> pygame.Surface:
        """Returns pre-cached 2D drop shadow for Scout."""
        if ('scout_shadow', target_size) in self._shadow_cache:
            return self._shadow_cache[('scout_shadow', target_size)]

        raw = self._load_raw_image('shadows/scout_shadow.png')
        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 85), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[('scout_shadow', target_size)] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(100)
        self._shadow_cache[('scout_shadow', target_size)] = shadow
        return shadow

    # -------------------------------------------------------------------------
    # SHOOTER COMBAT DRONE (Phase 8 Production 2D Sprite)
    # -------------------------------------------------------------------------
    def get_shooter_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (52, 48)) -> pygame.Surface:
        cache_key = ('shooter', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        raw = self._load_raw_image(f'enemies/shooter/shooter_{state}.png')
        if raw is None:
            raw = self._load_raw_image('enemies/shooter/shooter_idle.png')
        if raw is None:
            raw = self._load_raw_image('enemies/shooter/shooter_base.png')

        if raw is None:
            fallback = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.polygon(fallback, (239, 68, 68), [
                (target_size[0] - 2, target_size[1] // 2),
                (2, 4),
                (6, target_size[1] // 2),
                (2, target_size[1] - 4)
            ])
            self._skin_cache[cache_key] = fallback
            return fallback

        scaled = pygame.transform.smoothscale(raw, target_size)
        self._skin_cache[cache_key] = scaled
        return scaled

    def get_rotated_shooter_sprite(self, state: str = 'idle', angle_deg: float = 0.0, target_size: tuple[int, int] = (52, 48)) -> pygame.Surface:
        quantized_angle = int(round(angle_deg / 2.0)) * 2 % 360
        cache_key = ('shooter_rot', state, target_size, quantized_angle)

        if cache_key in self._rotated_cache:
            return self._rotated_cache[cache_key]

        base_sprite = self.get_shooter_sprite(state=state, target_size=target_size)
        rotated = pygame.transform.rotate(base_sprite, quantized_angle)
        self._rotated_cache[cache_key] = rotated
        return rotated

    def get_shooter_shadow(self, target_size: tuple[int, int] = (44, 28)) -> pygame.Surface:
        if ('shooter_shadow', target_size) in self._shadow_cache:
            return self._shadow_cache[('shooter_shadow', target_size)]

        raw = self._load_raw_image('shadows/shooter_shadow.png')
        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[('shooter_shadow', target_size)] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(100)
        self._shadow_cache[('shooter_shadow', target_size)] = shadow
        return shadow

    # -------------------------------------------------------------------------
    # HEAVY COMBAT DRONE (Phase 8 Production 2D Sprite)
    # -------------------------------------------------------------------------
    def get_heavy_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (64, 60)) -> pygame.Surface:
        cache_key = ('heavy', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        raw = self._load_raw_image(f'enemies/heavy/heavy_{state}.png')
        if raw is None:
            raw = self._load_raw_image('enemies/heavy/heavy_idle.png')
        if raw is None:
            raw = self._load_raw_image('enemies/heavy/heavy_base.png')

        if raw is None:
            fallback = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.polygon(fallback, (71, 85, 105), [
                (target_size[0] - 4, target_size[1] // 2),
                (4, 4),
                (12, target_size[1] // 2),
                (4, target_size[1] - 4)
            ])
            self._skin_cache[cache_key] = fallback
            return fallback

        scaled = pygame.transform.smoothscale(raw, target_size)
        self._skin_cache[cache_key] = scaled
        return scaled

    def get_rotated_heavy_sprite(self, state: str = 'idle', angle_deg: float = 0.0, target_size: tuple[int, int] = (64, 60)) -> pygame.Surface:
        quantized_angle = int(round(angle_deg / 2.0)) * 2 % 360
        cache_key = ('heavy_rot', state, target_size, quantized_angle)

        if cache_key in self._rotated_cache:
            return self._rotated_cache[cache_key]

        base_sprite = self.get_heavy_sprite(state=state, target_size=target_size)
        rotated = pygame.transform.rotate(base_sprite, quantized_angle)
        self._rotated_cache[cache_key] = rotated
        return rotated

    def get_heavy_shadow(self, target_size: tuple[int, int] = (58, 36)) -> pygame.Surface:
        if ('heavy_shadow', target_size) in self._shadow_cache:
            return self._shadow_cache[('heavy_shadow', target_size)]

        raw = self._load_raw_image('shadows/heavy_shadow.png')
        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 95), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[('heavy_shadow', target_size)] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(105)
        self._shadow_cache[('heavy_shadow', target_size)] = shadow
        return shadow

    # -------------------------------------------------------------------------
    # SHIELD / ELITE DRONE (Phase 8 Production 2D Sprite)
    # -------------------------------------------------------------------------
    def get_shield_drone_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (54, 50)) -> pygame.Surface:
        cache_key = ('shield_elite', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        raw = self._load_raw_image(f'enemies/shield_elite/shield_elite_{state}.png')
        if raw is None:
            raw = self._load_raw_image('enemies/shield_elite/shield_elite_idle.png')
        if raw is None:
            raw = self._load_raw_image('enemies/shield_elite/shield_elite_base.png')

        if raw is None:
            fallback = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.circle(fallback, (99, 102, 241), (target_size[0] // 2, target_size[1] // 2), target_size[0] // 2 - 2)
            self._skin_cache[cache_key] = fallback
            return fallback

        scaled = pygame.transform.smoothscale(raw, target_size)
        self._skin_cache[cache_key] = scaled
        return scaled

    def get_rotated_shield_drone_sprite(self, state: str = 'idle', angle_deg: float = 0.0, target_size: tuple[int, int] = (54, 50)) -> pygame.Surface:
        quantized_angle = int(round(angle_deg / 2.0)) * 2 % 360
        cache_key = ('shield_rot', state, target_size, quantized_angle)

        if cache_key in self._rotated_cache:
            return self._rotated_cache[cache_key]

        base_sprite = self.get_shield_drone_sprite(state=state, target_size=target_size)
        rotated = pygame.transform.rotate(base_sprite, quantized_angle)
        self._rotated_cache[cache_key] = rotated
        return rotated

    def get_shield_shadow(self, target_size: tuple[int, int] = (46, 30)) -> pygame.Surface:
        if ('shield_shadow', target_size) in self._shadow_cache:
            return self._shadow_cache[('shield_shadow', target_size)]

        raw = self._load_raw_image('shadows/shield_shadow.png')
        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[('shield_shadow', target_size)] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(100)
        self._shadow_cache[('shield_shadow', target_size)] = shadow
        return shadow

    # -------------------------------------------------------------------------
    # ALL 5 BOSS COMBAT PLATFORMS (Phase 8 Production 2D Sprites)
    # -------------------------------------------------------------------------
    def get_boss_sprite(self, boss_key: str, phase: int = 1, target_size: tuple[int, int] = (140, 140)) -> pygame.Surface:
        boss_map = {
            'ASSEMBLY WARDEN': 'assembly_warden.png',
            'assembly_warden': 'assembly_warden.png',
            'CORE EXECUTOR': 'core_executor.png',
            'core_executor': 'core_executor.png',
            'REACTOR TITAN': 'reactor_titan.png',
            'reactor_titan': 'reactor_titan.png',
            'DEFENSE COMMANDER': 'defense_commander.png',
            'defense_commander': 'defense_commander.png',
            'DRONE OVERLORD': 'drone_overlord.png',
            'drone_overlord': 'drone_overlord.png',
        }
        filename = boss_map.get(boss_key, 'assembly_warden.png')
        cache_key = ('boss', filename, phase, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        raw = self._load_raw_image(f'bosses/{filename}')
        if raw is None:
            fallback = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.circle(fallback, (239, 68, 68), (target_size[0] // 2, target_size[1] // 2), target_size[0] // 2 - 4)
            self._skin_cache[cache_key] = fallback
            return fallback

        scaled = pygame.transform.smoothscale(raw, target_size)

        # Multi-phase visual damage & heat overlay (alpha-safe: only tints solid boss pixels)
        if phase >= 2:
            phase_surf = scaled.copy()
            mask = pygame.mask.from_surface(scaled)
            col = (245, 158, 11, 70) if phase == 2 else ((239, 68, 68, 90) if phase == 3 else (225, 29, 72, 120))
            tint_surf = mask.to_surface(setcolor=col, unsetcolor=(0, 0, 0, 0))
            phase_surf.blit(tint_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            scaled = phase_surf

        self._skin_cache[cache_key] = scaled
        return scaled

    def get_rotated_boss_sprite(self, boss_key: str, angle_deg: float = 0.0, phase: int = 1, target_size: tuple[int, int] = (140, 140)) -> pygame.Surface:
        quantized_angle = int(round(angle_deg / 2.0)) * 2 % 360
        cache_key = ('boss_rot', boss_key, phase, target_size, quantized_angle)

        if cache_key in self._rotated_cache:
            return self._rotated_cache[cache_key]

        base_sprite = self.get_boss_sprite(boss_key=boss_key, phase=phase, target_size=target_size)
        rotated = pygame.transform.rotate(base_sprite, quantized_angle)
        self._rotated_cache[cache_key] = rotated
        return rotated

    def get_boss_shadow(self, target_size: tuple[int, int] = (120, 72)) -> pygame.Surface:
        if ('boss_shadow', target_size) in self._shadow_cache:
            return self._shadow_cache[('boss_shadow', target_size)]

        raw = self._load_raw_image('shadows/boss_shadow.png')
        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 110), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[('boss_shadow', target_size)] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(115)
        self._shadow_cache[('boss_shadow', target_size)] = shadow
        return shadow

    # -------------------------------------------------------------------------
    # PROJECTILES (Laser, Scatter, Missile, Hostile Bullet)
    # -------------------------------------------------------------------------
    def get_projectile_sprite(self, proj_type: str, target_size: tuple[int, int]) -> pygame.Surface:
        cache_key = ('proj', proj_type, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        file_map = {
            'pulse': 'projectiles/bullet_pulse.png',
            'scatter': 'projectiles/bullet_scatter.png',
            'missile': 'projectiles/missile.png',
            'enemy': 'projectiles/enemy_bullet.png',
        }
        rel = file_map.get(proj_type, 'projectiles/bullet_pulse.png')
        raw = self._load_raw_image(rel)
        if raw is None:
            fallback = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.circle(fallback, (56, 189, 248), (target_size[0] // 2, target_size[1] // 2), target_size[0] // 2)
            self._skin_cache[cache_key] = fallback
            return fallback

        scaled = pygame.transform.smoothscale(raw, target_size)
        self._skin_cache[cache_key] = scaled
        return scaled


_sprite_manager = None

def get_sprite_manager() -> SpriteManager:
    global _sprite_manager
    if _sprite_manager is None:
        _sprite_manager = SpriteManager()
    return _sprite_manager
