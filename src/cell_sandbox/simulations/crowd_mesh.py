"""Crowd Mesh — a distributed "wristband" wave simulation.

================================================================================
CONCEPT (the "stadium wristbands done right" idea)
================================================================================
Scatter N devices ("bands") at fixed positions in a crowd. Each band is an
autonomous agent that only knows its own LOCAL neighborhood — it has NO global
coordinate system and NO seat map. The interesting constraint (and the whole
point) is coordinated GLOBAL behavior emerging from LOCAL-ONLY knowledge.

Real stadiums cheat: a central system addresses each band by its known seat
location. That's the "omniscient controller" model and it's boring precisely
because the seating chart hands you every position for free. Here we throw that
information away on purpose and make the bands earn it back via local signals.

================================================================================
TWO LAYERS — keep these separate in your head
================================================================================
1. GRAPH CONSTRUCTION (slow / one-shot for now):
   How bands discover who is near them and how the controller assembles a
   global topology from local reports.

2. DYNAMICS ON THE GRAPH (fast / per-tick):
   Animations that run ON TOP of the constructed graph. First pass = flood-fill
   "wave" = graph-distance (BFS in hops, or weighted hops) from a source node.

================================================================================
DISCOVERY / REPORTING PROTOCOL (first pass, naive-but-honest)
================================================================================
- Every band has a unique ID and transmits it.
- Each band measures neighbors via a power-falloff signal and reports back an
  EDGE-SET WITH WEIGHTS, where weight = inverted power-falloff (stronger =
  closer, roughly). Report the WEIGHTS, not just a thresholded binary set —
  the controller wants the weighted, directed graph, not bare adjacency.
- Each band applies a lower-bound threshold AND a min/max neighbor count. This
  is a hybrid of fixed-radius and kNN graphs (see failure modes below).
- Controller receives all reports and assembles its view of the world: a
  weighted, DIRECTED graph. This directed graph is the raw material.

ASSUMPTIONS FOR THE FIRST PASS (known simplifications, revisit later):
- Perfect network connectivity. Every report reaches the controller cleanly.
  (Excluding real-world comms/collisions/timing on purpose.)
- Static graph. Bands don't move yet. Sorting the graph is the FIRST problem;
  evolving it performantly is a SECOND, separate problem.
- Signal strength ~= distance. NAIVE: it's really distance PLUS attenuation.
  An obstacle weakens a link without the bands being farther apart. So a weight
  is "effective path cost", not Euclidean distance. (See tomography note.)

================================================================================
GRAPH SORTING — the first big problem, and its two failure modes
================================================================================
FAILURE 1 — ISLANDS (density variance).
  Fixed falloff + fixed threshold => fixed effective radius, but crowd density
  isn't fixed. A tight cluster forms a dense clique that never reaches the
  sparse cells around it => disconnected component. This is the classic
  fixed-radius vs. kNN neighbor-graph tradeoff:
    - fixed-radius: density-sensitive; islands in sparse areas, hairballs in
      dense areas.
    - kNN: every node gets k edges regardless of density; nobody is orphaned,
      but has its own pathology (below).
  The "min and max neighbor count tied to weight" idea is a hybrid of the two.

FAILURE 2 — DIRECTED / ASYMMETRIC EDGES (the subtle one).
  Reported edges are DIRECTED and the asymmetry is SIGNAL, not noise.
  Band A at a cluster edge reports its k strongest neighbors — all INTO the
  cluster. Band B just outside is closer to A than A's weakest reported
  neighbor, but didn't survive A's fierce local competition. B, in the sparse
  region, DOES report A. => edge B->A exists, A->B doesn't.
  A one-directional edge means "this connection spans a density gradient" =>
  it's a CANDIDATE BRIDGE the controller can validate to reconnect islands.

RELATED KNOWN STRUCTURES worth stealing from (we have weights as a proxy for
geometry, not real coordinates):
  - Mutual kNN: keep an edge only if BOTH endpoints picked each other. Gives
    clean clusters but DISCONNECTS them. Useful inverted: the edges it DROPS
    are exactly the directional bridge candidates.
  - Relative Neighborhood Graph / Gabriel Graph: provably connected yet sparse
    ("is anyone in the lens between us?"). The geometric answer to
    "sparse but no islands." Port the idea via weighted edges.

PROPOSED FIRST-PASS PIPELINE:
  1. Bands report weighted, directed edge-sets. (assume perfect comms)
  2. Controller symmetrizes + repairs connectivity, bridging islands using the
     one-directional edges.
  3. Result: ONE connected weighted graph, NO coordinates.
  4. Animate = graph algorithms on it (flood for waves).

================================================================================
ANIMATION: WAVE (graph-native) vs. IMAGE (needs positions)
================================================================================
- WAVE / PULSE / spreading-activation: graph is ENOUGH. A wave is graph-distance
  (flood-fill / BFS) from a source. Looks spatial because graph-distance
  correlates with physical distance. Obstacle attenuation even HELPS — the wave
  routes around gaps like sound would. THIS IS THE FIRST-PASS TARGET.
- IMAGE / "draw a picture" / spell a word: fundamentally needs TRUE positions
  (which band is at "top-left of the T"?). Topology alone can't tell you that.
  That forces graph embedding / MDS (multidimensional scaling): treat pairwise
  weights as a distance matrix, solve for the 2D layout. Sensitive to
  obstacle-noise (warps near obstacles). DEFERRED — harder problem.

================================================================================
PARKED IDEAS (do not chase yet, but capture them)
================================================================================
- TOMOGRAPHY: weight-vs-expected-distance discrepancy is itself a measurement.
  A pair reading weaker than geometry implies => obstacle between them. This is
  Radio Tomographic Imaging. Ill-posed inverse problem (line integrals, CT-scan
  math family), COARSE fidelity in reality (multipath/diffraction). Great toy
  because simulated ground truth lets you SEE why the real thing is hard.
- LOCALIZATION FLIP: known fixed anchors + measured attenuations => solve for
  positions. Turns the sensor net into an indoor positioning system (works
  where GPS dies). Same machinery, bigger prize.
- COMMERCIAL ANGLE: the GRAPH is the product. Crowd density, flow, offline
  emergency relay mesh ("relay toward the north exit" without GPS), sensor
  fusion (graph weight + tomography as extra signals into a Kalman/particle
  filter alongside GPS/WiFi-RTT/BLE/UWB/IMU). Collaborative SLAM (cameras) is
  the solved cousin; pure-RF 3D reconstruction is the hard frontier.

================================================================================
TODO (dig in here) — build order suggestion
================================================================================
  [ ] World model: scatter N bands at fixed positions (+ optional obstacles).
  [ ] Signal model: power-falloff weight between two bands (+ obstacle atten).
  [ ] Per-band local report: thresholded, min/max-count, weighted, DIRECTED.
  [ ] Controller: assemble directed weighted graph from reports.
  [ ] Connectivity repair: detect islands, promote one-directional bridges.
  [ ] Flood-fill wave: BFS/weighted graph-distance from a source per tick.
  [ ] Render: map bands -> grid cells, color by wave phase/intensity.
  [ ] LATER: dynamic graph (bands move), embedding/MDS for pictorial anims,
      tomography, localization.
"""

