# DroneRL — Cost & Resource Analysis

This document documents the actual cost of running DroneRL: measured numbers,
the cost model that explains those numbers, and the economic implications if
the same architecture were used for something other than a coursework
assignment.

All numbers are reproducible on the maintainer's machine via:

```bash
uv run python -m analysis.cost_profile
```

The script writes the raw figures to `results/analysis/cost_profile.json`; the
tables below were copied verbatim from one such run on a 2023 MacBook Pro
(Apple M-series, Python 3.13).

---

## 1. Measured per-algorithm cost

1500 training episodes per algorithm, 12×12 grid, medium difficulty
(noise=0.5, density=0.12, difficulty=0.3), seed=11:

| Algorithm  | Wall time | Episodes/s | µs/episode | Peak Python heap | Q-table bytes |
|------------|-----------|-----------:|-----------:|-----------------:|--------------:|
| Bellman    | 5.83 s    | 257        | 3,885      | 971 KB *         | 4,608         |
| Q-Learning | 5.55 s    | 270        | 3,700      | 89.8 KB          | 4,608         |
| Double-Q   | 6.37 s    | 236        | 4,245      | 94.5 KB          | 9,216         |

\* Bellman's headline peak is inflated because it ran first in the loop and
absorbed the lazy-import allocations of NumPy / Matplotlib backends. The
Q-table footprint is 4,608 bytes on every algorithm except Double-Q (which
keeps two tables = 9,216 bytes). I'd consider Q-Learning's 89.8 KB the
honest "RL working set" number, with Bellman/Double-Q expected to sit in
the same ballpark on a warm interpreter.

**Reading the table.** Q-Learning is the cheapest per episode. Bellman is
slightly more expensive only because of an artefact in `decay_epsilon()`
allocations (it gets called every episode but the agent ignores its
own decay since α is constant — see `src/dronerl/agent.py`). Double-Q pays a real
~15% time premium for keeping two Q-tables in sync, which is consistent
with its design.

---

## 2. Cost model — how this scales

The training cost is dominated by tabular Q-table updates and ε-greedy
action sampling, both of which are O(1) per step. Total cost is therefore
linear in the number of *environment transitions*, not in grid size.

```
Wall time ≈ episodes × avg_steps_per_episode × T_step
Memory   ≈ rows × cols × actions × tables × 8 bytes  (float64)
```

Where `T_step` is roughly **3.7–4.2 µs** on the reference machine for
tabular Bellman / Q-Learning / Double-Q. The implied scaling table:

| Workload | Episodes | Estimated time | Q-table memory |
|----------|---------:|----------------|----------------|
| Single dev run (1 algo, 1500 ep) | 1.5 K    | ~6 s    | 4.6–9.2 KB |
| Scenario 1 (3 algos, 3.5K ep)    | 10.5 K   | ~41 s   | ~18.4 KB total |
| Scenario 2 (3 algos, 6K ep)      | 18 K     | ~71 s   | ~18.4 KB total |
| Multi-seed sweep (15 runs)       | 22.5 K   | ~89 s   | per-run, isolated |
| Alpha-decay sweep (36 runs)      | 54 K     | ~213 s  | per-run, isolated |

**Memory scales sublinearly with what matters.** Doubling the grid to 24×24
takes Q-table memory from 4.6 KB to 18.4 KB — still negligible. The wall is
the *state space explosion* once you start adding state dimensions
(velocity, battery, multi-drone), not the grid resolution itself.

---

## 3. When this design stops being free

Tabular Q-learning has a hard ceiling: every state needs its own row in the
Q-table. The bytes are cheap; the *samples needed to fill them* are not.
Sample complexity for tabular Q-learning is roughly `O(|S| × |A| / (1−γ)²)`
in the worst case (Even-Dar & Mansour, 2003) — meaning that to keep
training cost linear, the state space must stay small.

Concrete back-of-envelope numbers using the measured 3.9 µs/step:

- **Current** 12×12 grid (144 states): 1500 episodes train in ~6 s.
- **24×24 grid** (576 states): if convergence still takes ~10 episodes per
  state visit, ~40 s — still fine.
