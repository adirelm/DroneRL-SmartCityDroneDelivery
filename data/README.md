# `data/` — Input data

Per the course-wide submission guidelines (§2.4), this directory is
reserved for **input** data. The DroneRL project does not currently
consume any external input data — environments are generated in-memory
from `config/config.yaml`, hazards from the `HazardGenerator`, and
seeds from the analysis scripts.

Outputs (saved Q-tables, comparison charts, analysis artefacts) live
in `results/`. See [`../results/`](../results/).

If a future iteration of the project loads pre-recorded trajectories,
demonstration data, or external grids, they belong here.
