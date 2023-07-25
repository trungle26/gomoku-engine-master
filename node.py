from copy import deepcopy
from eva import EVA
from trans_table import TranspositionTable


DIRECTION = {'east': (0, 1),
             'northeast': (-1, 1),
             'north': (-1, 0),
             'northwest': (-1, -1)
             }


class Node:
    def __init__(self, size=15, win_length=5):
        self.size = size
        self.win_length = win_length
        self.board = [[None for _ in range(size)] for _ in range(size)]
        self.last_move = None
        self.current_player = 'X'
        # threat for each player
        self.threats = {'X': {}, 'O': {}}
        # candidate moves
        self.candidate_moves = set()
        self.candidate_moves.add((size//2, size//2))

    def __eq__(self, __value: object) -> bool:
        return isinstance(__value, Node) and self.board == __value.board

    def __hash__(self) -> int:
        return hash(str(self.board))
    
    def make_temp_move(self, row, col):
        self.board[row][col] = self.current_player
        r_hash = self.__hash__()
        self.board[row][col] = None
        return r_hash

    def get_legal_moves(self):
        # legal_moves = []
        # for i in range(self.relv_area.x1, self.relv_area.x2+1):
        #     for j in range(self.relv_area.y1, self.relv_area.y2+1):
        #         if self.board[i][j] is None:
        #             legal_moves.append((i, j))
        # return legal_moves
        return list(self.candidate_moves)

    # expand candidate moves
    def expand_candidate_moves(self, row, col):
        for direction in DIRECTION.values():
            # expand 2 steps in each direction both ways
            for i in range(-2, 3):
                for j in range(-2, 3):
                    if i == 0 and j == 0:
                        continue
                    r = row + i*direction[0]
                    c = col + j*direction[1]
                    # check if in range
                    if r >= 0 and r < self.size and c >= 0 and c < self.size:
                        # check if empty
                        if self.board[r][c] is None:
                            self.candidate_moves.add((r, c))
        # remove the previous move
        if self.last_move is not None:
            if self.last_move in self.candidate_moves:
                self.candidate_moves.remove(self.last_move)

    def make_move(self, row, col,tb_cache,cm_cache):
        tb_cache.set(self.__hash__(), self.threats)
        cm_cache.set(self.__hash__(), self.candidate_moves)
        self.board[row][col] = self.current_player
        self.last_move = (row, col)
        # self.relv_area.expand(row, col)
        moves_entry = cm_cache.get(self.__hash__())
        if moves_entry is not None:
            self.candidate_moves = moves_entry
        else:
            self.candidate_moves = deepcopy(self.candidate_moves)
            self.expand_candidate_moves(row, col)
            cm_cache.set(self.__hash__(), self.candidate_moves)
        threat_cache = tb_cache.get(self.__hash__())
        if threat_cache is not None:
            self.threats = threat_cache
        else:
            self.threats = deepcopy(self.threats)
            self.update_threats()
            tb_cache.set(self.__hash__(), self.threats)
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        return self

    def undo_move(self, row, col,tb_cache,cm_cache):
        self.board[row][col] = None
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self.candidate_moves = cm_cache.get(self.__hash__())
        self.threats = tb_cache.get(self.__hash__())


    def count_pieces_in_all_directions(self, row, col, player):
        threat = []
        for direction in DIRECTION.values():
            count, open_end = self.count_consecutive_pieces(
                row, col, direction, player)
            if count >= 3:
                threat.append((count, open_end))
        return threat

    # count consecutive pieces include broken line and open end in a direction both ways
    def count_consecutive_pieces(self, row, col, direction, player):
        count = 1
        open_end = 0
        for i in range(1, self.win_length):
            if row + i*direction[0] < 0 or row + i*direction[0] >= self.size or col + i*direction[1] < 0 or col + i*direction[1] >= self.size:
                break
            if self.board[row + i*direction[0]][col + i*direction[1]] == player:
                count += 1
            elif self.board[row + i*direction[0]][col + i*direction[1]] is None:
                open_end += 1
                break
            else:
                break
        for i in range(1, self.win_length):
            if row - i*direction[0] < 0 or row - i*direction[0] >= self.size or col - i*direction[1] < 0 or col - i*direction[1] >= self.size:
                break
            if self.board[row - i*direction[0]][col - i*direction[1]] == player:
                count += 1
            elif self.board[row - i*direction[0]][col - i*direction[1]] is None:
                open_end += 1
                break
            else:
                break
        if count >= self.win_length:
            return self.win_length, open_end
        return count, open_end

    # update threats for each player
    def update_threats(self):
        last_move = self.last_move
        if last_move is None:
            return
        # remove last move from threats
        if last_move in self.threats[self.current_player]:
            del self.threats[self.current_player][last_move]
        # remove last move from threats for opponent
        if last_move in self.threats['O' if self.current_player == 'X' else 'X']:
            del self.threats['O' if self.current_player == 'X' else 'X'][last_move]
        # update threats for each player in all directions from last move 4 moves away both ways
        for direction in DIRECTION.values(): 
            for j in range(-4, 5):
                if j == 0:
                    continue
                r = last_move[0] + j*direction[0]
                c = last_move[1] + j*direction[1]
                # check if in range
                if r >= 0 and r < self.size and c >= 0 and c < self.size:
                    # check if empty
                    if self.board[r][c] is None:
                        threat = self.count_consecutive_pieces(
                            r, c, direction, self.current_player)
                        # if threat is not empty
                        if any(threat):
                            # add to threats for current player with key as (rol,col) and value as threat
                            if threat[0] >= 3:
                                if (r, c) not in self.threats[self.current_player]:
                                    self.threats[self.current_player][(r, c)] = {}
                                self.threats[self.current_player][(r, c)][direction] = threat
                            # add to threats for other player with key as (rol,col) and value as threat
                        other_player = 'O' if self.current_player == 'X' else 'X'
                        threat = self.count_consecutive_pieces(
                            r, c, direction, other_player)
                        if any(threat):
                            if threat[0] >= 3:
                                if (r, c) not in self.threats[other_player]:
                                    self.threats[other_player][(r, c)] = {}
                                self.threats[other_player][(r, c)][direction] = threat
    def check_win(self):
        player = 'O' if self.current_player == 'X' else 'X'
        if self.last_move is None:
            return False
        last_move = self.last_move
        for direction in DIRECTION.values():
            count, open_end = self.count_consecutive_pieces(
                last_move[0], last_move[1], direction, player)
            if count >= self.win_length:
                return True
        return False

    # print board in a human readable format, with last digit of coordinates, empty cell is -

    def print_board(self):
        print(' ', end='')
        for i in range(self.size):
            print(' '+str(i % 10), end='')
        print()
        for i in range(self.size):
            print(str(i % 10), end='')
            for j in range(self.size):
                if self.board[i][j] is None:
                    print(' -', end='')
                else:
                    print(' '+self.board[i][j], end='')
            print()

    def heuristic(self, tt: 'TranspositionTable'):
        eval = 0
        if self.check_win():
            return -10000
        tt_entry = tt.get(self.__hash__())
        if tt_entry is not None:
            return tt_entry[2]
        player = self.current_player
        for threat in self.threats[player].values():
            for i in threat.values():
                    eval+=EVA[i]*1.1
        opponent = 'O' if player == 'X' else 'X'
        for threat in self.threats[opponent].values():
            for i in threat.values():
                    eval-=EVA[i]*0.9
        return eval


# test code
if __name__ == '__main__':
    node = Node()
    tt= TranspositionTable()
    # play in terminal
    while True:
        node.print_board()
        print(node.threats)
        print(node.heuristic(tt))
        print(node.current_player, 'to play')
        move = input('enter move: ')
        if move == 'q':
            break
        move = move.split(',')
        move = [int(move[0]), int(move[1])]
        node.make_move(*move)
        if node.check_win():
            node.print_board()
            print(node.current_player, 'wins')
            break
