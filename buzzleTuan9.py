from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                           QGridLayout, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QLineEdit,
                           QMessageBox, QTextEdit, QSplitter, QProgressBar,
                           QGroupBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import sys
import random
from collections import deque
import heapq

# Classes and functions from Solve.py
class Buzzle:
    def __init__(self, data=None):
        if data is None:
            self.data = [[1, 2, 3],
                        [4, 5, 6],
                        [7, 8, 0]]
        else:
            self.data = [row[:] for row in data]

    def is_goal(self, goal_state=None):
        if goal_state is None:
            goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        return self.data == goal_state

    def print_state(self):
        print("Trang thai hien tai: ")
        for i in range(3):
            for j in range(3):
                print(self.data[i][j], end=" ")
            print("\n")
    
    def entry_state(self):
        """Get puzzle state from user input with error handling"""
        print("Nhập trạng thái (0-8, mỗi số xuất hiện đúng 1 lần, 0 đại diện cho ô trống):")
        print("Chọn cách nhập:")
        print("1. Nhập thủ công từng ô")
        print("2. Sử dụng trạng thái mẫu (để kiểm thử)")
        
        choice = input("Lựa chọn của bạn (1/2): ").strip()
        
        if choice == "2":
            # Sử dụng một trạng thái mẫu dễ giải
            self.data = [[1, 2, 3], [4, 0, 6], [7, 5, 8]]
            return
            
        # Danh sách để kiểm tra tính hợp lệ
        used_numbers = set()
        
        for i in range(3):
            for j in range(3):
                while True:
                    try:
                        x = int(input(f"Nhập giá trị cho ô [{i},{j}] (0-8): "))
                        if 0 <= x <= 8 and x not in used_numbers:
                            self.data[i][j] = x
                            used_numbers.add(x)
                            break
                        else:
                            if x in used_numbers:
                                print(f"Lỗi: Số {x} đã được sử dụng. Mỗi số chỉ được dùng một lần.")
                            else:
                                print("Lỗi: Vui lòng nhập số từ 0 đến 8.")
                    except ValueError:
                        print("Lỗi: Vui lòng nhập một số nguyên.")

    def get_blank_position(self):
        """Return position (row, col) of blank space (0)"""
        for i in range(3):
            for j in range(3):
                if self.data[i][j] == 0:
                    return (i, j)
        return (-1, -1)  # Should never happen in a valid puzzle

def create_new_state(data, move):
    """Tạo trạng thái mới từ data và move"""
    new_data = [row[:] for row in data]
    blank_pos = None
    
    # Tìm vị trí ô trống
    for i in range(3):
        for j in range(3):
            if new_data[i][j] == 0:
                blank_pos = (i, j)
                break
        if blank_pos:
            break
            
    if blank_pos is None:
        return False, None
        
    i, j = blank_pos
    if move == "up" and i > 0:
        new_data[i][j], new_data[i-1][j] = new_data[i-1][j], new_data[i][j]
        return True, new_data
    elif move == "down" and i < 2:
        new_data[i][j], new_data[i+1][j] = new_data[i+1][j], new_data[i][j]
        return True, new_data
    elif move == "left" and j > 0:
        new_data[i][j], new_data[i][j-1] = new_data[i][j-1], new_data[i][j]
        return True, new_data
    elif move == "right" and j < 2:
        new_data[i][j], new_data[i][j+1] = new_data[i][j+1], new_data[i][j]
        return True, new_data
    
    return False, None

def is_solvable(state):
    """
    Kiểm tra xem một trạng thái puzzle có giải được không.
    Trong 8-puzzle, tính số inversions trong danh sách trạng thái.
    Puzzle có thể giải được nếu số inversions là chẵn.
    """
    # Flatten state để đếm inversions
    flat_state = [num for row in state for num in row if num != 0]
    
    inversions = 0
    for i in range(len(flat_state)):
        for j in range(i+1, len(flat_state)):
            if flat_state[i] > flat_state[j]:
                inversions += 1
                
    return inversions % 2 == 0

def bfs(initial_state):
    """Breadth First Search"""
    frontier = deque([(initial_state.data, [])])  # (state_data, path)
    explored = {str(initial_state.data)}
    nodes_expanded = 0
    max_frontier_size = 1
    
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        current_data, path = frontier.popleft()
        nodes_expanded += 1
        
        if Buzzle(current_data).is_goal():
            return path, nodes_expanded, max_frontier_size
            
        for move in ["up", "down", "left", "right"]:
            success, new_data = create_new_state(current_data, move)
            if success and str(new_data) not in explored:
                new_path = path + [(move, new_data)]
                if Buzzle(new_data).is_goal():
                    return new_path, nodes_expanded + 1, max(max_frontier_size, len(frontier) + 1)
                explored.add(str(new_data))
                frontier.append((new_data, new_path))
                
    return [], nodes_expanded, max_frontier_size

def dfs(initial_state):
    """Depth First Search"""
    # DFS có thể đi sâu vô hạn, nên thêm giới hạn độ sâu
    max_depth = 30
    frontier = [(initial_state.data, [], 0)]  # (state_data, path, depth)
    explored = {str(initial_state.data)}
    nodes_expanded = 0
    max_frontier_size = 1
    
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        current_data, path, depth = frontier.pop()
        nodes_expanded += 1
        
        if depth > max_depth:  # Giới hạn độ sâu
            continue
        
        if Buzzle(current_data).is_goal():
            return path, nodes_expanded, max_frontier_size
            
        # DFS thêm nút con theo thứ tự ngược để duy trì thứ tự duyệt
        for move in reversed(["up", "down", "left", "right"]):
            success, new_data = create_new_state(current_data, move)
            if success and str(new_data) not in explored:
                new_path = path + [(move, new_data)]
                if Buzzle(new_data).is_goal():
                    return new_path, nodes_expanded + 1, max(max_frontier_size, len(frontier) + 1)
                explored.add(str(new_data))
                frontier.append((new_data, new_path, depth + 1))
                
    return [], nodes_expanded, max_frontier_size

def manhattan_distance(state):
    """Calculate Manhattan distance heuristic"""
    distance = 0
    goal_positions = {1:(0,0), 2:(0,1), 3:(0,2),
                     4:(1,0), 5:(1,1), 6:(1,2),
                     7:(2,0), 8:(2,1), 0:(2,2)}
                     
    for i in range(3):
        for j in range(3):
            value = state.data[i][j]
            if value != 0:  # Không tính khoảng cách cho ô trống
                goal_i, goal_j = goal_positions[value]
                distance += abs(i - goal_i) + abs(j - goal_j)
    return distance