from dataclasses import dataclass
from typing import Iterable, NamedTuple, Protocol, final, override, runtime_checkable

from pygae.math import Vec2, Vec2Like

from cell_sandbox.renderers.cell_renderer import CellRenderer

from ..registry import simulation
from ..core import LifeSimulation, SimulationDigest


# TODO: constants — N bands, world size, falloff exponent, threshold,
# min/max neighbor counts, obstacle definitions, tile/phase colors.
CELL_POWER = 2500
CELL_POWER_SOFTENING = 2

CellState = tuple[int, tuple[int, int, int, int]]
EdgeReport = tuple[int, list[int, float]]

@runtime_checkable
class Controller(Protocol):

    def update(self, edges: Iterable[EdgeReport]) -> Iterable[CellState]:
        ...


class NaiveController:

    def update(self, edges: Iterable[EdgeReport]) -> Iterable[CellState]:
        # TODO: discover the graph
        # TODO: render the animation
        return [(id_, (55, 55, 255, 255)) for id_, _ in edges]


class Cell(NamedTuple):
    location: Vec2
    color: tuple[int, int, int, int] = (55, 55, 255, 255)


# TODO: presets — different crowd layouts (uniform scatter, clustered,
# with-obstacles, sparse-bridge stress test).
_PRESETS: list[tuple[str, set[Cell]]] = [
    ("debug-1", {
        Cell(Vec2(-10, 0)),
        Cell(Vec2(10, 0)),
    }),
    ("debug-2", {
        Cell(Vec2(-100, 0)),
        Cell(Vec2(100, 0)),
    }),
    ("debug-3", {
        Cell(Vec2(-1, 0)),
        Cell(Vec2(0, 0)),
    })
]


