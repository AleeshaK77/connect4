# --- Search Configuration ---
MAX_DEPTH = 42                # Total slots on a Connect 4 board
DEFAULT_TIME_LIMIT = 2.0      # Seconds
ASPIRATION_WINDOW = 50        # Used for future search optimizations

# --- Evaluation Scores ---
# Using high values for wins to ensure they outweigh any combination of threats
WIN_SCORE = 1000000
DRAW_SCORE = 0
CENTER_COLUMN_BONUS = 3
ADJACENT_COLUMN_BONUS = 1

# --- Tactical Weights ---
# These are the "knobs" the Trainer will eventually twist
THREAT_SCORE = 100            # Value of a 3-in-a-row with an open end
TWO_IN_A_ROW_SCORE = 10       # Value of a 2-in-a-row

# --- Feature Toggles ---
USE_QUIESCENCE = True
USE_ITERATIVE_DEEPENING = True
USE_SINGULAR_EXTENSION = True
USE_PROBCUT = False           # Keeping False until we implement

# --- ProbCut Parameters ---
# These usually require training to get right
PROBCUT_DEPTH_REDUCE = 3      # How many levels to skip
PROBCUT_MARGIN = 1.5          # The multiplier for the cutoff threshold

