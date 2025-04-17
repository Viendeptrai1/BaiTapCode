# Import các thuật toán từ module search_algorithms
from .search_algorithms import (
    bfs, dfs, ucs, ids,
    astar, greedy, idastar,
    hill_climbing_max, hill_climbing_random, simulated_annealing,
    genetic_algorithm
)

# Import hàm tìm kiếm AND/OR từ and_or_search.py
from .and_or_search import and_or_graph_search

# Import các thành phần core
from src.core.AndOrProblemAdapter import AndOrProblemAdapter
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
            "simulated_annealing": "Simulated Annealing"
        },
        "Tìm kiếm dựa trên đồ thị (Graph-based)": { # Đã đổi tên nhóm
             "simplified_or_search": "Simplified OR Search (Recursive)" # <<< Sửa Key và Tên
        },
         "Thuật toán Tiến hóa (Evolutionary Algorithms)": {
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
    "simplified_or_search": and_or_graph_search, # <<< Sửa Key
    "genetic_algorithm": genetic_algorithm
}

# Các thuật toán không cần kiểm tra is_solvable() trước khi chạy
SKIP_SOLVABLE_CHECK_ALGOS = {
    "hill_climbing_max",
    "hill_climbing_random",
    "simulated_annealing",
    "genetic_algorithm",
    "simplified_or_search" # <<< Sửa Key
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

    # Kiểm tra is_solvable cho các thuật toán cần thiết
    # if algo_key_lower not in SKIP_SOLVABLE_CHECK_ALGOS:
    #     if not is_solvable(start_state.data):
    #         print(f"Algorithm {algorithm_key.upper()}: Initial state is unsolvable.")
    #         return [], 0, 0 # Trả về không tìm thấy

    # Xử lý đặc biệt cho Simplified OR Search (trước đây là AND/OR)
    if algo_key_lower == "simplified_or_search": # <<< Sửa Key trong điều kiện if
        problem_adapter = AndOrProblemAdapter(start_state)
        # Hàm simplified_and_or_search trả về (plan, nodes_expanded)
        plan, nodes_expanded = solver_func(problem_adapter) # Gọi hàm đã import

        if plan == 'failure':
            # Kiểm tra lại xem có phải do unsolvable không
            if not is_solvable(start_state.data):
                 print("Simplified OR Search failed: Initial state is unsolvable.")
            # Nếu solvable mà vẫn fail -> có thể do lỗi khác hoặc giới hạn đệ quy
            return [], nodes_expanded, 1 # max_fringe không áp dụng rõ ràng, đặt là 1
        else:
            # Chuyển đổi plan (list of moves) thành path (list of (move, state_data))
            path = []
            current_data = start_state.data
            temp_state_data = current_data
            # Dùng adapter để lấy trạng thái tuple (đảm bảo tính nhất quán)
            current_tuple = tuple(map(tuple, temp_state_data))
            for move in plan:
                # Dùng lại hàm result của adapter để lấy trạng thái tuple tiếp theo
                next_state_tuple = problem_adapter.result(current_tuple, move)
                if next_state_tuple is not None: # Kiểm tra hành động hợp lệ
                     next_data = [list(row) for row in next_state_tuple] # Chuyển về list of list
                     path.append((move, next_data))
                     temp_state_data = next_data # Cập nhật trạng thái data
                     current_tuple = next_state_tuple # Cập nhật trạng thái tuple
                else:
                     # Lỗi logic nếu plan chứa bước đi không hợp lệ (không nên xảy ra)
                     print(f"Error reconstructing OR path: Invalid move '{move}' from state {temp_state_data}")
                     return [], nodes_expanded, 1

            return path, nodes_expanded, 1

    # Xử lý các thuật toán khác (không thay đổi logic, chỉ dùng algo_key_lower)
    else:
        # Kiểm tra is_solvable cho các thuật toán khác ở đây nếu muốn
        if algo_key_lower not in SKIP_SOLVABLE_CHECK_ALGOS:
            if not is_solvable(start_state.data):
                print(f"Algorithm {algorithm_key.upper()}: Initial state is unsolvable.")
                return [], 0, 0 # Trả về không tìm thấy
        # Gọi hàm solver tương ứng
        return solver_func(start_state)
