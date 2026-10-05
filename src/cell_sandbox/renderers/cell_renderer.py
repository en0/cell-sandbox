from typing import final, override

from pygae.core import GameObject
from pygae.math import Vec2Like
from pygame import Surface, draw

from ..core import AColor, CellSimState, LifeSimulation
from ..objects import Camera


COLOR_BG = (0x0a, 0x0a, 0x0a)


@final
class CellRenderer(GameObject):

    def __init__(self, camera: Camera, sim: LifeSimulation[CellSimState]) -> None:
        super().__init__()
        self._prev: frozenset[Vec2Like] = frozenset()
        self._cells: frozenset[Vec2Like] = frozenset()
        self._buffer: frozenset[Vec2Like] = frozenset()
        self._colors: dict[Vec2Like, AColor | None] = dict()
        self._cam = camera
        self._sim = sim

    @override
    def fixed_update(self, delta: float) -> None:
        self._colors = dict(self._sim.get_state())
        self._cells = frozenset(self._colors.keys())
        if self._cells == self._prev: return
        self._buffer = self._cells | self._prev
        self._prev = self._cells

    @override
    def pre_render(self, surface: Surface, alpha: float):
        surface.fill(COLOR_BG)
        scale = self._cam.get_pixel_scale()
        box = self._cam.get_bbox()
        width = scale
        for pos in self._buffer:
            if not box.collidepoint(pos): continue
            if color := self._colors.get(pos):
                _pos = self._cam.world_to_screen(pos, alpha)
                _ = draw.rect(surface, color, (_pos.x-(width/2), _pos.y-(width/2), width, width))
