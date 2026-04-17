"""Tests for GUI-side training orchestration."""


from src.agent import Agent
from src.environment import Environment


def test_training_step_tracks_goal_episode_and_reset(ui_logic, monkeypatch):
    ui_logic.state = (10, 11)
    ui_logic.env.drone_pos = (10, 11)
    monkeypatch.setattr(ui_logic.agent, "choose_action", lambda state: 1)

    ui_logic.training_step()

    assert ui_logic.episode == 1
    assert ui_logic.goals_reached == 1
    assert ui_logic.reward_history == [100.0]
    assert ui_logic.steps == 0
    assert ui_logic.state == ui_logic.env.start


def test_training_step_resets_when_max_steps_reached(ui_logic, monkeypatch):
    ui_logic.max_steps = 1
    monkeypatch.setattr(ui_logic.agent, "choose_action", lambda state: 3)

    ui_logic.training_step()

    assert ui_logic.episode == 1
    assert ui_logic.reward_history == [-1.0]
    assert ui_logic.steps == 0


def test_check_convergence_covers_guard_clauses_and_success(ui_logic):
    assert ui_logic.check_convergence() is False

    ui_logic.episode = ui_logic.min_episodes
    ui_logic.agent.epsilon = ui_logic.max_eps_converge + 0.01
    assert ui_logic.check_convergence() is False

    ui_logic.agent.epsilon = ui_logic.max_eps_converge
    ui_logic.goal_history = [True] * ui_logic.converge_window
    assert ui_logic.check_convergence() is True
    assert ui_logic.converged is True
    assert ui_logic.check_convergence() is False


def test_demo_mode_progress_pause_and_metrics(ui_logic, monkeypatch):
    ui_logic.enter_demo()
    assert ui_logic.demo_mode is True
    assert ui_logic.demo_trail == [ui_logic.env.start]

    ui_logic.state = (10, 11)
    ui_logic.env.drone_pos = (10, 11)
    monkeypatch.setattr(ui_logic.agent, "get_best_action", lambda state: 1)

    ui_logic.demo_step(fps=8)
    assert ui_logic.demo_pause == 24
    assert ui_logic.demo_last_reward == 100.0
    assert ui_logic.get_metrics()["total_reward"] == 100.0

    ui_logic.demo_pause = 1
    ui_logic.demo_step(fps=8)
    assert ui_logic.state == ui_logic.env.start
    assert ui_logic.demo_trail == [ui_logic.env.start]


def test_demo_step_waits_for_frame_budget(ui_logic, monkeypatch):
    ui_logic.enter_demo()
    ui_logic.demo_speed = 2
    monkeypatch.setattr(ui_logic.agent, "get_best_action", lambda state: 3)

    ui_logic.demo_step(fps=8)

    assert ui_logic.demo_timer == 1
    assert ui_logic.steps == 0


def test_exit_demo_and_reset_clear_runtime_state(ui_logic, ui_config):
    ui_logic.demo_mode = True
    ui_logic.converged = True
    ui_logic.reward_history.extend([1.0, 2.0])
    ui_logic.episode = 4
    ui_logic.steps = 3
    ui_logic.goals_reached = 2

    ui_logic.exit_demo()
    assert ui_logic.demo_mode is False

    new_agent = Agent(ui_config)
    new_env = Environment(ui_config)
    ui_logic.reset(new_agent, new_env)

    assert ui_logic.agent is new_agent
    assert ui_logic.env is new_env
    assert ui_logic.episode == 0
    assert ui_logic.steps == 0
    assert ui_logic.goals_reached == 0
    assert ui_logic.reward_history == []
    assert ui_logic.converged is False
