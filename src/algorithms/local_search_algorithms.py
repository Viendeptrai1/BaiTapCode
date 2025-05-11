import random
import math

# Import các thành phần cần thiết từ buzzle_logic và các hàm heuristic
from src.core.buzzle_logic import Buzzle, create_new_state, manhattan_distance, is_solvable # is_solvable có thể không cần cho mọi local search

# Có thể cần thêm hàm number_of_misplaced_tiles nếu chưa có hoặc muốn tách riêng
# from src.core.buzzle_logic import number_of_misplaced_tiles # Giả sử hàm này tồn tại

# --- Helper Functions (nếu cần) ---

def number_of_misplaced_tiles(buzzle_instance_or_data):
    """Tính số ô sai vị trí so với trạng thái đích.
    Có thể nhận vào Buzzle instance hoặc data (list of lists).
    Ô trống (0) không được tính là sai vị trí."""
    if isinstance(buzzle_instance_or_data, Buzzle):
        data = buzzle_instance_or_data.data
    else:
        data = buzzle_instance_or_data
    
    goal_state_flat = [1, 2, 3, 4, 5, 6, 7, 8, 0] # Trạng thái đích phẳng
    current_flat = [tile for row in data for tile in row]
    misplaced = 0
    for i in range(len(current_flat)):
        if current_flat[i] != 0 and current_flat[i] != goal_state_flat[i]:
            misplaced += 1
    return misplaced

def generate_random_solvable_state():
    """
    Tạo ra một trạng thái 8-puzzle ngẫu nhiên và đảm bảo nó có thể giải được.
    Trả về: list of lists đại diện cho data của puzzle.
    """
    while True:
        numbers = list(range(9)) # 0 đến 8
        random.shuffle(numbers)
        new_state_data = [numbers[i:i+3] for i in range(0, 9, 3)]
        if is_solvable(new_state_data):
            return new_state_data

# --- Thuật toán Leo đồi (Hill Climbing) ---

def hill_climbing(initial_state, heuristic_func=manhattan_distance):
    """
    Thuật toán Leo đồi đơn giản.
    heuristic_func: hàm để đánh giá trạng thái (ví dụ: manhattan_distance, number_of_misplaced_tiles)
    Trả về: (path_to_goal, nodes_evaluated, max_neighbors_at_step) 
             hoặc (None, nodes_evaluated, max_neighbors_at_step) nếu bị kẹt.
             path_to_goal là list các (move, state_data)
    """
    # Kiểm tra xem initial_state có phải là Buzzle object không, nếu không thì tạo mới
    if not isinstance(initial_state, Buzzle):
        current_buzzle = Buzzle(initial_state)
    else:
        current_buzzle = initial_state

    current_h = heuristic_func(current_buzzle)
    
    path_of_states_data = [current_buzzle.data] 
    nodes_evaluated = 1 
    max_neighbors_at_step = 0

    while True:
        if current_buzzle.is_goal():
            break # Đã đạt đích

        best_neighbor_data = None
        best_neighbor_h = current_h
        
        possible_moves_this_step = []
        for move in ["up", "down", "left", "right"]:
            success, neighbor_data = create_new_state(current_buzzle.data, move)
            if success:
                possible_moves_this_step.append(neighbor_data)
                
        max_neighbors_at_step = max(max_neighbors_at_step, len(possible_moves_this_step))
        # Đánh giá các láng giềng được tạo ra
        # nodes_evaluated += len(possible_moves_this_step) # Mỗi neighbor được xem xét là một node evaluated

        for neighbor_data in possible_moves_this_step:
            neighbor_buzzle = Buzzle(neighbor_data)
            nodes_evaluated +=1 # Đánh giá một láng giềng
            neighbor_h = heuristic_func(neighbor_buzzle)
            
            if neighbor_h < best_neighbor_h: # Tìm trạng thái tốt hơn (h nhỏ hơn)
                best_neighbor_h = neighbor_h
                best_neighbor_data = neighbor_data
        
        if best_neighbor_data is None: # Không tìm thấy láng giềng nào tốt hơn -> bị kẹt
            break
        
        # Di chuyển đến trạng thái tốt nhất
        current_buzzle = Buzzle(best_neighbor_data)
        current_h = best_neighbor_h
        path_of_states_data.append(current_buzzle.data)

    # Tái tạo path (move, state) từ path_of_states_data
    final_path = []
    # Chỉ tái tạo path nếu đích thực sự được tìm thấy và có ít nhất một bước đi
    if Buzzle(path_of_states_data[-1]).is_goal() and len(path_of_states_data) > 1:
        for i in range(len(path_of_states_data) - 1):
            prev_state_data = path_of_states_data[i]
            next_state_data = path_of_states_data[i+1]
            found_move = None
            for move_candidate in ["up", "down", "left", "right"]:
                success, potential_next_data = create_new_state(prev_state_data, move_candidate)
                if success and potential_next_data == next_state_data:
                    found_move = move_candidate
                    break
            if found_move:
                final_path.append((found_move, next_state_data))
            else:
                 # Điều này không nên xảy ra nếu path_of_states_data được xây dựng đúng từ các bước đi hợp lệ
                 print("HillClimbing Error: Could not reconstruct move during final path generation.")
                 return None, nodes_evaluated, max_neighbors_at_step 
        return final_path, nodes_evaluated, max_neighbors_at_step
    
    # Nếu trạng thái cuối cùng không phải là goal (tức là bị kẹt)
    if not Buzzle(path_of_states_data[-1]).is_goal():
        return None, nodes_evaluated, max_neighbors_at_step
    else: # Trạng thái ban đầu là goal, không có path di chuyển (path_of_states_data chỉ có 1 phần tử)
        return [], nodes_evaluated, max_neighbors_at_step

