from collections import deque
import heapq
import time

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
        print("Nhap trang thai: ")
        for i in range(3):
            for j in range(3):
                x = int(input(f"Nhap data[{i},{j}]: "))
                self.data[i][j] = x
    
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

def bfs(initial_state):
    """Breadth First Search"""
    frontier = deque([(initial_state.data, [])])  # (state_data, path)
    explored = set([str(initial_state.data)])
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
                explored.add(str(new_data))
                frontier.append((new_data, path + [(move, new_data)]))
                
    return [], nodes_expanded, max_frontier_size

def dfs(initial_state):
    """Depth First Search"""
    frontier = [(initial_state.data, [])]  # (state_data, path)
    explored = set([str(initial_state.data)])
    nodes_expanded = 0
    max_frontier_size = 1
    
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        current_data, path = frontier.pop()
        nodes_expanded += 1
        
        if Buzzle(current_data).is_goal():
            return path, nodes_expanded, max_frontier_size
            
        for move in reversed(["up", "down", "left", "right"]):  # Reverse để duy trì thứ tự DFS
            success, new_data = create_new_state(current_data, move)
            if success and str(new_data) not in explored:
                explored.add(str(new_data))
                frontier.append((new_data, path + [(move, new_data)]))
                
    return [], nodes_expanded, max_frontier_size

def astar(initial_state):
    """A* Search với Manhattan distance"""
    frontier = [(0, 0, initial_state.data, [])]  # (f_value, counter, state_data, path)
    explored = set([str(initial_state.data)])
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
                explored.add(str(new_data))
                new_path = path + [(move, new_data)]
                g_value = len(new_path)  # chi phí đường đi
                h_value = manhattan_distance(Buzzle(new_data))  # ước lượng heuristic
                f_value = g_value + h_value
                heapq.heappush(frontier, (f_value, counter, new_data, new_path))
                counter += 1
                
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
            if value != 0:
                goal_i, goal_j = goal_positions[value]
                distance += abs(i - goal_i) + abs(j - goal_j)
    return distance

def ucs(initial_state):
    """Uniform Cost Search - tìm kiếm theo chi phí đồng nhất"""
    frontier = [(0, 0, initial_state.data, [])]  # (cost, counter, state_data, path)
    explored = set([str(initial_state.data)])
    nodes_expanded = 0
    max_frontier_size = 1
    counter = 1
    
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        cost, _, current_data, path = heapq.heappop(frontier)
        nodes_expanded += 1
        
        if Buzzle(current_data).is_goal():
            return path, nodes_expanded, max_frontier_size
            
        for move in ["up", "down", "left", "right"]:
            success, new_data = create_new_state(current_data, move)
            if success and str(new_data) not in explored:
                explored.add(str(new_data))
                new_path = path + [(move, new_data)]
                new_cost = len(new_path)  # Chi phí = số bước đi
                heapq.heappush(frontier, (new_cost, counter, new_data, new_path))
                counter += 1
                
    return [], nodes_expanded, max_frontier_size

def greedy(initial_state):
    """Greedy Best-First Search - chỉ sử dụng heuristic"""
    frontier = [(manhattan_distance(Buzzle(initial_state.data)), 0, initial_state.data, [])]
    explored = set([str(initial_state.data)])
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
                explored.add(str(new_data))
                new_path = path + [(move, new_data)]
                h_value = manhattan_distance(Buzzle(new_data))
                heapq.heappush(frontier, (h_value, counter, new_data, new_path))
                counter += 1
                
    return [], nodes_expanded, max_frontier_size

def dfs_limited(initial_state, depth_limit):
    """DFS với giới hạn độ sâu"""
    frontier = [(initial_state.data, [], 0)]  # (state_data, path, depth)
    explored = set([str(initial_state.data)])
    nodes_expanded = 0
    max_frontier_size = 1
    
    while frontier:
        max_frontier_size = max(max_frontier_size, len(frontier))
        current_data, path, depth = frontier.pop()
        nodes_expanded += 1
        
        if depth > depth_limit:
            continue
            
        if Buzzle(current_data).is_goal():
            return True, path, nodes_expanded, max_frontier_size
            
        for move in reversed(["up", "down", "left", "right"]):
            success, new_data = create_new_state(current_data, move)
            if success and str(new_data) not in explored:
                explored.add(str(new_data))
                frontier.append((new_data, path + [(move, new_data)], depth + 1))
                
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

def solve_puzzle(algorithm, start_state):
    """Unified interface for all search algorithms"""
    algorithms = {
        "bfs": bfs,
        "dfs": dfs,
        "ucs": ucs,
        "astar": astar,
        "greedy": greedy,
        "ids": ids
    }
    return algorithms.get(algorithm, bfs)(start_state)

def print_solution(path):
    if not path:
        print("Không tìm thấy lời giải!")
        return
    
    print("Các bước di chuyển:")
    for i, (move, state) in enumerate(path, 1):
        print(f"Bước {i}: {move}")
        Buzzle(state).print_state()
    print(f"Tổng số bước: {len(path)}")

# Main execution
if __name__ == "__main__":
    A = Buzzle()
    A.entry_state()
    A.print_state()
    solution, nodes, fringe = solve_puzzle("bfs", A)
    if solution:
        print_solution(solution)
        print(f"Nodes expanded: {nodes}")
        print(f"Max fringe size: {fringe}")
    else:
        print("No solution found!")