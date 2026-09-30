
from collections import Counter
from random import randint
from typing import Iterable, final, override

from pygae.core import GameObject
from pygae.math import Vec2
from pygame import K_r, Surface, draw

from cell_sandbox.setting import SCREEN_SIZE

SCREEN_CENTER_X = (SCREEN_SIZE[0]//2)
SCREEN_CENTER_Y = (SCREEN_SIZE[1]//2)
SCALE = 0.8

MIN_X, MAX_X = int(-(SCREEN_CENTER_X*SCALE)), int((SCREEN_CENTER_X*SCALE))
MIN_Y, MAX_Y = int(-(SCREEN_CENTER_Y*SCALE)), int((SCREEN_CENTER_Y*SCALE))

POINT_COUNT = 200

LINE_COLOR = (55, 10, 10, 255)
POINT_COLOR = (255, 10, 10, 255)

@final
class BrainStorm(GameObject):

    def __init__(self) -> None:
        super().__init__()
        self._points: list[Vec2] = []
        self._tri: set[tuple[Vec2, Vec2, Vec2]] = set()
        scale_factor = (MAX_X * MAX_Y * 2)
        self._super: tuple[Vec2, Vec2, Vec2] = (
            Vec2(0, -scale_factor),
            Vec2(scale_factor, scale_factor),
            Vec2(-scale_factor, scale_factor),
        )
        self._super_set = set(self._super)

    def _in_circumcircle(self, point: Vec2, tri: tuple[Vec2, Vec2, Vec2]) -> bool:
        # TODO: Change this to use the determinant form.
        a, b, c = tri
        d = 2 * (a.x*(b.y - c.y) + b.x*(c.y - a.y) + c.x * (a.y - b.y))
        ux = ((a.x**2 + a.y**2)*(b.y - c.y) + (b.x**2 + b.y**2)*(c.y - a.y) + (c.x**2 + c.y**2)*(a.y - b.y)) / d
        uy = ((a.x**2 + a.y**2)*(c.x - b.x) + (b.x**2 + b.y**2)*(a.x - c.x) + (c.x**2 + c.y**2)*(b.x - a.x)) / d
        u = Vec2(ux, uy)
        r = u.distance(a)
        return r>=u.distance(point)

    def _collect_boundary(self, tris: list[tuple[Vec2, Vec2, Vec2]]) -> Iterable[tuple[Vec2, Vec2]]:
        counter = Counter()
        for (a, b, c) in tris:
            self._tri.remove((a, b, c))
            for edge in ((a, b), (b, c), (c, a)):
                counter[frozenset(edge)] += 1
        return [e for e, n in counter.items() if n == 1]

    def _add_point(self, point: Vec2):
        bad: list[tuple[Vec2,Vec2,Vec2]] = []

        # Collect bad triangles
        for tri in self._tri:
            if self._in_circumcircle(point, tri):
                bad.append(tri)

        # Remove the bad triangles and create replacement edges to boundary points
        for (v1, v2) in self._collect_boundary(bad):
            self._tri.add((v1, v2, point))

        self._points.append(point)

    def _remove_super_triangle(self):
        self._tri = {
            t for t in self._tri
            if not set(t).intersection(self._super_set)
        }

    def _reset(self) -> None:
        self._points.clear()
        self._tri.clear()
        self._tri.add(self._super)

    def on_load(self) -> None:
        self.bind_keyboard_button("RESET", K_r)
        self._reset()

    def pre_fixed_update(self, delta: float):
        if self.input_pressed("RESET"): self.on_load()
        if len(self._points) >= POINT_COUNT: return
        x = randint(MIN_X, MAX_X)
        y = randint(MIN_Y, MAX_Y)
        self._add_point(Vec2(x, y))

    def pre_render(self, surface: Surface, alpha: float):
        surface.fill("black")

    def post_render(self, surface: Surface, alpha: float):
        for (a, b, c) in self._tri:
            if not {a, b, c}.intersection(self._super_set):
                draw.line(surface, LINE_COLOR, self._to_world(a), self._to_world(b), 1)
                draw.line(surface, LINE_COLOR, self._to_world(b), self._to_world(c), 1)
                draw.line(surface, LINE_COLOR, self._to_world(c), self._to_world(a), 1)
        for point in map(self._to_world, self._points):
            draw.circle(surface, POINT_COLOR, point, 4)

    def _to_world(self, vect: Vec2) -> Vec2:
        return vect + (SCREEN_CENTER_X, SCREEN_CENTER_Y)