- **48×48 grid** (2304 states): ~3 minutes — borderline.
- **96×96 grid or with velocity dimension** (~36K states): ~50 minutes.
  At this point function approximation (DQN with a small MLP) starts being
  faster *and* more memory-efficient because the network parameters don't
  grow with the state count.

A natural cloud comparison: on AWS `c7i.large` (~$0.09/hr on-demand,
2 vCPUs), a 1500-episode dev run costs roughly **$0.0002** of compute.
The full README comparison suite (multi-seed + decay sweep) is **~$0.008**.
The price-per-experiment is so low that the only real cost gates are
developer time and disk space for charts.

**Where the cost picture would actually flip.** If the same lab were
extended to:

- A function-approximation baseline (DQN, ~1M parameters): GPU-time
  becomes the bottleneck. A T4 spot instance is ~$0.20/hr, and one DQN run
  at the same problem complexity is more like 30 minutes — so a single
  comparison sweep would cost ~$5–10 instead of $0.01.
- A multi-agent variant (≥ 2 drones with shared environment): state space
  multiplies, sample complexity blows up, and even tabular methods become
  expensive enough to matter.
- Hyperparameter optimisation at scale (e.g. Optuna with 200 trials on
  Scenario 2): ~200 × 71 s = ~4 hours of single-machine time, or ~$0.40.

These are not part of this assignment — but documenting them is the point
of "cost awareness": the architecture *currently* costs nothing, and the
shape of "what makes it stop costing nothing" is mostly about state-space
growth, not about training-time tuning.

---

## 4. Operational footprint

Beyond the algorithm itself, the project ships with:

| Artifact | Cost |
|----------|------|
| Comparison charts (PNG) | 80–160 KB each, 4 files = ~440 KB |
| Pygame GUI | RAM dominated by font + tile rendering, idles at ~80 MB |
| Test suite | 315 tests, ~12 s wall time |
| CI workflow | One run on push: ~3 min cumulative across the 3.11/3.12/3.13 matrix |

CI on GitHub Actions is free for public repos (within Actions minutes
limits). The dependency footprint at install time (`uv sync --dev`) is
`pygame + numpy + matplotlib + pyyaml + pytest + pytest-cov + ruff`,
totalling ~80 MB on disk.

---

## 5. Development cost — the AI-assisted side

The runtime numbers above are the cheap part. The expensive part is what it
costs to *build* a project like this when most of the code is generated by
Claude through Claude Code. The course is explicitly a "Vibe Coding"
workshop, so reasoning about the development-side cost is part of being
honest about how this artifact came into existence.

### Time

I'm reporting *order of magnitude* numbers, not stopwatch-accurate ones.
Across both assignments, focused development time was approximately:

| Phase                                            | Estimated hours |
|--------------------------------------------------|----------------:|
| Assignment 1 (Bellman + GUI + tests + docs)      | 25–40           |
| Assignment 2 (Q-Learning + Double-Q + comparison)| 15–25           |
| Assignment 2 polish after lecturer feedback      | 8–15            |
| **Total**                                        | **~50–80 h**    |

The *naïve* expectation about AI assistance is "it makes me 10× faster".
That has not been my experience. What it actually does is **redistribute**
the time:

- **Less time** writing boilerplate, scaffolding test files, drafting
  docstrings, looking up library APIs.
