"""
Implementation of AND-OR graph search for a non-deterministic 2x2 puzzle.
The puzzle has two possible outcomes for each action:
1. The intended tile moves.
2. An adjacent tile (the 'other' one) slips into the blank space.
"""

import copy # Potentially useful, but direct manipulation might be cleaner

FAILURE = None
EMPTY_PLAN = [] # Represents an empty plan (e.g., when goal is reached)
# DEBUG_AND_OR_SEARCH = True # Set to True to enable verbose logging

class NonDeterministicPuzzle:
    """
    Represents a 2x2 non-deterministic puzzle.
    States are represented as tuple of tuples, e.g., ((1, 2), (3, 0)).
    Actions are the (row, col) of the tile intended to be moved into the blank.
    """
    def __init__(self, initial_matrix, goal_matrix, size=2):
        if not (isinstance(initial_matrix, list) and \
                all(isinstance(row, list) for row in initial_matrix) and \
                len(initial_matrix) == size and \
                all(len(row) == size for row in initial_matrix)):
            raise ValueError(f"Initial matrix must be a {size}x{size} list of lists.")
        
        if not (isinstance(goal_matrix, list) and \
                all(isinstance(row, list) for row in goal_matrix) and \
                len(goal_matrix) == size and \
                all(len(row) == size for row in goal_matrix)):
            raise ValueError(f"Goal matrix must be a {size}x{size} list of lists.")

        self.initial_state = tuple(map(tuple, initial_matrix))
        self.goal_state = tuple(map(tuple, goal_matrix))
        self.size = size
        
        # Validate content of states
        expected_tiles = set(range(size * size))
        initial_tiles = set(tile for row in self.initial_state for tile in row)
        goal_tiles = set(tile for row in self.goal_state for tile in row)

        if initial_tiles != expected_tiles:
            raise ValueError(f"Initial state must contain all tiles from 0 to {size*size -1}. Found: {initial_tiles}")
        if 0 not in initial_tiles:
            raise ValueError("Initial state must contain a blank tile (0).")
        if goal_tiles != expected_tiles:
            raise ValueError(f"Goal state must contain all tiles from 0 to {size*size -1}. Found: {goal_tiles}")
        if 0 not in goal_tiles:
            raise ValueError("Goal state must contain a blank tile (0).")

        self.log_func = lambda x: None # Default no-op logger

    def set_logger(self, logger_func):
        """Sets a custom logging function."""
        self.log_func = logger_func if callable(logger_func) else lambda x: None

    def _find_blank(self, state_tuple):
        """Finds the (row, col) of the blank tile (0) in a state."""
        for r in range(self.size):
            for c in range(self.size):
                if state_tuple[r][c] == 0:
                    return r, c
        # This should not be reached if states are validated to contain a 0
        raise ValueError("Blank tile (0) not found in state. This should not happen.")

    def is_goal(self, state_tuple):
        """Checks if the given state is the goal state."""
        return state_tuple == self.goal_state

    def actions(self, state_tuple):
        """
        Returns a list of possible intended actions from the current state.
        An action is represented by the (row, col) of the tile to be moved 
        into the blank space.
        """
        br, bc = self._find_blank(state_tuple)
        possible_actions = []
        # Iterate over neighbors of the blank space
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            tr, tc = br + dr, bc + dc  # Potential tile's coordinates
            if 0 <= tr < self.size and 0 <= tc < self.size:
                # This tile at (tr, tc) can be moved into the blank at (br, bc)
                possible_actions.append((tr, tc)) 
        return possible_actions

    def _get_direction_name(self, action_pos, blank_pos):
        """Trả về tên hướng di chuyển của ô trống dựa trên vị trí của ô được di chuyển.
        
        Args:
            action_pos: Tọa độ (r,c) của ô được di chuyển
            blank_pos: Tọa độ (r,c) của ô trống
        
        Returns:
            String: "Phải", "Trái", "Lên", "Xuống" hoặc "(không xác định)"
        """
        tr, tc = action_pos  # Ô được di chuyển
        br, bc = blank_pos  # Ô trống
        
        # Xác định hướng di chuyển của ô trống
        if tr == br:  # Cùng hàng, di chuyển ngang
            if tc < bc:  # Ô được di chuyển nằm bên trái ô trống
                return "Trái"  # Ô trống di chuyển sang trái
            else:  # Ô được di chuyển nằm bên phải ô trống
                return "Phải"  # Ô trống di chuyển sang phải
        elif tc == bc:  # Cùng cột, di chuyển dọc
            if tr < br:  # Ô được di chuyển nằm phía trên ô trống
                return "Lên"  # Ô trống di chuyển lên trên
            else:  # Ô được di chuyển nằm phía dưới ô trống
                return "Xuống"  # Ô trống di chuyển xuống dưới
        
        return "(không xác định)"  # Trường hợp không xác định được
    
    def _action_to_string(self, action_pos, state_tuple):
        """Chuyển đổi hành động từ tọa độ sang chuỗi mô tả hướng di chuyển."""
        blank_pos = self._find_blank(state_tuple)
        direction = self._get_direction_name(action_pos, blank_pos)
        tile_value = state_tuple[action_pos[0]][action_pos[1]]
        return f"di chuyển ô {tile_value} {direction}"

    def results(self, state_tuple, action_intended_tile_pos):
        """
        Returns a list of possible resulting states (tuple of tuples) 
        for a given intended action.

        MODIFIED FOR "ADJACENT SLIP":
        1. Normal outcome: The intended tile moves into the blank.
        2. Slip outcome: Instead of the intended tile, another adjacent tile 
           to the blank slips into the blank position.
        
        Args:
            state_tuple: The current state of the puzzle.
            action_intended_tile_pos: (tr, tc) of the tile intended to move.
        """
        
        outcomes = []
        current_matrix_list_of_lists = [list(row) for row in state_tuple]

        tr, tc = action_intended_tile_pos  # Tile's original row and column (intended to move)
        br, bc = self._find_blank(state_tuple)  # Blank's row and column

        # 1. Normal Outcome
        matrix_normal = [row[:] for row in current_matrix_list_of_lists]
        matrix_normal[br][bc], matrix_normal[tr][tc] = matrix_normal[tr][tc], matrix_normal[br][bc]
        normal_outcome = tuple(map(tuple, matrix_normal))
        outcomes.append(normal_outcome)

        # 2. Adjacent Slip Outcome: Find other tiles adjacent to blank (not the intended one)
        adjacent_tiles = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # Four directions
            adj_r, adj_c = br + dr, bc + dc  # Position adjacent to blank
            # Check if position is valid and not the intended tile
            if (0 <= adj_r < self.size and 0 <= adj_c < self.size and 
                (adj_r, adj_c) != (tr, tc)):
                adjacent_tiles.append((adj_r, adj_c))
        
        # Default to no change if no other adjacent tiles (should be rare in 2x2)
        slip_outcome = state_tuple
        
        if adjacent_tiles:
            # For deterministic testing, choose first available adjacent tile
            # Could be made random with: random.choice(adjacent_tiles)
            slip_r, slip_c = adjacent_tiles[0]
            
            # Create slip outcome: the other adjacent tile moves into blank
            matrix_slip = [row[:] for row in current_matrix_list_of_lists]
            matrix_slip[br][bc], matrix_slip[slip_r][slip_c] = matrix_slip[slip_r][slip_c], matrix_slip[br][bc]
            slip_outcome = tuple(map(tuple, matrix_slip))
            slip_direction = self._get_direction_name((slip_r, slip_c), (br, bc))
            slip_tile = state_tuple[slip_r][slip_c]
            self.log_func(f"    [KẾT QUẢ] Trượt lân cận: Ô {slip_tile} trượt {slip_direction} vào ô trống thay vì ô dự định.")
        else:
            # This should be rare: blank has only one adjacent tile (the intended one)
            # In this case, we'll use the normal outcome to ensure state change
            slip_outcome = normal_outcome
            self.log_func(f"    [KẾT QUẢ] Không có ô lân cận nào khác để trượt. Sử dụng kết quả bình thường.")

        outcomes.append(slip_outcome)

        action_direction = self._get_direction_name(action_intended_tile_pos, (br, bc))
        action_tile = state_tuple[tr][tc]
        self.log_func(f"    [KẾT QUẢ] Cho hành động (di chuyển ô {action_tile} {action_direction}) từ trạng thái {state_tuple}:")
        self.log_func(f"    [KẾT QUẢ] Kết quả thông thường: {normal_outcome}")
        self.log_func(f"    [KẾT QUẢ] Kết quả trượt lân cận: {slip_outcome}")

        return outcomes