def random_restart_hill_climbing(initial_state_data, # Nhận data thay vì Buzzle object để dễ dàng khởi tạo ngẫu nhiên
                                 heuristic_func=manhattan_distance, 
                                 max_restarts=10,
                                 max_total_nodes_evaluated=None): # Thêm giới hạn tổng số node
    """
    Leo đồi với khởi động lại ngẫu nhiên.
    initial_state_data: list of lists, dữ liệu trạng thái ban đầu.
    heuristic_func: hàm đánh giá.
    max_restarts: số lần khởi động lại tối đa.
    max_total_nodes_evaluated: tùy chọn, giới hạn tổng số node được đánh giá qua tất cả các lần chạy.

    Trả về: (path_to_goal, total_nodes_evaluated_accross_restarts, num_restarts_done)
             hoặc (None, total_nodes_evaluated_accross_restarts, num_restarts_done) nếu không tìm thấy sau tất cả các lần khởi động lại.
    """
    # Lưu trữ tổng số node đã đánh giá qua tất cả các lần khởi động lại
    total_nodes_evaluated_accross_restarts = 0

    # Chạy lần đầu với trạng thái ban đầu được cung cấp
    path, nodes, _ = hill_climbing(Buzzle(initial_state_data), heuristic_func)
    total_nodes_evaluated_accross_restarts += nodes

    if path is not None: # Tìm thấy lời giải ngay lần đầu
        return path, total_nodes_evaluated_accross_restarts, 0

    for i in range(max_restarts):
        if max_total_nodes_evaluated and total_nodes_evaluated_accross_restarts >= max_total_nodes_evaluated:
            # print(f"RandomRestart: Reached max_total_nodes_evaluated limit ({max_total_nodes_evaluated}).")
            break

        random_start_data = generate_random_solvable_state()
        
        path, nodes, _ = hill_climbing(Buzzle(random_start_data), heuristic_func)
        total_nodes_evaluated_accross_restarts += nodes
        
        if path is not None: # Tìm thấy lời giải sau một lần khởi động lại
            return path, total_nodes_evaluated_accross_restarts, i + 1
            
    # Không tìm thấy lời giải sau tất cả các lần khởi động lại
    return None, total_nodes_evaluated_accross_restarts, max_restarts

# --- Thuật toán Luyện tôi mô phỏng (Simulated Annealing) ---

