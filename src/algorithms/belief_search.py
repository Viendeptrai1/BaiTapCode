from collections import deque
import itertools
import numpy as np
from src.core.buzzle_logic import Buzzle, create_new_state, is_solvable
import random

def get_possible_states(observation):
    """
    Tạo tất cả các trạng thái khả thi dựa trên quan sát 
    
    Args:
        observation: Mảng các giá trị quan sát được
    
    Returns:
        List các trạng thái Buzzle khả thi
    """
    # Kiểm tra số lượng ô quan sát
    num_observed = len(observation)
    
    if num_observed == 6:
        # Quan sát 6 ô: [0,0], [0,1], [0,2], [1,0], [1,1], [1,2]
        possible_states = []
        missing = [i for i in range(9) if i not in observation]
        
        # Tạo tất cả các hoán vị của missing
        for p1 in missing:
            for p2 in missing:
                if p1 == p2:
                    continue
                for p3 in missing:
                    if p1 == p3 or p2 == p3:
                        continue
                    
                    # Tạo trạng thái mới với các ô đã quan sát và các ô còn lại
                    state_data = [
                        [observation[0], observation[1], observation[2]],
                        [observation[3], observation[4], observation[5]],
                        [p1, p2, p3]
                    ]
                    
                    # Kiểm tra xem trạng thái có hợp lệ không (chỉ có một số 0)
                    if sum(row.count(0) for row in state_data) == 1:
                        possible_states.append(Buzzle(state_data))
        
        return possible_states
    
    elif num_observed == 5:
        # Quan sát 5 ô: [0,0], [0,1], [0,2], [1,0], [1,1]
        possible_states = []
        missing = [i for i in range(9) if i not in observation]
        
        # Tạo tất cả các hoán vị của missing
        for p1 in missing:
            for p2 in missing:
                if p1 == p2:
                    continue
                for p3 in missing:
                    if p1 == p3 or p2 == p3:
                        continue
                    for p4 in missing:
                        if p1 == p4 or p2 == p4 or p3 == p4:
                            continue
                        
                        # Tạo trạng thái mới với các ô đã quan sát và các ô còn lại
                        state_data = [
                            [observation[0], observation[1], observation[2]],
                            [observation[3], observation[4], p1],
                            [p2, p3, p4]
                        ]
                        
                        # Kiểm tra xem trạng thái có hợp lệ không (chỉ có một số 0)
                        if sum(row.count(0) for row in state_data) == 1:
                            possible_states.append(Buzzle(state_data))
        
        return possible_states
        
    elif num_observed == 3:
        # Quan sát 3 ô: [0,0], [0,1], [0,2]
        possible_states = []
        missing = [i for i in range(9) if i not in observation]
        
        # Generate all permutations of missing tiles
        for p in generate_permutations(missing):
            # Create a new state with observed and missing tiles
            state_data = [
                [observation[0], observation[1], observation[2]],
                [p[0], p[1], p[2]],
                [p[3], p[4], p[5]]
            ]
            
            # Check if the state is valid (has exactly one zero)
            if sum(row.count(0) for row in state_data) == 1:
                possible_states.append(Buzzle(state_data))
        
        return possible_states
    
    else:
        raise ValueError("Chỉ hỗ trợ quan sát 3, 5 hoặc 6 ô")

def is_valid_action(state, action):
    """
    Kiểm tra xem một hành động có hợp lệ cho trạng thái không
    
    Args:
        state: Đối tượng Buzzle
        action: Hành động ("up", "down", "left", "right")
    
    Returns:
        True nếu hành động hợp lệ, False nếu không
    """
    # Lấy vị trí của ô trống (số 0)
    zero_row, zero_col = None, None
    for r in range(3):
        for c in range(3):
            if state.data[r][c] == 0:
                zero_row, zero_col = r, c
                break
        if zero_row is not None:
            break
    
    # Kiểm tra tính hợp lệ dựa trên vị trí của ô trống
    if action == "up":
        return zero_row < 2  # Không thể di chuyển lên nếu ô trống ở hàng cuối cùng
    elif action == "down":
        return zero_row > 0  # Không thể di chuyển xuống nếu ô trống ở hàng đầu tiên
    elif action == "left":
        return zero_col < 2  # Không thể di chuyển sang trái nếu ô trống ở cột cuối cùng
    elif action == "right":
        return zero_col > 0  # Không thể di chuyển sang phải nếu ô trống ở cột đầu tiên
    else:
        return False  # Hành động không hợp lệ

