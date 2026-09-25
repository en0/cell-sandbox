
from pygae.core import GameObject


class SelectionScene(GameObject):
    def on_load(self) -> None:
        print("Player loaded")

    def pre_fixed_update(self, delta: float):
        print("Player physics step")

    def pre_update(self, delta: float):
        print("Player animation logic")

    def post_render(self, surface: Surface, alpha: float):
        print("Player post-render overlay")

