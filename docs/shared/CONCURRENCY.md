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
| `Trainer.run_episode` × N (one algorithm) | CPU-bound | 5.6–6.4 s / 1500 ep | None — single thread |
| `multi_seed_robustness` (5 seeds × 3 algos × 1500 ep) | CPU-bound | ~89 s | None — serial |
| `alpha_decay_sweep` (6 decays × 3 seeds × 2 algos × 1500 ep) | CPU-bound | ~213 s | None — serial |
| Pygame render + event loop | event-driven | 30 FPS clock-locked | Implicit (Pygame's main loop) |
| Q-table save/load | I/O-bound | < 5 ms | None |
| Config load (YAML) | I/O-bound | < 10 ms | None |
| Hazard generator boot | CPU-bound | < 50 ms | None |
| Chart generation triggered from GUI | CPU-bound, long | minutes | **Process-level (subprocess.Popen)** |
| OS file viewer (open chart, etc.) | I/O / OS-bound | sub-second | **Process-level (subprocess.Popen)** |

The two paths that **do** use process-level isolation are documented
below.

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

## 3. Parallelism we deliberately did not implement

The two analysis sweeps are *embarrassingly parallel*: each
`(algorithm, seed)` cell is independent, so a `multiprocessing.Pool`
across N CPU cores would give ~N× speed-up. The reason it isn't done:

| Cost | Benefit |
|------|---------|
| ~30 lines of Pool boilerplate + per-worker `np.random.seed` discipline | Wall time drops from ~89 s → ~12 s on an 8-core machine for `multi_seed_robustness` |
| Test discipline: parametrised tests must work in worker processes; `pytest` defaults to in-process | Sweep is run **once** per analysis cycle, not in CI |
| Risk: silent correctness regressions if seeding is not exactly per-worker (a known multiprocessing footgun for stochastic RL benchmarks) | Negligible at the 89 s scale |

The decision aligns with the CLAUDE.md "no premature abstraction"
rule and §1's self-critique principle. If a future assignment grew the
sweep envelope to thousands of seeds or required interactive
parameter tuning, the right answer would flip — and the change would
be one Pool added in `analysis/_runner.py`, since the `train_run`
boundary is already pure (config in, history out, no shared state).

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
| 1 | **Operation identification** — CPU-bound vs I/O-bound, right tool, value assessment | ✅ done in §1 above |
| 2 | **Implementation** — process / thread count, dynamic sizing, safe data sharing, correct synchronization | ✅ Process count = 1 (GUI) + 0..1 (`subprocess.Popen` for charts). Sizing is event-driven, not static. Data sharing is *by file* (chart written to `results/comparison/`), which is the safest possible IPC primitive |
| 3 | **Resource management** — proper close, exception handling, prevent memory leaks | ✅ `subprocess.Popen` workers are detached (stdout/stderr → DEVNULL) and exit on their own. `pygame.quit()` is called on GUI exit. Q-table save uses `np.save(path)` which closes the file handle on return |
| 4 | **Safety** — protect shared state, prevent deadlocks, mutual locks | ✅ N/A by design — no shared mutable state across threads/processes. No deadlock surface |

---

## 6. What this document is not

- It is not a claim that the project would not benefit from
  parallelism — it would, modestly. §3 documents the trade-off
  honestly.
- It is not a thread-safety audit of NumPy / Pygame / Matplotlib
  internals. Those libraries have their own safety guarantees that we
  rely on (e.g. NumPy's BLAS calls release the GIL — which is why the
  *future* parallel sweep would be Pool-based, not Thread-based).
- It is not an excuse to avoid concurrency where it would matter:
  the multi-seed sweep is pure-CPU and would respond well to
  `multiprocessing.Pool` if the workload grew an order of magnitude.
  The decision to keep it serial is reviewed each sprint, not once.
