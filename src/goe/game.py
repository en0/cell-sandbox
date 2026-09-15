from typing import final, override

from pygae.core import GameEngine

from goe.scenes import SimulationScene
from goe.setting import SCREEN_SIZE, FIXED_DT, MAX_FRAMERATE


@final
class GameOfLife(GameEngine):

    SCREEN_SIZE = SCREEN_SIZE
    FIXED_DT = FIXED_DT
    MAX_FRAMERATE = MAX_FRAMERATE

    @override
    def on_load(self) -> None:
        self.set_scene(SimulationScene())
