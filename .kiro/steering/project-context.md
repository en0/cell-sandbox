# Project Context: Game of Ecology (goe)

Background so your teaching is grounded in this specific codebase. Use it to point at
fundamentals, not to solve problems.

## What this is

A "Game of Ecology" — a sandbox of cellular-automata and grid simulations (Conway's
Game of Life, Brian's Brain, Doom Fire, Wave Function Collapse). It is a learning
vehicle for the concepts underneath: grids, neighborhoods, state-transition rules,
rendering, and game loops.

## Stack

- Python >= 3.12, managed with `uv`.
- Built on a local `pygae` engine (`../pygae`), which wraps `pygame`.
- Tests: `pytest` (plus `pytest-watcher` / `ptw` for watch mode).
- Entry point: `gol` script -> `goe:main`; run module via `python -m goe`.

## Layout (`src/goe/`)

- `core.py` — shared types: the `LifeSimulation` Protocol, `SimulationDigest`,
  `Actions`, `Events`, and event factory functions.
- `game.py` — `GameOfLife` game engine subclass; loads the scene.
- `setting.py` — screen/sim constants and which `SIMULATION` and `RENDERER` are active.
- `simulations/` — the individual automata implementations.
- `scenes/` — scene wiring (input, camera, rendering).
- `objects/` — supporting objects.
- `helpers.py` — utilities (`ascii2tuple`, `random_field`, `normalize_value`).
- `tests/` in `src/tests/`.

## Teaching hooks

- The `LifeSimulation` Protocol is the central abstraction. When Ian works on a new
  simulation, anchor discussion in what each method (`update_step`, `collect`,
  `get_color`, `reload`, `get_digest`) is really responsible for and why.
- Cellular automata rest on fundamentals worth returning to: the grid representation,
  the neighborhood definition, and the pure state-transition rule.

Follow `learning-mode.md` for all guidance. This file is context, not license to
write code.
