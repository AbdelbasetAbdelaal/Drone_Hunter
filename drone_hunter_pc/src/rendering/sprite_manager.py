import os
import math
import pygame
from src.data.settings import COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_EMERALD, COLOR_WHITE

class SpriteManager:
    _instance = None

    HIGH_FIDELITY_PLAYER_MAP = {
        0: 'high_fidelity/player_drones/01_striker/hero_2048.png',
        1: 'high_fidelity/player_drones/02_phantom/hero_2048.png',
        2: 'high_fidelity/player_drones/03_titan/hero_2048.png',
        3: 'high_fidelity/player_drones/04_velocity/hero_2048.png',
        4: 'high_fidelity/player_drones/05_aegis_quad/hero_2048.png',
    }

    HIGH_FIDELITY_PLAYER_SHADOW_MAP = {
        0: 'high_fidelity/player_drones/01_striker/shadow_2048.png',
        1: 'high_fidelity/player_drones/02_phantom/shadow_2048.png',
        2: 'high_fidelity/player_drones/03_titan/shadow_2048.png',
        3: 'high_fidelity/player_drones/04_velocity/shadow_2048.png',
        4: 'high_fidelity/player_drones/05_aegis_quad/shadow_2048.png',
    }

    HIGH_FIDELITY_ENEMY_MAP = {
        'scout': 'high_fidelity/enemies/scout/hero_2048.png',
        'shooter': 'high_fidelity/enemies/shooter/hero_2048.png',
        'heavy': 'high_fidelity/enemies/heavy/hero_2048.png',
        'shield_elite': 'high_fidelity/enemies/shield_elite/hero_2048.png',
        'shield': 'high_fidelity/enemies/shield_elite/hero_2048.png',
        'support_special': 'high_fidelity/enemies/support_special/hero_2048.png',
        'support': 'high_fidelity/enemies/support_special/hero_2048.png',
    }

    HIGH_FIDELITY_ENEMY_SHADOW_MAP = {
        'scout': 'high_fidelity/enemies/scout/shadow_2048.png',
        'shooter': 'high_fidelity/enemies/shooter/shadow_2048.png',
        'heavy': 'high_fidelity/enemies/heavy/shadow_2048.png',
        'shield_elite': 'high_fidelity/enemies/shield_elite/shadow_2048.png',
        'shield': 'high_fidelity/enemies/shield_elite/shadow_2048.png',
        'support_special': 'high_fidelity/enemies/support_special/shadow_2048.png',
        'support': 'high_fidelity/enemies/support_special/shadow_2048.png',
    }

    HIGH_FIDELITY_BOSS_MAP = {
        'ASSEMBLY WARDEN': 'high_fidelity/bosses/assembly_warden/hero_2048.png',
        'assembly_warden': 'high_fidelity/bosses/assembly_warden/hero_2048.png',
        'CORE EXECUTOR': 'high_fidelity/bosses/core_executor/hero_2048.png',
        'core_executor': 'high_fidelity/bosses/core_executor/hero_2048.png',
        'REACTOR TITAN': 'high_fidelity/bosses/reactor_titan/hero_2048.png',
        'reactor_titan': 'high_fidelity/bosses/reactor_titan/hero_2048.png',
        'DEFENSE COMMANDER': 'high_fidelity/bosses/defense_commander/hero_2048.png',
        'defense_commander': 'high_fidelity/bosses/defense_commander/hero_2048.png',
        'DRONE OVERLORD': 'high_fidelity/bosses/drone_overlord/hero_2048.png',
        'drone_overlord': 'high_fidelity/bosses/drone_overlord/hero_2048.png',
    }

    HIGH_FIDELITY_BOSS_SHADOW_MAP = {
        'ASSEMBLY WARDEN': 'high_fidelity/bosses/assembly_warden/shadow_2048.png',
        'assembly_warden': 'high_fidelity/bosses/assembly_warden/shadow_2048.png',
        'CORE EXECUTOR': 'high_fidelity/bosses/core_executor/shadow_2048.png',
        'core_executor': 'high_fidelity/bosses/core_executor/shadow_2048.png',
        'REACTOR TITAN': 'high_fidelity/bosses/reactor_titan/shadow_2048.png',
        'reactor_titan': 'high_fidelity/bosses/reactor_titan/shadow_2048.png',
        'DEFENSE COMMANDER': 'high_fidelity/bosses/defense_commander/shadow_2048.png',
        'defense_commander': 'high_fidelity/bosses/defense_commander/shadow_2048.png',
        'DRONE OVERLORD': 'high_fidelity/bosses/drone_overlord/shadow_2048.png',
        'drone_overlord': 'high_fidelity/bosses/drone_overlord/shadow_2048.png',
    }

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
        self._preload_high_fidelity_assets()

    def _resolve_file_path(self, rel_path: str) -> str | None:
        candidates = [
            os.path.join(self.base_dir, rel_path),
            os.path.join(os.path.dirname(self.base_dir), 'high_fidelity', rel_path),
            os.path.join(os.path.dirname(self.base_dir), rel_path),
            os.path.join('Drone_Hunter_Phase8_2D_Assets_v04_HighFidelity', 'production', rel_path),
        ]
        for c in candidates:
            if os.path.exists(c):
                return c
        return None

    def _load_raw_image(self, rel_path: str) -> pygame.Surface | None:
        if rel_path in self._raw_cache:
            return self._raw_cache[rel_path]

        full_path = self._resolve_file_path(rel_path)
        if not full_path or not os.path.exists(full_path):
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

    def _preload_high_fidelity_assets(self):
        """Preloads high-fidelity 2048 master assets to ensure 0 runtime disk I/O."""
        for rel in self.HIGH_FIDELITY_PLAYER_MAP.values():
            self._load_raw_image(rel)
        for rel in self.HIGH_FIDELITY_ENEMY_MAP.values():
            self._load_raw_image(rel)
        for rel in self.HIGH_FIDELITY_BOSS_MAP.values():
            self._load_raw_image(rel)

    # -------------------------------------------------------------------------
    # PLAYER DRONES (High-Fidelity Variants 0..4)
    # -------------------------------------------------------------------------
    def get_player_sprite(self, state: str = 'idle', skin_idx: int = 0, target_size: tuple[int, int] = (90, 78)) -> pygame.Surface:
        idx = max(0, min(4, skin_idx))
        cache_key = (state, idx, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_PLAYER_MAP.get(idx)
        raw = self._load_raw_image(hf_rel) if hf_rel else None

        if raw is not None:
            # 2048 hero points UP; rotate 270 (90 deg clockwise) so nose faces East/Right along 2D aim vector
            raw_rot = pygame.transform.rotate(raw, 270)
            scaled = pygame.transform.smoothscale(raw_rot, target_size)
        else:
            # Fallback to local sprites
            raw = self._load_raw_image(f'player/drone_chassis_{idx}.png')
            if raw is None:
                raw = self._load_raw_image(f'player/chassis_{idx}.png')
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

        if state == 'hit':
            hit_surf = scaled.copy()
            mask = pygame.mask.from_surface(scaled)
            tint = mask.to_surface(setcolor=(255, 255, 255, 140), unsetcolor=(0, 0, 0, 0))
            hit_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            scaled = hit_surf

        self._skin_cache[cache_key] = scaled
        return scaled

    def get_player_shadow(self, skin_idx: int = 0, target_size: tuple[int, int] = (76, 48)) -> pygame.Surface:
        idx = max(0, min(4, skin_idx))
        cache_key = ('player_shadow', idx, target_size)
        if cache_key in self._shadow_cache:
            return self._shadow_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_PLAYER_SHADOW_MAP.get(idx)
        raw = self._load_raw_image(hf_rel) if hf_rel else None

        if raw is None:
            raw = self._load_raw_image('shadows/player_shadow.png')

        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[cache_key] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(110)
        self._shadow_cache[cache_key] = shadow
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
        quantized_angle = int(round(angle_deg / 2.0)) * 2 % 360
        cache_key = (state, skin_idx, target_size, quantized_angle)

        if cache_key in self._rotated_cache:
            return self._rotated_cache[cache_key]

        base_sprite = self.get_player_sprite(state=state, skin_idx=skin_idx, target_size=target_size)
        rotated = pygame.transform.rotate(base_sprite, quantized_angle)
        self._rotated_cache[cache_key] = rotated
        return rotated

    # -------------------------------------------------------------------------
    # SCOUT COMBAT DRONE (High-Fidelity 2D)
    # -------------------------------------------------------------------------
    def get_scout_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (52, 46)) -> pygame.Surface:
        cache_key = ('scout', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_MAP.get('scout')
        raw = self._load_raw_image(hf_rel) if hf_rel else None

        if raw is not None:
            raw_rot = pygame.transform.rotate(raw, 270)
            scaled = pygame.transform.smoothscale(raw_rot, target_size)
        else:
            raw = self._load_raw_image(f'enemies/scout/scout_{state}.png')
            if raw is None:
                raw = self._load_raw_image('enemies/scout/scout_idle.png')
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

        if state == 'hit':
            hit_surf = scaled.copy()
            mask = pygame.mask.from_surface(scaled)
            tint = mask.to_surface(setcolor=(255, 255, 255, 140), unsetcolor=(0, 0, 0, 0))
            hit_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            scaled = hit_surf

        self._skin_cache[cache_key] = scaled
        return scaled

    def get_rotated_scout_sprite(self, state: str = 'idle', angle_deg: float = 0.0, target_size: tuple[int, int] = (44, 40)) -> pygame.Surface:
        quantized_angle = int(round(angle_deg / 2.0)) * 2 % 360
        cache_key = ('scout_rot', state, target_size, quantized_angle)

        if cache_key in self._rotated_cache:
            return self._rotated_cache[cache_key]

        base_sprite = self.get_scout_sprite(state=state, target_size=target_size)
        rotated = pygame.transform.rotate(base_sprite, quantized_angle)
        self._rotated_cache[cache_key] = rotated
        return rotated

    def get_scout_shadow(self, target_size: tuple[int, int] = (36, 22)) -> pygame.Surface:
        cache_key = ('scout_shadow', target_size)
        if cache_key in self._shadow_cache:
            return self._shadow_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_SHADOW_MAP.get('scout')
        raw = self._load_raw_image(hf_rel) if hf_rel else None
        if raw is None:
            raw = self._load_raw_image('shadows/scout_shadow.png')

        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 85), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[cache_key] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(100)
        self._shadow_cache[cache_key] = shadow
        return shadow

    # -------------------------------------------------------------------------
    # SHOOTER COMBAT DRONE (High-Fidelity 2D)
    # -------------------------------------------------------------------------
    def get_shooter_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (52, 48)) -> pygame.Surface:
        cache_key = ('shooter', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_MAP.get('shooter')
        raw = self._load_raw_image(hf_rel) if hf_rel else None

        if raw is not None:
            raw_rot = pygame.transform.rotate(raw, 270)
            scaled = pygame.transform.smoothscale(raw_rot, target_size)
        else:
            raw = self._load_raw_image(f'enemies/shooter/shooter_{state}.png')
            if raw is None:
                raw = self._load_raw_image('enemies/shooter/shooter_idle.png')
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

        if state == 'hit':
            hit_surf = scaled.copy()
            mask = pygame.mask.from_surface(scaled)
            tint = mask.to_surface(setcolor=(255, 255, 255, 140), unsetcolor=(0, 0, 0, 0))
            hit_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            scaled = hit_surf

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
        cache_key = ('shooter_shadow', target_size)
        if cache_key in self._shadow_cache:
            return self._shadow_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_SHADOW_MAP.get('shooter')
        raw = self._load_raw_image(hf_rel) if hf_rel else None
        if raw is None:
            raw = self._load_raw_image('shadows/shooter_shadow.png')

        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[cache_key] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(100)
        self._shadow_cache[cache_key] = shadow
        return shadow

    # -------------------------------------------------------------------------
    # HEAVY COMBAT DRONE (High-Fidelity 2D)
    # -------------------------------------------------------------------------
    def get_heavy_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (64, 60)) -> pygame.Surface:
        cache_key = ('heavy', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_MAP.get('heavy')
        raw = self._load_raw_image(hf_rel) if hf_rel else None

        if raw is not None:
            raw_rot = pygame.transform.rotate(raw, 270)
            scaled = pygame.transform.smoothscale(raw_rot, target_size)
        else:
            raw = self._load_raw_image(f'enemies/heavy/heavy_{state}.png')
            if raw is None:
                raw = self._load_raw_image('enemies/heavy/heavy_idle.png')
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

        if state == 'hit':
            hit_surf = scaled.copy()
            mask = pygame.mask.from_surface(scaled)
            tint = mask.to_surface(setcolor=(255, 255, 255, 140), unsetcolor=(0, 0, 0, 0))
            hit_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            scaled = hit_surf

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
        cache_key = ('heavy_shadow', target_size)
        if cache_key in self._shadow_cache:
            return self._shadow_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_SHADOW_MAP.get('heavy')
        raw = self._load_raw_image(hf_rel) if hf_rel else None
        if raw is None:
            raw = self._load_raw_image('shadows/heavy_shadow.png')

        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 95), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[cache_key] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(105)
        self._shadow_cache[cache_key] = shadow
        return shadow

    # -------------------------------------------------------------------------
    # SHIELD / ELITE DRONE (High-Fidelity 2D)
    # -------------------------------------------------------------------------
    def get_shield_drone_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (54, 50)) -> pygame.Surface:
        cache_key = ('shield_elite', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_MAP.get('shield_elite')
        raw = self._load_raw_image(hf_rel) if hf_rel else None

        if raw is not None:
            raw_rot = pygame.transform.rotate(raw, 270)
            scaled = pygame.transform.smoothscale(raw_rot, target_size)
        else:
            raw = self._load_raw_image(f'enemies/shield_elite/shield_elite_{state}.png')
            if raw is None:
                raw = self._load_raw_image('enemies/shield_elite/shield_elite_idle.png')
            if raw is None:
                fallback = pygame.Surface(target_size, pygame.SRCALPHA)
                pygame.draw.circle(fallback, (99, 102, 241), (target_size[0] // 2, target_size[1] // 2), target_size[0] // 2 - 2)
                self._skin_cache[cache_key] = fallback
                return fallback
            scaled = pygame.transform.smoothscale(raw, target_size)

        if state == 'hit':
            hit_surf = scaled.copy()
            mask = pygame.mask.from_surface(scaled)
            tint = mask.to_surface(setcolor=(255, 255, 255, 140), unsetcolor=(0, 0, 0, 0))
            hit_surf.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            scaled = hit_surf

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
        cache_key = ('shield_shadow', target_size)
        if cache_key in self._shadow_cache:
            return self._shadow_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_SHADOW_MAP.get('shield_elite')
        raw = self._load_raw_image(hf_rel) if hf_rel else None
        if raw is None:
            raw = self._load_raw_image('shadows/shield_shadow.png')

        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 90), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[cache_key] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(100)
        self._shadow_cache[cache_key] = shadow
        return shadow

    # -------------------------------------------------------------------------
    # ALL 5 BOSS COMBAT PLATFORMS (High-Fidelity 2D)
    # -------------------------------------------------------------------------
    def get_boss_sprite(self, boss_key: str, phase: int = 1, target_size: tuple[int, int] = (140, 140)) -> pygame.Surface:
        cache_key = ('boss', boss_key, phase, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_BOSS_MAP.get(boss_key)
        raw = self._load_raw_image(hf_rel) if hf_rel else None

        if raw is None:
            boss_file_map = {
                'ASSEMBLY WARDEN': 'bosses/assembly_warden.png',
                'assembly_warden': 'bosses/assembly_warden.png',
                'CORE EXECUTOR': 'bosses/core_executor.png',
                'core_executor': 'bosses/core_executor.png',
                'REACTOR TITAN': 'bosses/reactor_titan.png',
                'reactor_titan': 'bosses/reactor_titan.png',
                'DEFENSE COMMANDER': 'bosses/defense_commander.png',
                'defense_commander': 'bosses/defense_commander.png',
                'DRONE OVERLORD': 'bosses/drone_overlord.png',
                'drone_overlord': 'bosses/drone_overlord.png',
            }
            rel = boss_file_map.get(boss_key, 'bosses/assembly_warden.png')
            raw = self._load_raw_image(rel)

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

    def get_boss_shadow(self, boss_key: str = 'assembly_warden', target_size: tuple[int, int] = (120, 72)) -> pygame.Surface:
        cache_key = ('boss_shadow', boss_key, target_size)
        if cache_key in self._shadow_cache:
            return self._shadow_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_BOSS_SHADOW_MAP.get(boss_key)
        raw = self._load_raw_image(hf_rel) if hf_rel else None
        if raw is None:
            raw = self._load_raw_image('shadows/boss_shadow.png')

        if raw is None:
            shadow = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.ellipse(shadow, (0, 0, 0, 110), (0, 0, target_size[0], target_size[1]))
            self._shadow_cache[cache_key] = shadow
            return shadow

        shadow = pygame.transform.smoothscale(raw, target_size)
        shadow.set_alpha(115)
        self._shadow_cache[cache_key] = shadow
        return shadow

    # -------------------------------------------------------------------------
    # PROJECTILES (Laser, Scatter, Missile, Hostile Bullet)
    # -------------------------------------------------------------------------
    def get_projectile_sprite(self, proj_type: str, target_size: tuple[int, int]) -> pygame.Surface:
        cache_key = ('proj', proj_type, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        file_map = {
            'pulse': 'weapons/laser_pulse.png',
            'scatter': 'weapons/laser_scatter.png',
            'missile': 'weapons/missile.png',
            'enemy': 'weapons/enemy_bullet.png',
        }
        rel = file_map.get(proj_type, 'weapons/laser_pulse.png')
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

