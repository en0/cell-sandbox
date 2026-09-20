from collections import deque
from random import randint

from pygae.math import Vec2, Vec2Like
from pygame.math import clamp

from goe.core import LifeSimulation, SimulationDigest

BOTTOM = 30
HEIGHT = 25
WIDTH = 80
MAX_HEAT = 25


COLOR_MAP = [
    None,
    None,
    "#1B0000",
    "#320000",
    "#4A0000",
    "#620000",
    "#790000",
    "#900000",
    "#A80000",
    "#BF0000",
    "#D00000",
    "#E00000",
    "#F00000",
    "#FF1600",
    "#FF2D00",
    "#FF4500",
    "#FF5C00",
    "#FF7300",
    "#FF8900",
    "#FF9F00",
    "#FFB500",
    "#FFCA00",
    "#FFDC24",
    "#FFE04A",
    "#FFE878",
    "#FFF4B0",
]


class DoomFire(LifeSimulation):

    def __init__(self) -> None:
        self._columns: frozenset[int] = frozenset(w-(WIDTH//2) for w in range(WIDTH))
        self._min_y: int = min(self._columns)
        self._max_y: int = max(self._columns)
        self._generation: int = 0
        self._alive: int = 0

        self._flames: dict[Vec2Like, int] = {
            Vec2(x, BOTTOM): MAX_HEAT
            for x in self._columns
        }

    def reload(self, preset: int | None = None) -> int:
        self._generation = 0
        self._alive = 0
        self._flames = {
            Vec2(x, BOTTOM): MAX_HEAT
            for x in self._columns
        }

    def update_step(self) -> int:

        self._alive = 0
        for _y in range(-1, -HEIGHT, -1):
            y = _y+BOTTOM
            for x in self._columns:
                decay = randint(0, 4)
                offset = randint(-1, 1)
                source_x = clamp(x + offset, self._min_y, self._max_y)
                source_heat = self._flames.get((source_x, y+1), 0)
                heat = max(0, source_heat - decay)
                self._flames[Vec2(x, y)] = max(0, heat)
                self._alive += 1 if heat > 0 else 0

        self._generation += 1
        return self._generation

    def collect(self) -> frozenset[Vec2Like]:
        return frozenset(self._flames.keys())

    def get_color(self, cell: Vec2Like) -> tuple[int, int, int, int] | None:
        _, y = cell
        if y == BOTTOM: return None
        h = self._flames.get(cell, 0)
        return COLOR_MAP[h]

        _, y = cell
        if y == BOTTOM: return None
        h = self._flames.get(cell, 0)
        if h < 2: return None
        return (h*10, 0, 0)

    def get_digest(self) -> SimulationDigest:
        return SimulationDigest(
            generation=self._generation,
            preset="DoomFire",
            alive=len(self._flames),
        )

    def set_debug(self, dbg: bool) -> None:
        ...
