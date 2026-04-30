"""Training orchestration for DroneRL."""


from dronerl.base_agent import BaseAgent
from dronerl.config_loader import Config
from dronerl.environment import Environment


class Trainer:
    """Drives the training loop for one (agent, environment) pair and tracks metrics.

    Input:  ``agent`` (BaseAgent), ``environment`` (Environment) at construction;
            no per-call inputs to ``run_episode`` / ``run_step`` — the env owns the state.
    Output: per-episode reward and step counts on ``reward_history`` / ``steps_history``;
            ``get_metrics()`` returns a snapshot dict (mean reward, goal-rate, episode count).
    Setup:  Config — uses ``training.max_steps_per_episode`` to cap each episode.
    """

    def __init__(self, agent: BaseAgent, environment: Environment, config: Config):
        self.agent = agent
        self.env = environment
        self.max_steps = config.training.max_steps_per_episode
        self.on_episode_start = None

        self._episode_count = 0
        self._goal_count = 0
        self._reward_history: list[float] = []
        self._steps_history: list[int] = []

    @property
    def episode_count(self) -> int:
        """Number of episodes that have been run through ``run_episode``."""
        return self._episode_count

    @property
    def goal_rate(self) -> float:
        """Fraction of episodes that ended at the goal (0.0 if no episodes yet)."""
        if self._episode_count == 0:
            return 0.0
        return self._goal_count / self._episode_count

    @property
    def reward_history(self) -> list[float]:
        """Total reward per episode in chronological order."""
        return self._reward_history

    @property
    def steps_history(self) -> list[int]:
        """Number of environment steps each episode took, in chronological order."""
        return self._steps_history

    def run_episode(self) -> tuple[float, int, bool]:
        """Run a single training episode.

        Returns:
            Tuple of (total_reward, steps_taken, reached_goal).
        """
        if self.on_episode_start is not None:
            self.on_episode_start()
        state = self.env.reset()
        total_reward = 0.0
        reached_goal = False

        for step in range(1, self.max_steps + 1):  # noqa: B007
            action = self.agent.choose_action(state)
            next_state, reward, done, info = self.env.step(action)

            self.agent.update(state, action, reward, next_state, done)

            total_reward += reward
            state = next_state

            if done:
                reached_goal = info.get("event") == "goal"
                break

        self.agent.decay_epsilon()
        self._episode_count += 1
        if reached_goal:
            self._goal_count += 1
        self._reward_history.append(total_reward)
        self._steps_history.append(step)

        return total_reward, step, reached_goal

    def get_metrics(self) -> dict:
        """Return a dictionary of current training metrics."""
        recent = self._reward_history[-100:] if self._reward_history else []
        return {
            "episode_count": self._episode_count,
            "goal_rate": self.goal_rate,
            "total_goals": self._goal_count,
            "epsilon": self.agent.epsilon,
            "avg_reward": sum(recent) / len(recent) if recent else 0.0,
            "last_reward": self._reward_history[-1] if self._reward_history else 0.0,
            "avg_steps": (
                sum(self._steps_history[-100:]) / len(self._steps_history[-100:])
                if self._steps_history
                else 0.0
            ),
        }
