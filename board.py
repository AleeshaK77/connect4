class Board:
    def __init__(self):
        self.player_bits = [0, 0] 
        self.heights = [0, 7, 14, 21, 28, 35, 42]
        self.counter = 0 
        
        self.TOP_ROW_MASK = 0b1000000_1000000_1000000_1000000_1000000_1000000_1000000 #mask for 7th row (buffer)

    def make_move(self, column):
        if isinstance(column, tuple):
            column = column[0]
        move_bit = 1 << self.heights[column]
        self.player_bits[self.counter & 1] ^= move_bit
        self.heights[column] += 1
        self.counter += 1

    def undo_move(self, column):
        self.counter -= 1
        self.heights[column] -= 1
        move_bit = 1 << self.heights[column]
        self.player_bits[self.counter & 1] ^= move_bit

    def is_win(self, bitboard):
        #checks for 4 in a row using bitwise shifts
        directions = [1, 7, 6, 8] #vertical, horizontal, diag \, diag /
        for d in directions:
            m = bitboard & (bitboard >> d)
            if m & (m >> (2 * d)):
                return True
        return False

    def get_legal_moves(self):
        return [c for c in range(7) if not ((1 << self.heights[c]) & self.TOP_ROW_MASK)] #returns columns where next piece wouldn't hit buffer row

    def is_draw(self):
        return self.counter == 42

    def __str__(self):
        rows = []
        for r in range(5, -1, -1): #start from top row (5) down to bottom (0)
            row_str = "|"
            for c in range(7):
                bit = 1 << (c * 7 + r)
                if self.player_bits[0] & bit:
                    row_str += " X "
                elif self.player_bits[1] & bit:
                    row_str += " O "
                else:
                    row_str += " . "
            row_str += "|"
            rows.append(row_str)
        
        footer = "  0  1  2  3  4  5  6  "
        return "\n".join(rows) + "\n" + footer

    def get_current_player_id(self):
        return self.counter & 1
    
    def get_ordered_moves(self):
        center_order = [3, 2, 4, 1, 5, 0, 6] #columns ordered by proximity to centre
        legal = self.get_legal_moves()
        return [c for c in center_order if c in legal]