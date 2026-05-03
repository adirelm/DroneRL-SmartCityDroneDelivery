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
  reports 4.2–4.7 µs / step on the reference machine (refreshed
  Pass-4 §11 from `results/analysis/cost_profile.json`), and a
  scaling table out to 54 K episodes.
- **Resource utilization.** Same doc: peak Python heap (~92–95 KB
  warm), Q-table bytes (4,608 single-table / 9,216 dual-table for
  Double-Q), and the artefact-induced bias in Bellman's first-loop
  measurement (recorded honestly).
- **Capacity.** Verified at the project's reference workload:
  12×12 grid, 1500 episodes, 5 seeds × 3 algorithms in parallel
  via `multiprocessing.Pool` (15 cells). Cost-projection in
  COST_ANALYSIS.md §2 / §3 extends the linear scaling rule to
  96×96 grids (~50 minutes on a single c7i.large vCPU) and a 36 K
  state-space ceiling beyond which function approximation (DQN)
  becomes faster — i.e. the upper bound is named, not implied.

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

Detailed Nielsen-heuristic mapping is in §10 of the audit; sub-attributes
mapped here for 25010 traceability:

- **Learnability.** README "User Workflow" walks the edit → train →
  compare arc; status-bar shortcut row in `_status_bar()`
  ([gui.py:149-151](../../src/dronerl/gui.py#L149-L151)) means the
  user never has to read the manual to discover an action.
- **Operability.** Every action has both keyboard and mouse paths
  (`actions.dispatch` keys + `dashboard.buttons` clicks). `R`
  resets, `SPACE` pauses, `1`/`2`/`3` switch algorithms — same
  semantics in every mode.
- **Accessibility.** Three distinct hue-separated algorithm colours
  (no red/green pair) plus redundant line-style and labelled legend
  on every chart. Colour palette and font sizes are
  `config/config.yaml`-driven so a user with different contrast
  needs can adjust without code. Honest scope note: not WCAG-tested
  via a CVD simulator — see [README "UX & accessibility notes"](../../README.md).
- **User error protection.** Editor refuses placement on start/goal
  cells; rejection now surfaces a 2.5 s flash message in the status
  bar (Pass-4 §10 fix — Nielsen #9). `S`/`L` save/load is a no-op
  when the savefile is missing rather than crashing.
- **Appropriateness recognisability.** README's Objectives + What
  Was Implemented + screenshot gallery (10 PNGs in `assets/assignment-2/`)
  let a first-time visitor see *what* the project does within ~30 s
  of opening the repo — they can recognise whether DroneRL fits
  their need (RL teaching demo, not a production agent).
- **User interface aesthetics.** Four-panel layout (grid /
  dashboard / status bar / optional editor) with toggleable overlays
  (`H` / `A`) keeps the chrome minimal — see screenshot
  `04_training_q_learning.png`. Detailed Nielsen #8 walk in
  §18 [14] below.

## 5. Reliability

> *Maturity, availability, fault tolerance, recoverability.*

- **Maturity.** 348 unit + integration tests, 97.58 % coverage
  (gate ≥ 85 % enforced via `addopts = --cov-fail-under=85` in
  `pyproject.toml`). CI matrix on Python 3.11 / 3.12 / 3.13.
- **Availability.** Scope note: a single-process desktop app has
  no SLO-style availability target — there is no service to be
  "available". The closest meaningful in-product analogue is
  *session continuity*: the GUI can pause / resume mid-training
  without losing state, and an algorithm switch preserves the
  trained Q-table unless the user explicitly resets. (Operability
  proper is mapped under §4.)
- **Fault tolerance.** `_validate_version()` in
  `src/dronerl/config_loader.py` warns on missing/mismatched
  config version. Editor `load` is a no-op when the savefile is
  missing rather than crashing. Factory raises a clear `ValueError`
  for unknown algorithm names (see `agent_factory.create_agent`).
  YAML parse errors surface as wrapped `ConfigError` rather than
  raw `yaml.YAMLError`. Editor refusal of protected START/GOAL
  cells now surfaces a status-bar flash rather than failing
  silently (Pass-4 §10 fix).
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
- **Non-repudiation.** Same scope: no multi-user transactions, no
  signed actions, no audit trail of *who* did what (it's a
  single-user desktop app). What the project *does* have, as the
  closest analogue, is a per-section audit-driven Git history —
  every commit names the § + finding ID it closes, providing
  non-repudiable provenance for *changes* rather than for *user
  actions*.

## 7. Maintainability

> *Modularity, reusability, analysability, modifiability, testability.*

Detailed coverage in §12 of the audit; sub-attributes mapped here for
25010 traceability:

- **Modularity.** 24 source modules in `src/dronerl/`, every file
  ≤ 150 *code* lines (gate excludes blanks/comments per §3.2;
  enforced by `scripts/check_file_sizes.sh` in pre-commit and CI).
  GUI alone splits across `gui.py` / `renderer.py` / `dashboard.py`
  / `overlays.py` / `buttons.py` / `sliders.py` / `editor.py` /
  `logger.py` rather than a monolith.
- **Reusability.** Three-layer agent hierarchy (Pass-3 refactor):
  `BaseAgent → DecayingAlphaAgent → {Q-Learning, Double-Q}` with
  shared `_td_update` kernel; `analysis/_runner.py` shared between
  multi-seed / alpha-decay / noise sweeps; `comparison.py` shared
  between GUI training mode, comparison-chart script, and analysis.
- **Analysability.** ARCHITECTURE.md provides module-by-module
  annotations and ADRs for the non-obvious choices (ADR-002 in
  particular documents the registry choice, the rejected
  `entry_points` alternative, and the rejected single-level
  hierarchy alternative). `BaseAgent._td_update` docstring names
  SARSA as the canonical override target.
- **Modifiability.** `ALGORITHM_REGISTRY` is the single source of
  truth: factory, GUI button labels, GUI keyboard dispatch
  (`actions._ALGO_KEYS` derives from the registry — Pass-4 fix),
  comparison runner, chart palette, analysis scripts, and
  parametrised tests all derive from it. Adding a new algorithm
  is genuinely one `AlgorithmSpec` line + a new subclass.
- **Testability.** 1:1 module ↔ unit-test mapping (26 unit-test
  files in `tests/unit/`, 2 integration files in `tests/integration/`).
  `TestFactoryAgentApi` is parametrised over `list(ALGORITHMS)`;
  `tests/unit/test_extensibility_recipe.py` (Pass-4 fix) registers
  a stub SARSA agent through the registry path on every CI push,
  validating the "Extending it" recipe end-to-end.

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

---

## §18 — Additional International Standards & Sources

§18 of the submission guidelines recommends cross-referencing five
international standards and sources beyond ISO/IEC 25010. Each is
named below with the concrete DroneRL artefact that demonstrates
alignment.

### [14] Nielsen — 10 Usability Heuristics

Each of Nielsen's 10 heuristics is mapped here to a *concrete
artefact* (file path, gate, screenshot) rather than only a
README pointer. The full per-heuristic narrative lives in the
README's *UX & accessibility notes* section.

- **#1 Visibility of system status.** `_status_bar()`
  ([gui.py:141-156](../../src/dronerl/gui.py)) renders mode +
  algorithm + flags + transient flash on every frame. Visible in
  [`assets/assignment-2/03_training_bellman.png`](../../assets/assignment-2/03_training_bellman.png).
- **#2 Match between system and the real world.** Cell-type
  vocabulary (drone / building / trap / pit / wind) chosen for
  domain familiarity; reward keys self-explanatory in
  [`config/config.yaml`](../../config/config.yaml).
- **#3 User control and freedom.** `R` reset, `SPACE` pause,
  algorithm switch never resets the board — see
  [`actions.dispatch`](../../src/dronerl/actions.py).
- **#4 Consistency and standards.** Algorithm colour palette
  driven by `ALGORITHM_REGISTRY` so the same algorithm is the same
  hue in every chart and button.
- **#5 Error prevention.** `Environment.is_protected_cell` refuses
  edits to start/goal; `S`/`L` no-op on missing brain file.
- **#6 Recognition rather than recall.** The status-bar shortcut
  row at the bottom of every frame is the in-app cheat-sheet —
  see [`assets/assignment-2/01_editor_sliders_and_algo_buttons.png`](../../assets/assignment-2/01_editor_sliders_and_algo_buttons.png).
- **#7 Flexibility and efficiency.** Every action has both a
  keyboard shortcut and a mouse-clickable button (the dashboard
  panel doubles as a fall-back path).
- **#8 Aesthetic and minimalist design.** Four panels (grid +
  dashboard + status bar + optional editor) with toggleable
  overlays (`H` heatmap, `A` arrows) — captured in
  [`assets/assignment-2/04_training_q_learning.png`](../../assets/assignment-2/04_training_q_learning.png).
- **#9 Help users recognise, diagnose, recover from errors.**
  Editor-rejection 2.5 s flash message in `gui._on_click`
  (Pass-4 §10 fix); destructive actions documented honestly in
  README's "What I'd do differently" rather than papered over.
- **#10 Help and documentation.** Status-bar cheat-sheet (in-app
  help) + README sections + `CLAUDE.md` / `ARCHITECTURE.md` for
  contributors.

### [15] ISO/IEC 25010 — Software Product Quality Model

This document, sections 1–8 above. Each of the eight quality
characteristics is mapped to the file, gate, or doc that satisfies it.

### [16] MIT Software Quality Assurance Plan

The MIT SQA framework prescribes: documented requirements,
configuration management, testing strategy, code review, defect
tracking, and traceability. DroneRL alignment:

- **Requirements management.** Per-feature PRDs in
  `docs/assignment-2/PRD_*.md`, plus the original
  `docs/assignment-1/PRD.md`. Each PRD names theoretical background,
  I/O requirements, performance metrics, alternatives considered,
  and success criteria.
- **Configuration management.** Single source of truth in
  `config/config.yaml` with a versioned `version` key validated by
  `_validate_version`; missing required top-level blocks are caught
  by `_validate_schema` (warns with the actionable list of missing
  keys); malformed YAML and empty files raise a clear `RuntimeError`
  rather than crashing downstream. `pyproject.toml` + `uv.lock` pin
  every runtime + dev dependency.
- **Testing strategy.** TDD per CLAUDE.md (RED → GREEN → REFACTOR),
  ≥85 % coverage gate (current: 97.58 %), 1:1 module-to-test mapping,
  bit-for-bit determinism test for the parallel sweep
  (`tests/integration/test_parallel_runner.py`).
- **Code review.** Pre-commit hooks (ruff + EOF + 150-line file
  size + pytest pre-push) act as the automated reviewer. The
  GitHub Actions CI matrix on Python 3.11/3.12/3.13 is the second.
- **Traceability.** Git history is per-section audit-driven, with
  each commit's message naming the § it addresses and the specific
  findings + fixes; commits link to the methodology phase
  (`instructions/review_methodology/`). Every audit finding
  ("F<N>.M") is grep-able from the commit log back to the audit
  doc entry that motivated it.
- **Defect tracking — scope note.** MIT SQA prescribes a formal
  defect log / issue tracker as a distinct deliverable. DroneRL
  uses **commit-message-driven defect tracking** (each
  `Pass-N §X: ...` commit names the finding it closes) and the
  per-section audit doc as the long-form defect register.
  Recording this honestly as a *project-scale* alternative rather
  than fabricating an `ISSUES.md` or pretending GitHub Issues are
  in use — the project is solo coursework, not a team workflow.

### [17] Google Engineering Practices

Google's public eng-practices repo prescribes:

- **Code review through small, focused changes.** Mirrored by the
  per-section commit pattern (each §N audit lands one or a few
  commits, all tightly scoped to that section's findings).
- **Style guides as a quality lever.** Mirrored by ruff's `select =
  ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]` rule set in
  `pyproject.toml`. The `N` (PEP 8 naming) rule in particular
  enforces descriptive, consistent names.
- **Testing pyramid.** Mirrored by `tests/unit/` (26 files, fast,
  per-module) ↔ `tests/integration/` (2 files, multi-component +
  parallel-runner determinism). Most coverage lands at the unit
  level by design.
- **Tests as documentation.** The parametrised
  `TestFactoryAgentApi` exercises every algorithm against the same
  fixtures, doubling as a contract-document for what `BaseAgent`
  subclasses must provide.
- **Scope note.** Several Google practices (multi-author code-review
  checklists, post-mortems, design-doc / RFC culture, blameless
  retrospectives, readability certification) **don't apply** to a
  solo coursework project — there's no second reviewer to checklist
  and no production incidents to post-mortem. Recording this
  honestly per the same calibration as [16] MIT defect-tracking and
  [18] Microsoft REST scope-note rather than fabricating
  team-workflow ceremony.

### [18] Microsoft REST API Guidelines

DroneRL has no HTTP surface, but the design principles transfer to
the `DroneRLSDK` Python API:

- **Stable, documented entry points.** `DroneRLSDK` is the single
  orchestration entry point (CLAUDE.md mandate). Public methods
  carry docstrings (added in earlier audit phases) and §16's
  Input / Output / Setup contract block.
- **Versioning.** `pyproject.toml` `version = "1.1.1"` mirrored by
  `dronerl.__version__` and `config/config.yaml`'s `version` key,
  cross-validated by `_validate_version` at start-up.
- **Consistent naming.** All public methods follow `snake_case`,
  enforced by ruff's `N` rule. `save_brain` / `load_brain` /
  `train` / `compare_algorithms` follow a verb-first convention.
- **Predictable error behaviour.** `agent_factory.create_agent`
  raises `ValueError` for unknown algorithm names (with the valid
  list in the message); `_validate_version` warns on missing /
  mismatched config version. No silent failures.
- **Idempotency of operations** (Pass-4 §18 addition). Repeated
  calls are safe and deterministic: `DroneRLSDK.save_brain(path)`
  overwrites the file (no append/duplicate state); `load_brain` is
  a no-op when the brain file is missing rather than crashing;
  `regenerate_hazards()` reseeds from the same RNG state given the
  same seed input; `set_dynamic_params(...)` updates the cached
  hazard parameters in place rather than stacking. The
  `train_step()` / `train_batch(n)` methods are *intentionally*
  non-idempotent (they mutate the agent's Q-table — that's the
  point of training); the Q-table is the externalised mutable
  state, captured by `save_brain` for explicit checkpointing.
- **Backwards compatibility / deprecation policy** (Pass-4 §18
  addition). The SDK is at `1.1.1`; the project's policy is
  semver-style: patch (`1.1.x`) preserves the public API
  (`DroneRLSDK` methods, `BaseAgent` subclass contract,
  `ALGORITHM_REGISTRY` shape); minor (`1.x.0`) may add new entries
  without removing old; major (`x.0.0`) reserved for breaking
  changes. The `_validate_version` cross-check between
  `pyproject.toml` / `__version__` / `config/config.yaml` warns
  on any drift so a stale config doesn't silently load against a
  newer SDK. Backward-compat hacks (e.g. `Agent = BellmanAgent`
  in `src/dronerl/agent.py`) are deliberate kept rather than
  ripped out, so existing tests / external scripts that
  pre-date the rename keep working.

The Microsoft guidelines' "REST" specifics (HTTP verbs, status
codes, URL design) don't apply to a single-process Pygame app —
recording that as a scope note rather than fabricating a fake REST
layer to tick the box.

### Python Enhancement Proposals (PEPs) — also followed

§18 of the submission guidelines names five international standards
above. The project additionally follows three Python-specific
standards that are arguably more directly traceable to source-level
artefacts and worth naming explicitly:

- **[PEP 8](https://peps.python.org/pep-0008/)** — Python style
  guide. Enforced by ruff's `N` rule (`pyproject.toml`'s
  `select = ["E", "F", "W", "I", "N", "UP", "B", "C4", "SIM"]`).
  Naming conventions, line length (`line-length = 100`), and import
  ordering are all gated on every commit.
- **[PEP 257](https://peps.python.org/pep-0257/)** — docstring
  conventions. The §16 "Input / Output / Setup" contract block
  enforced on **15 building-block classes** (`BaseAgent`,
  `DecayingAlphaAgent`, three agent subclasses, `Trainer`,
  `Environment`, `HazardGenerator`, `DroneRLSDK`, `ComparisonStore`,
  `GameLogic`, plus the Pass-4 §16 additions: `Config`, `Renderer`,
  `Dashboard`, `Overlays`) follows the PEP 257 layout (one-line
  summary, blank line, structured body). Verifiable via
  `grep -nE "Input:\|Output:\|Setup:" src/dronerl/*.py`.
- **[PEP 484](https://peps.python.org/pep-0484/)** — type hints.
  Used throughout `src/dronerl/`: e.g. `tuple[int, int]` for
  state, `int | None` for the `n_workers` keyword, `list[float]`
  for histories. Type hints make the §16 Input/Output contracts
  *machine-readable* and human-auditable; honest scope note —
  they are NOT machine-*type-checked* by a gate (no mypy / pyright
  in pre-commit or CI). The annotations are documentation
  augmentation, not runtime enforcement. Adding mypy is a
  reasonable Pass-6+ followup but was scope-noted out for the
  current submission.

These three are arguably the most directly auditable standards in
the project: any reviewer can run `ruff check`, read a class's
docstring, or check a function signature to verify compliance,
without needing to interpret a high-level model.
