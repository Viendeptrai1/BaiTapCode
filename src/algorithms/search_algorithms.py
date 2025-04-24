from collections import deque
import heapq
import random
import math
import sys # Import sys để điều chỉnh giới hạn đệ quy

# Import các thành phần cần thiết từ buzzle_logic
from src.core.buzzle_logic import Buzzle, create_new_state, manhattan_distance, is_solvable

# --- Thuật toán tìm kiếm không thông tin ---

def bfs(initial_state):
    """Breadth First Search"""
    # initial_state là một đối tượng Buzzle
    if not is_solvable(initial_state.data):
         print("BFS: Trạng thái không giải được.")
         return [], 0, 0 # Thêm kiểm tra solvability

    frontier = deque([(initial_state.data, [])])  # (state_data, path_of_moves)
    # Chuyển state_data thành tuple để hashable cho set
    explored = {tuple(map(tuple, initial_state.data))}
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        current_data, path = frontier.popleft()
        nodes_expanded += 1

        current_buzzle = Buzzle(current_data)
        if current_buzzle.is_goal():
            # Trả về path of (move, new_state_data)
            final_path = []
            temp_state = initial_state.data
            for move in path:
                success, next_state = create_new_state(temp_state, move)
                if success:
                     final_path.append((move, next_state))
                     temp_state = next_state
                else: # Lỗi logic
                     print("BFS Error: Invalid move in reconstructed path")
                     return [], nodes_expanded, max_frontier_size
            return final_path, nodes_expanded, max_frontier_size

        for move in ["up", "down", "left", "right"]:
            success, new_data = create_new_state(current_data, move)
            new_data_tuple = tuple(map(tuple, new_data)) if success else None

            if success and new_data_tuple not in explored:
                explored.add(new_data_tuple)
                new_path = path + [move] # Chỉ lưu trữ các bước di chuyển
                frontier.append((new_data, new_path))

    return [], nodes_expanded, max_frontier_size # Không tìm thấy lời giải

def dfs(initial_state, max_depth=30):
    """Depth First Search with depth limit"""
    if not is_solvable(initial_state.data):
        print("DFS: Trạng thái không giải được.")
        return [], 0, 0

    frontier = [(initial_state.data, [], 0)]  # (state_data, path_of_moves, depth)
    # Chuyển state_data thành tuple để hashable cho dict explored (lưu depth)
    explored = {tuple(map(tuple, initial_state.data)): 0}
    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        current_data, path, depth = frontier.pop()
        nodes_expanded += 1

        current_buzzle = Buzzle(current_data)
        if current_buzzle.is_goal():
            # Tái tạo path of (move, new_state_data)
            final_path = []
            temp_state = initial_state.data
            for move in path:
                success, next_state = create_new_state(temp_state, move)
                if success:
                    final_path.append((move, next_state))
                    temp_state = next_state
                else:
                    print("DFS Error: Invalid move in reconstructed path")
                    return [], nodes_expanded, max_frontier_size
            return final_path, nodes_expanded, max_frontier_size

        if depth >= max_depth:
            continue

        # DFS thêm nút con theo thứ tự ngược để duyệt trái sang phải (nếu cần)
        for move in reversed(["up", "down", "left", "right"]):
            success, new_data = create_new_state(current_data, move)
            new_data_tuple = tuple(map(tuple, new_data)) if success else None
            new_depth = depth + 1

            if success:
                 # Chỉ thêm vào frontier nếu chưa khám phá hoặc tìm thấy đường đi ngắn hơn
                 if new_data_tuple not in explored or new_depth < explored[new_data_tuple]:
                      explored[new_data_tuple] = new_depth
                      new_path = path + [move]
                      frontier.append((new_data, new_path, new_depth))

    return [], nodes_expanded, max_frontier_size # Không tìm thấy

