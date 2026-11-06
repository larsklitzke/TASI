# AGENTS.md

Guidance for coding agents working on the TASI library (Traffic Analysis and Situation
Interpretation). Users of the library find the public API in [`src/tasi/API.md`](src/tasi/API.md),
which is also shipped in the wheel (`site-packages/tasi/API.md`).

## Layout

| Path | Content |
|---|---|
| `src/tasi/pose`, `trajectory`, `dataset` | pandas-based core: `Pose`, `Trajectory`, `TrajectoryDataset`, ... (`geo.py`: geopandas variants) |
| `src/tasi/base.py` | shared base classes (`CollectionBase`, `PoseCollectionBase`) |
| `src/tasi/io/public` | pydantic models (`PosePublic`, `TrajectoryPublic`, ...), extra `io` |
| `src/tasi/io/orm` | SQLAlchemy models and `DatabaseSettings`, extra `io` (+ `database` to connect) |
| `src/tasi/io/osi` | ASAM OSI conversion, extra `osi` |
| `src/tasi/smos`, `extensions/smos` | safety metrics (PET), reachable via `Trajectory.smos` |
| `src/tasi/dlr` | DLR dataset download and readers, extra `download` |
| `src/tasi/plotting` | matplotlib plotting, extras `visualization` and `wms` |
| `src/tasi/calculus.py` | numerical helpers, optionally numba (`performance`) |
| `src/tasi/utils` | index helpers, `has_extra` / `requires_extra` |
| `src/tests` | unittest-style tests, run with pytest |
| `scripts/generate_api.py` | generates `src/tasi/API.md` |
| `doc/source` | Sphinx documentation |

## Concepts

- `Pose`, `Trajectory` and the datasets subclass `pandas.DataFrame` with a `(timestamp, id)`
  row index and multi-level columns, e.g. `("position", "easting")`. Positions are UTM.
- A `TrajectoryDataset` holds many traffic participants, `.trajectory(id)` returns a
  `Trajectory`. The `Geo*` classes are the geopandas variants (`.as_geo()`).
- The public models convert with `Model.from_tasi(obj)` / `.as_tasi()` and to the ORM with
  `.as_orm()` / `Model.from_orm(row)`.
- ORM tables use the placeholder schema `schema`. It is only resolved by engines from
  `DatabaseSettings().create_engine()` via `schema_translate_map`. Settings come from
  `TASI_ORM_*` environment variables or a `.tasiorm` file.

## Optional extras

The base package only depends on `numpy`, `pandas` and `coloredlogs`. Everything else lives in
extras defined in `pyproject.toml` (`geo`, `io`, `database`, `visualization`, `wms`,
`performance`, `dtw`, `download`, `osi`, `all`).

- Never import an optional dependency at module level of a module that the base package or a
  lighter extra imports. Either guard the module with `has_extra(...)` and raise an
  `ImportError` that names the extra (see `tasi/io/__init__.py`), or import inside the function.
- `tasi.utils.base.ExtraMapping` maps each extra to the module `has_extra` checks.
- When adding an extra, update `pyproject.toml` (including `all`), `ExtraMapping`, the extras
  list in `README.md`, `doc/source/getting_started/index.rst`, the header in
  `scripts/generate_api.py` and an `extra-*` job in `.gitlab-ci.yml`.

## Commands

```bash
uv sync --all-extras --group test --group dev      # environment
uv run pytest src/tests                            # all tests (incl. doctests)
uv run pytest src/tests --ignore=src/tests/io/test_orm   # without PostgreSQL
uv run --all-extras python scripts/generate_api.py # regenerate src/tasi/API.md
uv run pyright src/tasi                            # type check (not clean yet)
uv run make -C doc html                            # docs (needs --group docs and pandoc)
```

- `src/tests/io/test_orm` needs a PostgreSQL/PostGIS server configured via `TASI_ORM_*`.
- Some tests download the DLR UT dataset into `src/tasi/dataset/data/`. Never commit it.
- Code style: autopep8 with a line length of 100 (`[tool.autopep8]` in `pyproject.toml`).

## Rules

- Public API changes: add docstrings (Google style, as in the existing code), export the name in
  the package's `__all__`, and regenerate `src/tasi/API.md`. `src/tests/test_api_reference.py`
  fails if the file is outdated.
- The package ships `py.typed`: keep type hints on public functions accurate. pyright still
  reports existing errors; do not add new ones in the code you touch.
- CI runs on GitLab (`.gitlab-ci.yml`); releases are published to PyPI from GitHub Actions.
