#  Connect 4 Strategy Arena 

An experimental bitboard-driven Connect 4 engine designed for benchmarking and comparing modern search optimizations. This project serves as a modular sandbox for exploring **Game Theory** and **Search Optimization**, allowing you to pit different "AI Personalities" against each other.

---

##  The Intelligence: Search & Optimization

The engine solves the Connect 4 state-space using a variety of sophisticated search techniques:

### **Alpha-Beta Pruning**
Standard Minimax explores every single branch, which is computationally expensive. **Alpha-Beta Pruning** acts as our "scissors." It maintains two values: **Alpha** (the best score the maximizer is guaranteed) and **Beta** (the best score the minimizer is guaranteed). If a branch is found that is worse than the current guaranteed score, the engine stops searching it entirely—"pruning" the dead wood.



### **Iterative Deepening**
Rather than diving straight to a target depth (e.g., Depth 8), the engine searches Depth 1, then 2, then 3, and so on. This ensures that the **Transposition Table** is populated with the best moves from shallow searches, which allows Alpha-Beta to prune significantly earlier during deeper passes.

### **Singular Extensions & Quiescence**
*   **Singular Extensions:** When one move is significantly better than all alternatives, the engine "leans in" and searches that specific line deeper to avoid the "horizon effect."
*   **Quiescence Search:** The engine refuses to stop at the depth limit if the board is "noisy" (e.g., a player has an immediate threat). It continues until the position is "quiet," preventing tactical blunders.

---

##  Evaluation Function: Motivation & Logic

The evaluation function provides the AI with "intuition" when it cannot see the end of the game. It uses a **Sliding Window** approach, checking every possible 4-cell line (Horizontal, Vertical, Diagonal).

### **Pattern Weighting**
| Pattern | Strategic Motivation | Weight |
| :--- | :--- | :--- |
| `[X, X, X, X]` | **Terminal Win:** The ultimate goal. | +1,000,000 |
| `[X, X, X, .]` | **Major Threat:** Forces a response or results in a win next turn. | +100 |
| `[X, X, ., .]` | **Setup:** Building blocks for future tactical threats. | +10 |
| **Center Bias** | Control of Column 3 (the middle) is vital for maximizing win-paths. | +3 per piece |

**Why these weights?** We use **Exponential Scaling**. A 3-in-a-row is worth 10x more than a 2-in-a-row to ensure the engine prioritizes finishing a threat over starting a new one.

---

## System Architecture

The project is built on a **Modular Plugin Architecture**, decoupling the board physics from the search strategy.

### **1. The Foundation: `board.py`**
The "Physics Engine." It represents the board using **Bitboards** (64-bit integers). 
*   **Speed:** Win detection and move generation are handled via bitwise shifts, making it orders of magnitude faster than array-based boards.
*   **Purity:** This layer has no concept of "strategy"—it only knows the rules of the game.

### **2. The Brain: `search.py`**
The "Strategy Layer." It contains the recursive Alpha-Beta loop and the heuristic logic. It is **dynamically configured**; it reads a `settings` dictionary to determine which optimizations (ProbCut, Quiescence, etc.) to activate mid-search.

### **3. The Manager: `trainer.py` & `main.py`**
The "Arena Layer."
*   **Trainer:** Manages match logic, alternates player turns to neutralize the first-move advantage, and tracks performance metrics like node counts and win ratios.
*   **Main:** The user interface. This is where you define the engine "DNA" and launch the duel.

---

## Getting Started

1. **Clone the repository.**
2. **Open `main.py`** to define your `challenger` and `baseline` configurations, for example:
   ```python
   challenger = {"use_probcut": True, "use_quiescence": True}
   baseline   = {"use_probcut": False, "use_quiescence": True}
