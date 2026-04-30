# `docs/` Index

The course-wide submission guidelines (§2.2) call for `docs/PRD.md`,
`docs/PLAN.md`, and `docs/TODO.md` at the top of `docs/`. This project
spans two assignments with overlapping work, so the documents are
organised under per-assignment subdirectories. **This file is the
top-level pointer the guidelines expect.**

## Where each mandatory document lives

| Mandatory doc (per §2.2) | Active location | Notes |
|---|---|---|
| **`docs/PRD.md`** (Product Requirements) | [`docs/assignment-1/PRD.md`](assignment-1/PRD.md) | Initial scope: Bellman + GUI + tests + comparison surface. |
| **`docs/PLAN.md`** (Architecture & Planning) | [`docs/assignment-1/PLAN.md`](assignment-1/PLAN.md) and [`docs/shared/ARCHITECTURE.md`](shared/ARCHITECTURE.md) | The high-level plan + ADRs are in `ARCHITECTURE.md` (which is also the project's navigation index). The phase-level breakdown is in `assignment-1/PLAN.md`. |
| **`docs/TODO.md`** (Task tracking) | [`docs/assignment-1/TODO.md`](assignment-1/TODO.md) | 860 tasks, all completed. Per-phase definitions-of-done at the top of the file. |

## Specialized PRDs (per §2.3)

Assignment 2 introduced three new mechanisms; each got its own PRD:

- [`docs/assignment-2/PRD_q_learning.md`](assignment-2/PRD_q_learning.md) — Q-Learning (decaying α) + the registry refactor
- [`docs/assignment-2/PRD_double_q_learning.md`](assignment-2/PRD_double_q_learning.md) — Double Q-Learning (Hasselt 2010)
- [`docs/assignment-2/PRD_dynamic_board.md`](assignment-2/PRD_dynamic_board.md) — slider-driven hazard generator + `CellType.PIT`

Each specialized PRD includes: theoretical background, I/O requirements,
performance metrics, alternatives considered, and success criteria.

## Plans, TODOs, and per-assignment artefacts

```
docs/
├── INDEX.md                   ← this file
├── assignment-1/
│   ├── PRD.md                 ← satisfies §2.2.a
│   ├── PLAN.md                ← satisfies §2.2.b (with ARCHITECTURE.md)
│   └── TODO.md                ← satisfies §2.2.c (860 tasks, ✓)
├── assignment-2/
│   ├── PRD_q_learning.md      ← §2.3 specialized PRD
│   ├── PRD_double_q_learning.md
│   ├── PRD_dynamic_board.md
│   ├── PLAN_q_learning.md     ← per-feature PLAN
│   ├── PLAN_double_q_learning.md
│   ├── PLAN_dynamic_board.md
│   ├── TODO_q_learning.md     ← 560 tasks, ✓
│   ├── TODO_double_q_learning.md  (662 tasks, ✓)
│   ├── TODO_dynamic_board.md  (910 tasks, ✓)
│   ├── EXPERIMENTS.md         ← research log (hypotheses + findings)
│   ├── COST_ANALYSIS.md       ← runtime + AI development cost
│   ├── final_review_progress.md  (gitignored — methodology tracker)
│   └── submission_guidelines_audit.md (gitignored)
└── shared/
    ├── ARCHITECTURE.md        ← navigation index + ADRs
    ├── QUALITY_STANDARDS.md   ← ISO/IEC 25010 quality-characteristics map
    ├── CONCURRENCY.md         ← multiprocessing / threading / thread safety
    ├── FINAL_CHECKLIST.md     ← pre-submission §17 sweep (every item mapped)
    └── PROMPTS.md             ← prompt log + post-feedback iteration
```

## Reading order for a new contributor / grader

1. **Start at the project README** ([`../README.md`](../README.md)) for
   the public-facing overview.
2. **Then `docs/shared/ARCHITECTURE.md`** for the navigation index, the
   layered architecture, and the ADRs.
3. **Then the assignment of interest** (`docs/assignment-1/` or
   `docs/assignment-2/`) for PRD → PLAN → TODO depth.
4. **For Assignment 2 specifically**, follow it with
   [`assignment-2/EXPERIMENTS.md`](assignment-2/EXPERIMENTS.md) (research
   findings) and [`assignment-2/COST_ANALYSIS.md`](assignment-2/COST_ANALYSIS.md)
   (cost story).
5. **For "how the project was built"**, see
   [`shared/PROMPTS.md`](shared/PROMPTS.md), which logs the prompts and
   the post-feedback iteration phase.
6. **For ISO/IEC 25010 quality-characteristic mapping**, see
   [`shared/QUALITY_STANDARDS.md`](shared/QUALITY_STANDARDS.md). It maps
   each of the eight 25010 characteristics to the artefact, file, or
   gate in this repo that satisfies it.
7. **For concurrency / parallelism trade-offs**, see
   [`shared/CONCURRENCY.md`](shared/CONCURRENCY.md). It classifies
   each hot path as CPU- or I/O-bound, documents the
   `subprocess.Popen` surfaces and the `multiprocessing.Pool`
   sweep parallelism, and includes the §15.3 checklist.
8. **For the pre-submission final-checklist sweep (§17)**, see
   [`shared/FINAL_CHECKLIST.md`](shared/FINAL_CHECKLIST.md). It
   walks every §17.1–§17.6 item and maps it to the concrete file,
   gate, or doc that satisfies it.
