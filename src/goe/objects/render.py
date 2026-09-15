from typing import final, override

from pygae.core import GameObject
from pygae.math import Vec2Like
from pygame import Surface, draw
from goe.core import CellFlag, LifeSimulation
from goe.helpers import has_any_flag
from goe.objects import Camera
from goe.setting import CELL_ALIVE_COLOR, CELL_BORN_COLOR, CELL_DEBUG_ZOOM, CELL_DIED_COLOR, CELL_TYPE


_COLORS = {
    CellFlag.ALIVE: CELL_ALIVE_COLOR,
    CellFlag.DIED: CELL_ALIVE_COLOR,
    CellFlag.BORN: CELL_ALIVE_COLOR,
}


@final
class Renderer(GameObject):

    def __init__(self, camera: Camera, sim: LifeSimulation) -> None:
        super().__init__()
        self._prev: frozenset[Vec2Like] = frozenset()
        self._cells: frozenset[Vec2Like] = frozenset()
        self._buffer: frozenset[Vec2Like] = frozenset()
        self._cam = camera
        self._sim = sim

    def _get_color(self, vec: Vec2Like) -> tuple[int, int, int] | None:
        zoom = self._cam.get_zoom()
        flags = self._sim.get_flags(vec)
        if has_any_flag(flags, CellFlag.BORN) and zoom > CELL_DEBUG_ZOOM:
            return CELL_BORN_COLOR
        if has_any_flag(flags, CellFlag.BORN):
            return CELL_ALIVE_COLOR
        elif has_any_flag(flags, CellFlag.DIED, CellFlag.DEAD) and zoom > CELL_DEBUG_ZOOM:
            return CELL_DIED_COLOR
        elif has_any_flag(flags, CellFlag.ALIVE):
            return CELL_ALIVE_COLOR
        return None

    @override
    def fixed_update(self, delta: float) -> None:
        self._cells = self._sim.collect()
        if self._cells == self._prev: return
        self._buffer = self._cells | self._prev
        self._prev = self._cells

    @override
    def pre_render(self, surface: Surface, alpha: float):
        scale = self._cam.get_pixel_scale()
        width = 0.8*scale
        for pos in self._buffer:
            _pos = self._cam.world_to_screen(pos, alpha)
            if CELL_TYPE == "fuzzy" and has_any_flag(self._sim.get_flags(pos), CellFlag.ALIVE, CellFlag.BORN):
                _ = draw.circle(surface, CELL_ALIVE_COLOR, (_pos.x-(width/2), _pos.y-(width/2)), scale)
            else:
                color = self._get_color(pos)
                if color is None: continue
                if CELL_TYPE == "circle":
                    _ = draw.circle(surface, color, (_pos.x-(width/2), _pos.y-(width/2)), scale//2)
                elif CELL_TYPE == "cell":
                    _ = draw.rect(surface, color, (_pos.x-(width/2), _pos.y-(width/2), width, width))
