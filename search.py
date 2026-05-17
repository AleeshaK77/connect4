import time
import constants as c #type: ignore
from evaluator import Evaluator

class Search:
    def __init__(self, board):
        self.board = board
        self.evaluator = Evaluator()
        self.nodes_visited = 0
        self.start_time = 0
        self.time_limit = 0
        self.out_of_time = False

        self.settings = {
            "use_quiescence": c.USE_QUIESCENCE,
            "use_iterative_deepening": c.USE_ITERATIVE_DEEPENING,
            "use_singular_extension": c.USE_SINGULAR_EXTENSION,
            "use_probcut": c.USE_PROBCUT
        }

    def get_best_move(self, depth_limit=c.MAX_DEPTH, time_limit=c.DEFAULT_TIME_LIMIT):
        self.out_of_time = False
        self.start_time = time.time()
        self.time_limit = time_limit
        
        if self.settings["use_iterative_deepening"]:
            return self._iterative_deepening(depth_limit)
        return self._fixed_depth_search(depth_limit)

    def _fixed_depth_search(self, depth):
        self.nodes_visited = 0
        move = self._get_best_move_at_depth(depth)
        return move, self.nodes_visited

    def _iterative_deepening(self, max_depth):
        best_move_so_far = None
        total_nodes = 0
        for current_depth in range(1, max_depth + 1):
            if self._check_time(): break
            self.nodes_visited = 0
            move = self._get_best_move_at_depth(current_depth)
            if not self.out_of_time:
                best_move_so_far = move
                total_nodes += self.nodes_visited
            else:
                break
        return best_move_so_far, total_nodes

    def _get_best_move_at_depth(self, depth):
        best_score = -float('inf')
        best_move = None
        for move in self.board.get_ordered_moves():
            self.board.make_move(move)
            score = -self.alpha_beta(depth - 1, -float('inf'), float('inf'))
            self.board.undo_move(move)
            
            if self.out_of_time: return best_move
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def alpha_beta(self, depth, alpha, beta):
        """Pure Negamax: Score is always relative to the current mover."""
        if (self.nodes_visited & 1023 == 0) and self._check_time():
            return 0
        self.nodes_visited += 1
        opponent = 1 - self.board.get_current_player_id()
        if self.board.is_win(self.board.player_bits[opponent]):
            return -c.WIN_SCORE - depth

        if self.board.is_draw(): return c.DRAW_SCORE

        if depth <= 0:
            if self.settings["use_quiescence"]:
                return self.quiescence_search(alpha, beta)
            score = self.evaluator.evaluate(self.board)
            return score if self.board.get_current_player_id() == 0 else -score
        
        if self.settings.get("use_probcut"):
            if abs(beta) < (c.WIN_SCORE * 0.9): 
                v_scout = self.probcut_scout(depth, beta)
                
                if v_scout != float('inf') and v_scout >= int(beta * c.PROBCUT_MARGIN):
                    return beta
                
        extension = 0
        if self.settings["use_singular_extension"] and not self.evaluator.is_quiescent(self.board):
            extension = 1

        value = -float('inf')
        for move in self.board.get_ordered_moves():
            self.board.make_move(move)
            score = -self.alpha_beta(depth - 1 + extension, -beta, -alpha)
            self.board.undo_move(move)
            
            value = max(value, score)
            alpha = max(alpha, value)
            if alpha >= beta: break
        return value

    def quiescence_search(self, alpha, beta, q_depth=0):
        self.nodes_visited += 1
        if q_depth > 10: 
            score = self.evaluator.evaluate(self.board)
            return score if self.board.get_current_player_id() == 0 else -score

        static_eval = self.evaluator.evaluate(self.board)
        score = static_eval if self.board.get_current_player_id() == 0 else -static_eval
        
        if score >= beta: return beta
        if alpha < score: alpha = score

        if not self.evaluator.is_quiescent(self.board):
            for move in self.board.get_ordered_moves():
                self.board.make_move(move)
                if self.board.is_win(self.board.player_bits[(self.board.counter - 1) % 2]):
                    move_score = c.WIN_SCORE + (10 - q_depth)
                    self.board.undo_move(move)
                    if move_score >= beta: return beta
                    if move_score > alpha: alpha = move_score
                    continue
                
                res_score = -self.quiescence_search(-beta, -alpha, q_depth + 1)
                self.board.undo_move(move)
                if res_score >= beta: return beta
                if res_score > alpha: alpha = res_score
        
        return alpha
    
    def probcut_scout(self, depth, beta):
        r = c.PROBCUT_DEPTH_REDUCE
        margin_multiplier = c.PROBCUT_MARGIN 
        
        if depth < r + 1:
            return -float('inf') 

        threshold = int(beta * c.PROBCUT_MARGIN)
        if threshold >= c.WIN_SCORE:
            return -float('inf') 
        
        return -self.alpha_beta(depth - 1 - r, -(threshold + 1), -threshold)

    def _check_time(self):
        if time.time() - self.start_time > self.time_limit:
            self.out_of_time = True
            return True
        return False