"""DroneRL — Smart City Drone Delivery using tabular Q-Learning, Double Q-Learning, and Bellman."""

__version__ = "1.1.1"

# Curated public API — `from dronerl import DroneRLSDK` works out of the box.
# Submodules remain importable as `dronerl.<module>`; this layer just hoists
# the most-used classes so the package surface matches §14.2 ergonomics.
from dronerl.agent import BellmanAgent
from dronerl.agent_factory import create_agent
from dronerl.algorithms import (
    AGENT_CLASSES,
    ALGORITHM_COLORS,
    ALGORITHM_LABELS,
    ALGORITHM_REGISTRY,
    ALGORITHMS,
    AlgorithmSpec,
)
from dronerl.base_agent import BaseAgent, DecayingAlphaAgent
from dronerl.config_loader import Config, load_config
from dronerl.double_q_agent import DoubleQAgent
from dronerl.environment import CellType, Environment
from dronerl.q_agent import QLearningAgent
from dronerl.sdk import DroneRLSDK

__all__ = [
    "__version__",
    # Public classes (curated)
    "AlgorithmSpec", "BaseAgent", "BellmanAgent", "CellType", "Config",
    "DecayingAlphaAgent", "DoubleQAgent", "DroneRLSDK", "Environment",
    "QLearningAgent", "create_agent", "load_config",
    # Registry collections
    "AGENT_CLASSES", "ALGORITHM_COLORS", "ALGORITHM_LABELS",
    "ALGORITHM_REGISTRY", "ALGORITHMS",
    # Submodules (importable as `dronerl.<name>`)
    "actions", "agent", "agent_factory", "algorithms", "base_agent",
    "comparison", "config_loader", "constants", "double_q_agent",
    "environment", "hazard_generator", "logger", "q_agent", "sdk",
    "trainer", "buttons", "dashboard", "editor", "game_logic", "gui",
    "overlays", "renderer", "sliders",
]