def ucs(initial_state):
    """Uniform Cost Search"""
    if not is_solvable(initial_state.data):
        print("UCS: Trạng thái không giải được.")
        return [], 0, 0

    # (cost, tie_breaker, state_data, path_of_moves)
    frontier = [(0, 0, initial_state.data, [])]
    # explored lưu state_tuple -> cost
    explored = {tuple(map(tuple, initial_state.data)): 0}
    nodes_expanded = 0
    max_frontier_size = 1
    counter = 1  # tie breaker

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        cost, _, current_data, path = heapq.heappop(frontier)
        nodes_expanded += 1

        current_data_tuple = tuple(map(tuple, current_data))
        # Skip nếu đã có đường đi tốt hơn được tìm thấy trước đó
        if cost > explored.get(current_data_tuple, float('inf')):
            continue

        current_buzzle = Buzzle(current_data)
        if current_buzzle.is_goal():
            # Tái tạo path of (move, new_state_data)
            final_path = []
            temp_state = initial_state.data
            for move in path:
                success, next_state = create_new_state(temp_state, move)
                if success:
                    final_path.append((move, next_state))
                    temp_state = next_state
                else:
                    print("UCS Error: Invalid move in reconstructed path")
                    return [], nodes_expanded, max_frontier_size
            return final_path, nodes_expanded, max_frontier_size

        for move in ["up", "down", "left", "right"]:
            success, new_data = create_new_state(current_data, move)
            if success:
                new_cost = cost + 1
                new_data_tuple = tuple(map(tuple, new_data))

                # Chỉ thêm vào frontier nếu chưa khám phá hoặc tìm thấy đường đi rẻ hơn
                if new_data_tuple not in explored or new_cost < explored[new_data_tuple]:
                    explored[new_data_tuple] = new_cost
                    new_path = path + [move]
                    heapq.heappush(frontier, (new_cost, counter, new_data, new_path))
                    counter += 1

    return [], nodes_expanded, max_frontier_size # Không tìm thấy

def dfs_limited(initial_state_data, initial_path, depth_limit, explored_global):
    """
    DFS với giới hạn độ sâu, dùng cho IDS.
    Tránh explored cục bộ, sử dụng explored_global để chia sẻ giữa các lần lặp.
    Trả về (found, path_of_moves, nodes_expanded_in_iter, max_frontier_in_iter)
    """
    # (state_data, path_of_moves, depth)
    frontier = [(initial_state_data, initial_path, 0)]
    # explored cục bộ cho lần lặp này để tránh chu trình trong lần lặp
    explored_local = {tuple(map(tuple, initial_state_data)): 0}

    nodes_expanded = 0
    max_frontier_size = 1

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        current_data, path, depth = frontier.pop()
        nodes_expanded += 1

        current_buzzle = Buzzle(current_data)
        if current_buzzle.is_goal():
            return True, path, nodes_expanded, max_frontier_size

        if depth >= depth_limit:
            continue

        # DFS thêm nút con theo thứ tự ngược
        for move in reversed(["up", "down", "left", "right"]):
            success, new_data = create_new_state(current_data, move)
            if success:
                new_depth = depth + 1
                new_data_tuple = tuple(map(tuple, new_data))

                # Kiểm tra explored cục bộ và global
                # Chỉ thêm nếu chưa có trong explored cục bộ HOẶC tìm thấy đường ngắn hơn trong explored cục bộ
                # Và cũng kiểm tra explored global (nếu có) để tối ưu
                current_local_depth = explored_local.get(new_data_tuple, float('inf'))

                if new_depth < current_local_depth:
                     # Kiểm tra thêm explored_global nếu cần
                     # current_global_depth = explored_global.get(new_data_tuple, float('inf'))
                     # if new_depth < current_global_depth:
                     #      explored_global[new_data_tuple] = new_depth # Cập nhật global

                     explored_local[new_data_tuple] = new_depth
                     new_path = path + [move]
                     frontier.append((new_data, new_path, new_depth))


    return False, [], nodes_expanded, max_frontier_size # Không tìm thấy trong giới hạn này

def ids(initial_state):
    """Iterative Deepening Search"""
    if not is_solvable(initial_state.data):
        print("IDS: Trạng thái không giải được.")
        return [], 0, 0

    total_nodes = 0
    max_fringe_overall = 0
    explored_global = {} # Có thể dùng để lưu độ sâu tốt nhất đã thấy

    for depth in range(50):  # Giới hạn độ sâu tối đa = 50
        # explored_global được truyền vào để có thể tối ưu giữa các lần lặp (tùy chọn)
        found, path_moves, nodes_iter, fringe_iter = dfs_limited(
            initial_state.data, [], depth, explored_global
        )
        total_nodes += nodes_iter
        max_fringe_overall = max(max_fringe_overall, fringe_iter)

        if found:
             # Tái tạo path of (move, new_state_data)
            final_path = []
            temp_state = initial_state.data
            for move in path_moves:
                success, next_state = create_new_state(temp_state, move)
                if success:
                    final_path.append((move, next_state))
                    temp_state = next_state
                else:
                    print("IDS Error: Invalid move in reconstructed path")
                    return [], total_nodes, max_fringe_overall
            return final_path, total_nodes, max_fringe_overall

    return [], total_nodes, max_fringe_overall # Không tìm thấy trong giới hạn

# --- Thuật toán tìm kiếm có thông tin ---

