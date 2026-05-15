# Connect 4: Adversarial Search and Heuristic Evaluation

This project implements a bitboard-driven Connect 4 engine designed as a modular sandbox for exploring adversarial search in deterministic two-player zero-sum games. The engine exposes a configurable set of search optimisations — iterative deepening, quiescence search, singular extensions, and ProbCut — that can be independently enabled or disabled, allowing systematic comparison of how each technique affects playing strength. Users may pit configurations against one another at varying search depths and observe the resulting win rates empirically.

---

## Project Architecture

| Module | Responsibility |
| :--- | :--- |
| `board.py` | Bitboard state representation and move generation via bitwise operations |
| `evaluator.py` | Heuristic evaluation function for non-terminal states |
| `search.py` | Alpha-beta search with configurable optimisation settings |
| `main.py` | Arena entry point; defines player configurations and launches matches |

---

## Theoretical Background

### Minimax and Alpha-Beta Pruning

The theoretical foundation of this engine is the **minimax** algorithm, which computes the optimal move for a player by assuming the opponent also plays optimally. At each node, the maximising player selects the action that maximises the backed-up value, while the minimising player selects the action that minimises it. The principal liability of minimax is that the number of game states examined is exponential in the search depth — $O(b^m)$ for a tree of branching factor $b$ and depth $m$.

**Alpha-beta pruning** recovers much of this cost without altering the minimax decision. The algorithm maintains two bounds along each path through the tree:

$$\alpha = \text{the best value found so far for Max}, \qquad \beta = \text{the best value found so far for Min}.$$

When the value at a node is found to be worse than the current $\alpha$ or $\beta$ for the player at that node, the remaining branches are pruned — they cannot influence the final decision and need not be examined. The general principle, as Russell & Norvig (2010) state, is that if a player has a better option $m$ available at the parent of a node $n$, or at any ancestor, then $n$ will never be reached in actual play.

The effectiveness of pruning depends critically on move ordering. Under best-first ordering, alpha-beta examines only $O(b^{m/2})$ nodes — reducing the effective branching factor from $b$ to $\sqrt{b}$, or equivalently, doubling the search depth achievable in the same time. Under random ordering, the bound degrades to $O(b^{3m/4})$. **Iterative deepening** recovers near-optimal ordering dynamically: by completing a search at depth $d$ before beginning depth $d+1$, the best moves from the shallower search — sometimes called **killer moves** — are used to order successors in the deeper pass. On an exponential game tree, iterative deepening adds only a constant fraction to total search time, which is typically more than recovered through improved pruning.

---

### Heuristic Evaluation and Cutoff

Alpha-beta, like minimax, must in principle search to terminal states. For Connect 4 this is computationally infeasible within a reasonable time budget, so the search is cut off at a maximum depth $d$ and non-terminal leaf nodes are evaluated by a heuristic function *Eval*. This yields heuristic minimax:

$$\text{H-Minimax}(s, d) = \begin{cases} \text{Eval}(s) & \text{if } \text{Cutoff-Test}(s, d) \\ \max_{a \in \text{Actions}(s)} \text{H-Minimax}(\text{Result}(s, a), d+1) & \text{if } \text{Player}(s) = \text{Max} \\ \min_{a \in \text{Actions}(s)} \text{H-Minimax}(\text{Result}(s, a), d+1) & \text{if } \text{Player}(s) = \text{Min.} \end{cases}$$

As Russell & Norvig (2010) note, the performance of a game-playing program depends strongly on the quality of its evaluation function. A well-formed *Eval* must satisfy three properties: it must order terminal states consistently with the true utility function (wins better than draws, draws better than losses); it must be computable within a tight time budget; and for non-terminal states, it must be strongly correlated with the actual probability of winning. Because the search is cut off before the outcome is known, *Eval* is necessarily an estimate — a guess about the final outcome given bounded computation.

Most evaluation functions are realised as **weighted linear combinations** of features extracted from the state:

$$\text{Eval}(s) = \sum_{i=1}^{n} w_i f_i(s),$$

where each $f_i$ captures a strategically relevant property of the position and $w_i$ reflects its estimated importance. This formulation assumes that feature contributions are independent, an assumption that is frequently violated in practice; non-linear combinations are sometimes used to address this.

---

### Evaluation Function Design

The evaluation function in `evaluator.py` operates via a **sliding window** over all possible four-cell lines — horizontal, vertical, and both diagonals — and scores each window according to its contents. The score for a position is the sum of all window scores from the engine's perspective minus those from the opponent's perspective.

The motivation for the weight structure is that adversarial search is only as strong as the heuristic guiding it. A function that cannot distinguish a three-in-a-row requiring an immediate response from an unrelated two-in-a-row will misorder moves and cause alpha-beta to prune suboptimally. The weights are chosen to reflect a strict strategic priority ordering:

| Pattern | Strategic Interpretation | Weight |
| :--- | :--- | :---: |
| Four in a row | Terminal win | +1,000,000 |
| Three in a row (one open end) | Immediate threat; forces a response | +100 |
| Two in a row (two open ends) | Tactical setup; building toward a threat | +10 |
| Centre column occupancy | Centre control maximises the number of reachable winning lines | +3 per piece |

The ten-to-one ratio between successive threat levels is deliberate: the engine must prefer completing an existing threat over initiating a new one, and the weight gap enforces this without requiring explicit threat-detection logic. Centre column bias reflects the structural asymmetry of Connect 4 — a piece placed in column 4 participates in more potential four-cell windows than a piece placed at the edge, and is therefore unconditionally more valuable in expectation.

---

### Search Extensions and Forward Pruning

**Quiescence search** addresses the instability of evaluating non-quiescent positions at the depth cutoff. If the position at the cutoff depth contains an unresolved immediate threat, the evaluation may fluctuate wildly depending on which player moves next — an artefact of the cutoff rather than the true position value. Quiescence search extends the tree beyond the nominal depth limit until a stable position is reached, preventing the engine from making tactically unsound moves at the boundary.

**Singular extensions** mitigate the **horizon effect**, which arises when serious but ultimately unavoidable consequences are deferred just beyond the search horizon by delaying tactics. When one move is found to be significantly better than all alternatives at a given node, it is flagged as a singular move. At the depth limit, if that move is legal, the search is extended along that line. Because singular moves are rare, the additional nodes generated are few relative to the improvement in tactical accuracy.

**ProbCut** is a forward-pruning technique that extends alpha-beta by pruning nodes that are *probably* outside the current $(\alpha, \beta)$ window, rather than only those that are *provably* so. A shallow search is conducted to obtain a backed-up value $v$; prior statistics are then used to estimate the probability that a full-depth search would return a value outside the window. If that probability exceeds a threshold, the node is pruned. ProbCut trades a small risk of pruning the optimal move for a potentially large reduction in nodes examined.

---

## Configuration and Usage

Each player is defined by a settings dictionary specifying the search depth and which optimisations are active. For example:

```python
challenger = {
    "depth": 8,
    "use_iterative_deepening": True,
    "use_quiescence": True,
    "use_singular_extensions": True,
    "use_probcut": False,
}

baseline = {
    "depth": 6,
    "use_iterative_deepening": True,
    "use_quiescence": False,
    "use_singular_extensions": False,
    "use_probcut": False,
}
```

Player turns are alternated across matches to neutralise first-move advantage. Win rates, node counts, and match durations are logged by `main.py`.

```bash
python main.py
```

---

## References

Russell, S., & Norvig, P. (2010). *Artificial Intelligence: A Modern Approach* (3rd ed.). Prentice Hall.
