from random import randint
from typing import final, override

from pygae.math import Vec2Like, Vec2

from cell_sandbox.renderers import CellRenderer

from ..core import LifeSimulation, SimulationDigest
from ..registry import simulation


@final
@simulation(CellRenderer)
class TempSimulation(LifeSimulation):

    def __init__(self) -> None:
        self._cells = frozenset()
        _ = self.reload()

    @override
    def reload(self, preset: int | None = None) -> int:
        return 0

    def update_step(self) -> int:
        self._cells = frozenset(Vec2(randint(-40, 40), randint(-40, 40)) for _ in range(10))
        return 0

    def collect(self) -> frozenset[Vec2Like]:
        return self._cells

    def get_color(self, cell: Vec2Like) -> tuple[int, int, int, int] | None:
        if cell in self._cells: return (84, 24, 24, 255)
        return None

    def get_digest(self) -> SimulationDigest:
        return SimulationDigest(
            generation=0,
            preset="N/A",
            alive=0,
        )

    def set_debug(self, dbg: bool) -> None:
        ...