def astar(initial_state):
    """A* Search với Manhattan distance"""
    if not is_solvable(initial_state.data):
        print("A*: Trạng thái không giải được.")
        return [], 0, 0

    initial_buzzle = Buzzle(initial_state.data)
    start_h = manhattan_distance(initial_buzzle)
    # (f_value, tie_breaker, state_data, path_of_moves, g_value)
    frontier = [(start_h, 0, initial_state.data, [], 0)]
    # explored lưu state_tuple -> g_value
    explored = {tuple(map(tuple, initial_state.data)): 0}
    nodes_expanded = 0
    max_frontier_size = 1
    counter = 1  # tie breaker

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        _, _, current_data, path, g_value = heapq.heappop(frontier)
        nodes_expanded += 1

        current_data_tuple = tuple(map(tuple, current_data))
        # Skip nếu đã có đường đi tốt hơn (rẻ hơn) được tìm thấy trước đó
        if g_value > explored.get(current_data_tuple, float('inf')):
            continue

        current_buzzle = Buzzle(current_data)
        if current_buzzle.is_goal():
            # Tái tạo path of (move, new_state_data)
            final_path = []
            temp_state = initial_state.data
            for move in path:
                success, next_state = create_new_state(temp_state, move)
                if success:
                    final_path.append((move, next_state))
                    temp_state = next_state
                else:
                    print("A* Error: Invalid move in reconstructed path")
                    return [], nodes_expanded, max_frontier_size
            return final_path, nodes_expanded, max_frontier_size

        for move in ["up", "down", "left", "right"]:
            success, new_data = create_new_state(current_data, move)
            if success:
                new_g = g_value + 1
                new_data_tuple = tuple(map(tuple, new_data))

                # Chỉ xem xét nếu chưa khám phá hoặc tìm thấy đường đi rẻ hơn
                if new_data_tuple not in explored or new_g < explored[new_data_tuple]:
                    explored[new_data_tuple] = new_g
                    new_buzzle = Buzzle(new_data)
                    h_value = manhattan_distance(new_buzzle)
                    f_value = new_g + h_value
                    new_path = path + [move]
                    heapq.heappush(frontier, (f_value, counter, new_data, new_path, new_g))
                    counter += 1

    return [], nodes_expanded, max_frontier_size # Không tìm thấy

def greedy(initial_state):
    """Greedy Best-First Search - chỉ sử dụng heuristic"""
    if not is_solvable(initial_state.data):
        print("Greedy: Trạng thái không giải được.")
        return [], 0, 0

    initial_buzzle = Buzzle(initial_state.data)
    start_h = manhattan_distance(initial_buzzle)
    # (h_value, tie_breaker, state_data, path_of_moves)
    frontier = [(start_h, 0, initial_state.data, [])]
    # explored chỉ cần lưu state_tuple đã thăm
    explored = {tuple(map(tuple, initial_state.data))}
    nodes_expanded = 0
    max_frontier_size = 1
    counter = 1

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        _, _, current_data, path = heapq.heappop(frontier)
        nodes_expanded += 1

        current_buzzle = Buzzle(current_data)
        if current_buzzle.is_goal():
             # Tái tạo path of (move, new_state_data)
            final_path = []
            temp_state = initial_state.data
            for move in path:
                success, next_state = create_new_state(temp_state, move)
                if success:
                    final_path.append((move, next_state))
                    temp_state = next_state
                else:
                    print("Greedy Error: Invalid move in reconstructed path")
                    return [], nodes_expanded, max_frontier_size
            return final_path, nodes_expanded, max_frontier_size

        for move in ["up", "down", "left", "right"]:
            success, new_data = create_new_state(current_data, move)
            if success:
                new_data_tuple = tuple(map(tuple, new_data))
                if new_data_tuple not in explored:
                    explored.add(new_data_tuple)
                    new_buzzle = Buzzle(new_data)
                    h_value = manhattan_distance(new_buzzle)
                    new_path = path + [move]
                    heapq.heappush(frontier, (h_value, counter, new_data, new_path))
                    counter += 1

    return [], nodes_expanded, max_frontier_size # Không tìm thấy

