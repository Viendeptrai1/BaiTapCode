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

    # (f_score, tie_breaker, g_score, state_data, path_of_moves)
    frontier = [(manhattan_distance(initial_state), 0, 0, initial_state.data, [])]
    # explored lưu state_tuple -> g_score
    explored = {tuple(map(tuple, initial_state.data)): 0}
    nodes_expanded = 0
    max_frontier_size = 1
    counter = 1 # tie breaker

    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        _, _, g_score, current_data, path = heapq.heappop(frontier)
        nodes_expanded += 1

        current_data_tuple = tuple(map(tuple, current_data))

        # Nếu đã tìm thấy đường đi tốt hơn tới current_data (do cập nhật trong heap)
        if g_score > explored.get(current_data_tuple, float('inf')):
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
                new_g_score = g_score + 1
                new_data_tuple = tuple(map(tuple, new_data))

                if new_g_score < explored.get(new_data_tuple, float('inf')):
                    explored[new_data_tuple] = new_g_score
                    f_score = new_g_score + manhattan_distance(Buzzle(new_data))
                    new_path = path + [move]
                    heapq.heappush(frontier, (f_score, counter, new_g_score, new_data, new_path))
                    counter += 1

    return [], nodes_expanded, max_frontier_size # Không tìm thấy

def greedy(initial_state):
    """Greedy Best-First Search với Manhattan distance"""
    if not is_solvable(initial_state.data):
        print("Greedy: Trạng thái không giải được.")
        return [], 0, 0

    # (h_score, tie_breaker, state_data, path_of_moves)
    frontier = [(manhattan_distance(initial_state), 0, initial_state.data, [])]
    # explored lưu chỉ state_tuple để tránh chu trình, không cần cost
    explored = {tuple(map(tuple, initial_state.data))}
    nodes_expanded = 0
    max_frontier_size = 1
    counter = 1 # tie breaker

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
                    h_score = manhattan_distance(Buzzle(new_data))
                    new_path = path + [move]
                    heapq.heappush(frontier, (h_score, counter, new_data, new_path))
                    counter += 1

    return [], nodes_expanded, max_frontier_size # Không tìm thấy

# Helper for IDA*
def _ida_search(current_data_tuple, g, bound, path_moves, visited_in_path):
    """
    Hàm đệ quy cho IDA*.
    current_data_tuple: Trạng thái hiện tại (dưới dạng tuple).
    g: Chi phí từ trạng thái đầu đến trạng thái hiện tại.
    bound: Ngưỡng f-cost hiện tại.
    path_moves: Danh sách các nước đi từ trạng thái đầu đến hiện tại.
    visited_in_path: Set các trạng thái (tuple) trong đường đi hiện tại để tránh chu trình.
    Trả về: (found, min_f_cost_exceeding_bound, path_moves_if_found, nodes_expanded_in_this_path)
    """
    current_buzzle = Buzzle(list(map(list, current_data_tuple))) # Chuyển tuple về list để tạo Buzzle
    h = manhattan_distance(current_buzzle)
    f = g + h

    nodes_expanded_here = 1 # Nút hiện tại được "mở rộng" (đánh giá)

    if f > bound:
        return False, f, [], nodes_expanded_here # Trả về f mới để cập nhật bound

    if current_buzzle.is_goal():
        return True, f, path_moves, nodes_expanded_here

    min_f_exceeding = float('inf')

    # Duyệt các nước đi theo một thứ tự nhất định (ví dụ: U, D, L, R)
    # Có thể thử các thứ tự khác nhau để xem ảnh hưởng
    for move in ["up", "down", "left", "right"]:
        success, new_data = create_new_state(list(map(list,current_data_tuple)), move)
        if success:
            new_data_tuple = tuple(map(tuple, new_data))
            if new_data_tuple not in visited_in_path:
                visited_in_path.add(new_data_tuple)
                new_path_moves = path_moves + [move]
                found, new_bound_candidate, result_path, nodes_child = _ida_search(
                    new_data_tuple, g + 1, bound, new_path_moves, visited_in_path
                )
                nodes_expanded_here += nodes_child
                if found:
                    return True, new_bound_candidate, result_path, nodes_expanded_here
                min_f_exceeding = min(min_f_exceeding, new_bound_candidate)
                visited_in_path.remove(new_data_tuple) # Backtrack

    return False, min_f_exceeding, [], nodes_expanded_here

def idastar(initial_state):
    """Iterative Deepening A* Search"""
    if not is_solvable(initial_state.data):
        print("IDA*: Trạng thái không giải được.")
        return [], 0, 0

    bound = manhattan_distance(initial_state)
    initial_data_tuple = tuple(map(tuple, initial_state.data))
    total_nodes_expanded = 0

    while True:
        # Bắt đầu tìm kiếm với bound hiện tại
        # visited_in_path để tránh chu trình trong một lần lặp của _ida_search
        found, new_bound, path_moves, nodes_iter = _ida_search(
            initial_data_tuple, 0, bound, [], {initial_data_tuple}
        )
        total_nodes_expanded += nodes_iter

        if found:
            # Tái tạo path (move, state_data) từ path_moves
            final_path = []
            temp_state = initial_state.data
            for move in path_moves:
                success, next_state = create_new_state(temp_state, move)
                if success:
                    final_path.append((move, next_state))
                    temp_state = next_state
                else:
                    print("IDA* Error: Invalid move in reconstructed path")
                    # Should not happen if _ida_search is correct
                    return [], total_nodes_expanded, 0 # max_frontier is not tracked here
            return final_path, total_nodes_expanded, 0 # max_frontier is not tracked by IDA*

        if new_bound == float('inf'): # Không tìm thấy nút nào nữa
            return [], total_nodes_expanded, 0 # Không tìm thấy giải pháp

        bound = new_bound # Cập nhật bound cho lần lặp tiếp theo

# sys.setrecursionlimit(2000) # Tăng giới hạn đệ quy nếu cần cho IDA* hoặc DFS sâu

