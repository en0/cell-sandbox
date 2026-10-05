from typing import final, override
from pygame import Surface, draw

from pygae.core import GameObject
from pygae.math import Vec2, Vec2Like

from ..core import AColor, CellSimState, LifeSimulation
from ..objects import Camera


COLOR_BG   = (240, 240, 240)
COLOR_CELL = (198, 230, 251)


@final
class ZypherRenderer(GameObject):

    def __init__(self, camera: Camera, sim: LifeSimulation[CellSimState]) -> None:
        super().__init__()
        self._cells: dict[Vec2, AColor | None] = dict()
        self._cam = camera
        self._sim = sim

    @override
    def fixed_update(self, delta: float) -> None:
        self._cells = dict(self._sim.get_state())

    @override
    def pre_render(self, surface: Surface, alpha: float):
        surface.fill(COLOR_BG)
        scale = self._cam.get_pixel_scale()
        width = 0.8*scale
        bbox = self._cam.get_bbox().inflate(width, width)
        for pos, c in self._cells.items():
            if not bbox.collidepoint(pos): continue
            if c:
                _pos = self._cam.world_to_screen(pos, alpha)
                _ = draw.circle(surface, COLOR_CELL, (_pos.x-(width/2), _pos.y-(width/2)), scale)
