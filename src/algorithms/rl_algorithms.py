import numpy as np
import random
import time
import collections
from src.core.buzzle_logic import Buzzle, create_new_state

# Ensure the Buzzle class has a generate_random_state method
setattr(Buzzle, 'generate_random_state', 
        staticmethod(lambda: [list(row) for row in random.sample(list(map(tuple, 
                              [list(range(1,4)), list(range(4,7)), [7,8,0]])), 3)]))

# Định nghĩa hàm heuristic để ước lượng khoảng cách tới đích
def manhattan_distance(state):
    """
    Tính khoảng cách Manhattan từ trạng thái hiện tại tới trạng thái đích.
    Trạng thái đích: [[1,2,3], [4,5,6], [7,8,0]]
    """
    goal_positions = {
        0: (2, 2), 1: (0, 0), 2: (0, 1), 3: (0, 2),
        4: (1, 0), 5: (1, 1), 6: (1, 2), 7: (2, 0), 8: (2, 1)
    }
    
    distance = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:  # Bỏ qua ô trống
                goal_i, goal_j = goal_positions[state[i][j]]
                distance += abs(i - goal_i) + abs(j - goal_j)
    
    return distance

def misplaced_tiles(state):
    """
    Đếm số ô đặt sai vị trí so với trạng thái đích.
    """
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    count = 0
    
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0 and state[i][j] != goal[i][j]:
                count += 1
                
    return count

