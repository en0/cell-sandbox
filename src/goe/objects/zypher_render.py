from typing import final, override

from pygae.core import GameObject
from pygae.math import Vec2Like
from pygame import Surface, draw
from goe.core import LifeSimulation
from goe.objects import Camera


COLOR_BG   = (240, 240, 240)
COLOR_CELL = (198, 230, 251)


@final
class ZypherRenderer(GameObject):

    def __init__(self, camera: Camera, sim: LifeSimulation) -> None:
        super().__init__()
        self._cells: frozenset[Vec2Like] = frozenset()
        self._cam = camera
        self._sim = sim

    @override
    def fixed_update(self, delta: float) -> None:
        self._cells = self._sim.collect()

    @override
    def pre_render(self, surface: Surface, alpha: float):
        surface.fill(COLOR_BG)
        scale = self._cam.get_pixel_scale()
        width = 0.8*scale
        for pos in self._cells:
            if self._sim.get_color(pos):
                _pos = self._cam.world_to_screen(pos, alpha)
                _ = draw.circle(surface, COLOR_CELL, (_pos.x-(width/2), _pos.y-(width/2)), scale)
