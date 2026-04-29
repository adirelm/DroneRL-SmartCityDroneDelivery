# DroneRL — ISO/IEC 25010 Quality-Characteristics Map

This doc cross-references DroneRL's existing implementation and
documentation against the eight quality characteristics of
**ISO/IEC 25010** (Software Product Quality Model).

The point of this document is *not* to add new quality machinery —
the project already enforces each characteristic through code,
tests, CI, or docs. The point is to name the standard explicitly and
make the mapping auditable, as required by §13 of the submission
guidelines.

For each characteristic I record:

- **What 25010 calls for** — the standard's sub-attributes.
- **How DroneRL satisfies it** — concrete artefact, file, or gate.
- **Honest scope note** — what is *not* in scope and why.

---

## 1. Functional Suitability

> *Functional completeness, correctness, appropriateness.*

- **Completeness.** Three RL algorithms (Bellman, Q-Learning,
  Double Q-Learning) plus a configurable 12×12 grid environment with
  stochastic wind, hazards, and an interactive editor. Every feature
  promised by the assignment brief is delivered (see
  [README.md](../../README.md) feature list).
- **Correctness.** Algorithm-level correctness is verified by
  parametrised tests (`tests/unit/test_agent_factory.py
  ::TestFactoryAgentApi`) and per-algorithm tests
  (`test_agent.py`, `test_q_agent.py`, `test_double_q_agent.py`).
  Empirical correctness of the comparison claims is supported by the
  multi-seed and alpha-decay sweep experiments in
  [docs/assignment-2/EXPERIMENTS.md](../assignment-2/EXPERIMENTS.md),
  including the cases where the textbook prediction was *not*
  observed at this training budget.
- **Appropriateness.** Each algorithm's role is documented:
  Bellman as the constant-α baseline, Q-Learning with decaying α,
  Double-Q with two tables for bias correction. The README's
  "Algorithm Comparison" section explains *when* each helps.

## 2. Performance Efficiency

> *Time behavior, resource utilization, capacity.*

- **Time behavior.** [docs/assignment-2/COST_ANALYSIS.md §1](../assignment-2/COST_ANALYSIS.md)
  reports 3.7–4.2 µs / step on the reference machine, and a
  scaling table out to 54 K episodes.
- **Resource utilization.** Same doc: peak Python heap, Q-table
  bytes, the artefact-induced bias in Bellman's first-loop
  measurement (recorded honestly).
- **Capacity.** §2 of `COST_ANALYSIS.md` derives the linear
  scaling rule and projects memory growth to a 24×24 grid.
  Sample-complexity ceiling discussed in §3 of the same doc.

## 3. Compatibility

> *Co-existence, interoperability.*

- **Co-existence.** No globals; all state is contained in `Config`,
  `BaseAgent`, `Environment`, `Trainer`, `DroneRLSDK`. Multiple
  agents/environments can coexist in one Python process — the
  comparison runner does this every run.
- **Interoperability.** Q-tables are NumPy `.npy` files (NumPy is
  the lingua franca of Python ML). Configs are YAML. Charts are
  PNG. No proprietary serialization formats.
- **Scope note.** No network protocol, no IPC. Single-process
  Pygame app — the interoperability surface is files-on-disk plus
  the `DroneRLSDK` Python API, both of which are open formats.

## 4. Usability

> *Learnability, operability, accessibility, user error protection.*

Already audited under §10 of the submission guidelines. See:

- README → "Keyboard Controls" section (every shortcut is in the
  status bar and in the README — Recognition not Recall).
- README → "UX & accessibility notes" section (Nielsen heuristics
  + accessibility considerations + known limitations).
- `_status_bar()` in `src/dronerl/gui.py` (live operability feedback).
- Editor refuses placement on start/goal cells (user error
  protection).

## 5. Reliability

> *Maturity, availability, fault tolerance, recoverability.*

- **Maturity.** 301 unit + integration tests, 97.62 % coverage
  (gate ≥ 85 % enforced via `addopts = --cov-fail-under=85` in
  `pyproject.toml`). CI matrix on Python 3.11 / 3.12 / 3.13.
- **Availability.** GUI can pause / resume mid-training without
  losing state; algorithm switch never resets the trained Q-table
  unless explicitly requested.
- **Fault tolerance.** `_validate_version()` in
  `src/dronerl/config_loader.py` warns on missing/mismatched
  config version. Editor `load` is a no-op when the savefile is
  missing rather than crashing. Factory raises a clear `ValueError`
  for unknown algorithm names (see `agent_factory.create_agent`).
- **Recoverability.** `DroneRLSDK.save_brain` / `load_brain`
  persist the agent's Q-table(s) to disk; training can resume from
  a checkpoint without re-running episodes.

## 6. Security

> *Confidentiality, integrity, authentication, accountability.*

- **Confidentiality.** No credentials are required, stored, or
  transmitted. `.gitignore` blocks the canonical secret patterns
  (`*.pem`, `*.key`, `credentials.json`, `*.crt`, `*.p12`,
  `*.pfx`, `secrets.json`) so an accidental check-in is caught.
- **Integrity.** `uv.lock` pins every dependency hash; the CI
  workflow runs `uv sync --frozen --dev` so an upstream package
  cannot be silently substituted.
- **Authentication / Accountability.** Single-process desktop app
  with no multi-user surface — there is nobody to authenticate.
  Recording this as a scope note rather than fabricating a
  fictional auth layer (CLAUDE.md mandates "no premature
  abstraction").

## 7. Maintainability

> *Modularity, reusability, analysability, modifiability, testability.*

Already audited under §12. Summary:

- 25 source modules, every file ≤ 150 lines (pre-commit gate +
  CI gate via `scripts/check_file_sizes.sh`).
- `BaseAgent` abstract class + `ALGORITHM_REGISTRY` deliver a
  one-line extension surface for new algorithms.
- 1:1 module ↔ unit-test mapping (one test file per source module).
- ARCHITECTURE.md provides module-by-module annotations and ADRs
  for the non-obvious choices (e.g. ADR-002 — why a registry, not
  `entry_points`).

## 8. Portability

> *Adaptability, installability, replaceability.*

- **Adaptability.** All hyperparameters, colours, dimensions, and
  reward magnitudes live in `config/config.yaml`; behavior changes
  without editing source. CI matrix verifies the codebase runs on
  Python 3.11, 3.12, and 3.13 unchanged.
- **Installability.** `uv sync --dev` is the single install
  command (mandated by `pyproject.toml`'s `requires-python =
  ">=3.11,<3.14"` and the `uv.lock` lockfile). README's "Setup"
  section gives a one-line install path.
- **Replaceability.** `DroneRLSDK` is the single orchestration
  entry point — GUI, scripts, and analysis all go through it. A
  CLI front-end or web front-end can replace the Pygame layer
  without touching the RL code (see README → "Replacing the GUI"
  bullet under "Extending it").

---

## What this document is not

- It is not a *separate* QA process. The gates listed above
  (pre-commit, CI, coverage, file-size) already enforce each
  characteristic — this doc just renames them in 25010 vocabulary.
- It is not a certification claim. ISO/IEC 25010 is a *model* for
  reasoning about software quality, not a pass/fail standard, and
  formal certification was not in scope for this assignment.
- It is not an exhaustive sub-attribute breakdown. The standard
  has ~30 sub-attributes; I have grouped them by characteristic
  and recorded the ones that materially apply to a single-process
  desktop RL learning project.
