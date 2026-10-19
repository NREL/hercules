# Agent Instructions for Hercules

Use this file as the default working agreement when editing this repository.

## Project Intent

- Hercules is an open-source, real-time hybrid plant **simulation** framework.
  It co-simulates wind, solar, storage, electrolyzers and thermal plants and can be
  driven by an external controller such as Hycon.
- Prefer simple, concise implementations over clever abstractions.
- Keep changes scoped to the requested task. Avoid broad refactors unless requested.

## Hercules Conventions

### Units

Hercules uses a strict units convention (see [docs/units.md](docs/units.md)):

- **Power is in kW** everywhere in component interfaces, `h_dict`, YAML input, and
  logged output — component ratings, setpoints, `power` channels, `interconnect_limit`,
  etc.
- **Energy is in kWh** in all input/output interfaces (e.g. `energy_capacity`).
- Some models use different units internally for numerical convenience
  (e.g. `BatterySimple` stores energy in kJ and converts at the boundary with
  `kWh2kJ` / `kJ2kWh`). Keep those conversions localized to the component.
- MW / MWh appear only at the presentation layer (plots, analysis, docstring examples).
  Do not add MW/MWh into component interfaces.
- LMP values, if introduced, are in `$/MWh`.

### Central data structure: `h_dict`

Nearly all state flows through a nested dictionary called `h_dict`
(see [docs/h_dict.md](docs/h_dict.md)):

- Top-level simulation keys: `dt`, `starttime`, `endtime`, `starttime_utc`,
  `endtime_utc`, `step`, `time`, `verbose`, `output_dir`, `output_file`, `logging`,
  `plant`, `external_data`, `controller`.
- `plant.interconnect_limit` (kW) is required.
- `plant.locally_generated_power` (kW) is the sum of all `generator`-category
  component powers, computed by `HybridPlant`.
- Plant components are auto-discovered: **any top-level `h_dict` entry whose value
  is a dict containing a `component_type` key is treated as a component**. The key
  itself is a user-chosen `component_name` (e.g. `wind_farm`, `battery_unit_1`) and
  becomes the handle used throughout the run: `h_dict[component_name][...]`.
- Every component must write its output power to
  `h_dict[component_name]["power"]` on each `step`.

### Component names, types, and categories

Three related concepts — do not confuse them (see
[docs/component_types.md](docs/component_types.md)):

| Concept              | Set by                                | Purpose                                                            |
| -------------------- | ------------------------------------- | ------------------------------------------------------------------ |
| `component_name`     | User (YAML top-level key)             | Unique instance ID; key into `h_dict`                              |
| `component_type`     | User (`component_type:` YAML field)   | Registry lookup selecting the Python class                         |
| `component_category` | Developer (class attribute)           | `"generator"`, `"storage"`, or `"load"`; drives sign / aggregation |

- `component_type` is set automatically from the concrete class name — never
  hardcode it.
- `component_category` is a required `ClassVar[str]` on every `ComponentBase`
  subclass; `ComponentBase.__init_subclass__` will raise `TypeError` if it is
  missing or invalid.

### Sign conventions

- `generator` components produce **positive** power.
- `load` components consume power and are **negative**-signed.
- `storage` components are modeled internally with **discharge negative** at the
  component level. `HybridPlant` flips the sign on the setpoint going in and the
  power coming out so that, at the plant level, positive means discharge —
  consistent with generators.

## Architecture and Public API

Public surface exported from `hercules/__init__.py`:

- `HerculesModel` — top-level simulation driver; entry point for running a YAML
  input file (`hercules/hercules_model.py`).
- `HerculesOutput` — convenience reader for the HDF5 output file, exposes
  `.df` (a `pandas.DataFrame`) and `.metadata` (`hercules/hercules_output.py`).
- `HERCULES_ROOT_DIR`, `HERCULES_EXAMPLE_DIR`.

Internal orchestration:

- `HybridPlant` (`hercules/hybrid_plant.py`) instantiates components, aggregates
  `locally_generated_power`, and applies the storage sign convention.
- `COMPONENT_REGISTRY` (`hercules/component_registry.py`) maps `component_type`
  strings to component classes.

## Function Design Themes

- Public analysis / reader helpers that operate on simulation output should take a
  `HerculesOutput` as the first positional argument, named `ho`. Non-`HerculesOutput`
  helpers should be kept private (underscore-prefixed) unless there is a clear
  reason otherwise.
- Component classes take `(h_dict, component_name)` in `__init__` and always
  call `super().__init__(h_dict, component_name)` first.
- Component classes must implement:
  - `__init__(self, h_dict, component_name)`
  - `get_initial_conditions_and_meta_data(self, h_dict) -> dict`
  - `step(self, h_dict) -> dict`
- Both `get_initial_conditions_and_meta_data` and `step` **must return** the
  (possibly-updated) `h_dict`.
