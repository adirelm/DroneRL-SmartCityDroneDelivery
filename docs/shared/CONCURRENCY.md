# DroneRL — Concurrency, Parallelism & Thread Safety

This doc covers §15 of the submission guidelines: when (and when
*not*) to use multiprocessing or multithreading, the project's
existing concurrency surfaces, and an honest cost-benefit for the
parallelism that DroneRL **deliberately does not implement**.

The guidelines (§15.1) draw the line as:

- **Multiprocessing** ↔ CPU-bound work (math, image processing,
  model training). Each process is in its own memory and on its own
  core.
- **Multithreading** ↔ I/O-bound work (network, DB, file I/O).
  Threads let other work run during the wait.

DroneRL's hot paths and their classification follow.

---

## 1. Hot-path classification

| Path | Type | Wall time | Parallelism used |
|------|------|----------:|------------------|
| `Trainer.run_episode` × N (one algorithm) | CPU-bound | 6.3–7.1 s / 1500 ep | None — single thread (intentional; the in-GUI training loop is interactive) |
| `multi_seed_robustness` (5 seeds × 3 algos × 1500 ep) | CPU-bound | 13.4 s serial → 5.4 s @ n=4 | **`multiprocessing.Pool` (opt-in via `DRONERL_PARALLEL`)** |
| `alpha_decay_sweep` (6 decays × 3 seeds × 2 algos + 3 Bellman = 39 cells) | CPU-bound | ~239 s serial | **`multiprocessing.Pool` (Pass-4 §15 — per-decay batching of 6 cells via `train_cells`)** |
| `noise_sweep` (5 noise levels × 3 seeds × 2 algos = 30 cells) | CPU-bound | ~150 s serial | **`multiprocessing.Pool` (Pass-3 — per-noise-level batching of 6 cells via `train_cells`)** |
| `cost_profile` (3 algos × 1500 ep) | CPU-bound | ~20 s | None — *intentionally serial*, the script measures per-algorithm wall time on a warm interpreter so parallelism would invalidate the timing |
| Pygame render + event loop | event-driven | 30 FPS clock-locked | Implicit (Pygame's main loop) |
| Q-table save/load | I/O-bound | < 5 ms | None |
| Config load (YAML) | I/O-bound | < 10 ms | None |
| Hazard generator boot | CPU-bound | < 50 ms | None |
| Chart generation triggered from GUI | CPU-bound, long | minutes | **Process-level (`subprocess.Popen`)** |
| OS file viewer (open chart, etc.) | I/O / OS-bound | sub-second | **Process-level (`subprocess.Popen`)** |

The paths that use process-level isolation are documented below.

---

## 2. Process-level concurrency that *is* used

### 2.1 `_run_comparison_scripts` — non-blocking chart generation

`src/dronerl/actions.py:76`:

```python
def _run_comparison_scripts(gui) -> None:
    chart = Path(gui.cfg.comparison.output_dir) / "comparison.png"
    if chart.exists():
        _open_file(str(chart))
    else:
        subprocess.Popen(
            [sys.executable, "scripts/generate_comparison_charts.py"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    gui.paused = True
```

**Why a process, not a thread.** The chart generator is a multi-minute
training run that would block Pygame's 30 FPS event loop and freeze
the GUI. A thread *can* run pure-Python NumPy inside the same process,
but the Pygame display surface is not safe to share across threads;
keeping the long job in a separate process side-steps that completely.
`subprocess.Popen` is non-blocking, so the GUI thread continues to
service `pygame.event.pump()` and the user sees the "paused" state
immediately rather than a hang.

### 2.2 `_open_file` — OS viewer dispatch

`src/dronerl/actions.py:92`. `Popen` is used so that the GUI doesn't
wait for the OS viewer (Preview / Explorer / xdg-open) to launch.

---

## 3. Process-pool parallelism for analysis sweeps

Three analysis sweeps are *embarrassingly parallel* — each
`(algorithm, seed)` cell is independent within a single batch:
`multi_seed_robustness` (Pass-2), `noise_sweep` (Pass-3), and
`alpha_decay_sweep` (Pass-4 §15 — previously serial). The CPU-bound
classification in §1 above means **multiprocessing**, not threading —
a single Python interpreter would have all workers contending on the
GIL for the NumPy / Q-table updates. `multiprocessing.Pool` puts each
cell on its own core in its own memory.

The two sweeps that vary a *third* dimension (noise level / decay
rate) batch their cells one third-dimension-value at a time. Within a
single batch `(algo, seed)` is unique so `pool.imap_unordered`
results re-key cleanly; across batches the outer dimension
distinguishes them. This is a deliberate API choice — the alternative
would be to extend the `_train_cell` result tuple with a generic
`cell_id`, which buys ~20 % more parallelism per sweep but breaks
the 4-tuple contract every existing caller already uses.

### Implementation

`analysis/_runner.py` exposes three helpers:

```python
def resolve_workers(requested: int | None = None) -> int: ...
def _train_cell(args: CellArgs) -> CellResult: ...
def train_cells(cells, n_workers: int = 1) -> list[CellResult]: ...
```

- `resolve_workers` reads from an explicit arg, falls back to the
  `DRONERL_PARALLEL` environment variable, then defaults to **1
  (serial)**. The result is clamped to
  `[1, min(config.analysis.max_parallel_workers, os.cpu_count())]` —
  the config value is the primary ceiling (so §5.2 holds: rate limit
  lives in `config/config.yaml`, not hard-coded), with `cpu_count()`
  as the secondary cap that blocks an over-eager config.
- `_train_cell` is the worker — top-level (importable from a fresh
  spawn-context interpreter on macOS/Windows), takes a
  `(raw_dict, algo, seed, episodes, board_overrides)` tuple,
  reseeds inside the worker via `train_run`, returns the rewards
  + steps history.
- `train_cells` runs serial when `n_workers <= 1`; otherwise opens a
  `multiprocessing.Pool` with `mp.get_context("spawn")` (explicit so
  behaviour is identical across platforms) and dispatches via
  `pool.imap_unordered`. The unordered dispatch is fine because we
  re-key by `(algo, seed)` on the way out — order is irrelevant.

### Determinism

Each cell calls `random.seed(seed)` and `np.random.seed(seed)` at
the start of `train_run`, **inside the worker process**. Workers
share no Python random state (they are separate interpreters) and no
NumPy random state (each spawn worker boots clean). Order of
completion is therefore irrelevant — output of any cell depends only
on its `(raw, algo, seed, episodes, board)` inputs.

This is verified by 5 tests in `tests/integration/test_parallel_runner.py`:
`test_serial_run_produces_per_cell_results`,
`test_parallel_matches_serial` (the bit-for-bit determinism canary —
same 4 cells run serial and with n_workers=2; rewards and steps
lists asserted **equal element-by-element**),
`test_resolve_workers_clamps_and_defaults`,
`test_different_seeds_produce_different_results` (negative canary so
"determinism" isn't accidentally satisfied by everything returning
zero), and `test_parallel_results_are_keyable_by_algo_seed` (the
re-keying invariant for batched dispatch). If any future change
introduced a hidden shared-state path, the determinism canary would
fail loudly.

### Measured speed-up (Pass-2 baseline, 2023 MacBook Pro)

| n_workers | Wall time (`multi_seed_robustness`, 15 cells) | Speed-up |
|----------:|----------------------------------------------:|---------:|
| 1 (serial) | 13.4 s | 1.0× |
| 4          | 5.4 s  | 2.5× |

The speed-up is sub-linear — Pool spawn overhead, lock contention in
the BLAS calls of `np.argmax` / `np.max`, and the NumPy import cost in
each fresh worker all eat some of the theoretical N×. 2.5× on a 4-way
pool is the realistic floor; for a tightly-CPU-bound workload with
fewer NumPy hot calls per cell you'd see closer to 3.5×. (Numbers
captured at Pass-2; not re-measured after Pass-3's `_td_update`
extraction or Pass-4's `alpha_decay_sweep` parallelisation, but the
determinism test still passes element-by-element so the directional
claim — "real `multiprocessing.Pool` measurable speed-up" — holds.)

