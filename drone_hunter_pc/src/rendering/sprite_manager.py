import os
import math
import logging
from collections import OrderedDict
import pygame
from src.data.settings import COLOR_CYAN, COLOR_GOLD, COLOR_CRIMSON, COLOR_EMERALD, COLOR_WHITE
from src.data.game_data import WEAPON_ASSETS, VFX_ASSETS

logger = logging.getLogger(__name__)

class SpriteManager:
    _instance = None
    ANGLE_STEP = 6  # 360 / 6 = 60 discrete orientations (bounded quantization)
    MAX_ROTATION_ENTRIES = 120  # Strict bounded LRU rotation cache capacity (120 entries)

    HIGH_FIDELITY_PLAYER_MAP = {
        0: 'high_fidelity/player_drones/01_striker/hero_2048.png',
        1: 'high_fidelity/player_drones/02_phantom/hero_2048.png',
        2: 'high_fidelity/player_drones/03_titan/hero_2048.png',
        3: 'high_fidelity/player_drones/04_velocity/hero_2048.png',
        4: 'high_fidelity/player_drones/05_aegis_quad/hero_2048.png',
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

    # Canonical base dimensions for downscaling high-res master PNGs to avoid huge RAM footprint
    CANONICAL_PLAYER_SIZE = (352, 304)
    CANONICAL_ENEMY_SIZES = {
        'scout': (170, 156),
        'shooter': (190, 176),
        'heavy': (230, 216),
        'shield_elite': (190, 176),
        'support_special': (190, 176),
    }
    CANONICAL_BOSS_SIZE = (320, 320)

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(SpriteManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, assets_dir: str = None):
        if getattr(self, '_initialized', False):
            return

        proj_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if assets_dir and os.path.exists(assets_dir):
            self.base_dir = os.path.abspath(assets_dir)
        else:
            default_candidates = [
                os.path.join(proj_root, 'assets', 'sprites'),
                os.path.abspath('assets/sprites'),
                os.path.abspath('drone_hunter_pc/assets/sprites'),
            ]
            self.base_dir = default_candidates[0]
            for dc in default_candidates:
                if os.path.exists(dc):
                    self.base_dir = dc
                    break

        self._canonical_cache: dict[str, pygame.Surface] = {}
        self._raw_cache: dict[str, pygame.Surface] = {}
        self._skin_cache: dict[tuple, pygame.Surface] = {}
        self._rotated_cache: OrderedDict[tuple, pygame.Surface] = OrderedDict()

        # Asset usage diagnostics telemetry (tracks actual render usage)
        self.weapon_asset_loaded: dict[str, bool] = {}
        self.weapon_asset_requested: dict[str, int] = {}
        self.weapon_asset_rendered: dict[str, int] = {}
        
        self.vfx_asset_loaded: dict[str, bool] = {}
        self.vfx_asset_requested: dict[str, int] = {}
        self.vfx_asset_rendered: dict[str, int] = {}

        self._initialized = True
        self._preload_high_fidelity_canonical_assets()
        self.validate_weapon_assets()
        self.validate_vfx_assets()

    def validate_weapon_assets(self) -> dict[str, bool]:
        """Preloads and validates all authoritative production weapon PNG assets."""
        results = {}
        from src.data.game_data import WEAPON_ASSETS
        for w_id, rel_path in WEAPON_ASSETS.items():
            base_name = os.path.basename(rel_path)
            surf = self._load_raw_image(rel_path)
            if surf is not None:
                results[w_id] = True
                self.weapon_asset_loaded[base_name] = True
                logger.info(f"[ASSET] weapon loaded: {base_name}")
            else:
                results[w_id] = False
                self.weapon_asset_loaded[base_name] = False
                logger.error(f"[ASSET ERROR] Missing: {rel_path}")
        return results

    def validate_vfx_assets(self) -> dict[str, bool]:
        """Preloads and validates all authoritative production VFX PNG assets."""
        results = {}
        from src.data.game_data import VFX_ASSETS
        for v_id, rel_path in VFX_ASSETS.items():
            base_name = os.path.basename(rel_path)
            surf = self._load_raw_image(rel_path)
            if surf is not None:
                results[v_id] = True
                self.vfx_asset_loaded[base_name] = True
                logger.info(f"[ASSET] VFX loaded: {base_name}")
            else:
                results[v_id] = False
                self.vfx_asset_loaded[base_name] = False
                logger.error(f"[ASSET ERROR] Missing: {rel_path}")
        return results

    def track_weapon_render(self, asset_name: str):
        base_name = os.path.basename(asset_name)
        if not base_name.endswith('.png'): base_name += '.png'
        self.weapon_asset_rendered[base_name] = self.weapon_asset_rendered.get(base_name, 0) + 1
        
    def track_vfx_render(self, asset_name: str):
        base_name = os.path.basename(asset_name)
        if not base_name.endswith('.png'): base_name += '.png'
        self.vfx_asset_rendered[base_name] = self.vfx_asset_rendered.get(base_name, 0) + 1

    def _resolve_file_path(self, rel_path: str) -> str | None:
        candidates = [
            os.path.join(self.base_dir, rel_path),
            os.path.join(os.path.dirname(self.base_dir), rel_path),
            os.path.join(os.path.dirname(self.base_dir), 'high_fidelity', rel_path),
            os.path.join('assets', 'sprites', rel_path),
            os.path.join('drone_hunter_pc', 'assets', 'sprites', rel_path),
            os.path.join('Drone_Hunter_Phase8_2D_Assets_v04_HighFidelity', 'production', rel_path),
        ]
        for c in candidates:
            if os.path.exists(c):
                return os.path.abspath(c)
        return None

    def _load_canonical_asset(self, rel_path: str, rotate_deg: int, canonical_size: tuple[int, int]) -> pygame.Surface | None:
        if rel_path in self._canonical_cache:
            return self._canonical_cache[rel_path]

        full_path = self._resolve_file_path(rel_path)
        if not full_path or not os.path.exists(full_path):
            return None

        try:
            raw_surf = pygame.image.load(full_path)
            if pygame.display.get_surface() is not None:
                raw_surf = raw_surf.convert_alpha()

            if rotate_deg != 0:
                raw_surf = pygame.transform.rotate(raw_surf, rotate_deg)

            canonical = pygame.transform.smoothscale(raw_surf, canonical_size)
            self._canonical_cache[rel_path] = canonical
            return canonical
        except Exception as e:
            logger.error(f"[ASSET ERROR] Failed loading canonical {rel_path}: {e}")
            return None

    def _load_raw_image(self, rel_path: str) -> pygame.Surface | None:
        if rel_path in self._raw_cache:
            return self._raw_cache[rel_path]

        full_path = self._resolve_file_path(rel_path)
        if not full_path or not os.path.exists(full_path):
            return None

        try:
            surf = pygame.image.load(full_path)
            if pygame.display.get_surface() is not None:
                surf = surf.convert_alpha()
            self._raw_cache[rel_path] = surf
            return surf
        except Exception as e:
            logger.error(f"[ASSET ERROR] Failed loading raw {rel_path}: {e}")
            return None

    def _preload_high_fidelity_canonical_assets(self):
        for rel in self.HIGH_FIDELITY_PLAYER_MAP.values():
            self._load_canonical_asset(rel, 270, self.CANONICAL_PLAYER_SIZE)

        for key, rel in self.HIGH_FIDELITY_ENEMY_MAP.items():
            size = self.CANONICAL_ENEMY_SIZES.get(key, (190, 176))
            self._load_canonical_asset(rel, 270, size)

        for rel in set(self.HIGH_FIDELITY_BOSS_MAP.values()):
            self._load_canonical_asset(rel, 0, self.CANONICAL_BOSS_SIZE)

    def _get_or_create_rotated_surface(self, base_key: tuple, base_surf: pygame.Surface, angle_deg: float) -> pygame.Surface:
        quantized_angle = int(round(angle_deg / self.ANGLE_STEP)) * self.ANGLE_STEP % 360
        cache_key = (base_key, quantized_angle)

        if cache_key in self._rotated_cache:
            self._rotated_cache.move_to_end(cache_key)
            return self._rotated_cache[cache_key]

        rotated = pygame.transform.rotate(base_surf, quantized_angle)
        self._rotated_cache[cache_key] = rotated

        while len(self._rotated_cache) > self.MAX_ROTATION_ENTRIES:
            self._rotated_cache.popitem(last=False)

        return rotated

    def get_player_sprite(self, state: str = 'idle', skin_idx: int = 0, target_size: tuple[int, int] = (176, 152)) -> pygame.Surface:
        idx = max(0, min(4, skin_idx))
        cache_key = ('player', state, idx, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_PLAYER_MAP.get(idx)
        canonical = self._load_canonical_asset(hf_rel, 270, self.CANONICAL_PLAYER_SIZE) if hf_rel else None

        if canonical is not None:
            scaled = pygame.transform.smoothscale(canonical, target_size) if canonical.get_size() != target_size else canonical
        else:
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

        self._skin_cache[cache_key] = scaled
        return scaled

    def get_rotated_player_sprite(self, state: str = 'idle', skin_idx: int = 0, angle_deg: float = 0.0, target_size: tuple[int, int] = (176, 152)) -> pygame.Surface:
        base_key = ('player', 'base', max(0, min(4, skin_idx)), target_size)
        base_sprite = self.get_player_sprite(state=state, skin_idx=skin_idx, target_size=target_size)
        return self._get_or_create_rotated_surface(base_key, base_sprite, angle_deg)

    def get_scout_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (52, 46)) -> pygame.Surface:
        cache_key = ('scout', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_MAP.get('scout')
        canonical = self._load_canonical_asset(hf_rel, 270, self.CANONICAL_ENEMY_SIZES['scout']) if hf_rel else None

        if canonical is not None:
            scaled = pygame.transform.smoothscale(canonical, target_size) if canonical.get_size() != target_size else canonical
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
        state_key = 'hit' if state == 'hit' else 'base'
        base_key = ('scout', state_key, target_size)
        base_sprite = self.get_scout_sprite(state=state, target_size=target_size)
        return self._get_or_create_rotated_surface(base_key, base_sprite, angle_deg)

    def get_shooter_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (52, 48)) -> pygame.Surface:
        cache_key = ('shooter', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_MAP.get('shooter')
        canonical = self._load_canonical_asset(hf_rel, 270, self.CANONICAL_ENEMY_SIZES['shooter']) if hf_rel else None

        if canonical is not None:
            scaled = pygame.transform.smoothscale(canonical, target_size) if canonical.get_size() != target_size else canonical
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
        state_key = 'hit' if state == 'hit' else 'base'
        base_key = ('shooter', state_key, target_size)
        base_sprite = self.get_shooter_sprite(state=state, target_size=target_size)
        return self._get_or_create_rotated_surface(base_key, base_sprite, angle_deg)

    def get_heavy_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (64, 60)) -> pygame.Surface:
        cache_key = ('heavy', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_MAP.get('heavy')
        canonical = self._load_canonical_asset(hf_rel, 270, self.CANONICAL_ENEMY_SIZES['heavy']) if hf_rel else None

        if canonical is not None:
            scaled = pygame.transform.smoothscale(canonical, target_size) if canonical.get_size() != target_size else canonical
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
        state_key = 'hit' if state == 'hit' else 'base'
        base_key = ('heavy', state_key, target_size)
        base_sprite = self.get_heavy_sprite(state=state, target_size=target_size)
        return self._get_or_create_rotated_surface(base_key, base_sprite, angle_deg)

    def get_shield_drone_sprite(self, state: str = 'idle', target_size: tuple[int, int] = (54, 50)) -> pygame.Surface:
        cache_key = ('shield_elite', state, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_ENEMY_MAP.get('shield_elite')
        canonical = self._load_canonical_asset(hf_rel, 270, self.CANONICAL_ENEMY_SIZES['shield_elite']) if hf_rel else None

        if canonical is not None:
            scaled = pygame.transform.smoothscale(canonical, target_size) if canonical.get_size() != target_size else canonical
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
        state_key = 'hit' if state == 'hit' else 'base'
        base_key = ('shield_elite', state_key, target_size)
        base_sprite = self.get_shield_drone_sprite(state=state, target_size=target_size)
        return self._get_or_create_rotated_surface(base_key, base_sprite, angle_deg)

    def get_boss_sprite(self, boss_key: str, phase: int = 1, target_size: tuple[int, int] = (140, 140)) -> pygame.Surface:
        cache_key = ('boss', boss_key, phase, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        hf_rel = self.HIGH_FIDELITY_BOSS_MAP.get(boss_key)
        canonical = self._load_canonical_asset(hf_rel, 0, self.CANONICAL_BOSS_SIZE) if hf_rel else None

        if canonical is not None:
            scaled = pygame.transform.smoothscale(canonical, target_size) if canonical.get_size() != target_size else canonical
        else:
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
        base_key = ('boss', boss_key, phase, target_size)
        base_sprite = self.get_boss_sprite(boss_key=boss_key, phase=phase, target_size=target_size)
        return self._get_or_create_rotated_surface(base_key, base_sprite, angle_deg)

    def get_rotated_surface(self, surf: pygame.Surface, angle_deg: float) -> pygame.Surface:
        quantized_angle = int(round(angle_deg / self.ANGLE_STEP)) * self.ANGLE_STEP % 360
        surf_id = id(surf)
        cache_key = (surf_id, quantized_angle)

        if cache_key in self._rotated_cache:
            self._rotated_cache.move_to_end(cache_key)
            return self._rotated_cache[cache_key]

        rotated = pygame.transform.rotate(surf, quantized_angle)
        self._rotated_cache[cache_key] = rotated
        while len(self._rotated_cache) > self.MAX_ROTATION_ENTRIES:
            self._rotated_cache.popitem(last=False)
        return rotated

    # -------------------------------------------------------------------------
    # PROJECTILES (Laser, Scatter, Missile, Hostile Bullet)
    # -------------------------------------------------------------------------
    def get_projectile_sprite(self, proj_type: str, target_size: tuple[int, int]) -> pygame.Surface:
        cache_key = ('proj', proj_type, target_size)
        rel = WEAPON_ASSETS.get(proj_type, proj_type if proj_type.endswith('.png') else 'weapons/laser_pulse.png')
        base_name = os.path.basename(rel)

        if cache_key in self._skin_cache:
            self.weapon_asset_requested[base_name] = self.weapon_asset_requested.get(base_name, 0) + 1
            return self._skin_cache[cache_key]

        # Try individual weapon folder first
        indiv_path = f"weapons/{proj_type}/projectile.png"
        raw = self._load_raw_image(indiv_path)
        if raw is None:
            raw = self._load_raw_image(rel)

        if raw is None:
            logger.error(f"[ASSET ERROR] Missing weapon sprite: {rel}")
            raise RuntimeError(f"Missing production weapon asset: {rel}. Do NOT use procedural fallbacks.")

        self.weapon_asset_requested[base_name] = self.weapon_asset_requested.get(base_name, 0) + 1
        scaled = pygame.transform.smoothscale(raw, target_size)
        self._skin_cache[cache_key] = scaled
        return scaled

    def get_vfx_sprite(self, name: str, target_size: tuple[int, int]) -> pygame.Surface:
        cache_key = ('vfx', name, target_size)
        if cache_key in self._skin_cache:
            rel = VFX_ASSETS.get(name, f'vfx/{name}.png' if not name.startswith('vfx/') else name)
            base_name = os.path.basename(rel)
            self.vfx_asset_requested[base_name] = self.vfx_asset_requested.get(base_name, 0) + 1
            return self._skin_cache[cache_key]

        rel = VFX_ASSETS.get(name)
        if not rel:
            if name.startswith('vfx/') or name.endswith('.png'):
                rel = name
            else:
                rel = f'vfx/{name}.png'

        raw = self._load_raw_image(rel)
        base_name = os.path.basename(rel)
        if raw is None:
            logger.error(f"[ASSET ERROR] Missing VFX sprite: {rel}")
            raise RuntimeError(f"Missing production VFX asset: {rel}. Do NOT use procedural fallbacks.")

        self.vfx_asset_requested[base_name] = self.vfx_asset_requested.get(base_name, 0) + 1
        scaled = pygame.transform.smoothscale(raw, target_size)
        self._skin_cache[cache_key] = scaled
        return scaled

    def get_weapon_icon_sprite(self, weapon_id: str, target_size: tuple[int, int] = (48, 48)) -> pygame.Surface:
        cache_key = ('w_icon', weapon_id, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        rel = f'weapons/{weapon_id}/icon.png'
        raw = self._load_raw_image(rel)
        if raw is None:
            rel = WEAPON_ASSETS.get(weapon_id, 'weapons/laser_pulse.png')
            raw = self._load_raw_image(rel)

        if raw is not None:
            scaled = pygame.transform.smoothscale(raw, target_size)
        else:
            scaled = pygame.Surface(target_size, pygame.SRCALPHA)
            pygame.draw.circle(scaled, (14, 165, 233), (target_size[0] // 2, target_size[1] // 2), target_size[0] // 2 - 2)

        self._skin_cache[cache_key] = scaled
        return scaled

    def get_weapon_muzzle_sprite(self, weapon_id: str, target_size: tuple[int, int] = (48, 48)) -> pygame.Surface:
        cache_key = ('w_muzzle', weapon_id, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        rel = f'weapons/{weapon_id}/muzzle.png'
        raw = self._load_raw_image(rel)
        if raw is None:
            rel = WEAPON_ASSETS.get(weapon_id, 'weapons/laser_pulse.png')
            raw = self._load_raw_image(rel)

        scaled = pygame.transform.smoothscale(raw, target_size) if raw else pygame.Surface(target_size, pygame.SRCALPHA)
        self._skin_cache[cache_key] = scaled
        return scaled

    def get_weapon_impact_sprite(self, weapon_id: str, target_size: tuple[int, int] = (56, 56)) -> pygame.Surface:
        cache_key = ('w_impact', weapon_id, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        rel = f'weapons/{weapon_id}/impact.png'
        raw = self._load_raw_image(rel)
        if raw is None:
            rel = WEAPON_ASSETS.get(weapon_id, 'weapons/laser_pulse.png')
            raw = self._load_raw_image(rel)

        scaled = pygame.transform.smoothscale(raw, target_size) if raw else pygame.Surface(target_size, pygame.SRCALPHA)
        self._skin_cache[cache_key] = scaled
        return scaled

    def get_player_state_sprite(self, state: str, skin_idx: int, target_size: tuple[int, int]) -> pygame.Surface:
        cache_key = ('player_state', state, skin_idx, target_size)
        if cache_key in self._skin_cache:
            return self._skin_cache[cache_key]

        raw = self._load_raw_image(f'player/player_{state}.png')
        if raw is None:
            fallback = pygame.Surface(target_size, pygame.SRCALPHA)
            self._skin_cache[cache_key] = fallback
            return fallback

        scaled = pygame.transform.smoothscale(raw, target_size)
        self._skin_cache[cache_key] = scaled
        return scaled

    # -------------------------------------------------------------------------
    # CACHE INTROSPECTION & PROFILING
    # -------------------------------------------------------------------------
    def get_cache_stats(self) -> dict:
        return {
            'canonical_surfaces': len(self._canonical_cache),
            'scaled_surfaces': len(self._skin_cache),
            'rotated_surfaces': len(self._rotated_cache),
            'max_rotation_capacity': self.MAX_ROTATION_ENTRIES,
            'angle_step': self.ANGLE_STEP,
            'weapon_asset_loaded': dict(self.weapon_asset_loaded),
            'weapon_asset_requested': dict(self.weapon_asset_requested),
            'weapon_asset_rendered': dict(self.weapon_asset_rendered),
            'vfx_asset_loaded': dict(self.vfx_asset_loaded),
            'vfx_asset_requested': dict(self.vfx_asset_requested),
            'vfx_asset_rendered': dict(self.vfx_asset_rendered),
        }

    def clear_rotation_cache(self):
        self._rotated_cache.clear()


_sprite_manager = None

def get_sprite_manager() -> SpriteManager:
    global _sprite_manager
    if _sprite_manager is None:
        _sprite_manager = SpriteManager()
    return _sprite_manager