def simulated_annealing(initial_state, # Nhận Buzzle object hoặc data
                        heuristic_func=manhattan_distance, 
                        initial_temp=100.0, # Nên là float
                        cooling_rate=0.99, 
                        min_temp=0.1, 
                        max_iterations_per_temp_schedule=10000, # Tổng số lần lặp tối đa
                        max_iterations_at_each_temp=None): # Số lần lặp tại mỗi mức nhiệt độ (tùy chọn)
    """
    Thuật toán Luyện tôi mô phỏng.
    heuristic_func: hàm để đánh giá trạng thái (cần tối thiểu hóa).
    initial_temp: Nhiệt độ ban đầu.
    cooling_rate: Tỷ lệ làm mát (ví dụ: 0.99, 0.95).
    min_temp: Nhiệt độ tối thiểu để dừng.
    max_iterations_per_temp_schedule: Tổng số lần lặp tối đa cho toàn bộ quá trình.
    max_iterations_at_each_temp: Số lần lặp tại mỗi mức nhiệt độ (nếu được cung cấp, vòng lặp nhiệt độ sẽ có thêm điều kiện này).

    Trả về: (best_state_data_if_goal, nodes_evaluated, iterations_run)
             best_state_data_if_goal là data của goal state nếu trạng thái tốt nhất tìm được là goal, ngược lại là None.
             SA thường không trả về path.
    """
    if not isinstance(initial_state, Buzzle):
        current_buzzle = Buzzle(initial_state)
    else:
        current_buzzle = initial_state
    
    current_h = heuristic_func(current_buzzle)
    
    best_buzzle_overall = current_buzzle # Lưu trữ trạng thái tốt nhất từng thấy
    best_h_overall = current_h

    nodes_evaluated = 1 # Đánh giá trạng thái ban đầu
    total_iterations_run = 0
    
    temp = float(initial_temp)

    # Biến cờ để kiểm tra xem có bị kẹt hoàn toàn không (không có nước đi nào)
    stuck_without_moves = False

    while temp > min_temp and total_iterations_run < max_iterations_per_temp_schedule and not stuck_without_moves:
        iterations_this_temp = 0
        
        # Vòng lặp bên trong: thực hiện một số lần lặp tại nhiệt độ hiện tại
        while total_iterations_run < max_iterations_per_temp_schedule and not stuck_without_moves:
            if max_iterations_at_each_temp and iterations_this_temp >= max_iterations_at_each_temp:
                break # Đã đủ số lần lặp cho nhiệt độ này

            # Không cần kiểm tra is_goal() ở đây nữa, vì best_buzzle_overall sẽ được cập nhật
            # và kết quả cuối cùng sẽ dựa trên best_buzzle_overall.is_goal()

            # Chọn ngẫu nhiên một trạng thái lân cận hợp lệ
            possible_next_states_data = []
            for move in ["up", "down", "left", "right"]:
                success, neighbor_data = create_new_state(current_buzzle.data, move)
                if success:
                    possible_next_states_data.append(neighbor_data)
            
            if not possible_next_states_data: 
                stuck_without_moves = True # Bị kẹt, không có nước đi nào
                break 

            next_state_data = random.choice(possible_next_states_data)
            next_buzzle = Buzzle(next_state_data)
            nodes_evaluated += 1
            next_h = heuristic_func(next_buzzle)
            
            delta_e = next_h - current_h 

            if delta_e < 0: 
                current_buzzle = next_buzzle
                current_h = next_h
                if current_h < best_h_overall:
                    best_h_overall = current_h
                    best_buzzle_overall = current_buzzle
            else: 
                try:
                    if temp > 1e-9: 
                        probability = math.exp(-delta_e / temp)
                        if random.random() < probability:
                            current_buzzle = next_buzzle
                            current_h = next_h
                except OverflowError: 
                    pass 
            
            total_iterations_run += 1
            iterations_this_temp += 1
        
        temp *= cooling_rate 

    result_state_data = best_buzzle_overall.data if best_buzzle_overall.is_goal() else None
    return result_state_data, nodes_evaluated, total_iterations_run

# --- Thuật toán Di truyền (Genetic Algorithm) ---

def genetic_algorithm_objective_function(state_data, heuristic_func=manhattan_distance):
    """
    Hàm mục tiêu (fitness) cho Thuật toán Di truyền.
    Giá trị càng cao càng tốt.
    heuristic_func được truyền vào để tính h(n).
    """
    # Giả định heuristic_func có thể nhận data trực tiếp (như number_of_misplaced_tiles và manhattan_distance hiện tại)
    # hoặc một đối tượng Buzzle. Để nhất quán, chúng ta có thể luôn tạo Buzzle.
    if isinstance(state_data, Buzzle):
        h_value = heuristic_func(state_data)
    else:
        h_value = heuristic_func(Buzzle(state_data))

    # Lựa chọn 1: Đơn giản là -h(n)
    fitness = -h_value
    return fitness

