# Import các thuật toán từ module search_algorithms (cổ điển)
from .search_algorithms import (
    bfs, dfs, ucs, ids,
    astar, greedy, idastar
)
# Import các thuật toán từ local_search_algorithms
from .local_search_algorithms import (
    hill_climbing, 
    random_restart_hill_climbing, 
    simulated_annealing, 
    genetic_algorithm,
    number_of_misplaced_tiles, # Import luôn các heuristic nếu cần dùng trực tiếp ở đây
    manhattan_distance
)


# Import các thành phần core
from src.core.buzzle_logic import is_solvable, Buzzle, create_new_state # create_new_state có thể không cần trực tiếp ở manager

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
            "hill_climbing": "Hill Climbing",
            "random_restart_hc": "Random-Restart Hill Climbing", # Key ngắn gọn hơn
            "simulated_annealing": "Simulated Annealing",
            "genetic_algorithm": "Genetic Algorithm"
        }
    }
    return groups

# Dictionary ánh xạ tên thuật toán (key trong groups) sang hàm thực thi
SOLVER_FUNCTIONS = {
    # Cổ điển
    "bfs": bfs,
    "dfs": dfs,
    "ucs": ucs,
    "astar": astar,
    "idastar": idastar,
    "greedy": greedy,
    "ids": ids,
    # Cục bộ
    "hill_climbing": hill_climbing,
    "random_restart_hc": random_restart_hill_climbing, 
    "simulated_annealing": simulated_annealing,
    "genetic_algorithm": genetic_algorithm
}

# Các thuật toán không cần kiểm tra is_solvable() trước khi chạy
# Hoặc các thuật toán có cách xử lý is_solvable() riêng hoặc không áp dụng
SKIP_SOLVABLE_CHECK_ALGOS = {
    "hill_climbing",
    "random_restart_hc",
    "simulated_annealing",
    "genetic_algorithm"
}


def solve_puzzle(algorithm_key, start_state, ui_update_callback=None, stop_event=None, heuristic_name=None):
    """
    Unified interface for all search algorithms.
    Input:
        algorithm_key (str): Key của thuật toán (ví dụ: 'bfs', 'astar').
        start_state (Buzzle object): Trạng thái bắt đầu.
        ui_update_callback: (Optional) callback để cập nhật UI với trạng thái hiện tại.
        stop_event: (Optional) threading.Event để dừng thuật toán sớm.
        heuristic_name: (Optional) Tên của heuristic được chọn từ UI (ví dụ 'manhattan', 'misplaced')
                        Sẽ được dùng cho các thuật toán cục bộ.
    Output:
        (result, nodes_expanded, max_fringe_or_other_metric)
        result: path (list of tuples) cho thuật toán tìm đường, 
                hoặc best_state_data (list of lists) cho SA/GA nếu tìm thấy goal,
                hoặc None nếu không tìm thấy.
        nodes_expanded: Số nút đã duyệt/đánh giá.
        max_fringe_or_other_metric: Kích thước fringe/quần thể lớn nhất hoặc số lần lặp/khởi động lại.
    """
    algo_key_lower = algorithm_key.lower()
    solver_func = SOLVER_FUNCTIONS.get(algo_key_lower)

    if not solver_func:
        print(f"Error: Unknown algorithm key '{algorithm_key}'")
        return None, 0, 0

    # Xử lý is_solvable cho các thuật toán không nằm trong SKIP_SOLVABLE_CHECK_ALGOS
    if algo_key_lower not in SKIP_SOLVABLE_CHECK_ALGOS:
        if not is_solvable(start_state.data):
            print(f"Algorithm {algorithm_key.upper()}: Initial state is unsolvable.")
            return None, 0, 0 
    
    # Chọn hàm heuristic cho các thuật toán cục bộ dựa trên heuristic_name
    selected_heuristic_func = manhattan_distance # Mặc định
    if heuristic_name:
        if heuristic_name.lower() == 'manhattan':
            selected_heuristic_func = manhattan_distance
        elif heuristic_name.lower() == 'misplaced':
            selected_heuristic_func = number_of_misplaced_tiles
        # Có thể thêm các heuristic khác nếu có

    # Gọi hàm solver tương ứng
    # Một số thuật toán cục bộ có thể cần thêm tham số (ví dụ: heuristic_func)
    if algo_key_lower in ["hill_climbing", "random_restart_hc", "simulated_annealing"]:
        # initial_state cho random_restart_hc là data, các hàm khác là Buzzle object
        if algo_key_lower == "random_restart_hc":
             # random_restart_hill_climbing nhận initial_state_data
            return solver_func(start_state.data, heuristic_func=selected_heuristic_func)
        else:
            return solver_func(start_state, heuristic_func=selected_heuristic_func)
    elif algo_key_lower == "genetic_algorithm":
        return solver_func(start_state, heuristic_func_for_fitness=selected_heuristic_func)
    else: # Các thuật toán cổ điển
        return solver_func(start_state) # Giả sử các hàm này có thể nhận ui_update_callback, stop_event nếu cần
