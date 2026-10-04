from enum import IntEnum, StrEnum, auto
from typing import Callable, NamedTuple, Protocol

from pygae.core import GameObject
from pygae.math import Vec2, Vec2Like
from pygame import USEREVENT, Rect
from pygame.event import Event


class SimulationDigest(NamedTuple):
    generation: int
    preset: str
    alive: int
    died: int = 0
    born: int = 0


class LifeSimulation(Protocol):

    def reload(self, preset: int | None = None) -> int:
        ...

    def update_step(self) -> int:
        ...

    def collect(self) -> frozenset[Vec2Like]:
        ...

    def get_color(self, cell: Vec2Like) -> tuple[int, int, int, int] | None:
        ...

    def get_digest(self) -> SimulationDigest:
        ...

    def set_debug(self, dbg: bool) -> None:
        ...

    #TODO: I want to move this to the visitor pattern so the renderer can expect a state object that
    # it knows how to render. My initial idea was to use a generic where get_state returned type T.
    # The issue is with that is get_color becomes part of the identity or i have to return multiple
    # dicts which will increase allocations. The other idea is to have get_cell_state,
    # get_graph_state, etc, so the renderer can call a function that encodes the state shape and use
    # get_color if it makes sense for that simulation. the issue with this is that each new type of
    # simulation will be a new state shape which will mean adding a new simulation type requires me
    # to go hang the new state functions on existing simulations that just return None. I could use
    # a base-class or even a mixin to solve that. Maybe there is a better option. i will slpeed on it.


class Camera(Protocol):

    def get_bbox(self) -> Rect:
        ...

    def world_to_screen(self, world: Vec2Like, alpha: float) -> Vec2:
        ...

    def get_pixel_scale(self) -> float:
        ...

    def get_zoom(self) -> float:
        ...


RendererConstructor = Callable[(Camera, LifeSimulation), GameObject]


class Actions(StrEnum):
    RESET = auto()
    PAN_LEFT = auto()
    PAN_RIGHT = auto()
    PAN_UP = auto()
    PAN_DOWN = auto()
    PAN_HOME = auto()
    DEC_SIMSPEED = auto()
    INC_SIMSPEED = auto()
    SIM_TOGGLE_RUN = auto()
    SIM_STEP = auto()
    SIM_STEP_HOLD = auto()
    ZOOM = auto()
    ZOOM_IN = auto()
    ZOOM_OUT = auto()
    PRESET_0 = auto()
    PRESET_1 = auto()
    PRESET_2 = auto()
    PRESET_3 = auto()
    PRESET_4 = auto()
    PRESET_5 = auto()
    PRESET_6 = auto()
    PRESET_7 = auto()
    PRESET_8 = auto()
    PRESET_9 = auto()


class Events(IntEnum):
    CAM_ZOOM = USEREVENT + 1
    CAM_POS = USEREVENT + 2
    SIM_SPEED = USEREVENT + 3
    SIM_DIGEST = USEREVENT + 4


def make_cam_zoom_event(zoom: float) -> Event:
    return Event(Events.CAM_ZOOM, value=zoom)


def make_cam_pos_event(location: Vec2) -> Event:
    return Event(Events.CAM_POS, value=(location.x, location.y))


def make_sim_speed_event(rate: float) -> Event:
    return Event(Events.SIM_SPEED, value=rate)


def make_sim_digest(digest: SimulationDigest) -> Event:
    return Event(Events.SIM_DIGEST, value=digest)