def astar(initial_state):
    """A* Search với Manhattan distance"""
    frontier = [(manhattan_distance(Buzzle(initial_state.data)), 0, initial_state.data, [], 0)]
    # (f_value, tie_breaker, state_data, path, g_value)
    explored = {str(initial_state.data): 0}  # state_str -> g_value
    nodes_expanded = 0
    max_frontier_size = 1
    counter = 1  # tie breaker
    
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        _, _, current_data, path, g_value = heapq.heappop(frontier)
        
        # Nếu đã có đường đi tốt hơn, bỏ qua
        if g_value > explored.get(str(current_data), float('inf')):
            continue
            
        nodes_expanded += 1
        
        if Buzzle(current_data).is_goal():
            return path, nodes_expanded, max_frontier_size
            
        for move in ["up", "down", "left", "right"]:
            success, new_data = create_new_state(current_data, move)
            if not success:
                continue
                
            new_g = g_value + 1
            new_state_str = str(new_data)
            
            # Nếu đã có đường đi tốt hơn đến trạng thái này
            if new_state_str in explored and explored[new_state_str] <= new_g:
                continue
                
            new_path = path + [(move, new_data)]
            
            if Buzzle(new_data).is_goal():
                return new_path, nodes_expanded + 1, max(max_frontier_size, len(frontier) + 1)
                
            explored[new_state_str] = new_g
            h_value = manhattan_distance(Buzzle(new_data))
            f_value = new_g + h_value
            
            heapq.heappush(frontier, (f_value, counter, new_data, new_path, new_g))
            counter += 1
                
    return [], nodes_expanded, max_frontier_size

def ucs(initial_state):
    """Uniform Cost Search - tìm kiếm theo chi phí đồng nhất"""
    frontier = [(0, 0, initial_state.data, [])]  # (cost, tie_breaker, state_data, path)
    explored = {str(initial_state.data): 0}  # Lưu chi phí tối thiểu
    nodes_expanded = 0
    max_frontier_size = 1
    counter = 1  # tie breaker
    
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        cost, _, current_data, path = heapq.heappop(frontier)
        
        # Skip nếu đã có đường đi tốt hơn
        if cost > explored.get(str(current_data), float('inf')):
            continue
            
        nodes_expanded += 1
        
        if Buzzle(current_data).is_goal():
            return path, nodes_expanded, max_frontier_size
            
        for move in ["up", "down", "left", "right"]:
            success, new_data = create_new_state(current_data, move)
            if not success:
                continue
                
            new_cost = cost + 1
            new_state_str = str(new_data)
            
            if new_state_str in explored and explored[new_state_str] <= new_cost:
                continue
                
            new_path = path + [(move, new_data)]
            
            if Buzzle(new_data).is_goal():
                return new_path, nodes_expanded + 1, max(max_frontier_size, len(frontier) + 1)
                
            explored[new_state_str] = new_cost
            heapq.heappush(frontier, (new_cost, counter, new_data, new_path))
            counter += 1
                
    return [], nodes_expanded, max_frontier_size

def greedy(initial_state):
    """Greedy Best-First Search - chỉ sử dụng heuristic"""
    frontier = [(manhattan_distance(Buzzle(initial_state.data)), 0, initial_state.data, [])]
    explored = {str(initial_state.data)}
    nodes_expanded = 0
    max_frontier_size = 1
    counter = 1
    
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        _, _, current_data, path = heapq.heappop(frontier)
        nodes_expanded += 1
        
        if Buzzle(current_data).is_goal():
            return path, nodes_expanded, max_frontier_size
            
        for move in ["up", "down", "left", "right"]:
            success, new_data = create_new_state(current_data, move)
            if success and str(new_data) not in explored:
                new_path = path + [(move, new_data)]
                
                if Buzzle(new_data).is_goal():
                    return new_path, nodes_expanded + 1, max(max_frontier_size, len(frontier) + 1)
                    
                explored.add(str(new_data))
                h_value = manhattan_distance(Buzzle(new_data))
                heapq.heappush(frontier, (h_value, counter, new_data, new_path))
                counter += 1
                
    return [], nodes_expanded, max_frontier_size

def dfs_limited(initial_state, depth_limit):
    """DFS với giới hạn độ sâu"""
    frontier = [(initial_state.data, [], 0)]  # (state_data, path, depth)
    explored = {}  # state_str -> depth (để ghi nhớ độ sâu tối ưu)
    explored[str(initial_state.data)] = 0
    nodes_expanded = 0
    max_frontier_size = 1
    
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        current_data, path, depth = frontier.pop()
        
        # Skip nếu đã có đường đi tốt hơn (ngắn hơn)
        if depth > explored.get(str(current_data), float('inf')):
            continue
            
        nodes_expanded += 1
        
        if depth > depth_limit:
            continue
            
        if Buzzle(current_data).is_goal():
            return True, path, nodes_expanded, max_frontier_size
            
        for move in reversed(["up", "down", "left", "right"]):
            success, new_data = create_new_state(current_data, move)
            if not success:
                continue
                
            new_depth = depth + 1
            new_state_str = str(new_data)
            
            if new_state_str in explored and explored[new_state_str] <= new_depth:
                continue
                
            explored[new_state_str] = new_depth
            frontier.append((new_data, path + [(move, new_data)], new_depth))
                
    return False, [], nodes_expanded, max_frontier_size

def ids(initial_state):
    """Iterative Deepening Search - tìm kiếm sâu dần"""
    total_nodes = 0
    max_fringe = 0
    
    for depth in range(50):  # Giới hạn độ sâu tối đa = 50
        found, path, nodes, fringe = dfs_limited(initial_state, depth)
        total_nodes += nodes
        max_fringe = max(max_fringe, fringe)
        
        if found:
            return path, total_nodes, max_fringe
            
    return [], total_nodes, max_fringe
# <<< Thêm code AND/OR Search vào đây >>>
def and_or_graph_search(problem):
    # Lưu ý: Cần điều chỉnh để 'problem' tương thích với lớp Buzzle
    # hoặc tạo một lớp Problem mới phù hợp.
    # Giả sử problem có initial_state, goal_test, actions, result
    return or_search(problem.initial_state, problem, [])

def or_search(state, problem, path):
    if problem.goal_test(state):
        return []
    if state in path: # Kiểm tra chu trình đơn giản
        return 'failure'

    for action in problem.actions(state):
         # 'problem.result' cần trả về một danh sách các trạng thái con (AND nodes)
         # Nếu hành động chỉ dẫn đến một trạng thái (OR node), cần điều chỉnh logic
        results = problem.result(state, action) # Giả sử trả về list các state cho AND node

        # Nếu chỉ có 1 kết quả (như trong 8-puzzle thông thường), xử lý như OR node
        if not isinstance(results, list):
             results = [results] # Coi như AND node với 1 nhánh

        plan = and_search(results, problem, path + [state])
        if plan != 'failure':
            # Cấu trúc trả về cần phù hợp với cách bạn muốn biểu diễn kế hoạch
            # Ví dụ: [(action, state_con_1, plan_con_1), (action, state_con_2, plan_con_2), ...]
            # Hoặc đơn giản hơn nếu chỉ là OR node: return [(action, plan)]
            # Hiện tại đang giữ cấu trúc đơn giản cho OR node:
            return [(action, plan)] # Cần xem lại cấu trúc plan mong muốn

    return 'failure'

def and_search(states, problem, path):
    # Hàm này xử lý các AND node (nhiều trạng thái cần đạt được)
    plans = {} # Sử dụng dictionary để lưu plan cho từng state con
    for s in states:
        plan = or_search(s, problem, path)
        if plan == 'failure':
            return 'failure'
        # Cần định nghĩa cách lưu trữ plan cho từng state con
        plans[str(s)] = plan # Ví dụ lưu plan theo string của state

    # Trả về tập hợp các plan cho các state con
    # Cấu trúc trả về cần được xác định rõ ràng
    return plans # Ví dụ: trả về dict các plan
