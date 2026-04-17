# PRD -- Q-Learning Algorithm for DroneRL

## 1. Algorithm Description

DroneRL uses **Tabular Q-Learning**, an off-policy, model-free
reinforcement learning algorithm. The agent learns an action-value
function Q(s, a) that estimates the expected cumulative reward for
taking action _a_ in state _s_ and then following the optimal policy.

Key properties:

- **Off-policy**: The agent learns the optimal policy (greedy over Q)
  while exploring with a different behavior policy (epsilon-greedy).
- **Model-free**: No transition model P(s'|s,a) is needed; the agent
  learns purely from sampled (state, action, reward, next_state) tuples.
- **Tabular**: Q-values are stored in a lookup table (NumPy array)
  rather than approximated by a neural network. This is feasible because
  the state space is small and discrete.

## 2. Mathematical Formulation

### Bellman Optimality Update (Q-Learning Rule)

```
Q(s, a) <-- Q(s, a) + alpha * [ r + gamma * max_a' Q(s', a') - Q(s, a) ]
```

Where:

| Symbol | Meaning | Value |
|--------|---------|-------|
| `Q(s, a)` | Current Q-value for state s, action a | Stored in Q-table |
| `alpha` | Learning rate | 0.1 |
| `r` | Immediate reward | Depends on cell type |
| `gamma` | Discount factor | 0.95 |
| `max_a' Q(s', a')` | Best Q-value achievable from the next state | Looked up in Q-table |
| `s'` | Next state after taking action a in state s | From environment step |

On terminal states (goal reached or trap hit), the future value term is
zero:

```
Q(s, a) <-- Q(s, a) + alpha * [ r - Q(s, a) ]
```

### Implementation Reference (`agent.py`, lines 46-58)

```python
current_q = self.q_table[state[0], state[1], action]
next_max_q = 0.0 if done else self.get_max_q(next_state)
target = reward + self.gamma * next_max_q
self.q_table[state[0], state[1], action] += self.lr * (target - current_q)
```

## 3. State Space

| Property | Value |
|----------|-------|
| Representation | `(row, col)` tuple of discrete grid coordinates |
| Dimensions | `grid_rows x grid_cols` (default: 12 x 12 = 144 states) |
| Start state | `(0, 0)` -- top-left corner |
| Goal state | `(11, 11)` -- bottom-right corner |

Each state corresponds to a cell in the grid. The agent's position is
always one of the 144 discrete cells.

## 4. Action Space

| Index | Action | Delta (row, col) |
|-------|--------|-------------------|
| 0 | UP | (-1, 0) |
| 1 | DOWN | (+1, 0) |
| 2 | LEFT | (0, -1) |
| 3 | RIGHT | (0, +1) |

Four deterministic movement actions. In wind zones, the action may be
randomly overridden with probability `drift_probability = 0.3`.

## 5. Q-Table Structure

```
Shape: [rows x cols x num_actions] = [12 x 12 x 4]
Type:  numpy.ndarray, dtype=float64
Init:  All zeros
```

- **Axis 0**: Grid row (0..11)
- **Axis 1**: Grid column (0..11)
- **Axis 2**: Action index (0=UP, 1=DOWN, 2=LEFT, 3=RIGHT)

Total entries: 12 x 12 x 4 = **576 Q-values**.

The Q-table can be saved to and loaded from `.npy` files for persistence
(`agent.save()` / `agent.load()`).

## 6. Exploration Strategy

### Epsilon-Greedy with Exponential Decay

```
With probability epsilon:   choose random action   (explore)
With probability 1-epsilon: choose argmax Q(s, .)  (exploit)
```

After each episode, epsilon is decayed:

```
epsilon <-- max(epsilon_end, epsilon * epsilon_decay)
```

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `epsilon_start` | 1.0 | Begin with 100% random exploration |
| `epsilon_end` | 0.01 | Minimum exploration rate (never fully greedy) |
| `epsilon_decay` | 0.995 | Multiplicative decay per episode |

### Decay Trajectory

| Episode | Approximate Epsilon |
|---------|-------------------|
| 0 | 1.000 |
| 100 | 0.606 |
| 200 | 0.368 |
| 300 | 0.223 |
| 400 | 0.135 |
| 500 | 0.082 |
| 600 | 0.050 |
| 700 | 0.030 |
| 920+ | 0.010 (floor) |

Epsilon drops below 0.05 around episode ~600, which is when convergence
checks become eligible.

## 7. Hyperparameters

All hyperparameters are defined in `config/config.yaml` under the
`agent` and `training` sections.

### Agent Hyperparameters

| Parameter | Config Key | Default | Rationale |
|-----------|-----------|---------|-----------|
| Learning rate | `agent.learning_rate` | 0.1 | Standard value; balances speed vs. stability for tabular methods |
| Discount factor | `agent.discount_factor` | 0.95 | High enough to value future rewards (reaching the goal) but not so high as to slow convergence |
| Epsilon start | `agent.epsilon_start` | 1.0 | Full exploration initially to discover the state space |
| Epsilon end | `agent.epsilon_end` | 0.01 | Small residual exploration to handle stochastic wind zones |
| Epsilon decay | `agent.epsilon_decay` | 0.995 | Smooth exponential decay; reaches exploitable range by ~600 episodes |

### Training Hyperparameters

| Parameter | Config Key | Default | Rationale |
|-----------|-----------|---------|-----------|
| Max episodes | `training.max_episodes` | 5000 | Upper bound; convergence typically occurs well before this |
| Max steps per episode | `training.max_steps_per_episode` | 200 | Prevents infinite loops; optimal path in 12x12 grid is ~22 steps |
| Convergence window | `training.convergence_window` | 100 | Rolling window for goal-rate calculation |
| Convergence rate | `training.convergence_rate` | 0.95 | 95% of recent episodes must reach the goal |
| Min episodes before converge | `training.min_episodes_before_converge` | 200 | Prevents false positives from early lucky streaks |
| Max epsilon for converge | `training.max_epsilon_for_converge` | 0.05 | Ensures the agent is mostly exploiting when convergence is declared |

## 8. Convergence Criteria

The agent is considered converged when **all** of the following
conditions are met simultaneously:

1. **Minimum episodes**: At least 200 episodes have been completed.
2. **Low epsilon**: `epsilon < 0.05` (agent is predominantly exploiting).
3. **High goal rate**: At least 95% of the last 100 episodes ended by
   reaching the goal (positive total reward as a proxy).

### Implementation (`game_logic.py`)

```python
def check_convergence(self) -> bool:
    if self.episode < self.min_episodes:
        return False
    if self.agent.epsilon > self.max_eps_converge:
        return False
    recent_goals = sum(1 for r in self.reward_history[-w:] if r > 0)
    if recent_goals / w >= self.converge_rate:
        self.converged = True
        return True
    return False
```

When convergence is detected, the GUI auto-pauses and enables the
heatmap and arrow overlays so the user can inspect the learned policy.

## 9. Reward Shaping Rationale

| Event | Reward | Rationale |
|-------|--------|-----------|
| Step (empty cell) | -1 | Small penalty encourages the agent to find the shortest path rather than wandering |
| Goal reached | +100 | Large positive reward creates a strong gradient back through the Q-table toward the start |
| Trap hit (terminal) | -50 | Severe penalty teaches the agent to avoid traps; terminal to prevent lingering |
| Wind zone step | -2 | Slightly worse than empty cells; discourages wind zones when a safer path exists, but does not make them catastrophic |
| Wall / building collision | -5 | Moderate penalty; agent stays in place but learns not to walk into walls or buildings |

### Design Rationale

- **Goal >> |Trap|**: The goal reward (+100) is much larger than the trap
  penalty magnitude (50) to ensure the agent is motivated to reach the
  goal even when traps are nearby.
- **Step penalty is small but negative**: Without it, the agent has no
  incentive to prefer shorter paths. With it, every extra step costs
  utility, naturally selecting for efficiency.
- **Wind penalty between step and wall**: Wind zones are traversable
  (not terminal) but risky due to random drift. The -2 penalty makes
  them mildly aversive -- the agent learns to route around them when
  a building-free alternative exists.
- **Wall collision is non-terminal**: The agent does not "die" from
  hitting a wall; it simply wastes a step and receives -5. This lets
  it learn wall boundaries without restarting the episode.

## 10. Success Metrics

| Metric | Target | Typical Observed |
|--------|--------|-----------------|
| Convergence episode | < 1000 | ~600 episodes on default 12x12 grid |
| Goal rate (last 100 episodes) | >= 95% | 97-100% after convergence |
| Optimal path length | ~22 steps (Manhattan distance) | 22-26 steps depending on obstacles |
| Training time (fast mode, 100 eps/frame) | < 30 seconds | ~10-15 seconds on modern hardware |

On the default 12x12 grid with no obstacles, the Manhattan distance
from (0,0) to (11,11) is 22 steps. The agent typically learns a
near-optimal path within approximately 600 episodes. With obstacles,
wind zones, and traps, convergence may take longer but generally stays
well under 1000 episodes.