class QLearningAgent:
    """Agent học Q-learning cho puzzle 8-ô."""
    
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1, alpha_decay=0.99, epsilon_decay=0.99, min_alpha=0.01, min_epsilon=0.01):
        """
        Khởi tạo agent.
        
        Parameters:
        - alpha: Tỷ lệ học tập (learning rate)
        - gamma: Hệ số giảm (discount factor)
        - epsilon: Tham số khám phá (exploration parameter)
        - alpha_decay: Tốc độ giảm của alpha sau mỗi episode
        - epsilon_decay: Tốc độ giảm của epsilon sau mỗi episode
        - min_alpha: Giá trị tối thiểu của alpha
        - min_epsilon: Giá trị tối thiểu của epsilon
        """
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.alpha_decay = alpha_decay
        self.epsilon_decay = epsilon_decay
        self.min_alpha = min_alpha
        self.min_epsilon = min_epsilon
        self.q_table = {}  # Bảng Q để lưu giá trị Q(s,a)
        self.visited_states = set()  # Các trạng thái đã ghé thăm
        self.possible_moves = ["up", "down", "left", "right"]  # Các hành động có thể trong 8-puzzle
        self.experience_buffer = collections.deque(maxlen=1000)  # Buffer cho experience replay
        
    def get_q_value(self, state_tuple, action):
        """Lấy giá trị Q cho cặp trạng thái-hành động."""
        # state_tuple là tuple của tuple để có thể dùng làm key
        if (state_tuple, action) not in self.q_table:
            self.q_table[(state_tuple, action)] = 0.0
        return self.q_table[(state_tuple, action)]
    
    def get_max_q_value(self, state_tuple, possible_actions):
        """Lấy giá trị Q tối đa cho trạng thái hiện tại."""
        if not possible_actions:
            return 0.0
        return max(self.get_q_value(state_tuple, action) for action in possible_actions)
    
    def get_best_action(self, state_tuple, possible_actions):
        """Lấy hành động với giá trị Q tốt nhất (với epsilon-greedy)."""
        if not possible_actions:
            return None
            
        # Với xác suất epsilon, chọn ngẫu nhiên (khám phá)
        if random.random() < self.epsilon:
            return random.choice(possible_actions)
            
        # Tìm hành động có giá trị Q tốt nhất
        max_q = float("-inf")
        best_actions = []
        
        for action in possible_actions:
            q_value = self.get_q_value(state_tuple, action)
            if q_value > max_q:
                max_q = q_value
                best_actions = [action]
            elif q_value == max_q:
                best_actions.append(action)
                
        # Nếu có nhiều hành động có cùng giá trị Q tốt nhất, chọn ngẫu nhiên
        return random.choice(best_actions)
    
    def update_q_value(self, state_tuple, action, reward, next_state_tuple, possible_next_actions):
        """Cập nhật giá trị Q cho cặp (state, action)."""
        # Q(s,a) = Q(s,a) + alpha * [R + gamma * max_a' Q(s',a') - Q(s,a)]
        max_next_q = self.get_max_q_value(next_state_tuple, possible_next_actions)
        current_q = self.get_q_value(state_tuple, action)
        
        # Công thức cập nhật Q
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(state_tuple, action)] = new_q
    
    def experience_replay(self, batch_size=32):
        """Học từ kinh nghiệm quá khứ để cải thiện quá trình học tập."""
        if len(self.experience_buffer) < batch_size:
            return
            
        # Lấy mẫu ngẫu nhiên từ buffer
        batch = random.sample(self.experience_buffer, batch_size)
        
        for state_tuple, action, reward, next_state_tuple, possible_next_actions in batch:
            self.update_q_value(state_tuple, action, reward, next_state_tuple, possible_next_actions)
            
    def _get_reward(self, state, action, next_state):
        """
        Tính toán phần thưởng cho một hành động.
        
        Parameters:
        - state: Trạng thái hiện tại (2D list)
        - action: Hành động thực hiện
        - next_state: Trạng thái kết quả (2D list)
        
        Returns:
        - reward: Giá trị phần thưởng
        """
        # Sử dụng heuristic để tính toán phần thưởng
        current_dist = manhattan_distance(state)
        next_dist = manhattan_distance(next_state)
        
        # Nếu đến đích, thưởng lớn
        if Buzzle(next_state).is_goal():
            return 100.0
            
        # Nếu tiến gần đích hơn, thưởng nhỏ
        if next_dist < current_dist:
            return 1.0
            
        # Nếu đi xa đích hơn, phạt
        if next_dist > current_dist:
            return -1.0
            
        # Trường hợp đặc biệt: phạt nặng nếu quay lại trạng thái cũ (chu trình)
        if next_state == state:
            return -10.0
            
        # Phạt nhẹ để khuyến khích tìm đường ngắn nhất
        return -0.1
        
    def train(self, episodes=1000, max_steps=1000, use_experience_replay=True, batch_size=32):
        """
        Huấn luyện agent bằng cách chạy nhiều episode.
        
        Parameters:
        - episodes: Số lượng episode huấn luyện
        - max_steps: Số bước tối đa cho mỗi episode
        - use_experience_replay: Có sử dụng experience replay hay không
        - batch_size: Kích thước batch cho experience replay
        
        Returns:
        - stats: Thống kê về quá trình huấn luyện
        """
        start_time = time.time()
        stats = {
            'episodes': episodes,
            'episode_lengths': [],
            'episode_rewards': [],
            'steps_to_goal': [],
            'alpha_history': [],
            'epsilon_history': []
        }
        
        for episode in range(episodes):
            # Lưu lại alpha và epsilon hiện tại để theo dõi
            stats['alpha_history'].append(self.alpha)
            stats['epsilon_history'].append(self.epsilon)
            
            # Khởi tạo trạng thái bắt đầu
            puzzle = Buzzle()  # Sử dụng trạng thái mặc định hoặc ngẫu nhiên
            state_tuple = tuple(map(tuple, puzzle.data))
            total_reward = 0
            
            # Để theo dõi các trạng thái gần đây (tránh lặp)
            self._recent_states = collections.deque(maxlen=10)
            self._recent_states.append(puzzle.data)
            
            for step in range(max_steps):
                # Lấy các hành động có thể từ trạng thái hiện tại
                possible_actions = []
                for move in self.possible_moves:
                    success, _ = create_new_state(puzzle.data, move)
                    if success:
                        possible_actions.append(move)
                
                if not possible_actions:
                    break  # Không còn hành động khả thi
                
                # Chọn hành động (epsilon-greedy)
                action = self.get_best_action(state_tuple, possible_actions)
                
                # Thực hiện hành động
                success, next_data = create_new_state(puzzle.data, action)
                if not success:
                    continue
                
                next_puzzle = Buzzle(next_data)
                next_state_tuple = tuple(map(tuple, next_puzzle.data))
                
                # Tính toán phần thưởng
                reward = self._get_reward(puzzle.data, action, next_data)
                total_reward += reward
                
                # Lấy các hành động có thể từ trạng thái tiếp theo
                possible_next_actions = []
                for move in self.possible_moves:
                    success, _ = create_new_state(next_puzzle.data, move)
                    if success:
                        possible_next_actions.append(move)
                
                # Lưu trải nghiệm vào buffer
                if use_experience_replay:
                    self.experience_buffer.append((state_tuple, action, reward, next_state_tuple, possible_next_actions))
                
                # Cập nhật bảng Q
                self.update_q_value(state_tuple, action, reward, next_state_tuple, possible_next_actions)
                
                # Thực hiện experience replay
                if use_experience_replay and len(self.experience_buffer) >= batch_size:
                    self.experience_replay(batch_size)
                
                # Chuyển đến trạng thái tiếp theo
                puzzle = next_puzzle
                state_tuple = next_state_tuple
                self.visited_states.add(state_tuple)
                self._recent_states.append(puzzle.data)
                
                # Kiểm tra nếu đạt đến trạng thái đích
                if puzzle.is_goal():
                    stats['steps_to_goal'].append(step + 1)
                    break
            
            stats['episode_lengths'].append(step + 1)
            stats['episode_rewards'].append(total_reward)
            
            # Giảm alpha và epsilon theo lịch decay
            if self.alpha > self.min_alpha:
                self.alpha = max(self.min_alpha, self.alpha * self.alpha_decay)
            
            if self.epsilon > self.min_epsilon:
                self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        
        stats['training_time'] = time.time() - start_time
        stats['unique_states'] = len(self.visited_states)
        stats['q_table_size'] = len(self.q_table)
        stats['final_alpha'] = self.alpha
        stats['final_epsilon'] = self.epsilon
        
        return stats
    
    def solve(self, puzzle, max_steps=100):
        """
        Giải puzzle sử dụng chính sách đã học.
        
        Parameters:
        - puzzle: Trạng thái bắt đầu (Buzzle object)
        - max_steps: Số bước tối đa cho phép
        
        Returns:
        - path: Đường đi giải pháp (list các tuple (action, state_data))
        - steps: Số bước đã thực hiện
        - stats: Thống kê
        """
        path = []
        steps = 0
        current_puzzle = puzzle
        
        # Theo dõi trạng thái đã thăm và số lần thăm
        visited_states = {}
        # Theo dõi các hành động đã thử ở mỗi trạng thái
        tried_actions = {}
        
        while steps < max_steps:
            state_tuple = tuple(map(tuple, current_puzzle.data))
            
            # Kiểm tra đã đến đích chưa
            if current_puzzle.is_goal():
                break
            
            # Kiểm tra chu trình
            if state_tuple in visited_states:
                visited_states[state_tuple] += 1
                
                # Nếu đã thăm quá nhiều lần, tìm đường đi thay thế
                if visited_states[state_tuple] > 2:
                    print(f"Phát hiện chu trình tại bước {steps}, tìm hành động khác")
                    
                    # Lấy các hành động chưa thử cho trạng thái này
                    if state_tuple not in tried_actions:
                        tried_actions[state_tuple] = set()
                    
                    # Lấy tất cả các hành động hợp lệ
                    valid_moves = current_puzzle.get_valid_moves()
                    
                    # Lọc ra các hành động chưa thử
                    untried_moves = [move for move in valid_moves if move not in tried_actions[state_tuple]]
                    
                    if untried_moves:
                        # Chọn hành động chưa thử tốt nhất dựa trên heuristic
                        best_move = None
                        best_score = float('inf')
                        
                        for move in untried_moves:
                            success, next_state = create_new_state(current_puzzle.data, move)
                            if success:
                                score = manhattan_distance(next_state)
                                if score < best_score:
                                    best_score = score
                                    best_move = move
                        
                        if best_move:
                            # Đánh dấu đã thử hành động này
                            tried_actions[state_tuple].add(best_move)
                            
                            # Thực hiện hành động
                            success, next_state = create_new_state(current_puzzle.data, best_move)
                            if success:
                                path.append((best_move, next_state))
                                current_puzzle = Buzzle(next_state)
                                steps += 1
                                continue
                    
                    # Nếu không có hành động nào khả thi, quay lại một bước
                    if len(path) > 1:
                        path.pop()  # Loại bỏ bước cuối cùng
                        _, prev_state = path[-1]  # Lấy trạng thái trước đó
                        current_puzzle = Buzzle(prev_state)
                        continue
            else:
                visited_states[state_tuple] = 1
            
            # Lấy các hành động hợp lệ
            valid_moves = current_puzzle.get_valid_moves()
            if not valid_moves:
                break
            
            # Lấy hành động từ Q-table nếu có
            if state_tuple in self.q_table:
                q_values = self.q_table[state_tuple]
                
                # Lọc các hành động hợp lệ
                valid_q_actions = {move: q_values.get(move, 0) for move in valid_moves}
                
                # Chọn hành động tốt nhất
                if valid_q_actions:
                    action = max(valid_q_actions.items(), key=lambda x: x[1])[0]
                else:
                    # Nếu không có giá trị Q cho các hành động hợp lệ, sử dụng heuristic
                    best_move = None
                    best_score = float('inf')
                    
                    for move in valid_moves:
                        success, next_state = create_new_state(current_puzzle.data, move)
                        if success:
                            score = manhattan_distance(next_state)
                            if score < best_score:
                                best_score = score
                                best_move = move
                    
                    action = best_move if best_move else random.choice(valid_moves)
            else:
                # Nếu không có thông tin trong Q-table, sử dụng heuristic
                best_move = None
                best_score = float('inf')
                
                for move in valid_moves:
                    success, next_state = create_new_state(current_puzzle.data, move)
                    if success:
                        score = manhattan_distance(next_state)
                        if score < best_score:
                            best_score = score
                            best_move = move
                
                action = best_move if best_move else random.choice(valid_moves)
            
            # Thực hiện hành động
            success, next_state = create_new_state(current_puzzle.data, action)
            if not success:
                continue
            
            # Cập nhật đường đi và trạng thái
            path.append((action, next_state))
            current_puzzle = Buzzle(next_state)
            steps += 1
            
            # Đánh dấu đã thử hành động này
            if state_tuple not in tried_actions:
                tried_actions[state_tuple] = set()
            tried_actions[state_tuple].add(action)
        
        # Thống kê
        stats = {
            'steps': steps,
            'path_length': len(path),
            'success': current_puzzle.is_goal(),
            'visited_states': len(visited_states)
        }
        
        return path, steps, stats
    
    def get_utility_map(self):
        """
        Tạo bản đồ giá trị utility cho các trạng thái đã thăm.
        U(s) = max_a Q(s,a)
        
        Returns:
        - utility_map: Dictionary map từ trạng thái đến giá trị utility
        """
        utility_map = {}
        
        # Nhóm các cặp (state, action) theo state
        states_actions = {}
        for (state, action) in self.q_table:
            if state not in states_actions:
                states_actions[state] = []
            states_actions[state].append(action)
            
        # Tính giá trị utility cho mỗi trạng thái
        for state, actions in states_actions.items():
            utility_map[state] = max(self.get_q_value(state, action) for action in actions)
            
        return utility_map