# <<< Kết thúc phần thêm code AND/OR Search >>>

# ... (Các hàm khác như get_algorithm_groups, solve_puzzle)
def idastar(initial_state):
    """Iterative Deepening A* - combines IDS with A* heuristic"""
    initial_h = manhattan_distance(Buzzle(initial_state.data))
    bound = initial_h
    
    nodes_expanded = 0
    max_frontier_size = 0
    
    path = []
    
    while True:
        t, found, path, nodes, frontier = _ida_search(initial_state.data, [], 0, bound, {}, 0)
        nodes_expanded += nodes
        max_frontier_size = max(max_frontier_size, frontier)
        
        if found:
            return path, nodes_expanded, max_frontier_size
            
        if t == float('inf'):  # No solution found
            return [], nodes_expanded, max_frontier_size
            
        bound = t  # Update bound for next iteration
        
def _ida_search(current_data, path, g, bound, visited, frontier_size):
    """Helper function for IDA* search"""
    current_h = manhattan_distance(Buzzle(current_data))
    f = g + current_h
    
    if f > bound:
        return f, False, [], 0, frontier_size
        
    if Buzzle(current_data).is_goal():
        return 0, True, path, 1, frontier_size
        
    min_cost = float('inf')
    nodes_expanded = 1
    best_path = []
    max_frontier = frontier_size
    
    state_str = str(current_data)
    if state_str in visited and visited[state_str] <= g:
        return float('inf'), False, [], 0, frontier_size
    visited[state_str] = g
    
    for move in ["up", "down", "left", "right"]:
        success, new_data = create_new_state(current_data, move)
        if not success:
            continue
            
        new_frontier = frontier_size + 1
        max_frontier = max(max_frontier, new_frontier)
        
        t, found, new_path, nodes, new_max_frontier = _ida_search(
            new_data, path + [(move, new_data)], g + 1, bound, visited.copy(), new_frontier
        )
        nodes_expanded += nodes
        max_frontier = max(max_frontier, new_max_frontier)
        
        if found:
            return t, True, new_path, nodes_expanded, max_frontier
            
        if t < min_cost:
            min_cost = t
            best_path = new_path
            
    return min_cost, False, best_path, nodes_expanded, max_frontier

def hill_climbing_max(initial_state):
    """Hill Climbing search algorithm that always selects the best move"""
    current_data = initial_state.data
    current_h = manhattan_distance(Buzzle(current_data))
    
    path = []
    nodes_expanded = 1
    max_frontier_size = 1
    
    while True:
        if Buzzle(current_data).is_goal():
            return path, nodes_expanded, max_frontier_size
            
        best_h = current_h
        best_move = None
        best_state = None
        neighbors = 0
        
        for move in ["up", "down", "left", "right"]:
            success, new_data = create_new_state(current_data, move)
            if not success:
                continue
                
            neighbors += 1
            new_h = manhattan_distance(Buzzle(new_data))
            
            if new_h < best_h:
                best_h = new_h
                best_move = move
                best_state = new_data
                
        nodes_expanded += neighbors
        max_frontier_size = max(max_frontier_size, neighbors)
        
        # If no better move found, we've reached a local minimum
        if best_move is None:
            break
            
        # Move to the best neighbor
        current_data = best_state
        current_h = best_h
        path.append((best_move, best_state))
        
        # Early termination if goal reached
        if current_h == 0:
            break
            
    # Check if we found a solution
    if Buzzle(current_data).is_goal():
        return path, nodes_expanded, max_frontier_size
    else:
        return [], nodes_expanded, max_frontier_size

def hill_climbing_random(initial_state):
    """Hill Climbing with random moves when stuck in local minimum"""
    current_data = initial_state.data
    current_h = manhattan_distance(Buzzle(current_data))
    
    path = []
    nodes_expanded = 1
    max_frontier_size = 1
    max_restarts = 5  # Limit the number of random restarts
    restarts = 0
    
    while restarts <= max_restarts:
        if Buzzle(current_data).is_goal():
            return path, nodes_expanded, max_frontier_size
            
        best_h = current_h
        best_move = None
        best_state = None
        neighbors = 0
        
        for move in ["up", "down", "left", "right"]:
            success, new_data = create_new_state(current_data, move)
            if not success:
                continue
                
            neighbors += 1
            new_h = manhattan_distance(Buzzle(new_data))
            
            if new_h < best_h:
                best_h = new_h
                best_move = move
                best_state = new_data
                
        nodes_expanded += neighbors
        max_frontier_size = max(max_frontier_size, neighbors)
        
        # If no better move found, we've reached a local minimum
        if best_move is None:
            # Try a random move instead of giving up
            random_moves = []
            for move in ["up", "down", "left", "right"]:
                success, new_data = create_new_state(current_data, move)
                if success:
                    random_moves.append((move, new_data))
            
            if random_moves:
                import random
                # Choose a random valid move
                random_move, random_state = random.choice(random_moves)
                current_data = random_state
                current_h = manhattan_distance(Buzzle(current_data))
                path.append((f"random-{random_move}", random_state))
                restarts += 1
            else:
                break  # No moves possible
        else:
            # Move to the best neighbor
            current_data = best_state
            current_h = best_h
            path.append((best_move, best_state))
            
            # Early termination if goal reached
            if current_h == 0:
                break
            
    # Check if we found a solution
    if Buzzle(current_data).is_goal():
        return path, nodes_expanded, max_frontier_size
    else:
        return [], nodes_expanded, max_frontier_size

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
            # <<< Thêm SA vào đây >>>
            "simulated_annealing": "Simulated Annealing"
            # <<< Kết thúc thêm SA >>>
        },
        # <<< Thêm nhóm mới và thuật toán >>>
        "Thuật toán trong môi trường phức tạp / Đồ thị AND/OR": {
             "and_or_search": "AND/OR Graph Search"
        },
        # <<< Thêm nhóm GA >>>
         "Thuật toán Tiến hóa (Evolutionary Algorithms)": {
             "genetic_algorithm": "Genetic Algorithm"
         }
        # <<< Kết thúc phần thêm nhóm >>>
    }
    return groups

