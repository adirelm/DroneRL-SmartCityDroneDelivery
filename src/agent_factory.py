"""Factory for creating RL agents based on config.algorithm.name.

The actual mapping from algorithm name to agent class lives in
``src.algorithms``; this module is a thin wrapper that adds validation.
"""

from src.algorithms import AGENT_CLASSES, ALGORITHMS
from src.base_agent import BaseAgent
from src.config_loader import Config


def create_agent(config: Config) -> BaseAgent:
    """Create the agent specified by ``config.algorithm.name``."""
    name = config.algorithm.name
    if name not in AGENT_CLASSES:
        valid = ", ".join(sorted(ALGORITHMS))
        raise ValueError(f"Unknown algorithm: '{name}'. Valid: {valid}")
    return AGENT_CLASSES[name](config)
