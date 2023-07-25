import cProfile
from copy import deepcopy
from re import T
from negamax import negamax, negamax_iterative_deepening
import multiprocessing as mp
from trans_table import TTManager

from node import Node
from trans_table import TranspositionTable


def iterative_smp(node, depth, alpha, beta, ttx, tb_cachex, cm_cachex):
    num_process = 6
    q = mp.Queue()
    TTManager.register('TranspositionTable', TranspositionTable)
    # with mp.Pool(processes=num_process) as pool:
    #     for d in range(depth):
    #         best_score = -10000
    #         best_move = None
    #         processes:List['mp.Process'] = []
    #         q= mp.Queue()
    #         for i in range(num_process):
    #             c_node = deepcopy(node)
    #             if i > 0:
    #                 process = mp.Process(target=negamax, args=(
    #                     c_node, d+1, alpha, beta, tt, cache,i))
    #             else:
    #                 process = mp.Process(target=negamax, args=(
    #                     c_node, d+1, alpha, beta, tt, cache,i, q))
    #             processes.append(process)
    #             process.start()
    #         # terminate other processes when process 0 is done and get the result from only process 0
    #         processes[0].join()
    #         best_score, best_move = q.get()
    #         print(f'depth: {d+1} score: {best_score} move: {best_move}')
    #         for i in range(1, num_process):
    #             processes[i].terminate()
    #         if best_score > 9000:
    #             break
    # return best_score, best_move
    with TTManager() as manager:
        tt = manager.TranspositionTable()
        tb_cache = manager.TranspositionTable()
        cm_cache = manager.TranspositionTable()
        tt.clone(ttx)
        tb_cache.clone(tb_cachex)
        cm_cache.clone(cm_cachex)
        processes = []
        for i in range(num_process):
            c_node = deepcopy(node)
            process = mp.Process(target=negamax_iterative_deepening, args=(
                c_node, depth, alpha, beta, tt, tb_cache,cm_cache , i,q))
            processes.append(process)
            process.start()
        processes[0].join()
        for i in range(1, num_process):
            processes[i].terminate()
            processes[i].join()
        best_score, best_move = q.get()
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
    cProfile.run('iterative_smp(game, 4, -10000, 10000, tt,tb_cache, cm_cache)')
