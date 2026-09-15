import math
from typing import final, override

from pygae.core import GameObject
from pygae.math import Vec2Like
from pygame import BLEND_RGB_ADD, BLEND_RGB_MULT, SRCALPHA, Color, Surface
from pygame.transform import smoothscale

from goe.core import CellFlag, LifeSimulation
from goe.helpers import has_any_flag
from goe.objects import Camera
from goe.setting import CELL_ALIVE_COLOR, CELL_BORN_COLOR


BLOOM_QUANTIZTION_COUNT = 32


def _make_bloom_map(size: int) -> Surface:
    surf = Surface((size, size), SRCALPHA)
    c = size / 2
    for y in range(size):
        for x in range(size):
            d = math.hypot(x - c, y - c) / c
            if d >= 1.0: continue
            a = (1.0 - d) ** 2.2
            v = int(255 * a)
            surf.set_at((x, y), (v, v, v, v))
    return surf


@final
class FancyRenderer(GameObject):

    def __init__(self, camera: Camera, sim: LifeSimulation) -> None:
        super().__init__()
        self._cam = camera
        self._sim = sim
        self._bloom = None
        self._prev: frozenset[Vec2Like] = frozenset()
        self._cells: frozenset[Vec2Like] = frozenset()
        self._buffer: dict[Vec2Like, float] = dict()
        self._to_remove: set[Vec2Like] = set()
        self._bloom_cache: dict[int, tuple[int, tuple[int, int, int, int]]] = dict()

    def _blit_bloom(self, surface: Surface, pos: Vec2Like, radius: int, color: Color, intensity: float):
        if self._bloom is None: self._bloom = _make_bloom_map(128)
        red, green, blue = color
        diameter = max(1, int(radius * 2))
        q_intensity = round(intensity * BLOOM_QUANTIZTION_COUNT)/BLOOM_QUANTIZTION_COUNT
        blend_color = (int(red * q_intensity), int(green * q_intensity), int(blue * q_intensity), 255)
        cache_key = (diameter, blend_color)
        if cache_key not in self._bloom_cache:
            bloom = smoothscale(self._bloom, (diameter, diameter))
            _ = bloom.fill(blend_color, special_flags=BLEND_RGB_MULT)
            self._bloom_cache[cache_key] = bloom
        bloom = self._bloom_cache[cache_key]
        x, y = pos
        _ = surface.blit(bloom, (x - diameter / 2, y - diameter / 2), special_flags=BLEND_RGB_ADD)

    @override
    def post_fixed_update(self, delta: float) -> None:
        self._prev = self._cells
        self._cells = self._sim.collect()
        for c in self._cells:
            _ = self._buffer.setdefault(c, 0)
        for c in self._to_remove:
            del self._buffer[c]
        self._to_remove.clear()

    @override
    def pre_update(self, delta: float) -> None:
        for k in self._buffer.keys():
            v = self._buffer[k]
            flags = self._sim.get_flags(k)
            if has_any_flag(flags, CellFlag.ALIVE, CellFlag.BORN):
                v += (1 - v) * (1 - math.exp(-10*delta))
            elif has_any_flag(flags, CellFlag.DIED, CellFlag.DEAD):
                v -= 5 * delta
            self._buffer[k] = intensity = max(min(v, 1), 0)
            if intensity <= 0:
                self._to_remove.add(k)


    @override
    def pre_render(self, surface: Surface, alpha: float):
        scale = self._cam.get_pixel_scale()
        zoom = self._cam.get_zoom()
        width = 1.3 * scale
        bbox = self._cam.get_bbox().inflate(width//2, width//2)

        for k in self._buffer.keys():
            intensity = self._buffer[k]
            if intensity > 0:
                if bbox.collidepoint(k.x, k.y):
                    pos = self._cam.world_to_screen(k, alpha)
                    n_intensity = intensity * (zoom**3)
                    if n_intensity > 0.15:
                        self._blit_bloom(
                            surface,
                            ((pos.x)-(width/2), (pos.y)-(width/2)),
                            width/2,
                            CELL_BORN_COLOR,
                            n_intensity
                        )
                    self._blit_bloom(surface, (pos.x-(width/2), pos.y-(width/2)), width*2, CELL_ALIVE_COLOR, intensity)
            else:
                self._to_remove.add(k)

