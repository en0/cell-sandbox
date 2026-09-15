from typing import final, override

from pygae.input import AXIS_MWHEEL_DY, DEVICE_KEYBOARD, DEVICE_MOUSE, TYPE_AXIS, TYPE_BUTTON, InputBinding
from pygae.input.types import IInputService
from pygame import K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9, K_0, K_DOWN, K_HOME, K_RETURN, K_SPACE, K_UP, K_a, K_d, K_e, K_f, K_q, K_r, K_s, K_w, Surface

from pygae.core import GameObject

from goe.core import Actions, LifeSimulation
from goe.objects import Camera, HeadsUpDisplay, Simulation, Renderer, ZypherRenderer
from goe.objects.render_fancy import FancyRenderer
from goe.setting import RENDERER, SIMULATION
from goe.simulations import DoomFire, GolSimulation, BriansBrainSimulation


@final
class SimulationScene(GameObject):

    def _bind_keys(self):
        input_srv = self.get_service(IInputService)
        input_srv.bind(Actions.PAN_LEFT, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_a))
        input_srv.bind(Actions.PAN_RIGHT, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_d))
        input_srv.bind(Actions.PAN_UP, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_w))
        input_srv.bind(Actions.PAN_DOWN, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_s))
        input_srv.bind(Actions.PAN_HOME, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_HOME))
        input_srv.bind(Actions.DEC_SIMSPEED, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_q))
        input_srv.bind(Actions.INC_SIMSPEED, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_e))
        input_srv.bind(Actions.SIM_TOGGLE_RUN, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_RETURN))
        input_srv.bind(Actions.SIM_STEP, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_SPACE))
        input_srv.bind(Actions.SIM_STEP_HOLD, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_f))
        input_srv.bind(Actions.ZOOM, InputBinding(TYPE_AXIS, DEVICE_MOUSE, AXIS_MWHEEL_DY))
        input_srv.bind(Actions.ZOOM_IN, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_UP))
        input_srv.bind(Actions.ZOOM_OUT, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_DOWN))
        input_srv.bind(Actions.RESET, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_r))
        input_srv.bind(Actions.PRESET_0, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_1))
        input_srv.bind(Actions.PRESET_1, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_2))
        input_srv.bind(Actions.PRESET_2, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_3))
        input_srv.bind(Actions.PRESET_3, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_4))
        input_srv.bind(Actions.PRESET_4, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_5))
        input_srv.bind(Actions.PRESET_5, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_6))
        input_srv.bind(Actions.PRESET_6, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_7))
        input_srv.bind(Actions.PRESET_7, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_8))
        input_srv.bind(Actions.PRESET_8, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_9))
        input_srv.bind(Actions.PRESET_9, InputBinding(TYPE_BUTTON, DEVICE_KEYBOARD, K_0))

    @override
    def on_load(self) -> None:

        self._bind_keys()

        # TODO: Presets feed into sim. Use "save" service
        camera = Camera()
        sim = self._get_simulation()
        simulation = Simulation(sim)
        renderer = self._get_renderer(camera, sim)

        self.spawn_child(camera)
        self.spawn_child(simulation)
        self.spawn_child(renderer)
        self.spawn_child(HeadsUpDisplay())

    @override
    def pre_render(self, surface: Surface, alpha: float):
        _ = surface.fill("black")

    @staticmethod
    def _get_simulation():
        if SIMULATION == "GameOfLife":
            return GolSimulation()
        elif SIMULATION == "BriansBrain":
            return BriansBrainSimulation()
        elif SIMULATION == "DoomFire":
            return DoomFire()
        raise ValueError(f"Unknown Simulation {SIMULATION}")

    @staticmethod
    def _get_renderer(camera: Camera, sim: LifeSimulation):
        if RENDERER == "standard":
            return Renderer(camera, sim)
        elif RENDERER == "zypher":
            return ZypherRenderer(camera, sim)
        elif RENDERER == "bloom":
            return FancyRenderer(camera, sim)
        raise ValueError(f"Unknown Renderer {RENDERER}")