def and_or_search(problem, log_func=None, p_slip=0.1):
    """
    Top-level function to start the AND-OR search.
    Args:
        problem: An instance of NonDeterministicPuzzle.
        log_func: An optional function to handle logging messages.
        p_slip: Probability of slip outcome (default: 0.1 or 10%)
    Returns:
        A conditional plan or FAILURE (None).
    """
    if log_func and callable(log_func):
        problem.set_logger(log_func)
    else:
        problem.set_logger(lambda x: None) # Ensure a no-op logger if none provided or invalid

    # Pass log_func to or_search and and_search
    return or_search(problem, problem.initial_state, [], log_func, p_slip)

def or_search(problem, state, path, log_func, p_slip):
    log_func(f"[HOẶC] Trạng thái: {state}, Đường đi: {path}")

    if problem.is_goal(state):
        log_func(f"[HOẶC] Đã tìm thấy đích cho trạng thái: {state}")
        return EMPTY_PLAN
    
    if state in path: # Cycle detected
        log_func(f"[HOẶC] Phát hiện chu trình cho trạng thái: {state} trong đường đi: {path}")
        return FAILURE
    
    current_path_to_children = path + [state]

    possible_actions = problem.actions(state)
    
    # Hiển thị hành động dưới dạng hướng thay vì tọa độ
    action_descriptions = []
    for action in possible_actions:
        blank_pos = problem._find_blank(state)
        direction = problem._get_direction_name(action, blank_pos)
        tile_value = state[action[0]][action[1]]
        action_descriptions.append(f"ô {tile_value} {direction}")
    
    log_func(f"[HOẶC] Các hành động khả thi cho {state}: {action_descriptions}")

    for action in possible_actions:
        # Lấy mô tả hướng di chuyển cho action
        blank_pos = problem._find_blank(state)
        direction = problem._get_direction_name(action, blank_pos)
        tile_value = state[action[0]][action[1]]
        action_desc = f"ô {tile_value} {direction}"
        
        log_func(f"[HOẶC] Thử hành động: {action_desc} từ trạng thái: {state}")
        
        resulting_states = problem.results(state, action)
        log_func(f"[HOẶC] Kết quả cho hành động {action_desc}: {resulting_states}")
        
        conditional_plan_for_outcomes = and_search(problem, resulting_states, current_path_to_children, log_func, p_slip)
        
        if conditional_plan_for_outcomes is not FAILURE:
            log_func(f"[HOẶC] Thành công! Hành động {action_desc} từ {state} dẫn đến kế hoạch: {conditional_plan_for_outcomes}")
            return [action, conditional_plan_for_outcomes]
        else:
            log_func(f"[HOẶC] Hành động {action_desc} từ {state} thất bại (and_search trả về FAILURE).")
            
    log_func(f"[HOẶC] Tất cả hành động thất bại cho trạng thái: {state}. Trả về FAILURE.")
    return FAILURE

