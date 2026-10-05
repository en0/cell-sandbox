from collections import deque
from collections.abc import Generator
from random import choice, choices
from typing import NamedTuple, final, override

from pygae.math import Vec2, Vec2Like
from pygame import Rect

from cell_sandbox.renderers import CellRenderer

from ..core import CellSimState, LifeSimulation, SimulationDigest
from ..helpers import ascii2tuple
from ..registry import simulation


RED = (200, 0, 0, 255)


WIDTH = 100
HEIGHT = 100


NEIGHBORS = ascii2tuple("""
    ##.
    #.#
    .##
""")


T_GRASS_DARK = 0
T_GRASS_STANDARD = 1
T_GRASS_LIGHT = 2
T_GRASS_BRIGHT = 3
T_GRASS_HIGHLIGHT = 4
T_WATER_DEEP = 5
T_WATER_DARK = 6
T_WATER_STANDARD = 7
T_WATER_LIGHT = 8
T_WATER_HIGHLIGHT = 9
T_WATER_SPARKLE = 10
T_TRANSITION_GRASS_WATER = 11

TS_GRASS = set([
    T_GRASS_DARK,
    T_GRASS_STANDARD,
    T_GRASS_LIGHT,
    T_GRASS_BRIGHT,
    T_GRASS_HIGHLIGHT,
])

TS_WATER = set([
    T_WATER_DEEP,
    T_WATER_DARK,
    T_WATER_STANDARD,
    T_WATER_LIGHT,
    T_WATER_HIGHLIGHT,
    T_WATER_SPARKLE,
])

TS_TRANSITION = set([
    T_TRANSITION_GRASS_WATER
])


TILE_COLOR: list[tuple[int, int, int, int]] = [
    (38, 59, 34, 255),   	# Dark grass
    (70, 111, 50, 255),  	# Standard grass
    (92, 137, 58, 255),  	# Light grass
    (120, 168, 74, 255), 	# Bright grass
    (155, 196, 102, 255),	# Grass highlight
    (24, 47, 58, 255),   	# Deep water
    (31, 75, 89, 255),   	# Dark water
    (49, 133, 154, 255), 	# Standard water
    (75, 166, 177, 255), 	# Light water
    (120, 198, 194, 255),	# Water highlight
    (176, 224, 200, 255),	# Water sparkle
    (102, 139, 120, 255),	# Grass-water transition
]


TILES = set(range(len(TILE_COLOR)))


ADJACENT_TILES: dict[int, set[int]] = {

    # Grass band (0-4): each shade blends with itself and its gradient
    # neighbours (+/-1). The light end (4) is where the transition tile can sit.
    0:  set([0, 1]),          # Dark grass
    1:  set([1, 0, 2]),       # Standard grass
    2:  set([2, 1, 3]),       # Light grass
    3:  set([3, 2, 4]),       # Bright grass
    4:  set([4, 3, 11]),      # Grass highlight -> can meet transition

    # Water band (5-10): same internal gradient blending. The light end (8)
    # is where the transition tile can sit.
    5:  set([5, 6]),          # Deep water
    6:  set([6, 5, 7]),       # Dark water
    7:  set([7, 6, 8]),       # Standard water
    8:  set([8, 7, 9, 11]),   # Light water -> can meet transition
    9:  set([9, 8, 10]),      # Water highlight
    10: set([10, 9]),         # Water sparkle

    # Transition (11): the only seam between grass and water. Touches the
    # light ends of both bands and itself, so it forms coherent shorelines.
    11: set([11, 4, 8]),      # Grass-water transition
}


for k in ADJACENT_TILES.keys():
    for v in ADJACENT_TILES[k]:
        ADJACENT_TILES[v].add(k)


