# Tests

The suite is split into two tiers. Run the full suite with:

```bash
uv run pytest tests/
```

## `tests/unit/` (26 files, fast, no I/O beyond temp dirs)

One unit-test file per source module in `src/dronerl/` — the 1:1 mapping is
deliberate (see §6 of the submission audit) and is the reason the
`scripts/check_file_sizes.sh` 150-line cap stays cheap to enforce: small
modules + small focused tests = cheap verification.

Conventions:

- Pure-function or single-class scope. A unit test must not need
  another module's behaviour to be correct.
- No real disk writes outside `tmp_path`. No subprocess spawn. No
  `multiprocessing.Pool`.
- Use the `pygame_ready` / `ui_config` / `ui_agent` / `ui_env` /
  `ui_logic` fixtures from `tests/conftest.py` for GUI-adjacent
  tests; they cover Pygame init + a default `Config`.

Run only the unit tier:

```bash
uv run pytest tests/unit/
```

## `tests/integration/` (2 files, slower, multi-component)

Tests that require the full SDK orchestration path or
`multiprocessing.Pool`-based parallel runs:

- `test_sdk_comparison.py` — exercises `DroneRLSDK.run_comparison`
  end-to-end across the 3 registered algorithms, with the predicted
  algorithm-ordering tolerance pinned at ±5 reward units.
- `test_parallel_runner.py` — bit-for-bit determinism check on
  `analysis._runner.train_cells` under `multiprocessing.Pool` with
  `spawn` context (added in §15 audit; regression test for the
  `imap_unordered` re-keying bug).

Run only the integration tier:

```bash
uv run pytest tests/integration/
```

## Coverage gate

`pyproject.toml` `[tool.pytest.ini_options] addopts = "--cov=src/dronerl
--cov-fail-under=85"` — every plain `uv run pytest` enforces the
≥ 85 % bar. Current: **344 tests, 97.20 % coverage** (Pass-4 §13).

## Adding a new algorithm

`tests/unit/test_extensibility_recipe.py` is the canonical worked example:
it defines a stub SARSA agent inline, registers it via
`ALGORITHM_REGISTRY`, and asserts the factory builds it. Use it as the
template for any new agent type — see also README "Extending it".
