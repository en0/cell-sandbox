from typing import final, override

from pygae.core import GameEngine

from cell_sandbox.scenes.brainstorm import BrainStorm
from cell_sandbox.scenes.selection import SelectionScene

from .setting import SCREEN_SIZE, FIXED_DT, MAX_FRAMERATE


@final
class GameOfLife(GameEngine):

    SCREEN_SIZE = SCREEN_SIZE
    FIXED_DT = FIXED_DT
    MAX_FRAMERATE = MAX_FRAMERATE

    @override
    def on_load(self) -> None:
        #self.set_scene(SelectionScene())
        self.set_scene(BrainStorm())
