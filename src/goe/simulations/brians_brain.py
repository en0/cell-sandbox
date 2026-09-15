from typing import final, override

from pygae.math import Vec2, Vec2Like

from goe.core import CellFlag, LifeSimulation, SimulationDigest
from goe.helpers import ascii2tuple

_NEIGHBORS = ascii2tuple("""
    ###
    #.#
    ###
""")


_PRESETS = [
    ("glider", {
        Vec2(x, y): CellFlag.ALIVE for x, y in ascii2tuple("""
        #.#.#.#.#.
        .#.#.#.#.#
        #.#.#.#.#.
        .#.#.#.#.#
        #.#.#.#.#.
        .#.#.#.#.#
        #.#.#.#.#.
        .#.#.#.#.#
       """)
    }),
    ("chaos", {
        Vec2(x, y): CellFlag.ALIVE for x, y in ascii2tuple("""
        ......
        ......
        ##..##
       """)
    }),
    ("worm", {
        Vec2(x, y): CellFlag.ALIVE for x, y in ascii2tuple("""
           ##..##
           ##..##
           ##..##
       """)
    }),
]



@final
class BriansBrainSimulation(LifeSimulation):

    WIDTH = 50
    HEIGHT = 50

    def __init__(self):
        self._index = 0
        self._generation = 0
        self._cells: dict[Vec2, CellFlag] = dict()

    @override
    def reload(self, preset: int | None = None) -> int:
        # Only change if its valid.
        # If none given, change to the current (just a reset)
        if preset is not None:
            if 0 <= preset < len(_PRESETS):
                self._index = preset
            else:
                return -1

        _, self._cells = _PRESETS[self._index]

        self._generation = 0
        return self._index

    @override
    def update_step(self) -> int:
        if len(self._cells) == 0:
            return self._generation

        counts: dict[Vec2, int] = {}
        for k, v in self._cells.items():
            if v == CellFlag.ALIVE:
                _ = counts.setdefault(k, 0)
                for neighbor in (k+n for n in _NEIGHBORS):
                    count = counts.get(neighbor, 0)
                    counts[neighbor] = count + 1


        new_state = {}
        for k, v in counts.items():
            x, y = k
            if -self.WIDTH > x or x > self.WIDTH: continue
            if -self.HEIGHT > y or y > self.HEIGHT: continue
            if self._cells.get(k, 0) == CellFlag.ALIVE:
                new_state[k] = CellFlag.DIED
            elif self._cells.get(k, 0) != CellFlag.DIED and v == 2:
                new_state[k] = CellFlag.ALIVE
        self._cells = new_state

        self._generation += 1
        return self._generation

    @override
    def collect(self) -> frozenset[Vec2Like]:
        return frozenset(self._cells.keys())

    @override
    def get_digest(self) -> SimulationDigest:
        preset_name, _ = _PRESETS[self._index]
        return SimulationDigest(
            generation=self._generation,
            preset=preset_name,
            alive=len(self._cells),
            born=-1,
            died=-1,
        )

    @override
    def get_flags(self, cell: Vec2Like) -> CellFlag:
        return self._cells.get(cell, CellFlag.DEAD)

