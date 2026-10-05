from collections.abc import Iterable
from enum import IntEnum, StrEnum, auto
from typing import Callable, NamedTuple, Protocol, TypeVar

from pygae.core import GameObject
from pygae.math import Vec2, Vec2Like
from pygame import USEREVENT, Rect
from pygame.event import Event


T = TypeVar("T")

AColor = tuple[int, int, int, int]
CellSimState = Iterable[tuple[Vec2, AColor | None]]
GraphSimState = tuple[
    Iterable[tuple[Vec2, AColor]],       # Nodes
    Iterable[tuple[Vec2, Vec2, AColor]], # Edges
]


class SimulationDigest(NamedTuple):
    generation: int
    preset: str
    alive: int = -1
    died: int = -1
    born: int = -1


class LifeSimulation(Protocol[T]):

    def reload(self, preset: int | None = None) -> int:
        ...

    def update_step(self) -> int:
        ...

    def get_state(self) -> T:
        ...

    def get_digest(self) -> SimulationDigest:
        ...

    # TODO: get rid of this. it's not the simulations job. it's the renderer
    def set_debug(self, dbg: bool) -> None:
        ...


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