def solve_puzzle(algorithm, start_state):
    """Unified interface for all search algorithms"""
    # Lưu ý: AND/OR Search có thể không cần kiểm tra is_solvable theo cách thông thường
    # if not is_solvable(start_state.data) and algorithm.lower() not in ["hill_climbing_max", "hill_climbing_random", "and_or_search"]:
    #     return [], 0, 0

    algorithms = {
        "bfs": bfs,
        "dfs": dfs,
        "ucs": ucs,
        "astar": astar,
        "idastar": idastar,
        "greedy": greedy,
        "ids": ids,
        "hill_climbing_max": hill_climbing_max,
        "hill_climbing_random": hill_climbing_random,
        # <<< Thêm AND/OR Search vào đây >>>
        "and_or_search": and_or_graph_search,
        # <<< Thêm SA và GA vào đây >>>
        "simulated_annealing": simulated_annealing,
        "genetic_algorithm": genetic_algorithm
        # <<< Kết thúc phần thêm AND/OR Search >>>
    }

    # Lấy hàm giải thuật tương ứng, mặc định là BFS
    solver = algorithms.get(algorithm.lower(), bfs)

    # <<< Lưu ý quan trọng về tham số cho AND/OR Search >>>
    if algorithm.lower() == "and_or_search":
        # Thuật toán AND/OR cần một đối tượng 'problem' có cấu trúc khác
        # Bạn cần tạo một đối tượng problem tương thích với Buzzle
        # Ví dụ:
        # class AndOrProblemAdapter:
        #     def __init__(self, initial_buzzle_state):
        #         self.initial_state = initial_buzzle_state.data # Hoặc cả object Buzzle
        #     def goal_test(self, state_data):
        #         return Buzzle(state_data).is_goal()
        #     def actions(self, state_data):
        #         # Trả về các hành động hợp lệ ['up', 'down', ...]
        #         # Cần logic để xác định hành động từ state_data
        #         pass
        #     def result(self, state_data, action):
        #         # Trả về danh sách các trạng thái kết quả (AND nodes)
        #         # Hoặc một trạng thái duy nhất nếu là OR node
        #         # Cần logic để tạo state mới từ state_data và action
        #         success, new_data = create_new_state(state_data, action)
        #         if success:
        #              # Quyết định trả về list hay single state dựa trên logic bài toán AND/OR
        #              return [new_data] # Ví dụ trả về list cho phù hợp and_search
        #         return [] # Hoặc trạng thái gốc nếu hành động không hợp lệ

        # problem_adapter = AndOrProblemAdapter(start_state)
        # return solver(problem_adapter) # Gọi với adapter thay vì start_state
        print("Lưu ý: AND/OR Search cần một đối tượng 'problem' được điều chỉnh.")
        print("Hàm solve_puzzle cần được sửa đổi để tạo và truyền 'problem' phù hợp.")
        return [], 0, 0 # Trả về rỗng vì chưa thể gọi trực tiếp
    else:
         # Gọi các thuật toán khác như bình thường
         return solver(start_state)
    # <<< Kết thúc phần lưu ý >>>

# <<< Thêm code Simulated Annealing >>>
def simulated_annealing(initial_state, initial_temp=100, cooling_rate=0.99, min_temp=0.1):
    """Simulated Annealing search algorithm"""
    current_data = initial_state.data
    current_h = manhattan_distance(Buzzle(current_data))
    
    path = [] # SA không theo dõi đường đi tối ưu, chỉ trạng thái cuối
    nodes_evaluated = 0 # Đếm số trạng thái được đánh giá
    max_neighbors = 4 # Tối đa 4 hàng xóm cho mỗi trạng thái

    temp = initial_temp

    while temp > min_temp:
        nodes_evaluated += 1
        if Buzzle(current_data).is_goal():
            # Trả về đường đi rỗng vì SA không tối ưu đường đi
            return [], nodes_evaluated, max_neighbors 

        # Chọn ngẫu nhiên một trạng thái lân cận
        possible_moves = []
        for move in ["up", "down", "left", "right"]:
            success, neighbor_data = create_new_state(current_data, move)
            if success:
                possible_moves.append((move, neighbor_data))
        
        if not possible_moves:
            break # Không còn nước đi nào

        move, next_data = random.choice(possible_moves)
        next_h = manhattan_distance(Buzzle(next_data))
        nodes_evaluated += 1 # Đánh giá trạng thái mới

        delta_e = next_h - current_h

        # Nếu trạng thái mới tốt hơn, luôn di chuyển
        if delta_e < 0:
            current_data = next_data
            current_h = next_h
            # Không lưu path chi tiết cho SA
        # Nếu trạng thái mới tệ hơn, di chuyển với xác suất nhất định
        else:
            # Dùng thư viện math thay vì numpy nếu không có
            import math 
            probability = math.exp(-delta_e / temp)
            if random.random() < probability:
                current_data = next_data
                current_h = next_h
                # Không lưu path chi tiết cho SA

        # Giảm nhiệt độ
        temp *= cooling_rate

    # Trả về kết quả cuối cùng (có thể không phải goal)
    # Nếu trạng thái cuối là goal, trả về path rỗng
    if Buzzle(current_data).is_goal():
         return [], nodes_evaluated, max_neighbors
    else: # Không tìm thấy lời giải
         return [], nodes_evaluated, max_neighbors
# <<< Kết thúc phần thêm code Simulated Annealing >>>

# <<< Thêm code Genetic Algorithm >>>
def calculate_fitness(state_data):
    """Hàm đánh giá độ thích nghi (fitness), giá trị càng cao càng tốt."""
    # Ví dụ: nghịch đảo của Manhattan distance (cộng 1 để tránh chia cho 0)
    # Hoặc số ô đúng vị trí
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    correct_tiles = 0
    for r in range(3):
        for c in range(3):
            if state_data[r][c] != 0 and state_data[r][c] == goal[r][c]:
                correct_tiles += 1
    # return 1 / (1 + manhattan_distance(Buzzle(state_data)))
    return correct_tiles

def generate_initial_population(initial_state_data, size=100):
    """Tạo quần thể ban đầu, bao gồm trạng thái ban đầu và các trạng thái ngẫu nhiên hợp lệ."""
    population = {str(initial_state_data)} # Dùng set để tránh trùng lặp
    # Tạo thêm các trạng thái ngẫu nhiên hợp lệ
    while len(population) < size:
        numbers = list(range(9))
        random.shuffle(numbers)
        new_state_data = [numbers[i:i+3] for i in range(0, 9, 3)]
        if is_solvable(new_state_data): # Chỉ thêm trạng thái giải được
             # Chuyển list sang tuple để hashable cho set
             population.add(str(new_state_data)) 
    # Chuyển lại thành list các list data
    return [eval(s) for s in population]

def select_parents(population, fitness_scores, num_parents):
    """Chọn cha mẹ dựa trên fitness (ví dụ: tournament selection)."""
    parents = []
    population_with_fitness = list(zip(population, fitness_scores))
    
    # Tournament Selection
    tournament_size = 5 
    for _ in range(num_parents):
        tournament = random.sample(population_with_fitness, tournament_size)
        # Chọn cá thể tốt nhất trong tournament
        winner = max(tournament, key=lambda item: item[1])[0] 
        parents.append(winner)
    return parents