def apply_action(state, action):
    """
    Áp dụng hành động lên trạng thái và trả về trạng thái mới
    
    Args:
        state: Đối tượng Buzzle
        action: Hành động ("up", "down", "left", "right")
    
    Returns:
        Trạng thái Buzzle mới sau khi áp dụng hành động
    """
    # Tạo bản sao của dữ liệu trạng thái để không thay đổi trạng thái ban đầu
    new_data = [row[:] for row in state.data]
    
    # Tìm vị trí của ô trống (số 0)
    zero_row, zero_col = None, None
    for r in range(3):
        for c in range(3):
            if new_data[r][c] == 0:
                zero_row, zero_col = r, c
                break
        if zero_row is not None:
            break
    
    # Áp dụng hành động
    if action == "up" and zero_row < 2:
        # Di chuyển ô dưới lên trên (ô trống xuống dưới)
        new_data[zero_row][zero_col] = new_data[zero_row + 1][zero_col]
        new_data[zero_row + 1][zero_col] = 0
    elif action == "down" and zero_row > 0:
        # Di chuyển ô trên xuống dưới (ô trống lên trên)
        new_data[zero_row][zero_col] = new_data[zero_row - 1][zero_col]
        new_data[zero_row - 1][zero_col] = 0
    elif action == "left" and zero_col < 2:
        # Di chuyển ô bên phải sang trái (ô trống sang phải)
        new_data[zero_row][zero_col] = new_data[zero_row][zero_col + 1]
        new_data[zero_row][zero_col + 1] = 0
    elif action == "right" and zero_col > 0:
        # Di chuyển ô bên trái sang phải (ô trống sang trái)
        new_data[zero_row][zero_col] = new_data[zero_row][zero_col - 1]
        new_data[zero_row][zero_col - 1] = 0
    
    return Buzzle(new_data)

def hash_belief_state(belief_state):
    """
    Tạo một hash cho belief state để kiểm tra đã duyệt
    
    Args:
        belief_state: Tập hợp các trạng thái Buzzle
    
    Returns:
        Một frozenset chứa các tuples đại diện cho các trạng thái
    """
    # Chuyển mỗi trạng thái Buzzle thành tuple để có thể hash
    state_tuples = frozenset(tuple(map(tuple, state.data)) for state in belief_state)
    return state_tuples

def get_belief_states_str(belief_states, max_display=5):
    """
    Tạo chuỗi biểu diễn cho tập trạng thái niềm tin
    
    Args:
        belief_states: Tập hợp các trạng thái Buzzle
        max_display: Số trạng thái tối đa để hiển thị
    
    Returns:
        Chuỗi biểu diễn các trạng thái
    """
    result = []
    count = 0
    
    # Chuyển đổi từ frozenset sang list nếu cần
    states_list = list(belief_states)
    
    # Hiển thị các trạng thái đầu tiên
    for state in states_list[:max_display]:
        count += 1
        result.append(f"State {count}:")
        for row in state.data:
            result.append(str(row))
        result.append("")
    
    # Nếu có nhiều hơn max_display trạng thái
    if len(states_list) > max_display:
        result.append(f"... và {len(states_list) - max_display} trạng thái khác")
    
    return "\n".join(result)

def generate_permutations(elements):
    """
    Tạo tất cả các hoán vị của một tập hợp các phần tử
    
    Args:
        elements: Danh sách các phần tử
    
    Returns:
        Danh sách các hoán vị
    """
    if len(elements) <= 1:
        return [elements]
    
    result = []
    for i, e in enumerate(elements):
        rest = elements[:i] + elements[i+1:]
        for p in generate_permutations(rest):
            result.append([e] + p)
    
    return result

def get_observation(state, num_cells=6):
    """
    Hàm lấy quan sát từ một trạng thái
    
    Args:
        state: Trạng thái Buzzle
        num_cells: Số ô được quan sát (mặc định là 6)
        
    Returns:
        Danh sách các ô được quan sát
    """
    if num_cells == 3:
        return state.data[0]  # Chỉ trả về hàng đầu tiên
    elif num_cells == 5:
        # Trả về hàng đầu tiên và 2 ô đầu của hàng thứ 2
        return state.data[0] + state.data[1][:2]
    elif num_cells == 6:
        # Trả về hàng đầu tiên và toàn bộ hàng thứ 2
        return state.data[0] + state.data[1]
    else:
        raise ValueError("Chỉ hỗ trợ quan sát 3, 5 hoặc 6 ô")

