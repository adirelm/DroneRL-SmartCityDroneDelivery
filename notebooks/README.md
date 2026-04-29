# `notebooks/`

Reproducible analysis notebooks — execute end-to-end inside Jupyter or VS
Code's Python kernel and produce every chart inline.

## Files

- [`research_analysis.ipynb`](research_analysis.ipynb) — runs all three
  experiments (multi-seed robustness, alpha-decay sweep, cost profile),
  displays the charts inline, and links back to
  [`docs/assignment-2/EXPERIMENTS.md`](../docs/assignment-2/EXPERIMENTS.md)
  for the deeper write-up.

## Running

```bash
uv sync --dev --with jupyter notebook        # install jupyter once
uv run jupyter notebook notebooks/research_analysis.ipynb
```

Or open in VS Code with the Python kernel — the notebook puts the repo
root on `sys.path` from its first cell so `import analysis` works.

## Why a notebook AND a markdown write-up?

Per the course-wide submission guidelines (§9.2 — *Results Analysis
Notebook*) the lecturer wants a Jupyter notebook *or similar tool* that
shows the analysis end-to-end. We keep the deeper hypothesis-by-hypothesis
write-up in `EXPERIMENTS.md` (markdown) because that's where the
narrative lives, and use the notebook as the executable mirror — every
claim in `EXPERIMENTS.md` can be reproduced by running this notebook.