_PRESETS: list[tuple[str, dict[Vec2, frozenset[int]]]] = [
    ("open", {}),
    ("shore", {
        Vec2(0, -20):  frozenset([T_GRASS_LIGHT, T_GRASS_STANDARD]),
        Vec2(0, 20):   frozenset([T_WATER_DARK, T_WATER_DEEP]),
        Vec2(-20, 20): frozenset([T_GRASS_LIGHT, T_GRASS_STANDARD]),
    }),
    ("island", {
        Vec2(0, 0):    frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-30, 0):  frozenset([T_WATER_DEEP, T_WATER_DARK]),
        Vec2(30, 0):   frozenset([T_WATER_DEEP, T_WATER_DARK]),
        Vec2(0, -30):  frozenset([T_WATER_DEEP, T_WATER_DARK]),
        Vec2(0, 30):   frozenset([T_WATER_DEEP, T_WATER_DARK]),
    }),
    ("river", {
        Vec2(-45, -20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-40, -20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-35, -20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-30, -20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-25, -20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-20, -20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-15, -20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-10, -20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-5, -20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(0, -20):    frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(5, -20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(10, -20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(15, -20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(20, -20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(25, -20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(30, -20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(35, -20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(40, -20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(45, -20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),

        Vec2(-45, 0):  frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(-40, 0):  frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(-35, 0):  frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(-30, 0):  frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(-25, 0):  frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(-20, 0):  frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(-15, 0):  frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(-10, 0):  frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(-5, 0):  frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(0, 0):    frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(5, 0):   frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(10, 0):   frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(15, 0):   frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(20, 0):   frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(25, 0):   frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(30, 0):   frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(35, 0):   frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(40, 0):   frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),
        Vec2(45, 0):   frozenset([T_WATER_STANDARD, T_WATER_LIGHT]),

        Vec2(-45, 20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-40, 20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-35, 20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-30, 20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-25, 20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-20, 20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-15, 20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-10, 20):  frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(-5, 20):    frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(0, 20):    frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(5, 20):    frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(10, 20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(15, 20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(20, 20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(25, 20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(30, 20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(35, 20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(40, 20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
        Vec2(45, 20):   frozenset([T_GRASS_STANDARD, T_GRASS_LIGHT]),
    }),
]


class _Envelope(NamedTuple):
    root: Vec2
    opts: set[int]


@final
@simulation(CellRenderer)
class WFCSimulation(LifeSimulation):

    def __init__(self) -> None:

        self._world = Rect(0, 0, WIDTH, HEIGHT)
        self._world.center = (0, 0)

        self._generation: int = 0
        self._index: int = 0
        self._cells: dict[Vec2, int] = {}
        self._super_cells: dict[Vec2, set[int]] = {}
        self._buckets: dict[int, set[Vec2]] = {}

        _ = self.reload()

    def _gen_neigbors(self, root: Vec2) -> Generator[Vec2, None, None]:
        """Get the neighbors for the given cell."""
        return (
            root + v
            for v in NEIGHBORS
            if self._world.collidepoint(root+v)
        )

    def _select_tile(self, cell: Vec2) -> int:
        """Select the next cell from the given options of cells.

        This could be where we do some weighting on selections or do some clustering checks, etc.
        """
        def _weight(c, t) -> int:
            ## TODO: ...
            return 10

        tiles = list(self._super_cells[cell])

        weights: list[int] = []
        for tile in tiles:
            weights.append(_weight(cell, tile))

        return choices(tiles, weights, k=1)[0]

    def _pick_next_cell(self, last_attempt: Vec2 | None = None) -> Vec2 | None:
        """Select the lowest entropy cell for the remaining cells

        The last_attempt cell can optionally be provided which the algorithm can use to select a
        better pick
        """
        if len(self._buckets.keys()) == 0: return None
        if last_attempt is not None: return last_attempt
        bucket = min(self._buckets.keys())
        return choice(list(self._buckets[bucket]))

    @staticmethod
    def _collect_adjacent_tile_options(root: Vec2, super_cells: dict[Vec2, set[int]]) -> set[int]:
        """Get the full list of adjacent posibilities for the given root."""
        ret: set[int] = set()
        for p in super_cells[root]:
            for _p in ADJACENT_TILES[p]:
                ret.add(_p)
        return ret

    @staticmethod
    def _compute_bucket(root: Vec2, super_cells: dict[Vec2, set[int]]) -> int | None:
        """Get the bucket for the given root cell.

        This is where we could do some selection weighting to weight some options over others.

        """
        bucket = len(super_cells[root])
        return bucket if bucket > 1 else None

    @override
    def reload(self, preset: int | None = None) -> int:
        # Only change if its valid.
        # If none given, change to the current (just a reset)
        if preset is not None:
            if 0 <= preset < len(_PRESETS):
                self._index = preset
            else:
                return -1

        _, seeds = _PRESETS[self._index]

        self._buckets = {}
        x, y, w, h = self._world
        for _y in range(y, y + h):
            for _x in range(x, x + w):
                v = Vec2(_x, _y)
                s = set(TILES)
                self._super_cells[v] = s
                self._buckets.setdefault(len(s), set()).add(v)
        self._cells = dict()
        self._generation = 0

        tile_count = len(TILES)
        for k, v in seeds.items():
            self._super_cells[k] = set(v)

            if k in self._buckets[tile_count]:
                self._buckets[tile_count].remove(k)
            else:
                # Got to find it :/
                for _bucket, _posabilties in self._buckets.items():
                    if k in _posabilties:
                        _posabilties.remove(k)
                        break

            self._buckets.setdefault(len(v), set()).add(k)
            if not self._try_update_step(k):
                print("WARNING!!! This preset seems to have a constraints!")
                print("Skipping vector", k)

        return self._index

    def _try_update_step(self, current_cell: Vec2) -> bool:

        # Get the next cell and seed the queue with it's details.
        # exit if there is no current cell, means we are done
        current_cell_tile = self._select_tile(current_cell)
        queue = deque([_Envelope(current_cell, {current_cell_tile})])

        # A sparse buffer to track changes to be committed.
        super_cells: dict[Vec2, set[int]] = dict()

        while queue:

            e = queue.popleft()

            # Add the current cell to the sparse buffer
            if e.root not in super_cells:
                super_cells[e.root] = set(self._super_cells[e.root])

            # Merge the options by getting the set-intersection between the adjacent options and the
            # super-positions. keep track of the counts to detect if changes where actually made.
            before = len(super_cells[e.root])
            super_cells[e.root] &= e.opts
            after = len(super_cells[e.root])

            # Contradictions mean we hit a dead end and this cycle is a bust. we have to discard and
            # start over.
            if len(super_cells[e.root]) == 0:
                print("Contradiction")
                return False

            # If we made changes, propogate those changes down to the neighbors
            if before > after:
                _opts = self._collect_adjacent_tile_options(e.root, super_cells)
                for n in self._gen_neigbors(e.root):
                    queue.append(_Envelope(n, set(_opts)))

        # Copy the buffer back to the live sets
        for c in super_cells:

            # Collect the old and new bucket location for the cell 'c'
            bucket_before = self._compute_bucket(c, self._super_cells)
            bucket_after = self._compute_bucket(c, super_cells)

            # Remove the cell from the old bucket and clean out they bucket if it's empty
            if bucket_before is not None and bucket_after != bucket_before:
                self._buckets[bucket_before].remove(c)
                if len(self._buckets[bucket_before]) == 0:
                    del self._buckets[bucket_before]

            # Record the new super-positions
            self._super_cells[c] = super_cells[c]

            # Move collapsed cells into the output
            if len(super_cells[c]) == 1:
                self._cells[c] = next(iter(super_cells[c]))

            # If not collapsed, record the new bucket location
            elif bucket_after is not None and bucket_after != bucket_before:
                self._buckets.setdefault(bucket_after, set()).add(c)

        return True

    @override
    def update_step(self) -> int:

        # Get the next best cell to work on. if none, we are done
        current_cell = self._pick_next_cell()
        if current_cell is None: return self._generation

        # Try for len(tiles) times. once we get a succefull update, return early
        for _ in range(len(TILES)):
            if self._try_update_step(current_cell):
                self._generation += 1
                return self._generation
            # ask the picker to give is a new cell to try.
            current_cell = self._pick_next_cell(current_cell)

        # If we never got a successfull udpate, it's considered impossible. reset and try again
        _ = self.reload()
        return self._generation

    @override
    def get_state(self) -> CellSimState:
        return [(k, TILE_COLOR[v]) for k, v in self._cells.items()]

    @override
    def get_digest(self) -> SimulationDigest:
        preset_name, _ = _PRESETS[self._index]
        return SimulationDigest(
            generation=self._generation,
            preset=preset_name,
            alive=len(self._cells),
        )
