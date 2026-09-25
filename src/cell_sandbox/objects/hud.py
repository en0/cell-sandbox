from typing import final, override

from pygae.core import GameObject
from pygame import Surface
from pygame.font import Font, SysFont

from goe.core import Events, SimulationDigest


FONT_SIZE = 25
FONT_COLOR = "#00F0F0"
FONT_PADDING = 7

HUD_CAM_ZOOM = "Zoom"
HUD_CAM_POS = "Location"
HUD_SPEED = "Speed"

HUD_PRESET = "Preset Name"
HUD_GENERATION = "Generation"
HUD_CELL = "Cell Count"


@final
class HeadsUpDisplay(GameObject):


    def __init__(self) -> None:
        super().__init__()
        self._font: Font
        self._lhud: dict[str, Surface | None] = {
            HUD_SPEED: None,
            HUD_CAM_ZOOM: None,
            HUD_CAM_POS: None,
        }
        self._rhud: dict[str, Surface | None] = {
            HUD_PRESET: None,
            HUD_GENERATION: None,
            HUD_CELL: None
        }

    def _render_digest(self, digest: SimulationDigest):
        self._render_rhud_elem(HUD_GENERATION, digest.generation)
        self._render_rhud_elem(HUD_CELL, f"{digest.alive} (born={digest.born}, died={digest.died})")
        self._render_rhud_elem(HUD_PRESET, digest.preset)

    def _render_lhud_elem(self, label, value) -> None:
        img = self._font.render(f"{label}: {value}", True, FONT_COLOR)
        self._lhud[label] = img

    def _render_rhud_elem(self, label, value) -> None:
        img = self._font.render(f"{label}: {value}", True, FONT_COLOR)
        self._rhud[label] = img

    @override
    def on_load(self) -> None:
        self._font = SysFont("Arial", FONT_SIZE)
        self.subscribe(Events.SIM_SPEED, lambda e: self._render_lhud_elem(HUD_SPEED, f"{e.value:.2f} Hz"))
        self.subscribe(Events.CAM_ZOOM, lambda e: self._render_lhud_elem(HUD_CAM_ZOOM, f"{e.value * 100:.2f}%"))
        self.subscribe(Events.CAM_POS, lambda e: self._render_lhud_elem(HUD_CAM_POS, f"{e.value[0]:.2f}, {e.value[1]:.2f}"))
        self.subscribe(Events.SIM_DIGEST, lambda e: self._render_digest(e.value))

        for k in self._lhud.keys():
            self._render_lhud_elem(k, "loading...")

    @override
    def render(self, surface: Surface, alpha: float) -> None:
        self._render_lhud(surface)
        self._render_rhud(surface)

    def _render_lhud(self, surface: Surface) -> None:
        x, y = 0, 0
        for i, img in enumerate(self._lhud.values()):
            if img is not None:
                y = i * (FONT_SIZE + FONT_PADDING) + FONT_PADDING
                x = max(img.get_width() + FONT_PADDING, x)
                _ = surface.blit(img, (FONT_PADDING, y))

    def _render_rhud(self, surface: Surface) -> None:
        x, y = 0, 0
        for i, img in enumerate(self._rhud.values()):
            if img is not None:
                y = (i * (FONT_SIZE + FONT_PADDING) + FONT_PADDING)
                x = max(img.get_width() + FONT_PADDING, x)
                _ = surface.blit(img, (FONT_PADDING+300, y))