- Validate YAML / `h_dict` inputs early in `__init__` with a clear message that
  names the offending key. Prefer raising `ValueError` or `TypeError` over
  silently defaulting for typos.

## Adding a New Component

See [docs/adding_components.md](docs/adding_components.md). In short:

1. Create a new module under `hercules/plant_components/`.
2. Subclass `ComponentBase`, set `component_category`, and implement
   `__init__`, `step`, and `get_initial_conditions_and_meta_data`.
3. Register the class in `COMPONENT_REGISTRY` in
   [hercules/component_registry.py](hercules/component_registry.py).
4. Add a docs page under `docs/` and link it from `docs/_toc.yml` and
   `docs/component_types.md`.
5. Add a `tests/<component>_test.py` and a matching `h_dict_*` fixture in
   `tests/test_inputs/h_dict.py`.

## Module Organization

- Plant components live in `hercules/plant_components/` — one component per file.
- Simulation-level machinery lives directly in `hercules/`
  (`hercules_model.py`, `hybrid_plant.py`, `hercules_output.py`, `utilities.py`,
  `component_registry.py`).
- Shared helpers (logging setup, HDF5 I/O, input loading, unit helpers) go in
  `hercules/utilities.py`. Example-only helpers go in
  `hercules/utilities_examples.py`.
- Grid and resource utilities live in `hercules/grid/` and `hercules/resource/`.
- New public modules should be re-exported from `hercules/__init__.py` if they are
  intended for user code.

## Python Style

- Target Python 3.10+.
- Use Google-style docstrings for public functions, classes, and methods
  (see [docs/contribute.md](docs/contribute.md)).
- Docstring `Args` entries should state units where relevant
  (e.g. `energy_capacity (float): Deliverable energy capacity in kWh.`).
- Follow existing naming and API style in `hercules/plant_components/`.
- Ruff is configured with `line-length = 100`, `target-version = "py310"`, and
  `select = ["E", "F", "I"]`. Format with Ruff.
- Favor readability first: straightforward control flow, minimal nesting, clear
  names. Avoid heavy abstractions (extra inheritance layers, dataclasses,
  metaclasses) beyond what the existing `ComponentBase` pattern requires.

## Input Files and Examples

- Input files are YAML and loaded with `load_hercules_input()` in
  `hercules/utilities.py`. They must contain `dt`, `starttime_utc`, `endtime_utc`,
  and a `plant.interconnect_limit`.
- Example inputs live under `examples/` (see e.g. `examples/hercules_input_example.yaml`
  and the numbered scenario folders). Prefer extending an existing example over
  inventing a new folder layout.
- Post-load `h_dict` test fixtures live in `tests/test_inputs/h_dict.py`. They
  bypass `load_hercules_input` and therefore populate both `starttime_utc` /
  `endtime_utc` (as `pd.Timestamp`) **and** the derived numeric `starttime` /
  `endtime` (seconds). Match this pattern when adding a new fixture.

## Test Conventions

- Tests live in `tests/`, one file per module (e.g. `battery_simple_test.py`
  tests `hercules/plant_components/battery_simple.py`). Regression / integration
  tests live in `tests/regression_tests/` and `tests/example_regression_tests/`.
- Component tests build an `h_dict` from `tests/test_inputs/h_dict.py`, wrap it
  in `copy.deepcopy` before mutating, and instantiate the component directly
  (e.g. `BatterySimple(test_h_dict, "battery")`). There is no shared
  `HerculesOutput` fixture — Hercules is a simulator, not an analysis package.
- Use `pytest` idioms: small `@pytest.fixture` factories are fine; use
  `pytest.approx` (or `numpy.testing.assert_*_almost_equal`) for floating-point
  comparisons.
- New public functions and new components require a matching test file mirroring
  the module name.

## Validation and Tooling

- Work inside the project virtual environment. Both `.venv` (uv-managed) and a
  conda env named `hercules` are supported layouts (see
  [docs/install.md](docs/install.md)).
- Lint and format with Ruff.
- Run the test suite after code changes.
- Run `pre-commit` before finishing; hooks are installed via the `develop` extra
  (`pip install -e ".[develop]"`, then `pre-commit install`).

Recommended commands (pick whichever activation matches your setup):

```bash
# Option A: uv / .venv
source .venv/bin/activate

# Option B: conda
conda activate hercules

ruff check .
ruff format .
pytest
pre-commit run --all-files
```

## Packaging and Naming

- Distribution name (on PyPI / in `pyproject.toml`): `nlr-hercules`.
- Import package name: `hercules` (e.g. `from hercules import HerculesModel`).
- Version is sourced from installed package metadata in
  `hercules/__init__.py` via `importlib.metadata.version("nlr-hercules")`;
  bump the version in `pyproject.toml` rather than hardcoding it elsewhere.