def count_misplaced_tiles(state_data):
    """Đếm số ô sai vị trí so với trạng thái đích."""
    goal = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    count = 0
    
    for i in range(3):
        for j in range(3):
            if state_data[i][j] != 0 and state_data[i][j] != goal[i][j]:
                count += 1
                
    return count

def calculate_manhattan_distance(state_data):
    """Tính tổng khoảng cách Manhattan từ hiện tại đến đích."""
    goal_positions = {
        1: (0, 0), 2: (0, 1), 3: (0, 2),
        4: (1, 0), 5: (1, 1), 6: (1, 2),
        7: (2, 0), 8: (2, 1), 0: (2, 2)
    }
    
    distance = 0
    for i in range(3):
        for j in range(3):
            tile = state_data[i][j]
            if tile != 0:  # Bỏ qua ô trống
                goal_i, goal_j = goal_positions[tile]
                distance += abs(i - goal_i) + abs(j - goal_j)
                
    return distance

def value_iteration(gamma=0.9, iterations=100, max_states_to_explore=10000, theta=0.01):
    """
    Thuật toán Value Iteration cho 8-puzzle.
    
    Parameters:
    - gamma: Hệ số giảm (discount factor)
    - iterations: Số lần lặp tối đa
    - max_states_to_explore: Số trạng thái tối đa để khám phá
    - theta: Ngưỡng hội tụ
    
    Returns:
    - utilities: Bản đồ giá trị
    - policy: Chính sách
    - stats: Thống kê
    """
    # Khởi tạo utilities và policy
    utilities = {}
    policy = {}
    
    # Thêm trạng thái đích vào utilities
    goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    goal_tuple = tuple(map(tuple, goal_state))
    utilities[goal_tuple] = 100.0  # Giá trị cao cho trạng thái đích
    
    # Khởi tạo hàng đợi trạng thái cần khám phá
    states_to_explore = collections.deque([goal_state])
    explored_states = {goal_tuple}
    
    # Thêm các trạng thái đơn giản gần đích
    print("Adding extra states for simple puzzles...")
    simple_states_added = 0
    for _ in range(50):  # Thêm một số trạng thái đơn giản
        simple_puzzle = Buzzle(goal_state)
        # Thực hiện một số bước ngẫu nhiên từ trạng thái đích
        for _ in range(random.randint(1, 5)):
            moves = simple_puzzle.get_valid_moves()
            if not moves:
                break
            action = random.choice(moves)
            success, new_state = create_new_state(simple_puzzle.data, action)
            if success:
                simple_puzzle = Buzzle(new_state)
                
        state_tuple = tuple(map(tuple, simple_puzzle.data))
        if state_tuple not in explored_states:
            explored_states.add(state_tuple)
            states_to_explore.append(simple_puzzle.data)
            # Khởi tạo giá trị dựa trên khoảng cách Manhattan
            dist = manhattan_distance(simple_puzzle.data)
            utilities[state_tuple] = max(0, 100 - 5 * dist)
            simple_states_added += 1
    
    print(f"Added {simple_states_added} simple states near the goal")
    
    # Khám phá không gian trạng thái
    while states_to_explore and len(explored_states) < max_states_to_explore:
        current_state = states_to_explore.popleft()
        current_puzzle = Buzzle(current_state)
        
        # Lấy các hành động hợp lệ
        valid_moves = current_puzzle.get_valid_moves()
        
        for action in valid_moves:
            success, next_state = create_new_state(current_state, action)
            if not success:
                continue
                
            next_tuple = tuple(map(tuple, next_state))
            
            # Nếu trạng thái mới chưa được khám phá
            if next_tuple not in explored_states:
                explored_states.add(next_tuple)
                states_to_explore.append(next_state)
                
                # Khởi tạo giá trị dựa trên khoảng cách Manhattan
                dist = manhattan_distance(next_state)
                utilities[next_tuple] = max(0, 100 - 5 * dist)
    
    # Value Iteration
    for i in range(iterations):
        delta = 0
        for state_tuple in list(utilities.keys()):
            if state_tuple == goal_tuple:
                continue
                
            state = [list(row) for row in state_tuple]
            current_puzzle = Buzzle(state)
            valid_moves = current_puzzle.get_valid_moves()
            
            if not valid_moves:
                continue
                
            old_value = utilities[state_tuple]
            action_values = []
            
            for action in valid_moves:
                success, next_state = create_new_state(state, action)
                if not success:
                    continue
                    
                next_tuple = tuple(map(tuple, next_state))
                
                # Nếu trạng thái tiếp theo không có trong utilities, bỏ qua
                if next_tuple not in utilities:
                    continue
                
                # Tính phần thưởng
                reward = 0
                if next_tuple == goal_tuple:
                    reward = 100
                else:
                    # Sử dụng heuristic để tính phần thưởng
                    current_dist = manhattan_distance(state)
                    next_dist = manhattan_distance(next_state)
                    
                    if next_dist < current_dist:
                        reward = 1.0
                    elif next_dist > current_dist:
                        reward = -1.0
                    else:
                        reward = -0.1
                
                action_values.append((action, reward + gamma * utilities[next_tuple]))
            
            if action_values:
                best_action, best_value = max(action_values, key=lambda x: x[1])
                utilities[state_tuple] = best_value
                policy[state_tuple] = best_action
                
                delta = max(delta, abs(old_value - best_value))
        
        # Kiểm tra hội tụ
        if delta < theta:
            break
    
    # Thống kê
    stats = {
        'iterations': iterations,
        'states_explored': len(explored_states),
        'utilities': len(utilities),
        'policy': len(policy)
    }
    
    return utilities, policy, stats

