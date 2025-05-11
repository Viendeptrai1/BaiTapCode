from .search_algorithms import (
    bfs, dfs, ucs, ids,
    astar, greedy, idastar
    # hill_climbing_max, hill_climbing_random, simulated_annealing,
    # genetic_algorithm
)
# Thêm import cho các thuật toán tìm kiếm cục bộ
from .local_search_algorithms import (
    hill_climbing, 
    random_restart_hill_climbing, 
    simulated_annealing, 
    genetic_algorithm,
    number_of_misplaced_tiles, # Có thể export cả hàm heuristic này nếu muốn dùng từ bên ngoài
    manhattan_distance # manhattan_distance đã được import từ core.buzzle_logic trong local_search_algorithms, nhưng có thể export lại ở đây nếu cần
)
from .algorithm_manager import solve_puzzle, get_algorithm_groups

__all__ = [
    'bfs', 'dfs', 'ucs', 'ids',
    'astar', 'greedy', 'idastar',
    # 'hill_climbing_max', 'hill_climbing_random', 'simulated_annealing',
    # 'genetic_algorithm',
    'solve_puzzle', 'get_algorithm_groups',
    'number_of_misplaced_tiles', # Thêm vào nếu muốn có thể truy cập trực tiếp
    # 'manhattan_distance' # Tương tự, nếu muốn truy cập trực tiếp từ module này
]
