import importlib
import pkgutil

from .core import LifeSimulation, RendererConstructor


REGISTRY: list[LifeSimulation] = []


def simulation(renderer: RendererConstructor = None):
    def _wrap(cls: type[LifeSimulation]) -> type[LifeSimulation]:
        REGISTRY.append((cls, renderer))
        return cls
    return _wrap


def collect_simulations() -> list[tuple[str, LifeSimulation]]:
    from . import simulations
    for _, name, _ in pkgutil.walk_packages(simulations.__path__, simulations.__name__ + "."):
        _ = importlib.import_module(name)
    return [(x.__name__, x, y) for x, y in REGISTRY]

