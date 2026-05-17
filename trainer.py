import time
import random
import constants as c # type: ignore
from board import Board
from search import Search # type: ignore

class Trainer:
    def __init__(self):
        self.stats = {
            "challenger_wins": 0,
            "baseline_wins": 0,
            "draws": 0,
            "total_nodes": 0
        }

    def play_match(self, p1_settings, p2_settings, games=10, p1_depth = 8, p2_depth = 6):
        """
        p1: Challenger (usually with ProbCut)
        p2: Baseline (standard)
        """
        p1_wins = 0
        p2_wins = 0
        draws = 0

        for i in range(games):
            board = Board()
            players = [p1_settings, p2_settings] if i % 2 == 0 else [p2_settings, p1_settings]
            depths = [p1_depth, p2_depth] if i % 2 == 0 else [p2_depth, p1_depth]
            
            print(f"--- Game {i+1} ---")
            while not (board.is_win(board.player_bits[0]) or 
                   board.is_win(board.player_bits[1]) or 
                   board.is_draw()):
                current_idx = board.get_current_player_id()
                
                searcher = Search(board)
                searcher.settings = players[current_idx]
                
                move = searcher.get_best_move(depths[current_idx])
                board.make_move(move)

            challenger_id = i % 2
            winner = self._run_single_game(board, p1_settings, p2_settings, p1_depth, p2_depth)
            
            if winner == -1:
                self.stats["draws"] += 1
                result_text = "Draw"
            elif winner == challenger_id:
                self.stats["challenger_wins"] += 1
                result_text = "Challenger Wins"
            else:
                self.stats["baseline_wins"] += 1
                result_text = "Baseline Wins"

            print(f"Game {i+1}/{games}: {result_text}")

        self._print_summary()

    def _run_single_game(self, board, p1_config, p2_config, p1_depth, p2_depth):
        search_p1 = Search(board)
        search_p2 = Search(board)
        
        search_p1.settings.update(p1_config)
        search_p2.settings.update(p2_config)

        depths = [p1_depth, p2_depth]

        while not board.is_draw():
            current_player = board.get_current_player_id()
            engine = search_p1 if current_player == 0 else search_p2
            
            current_depth = depths[current_player]
            
            result = engine.get_best_move(depth_limit=current_depth, time_limit=0.5)
            
            if isinstance(result, tuple):
                move, nodes = result
            else:
                move, nodes = result, 0 # Fallback if only move returned
                
            self.stats["total_nodes"] += nodes
            
            if move is None: 
                move = random.choice(board.get_legal_moves())
            
            board.make_move(move)
            
            if board.is_win(board.player_bits[current_player]):
                return current_player
        
        return -1

    def _print_summary(self):
        print("\n" + "="*30)
        print("      FINAL TOURNAMENT RECAP")
        print("="*30)
        print(f"Challenger Wins: {self.stats['challenger_wins']}")
        print(f"Baseline Wins:   {self.stats['baseline_wins']}")
        print(f"Draws:           {self.stats['draws']}")
        print(f"Avg Nodes/Game:  {self.stats['total_nodes'] // sum(self.stats.values()):,}")
        print("="*30)