def crossover(parent1_data, parent2_data):
    """Lai ghép hai trạng thái (cần đảm bảo tính hợp lệ)."""
    # Cách lai ghép đơn giản: tạo một trạng thái con bằng cách di chuyển ô trống
    # của parent1 theo hướng gần nhất với ô trống của parent2 (heuristic).
    # Đây là một cách đơn giản hóa, GA thực sự phức tạp hơn.
    # Hoặc thử một cách khác: Lấy một phần của parent1, phần còn lại từ parent2 và điền số còn thiếu.
    
    # Cách 1: Di chuyển ô trống (có thể không hiệu quả lắm)
    # blank1 = Buzzle(parent1_data).get_blank_position()
    # blank2 = Buzzle(parent2_data).get_blank_position()
    # # Di chuyển ô trống của parent1 một bước về phía blank2
    # # ... logic phức tạp để tìm nước đi tốt nhất ...
    # # Tạm thời chỉ trả về parent1 để tránh lỗi
    # return parent1_data 

    # Cách 2: Single-point crossover trên flatten list (cần sửa lỗi số trùng)
    p1_flat = [num for row in parent1_data for num in row]
    p2_flat = [num for row in parent2_data for num in row]
    
    point = random.randint(1, 8)
    child_flat = p1_flat[:point]
    
    # Thêm các số từ p2 chưa có trong child, theo thứ tự
    remaining_from_p2 = [num for num in p2_flat if num not in child_flat]
    child_flat.extend(remaining_from_p2)

    # Đảm bảo đủ 9 số (trường hợp hiếm gặp lỗi)
    if len(child_flat) != 9:
         return parent1_data # Trả về parent nếu có lỗi

    # Reshape thành 3x3
    child_data = [child_flat[i:i+3] for i in range(0, 9, 3)]
    
    # Quan trọng: Kiểm tra xem con có hợp lệ không (đủ số 0-8)
    if set(num for row in child_data for num in row) == set(range(9)):
        return child_data
    else:
        # Nếu không hợp lệ, trả về một trong hai cha mẹ ngẫu nhiên
        return random.choice([parent1_data, parent2_data])


def mutate(state_data, mutation_rate=0.1):
    """Đột biến trạng thái (ví dụ: di chuyển ngẫu nhiên ô trống)."""
    if random.random() < mutation_rate:
        possible_moves = []
        for move in ["up", "down", "left", "right"]:
            success, neighbor_data = create_new_state(state_data, move)
            if success:
                possible_moves.append(neighbor_data)
        if possible_moves:
            return random.choice(possible_moves)
    return state_data

def genetic_algorithm(initial_state, population_size=100, generations=500, mutation_rate=0.1, elitism_rate=0.1):
    """Genetic Algorithm for 8-puzzle."""
    population = generate_initial_population(initial_state.data, population_size)
    
    nodes_evaluated = 0 # Đếm số trạng thái được đánh giá trong các thế hệ
    max_pop_size = population_size # Kích thước quần thể là cố định
    
    best_solution_data = None
    best_fitness = -1

    for gen in range(generations):
        # Đánh giá fitness
        fitness_scores = [calculate_fitness(ind) for ind in population]
        nodes_evaluated += len(population)

        # Tìm cá thể tốt nhất thế hệ này
        current_best_idx = max(range(len(fitness_scores)), key=fitness_scores.__getitem__)
        current_best_fitness = fitness_scores[current_best_idx]
        current_best_individual = population[current_best_idx]

        # Cập nhật lời giải tốt nhất toàn cục
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_solution_data = current_best_individual
            # Kiểm tra xem có phải goal state không
            if Buzzle(best_solution_data).is_goal():
                 # Trả về path rỗng vì GA không tối ưu đường đi
                 return [], nodes_evaluated, max_pop_size

        # Elitism: Giữ lại một phần cá thể tốt nhất
        num_elites = int(elitism_rate * population_size)
        sorted_population = [x for _, x in sorted(zip(fitness_scores, population), key=lambda pair: pair[0], reverse=True)]
        next_population = sorted_population[:num_elites]

        # Selection, Crossover, Mutation để tạo phần còn lại
        num_parents = population_size - num_elites # Số lượng cha mẹ cần để tạo con
        if num_parents % 2 != 0: # Đảm bảo số lượng cha mẹ là chẵn để lai ghép cặp đôi
             num_parents -=1 
             if num_elites < population_size: # Bù lại vào elite nếu có thể
                 num_elites += 1
                 # Đảm bảo next_population có đủ elite
                 if len(next_population) < num_elites and len(sorted_population) >= num_elites:
                     next_population = sorted_population[:num_elites]
             # Nếu không bù được, thế hệ sau sẽ nhỏ hơn 1 chút, không sao
        
        # Chỉ chọn cha mẹ nếu cần tạo con
        parents = []
        if num_parents > 0:
             parents = select_parents(population, fitness_scores, num_parents)
        
        # Tạo con cái
        offspring = []
        for i in range(0, len(parents), 2):
             parent1 = parents[i]
             # Kiểm tra nếu còn parent2
             if i + 1 < len(parents):
                 parent2 = parents[i+1]
                 child1 = crossover(parent1, parent2)
                 child2 = crossover(parent2, parent1) # Có thể tạo 2 con khác nhau
                 offspring.append(mutate(child1, mutation_rate))
                 offspring.append(mutate(child2, mutation_rate))
             else: # Nếu số parents lẻ, chỉ dùng parent1 (hiếm khi xảy ra nếu logic trên đúng)
                  child = mutate(parent1, mutation_rate) # Tự đột biến
                  offspring.append(child)


        # Thêm con cái vào quần thể mới (chỉ thêm đủ số lượng)
        needed = population_size - len(next_population)
        next_population.extend(offspring[:needed])
        
        # Cập nhật quần thể cho thế hệ tiếp theo
        population = next_population
        
        # Đảm bảo population size không vượt quá giới hạn (phòng lỗi)
        population = population[:population_size]
        
        # Nếu quần thể rỗng thì dừng
        if not population:
            break

    # Kết thúc số thế hệ, kiểm tra xem lời giải tốt nhất có phải goal không
    if best_solution_data and Buzzle(best_solution_data).is_goal():
         return [], nodes_evaluated, max_pop_size
    else:
         # Không tìm thấy lời giải trong số thế hệ cho trước
         return [], nodes_evaluated, max_pop_size
# <<< Kết thúc phần thêm code Genetic Algorithm >>>

# Original puzzle_gui.py code starts here
class SolverThread(QThread):
    """Thread riêng cho việc giải puzzle để không block UI"""
    solution_ready = pyqtSignal(list, int, int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, algorithm, start_state):
        super().__init__()
        self.algorithm = algorithm
        self.start_state = start_state
        
    def run(self):
        try:
            path, nodes, fringe = solve_puzzle(self.algorithm, self.start_state)
            self.solution_ready.emit(path, nodes, fringe)
        except Exception as e:
            self.error_occurred.emit(str(e))