def and_search(problem, states_to_achieve, path, log_func, p_slip):
    log_func(f"[VÀ] Các trạng thái cần đạt: {states_to_achieve}, Đường đi: {path}")

    outcome_to_plan_map = {}

    if not states_to_achieve:
        log_func("[VÀ] Không có trạng thái nào cần đạt. Đây có thể là vấn đề.")
        # Depending on semantics, this could be an empty plan or failure.
        # For AND-OR, if an action has no outcomes, it might be considered unplannable.
        return FAILURE # Or an empty map {} if that's more appropriate for no outcomes.

    # Determine the primary (normal) outcome - it's the first one in the results list
    if len(states_to_achieve) > 0:
        primary_state = states_to_achieve[0]
        log_func(f"[VÀ] Kết quả chính (bình thường): {primary_state}")
    else:
        return FAILURE

    # First, try to find a plan for the primary outcome
    log_func(f"[VÀ] Xử lý trạng thái kết quả chính: {primary_state}")
    primary_plan = or_search(problem, primary_state, path, log_func, p_slip)
    
    if primary_plan is FAILURE:
        log_func(f"[VÀ] Thất bại cho kết quả chính. Hủy bỏ nút VÀ.")
        return FAILURE
    
    log_func(f"[VÀ] Tìm thấy kế hoạch cho kết quả chính: {primary_plan}")
    outcome_to_plan_map[primary_state] = primary_plan
    
    # For other outcomes (slip outcomes), we have two options based on probability:
    # 1. If probability is low (p_slip < threshold), we can use the primary plan
    # 2. Otherwise, find a specific plan for each outcome
    
    for i, s_i in enumerate(states_to_achieve):
        if i == 0:  # Skip the primary outcome which we already processed
            continue
            
        log_func(f"[VÀ] Xử lý trạng thái kết quả phụ s_i: {s_i}")
        
        # If slip probability is low (< 15%), use the primary plan for this outcome too
        if p_slip < 0.15:
            log_func(f"[VÀ] Sử dụng kế hoạch chính cho kết quả xác suất thấp (p={p_slip})")
            outcome_to_plan_map[s_i] = primary_plan
        else:
            # Traditional AND-OR approach: find specific plan for this outcome
            plan_for_s_i = or_search(problem, s_i, path, log_func, p_slip) 
            
            if plan_for_s_i is FAILURE:
                log_func(f"[VÀ] Thất bại cho s_i: {s_i}. Hủy bỏ nút VÀ.")
                return FAILURE
            
            log_func(f"[VÀ] Tìm thấy kế hoạch cho s_i {s_i}: {plan_for_s_i}")
            outcome_to_plan_map[s_i] = plan_for_s_i
        
    log_func(f"[VÀ] Tất cả trạng thái kết quả đều đạt được. Trả về bản đồ: {outcome_to_plan_map}")
    return outcome_to_plan_map