def _ida_search(current_data_tuple, g, bound, path_moves, visited_in_path):
    """
    Hàm đệ quy cho IDA*.
    Trả về (new_bound, found, final_path_moves, nodes_in_subtree, max_fringe_in_subtree).
    Sử dụng visited_in_path để tránh chu trình trong nhánh hiện tại.
    """
    nodes_expanded = 1
    max_fringe = 1 # Kích thước fringe cục bộ của nhánh này

    current_buzzle = Buzzle(list(map(list, current_data_tuple))) # Chuyển tuple về list để dùng Buzzle
    current_h = manhattan_distance(current_buzzle)
    f = g + current_h

    if f > bound:
        return f, False, [], nodes_expanded, max_fringe # Trả về f để cập nhật bound

    if current_buzzle.is_goal():
        return f, True, path_moves, nodes_expanded, max_fringe

    min_cost_above_bound = float('inf')
    found_in_subtree = False
    best_path_from_here = []

    # Thêm vào tập visited của nhánh hiện tại
    visited_in_path.add(current_data_tuple)

    successors = []
    for move in ["up", "down", "left", "right"]:
        success, new_data = create_new_state(list(map(list, current_data_tuple)), move)
        if success:
            new_data_tuple = tuple(map(tuple, new_data))
            if new_data_tuple not in visited_in_path: # Chỉ xét nếu chưa có trong đường đi hiện tại
                successors.append((move, new_data_tuple))

    max_fringe = max(max_fringe, len(successors)) # Cập nhật max fringe

    for move, next_data_tuple in successors:
        new_g = g + 1
        new_path_moves = path_moves + [move]

        # Gọi đệ quy, truyền bản sao của visited_in_path
        cost, found, result_path, nodes_subtree, fringe_subtree = _ida_search(
            next_data_tuple, new_g, bound, new_path_moves, visited_in_path.copy()
        )

        nodes_expanded += nodes_subtree
        max_fringe = max(max_fringe, fringe_subtree) # Cập nhật max fringe từ các nhánh con

        if found:
            # Tìm thấy ở nhánh con, trả về luôn
            # visited_in_path.remove(current_data_tuple) # Xóa khi backtrack (không cần thiết vì truyền copy)
            return cost, True, result_path, nodes_expanded, max_fringe

        # Nếu không tìm thấy, cập nhật chi phí nhỏ nhất vượt ngưỡng
        min_cost_above_bound = min(min_cost_above_bound, cost)

    # visited_in_path.remove(current_data_tuple) # Xóa khi backtrack (không cần thiết vì truyền copy)
    # Không tìm thấy trong bất kỳ nhánh con nào
    return min_cost_above_bound, False, [], nodes_expanded, max_fringe


def idastar(initial_state):
    """Iterative Deepening A*"""
    if not is_solvable(initial_state.data):
        print("IDA*: Trạng thái không giải được.")
        return [], 0, 0

    initial_buzzle = Buzzle(initial_state.data)
    bound = manhattan_distance(initial_buzzle)
    initial_data_tuple = tuple(map(tuple, initial_state.data))

    nodes_expanded_total = 0
    max_frontier_total = 0

    while True:
        # Bắt đầu tìm kiếm từ trạng thái ban đầu với ngưỡng 'bound'
        # visited_in_path là set rỗng ban đầu
        cost, found, path_moves, nodes_iter, fringe_iter = _ida_search(
            initial_data_tuple, 0, bound, [], set()
        )

        nodes_expanded_total += nodes_iter
        max_frontier_total = max(max_frontier_total, fringe_iter)

        if found:
            # Tái tạo path of (move, new_state_data)
            final_path = []
            temp_state = initial_state.data
            for move in path_moves:
                success, next_state = create_new_state(temp_state, move)
                if success:
                    final_path.append((move, next_state))
                    temp_state = next_state
                else:
                    print("IDA* Error: Invalid move in reconstructed path")
                    return [], nodes_expanded_total, max_frontier_total
            return final_path, nodes_expanded_total, max_frontier_total

        if cost == float('inf'):  # Không tìm thấy nút nào nữa -> không có lời giải
            return [], nodes_expanded_total, max_frontier_total

        bound = cost  # Cập nhật ngưỡng cho lần lặp tiếp theo

# --- Thuật toán tìm kiếm cục bộ ---

def hill_climbing_max(initial_state):
    """Hill Climbing search algorithm that always selects the best move"""
    current_data = initial_state.data
    current_buzzle = Buzzle(current_data)
    current_h = manhattan_distance(current_buzzle)

    path_of_states = [current_data] # Lưu trữ dãy trạng thái đã đi qua
    nodes_evaluated = 1 # Đánh giá trạng thái ban đầu
    max_neighbors_at_step = 0

    while True:
        if current_buzzle.is_goal():
            break # Đã đạt đích

        best_h = current_h
        best_neighbor_data = None
        neighbors_evaluated_this_step = 0

        possible_moves = []
        for move in ["up", "down", "left", "right"]:
            success, neighbor_data = create_new_state(current_data, move)
            if success:
                possible_moves.append((move, neighbor_data))

        max_neighbors_at_step = max(max_neighbors_at_step, len(possible_moves))

        for move, neighbor_data in possible_moves:
            neighbors_evaluated_this_step += 1
            neighbor_buzzle = Buzzle(neighbor_data)
            neighbor_h = manhattan_distance(neighbor_buzzle)

            if neighbor_h < best_h:
                best_h = neighbor_h
                best_neighbor_data = neighbor_data

        nodes_evaluated += neighbors_evaluated_this_step

        # Nếu không tìm thấy nước đi tốt hơn -> local minimum/plateau
        if best_neighbor_data is None:
            break

        # Di chuyển đến trạng thái tốt nhất
        current_data = best_neighbor_data
        current_buzzle = Buzzle(current_data)
        current_h = best_h
        path_of_states.append(current_data)

    # Tái tạo path (move, state) từ path_of_states
    final_path = []
    if len(path_of_states) > 1:
        for i in range(len(path_of_states) - 1):
            # Tìm move giữa state[i] và state[i+1] (hơi tốn kém)
            prev_state = path_of_states[i]
            next_state = path_of_states[i+1]
            found_move = None
            for move in ["up", "down", "left", "right"]:
                success, potential_next = create_new_state(prev_state, move)
                if success and potential_next == next_state:
                    found_move = move
                    break
            if found_move:
                final_path.append((found_move, next_state))
            else:
                 print("HillClimbing Error: Could not reconstruct move.")
                 # Có thể trả về lỗi hoặc path hiện tại
                 # return [], nodes_evaluated, max_neighbors_at_step

    # Kiểm tra xem trạng thái cuối có phải là goal không
    if Buzzle(current_data).is_goal():
        return final_path, nodes_evaluated, max_neighbors_at_step
    else:
        # Không tìm thấy lời giải (kẹt ở local minimum)
        # Trả về path rỗng hoặc path đã đi được tùy yêu cầu
        return [], nodes_evaluated, max_neighbors_at_step


