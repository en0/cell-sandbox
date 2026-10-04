
from typing import final

from pygae.core import GameObject
from pygame import K_DOWN, K_RETURN, K_UP, Surface
from pygame.font import SysFont

from ..registry import collect_simulations
from cell_sandbox.scenes.simulation import SimulationScene
from cell_sandbox.setting import SCREEN_SIZE


SCREEN_CENTER_X = SCREEN_SIZE[0]//2
SCREEN_CENTER_Y = SCREEN_SIZE[1]//2

FONT_SIZE = 25
FONT_COLOR = (255, 255, 255, 255)
FONT_COLOR_SEL = (255, 55, 55, 255)
BG_COLOR = (0, 0, 0, 255)

LINE_HEIGHT = FONT_SIZE + 10


@final
class SelectionScene(GameObject):

    def __init__(self) -> None:
        super().__init__()
        self._selected_index = 0
        self._sims = collect_simulations()
        self._font = None

    def on_load(self) -> None:
        self._selected_index = 0
        self._font = SysFont("Arial", FONT_SIZE)
        self.bind_keyboard_button("MENU_SELECT", K_RETURN)
        self.bind_keyboard_button("MENU_DOWN", K_DOWN)
        self.bind_keyboard_button("MENU_UP", K_UP)

    def pre_fixed_update(self, delta: float):
        if self.input_pressed("MENU_UP"):
            self._selected_index -= 1
        if self.input_pressed("MENU_DOWN"):
            self._selected_index += 1
        self._selected_index = max(min(self._selected_index, len(self._sims) - 1), 0)
        if self.input_pressed("MENU_SELECT"):
            _, sim, ren = self._sims[self._selected_index]
            self.set_scene(SimulationScene(self, ren, sim()))

    def pre_render(self, surface: Surface, alpha: float):
        surface.fill(BG_COLOR)

    def post_render(self, surface: Surface, alpha: float):
        surfs = []
        for i, (name, *_) in enumerate(self._sims):
            bg_color = FONT_COLOR_SEL if i == self._selected_index else None
            surf = self._font.render(name, True, FONT_COLOR, bg_color)
            surfs.append(surf)

        half_hight = len(surfs) * LINE_HEIGHT
        for i, s in enumerate(surfs):
            half_width = s.get_width()//2
            x = SCREEN_CENTER_X - half_width
            y_pad = SCREEN_CENTER_Y - half_hight
            surface.blit(s, (x, LINE_HEIGHT*i+y_pad))