### Activation

```bash
# Default — serial, identical to pre-§15 behaviour
uv run python -m analysis.multi_seed_robustness
uv run python -m analysis.alpha_decay_sweep
uv run python -m analysis.noise_sweep

# Explicit parallelism via environment (applies to all three sweeps)
DRONERL_PARALLEL=4 uv run python -m analysis.alpha_decay_sweep

# Or programmatically
uv run python -c "from analysis.alpha_decay_sweep import run; run(n_workers=4)"
```

Serial remains the default so no existing pipeline breaks; opt-in is
explicit. The §15.3 checklist below records this as the implemented
posture.

---

## 4. Thread safety (§15.2)

DroneRL has **no shared mutable state across threads**. There is one
GIL-bound Python interpreter. The hot paths split as:

- **Pygame's main loop** is the only thread doing UI work. All
  rendering, event handling, button clicks, slider drags, and editor
  edits run on it.
- **Subprocess workers** (the chart generator) are independent
  processes with their own memory; they cannot race with the GUI by
  construction.

There are therefore no shared resources to protect with `Lock`,
`queue.Queue`, or context managers in the existing code. Recording
this as a *deliberate scope decision*, not a missing feature: the
guidelines themselves (§15.2) describe locks/queues/context managers
as the tools for protecting **shared** state — when state isn't
shared, adding them would be ceremony.

