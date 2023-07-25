"""Gomoku game node using bitboard representation"""

from node import DIRECTION


DIRECTION = ((1, 0), (0, 1), (1, 1), (1, -1))


class Node:
    def __init__(self, board_size, win_length):
        self.board_size = board_size
        self.win_length = win_length
        #each player has a 4 bitboard for each direction(row, col, diag, anti-diag)
        self.bitboard = [[[0 for _ in range(board_size)], [0 for _ in range(board_size)], [0 for _ in range(2*board_size-1)], [0 for _ in range(2*board_size-1)]]*2]
        self.candidate_moves = []
        self.current_player = 1
        self.last_move = None
    
    def get_line(self, row, col, player, direction):
        '''get the line of the given direction
        player: 0 or 1 or 2, 2 means both players
        '''
        
        
    def check_pattern(self, line, pattern):
        '''check if the pattern is in the line'''
        pass
        
  
    def expand_candidate_moves(self, row, col):
        '''remove the move from candidate move and expand in each direction 2 squares'''
        self.candidate_moves.remove((row, col))
        for direction in DIRECTION:
            for i in range(-2, 3):
                new_row = row + i*direction[0]
                new_col = col + i*direction[1]
                if new_row >= 0 and new_row < self.board_size and new_col >= 0 and new_col < self.board_size:
                    if (new_row, new_col) not in self.candidate_moves:
                        self.candidate_moves.append((new_row, new_col))

    def make_move(self, row, col):
        self.bitboard[self.current_player][0][row] |= 1 << col
        self.bitboard[self.current_player][1][col] |= 1 << row
        self.bitboard[self.current_player][2][row+col] |= 1 << row
        self.bitboard[self.current_player][3][row-col+self.board_size-1] |= 1 << row
        self.last_move = (row, col)
        self.current_player = 1 - self.current_player
        return self
    
    def print_board(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.bitboard[0][0][row] & (1 << col):
                    print('X', end='')
                elif self.bitboard[1][0][row] & (1 << col):
                    print('O', end='')
                else:
                    print('.', end='')
            print()
    


    