if __name__ == '__main__':
    # DEBUG_AND_OR_SEARCH = True # Enable debugging for standalone run
    # Example Usage (for testing purposes)
    # Define a 2x2 puzzle
    # Goal: [[1, 2], [3, 0]] (0 is blank)
    # Initial: e.g., [[0, 1], [2, 3]] or some other configuration

    initial_config = [[1, 0], [3, 2]] # Blank at (0,1)
    # A bit more complex initial state:
    # initial_config = [[3,1],[0,2]] # Blank at (1,0)
    # initial_config = [[0,1],[2,3]] # Blank at (0,0) - one step from a common goal if goal is [[1,2],[3,0]] 
    # initial_config = [[1,2],[0,3]] # Blank at (1,0)

    goal_config = [[1, 2], [3, 0]] # Common goal for 8-puzzle like problems

    print(f"Initial state: {initial_config}")
    print(f"Goal state: {goal_config}")

    try:
        puzzle_problem = NonDeterministicPuzzle(initial_matrix=initial_config, goal_matrix=goal_config)

        # Define a logger for testing if needed
        def console_logger(message):
            print(message)

        print("Starting AND-OR Search...")
        solution_plan = and_or_search(puzzle_problem, console_logger, p_slip=0.1)

        if solution_plan is FAILURE:
            print("No solution found.")
        elif solution_plan == EMPTY_PLAN:
            print("Initial state is already the goal state.")
        else:
            print("Solution Plan Found:")
            
            def pretty_print_plan(plan, indent=0):
                if plan == EMPTY_PLAN:
                    print("  " * indent + "<GOAL REACHED (Empty Plan)>")
                    return
                if plan == FAILURE: # Should not be part of a successful plan structure
                    print("  " * indent + "<FAILURE ENCOUNTERED>") 
                    return

                action = plan[0]
                outcomes_map = plan[1]
                
                tile_to_move_val = "?" 
                # To get tile_to_move_val, we'd need the state *before* this action was taken.
                # The action is (tr, tc) - coordinates of the tile being moved.
                # This requires context of the state from which 'action' was chosen.
                # For now, just print action coordinates.
                print("  " * indent + f"IF Perform Action (move tile at {action}):")
                
                for outcome_state, sub_plan in outcomes_map.items():
                    print("  " * (indent + 1) + f"IF Outcome is {outcome_state}:")
                    pretty_print_plan(sub_plan, indent + 2)

            pretty_print_plan(solution_plan)

    except ValueError as e:
        print(f"Error setting up puzzle: {e}")
    except Exception as e:
        import traceback
        print(f"An unexpected error occurred: {e}")
        print(traceback.format_exc())

    # Test a simple case where initial is goal
    print("\n--- Test: Initial is Goal ---")
    try:
        puzzle_problem_goal = NonDeterministicPuzzle(initial_matrix=goal_config, goal_matrix=goal_config)
        solution_plan_goal = and_or_search(puzzle_problem_goal, console_logger, p_slip=0.1)
        if solution_plan_goal == EMPTY_PLAN:
            print("Correctly identified: Initial state is already the goal state.")
        else:
            print(f"Unexpected plan for initial=goal: {solution_plan_goal}")
    except ValueError as e:
        print(f"Error: {e}")


    # Test a one-step problem (if deterministic, otherwise more complex)
    # If initial = [[1, 2], [0, 3]] and goal = [[1, 2], [3, 0]]
    # Action: move tile 3 from (1,1) to blank at (1,0)
    # Normal outcome: [[1, 2], [3, 0]] -> GOAL
    # Slip outcome: other tile adj to blank (0,0) - say tile 1 at (0,0) moves to (1,0)
    #   This needs careful check of `