def generate_ga_population(size, initial_puzzle_data=None, ensure_solvable=True):
    """
    Tạo quần thể ban đầu.
    size: Kích thước quần thể mong muốn.
    initial_puzzle_data: Tùy chọn, một trạng thái ban đầu (dạng data) để thêm vào quần thể.
    ensure_solvable: Cờ để đảm bảo tất cả các cá thể được tạo là solvable.
    Trả về: list các state_data.
    """
    population_data = []
    # Sử dụng set để kiểm tra trùng lặp hiệu quả nếu muốn đảm bảo quần thể duy nhất
    # population_tuples = set()

    if initial_puzzle_data:
        # Đảm bảo initial_puzzle_data là list of lists, không phải Buzzle object
        init_data_to_add = initial_puzzle_data.data if isinstance(initial_puzzle_data, Buzzle) else initial_puzzle_data
        if not ensure_solvable or is_solvable(init_data_to_add):
            population_data.append(init_data_to_add)
            # population_tuples.add(tuple(map(tuple, init_data_to_add)))

    max_attempts = size * 20 # Tăng số lần thử nếu cần nhiều cá thể duy nhất
    attempts = 0

    while len(population_data) < size and attempts < max_attempts:
        attempts += 1
        numbers = list(range(9))
        random.shuffle(numbers)
        new_state_data = [numbers[i:i+3] for i in range(0, 9, 3)]
        
        # new_state_tuple = tuple(map(tuple, new_state_data))
        # if new_state_tuple in population_tuples: # Kiểm tra trùng lặp nếu cần
        #     continue

        if not ensure_solvable or is_solvable(new_state_data):
            population_data.append(new_state_data)
            # population_tuples.add(new_state_tuple)
            
    if len(population_data) < size and ensure_solvable:
         print(f"GA Warning: Could only generate {len(population_data)}/{size} unique solvable states for initial population after {max_attempts} attempts.")
    elif len(population_data) < size and not ensure_solvable:
         print(f"GA Warning: Could only generate {len(population_data)}/{size} states for initial population after {max_attempts} attempts (solvability not strictly enforced for all generated). ")

    return population_data

def select_parents_ga(population_data, fitness_scores, num_parents, tournament_size=5):
    """
    Chọn cha mẹ bằng Tournament Selection.
    population_data: list các state_data.
    fitness_scores: list các điểm fitness tương ứng với population_data.
    num_parents: số lượng cha mẹ cần chọn.
    tournament_size: số lượng cá thể tham gia mỗi giải đấu.
    Trả về: list các state_data của cha mẹ được chọn.
    """
    parents_data = []
    population_with_fitness = list(zip(population_data, fitness_scores))

    if not population_with_fitness:
        return [] 

    actual_tournament_size = min(tournament_size, len(population_with_fitness))
    if actual_tournament_size <= 0:
        return [] 

    for _ in range(num_parents):
        if not population_with_fitness: # Nếu quần thể đã cạn kiệt trong quá trình lấy mẫu
            break
        # Đảm bảo actual_tournament_size không lớn hơn số cá thể còn lại
        current_max_tournament_size = min(actual_tournament_size, len(population_with_fitness))
        if current_max_tournament_size <=0: break

        tournament_participants = random.sample(population_with_fitness, current_max_tournament_size)
        
        winner = max(tournament_participants, key=lambda item: item[1])
        parents_data.append(winner[0]) 
        
    return parents_data