def belief_bfs(initial_belief_state, goal_test, debug=False):
    """
    Thuật toán tìm kiếm theo chiều rộng dựa trên niềm tin (Belief-Based BFS)
    cho bài toán 8-puzzle với thông tin một phần. Thuật toán duy trì một tập
    trạng thái niềm tin mà không cần quan sát thêm sau trạng thái ban đầu.
    
    Args:
        initial_belief_state: Tập hợp các trạng thái Buzzle có thể có (hoặc danh sách)
        goal_test: Hàm kiểm tra mục tiêu (nhận vào một trạng thái Buzzle)
        debug: Bật/tắt chế độ debug
    
    Returns:
        (path, visited_nodes, max_fringe, debug_info): (đường đi, số node đã thăm, 
        kích thước fringe tối đa, thông tin debug)
    """
    # Chuyển đổi danh sách thành tập hợp nếu cần
    if isinstance(initial_belief_state, list):
        initial_belief_state = set(initial_belief_state)
    
    # Khởi tạo thông tin debug
    debug_info = {"belief_states": []} if debug else None
    
    # Các hành động có thể thực hiện
    actions = ["up", "down", "left", "right"]
    
    # Khởi tạo frontier với trạng thái ban đầu, đường đi rỗng
    frontier = [(initial_belief_state, [])]
    
    # Tập hợp các trạng thái đã thăm (để tránh lặp lại)
    explored = set()
    explored.add(hash_belief_state(initial_belief_state))
    
    # Số node đã thăm và kích thước fringe tối đa
    visited_nodes = 1
    max_fringe = 1
    
    if debug:
        debug_info["belief_states"].append(f"Trạng thái niềm tin ban đầu ({len(initial_belief_state)} trạng thái có thể):")
        debug_info["belief_states"].append(get_belief_states_str(initial_belief_state))
    
    while frontier:
        # Lấy trạng thái hiện tại từ frontier
        current_belief_state, current_path = frontier.pop(0)
        
        # Kiểm tra mục tiêu trong các trạng thái niềm tin
        goal_states = []
        for state in current_belief_state:
            if goal_test(state):
                goal_states.append(state)
        
        if goal_states:
            if debug:
                debug_info["belief_states"].append(f"Đã tìm thấy {len(goal_states)} trạng thái mục tiêu!")
                debug_info["belief_states"].append(get_belief_states_str(goal_states))
            return current_path, visited_nodes, max_fringe, debug_info
        
        # Thử mỗi hành động
        for action in actions:
            # Áp dụng hành động cho tất cả các trạng thái trong niềm tin hiện tại
            next_belief_state = set()
            valid_action_exists = False
            
            for state in current_belief_state:
                # Kiểm tra xem hành động có hợp lệ không
                if is_valid_action(state, action):
                    valid_action_exists = True
                    # Áp dụng hành động và thêm trạng thái mới vào tập niềm tin mới
                    next_state = apply_action(state, action)
                    next_belief_state.add(next_state)
            
            # Nếu không có trạng thái niềm tin mới (tất cả hành động đều không hợp lệ)
            if not valid_action_exists or not next_belief_state:
                continue
            
            # Tạo hash cho trạng thái niềm tin mới để kiểm tra đã thăm
            next_hash = hash_belief_state(next_belief_state)
            
            # Nếu trạng thái niềm tin mới chưa được thăm
            if next_hash not in explored:
                # Thêm vào danh sách đã thăm
                explored.add(next_hash)
                
                # Thêm vào frontier với đường đi cập nhật
                next_path = current_path + [action]  # Chỉ lưu hành động
                frontier.append((next_belief_state, next_path))
                
                # Cập nhật số node đã thăm và kích thước fringe tối đa
                visited_nodes += 1
                max_fringe = max(max_fringe, len(frontier))
                
                if debug:
                    debug_info["belief_states"].append(f"Bước {len(current_path) + 1}: Thực hiện hành động {action.upper()}")
                    debug_info["belief_states"].append(f"Kết quả: {len(next_belief_state)} trạng thái có thể")
                    debug_info["belief_states"].append(get_belief_states_str(next_belief_state))
    
    # Không tìm thấy đường đi
    return None, visited_nodes, max_fringe, debug_info 