"""
================================================================================
                    DRONE HUNTER 2D - FONT MANAGER
================================================================================
Cached font creation with automatic fallback mechanisms and lazy initialization.
"""

import pygame

_font_cache = {}

def ensure_font_init():
    """Ensures pygame and pygame.font are initialized."""
    try:
        if not pygame.get_init():
            pygame.init()
        if not pygame.font.get_init():
            pygame.font.init()
    except Exception:
        pass

def safe_create_font(name: str, size: int, bold: bool = False) -> pygame.font.Font:
    """Safely creates font with internal caching and system font fallbacks."""
    ensure_font_init()
    cache_key = (name, size, bold)
    if cache_key in _font_cache:
        return _font_cache[cache_key]

    try:
        font = pygame.font.SysFont(name, size, bold=bold)
    except Exception:
        try:
            font = pygame.font.Font(None, size)
        except Exception:
            ensure_font_init()
            font = pygame.font.Font(None, size)

    _font_cache[cache_key] = font
    return font

class _LazyFont:
    """Lazily evaluates fonts so module imports never crash if font engine is uninitialized."""
    def __init__(self, name: str, size: int, bold: bool = False):
        self.name = name
        self.size = size
        self.bold = bold

    def _get(self) -> pygame.font.Font:
        return safe_create_font(self.name, self.size, self.bold)

    def render(self, *args, **kwargs):
        return self._get().render(*args, **kwargs)

    def size(self, *args, **kwargs):
        return self._get().size(*args, **kwargs)

    def get_linesize(self, *args, **kwargs):
        return self._get().get_linesize(*args, **kwargs)

    def get_height(self, *args, **kwargs):
        return self._get().get_height(*args, **kwargs)

    def get_ascent(self, *args, **kwargs):
        return self._get().get_ascent(*args, **kwargs)

    def get_descent(self, *args, **kwargs):
        return self._get().get_descent(*args, **kwargs)

# Lazy Font Singletons
font_title = _LazyFont("Impact", 52)
font_banner = _LazyFont("Verdana", 22, bold=True)
font_card = _LazyFont("Segoe UI", 16, bold=True)
font_hud = _LazyFont("Consolas", 18, bold=True)
font_gameover = _LazyFont("Impact", 54)
