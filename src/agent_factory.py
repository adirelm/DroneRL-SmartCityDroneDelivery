"""Factory for creating RL agents based on config.algorithm.name."""

from src.agent import BellmanAgent
from src.base_agent import BaseAgent
from src.config_loader import Config
from src.double_q_agent import DoubleQAgent
from src.q_agent import QLearningAgent

_AGENTS: dict[str, type[BaseAgent]] = {
    "bellman": BellmanAgent,
    "q_learning": QLearningAgent,
    "double_q": DoubleQAgent,
}


def create_agent(config: Config) -> BaseAgent:
    """Create the agent specified by `config.algorithm.name`."""
    name = config.algorithm.name
    if name not in _AGENTS:
        valid = ", ".join(sorted(_AGENTS))
        raise ValueError(f"Unknown algorithm: '{name}'. Valid: {valid}")
    return _AGENTS[name](config)
