from typing import final, override

from pygae.math import Vec2, Vec2Like

from goe.core import LifeSimulation, SimulationDigest
from goe.helpers import ascii2tuple, random_field

_STATE_READY = 0
_STATE_FIRE = 1
_STATE_REFRACTORY = 2

_STATE_TO_COLOR = {
    _STATE_READY: None,
    _STATE_FIRE: (0, 0, 170, 255),
    _STATE_REFRACTORY: (0, 0, 170, 255),
}

_STATE_TO_COLOR_DEBUG = {
    _STATE_READY: (30, 20, 20, 255),
    _STATE_FIRE: (0, 50, 170, 255),
    _STATE_REFRACTORY: (0, 0, 170, 255),
}


_NEIGHBORS = ascii2tuple("""
    ###
    #.#
    ###
""")


_PRESETS = [
    ("Checkers", {
        Vec2(x, y): _STATE_FIRE for x, y in ascii2tuple("""
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
        Vec2(x, y): _STATE_FIRE for x, y in ascii2tuple("""
        ......
        ......
        ##..##
       """)
    }),
    ("worm", {
        Vec2(x, y): _STATE_FIRE for x, y in ascii2tuple("""
           ##..##
           ##..##
           ##..##
       """)
    }),
    ("random", {Vec2(x, y): _STATE_FIRE for x, y in random_field(100, 100)})
]


@final
class BriansBrainSimulation(LifeSimulation):

    WIDTH = 50
    HEIGHT = 50

    def __init__(self):
        self._index = 0
        self._generation = 0
        self._cells: dict[Vec2Like, int] = dict()
        self._prev: frozenset[Vec2Like] = set()
        self._palet = _STATE_TO_COLOR
        self._died: int = 0
        self._born: int = 0

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
        self._prev = frozenset()
        self._died = 0
        self._born = 0

        self._generation = 0
        return self._index

    @override
    def update_step(self) -> int:

        if len(self._cells) == 0:
            return self._generation

        self._died = len(self._prev - self._cells.keys())
        self._born = len(self._cells.keys() - self._prev)
        self._prev = frozenset(self._cells.keys())

        counts: dict[Vec2, int] = {}
        for k, c in self._cells.items():
            if c == _STATE_FIRE:
                _ = counts.setdefault(k, 0)
                for neighbor in (k+n for n in _NEIGHBORS):
                    count = counts.get(neighbor, 0)
                    counts[neighbor] = count + 1


        new_state = {}
        for k, c in counts.items():
            x, y = k
            if -self.WIDTH > x or x > self.WIDTH: continue
            if -self.HEIGHT > y or y > self.HEIGHT: continue
            if self._cells.get(k) == _STATE_FIRE:
                new_state[k] = _STATE_REFRACTORY
            elif self._cells.get(k) != _STATE_REFRACTORY and c == 2:
                new_state[k] = _STATE_FIRE
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
            born=self._born,
            died=self._died,
        )

    @override
    def get_color(self, cell: Vec2Like) -> tuple[int, int, int, int] | None:
        v = self._cells.get(cell, _STATE_READY)
        return self._palet.get(v)

    @override
    def set_debug(self, dbg: bool) -> None:
        self._palet = _STATE_TO_COLOR_DEBUG if dbg else _STATE_TO_COLOR