def hill_climbing_random(initial_state, max_sidesteps=10):
    """Hill Climbing with random sidesteps when stuck"""
    current_data = initial_state.data
    current_buzzle = Buzzle(current_data)
    current_h = manhattan_distance(current_buzzle)

    path_of_states = [current_data]
    nodes_evaluated = 1
    max_neighbors_at_step = 0
    sidesteps_taken = 0

    while True:
        if current_buzzle.is_goal():
            break

        best_h = current_h
        best_neighbor_data = None
        equal_neighbors_data = [] # Lưu các trạng thái có h bằng current_h
        neighbors_evaluated_this_step = 0

        possible_moves = []
        for move in ["up", "down", "left", "right"]:
            success, neighbor_data = create_new_state(current_data, move)
            if success:
                possible_moves.append((move, neighbor_data))

        max_neighbors_at_step = max(max_neighbors_at_step, len(possible_moves))

        for move, neighbor_data in possible_moves:
            neighbors_evaluated_this_step += 1
            neighbor_buzzle = Buzzle(neighbor_data)
            neighbor_h = manhattan_distance(neighbor_buzzle)

            if neighbor_h < best_h:
                best_h = neighbor_h
                best_neighbor_data = neighbor_data
                equal_neighbors_data = [] # Reset khi tìm thấy cái tốt hơn
            elif neighbor_h == current_h: # Chỉ xét bằng với H hiện tại, không phải best_h
                equal_neighbors_data.append(neighbor_data)

        nodes_evaluated += neighbors_evaluated_this_step

        next_data = None
        if best_neighbor_data is not None:
            # Ưu tiên nước đi tốt hơn
            next_data = best_neighbor_data
            sidesteps_taken = 0 # Reset sidesteps
        elif equal_neighbors_data and sidesteps_taken < max_sidesteps:
            # Nếu không có nước đi tốt hơn và còn lượt đi ngang -> chọn ngẫu nhiên
            next_data = random.choice(equal_neighbors_data)
            sidesteps_taken += 1
        else:
            # Không có nước đi tốt hơn, hết lượt đi ngang -> dừng
            break

        # Di chuyển đến trạng thái tiếp theo
        current_data = next_data
        current_buzzle = Buzzle(current_data)
        current_h = manhattan_distance(current_buzzle) # Cập nhật lại h cho trạng thái mới
        path_of_states.append(current_data)


    # Tái tạo path (move, state)
    final_path = []
    if len(path_of_states) > 1:
        for i in range(len(path_of_states) - 1):
            prev_state = path_of_states[i]
            next_state = path_of_states[i+1]
            found_move = None
            for move in ["up", "down", "left", "right"]:
                success, potential_next = create_new_state(prev_state, move)
                if success and potential_next == next_state:
                    found_move = move
                    break
            if found_move:
                 # Thêm tiền tố nếu là random step? Không cần thiết lắm
                 # move_label = f"sidestep-{found_move}" if prev_h == next_h else found_move
                 final_path.append((found_move, next_state))
            else:
                 print("HillClimbingRandom Error: Could not reconstruct move.")

    if Buzzle(current_data).is_goal():
        return final_path, nodes_evaluated, max_neighbors_at_step
    else:
        return [], nodes_evaluated, max_neighbors_at_step


