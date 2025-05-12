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
# Import các thuật toán thỏa mãn ràng buộc CSP
from .csp_algorithms import (
    solve_puzzle_with_ac3,
    solve_puzzle_with_backtracking,
    state_to_positions,
    positions_to_state,
    create_puzzle_state_from_known_positions
)
# Import các thuật toán học tăng cường (RL)
from .rl_algorithms import (
    QLearningAgent,
    value_iteration,
    solve_with_value_iteration
)

import os
import pickle
import warnings

# Import các thành phần core
from src.core.buzzle_logic import is_solvable, Buzzle, create_new_state # create_new_state có thể không cần trực tiếp ở manager

def get_algorithm_groups():
    """
    Group algorithms by their characteristics
    Returns a dictionary of algorithm groups
    """
    groups = {
        "Tìm kiếm không có thông tin (Uninformed Search)": {
            "bfs": "Tìm Kiếm Theo Chiều Rộng",
            "dfs": "Tìm Kiếm Theo Chiều Sâu",
            "ucs": "Tìm Kiếm Chi Phí Đồng Nhất",
            "ids": "Tìm Kiếm Sâu Dần"
        },
        "Tìm kiếm có thông tin (Informed Search)": {
            "astar": "Tìm Kiếm A*",
            "idastar": "Tìm Kiếm IDA*",
            "greedy": "Tìm Kiếm Tham Lam"
        },
        "Tìm kiếm cục bộ (Local Search)": {
            "hill_climbing": "Leo Đồi",
            "random_restart_hc": "Leo Đồi Khởi Động Lại", # Key ngắn gọn hơn
            "simulated_annealing": "Mô Phỏng Luyện Kim",
            "genetic_algorithm": "Thuật Toán Di Truyền"
        },
        "Thuật toán thỏa mãn ràng buộc (CSP)": {
            "ac3": "Thuật Toán AC-3",
            "backtracking": "Thuật Toán Backtracking",
            "backtracking_with_mrv": "Backtracking với MRV",
            "backtracking_with_mrv_lcv": "Backtracking với MRV & LCV"
        },
        "Học tăng cường (Reinforcement Learning)": {
            "q_learning": "Q-Learning (Đã huấn luyện)",
            "value_iteration": "Value Iteration (Đã huấn luyện)"
        }
    }
    return groups

# Load pre-trained RL models from disk
def load_rl_models():
    """Load pre-trained RL models from disk."""
    models = {
        'q_learning': None,
        'value_iteration': {'utilities': None, 'policy': None}
    }
    
    # Paths to models
    q_learning_path = "models/q_learning_model.pkl"
    value_iteration_path = "models/value_iteration_model.pkl"
    
    # Try to load Q-Learning model
    if os.path.exists(q_learning_path):
        try:
            with open(q_learning_path, 'rb') as f:
                models['q_learning'] = {
                    'agent': pickle.load(f),
                    'training_stats': {'loaded_from_disk': True}
                }
            print(f"Loaded Q-Learning model from {q_learning_path}")
        except Exception as e:
            print(f"Error loading Q-Learning model: {e}")
    else:
        print(f"Warning: Q-Learning model file {q_learning_path} not found")
    
    # Try to load Value Iteration model
    if os.path.exists(value_iteration_path):
        try:
            with open(value_iteration_path, 'rb') as f:
                vi_model = pickle.load(f)
                models['value_iteration'] = {
                    'utilities': vi_model['utilities'],
                    'policy': vi_model['policy'],
                    'stats': vi_model['stats']
                }
            print(f"Loaded Value Iteration model from {value_iteration_path}")
        except Exception as e:
            print(f"Error loading Value Iteration model: {e}")
    else:
        print(f"Warning: Value Iteration model file {value_iteration_path} not found")
    
    return models

# Khởi tạo RL agents từ mô hình đã huấn luyện
RL_AGENTS = load_rl_models()

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
    "genetic_algorithm": genetic_algorithm,
    # CSP
    "ac3": solve_puzzle_with_ac3,
    "backtracking": lambda known_positions: solve_puzzle_with_backtracking(known_positions, use_mrv=False, use_lcv=False),
    "backtracking_with_mrv": lambda known_positions: solve_puzzle_with_backtracking(known_positions, use_mrv=True, use_lcv=False),
    "backtracking_with_mrv_lcv": lambda known_positions: solve_puzzle_with_backtracking(known_positions, use_mrv=True, use_lcv=True),
    # RL
    "q_learning": lambda puzzle: solve_with_q_learning(puzzle),
    "value_iteration": lambda puzzle: solve_with_value_iteration_wrapper(puzzle)
}

# Các thuật toán không cần kiểm tra is_solvable() trước khi chạy
# Hoặc các thuật toán có cách xử lý is_solvable() riêng hoặc không áp dụng
SKIP_SOLVABLE_CHECK_ALGOS = {
    "hill_climbing",
    "random_restart_hc",
    "simulated_annealing",
    "genetic_algorithm",
    "ac3",
    "backtracking",
    "backtracking_with_mrv",
    "backtracking_with_mrv_lcv",
    "q_learning",
    "value_iteration"
}

