from dataclasses import dataclass
from enum import Flag, IntEnum, StrEnum, auto
from typing import NamedTuple, Protocol

from pygae.math import Vec2, Vec2Like
from pygame import Rect, USEREVENT
from pygame.event import Event


class CellFlag(Flag):
    BORN  = 0b0001
    ALIVE = 0b0010
    DIED  = 0b0100
    DEAD  = 0b1000


class Cell(NamedTuple):
    pos: Vec2
    flags: CellFlag


class SimulationDigest(NamedTuple):
    generation: int
    preset: str
    alive: int
    dead: int = 0
    died: int = 0
    born: int = 0


class LifeSimulation(Protocol):

    def reload(self, preset: int | None = None) -> int:
        ...

    def update_step(self) -> int:
        ...

    def collect(self) -> frozenset[Vec2Like]:
        ...

    def get_flags(self, cell: Vec2Like) -> CellFlag:
        ...

    def get_digest(self) -> SimulationDigest:
        ...


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