def simulated_annealing(initial_state, initial_temp=100, cooling_rate=0.995, min_temp=0.1, max_iterations=10000):
    """Simulated Annealing search algorithm"""
    current_data = initial_state.data
    current_buzzle = Buzzle(current_data)
    current_h = manhattan_distance(current_buzzle)

    best_data = current_data
    best_h = current_h

    # SA không lưu path, chỉ lưu trạng thái tốt nhất tìm được
    nodes_evaluated = 1 # Đánh giá trạng thái ban đầu
    max_neighbors_considered = 4 # Luôn là 4

    temp = initial_temp
    iterations = 0

    while temp > min_temp and iterations < max_iterations:
        iterations += 1

        if current_buzzle.is_goal():
            best_data = current_data # Cập nhật best nếu đạt goal
            best_h = 0
            break # Dừng sớm nếu tìm thấy goal

        # Chọn ngẫu nhiên một trạng thái lân cận hợp lệ
        possible_moves = []
        for move in ["up", "down", "left", "right"]:
            success, neighbor_data = create_new_state(current_data, move)
            if success:
                possible_moves.append(neighbor_data)

        if not possible_moves:
            break # Không còn nước đi nào

        next_data = random.choice(possible_moves)
        next_buzzle = Buzzle(next_data)
        next_h = manhattan_distance(next_buzzle)
        nodes_evaluated += 1 # Đánh giá trạng thái mới

        delta_e = next_h - current_h

        # Nếu trạng thái mới tốt hơn, luôn di chuyển
        if delta_e < 0:
            current_data = next_data
            current_h = next_h
            current_buzzle = next_buzzle
            # Cập nhật trạng thái tốt nhất nếu cần
            if current_h < best_h:
                best_h = current_h
                best_data = current_data
        # Nếu trạng thái mới tệ hơn, di chuyển với xác suất nhất định
        else:
            try:
                probability = math.exp(-delta_e / temp)
                if random.random() < probability:
                    current_data = next_data
                    current_h = next_h
                    current_buzzle = next_buzzle
            except OverflowError: # Tránh lỗi khi delta_e lớn và temp nhỏ
                pass

        # Giảm nhiệt độ
        temp *= cooling_rate

    # Trả về kết quả dựa trên trạng thái tốt nhất tìm được
    # Path luôn rỗng vì SA không tối ưu đường đi
    if Buzzle(best_data).is_goal():
         return [], nodes_evaluated, max_neighbors_considered
    else: # Không tìm thấy lời giải (hoặc không đạt goal state)
         # Có thể trả về trạng thái tốt nhất tìm được nếu muốn, nhưng giao diện đang mong path
         return [], nodes_evaluated, max_neighbors_considered

# --- Thuật toán Tiến hóa (Genetic Algorithm) ---

def calculate_fitness(state_data):
    """Hàm đánh giá độ thích nghi (fitness). Giá trị càng cao càng tốt."""
    # Cách 1: Số ô đúng vị trí (cao hơn là tốt hơn)
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    correct_tiles = 0
    for r in range(3):
        for c in range(3):
            # Không tính ô trống
            if state_data[r][c] != 0 and state_data[r][c] == goal[r][c]:
                correct_tiles += 1
    return correct_tiles

    # Cách 2: Nghịch đảo Manhattan distance + 1 (cao hơn là tốt hơn)
    # dist = manhattan_distance(Buzzle(state_data))
    # return 1 / (1 + dist)


def generate_initial_population(initial_state_data, size=100):
    """
    Tạo quần thể ban đầu gồm các trạng thái ngẫu nhiên hợp lệ (solvable).
    Luôn bao gồm trạng thái ban đầu được cung cấp.
    """
    population_data = [initial_state_data] # Bắt đầu với trạng thái ban đầu
    population_tuples = {tuple(map(tuple, initial_state_data))} # Dùng set tuple để tránh trùng lặp

    # Tạo thêm các trạng thái ngẫu nhiên hợp lệ (solvable)
    attempts = 0
    max_attempts = size * 10 # Giới hạn số lần thử để tránh vòng lặp vô hạn

    while len(population_data) < size and attempts < max_attempts:
        attempts += 1
        numbers = list(range(9))
        random.shuffle(numbers)
        new_state_data = [numbers[i:i+3] for i in range(0, 9, 3)]
        if is_solvable(new_state_data):
            new_state_tuple = tuple(map(tuple, new_state_data))
            if new_state_tuple not in population_tuples:
                population_tuples.add(new_state_tuple)
                population_data.append(new_state_data)

    if len(population_data) < size:
         print(f"Warning: Could only generate {len(population_data)} unique solvable states for initial population.")

    return population_data # Trả về list các list data