def crossover_ga(parent1_data, parent2_data):
    """
    Lai ghép Single-point crossover trên danh sách phẳng, sau đó sửa chữa.
    Trả về: hai child_data (hai trạng thái con mới).
    """
    p1_flat = [num for row in parent1_data for num in row]
    p2_flat = [num for row in parent2_data for num in row]
    size = len(p1_flat) 

    child1_flat = [-1] * size 
    point = random.randint(1, size - 2) if size > 2 else 1
    
    child1_flat[:point] = p1_flat[:point]
    current_child1_elements = set(child1_flat[:point])
    idx_p2 = 0
    for i in range(point, size):
        # Tìm số tiếp theo từ parent2 mà chưa có trong child1
        original_idx_p2 = idx_p2
        found_val_in_p2 = False
        while idx_p2 < size:
            if p2_flat[idx_p2] not in current_child1_elements:
                child1_flat[i] = p2_flat[idx_p2]
                current_child1_elements.add(p2_flat[idx_p2])
                idx_p2 += 1 # Tiến idx_p2 cho lần tìm kiếm tiếp theo từ p2
                found_val_in_p2 = True
                break
            idx_p2 += 1
        if not found_val_in_p2: # Nếu duyệt hết p2 mà không tìm đủ
            # print("Crossover Warning: Could not complete child1 from parent2. Filling missing with remaining unique numbers.")
            remaining_numbers = [n for n in range(size) if n not in current_child1_elements]
            random.shuffle(remaining_numbers)
            for j in range(point, size):
                if child1_flat[j] == -1 and remaining_numbers:
                    child1_flat[j] = remaining_numbers.pop(0)
            # Đảm bảo không còn -1
            if -1 in child1_flat:
                 # Fallback an toàn nếu vẫn lỗi
                return [row[:] for row in parent1_data], [row[:] for row in parent2_data]
            break # Thoát khỏi vòng lặp điền child1

    child2_flat = [-1] * size
    # point có thể giữ nguyên hoặc tạo mới
    child2_flat[:point] = p2_flat[:point]
    current_child2_elements = set(child2_flat[:point])
    idx_p1 = 0
    for i in range(point, size):
        original_idx_p1 = idx_p1
        found_val_in_p1 = False
        while idx_p1 < size:
            if p1_flat[idx_p1] not in current_child2_elements:
                child2_flat[i] = p1_flat[idx_p1]
                current_child2_elements.add(p1_flat[idx_p1])
                idx_p1 += 1
                found_val_in_p1 = True
                break
            idx_p1 += 1
        if not found_val_in_p1:
            # print("Crossover Warning: Could not complete child2 from parent1. Filling missing.")
            remaining_numbers = [n for n in range(size) if n not in current_child2_elements]
            random.shuffle(remaining_numbers)
            for j in range(point, size):
                if child2_flat[j] == -1 and remaining_numbers:
                    child2_flat[j] = remaining_numbers.pop(0)
            if -1 in child2_flat:
                return [row[:] for row in parent1_data], [row[:] for row in parent2_data]
            break

    child1_final_data = [child1_flat[i:i+3] for i in range(0, size, 3)]
    child2_final_data = [child2_flat[i:i+3] for i in range(0, size, 3)]
    
    if set(child1_flat) != set(range(size)) or set(child2_flat) != set(range(size)):
        # print("Crossover Sanity Check Failed: Children do not contain all numbers 0-8. Returning parents.")
        return [row[:] for row in parent1_data], [row[:] for row in parent2_data]

    return child1_final_data, child2_final_data

def mutate_ga(state_data, mutation_rate):
    """
    Đột biến một cá thể bằng cách thực hiện một nước đi ngẫu nhiên hợp lệ.
    state_data: list of lists, dữ liệu của cá thể cần đột biến.
    mutation_rate: xác suất xảy ra đột biến.
    Trả về: state_data đã đột biến (hoặc bản gốc nếu không đột biến).
    """
    if random.random() < mutation_rate:
        possible_next_states_data = []
        for move in ["up", "down", "left", "right"]:
            success, neighbor_data = create_new_state(state_data, move)
            if success:
                possible_next_states_data.append(neighbor_data)
        
        if possible_next_states_data:
            return random.choice(possible_next_states_data)
    
    return [row[:] for row in state_data] 