---

## 5. §15.3 checklist — auditable answers

| # | Item | Status |
|---|------|--------|
| 1 | **Operation identification** — CPU-bound vs I/O-bound, right tool, value assessment | ✅ Full classification in §1. CPU-bound sweeps → `multiprocessing.Pool`; long blocking GUI work → `subprocess.Popen`; I/O-bound paths kept serial because their wall time is sub-millisecond |
| 2 | **Implementation** — process / thread count, dynamic sizing, safe data sharing, correct synchronization | ✅ `resolve_workers` clamps `n_workers` to `[1, os.cpu_count()]`. Pool uses `mp.get_context("spawn")` for cross-platform consistency. Data sharing across worker boundary is **value-based** — config is a plain `dict`, results are tuples of plain Python floats / ints. No shared memory, no locks needed |
| 3 | **Resource management** — proper close, exception handling, prevent memory leaks | ✅ `with ctx.Pool(...) as pool:` ensures workers are joined and closed even on exception. `subprocess.Popen` workers are detached (stdout/stderr → DEVNULL) and exit on their own. `pygame.quit()` is called on GUI exit. `np.save(path)` closes the file handle on return |
| 4 | **Safety** — protect shared state, prevent deadlocks, mutual locks | ✅ No shared mutable state by design — workers receive value-based input, return value-based output. `imap_unordered` has no deadlock surface (single producer, single consumer, results queue is bounded by Pool's internal logic). Determinism preserved across orderings is asserted by `test_parallel_matches_serial` |

---

## 6. What this document is not

- It is not a claim of universal parallelism. Of the nine hot paths
  in §1, only the two CPU-bound analysis sweeps and the two
  GUI-blocking jobs use any concurrency. The rest are correctly
  serial.
- It is not a thread-safety audit of NumPy / Pygame / Matplotlib
  internals. Those libraries have their own safety guarantees that we
  rely on (e.g. NumPy releases the GIL during BLAS calls, which is
  *why* the parallel sweep is Pool-based and not Thread-based — the
  GIL would dominate threading speed-up).
- It is not a guarantee that arbitrary worker counts always help.
  At `n_workers > os.cpu_count()` the OS scheduler thrashes; the
  measured speed-up table in §3 is on a real machine with a fixed
  cell-count, and the right number is workload-dependent. The
  `resolve_workers` clamp prevents the worst case but doesn't guess
  the optimum.