def select_parents_tournament(population_data, fitness_scores, num_parents, tournament_size=5):
    """Chọn cha mẹ bằng Tournament Selection."""
    parents = []
    population_with_fitness = list(zip(population_data, fitness_scores))

    if not population_with_fitness: # Tránh lỗi nếu quần thể rỗng
        return []

    # Đảm bảo tournament_size không lớn hơn kích thước quần thể
    actual_tournament_size = min(tournament_size, len(population_with_fitness))
    if actual_tournament_size <= 0:
        return [] # Không thể chọn nếu tournament size <= 0

    for _ in range(num_parents):
        # Chọn ngẫu nhiên các cá thể cho tournament
        tournament = random.sample(population_with_fitness, actual_tournament_size)
        # Chọn cá thể tốt nhất trong tournament
        winner_data = max(tournament, key=lambda item: item[1])[0]
        parents.append(winner_data)
    return parents

def crossover_single_point(parent1_data, parent2_data):
    """
    Lai ghép Single-point crossover trên danh sách phẳng.
    Cần xử lý để đảm bảo con cái hợp lệ (đủ số 0-8, không trùng).
    """
    p1_flat = [num for row in parent1_data for num in row]
    p2_flat = [num for row in parent2_data for num in row]

    point = random.randint(1, 8) # Điểm cắt từ 1 đến 8

    # Tạo con 1
    child1_flat = p1_flat[:point]
    needed_from_p2 = [num for num in p2_flat if num not in child1_flat]
    child1_flat.extend(needed_from_p2)
    # Đảm bảo đủ 9 số (hiếm khi thiếu nếu logic đúng, nhưng kiểm tra cho chắc)
    if len(child1_flat) == 9:
         child1_data = [child1_flat[i:i+3] for i in range(0, 9, 3)]
         # Kiểm tra lại tính hợp lệ (đủ số 0-8)
         if set(child1_flat) != set(range(9)):
              child1_data = parent1_data # Trả về cha/mẹ nếu không hợp lệ
    else:
         child1_data = parent1_data # Trả về cha/mẹ nếu không hợp lệ

    # Tạo con 2 (tương tự, đảo vai trò p1, p2)
    child2_flat = p2_flat[:point]
    needed_from_p1 = [num for num in p1_flat if num not in child2_flat]
    child2_flat.extend(needed_from_p1)
    if len(child2_flat) == 9:
         child2_data = [child2_flat[i:i+3] for i in range(0, 9, 3)]
         if set(child2_flat) != set(range(9)):
              child2_data = parent2_data
    else:
         child2_data = parent2_data


    # Quan trọng: Đảm bảo con cái cũng solvable? (Tùy chọn, có thể làm chậm)
    # if not is_solvable(child1_data): child1_data = parent1_data
    # if not is_solvable(child2_data): child2_data = parent2_data

    return child1_data, child2_data


def mutate_swap(state_data, mutation_rate=0.1):
    """Đột biến bằng cách di chuyển ngẫu nhiên ô trống."""
    if random.random() < mutation_rate:
        possible_moves = []
        # Tìm các nước đi hợp lệ từ trạng thái hiện tại
        for move in ["up", "down", "left", "right"]:
            success, neighbor_data = create_new_state(state_data, move)
            if success:
                possible_moves.append(neighbor_data)
        if possible_moves:
            # Chọn một trạng thái hàng xóm ngẫu nhiên làm kết quả đột biến
            return random.choice(possible_moves)
    # Nếu không đột biến hoặc không có nước đi hợp lệ, trả về trạng thái gốc
    return state_data

