from typing import final, override

from pygae.core import GameObject

from goe.core import Actions, LifeSimulation, make_sim_digest, make_sim_speed_event


@final
class Simulation(GameObject):

    def __init__(self, sim: LifeSimulation) -> None:
        super().__init__()
        self._sim: LifeSimulation = sim
        self._play = False
        self._step_forward_held = 0
        self._steps_per_sec = 7.5
        self._step_accum = 0.0
        self._MAX_STEP_PER_FRAME = 64
        self._old_cell_count = 0
        self._generation = 0

    @override
    def on_load(self) -> None:
        self._reload(0)
        self.publish_sim_speed()
        self.publish_simulation_report()

    def _reload(self, p: int | None = None):
        p = self._sim.reload(p)
        if p == -1: return

    def publish_sim_speed(self):
        event = make_sim_speed_event(self._steps_per_sec)
        self.publish(event)

    def publish_simulation_report(self):
        digest = self._sim.get_digest()
        event = make_sim_digest(digest)
        self.publish(event)

    @override
    def pre_fixed_update(self, delta: float):
        if self.input_pressed(Actions.RESET): self._reload()
        if self.input_pressed(Actions.PRESET_0): self._reload(0)
        if self.input_pressed(Actions.PRESET_1): self._reload(1)
        if self.input_pressed(Actions.PRESET_2): self._reload(2)
        if self.input_pressed(Actions.PRESET_3): self._reload(3)
        if self.input_pressed(Actions.PRESET_4): self._reload(4)
        if self.input_pressed(Actions.PRESET_5): self._reload(5)
        if self.input_pressed(Actions.PRESET_6): self._reload(6)
        if self.input_pressed(Actions.PRESET_7): self._reload(7)
        if self.input_pressed(Actions.PRESET_8): self._reload(8)
        if self.input_pressed(Actions.PRESET_9): self._reload(9)

        if self.input_pressed(Actions.INC_SIMSPEED):
            self._steps_per_sec = min(self._steps_per_sec * 2, 240.0)
            self.publish_sim_speed()
        if self.input_pressed(Actions.DEC_SIMSPEED):
            self._steps_per_sec = max(self._steps_per_sec / 2, 1)
            self.publish_sim_speed()
        if self.input_pressed(Actions.SIM_TOGGLE_RUN):
            self._play = not self._play
        if self.input_held(Actions.SIM_STEP):
            self._step_forward_held += 2 * delta
        else:
            self._step_forward_held = 0

        # Single Step
        if not self._play and self._step_forward_held < 1:
            if self.input_pressed(Actions.SIM_STEP):
                self._generation += self._sim.update_step()
        else:
            # Accumlate time
            self._step_accum += self._steps_per_sec * delta
            n = int(self._step_accum)
            if n > self._MAX_STEP_PER_FRAME:
                n = self._MAX_STEP_PER_FRAME
            self._step_accum -= n
            for i in range(n):
                self._generation += self._sim.update_step()
        self.publish_simulation_report()