- **More time** reading generated code carefully, deciding whether the
  AI's "obvious" approach is the right one, and reverting choices that
  looked clean but coupled things badly. The `BaseAgent` abstraction
  (mentioned in the README's "What I'd do differently") is one example
  where the first AI-generated draft had to be redesigned once Double-Q
  exposed a missing assumption.
- **Net effect**: rough subjective estimate of 1.5–2× faster than a hand-
  written equivalent, not an order of magnitude. The asymmetry matters
  because most of the *intellectual* work is still on the human side.

### Tokens & subscription cost

Token usage is hard to pin down precisely without instrumenting the
sessions, but for an order-of-magnitude estimate based on typical Claude
Code workflows:

- **Per focused hour of pair-programming**: roughly 100K–500K tokens
  (input + output combined; with prompt caching, repeated context costs
  are dramatically reduced). A long context-heavy session — like the
  ones I used for the comparison-runner refactor — sits at the upper end.
- **Across 50–80 hours**: somewhere between **5M and 40M tokens** total.
  This is a wide range; I'm choosing not to fake precision.

Translated to Anthropic API list prices (Sonnet 4.x at $3/MTok input,
$15/MTok output) the *if-billed-pay-as-you-go* cost would be roughly in
the **$30–$300** range for the entire project, depending on the
input/output mix and how aggressively prompt caching kicks in.

In practice I'm using a Claude **Max** subscription (~$200/month). For
the subscription user, marginal cost per session is $0 within rate
limits, so the effective cost is a function of *how many billing periods
the project spans* (in this case, two). Real outlay: **~$200–400** of
subscription, *plus* whatever fraction of API costs were incurred when
specific features (e.g. occasional Codex/GPT cross-checks) hit other
providers.

### Per-model breakdown

Estimated token usage by model and direction across the whole project
(both assignments + the post-feedback iteration). These are
order-of-magnitude figures derived from typical session sizes — I did
not instrument the sessions; the runtime / billing platform does the
exact accounting.

| Model | Input Tokens (est.) | Output Tokens (est.) | List-price unit | Total Cost (est.) |
|-------|--------------------:|---------------------:|-----------------|------------------:|
| Anthropic Claude Sonnet 4.x (Claude Code) | ~6 M | ~1.5 M | $3 / $15 per MTok | ~$40 |
| Anthropic Claude Opus 4.x (Claude Code, harder turns) | ~1.5 M | ~0.4 M | $15 / $75 per MTok | ~$53 |
| OpenAI GPT-5.4-Codex (Codex rescue, occasional) | ~0.2 M | ~0.05 M | included in Codex sub | $0 (sub) |
| **Total (list-price equivalent)** | **~7.7 M** | **~1.95 M** | — | **~$93** |
| Subscription paid (Claude Max × 2 months + Codex sub) | — | — | flat | **~$300** |

Two reasons the real outlay (~$300 subscription) is higher than the
list-price equivalent (~$93): (a) subscriptions buy access to
*capabilities* (rate limits, caching, longer context) that an
unsubscribed pay-as-you-go user wouldn't necessarily get; (b) flat
fees overpay for any individual project that doesn't fully consume
the rate-limit envelope. The list-price column is what an external
consumer would pay if they tried to reproduce this exact project
through pay-per-token API access only.

### Optimization strategies

Per §11.1 of the submission guidelines, cost-control techniques that
apply to AI-assisted development:

- **Prompt caching** — Anthropic's prompt cache (5-minute TTL) cuts
  the cost of repeated context (CLAUDE.md, AGENTS.md, recent file
  reads) by ~90 % on cache hits. The methodology's
  [10_self_critique_prompts.md](../../instructions/review_methodology/10_self_critique_prompts.md)
  explicitly chooses cache-friendly delays for `ScheduleWakeup`-style
  loops.
- **Smaller model for boilerplate, larger model for design.** Claude
  Sonnet 4.x covered ~80 % of the project; Opus was reached for only
  the harder design calls (the registry refactor, the Pass-2
  retrospective). This kept the Opus token volume below 2 MTok total.
- **Methodology over re-prompting** — once the
  `instructions/review_methodology/` framework was in place, each
  audit phase ran in one prompt instead of being rebuilt from
  scratch. That's what the user-side "one prompt per phase" rule
  is buying.
- **Avoid model thrash** — when Codex's GPT-5 cross-checks failed
  twice in the post-feedback session, I dropped them rather than
  retrying with random model variants. The rule of thumb:
  if a non-primary model fails twice, don't pay for a third try.
- **Batch verification at the gate** — pre-commit hooks run all
  checks locally so a CI re-run isn't needed for a typo. CI is paid
  per-minute on cloud runners; local cheap pre-commit is the
  batching equivalent of "use a smaller model first".

### Budget management (§11.2)

For a solo coursework project the budget controls are lightweight:

- **Forecasting at scale** — the per-experiment cost projections in
  §2 above (`~$0.01` for the runtime suite) plus the dev-cost
  estimates in this section give a clear order-of-magnitude
  ceiling. Doubling the project size would roughly double the
  Claude subscription months and barely move the runtime cost.
- **Real-time monitoring** — the Claude / Codex billing dashboards
  show usage live; both have built-in soft limits at the
  subscription tier. No custom telemetry pipeline is needed at this
  scale.
- **Overrun alerts** — the subscriptions themselves alert at the
  rate-limit ceiling. A serious production project would add a
  cost-per-merge dashboard via the GitHub Actions billing API, but
  for a coursework deliverable that's over-engineering.

### Hidden costs of the AI workflow

These are easy to under-count and worth naming explicitly:

- **AI-induced rework.** When the model generates a clean-looking
  refactor that turns out to subtly break a behavior (e.g. the
  `switch_algorithm` board-regeneration bug noted in the README), the
  cost is *amplified*: I spent debugging time on a problem I wouldn't
  have introduced if I'd written that line by hand.
- **Context restoration.** Long sessions force a cost when context fills
  up: re-explaining where things are, re-stating constraints, paying
  for a re-read of files the model has already seen. Disciplined use of
  CLAUDE.md / AGENTS.md / scoped tools (`Plan`, `Skill`) reduces this,
  but doesn't eliminate it.
- **Verification overhead.** Every AI-generated change still needs a
  test run + lint run + manual eyeball — that's the gating cost on
  speed. CI (Section 4) is part of how I keep that overhead bounded.
- **Prompts that don't land.** When a request requires 2–3 rounds of
  clarification (this happens routinely), the conversational overhead is
  pure waste from a cost perspective. The mitigation here is investing
  in better up-front prompt structure, which is itself a skill that
  costs hours to develop.

A reasonable rule of thumb from this project: **assume ~20–30% of
AI-assisted dev hours are spent on rework or verification that wouldn't
exist in a hand-written workflow.** That tax is real and shows up
nowhere in the runtime numbers.

### What this means for "design choices"

The runtime cost picture says "this app is essentially free to operate."
The development cost picture is more nuanced: the app was inexpensive in
absolute terms (a few hundred dollars of subscription, ~70 hours of my
time), but the *unit economics* of building software this way only work
because the problem is small enough that AI rework stays bounded. If
this project had to scale into hundreds of files with intricate
cross-module invariants, the AI-rework tax would compound and the cost
calculus would tilt back toward more upfront design and less generation.

This is the strongest design-choice cost signal in the project: not
"cloud is expensive" but **"AI-generated code is cheap to write and
expensive to verify, so keep modules small enough that verification
stays cheap."** That's the actual reason `CLAUDE.md` enforces a 150-line
file limit and 85% coverage minimum — both of those rules exist
specifically to bound the *verification* cost of AI-generated changes.

---

## 6. Tradeoffs the cost picture suggests

These are the design decisions that the cost analysis above informs:

- **Use Q-Learning as the default in the GUI**, not Double-Q. Q-Learning is
  ~15% faster per episode and converges to the same medium-difficulty
  result with much lower seed variance (see [EXPERIMENTS.md](EXPERIMENTS.md)).
  Double-Q's bias correction is worth the cost only on the harder scenario.
- **Don't pre-build a generic "registry" for hazard cell types.** With 4
  hazards the per-cell rendering / reward branches are clear; an indirect
  registry would add complexity without saving real lines. The dispatch
  table in `renderer.py` is *cheaper* per unit of clarity.
- **Skip GPU dependencies entirely.** This project never benefits from
  CUDA/MPS, so the install footprint stays small and CI stays fast.
- **Keep modules under 150 lines.** Driven directly by the AI-rework tax
  above: small modules mean each AI-generated change can be verified in
  isolation. This is a development-cost optimization, not just a style
  rule.

If a future assignment moves to function approximation, the calculus
flips on the first three. The 150-line rule applies regardless.