# Danh sách các thuật toán CSP
CSP_ALGORITHMS = {
    "ac3",
    "backtracking",
    "backtracking_with_mrv",
    "backtracking_with_mrv_lcv"
}

# Danh sách các thuật toán RL
RL_ALGORITHMS = {
    "q_learning",
    "value_iteration"
}

def solve_with_q_learning(puzzle):
    """
    Giải puzzle bằng Q-learning.
    
    Parameters:
    - puzzle: Trạng thái bắt đầu (Buzzle object)
    
    Returns:
    - path: Đường đi giải pháp
    - steps: Số bước thực hiện
    - stats: Bảng thống kê
    """
    global RL_AGENTS
    
    # Kiểm tra xem mô hình đã được tải chưa
    if RL_AGENTS['q_learning'] is None:
        warnings.warn("Q-Learning model not loaded. Solving will likely fail.")
        return [], 0, {"error": "Model not loaded"}
    
    # Lấy agent đã huấn luyện
    agent = RL_AGENTS['q_learning']['agent']
    training_stats = RL_AGENTS['q_learning']['training_stats']
    
    # Giải puzzle
    path, steps, q_table_size = agent.solve(puzzle, max_steps=150)
    
    # Bổ sung thông tin thống kê
    stats = {
        'agent': agent,  # Thêm agent vào stats để lấy utility map
        'loaded_from_disk': training_stats.get('loaded_from_disk', False),
        'q_table_size': q_table_size,
        'steps': steps
    }
    
    return path, steps, stats

def solve_with_value_iteration_wrapper(puzzle):
    """
    Giải puzzle bằng Value Iteration.
    
    Parameters:
    - puzzle: Trạng thái bắt đầu (Buzzle object)
    
    Returns:
    - path: Đường đi giải pháp
    - steps: Số bước thực hiện
    - stats: Bảng thống kê
    """
    global RL_AGENTS
    
    # Kiểm tra xem mô hình đã được tải chưa
    if RL_AGENTS['value_iteration']['utilities'] is None:
        warnings.warn("Value Iteration model not loaded. Solving will likely fail.")
        return [], 0, {"error": "Model not loaded"}
    
    # Lấy utilities và policy đã có
    utilities = RL_AGENTS['value_iteration']['utilities']
    policy = RL_AGENTS['value_iteration']['policy']
    vi_stats = RL_AGENTS['value_iteration'].get('stats', {})
    
    # Giải puzzle
    path, steps = solve_with_value_iteration(puzzle, utilities, policy)
    
    # Bổ sung thông tin thống kê
    stats = {
        'loaded_from_disk': True,
        'states_explored': vi_stats.get('states_explored', 0),
        'steps': steps
    }
    
    return path, steps, stats

def solve_puzzle(algorithm_key, start_state, ui_update_callback=None, stop_event=None, heuristic_name=None, known_positions=None):
    """
    Unified interface for all search algorithms.
    Input:
        algorithm_key (str): Key của thuật toán (ví dụ: 'bfs', 'astar').
        start_state (Buzzle object): Trạng thái bắt đầu.
        ui_update_callback: (Optional) callback để cập nhật UI với trạng thái hiện tại.
        stop_event: (Optional) threading.Event để dừng thuật toán sớm.
        heuristic_name: (Optional) Tên của heuristic được chọn từ UI (ví dụ 'manhattan', 'misplaced')
                        Sẽ được dùng cho các thuật toán cục bộ.
        known_positions: (Optional) Dictionary chứa các vị trí đã biết cho thuật toán CSP.
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

    # Xử lý thuật toán RL
    if algo_key_lower in RL_ALGORITHMS:
        path, steps, stats = solver_func(start_state)
        return path, steps, stats

    # Xử lý thuật toán CSP
    if algo_key_lower in CSP_ALGORITHMS:
        if known_positions is None:
            # Nếu không có vị trí đã biết, lấy từ trạng thái hiện tại
            known_positions = state_to_positions(start_state.data)
        
        # Gọi thuật toán CSP với known_positions
        solution, stats = solver_func(known_positions)
        
        if solution:
            # Chuyển đổi solution thành định dạng phù hợp với giao diện
            # Trong trường hợp này, chỉ trả về trạng thái cuối cùng
            return [("final", solution)], stats.get('nodes', 0) if 'nodes' in stats else stats.get('steps', 0), stats
        else:
            # Không tìm thấy giải pháp
            steps = stats.get('nodes', 0) if 'nodes' in stats else stats.get('steps', 0)
            return None, steps, stats
    
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
        # Call the genetic algorithm
        best_solution_data, total_fitness_evaluations, final_population_size = solver_func(start_state, heuristic_func_for_fitness=selected_heuristic_func)
        
        # Convert the result to the expected format for on_solution_ready
        if best_solution_data is not None:
            # Create a path with a single step showing the final state
            return [("final", best_solution_data)], total_fitness_evaluations, final_population_size
        else:
            return None, total_fitness_evaluations, final_population_size
    else: # Các thuật toán cổ điển
        return solver_func(start_state) # Giả sử các hàm này có thể nhận ui_update_callback, stop_event nếu cần
