from random import randint
from typing import final, override

from pygae.math import Vec2

from cell_sandbox.renderers import GraphRenderer

from ..core import GraphSimState, LifeSimulation, SimulationDigest
from ..registry import simulation


@final
@simulation(GraphRenderer)
class TempSimulation(LifeSimulation[GraphSimState]):

    def __init__(self) -> None:
        self._cells = frozenset()
        _ = self.reload()

    @override
    def reload(self, preset: int | None = None) -> int:
        return 0

    @override
    def update_step(self) -> int:
        self._cells = frozenset(Vec2(randint(-40, 40), randint(-40, 40)) for _ in range(10))
        return 0

    @override
    def get_state(self) -> GraphSimState:
        return (
            [(Vec2(10, 0), (255,55,55,255)), (Vec2(0, 10), (255,55,55,255))],
            [(Vec2(10, 0), Vec2(0, 10), (255,55,55,55))],
        )

    @override
    def get_digest(self) -> SimulationDigest:
        return SimulationDigest(
            generation=0,
            preset="N/A",
            alive=0,
        )