def genetic_algorithm(initial_state, population_size=100, generations=200, mutation_rate=0.1, elitism_rate=0.1):
    """Genetic Algorithm for 8-puzzle."""
    population_data = generate_initial_population(initial_state.data, population_size)

    nodes_evaluated = 0 # Đếm số lần tính fitness
    max_pop_size = len(population_data) # Kích thước quần thể có thể thay đổi chút ít

    best_solution_data = None
    best_fitness = -1 # Giả sử fitness không âm

    # Tìm trạng thái tốt nhất trong quần thể ban đầu
    initial_fitness_scores = [calculate_fitness(ind) for ind in population_data]
    nodes_evaluated += len(population_data)
    initial_best_idx = max(range(len(initial_fitness_scores)), key=initial_fitness_scores.__getitem__)
    best_fitness = initial_fitness_scores[initial_best_idx]
    best_solution_data = population_data[initial_best_idx]

    for gen in range(generations):
        if Buzzle(best_solution_data).is_goal():
             # print(f"GA: Goal found in generation {gen}")
             break # Dừng sớm

        # --- Đánh giá fitness ---
        fitness_scores = [calculate_fitness(ind) for ind in population_data]
        nodes_evaluated += len(population_data)

        # --- Cập nhật lời giải tốt nhất toàn cục ---
        current_best_idx = max(range(len(fitness_scores)), key=fitness_scores.__getitem__)
        current_best_fitness = fitness_scores[current_best_idx]
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_solution_data = population_data[current_best_idx]
            # if Buzzle(best_solution_data).is_goal(): break # Kiểm tra lại

        next_population_data = []
        population_tuples = set() # Để kiểm tra trùng lặp trong thế hệ mới

        # --- Elitism: Giữ lại top cá thể tốt nhất ---
        num_elites = int(elitism_rate * len(population_data))
        # Sắp xếp population_data dựa trên fitness_scores giảm dần
        sorted_indices = sorted(range(len(fitness_scores)), key=lambda k: fitness_scores[k], reverse=True)
        for i in range(num_elites):
            elite_idx = sorted_indices[i]
            elite_data = population_data[elite_idx]
            elite_tuple = tuple(map(tuple, elite_data))
            if elite_tuple not in population_tuples:
                 next_population_data.append(elite_data)
                 population_tuples.add(elite_tuple)

        # --- Selection, Crossover, Mutation để tạo phần còn lại ---
        num_offspring_needed = population_size - len(next_population_data)
        offspring_data = []

        # Chọn cha mẹ (ví dụ: tournament) - cần chọn đủ để tạo offspring
        # Số cha mẹ cần là num_offspring_needed (vì mỗi cặp tạo 2 con)
        num_parents_to_select = num_offspring_needed + (num_offspring_needed % 2) # Đảm bảo số chẵn
        parents_data = select_parents_tournament(population_data, fitness_scores, num_parents_to_select)

        # Lai ghép và đột biến
        for i in range(0, len(parents_data), 2):
            if i + 1 < len(parents_data): # Đảm bảo có cặp
                parent1 = parents_data[i]
                parent2 = parents_data[i+1]
                child1_data, child2_data = crossover_single_point(parent1, parent2)
                offspring_data.append(mutate_swap(child1_data, mutation_rate))
                # Chỉ thêm con thứ 2 nếu còn chỗ
                if len(offspring_data) < num_offspring_needed:
                     offspring_data.append(mutate_swap(child2_data, mutation_rate))

        # Thêm con cái vào thế hệ mới (tránh trùng lặp)
        for child_data in offspring_data:
             if len(next_population_data) >= population_size:
                  break
             child_tuple = tuple(map(tuple, child_data))
             if child_tuple not in population_tuples:
                  next_population_data.append(child_data)
                  population_tuples.add(child_tuple)

        # Cập nhật quần thể
        population_data = next_population_data
        max_pop_size = max(max_pop_size, len(population_data)) # Cập nhật max size nếu cần

        if not population_data: # Nếu quần thể bị rỗng (lỗi?)
            print("GA Warning: Population became empty.")
            break

    # Kết thúc số thế hệ
    # Trả về path rỗng vì GA không tối ưu đường đi
    # Kết quả dựa trên best_solution_data tìm được
    if best_solution_data and Buzzle(best_solution_data).is_goal():
         return [], nodes_evaluated, max_pop_size
    else:
         # Không tìm thấy lời giải (goal state)
         return [], nodes_evaluated, max_pop_size

# --- CSP Backtracking Search Algorithm ---
def backtracking_search(initial_state):
    """
    CSP Backtracking Search for 8-puzzle.
    Variables: 9 positions (row,col)
    Domain: {0..8} for each variable
    Constraint: all values must be unique (all-different)
    Returns: path (list of (var, val)), nodes_expanded, max_fringe_size
    """
    variables = [(i, j) for i in range(3) for j in range(3)]
    domains = {var: set(range(9)) for var in variables}
    assignment = dict()
    nodes_expanded = 0
    max_fringe_size = 0
    result = []
    
    def is_complete(assignment):
        return len(assignment) == 9
    
    def select_unassigned_variable(assignment, variables):
        for var in variables:
            if var not in assignment:
                return var
        return None

    def is_consistent(var, value, assignment):
        return value not in assignment.values()

    def backtrack(assignment):
        nonlocal nodes_expanded, max_fringe_size
        if is_complete(assignment):
            return assignment
        var = select_unassigned_variable(assignment, variables)
        for value in domains[var]:
            if is_consistent(var, value, assignment):
                assignment[var] = value
                nodes_expanded += 1
                max_fringe_size = max(max_fringe_size, len(assignment))
                result.append((var, value))
                sol = backtrack(assignment)
                if sol is not None:
                    return sol
                result.pop()
                del assignment[var]
        return None

    solution = backtrack(assignment)
    # Convert assignment to board if found
    if solution:
        board = [[-1 for _ in range(3)] for _ in range(3)]
        for (i, j), val in solution.items():
            board[i][j] = val
        # Optionally: check is_solvable(board)
        # Return as a single step path for CSP
        return [((None, board))], nodes_expanded, max_fringe_size
    else:
        return [], nodes_expanded, max_fringe_size

