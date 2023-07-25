from copy import deepcopy
import timeit

from more_itertools import last
from node import Node
from trans_table import TranspositionTable
import cProfile
import random

# negamax with alpha-beta pruning and transposition table
# returns the best move and the score of the best move
# node is the current node
# depth is the depth of the search
# tt is the transposition table

# sort helper function


def sort_helper(key, tt):
    entry = tt.get(key)
    if entry is not None:
        return entry[2]
    else:
        return 0


def negamax(node: 'Node', depth, alpha, beta, tt, tb_cache, cm_cache, process_id=0):
    global node_explored, tt_hit
    # node_explored += 1
    alpha_orig = alpha
    tt_entry = tt.get(node.__hash__())
    if tt_entry is not None and tt_entry[0] >= depth:
        # tt_hit += 1
        if tt_entry[1] == 'exact':
            return tt_entry[2], tt_entry[3]
        elif tt_entry[1] == 'lowerbound':
            alpha = max(alpha, tt_entry[2])
        elif tt_entry[1] == 'upperbound':
            beta = min(beta, tt_entry[2])
        if alpha >= beta:
            return tt_entry[2], tt_entry[3]
    if node.check_win():
        tt_entry = (depth, 'exact', -10000, None)
        tt.set(node.__hash__(), tt_entry)
        return -10000, None
    if depth == 0:
        val = node.heuristic(tt)
        tt_entry = (depth, 'exact', val, None)
        tt.set(node.__hash__(), tt_entry)
        return val, None
    legal_moves = node.get_legal_moves()
    legal_moves.sort(key=lambda move: sort_helper(
        node.make_temp_move(*move), tt))
    # move the move corresponding to the process id to the front, push the rest back
    if process_id > 0 and process_id < len(legal_moves):
        legal_moves.insert(0, legal_moves.pop(process_id))

    if legal_moves == []:
        return 0, None
    best_score = -10000
    best_move = legal_moves[0]
    for move in legal_moves:
        # negascout
        score = 0
        if move != legal_moves[0]:
            last_move = deepcopy(node.last_move)
            node.make_move(*move, tb_cache, cm_cache)
            score, _ = negamax(node, depth-1, -alpha-1, -
                               alpha, tt, tb_cache, cm_cache)
            node.last_move = last_move
            node.undo_move(*move, tb_cache, cm_cache)
            score = -score
            if score > alpha and score < beta:
                last_move = deepcopy(node.last_move)
                node.make_move(*move, tb_cache, cm_cache)
                score, _ = negamax(node, depth-1, -beta, -
                                   score, tt, tb_cache, cm_cache)
                node.last_move = last_move
                node.undo_move(*move, tb_cache, cm_cache)
                score = -score
        else:
            node.make_move(*move, tb_cache, cm_cache)
            last_move = deepcopy(node.last_move)
            score, _ = negamax(node, depth-1, -beta, -
                               alpha, tt, tb_cache, cm_cache)
            node.last_move = last_move
            node.undo_move(*move, tb_cache, cm_cache)
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
    tt.set(node.__hash__(), tt_entry)
    return best_score, best_move

# iterative deepening negamax with alpha-beta pruning and transposition table


def negamax_iterative_deepening(node, depth, alpha, beta, tt, tb_cache, cm_cache, process_id=0, q=None):
    best_score = -10000
    best_move = None
    #print id of tt
    print(id(tt))
    # start timer
    start = timeit.default_timer()
    # print time elapsed after each iteration
    for i in range(1, depth+1):
        global node_explored, tt_hit
        best_score, best_move = negamax(
            node, i, alpha, beta, tt, tb_cache, cm_cache,process_id)
        print(f'depth: {i} score: {best_score} move: {best_move}')
        # print(f'Node explored: {node_explored}, TT hit: {tt_hit}')
        stop = timeit.default_timer()
        print(f'Time elapsed: {stop - start}')
        if best_score > 9000:
            break
    if q is not None:
        q.put((best_score, best_move))
    return best_score, best_move


if __name__ == '__main__':
    board_size = 15
    win_length = 5
    game = Node(board_size, win_length)
    tt = TranspositionTable()
    # cache the threat board
    tb_cache = TranspositionTable()
    cm_cache = TranspositionTable()
    node_explored = 0
    tt_hit = 0
    # play game in terminal
    i = 0
    game.make_move(7, 7, tb_cache, cm_cache)
    game.make_move(7, 8, tb_cache, cm_cache)
    game.make_move(6, 8, tb_cache, cm_cache)
    game.make_move(6, 7, tb_cache, cm_cache)
    cProfile.run(
        'negamax_iterative_deepening(game, 4, -10000, 10000, tt,tb_cache, cm_cache)')
    # while True:
    #     heuristic_time = 0
    #     node_explored = 0
    #     tt_hit = 0
    #     game.print_board()
    #     if game.check_win():
    #         print('You win!')
    #         break
    #     score, move = negamax_iterative_deepening(game, 25, -10000, 10000, tt,tb_cache, cm_cache)
    #     game.make_move(*move,tb_cache, cm_cache)
    #     game.print_board()
    #     if game.check_win():
    #         print('You lose!')
    #         break
    #     #input row and column convert to int
    #     row = int(input('row: '))
    #     col = int(input('col: '))
    #     game.make_move(row, col,tb_cache, cm_cache)
