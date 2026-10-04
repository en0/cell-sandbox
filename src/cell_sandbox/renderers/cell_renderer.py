from typing import final, override

from pygae.core import GameObject
from pygae.math import Vec2Like
from pygame import Surface, draw

from ..core import LifeSimulation
from ..objects import Camera


COLOR_BG = (0x0a, 0x0a, 0x0a)
DBG_ZOOM = 0.9


@final
class CellRenderer(GameObject):

    def __init__(self, camera: Camera, sim: LifeSimulation) -> None:
        super().__init__()
        self._prev: frozenset[Vec2Like] = frozenset()
        self._cells: frozenset[Vec2Like] = frozenset()
        self._buffer: frozenset[Vec2Like] = frozenset()
        self._cam = camera
        self._sim = sim

    @override
    def fixed_update(self, delta: float) -> None:
        self._cells = self._sim.collect()
        if self._cells == self._prev: return
        self._buffer = self._cells | self._prev
        self._prev = self._cells

    @override
    def pre_render(self, surface: Surface, alpha: float):
        surface.fill(COLOR_BG)
        scale = self._cam.get_pixel_scale()
        self._sim.set_debug(self._cam.get_zoom() > DBG_ZOOM)
        width = scale
        for pos in self._buffer:
            color = self._sim.get_color(pos)
            if color:
                _pos = self._cam.world_to_screen(pos, alpha)
                _ = draw.rect(surface, color, (_pos.x-(width/2), _pos.y-(width/2), width, width))
