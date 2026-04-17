"""Training, convergence detection, and demo logic for DroneRL."""

from src.base_agent import BaseAgent
from src.config_loader import Config
from src.environment import Environment


class GameLogic:
    """Manages training steps, convergence, and demo playback."""

    def __init__(self, agent: BaseAgent, env: Environment, config: Config):
        self.agent = agent
        self.env = env
        t = config.training
        self.max_steps = t.max_steps_per_episode
        self.converge_window = t.convergence_window
        self.converge_rate = t.convergence_rate
        self.min_episodes = t.min_episodes_before_converge
        self.max_eps_converge = t.max_epsilon_for_converge
        self.demo_speed = config.gui.demo_speed

        self.episode = 0
        self.steps = 0
        self.total_reward = 0.0
        self.goals_reached = 0
        self.reward_history = []

        self.demo_mode = False
        self.demo_timer = 0
        self.demo_pause = 0
        self.demo_last_reward = 0.0
        self.demo_trail = []  # path trail for demo visualization
        self.converged = False
        self.state = self.env.reset()

    @property
    def goal_rate(self) -> float:
        """Return goal-reach percentage over all episodes."""
        return (self.goals_reached / max(self.episode, 1)) * 100

    def training_step(self) -> None:
        """Run one step of training."""
        action = self.agent.choose_action(self.state)
        next_state, reward, done, info = self.env.step(action)
        self.agent.update(self.state, action, reward, next_state, done)
        self.state = next_state
        self.steps += 1
        self.total_reward += reward
        if done or self.steps >= self.max_steps:
            if info.get("event") == "goal":
                self.goals_reached += 1
            self.reward_history.append(self.total_reward)
            self.agent.decay_epsilon()
            self.episode += 1
            self.total_reward, self.steps = 0.0, 0
            self.state = self.env.reset()

    def check_convergence(self) -> bool:
        """Return True once if agent consistently reaches the goal."""
        if self.converged:
            return False
        if self.episode < self.min_episodes:
            return False
        if self.agent.epsilon > self.max_eps_converge:
            return False
        w = self.converge_window
        recent_goals = sum(
            1 for r in self.reward_history[-w:] if r > 0
        )
        if recent_goals / w >= self.converge_rate:
            self.converged = True
            return True
        return False

    def enter_demo(self) -> None:
        """Switch to demo mode."""
        self.demo_mode = True
        self.state = self.env.reset()
        self.steps = 0
        self.total_reward = 0.0
        self.demo_trail = [self.state]

    def exit_demo(self) -> None:
        """Exit demo mode."""
        self.demo_mode = False

    def demo_step(self, fps: int) -> None:
        """In demo mode, follow greedy policy one visible step at a time."""
        # Pause at goal — drone stays on the goal visually
        if self.demo_pause > 0:
            self.demo_pause -= 1
            if self.demo_pause == 0:
                self.state = self.env.reset()
                self.steps = 0
                self.total_reward = 0.0
                self.demo_trail = [self.state]
            return
        self.demo_timer += 1
        frames_per_step = max(1, fps // self.demo_speed)
        if self.demo_timer < frames_per_step:
            return
        self.demo_timer = 0
        action = self.agent.get_best_action(self.state)
        next_state, reward, done, _ = self.env.step(action)
        self.state = next_state
        self.demo_trail.append(self.state)
        self.steps += 1
        self.total_reward += reward
        if done or self.steps >= self.max_steps:
            self.demo_last_reward = self.total_reward
            self.demo_pause = fps * 3  # stay on goal 3 seconds

    def reset(self, agent: BaseAgent, env: Environment) -> None:
        """Hard reset all state."""
        self.agent = agent
        self.env = env
        self.episode = self.steps = self.goals_reached = 0
        self.total_reward = 0.0
        self.reward_history.clear()
        self.demo_mode = False
        self.converged = False
        self.state = self.env.reset()

    def get_metrics(self) -> dict:
        """Return current metrics for the dashboard."""
        if self.demo_mode and self.demo_pause > 0:
            display_reward = self.demo_last_reward
        else:
            display_reward = self.total_reward
        return {
            "episode": self.episode,
            "total_reward": display_reward,
            "epsilon": self.agent.epsilon,
            "steps": self.steps,
            "goal_rate": self.goal_rate,
        }
