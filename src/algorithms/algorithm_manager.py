# Import các thuật toán từ module search_algorithms
from .search_algorithms import (
    bfs, dfs, ucs, ids,
    astar, greedy, idastar,
    hill_climbing_max, hill_climbing_random, simulated_annealing,
    genetic_algorithm
)


# Import các thành phần core
from src.core.buzzle_logic import is_solvable, Buzzle, create_new_state

def get_algorithm_groups():
    """
    Group algorithms by their characteristics
    Returns a dictionary of algorithm groups
    """
    groups = {
        "Tìm kiếm không có thông tin (Uninformed Search)": {
            "bfs": "Breadth-First Search",
            "dfs": "Depth-First Search",
            "ucs": "Uniform Cost Search",
            "ids": "Iterative Deepening Search"
        },
        "Tìm kiếm có thông tin (Informed Search)": {
            "astar": "A* Search",
            "idastar": "IDA* Search",
            "greedy": "Greedy Best-First Search"
        },
        "Tìm kiếm cục bộ (Local Search)": {
            "hill_climbing_max": "Hill Climbing Max",
            "hill_climbing_random": "Hill Climbing Random",
            "simulated_annealing": "Simulated Annealing",
            "genetic_algorithm": "Genetic Algorithm"
        }
    }
    return groups

# Dictionary ánh xạ tên thuật toán (key trong groups) sang hàm thực thi
SOLVER_FUNCTIONS = {
    "bfs": bfs,
    "dfs": dfs,
    "ucs": ucs,
    "astar": astar,
    "idastar": idastar,
    "greedy": greedy,
    "ids": ids,
    "hill_climbing_max": hill_climbing_max,
    "hill_climbing_random": hill_climbing_random,
    "simulated_annealing": simulated_annealing,
    "genetic_algorithm": genetic_algorithm
}

# Các thuật toán không cần kiểm tra is_solvable() trước khi chạy
SKIP_SOLVABLE_CHECK_ALGOS = {
    "hill_climbing_max",
    "hill_climbing_random",
    "simulated_annealing",
    "genetic_algorithm"
}


def solve_puzzle(algorithm_key, start_state):
    """
    Unified interface for all search algorithms.
    Input:
        algorithm_key (str): Key của thuật toán (ví dụ: 'bfs', 'astar').
        start_state (Buzzle object): Trạng thái bắt đầu.
    Output:
        (path, nodes_expanded, max_fringe_or_pop_size)
        path: list of tuples (move, new_state_data), hoặc [] nếu không tìm thấy/không áp dụng.
    """
    # Chuyển key về chữ thường để đảm bảo tính nhất quán khi tra cứu
    algo_key_lower = algorithm_key.lower()
    solver_func = SOLVER_FUNCTIONS.get(algo_key_lower)

    if not solver_func:
        print(f"Error: Unknown algorithm key '{algorithm_key}'")
        return [], 0, 0

    # Kiểm tra is_solvable cho các thuật toán có yêu cầu
    if algo_key_lower not in SKIP_SOLVABLE_CHECK_ALGOS:
        if not is_solvable(start_state.data):
            print(f"Algorithm {algorithm_key.upper()}: Initial state is unsolvable.")
            return [], 0, 0 # Trả về không tìm thấy
            
    # Gọi hàm solver tương ứng
    return solver_func(start_state)