class PuzzleBoard(QWidget):
    """Một bảng puzzle đơn lẻ"""
    def __init__(self, title="Puzzle"):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Container cho grid puzzle với border
        puzzle_container = QWidget()
        puzzle_container.setStyleSheet("""
            QWidget {
                background-color: #333;
                border: 2px solid #666;
                border-radius: 5px;
            }
        """)
        container_layout = QVBoxLayout()
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(2, 2, 2, 2)
        
        # Grid cho các ô puzzle
        grid = QGridLayout()
        grid.setSpacing(1)
        self.tiles = []
        
        for i in range(3):
            row = []
            for j in range(3):
                btn = QPushButton()
                btn.setFixedSize(80, 80)
                btn.setFont(QFont('Arial', 24, QFont.Bold))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;
                        border: 1px solid #999;
                        border-radius: 0px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                """)
                grid.addWidget(btn, i, j)
                row.append(btn)
            self.tiles.append(row)
        
        container_layout.addLayout(grid)
        puzzle_container.setLayout(container_layout)
        layout.addWidget(puzzle_container)
        
        self.setLayout(layout)
    
    def update_board(self, state):
        for i in range(3):
            for j in range(3):
                value = state[i][j]
                self.tiles[i][j].setText(str(value) if value != 0 else "")

class SolutionNavigationPanel(QWidget):
    """Panel hiển thị từng bước của lời giải với nút điều hướng"""
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("Solution Navigator")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 12, QFont.Bold))
        
        # Puzzle display
        self.current_step_board = PuzzleBoard("Current Step")
        
        # Step info
        self.step_info = QLabel("Step 0/0")
        self.step_info.setAlignment(Qt.AlignCenter)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        
        # Move description
        self.move_desc = QLabel("No solution loaded")
        self.move_desc.setAlignment(Qt.AlignCenter)
        
        # Add all to main layout
        layout.addWidget(title_label)
        layout.addWidget(self.current_step_board)
        layout.addWidget(self.step_info)
        layout.addLayout(nav_layout)
        layout.addWidget(self.move_desc)
        
        self.setLayout(layout)
        
        # Solution data
        self.solution_path = []
        self.current_step = 0
        
        # Connect signals
        self.prev_btn.clicked.connect(self.go_to_previous_step)
        self.next_btn.clicked.connect(self.go_to_next_step)
    
    def set_solution(self, path):
        """Set solution path and reset to first step"""
        self.solution_path = path
        self.current_step = 0
        self.update_navigation_state()
        if path:
            self.show_current_step()
        else:
            self.reset_display()
    
    def update_navigation_state(self):
        """Update button states based on current position"""
        has_solution = len(self.solution_path) > 0
        self.prev_btn.setEnabled(has_solution and self.current_step > 0)
        self.next_btn.setEnabled(has_solution and self.current_step < len(self.solution_path) - 1)
        if has_solution:
            self.step_info.setText(f"Step {self.current_step}/{len(self.solution_path) - 1}")
        else:
            self.step_info.setText("Step 0/0")
    
    def show_current_step(self):
        """Display the current step"""
        if self.solution_path and 0 <= self.current_step < len(self.solution_path):
            move, state = self.solution_path[self.current_step]
            self.current_step_board.update_board(state)
            
            # Update move description
            if self.current_step == 0:
                self.move_desc.setText("Initial state")
            else:
                self.move_desc.setText(f"Move: {move}")
            
            self.update_navigation_state()
    
    def go_to_next_step(self):
        """Go to next step in solution"""
        if self.current_step < len(self.solution_path) - 1:
            self.current_step += 1
            self.show_current_step()
    
    def go_to_previous_step(self):
        """Go to previous step in solution"""
        if self.current_step > 0:
            self.current_step -= 1
            self.show_current_step()
    
    def reset_display(self):
        """Reset the display when no solution is loaded"""
        self.current_step_board.update_board([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
        self.move_desc.setText("No solution loaded")
        self.step_info.setText("Step 0/0")
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Input trạng thái
        input_group = QGroupBox("Trạng thái")
        input_layout = QVBoxLayout()
        
        # Start state input with random button
        start_input_layout = QHBoxLayout()
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Initial state (e.g: 1 2 0 3 4 5 6 7 8)")
        self.random_start_btn = QPushButton("Random Start")
        start_input_layout.addWidget(self.start_input)
        start_input_layout.addWidget(self.random_start_btn)
        
        input_layout.addLayout(start_input_layout)
        input_group.setLayout(input_layout)
        
        # Nút điều khiển
        button_group = QGroupBox("Điều khiển")
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Load States")
        self.reset_btn = QPushButton("Reset")
        self.solve_btn = QPushButton("Solve")
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.solve_btn)
        button_group.setLayout(button_layout)
        
        # Chọn thuật toán
        self.algo_select = AlgorithmSelectionPanel()
        
        # Thống kê kết quả
        stats_group = QGroupBox("Thống kê")
        stats_layout = QVBoxLayout()
        self.stats_label = QLabel("Ready")
        stats_layout.addWidget(self.stats_label)
        stats_group.setLayout(stats_layout)
        
        # Thêm vào layout chính
        layout.addWidget(input_group)
        layout.addWidget(button_group)
        layout.addWidget(self.algo_select)
        layout.addWidget(stats_group)
        layout.addStretch()
        
        self.setLayout(layout)

class ResultPanel(QWidget):
    """Panel hiển thị kết quả và mô tả thuật toán"""
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        
        # Phần hiển thị đường đi
        self.path_display = QTextEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setFixedHeight(200)
        
        # Phần hiển thị mô tả thuật toán
        self.algo_desc = QTextEdit()
        self.algo_desc.setReadOnly(True)
        self.algo_desc.setFixedHeight(200)
        
        # Tạo splitter để chia đôi panel
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.path_display)
        splitter.addWidget(self.algo_desc)
        splitter.setSizes([300, 300])  # Chia đều không gian
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
    def update_path(self, path):
        """Cập nhật hiển thị đường đi"""
        text = "Solution path:\n\n"
        for i, (move, state) in enumerate(path, 1):
            text += f"Step {i}: {move}\n"
            for row in state:
                text += f"{row}\n"
            text += "\n"
        self.path_display.setText(text)
        
    def update_algo_desc(self, algo_name):
        """Cập nhật mô tả thuật toán"""
        descriptions = {
            "bfs": "Breadth-First Search:\n- Tìm kiếm theo chiều rộng\n- Duyệt tất cả các trạng thái ở cùng độ sâu\n- Đảm bảo tìm ra đường đi ngắn nhất",
            "dfs": "Depth-First Search:\n- Tìm kiếm theo chiều sâu\n- Duyệt hết một nhánh trước khi quay lui\n- Không đảm bảo đường đi ngắn nhất",
            "ucs": "Uniform Cost Search:\n- Tìm kiếm theo chi phí đồng nhất\n- Mở rộng node có chi phí thấp nhất\n- Đảm bảo tìm ra đường đi tối ưu",
            "astar": "A* Search:\n- Kết hợp chi phí đường đi và heuristic\n- Sử dụng hàm f(n) = g(n) + h(n)\n- Đảm bảo tối ưu với heuristic admissible",
            "greedy": "Greedy Best-First Search:\n- Chỉ dựa vào heuristic\n- Luôn mở rộng node có h(n) nhỏ nhất\n- Nhanh nhưng không đảm bảo tối ưu",
            "ids": "Iterative Deepening Search:\n- DFS với độ sâu tăng dần\n- Kết hợp ưu điểm của BFS và DFS\n- Đảm bảo tìm ra đường đi ngắn nhất",
            "idastar": "Iterative Deepening A*:\n- Kết hợp IDS với heuristic của A*\n- Giảm yêu cầu bộ nhớ so với A*\n- Đảm bảo tìm ra đường đi tối ưu",
            "hill_climbing_max": "Hill Climbing Max:\n- Thuật toán tìm kiếm cục bộ\n- Luôn chọn bước đi cải thiện heuristic tốt nhất\n- Có thể bị kẹt ở cực tiểu cục bộ",
            "hill_climbing_random": "Hill Climbing Random:\n- Thuật toán tìm kiếm cục bộ với random\n- Khi bị kẹt ở cực tiểu cục bộ, chọn ngẫu nhiên một bước đi\n- Có thể tìm ra lời giải khi Hill Climbing Max thất bại",
            "simulated_annealing": "Simulated Annealing:\n- Thuật toán tìm kiếm cục bộ xác suất\n- Cho phép di chuyển đến trạng thái xấu hơn với xác suất giảm dần theo 'nhiệt độ'\n- Giúp thoát khỏi cực tiểu cục bộ\n- Không đảm bảo tìm ra đường đi tối ưu.",
            "genetic_algorithm": "Genetic Algorithm:\n- Thuật toán tiến hóa dựa trên chọn lọc tự nhiên\n- Duy trì một quần thể các trạng thái\n- Sử dụng lai ghép (crossover) và đột biến (mutation) để tạo thế hệ mới\n- Tìm kiếm lời giải tốt trong không gian trạng thái lớn\n- Thường không tìm đường đi cụ thể, mà tìm trạng thái đích."
        }
        self.algo_desc.setText(descriptions.get(algo_name.lower().replace("*", "").replace(" ", "_"), ""))

class AlgorithmSelectionPanel(QGroupBox):
    """Panel chọn thuật toán theo nhóm"""
    def __init__(self):
        super().__init__("Chọn Thuật Toán")
        layout = QVBoxLayout()
        
        # Lấy danh sách nhóm thuật toán từ Solve.py
        self.algorithm_groups = get_algorithm_groups()
        
        # Khởi tạo các nút radio và nhóm nút
        self.algorithm_radio_buttons = {}
        self.selected_algorithm = None
        self.button_group = QButtonGroup(self)
        
        # Tạo radio button cho từng thuật toán theo nhóm
        for i, (group_name, algorithms) in enumerate(self.algorithm_groups.items()):
            # Tạo group box cho nhóm thuật toán
            group_box = QGroupBox(group_name)
            group_layout = QVBoxLayout()
            
            # Thêm các radio button cho các thuật toán trong nhóm
            for algo_key, algo_name in algorithms.items():
                radio_btn = QRadioButton(algo_name)
                radio_btn.setObjectName(algo_key)  # Lưu key của thuật toán
                self.algorithm_radio_buttons[algo_key] = radio_btn
                self.button_group.addButton(radio_btn)
                group_layout.addWidget(radio_btn)
            
            group_box.setLayout(group_layout)
            layout.addWidget(group_box)
        
        # Mặc định chọn thuật toán đầu tiên trong nhóm đầu tiên
        first_group = list(self.algorithm_groups.values())[0]
        first_algo_key = list(first_group.keys())[0]
        self.algorithm_radio_buttons[first_algo_key].setChecked(True)
        self.selected_algorithm = first_algo_key
        
        # Kết nối sự kiện khi chọn thuật toán
        self.button_group.buttonClicked.connect(self.algorithm_selected)
        
        self.setLayout(layout)
    
    def algorithm_selected(self, button):
        """Xử lý khi người dùng chọn thuật toán"""
        self.selected_algorithm = button.objectName()
    
    def get_selected_algorithm(self):
        """Trả về thuật toán đang được chọn"""
        return self.selected_algorithm

    def generate_random_state(self):
        """Tạo một trạng thái ngẫu nhiên hợp lệ cho puzzle"""
        while True:
            numbers = list(range(9))  # Số từ 0-8
            random.shuffle(numbers)
            state = [numbers[i:i+3] for i in range(0, 9, 3)]
            # Đảm bảo trạng thái có thể giải được (quan trọng cho hầu hết thuật toán)
            # GA và SA có thể xử lý trạng thái không giải được nhưng kết quả sẽ là không tìm thấy
            # Bỏ qua kiểm tra is_solvable ở đây để cho phép test GA/SA với mọi trạng thái
            # if is_solvable(state):
            return state
    
    def random_start_state(self):
        """Tạo trạng thái đầu ngẫu nhiên và cập nhật UI"""
        self.start_state.data = self.generate_random_state()
        # Cập nhật input field để hiển thị giá trị được tạo
        flat_numbers = [str(num) for row in self.start_state.data for num in row]
        self.control_panel.start_input.setText(' '.join(flat_numbers))
        self.update_display()
        self.solution_navigator.set_solution([]) # Clear previous solution view
        self.result_panel.update_path([]) # Clear path display
        self.control_panel.stats_label.setText("Ready") # Reset stats
        self.statusBar().showMessage("Random start state generated.")

    
    def reset_states(self):
        """Reset to default states and clear UI"""
        self.start_state = Buzzle() # Default initial state
        # Goal state is fixed, no need to reset
        # self.goal_state = Buzzle([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.update_display()
        # Clear the input field
        self.control_panel.start_input.clear()
        # Reset solution navigator
        self.solution_navigator.set_solution([])
        # Reset result panel
        self.result_panel.update_path([])
        self.result_panel.update_algo_desc("") # Clear description
        # Reset current solution
        self.current_solution = []
        # Reset stats label
        self.control_panel.stats_label.setText("Ready")
        self.statusBar().showMessage("States reset to default.")

# <<< Thêm định nghĩa lớp PuzzleWindow vào đây >>>
class PuzzleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("8-Puzzle Solver")
        
        # Widget chính
        main_widget = QWidget()
        main_layout = QHBoxLayout()  # Chia layout theo chiều ngang
        
        # Panel trái 
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Container cho bảng puzzle và navigator
        boards_container = QWidget()
        boards_layout = QHBoxLayout()
        boards_layout.setSpacing(10)
        
        self.start_board = PuzzleBoard("Initial State")
        self.goal_board = PuzzleBoard("Goal State")
        self.solution_navigator = SolutionNavigationPanel()
        
        boards_layout.addWidget(self.start_board)
        boards_layout.addWidget(self.goal_board)
        boards_layout.addWidget(self.solution_navigator)
        
        boards_container.setLayout(boards_layout)
        
        # Thêm Result Panel vào panel trái
        self.result_panel = ResultPanel()
        
        left_layout.addWidget(boards_container, stretch=3) 
        left_layout.addWidget(self.result_panel, stretch=1) 
        left_panel.setLayout(left_layout)
        
        # Panel phải cho điều khiển
        self.control_panel = ControlPanel()
        
        # Thêm vào layout chính 
        main_layout.addWidget(left_panel, stretch=7)
        main_layout.addWidget(self.control_panel, stretch=3)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Set kích thước cửa sổ
        self.resize(1280, 720)
        
        # Kết nối signals
        self.control_panel.load_btn.clicked.connect(self.load_states)
        self.control_panel.reset_btn.clicked.connect(self.reset_states)
        self.control_panel.solve_btn.clicked.connect(self.solve_puzzle)
        self.control_panel.random_start_btn.clicked.connect(self.random_start_state)
        
        # Khởi tạo states
        self.start_state = Buzzle()
        self.goal_state = Buzzle([[1, 2, 3], [4, 5, 6], [7, 8, 0]]) # Trạng thái đích cố định
        self.update_display()
        
        # Status bar
        self.statusBar()
        
        # Lưu trữ solution path
        self.current_solution = []
    
    def load_states(self):
        """Load start state from input"""
        try:
            start_input = self.control_panel.start_input.text()
            start_numbers = [int(x) for x in start_input.split()]
            if len(start_numbers) != 9 or set(start_numbers) != set(range(9)):
                raise ValueError("Invalid start state input. Use 9 unique numbers (0-8).")
            self.start_state.data = [start_numbers[i:i+3] for i in range(0, 9, 3)]
            self.update_display()
            self.solution_navigator.set_solution([]) # Clear previous solution view
            self.result_panel.update_path([]) # Clear path display
            self.control_panel.stats_label.setText("Ready") # Reset stats
            self.statusBar().showMessage("Start state loaded.")
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
    
    def update_display(self):
        """Cập nhật hiển thị cả 2 bảng"""
        self.start_board.update_board(self.start_state.data)
        self.goal_board.update_board(self.goal_state.data)
    
    def solve_puzzle(self):
        """Xử lý khi nhấn nút Solve"""
        algorithm = self.control_panel.algo_select.get_selected_algorithm()
        
        # Kiểm tra tính giải được (trừ các thuật toán local search/evolutionary)
        unsolvable_check_algos = not algorithm.lower() in [
            "hill_climbing_max", 
            "hill_climbing_random", 
            "simulated_annealing", 
            "genetic_algorithm",
            "and_or_search" # AND/OR search might have different solvability logic
        ]
        if unsolvable_check_algos and not is_solvable(self.start_state.data):
            QMessageBox.warning(self, "Unsolvable Puzzle", 
                                "This puzzle configuration is mathematically unsolvable with the selected algorithm.")
            return
        
        # Disable nút solve và hiện progress bar
        self.control_panel.solve_btn.setEnabled(False)
        self.statusBar().showMessage(f"Solving with {algorithm.upper()}...")
        
        progress_bar = QProgressBar(self)
        progress_bar.setRange(0, 0)  # Indeterminate progress
        self.statusBar().addWidget(progress_bar, 1)
        
        # Chạy thuật toán trong thread riêng
        self.solver_thread = SolverThread(algorithm, self.start_state)
        self.solver_thread.solution_ready.connect(self.display_solution)
        self.solver_thread.error_occurred.connect(self.handle_solver_error)
        self.solver_thread.finished.connect(lambda: self.cleanup_ui(progress_bar))
        self.solver_thread.start()
    
    def display_solution(self, path, nodes, max_fringe):
        """Hiển thị kết quả khi giải xong"""
        self.current_solution = path # Lưu lại solution path
        
        # Cập nhật kết quả hiển thị
        selected_algo_name = self.control_panel.algo_select.get_selected_algorithm()
        self.result_panel.update_path(path) # Hiển thị đường đi (nếu có)
        self.result_panel.update_algo_desc(selected_algo_name) # Hiển thị mô tả algo
        
        # Cập nhật solution navigator (ngay cả khi path rỗng)
        self.solution_navigator.set_solution(path)
        # Nếu path rỗng, navigator sẽ tự reset
        if path:
             self.solution_navigator.current_step_board.update_board(path[0][1]) # Hiển thị bước đầu tiên nếu có
             self.solution_navigator.move_desc.setText("Move: initial state")
        
        # Cập nhật thống kê
        if path:
            stats = f"Solved in {len(path)} steps\nNodes evaluated/expanded: {nodes}\nMax fringe/population size: {max_fringe}"
            self.statusBar().showMessage(f"Solution found: {len(path)} steps.")
        elif selected_algo_name.lower() in ["genetic_algorithm", "simulated_annealing"]:
             # Các thuật toán này có thể không tìm thấy goal state
             stats = f"Goal state not reached.\nNodes evaluated: {nodes}\nMax population/neighbors: {max_fringe}"
             self.statusBar().showMessage(f"{selected_algo_name.upper()} finished. Goal not guaranteed.")
             # Cập nhật board cuối cùng của navigator nếu có thể (ví dụ: trạng thái tốt nhất của GA)
             # Logic này cần điều chỉnh tùy vào việc hàm GA/SA trả về gì khi thất bại
        else:
            stats = f"No solution found\nNodes expanded: {nodes}\nMax fringe size: {max_fringe}"
            self.statusBar().showMessage("No solution found.")
            
        self.control_panel.stats_label.setText(stats)
    
    def handle_solver_error(self, error_msg):
        """Xử lý lỗi từ solver thread"""
        QMessageBox.critical(self, "Solver Error", f"An error occurred during solving: {error_msg}")
        self.statusBar().showMessage("Error in solving process.")
    
    def cleanup_ui(self, progress_bar):
        """Dọn dẹp UI sau khi giải xong"""
        self.statusBar().removeWidget(progress_bar)
        self.control_panel.solve_btn.setEnabled(True)
        # Không nên tự động xóa status message ở đây

    def generate_random_state(self):
        """Tạo một trạng thái ngẫu nhiên hợp lệ cho puzzle"""
        while True:
            numbers = list(range(9))  # Số từ 0-8
            random.shuffle(numbers)
            state = [numbers[i:i+3] for i in range(0, 9, 3)]
            # Đảm bảo trạng thái có thể giải được (quan trọng cho hầu hết thuật toán)
            # GA và SA có thể xử lý trạng thái không giải được nhưng kết quả sẽ là không tìm thấy
            # Bỏ qua kiểm tra is_solvable ở đây để cho phép test GA/SA với mọi trạng thái
            # if is_solvable(state):
            return state
    
    def random_start_state(self):
        """Tạo trạng thái đầu ngẫu nhiên và cập nhật UI"""
        self.start_state.data = self.generate_random_state()
        # Cập nhật input field để hiển thị giá trị được tạo
        flat_numbers = [str(num) for row in self.start_state.data for num in row]
        self.control_panel.start_input.setText(' '.join(flat_numbers))
        self.update_display()
        self.solution_navigator.set_solution([]) # Clear previous solution view
        self.result_panel.update_path([]) # Clear path display
        self.control_panel.stats_label.setText("Ready") # Reset stats
        self.statusBar().showMessage("Random start state generated.")

    
    def reset_states(self):
        """Reset to default states and clear UI"""
        self.start_state = Buzzle() # Default initial state
        # Goal state is fixed, no need to reset
        # self.goal_state = Buzzle([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.update_display()
        # Clear the input field
        self.control_panel.start_input.clear()
        # Reset solution navigator
        self.solution_navigator.set_solution([])
        # Reset result panel
        self.result_panel.update_path([])
        self.result_panel.update_algo_desc("") # Clear description
        # Reset current solution
        self.current_solution = []
        # Reset stats label
        self.control_panel.stats_label.setText("Ready")
        self.statusBar().showMessage("States reset to default.")

# <<< Kết thúc thêm định nghĩa lớp PuzzleWindow >>>

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PuzzleWindow()
    window.show()
    sys.exit(app.exec())
