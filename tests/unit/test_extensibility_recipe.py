"""§12.1.a end-to-end extensibility test — register a 4th algorithm via the registry only.

Demonstrates that the README "Extending it" recipe (subclass ``BaseAgent``
+ append one ``AlgorithmSpec``) actually works end-to-end through
:func:`dronerl.agent_factory.create_agent`. CI runs this on every push,
so the recipe stops being "documented" and starts being "executed".
"""

from dronerl import agent_factory, algorithms
from dronerl.algorithms import ALGORITHM_REGISTRY, AlgorithmSpec
from dronerl.base_agent import BaseAgent


class _StubSarsaAgent(BaseAgent):
    """Minimal on-policy TD agent — not a real SARSA, just a registry probe."""

    algorithm_name = "Stub-SARSA (extensibility probe)"

    def update(self, state, action, reward, next_state, done) -> None:  # noqa: D401
        # On-policy variant: pick a follow-up action via current epsilon-greedy
        # policy and use *that* Q-value as the bootstrap target.
        next_action = 0 if done else self.choose_action(next_state)
        nr, nc = next_state
        next_q = 0.0 if done else float(self.q_table[nr, nc, next_action])
        target = reward + self.gamma * next_q
        r, c = state
        self.q_table[r, c, action] += 0.1 * (target - self.q_table[r, c, action])


def test_new_algorithm_registers_via_registry_only(ui_config, monkeypatch):
    """Adding a new ``AlgorithmSpec`` line is genuinely sufficient."""
    new_spec = AlgorithmSpec("stub_sarsa", "Stub SARSA", "#9b59b6", _StubSarsaAgent)
    extended_registry = ALGORITHM_REGISTRY + (new_spec,)
    extended_classes = {spec.name: spec.agent_class for spec in extended_registry}
    extended_names = tuple(spec.name for spec in extended_registry)

    monkeypatch.setattr(algorithms, "ALGORITHM_REGISTRY", extended_registry)
    monkeypatch.setattr(algorithms, "AGENT_CLASSES", extended_classes)
    monkeypatch.setattr(algorithms, "ALGORITHMS", extended_names)
    monkeypatch.setattr(agent_factory, "AGENT_CLASSES", extended_classes)
    monkeypatch.setattr(agent_factory, "ALGORITHMS", extended_names)

    cfg = ui_config
    cfg.algorithm.name = "stub_sarsa"
    agent = agent_factory.create_agent(cfg)

    assert isinstance(agent, _StubSarsaAgent)
    assert agent.q_table.shape == (cfg.environment.grid_rows, cfg.environment.grid_cols, 4)


def test_unknown_algorithm_after_registry_extension_still_rejects(ui_config, monkeypatch):
    """The factory's validation layer is not bypassed by the extension probe."""
    monkeypatch.setattr(agent_factory, "ALGORITHMS", ("bellman", "q_learning", "double_q"))
    monkeypatch.setattr(agent_factory, "AGENT_CLASSES", {"bellman": _StubSarsaAgent,
                                                         "q_learning": _StubSarsaAgent,
                                                         "double_q": _StubSarsaAgent})
    ui_config.algorithm.name = "totally_invented_name"
    try:
        agent_factory.create_agent(ui_config)
    except ValueError as exc:
        assert "Unknown algorithm" in str(exc)
    else:
        raise AssertionError("create_agent accepted an unregistered algorithm name")
