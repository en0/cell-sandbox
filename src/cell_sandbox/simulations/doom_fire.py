from random import randint
from typing import final, override

from pygae.math import Vec2
from pygame.math import clamp

from cell_sandbox.renderers.cell_renderer import CellRenderer

from ..core import AColor, CellSimState, LifeSimulation, SimulationDigest
from ..registry import simulation

BOTTOM = 30
HEIGHT = 25
WIDTH = 80
MAX_HEAT = 25


COLOR_MAP: list[AColor|None] = [
    None,
    None,
    (27, 0, 0, 255),
    (50, 0, 0, 255),
    (74, 0, 0, 255),
    (98, 0, 0, 255),
    (121, 0, 0, 255),
    (144, 0, 0, 255),
    (168, 0, 0, 255),
    (191, 0, 0, 255),
    (208, 0, 0, 255),
    (224, 0, 0, 255),
    (240, 0, 0, 255),
    (255, 22, 0, 255),
    (255, 45, 0, 255),
    (255, 69, 0, 255),
    (255, 92, 0, 255),
    (255, 115, 0, 255),
    (255, 137, 0, 255),
    (255, 159, 0, 255),
    (255, 181, 0, 255),
    (255, 202, 0, 255),
    (255, 220, 36, 255),
    (255, 224, 74, 255),
    (255, 232, 120, 255),
    (255, 244, 176, 255),
]


@final
@simulation(CellRenderer)
class DoomFire(LifeSimulation[CellSimState]):

    def __init__(self) -> None:
        self._columns: frozenset[int] = frozenset(w-(WIDTH//2) for w in range(WIDTH))
        self._min_y: int = min(self._columns)
        self._max_y: int = max(self._columns)
        self._generation: int = 0
        self._alive: int = 0

        self._flames: dict[Vec2, int] = {
            Vec2(x, BOTTOM): MAX_HEAT
            for x in self._columns
        }

    @override
    def reload(self, preset: int | None = None) -> int:
        self._generation = 0
        self._alive = 0
        self._flames = {
            Vec2(x, BOTTOM): MAX_HEAT
            for x in self._columns
        }

    @override
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

    @override
    def get_state(self) -> CellSimState:
        return [
            (k, COLOR_MAP[v])
            for k, v in self._flames.items()
            if k.y != BOTTOM
        ]

    @override
    def get_digest(self) -> SimulationDigest:
        return SimulationDigest(
            generation=self._generation,
            preset="DoomFire",
            alive=len(self._flames),
        )