def genetic_algorithm(initial_state, 
                      heuristic_func_for_fitness=manhattan_distance, 
                      population_size=100, 
                      generations=200, 
                      mutation_rate=0.1, 
                      elitism_rate=0.1, 
                      tournament_size_for_selection=5):
    """
    Thuật toán Di truyền cho 8-puzzle.
    initial_state: Trạng thái bắt đầu (Buzzle object hoặc data).
    heuristic_func_for_fitness: Hàm heuristic dùng để tính fitness (ví dụ: manhattan_distance).
    population_size: Kích thước quần thể.
    generations: Số thế hệ tối đa.
    mutation_rate: Tỷ lệ đột biến.
    elitism_rate: Tỷ lệ cá thể ưu tú được giữ lại cho thế hệ sau.
    tournament_size_for_selection: Kích thước giải đấu cho việc chọn cha mẹ.

    Trả về: (best_solution_data_if_goal, total_fitness_evaluations, final_population_size)
             best_solution_data_if_goal là data của goal state nếu tìm thấy, ngược lại None.
    """
    initial_puzzle_data_list = initial_state.data if isinstance(initial_state, Buzzle) else initial_state
    
    population_data = generate_ga_population(population_size, initial_puzzle_data_list, ensure_solvable=True)

    if not population_data:
        # print("GA Error: Initial population is empty. Aborting.")
        return None, 0, 0

    total_fitness_evaluations = 0
    best_solution_overall_data = None
    best_fitness_overall = -float('inf') 

    current_fitness_scores = [genetic_algorithm_objective_function(ind_data, heuristic_func_for_fitness) for ind_data in population_data]
    total_fitness_evaluations += len(population_data)
    
    for i in range(len(population_data)):
        if current_fitness_scores[i] > best_fitness_overall:
            best_fitness_overall = current_fitness_scores[i]
            best_solution_overall_data = population_data[i]
        if Buzzle(population_data[i]).is_goal():
            return population_data[i], total_fitness_evaluations, len(population_data)

    for gen in range(generations):
        if best_solution_overall_data and Buzzle(best_solution_overall_data).is_goal():
            break 

        # Fitness cho population_data hiện tại đã được tính ở vòng lặp trước hoặc khởi tạo
        # (trừ lần đầu tiên sau khởi tạo, đã tính ở trên)
        if gen > 0: # Tính lại fitness cho quần thể mới từ thế hệ trước
             current_fitness_scores = [genetic_algorithm_objective_function(ind_data, heuristic_func_for_fitness) for ind_data in population_data]
             total_fitness_evaluations += len(population_data)

             # Cập nhật lại best_solution_overall dựa trên fitness mới tính
             for i in range(len(population_data)):
                if current_fitness_scores[i] > best_fitness_overall:
                    best_fitness_overall = current_fitness_scores[i]
                    best_solution_overall_data = population_data[i]
                    if Buzzle(best_solution_overall_data).is_goal(): break 
             if best_solution_overall_data and Buzzle(best_solution_overall_data).is_goal(): break

        next_generation_data = []
        
        num_elites = int(elitism_rate * len(population_data))
        if num_elites > 0 and population_data:
            sorted_population_indices = sorted(range(len(population_data)), key=lambda k: current_fitness_scores[k], reverse=True)
            for i in range(min(num_elites, len(sorted_population_indices))):
                elite_idx = sorted_population_indices[i]
                next_generation_data.append(population_data[elite_idx])

        num_offspring_needed = population_size - len(next_generation_data)
        
        if num_offspring_needed > 0 and population_data and current_fitness_scores :
            num_parents_to_select = num_offspring_needed 
            if num_parents_to_select % 2 != 0 and num_offspring_needed < population_size :
                if len(population_data) > num_parents_to_select : # Chỉ tăng nếu có đủ cá thể để chọn thêm
                    num_parents_to_select +=1
            
            # Đảm bảo num_parents_to_select không vượt quá số lượng cá thể có thể chọn
            num_parents_to_select = min(num_parents_to_select, len(population_data))
            
            parents_data = []
            if num_parents_to_select > 0:
                parents_data = select_parents_ga(population_data, current_fitness_scores, num_parents_to_select, tournament_size_for_selection)

            current_offspring_count = 0
            for i in range(0, len(parents_data), 2):
                if current_offspring_count >= num_offspring_needed:
                    break
                
                if i + 1 < len(parents_data): 
                    parent1 = parents_data[i]
                    parent2 = parents_data[i+1]
                    
                    child1_data, child2_data = crossover_ga(parent1, parent2)
                    
                    mutated_child1 = mutate_ga(child1_data, mutation_rate)
                    next_generation_data.append(mutated_child1)
                    current_offspring_count += 1

                    if current_offspring_count < num_offspring_needed:
                        mutated_child2 = mutate_ga(child2_data, mutation_rate)
                        next_generation_data.append(mutated_child2)
                        current_offspring_count += 1
                elif len(parents_data) > i and current_offspring_count < num_offspring_needed: # Xử lý cha/mẹ lẻ cuối cùng
                    # Đột biến và thêm trực tiếp nếu chỉ có 1 cha mẹ còn lại và cần thêm offspring
                    mutated_parent = mutate_ga(parents_data[i], mutation_rate)
                    next_generation_data.append(mutated_parent)
                    current_offspring_count += 1
        
        population_data = next_generation_data
        if not population_data:
            break 

    final_best_solution_data = None
    if best_solution_overall_data and Buzzle(best_solution_overall_data).is_goal():
        final_best_solution_data = best_solution_overall_data
        
    return final_best_solution_data, total_fitness_evaluations, len(population_data) 