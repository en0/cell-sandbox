import importlib
import pkgutil

from .core import LifeSimulation


REGISTRY: list[LifeSimulation] = []


def simulation(cls: type[LifeSimulation]) -> type[LifeSimulation]:
    REGISTRY.append(cls())
    return cls


def collect_simulations() -> list[tuple[str, LifeSimulation]]:
    from . import simulations
    for _, name, _ in pkgutil.walk_packages(simulations.__path__, simulations.__name__ + "."):
        _ = importlib.import_module(name)
    return [(x.__class__.__name__, x) for x in REGISTRY]