@final
@simulation(CellRenderer)
class CrowdMeshSimulation(LifeSimulation):
    """Distributed wristband-wave sim. See module docstring for the design notes.

    First pass: static kNN-ish directed graph -> connectivity repair -> flood-fill
    wave. No coordinates recovered; wave is graph-distance from a source.
    """

    def __init__(self) -> None:
        self._index: int = 0
        self._generation: int = 0
        self._cells: dict[Vec2, (int, tuple[int, int, int, int])] = {}
        self._ctrl: Controller = NaiveController()
        # TODO: band positions, the directed weighted edge reports, the
        # controller's assembled graph, per-band wave state, source node(s).
        _ = self.reload()

    # --- graph construction (slow / one-shot for now) -----------------------

    # TODO: _signal_weight(a, b) -> float          # power falloff (+ obstacles)
    # TODO: _band_report(band) -> dict[id, weight] # local, thresholded, min/max
    # TODO: _assemble_graph(reports)               # directed weighted graph
    # TODO: _find_islands() / _repair_connectivity() using one-directional edges

    # --- dynamics on the graph (fast / per-tick) ----------------------------

    # TODO: _flood_step()  # advance the wave one hop of graph-distance

    # --- LifeSimulation protocol --------------------------------------------

    @override
    def reload(self, preset: int | None = None) -> int:
        if preset is not None:
            if 0 <= preset < len(_PRESETS):
                self._index = preset
            else:
                return -1
        # TODO: scatter bands, build reports, assemble + repair graph, seed wave.
        self._cells = {x.location: (hash(x.location), x.color) for x in (_PRESETS[self._index][1])}
        self._generation = 0
        return self._index

    @override
    def update_step(self) -> int:

        edges = {}    # A edge for each cell received.
        rev_map = {}  # A reverse map to lookup cell vector by id.

        # Find every edge for every cell.
        for a, (id_, _) in self._cells.items():
            rev_map[id_] = a
            for b, (b_id_, _) in self._cells.items():
                if a != b:
                    # inverse-square k/(r^2 + ε)
                    r = a.distance(b)
                    weight = CELL_POWER / ((r*r) + CELL_POWER_SOFTENING)
                    # scattering the edge out. cell A told cell B it's id.
                    edges.setdefault(b_id_, []).append((id_, weight))

        # Update the controller and get the new display
        # Copy the display into the cell map.
        for id_, color in self._ctrl.update(edges.items()):
            cell = rev_map[id_]
            self._cells[cell] = (id_, color)

        #self._debug_colors(edges)

        self._generation += 1
        return self._generation

    def _debug_colors(self, edges):
        """ DEBUGGING

        change color based on geometric mean of it's edge weights
        """
        for v, (id_, _) in self._cells.items():
            power = sum([w for _, w in edges[id_]]) / len(edges[id_])
            c = min(255, int(power * 0.3))
            color = (c*(55/255), c*(55/255), c, 255)
            self._cells[v] = (id_, color)

    @override
    def collect(self) -> frozenset[Vec2Like]:
        return frozenset(self._cells.keys())

    @override
    def get_color(self, cell: Vec2Like) -> tuple[int, int, int, int] | None:
        _, color = self._cells.get(cell, (None, None))
        return color

    @override
    def get_digest(self) -> SimulationDigest:
        preset_name, _ = _PRESETS[self._index]
        return SimulationDigest(
            generation=self._generation,
            preset=preset_name,
            alive=0,  # TODO: number of active/lit bands
        )

    @override
    def set_debug(self, dbg: bool) -> None:
        # TODO: debug view could draw the edges / highlight bridges + islands.
        ...
