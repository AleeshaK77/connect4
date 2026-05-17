import constants as c # type: ignore

class Evaluator:
    def __init__(self):
        pass

    def evaluate(self, board):
        player_1 = board.player_bits[0]
        player_2 = board.player_bits[1]

        if board.is_win(player_1): return c.WIN_SCORE #terminal wins
        if board.is_win(player_2): return -c.WIN_SCORE

        score = 0
        score += self.get_positional_score(player_1, player_2) #tie-breakers
        score += self.count_all_patterns(player_1, player_2)
        
        return score

    def get_positional_score(self, player_1, player_2):
        """Scores based on piece placement (Center is better)."""
        #column masks for a standard 6x7 bitboard
        center_mask = 0x1F80     #column 3        
        adjacency_mask = 0x3F03F       #columns 2 and 4
        
        player_1_center = bin(player_1 & center_mask).count('1')
        player_2_center = bin(player_2 & center_mask).count('1')
        player_1_adjacent = bin(player_1 & adjacency_mask).count('1')
        player_2_adjacent = bin(player_2 & adjacency_mask).count('1')
        
        return (player_1_center - player_2_center) * c.CENTER_COLUMN_BONUS + \
               (player_1_adjacent - player_2_adjacent) * c.ADJACENT_COLUMN_BONUS

    def count_all_patterns(self, player_1, player_2):
        empty = ~(player_1 | player_2)
        player_1_score = self.calculate_player_potential(player_1, empty)
        player_2_score = self.calculate_player_potential(player_2, empty)

        player_1_forks = self.detect_forks(player_1, empty) #check for forks: multiple threats created by same player
        player_2_forks = self.detect_forks(player_2, empty)

        return (player_1_score - player_2_score) + (player_1_forks - player_2_forks) * 500
    
    def detect_forks(self, p, empty):
        """Counts squares where the player has a winning threat."""
        threat_map = 0
        directions = [1, 7, 8, 6]
        
        for d in directions:
            #square is a threat if it completes 4-in-a-row
            #pattern: [P, P, P, E] or [P, E, P, P] etc.
            threat_map |= (p & (p << d) & (p << 2*d)) << d & empty
            threat_map |= (p & (p >> d) & (p >> 2*d)) >> d & empty
        
        return bin(threat_map).count('1') #if threat map has more than one bit set in a way the opponent cannot block both, then fork

    def calculate_player_potential(self, p, empty):
        """
        Uses bit-shifting to find groups of 3 or 2 that can actually be completed.
        """
        score = 0
        directions = [1, 7, 8, 6] #vertical, horizontal, diagonals
        
        for d in directions:
            # finding 3-in-a-row: 3 pieces + 1 empty space in line
            threes = (p & (p << d) & (p << 2*d)) & (empty << 3*d)
            score += bin(threes).count('1') * c.THREAT_SCORE
            
            #finding 2-in-a-row
            twos = (p & (p << d)) & (empty << 2*d) & (empty << 3*d)
            score += bin(twos).count('1') * c.TWO_IN_A_ROW_SCORE
            
        return score
    
    def is_quiescent(self, board):
        """Returns True if no player has an immediate winning move."""
        for move in board.get_legal_moves():
            board.make_move(move)
            if board.is_win(board.player_bits[(board.counter - 1) % 2]): #
                board.undo_move(move)
                return False
            board.undo_move(move)
        return True