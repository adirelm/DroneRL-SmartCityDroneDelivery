"""Algorithm registry — single source of truth for the project's RL algorithms.

To add a new algorithm:

    1. Implement a class inheriting from ``BaseAgent`` in its own module.
    2. Append one ``AlgorithmSpec`` to ``ALGORITHM_REGISTRY`` below.

Every module that needs the list of algorithms (factory, GUI controls,
comparison runner, charts, analysis scripts, tests) reads from this registry,
so the previous step is the only one required.
"""

from dataclasses import dataclass

from dronerl.agent import BellmanAgent
from dronerl.base_agent import BaseAgent
from dronerl.double_q_agent import DoubleQAgent
from dronerl.q_agent import QLearningAgent


@dataclass(frozen=True)
class AlgorithmSpec:
    """Metadata for one RL algorithm: identifier, display label, chart color, agent class."""

    name: str
    label: str
    color: str
    agent_class: type[BaseAgent]


ALGORITHM_REGISTRY: tuple[AlgorithmSpec, ...] = (
    AlgorithmSpec("bellman", "Bellman (constant α)", "#d35400", BellmanAgent),
    AlgorithmSpec("q_learning", "Q-Learning (decaying α)", "#2980b9", QLearningAgent),
    AlgorithmSpec("double_q", "Double Q-Learning", "#27ae60", DoubleQAgent),
)

ALGORITHMS: tuple[str, ...] = tuple(spec.name for spec in ALGORITHM_REGISTRY)
ALGORITHM_LABELS: dict[str, str] = {spec.name: spec.label for spec in ALGORITHM_REGISTRY}
ALGORITHM_COLORS: dict[str, str] = {spec.name: spec.color for spec in ALGORITHM_REGISTRY}
AGENT_CLASSES: dict[str, type[BaseAgent]] = {
    spec.name: spec.agent_class for spec in ALGORITHM_REGISTRY
}
