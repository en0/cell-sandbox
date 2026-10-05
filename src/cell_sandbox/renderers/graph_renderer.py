from typing import final, override
from pygame import Surface, draw

from pygae.core import GameObject
from pygae.math import Vec2

from ..core import AColor, GraphSimState, LifeSimulation
from ..objects import Camera


COLOR_BG = (9, 9, 9)


@final
class GraphRenderer(GameObject):

    def __init__(self, camera: Camera, sim: LifeSimulation[GraphSimState]) -> None:
        super().__init__()
        self._lines: list[tuple[Vec2, Vec2, AColor]] = []
        self._nodes: list[tuple[Vec2, AColor]] = []
        self._cam = camera
        self._sim = sim

    @override
    def fixed_update(self, delta: float) -> None:
        a, b = self._sim.get_state()
        self._nodes = list(a)
        self._lines = list(b)

    @override
    def pre_render(self, surface: Surface, alpha: float):
        surface.fill(COLOR_BG)
        scale = self._cam.get_pixel_scale()
        width = 0.8*scale
        for a, b, c in self._lines:
            _a = self._cam.world_to_screen(a, alpha)
            _b = self._cam.world_to_screen(b, alpha)
            _ = draw.line(surface, c, _a, _b, 1)
        for n, c in self._nodes:
            _n = self._cam.world_to_screen(n, alpha)
            _ = draw.circle(surface, c, _n, width)
