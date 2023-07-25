from copy import deepcopy
import timeit
from node_bb import GomokuBoard
from trans_table import TranspositionTable

# negamax with alpha-beta pruning and transposition table
# returns the best move and the score of the best move
# node is the current node
# depth is the depth of the search
# tt is the transposition table


def negamax(node: 'GomokuBoard', depth, alpha, beta, tt):
    global node_explored, tt_hit
    node_explored += 1
    alpha_orig = alpha
    tt_entry = tt[node.get_hash()]
    if tt_entry is not None and tt_entry[0] >= depth-1:
        tt_hit += 1
        if tt_entry[1] == 'exact':
            return tt_entry[2], tt_entry[3]
        elif tt_entry[1] == 'lowerbound':
            alpha = max(alpha, tt_entry[2])
        elif tt_entry[1] == 'upperbound':
            beta = min(beta, tt_entry[2])
        if alpha >= beta:
            return tt_entry[2], tt_entry[3]
    if node.is_win_around_move():
        return -1, None
    if depth == 0:
        return 0, None
    legal_moves = node.get_legal_moves_in_relevant_area()
    if legal_moves == []:
        return 0, None
    best_score = -1
    best_move = legal_moves[0]
    for move in legal_moves:
        child_node = deepcopy(node)
        child_node.make_move(move)
        score, _ = negamax(child_node, depth-1, -beta, -alpha, tt)
        score = -score
        if score > best_score:
            best_score = score
            best_move = move
        alpha = max(alpha, best_score)
        if alpha >= beta:
            break
    if best_score <= alpha_orig:
        tt_entry = (depth, 'upperbound', best_score, best_move)
    elif best_score >= beta:
        tt_entry = (depth, 'lowerbound', best_score, best_move)
    else:
        tt_entry = (depth, 'exact', best_score, best_move)
    tt[node.get_hash()] = tt_entry
    return best_score, best_move

# iterative deepening negamax with alpha-beta pruning and transposition table


def negamax_iterative_deepening(node, depth, alpha, beta, tt):
    best_score = -1
    best_move = None
    for i in range(1, depth+1):
        global node_explored, tt_hit
        best_score, best_move = negamax(node, i, alpha, beta, tt)
        print(f'depth: {i} score: {best_score} move: {best_move}')
        print(f'Node explored: {node_explored}, TT hit: {tt_hit}')
        if best_score == 1:
            break
    return best_score, best_move


if __name__ == '__main__':
    board_size = 5
    win_length = 5
    game = GomokuBoard()
    tt = TranspositionTable()
    node_explored = 0
    tt_hit = 0
    i = 0
    while not game.is_win_around_move():
        i += 1
        #calculate time taken
        time=timeit.timeit(lambda: negamax(game, 11-i, -1, 1, tt), number=1)
        print(f'Time taken: {time}')
        print(f'Node explored: {node_explored}, TT hit: {tt_hit}')
        best_score, best_move = negamax(game, 11-i, -1, 1, tt)
        if (best_move is None):
            break
        game.make_move(best_move)
        game.print_board()