def solve_with_value_iteration(puzzle, utilities, policy, max_steps=100):
    """
    Giải puzzle sử dụng chính sách từ Value Iteration.
    
    Parameters:
    - puzzle: Trạng thái bắt đầu (Buzzle object)
    - utilities: Bản đồ giá trị từ value iteration
    - policy: Chính sách từ value iteration
    - max_steps: Số bước tối đa cho phép
    
    Returns:
    - path: Đường đi giải pháp (list các tuple (action, state_data))
    - steps: Số bước đã thực hiện
    """
    path = []
    steps = 0
    current_puzzle = puzzle
    possible_moves = ["up", "down", "left", "right"]
    
    # Theo dõi trạng thái đã thăm và số lần thăm
    visited_states = {}
    # Theo dõi các hành động đã thử cho mỗi trạng thái
    tried_actions = {}
    
    while steps < max_steps:
        state_tuple = tuple(map(tuple, current_puzzle.data))
        
        # Kiểm tra đã đến đích chưa
        if current_puzzle.is_goal():
            break
            
        # Kiểm tra chu trình
        if state_tuple in visited_states:
            visited_states[state_tuple] += 1
            
            # Nếu đã thăm quá nhiều lần, tìm đường đi thay thế
            if visited_states[state_tuple] > 2:
                print(f"Phát hiện chu trình tại bước {steps}, tìm đường đi thay thế")
                
                # Lấy các hành động chưa thử cho trạng thái này
                if state_tuple not in tried_actions:
                    tried_actions[state_tuple] = set()
                
                # Lấy tất cả các hành động hợp lệ
                valid_moves = current_puzzle.get_valid_moves()
                
                # Lọc ra các hành động chưa thử
                untried_moves = [move for move in valid_moves if move not in tried_actions[state_tuple]]
                
                if untried_moves:
                    # Chọn hành động chưa thử tốt nhất dựa trên heuristic
                    best_move = None
                    best_score = float('inf')
                    
                    for move in untried_moves:
                        success, next_state = create_new_state(current_puzzle.data, move)
                        if success:
                            score = manhattan_distance(next_state)
                            if score < best_score:
                                best_score = score
                                best_move = move
                    
                    if best_move:
                        # Đánh dấu đã thử hành động này
                        tried_actions[state_tuple].add(best_move)
                        
                        # Thực hiện hành động
                        success, next_state = create_new_state(current_puzzle.data, best_move)
                        if success:
                            path.append((best_move, next_state))
                            current_puzzle = Buzzle(next_state)
                            steps += 1
                            continue
                
                # Nếu không có hành động nào khả thi, quay lại một bước
                if len(path) > 1:
                    path.pop()  # Loại bỏ bước cuối cùng
                    _, prev_state = path[-1]  # Lấy trạng thái trước đó
                    current_puzzle = Buzzle(prev_state)
                    continue
        else:
            visited_states[state_tuple] = 1
            
        # Sử dụng chính sách nếu có
        if state_tuple in policy:
            action = policy[state_tuple]
        else:
            # Nếu không có chính sách, sử dụng heuristic
            valid_moves = current_puzzle.get_valid_moves()
            if not valid_moves:
                break
                
            # Chọn hành động tốt nhất dựa trên heuristic
            best_move = None
            best_score = float('inf')
            
            for move in valid_moves:
                success, next_state = create_new_state(current_puzzle.data, move)
                if success:
                    score = manhattan_distance(next_state)
                    if score < best_score:
                        best_score = score
                        best_move = move
            
            if best_move:
                action = best_move
            else:
                # Không có hành động khả thi
                break
        
        # Thực hiện hành động
        success, next_state = create_new_state(current_puzzle.data, action)
        if not success:
            # Nếu không thành công, thử hành động khác
            continue
            
        # Cập nhật đường đi và trạng thái
        path.append((action, next_state))
        current_puzzle = Buzzle(next_state)
        steps += 1
        
        # Đánh dấu đã thử hành động này
        if state_tuple not in tried_actions:
            tried_actions[state_tuple] = set()
        tried_actions[state_tuple].add(action)
    
    return path, steps 