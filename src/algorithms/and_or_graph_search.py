"""
Implementation of AND-OR graph search for a non-deterministic 2x2 puzzle.
The puzzle has two possible outcomes for each action:
1. The intended tile moves.
2. An adjacent tile (the 'other' one) slips into the blank space.
"""

import copy # Potentially useful, but direct manipulation might be cleaner

FAILURE = None
EMPTY_PLAN = [] # Represents an empty plan (e.g., when goal is reached)
DEBUG_AND_OR_SEARCH = True # Set to True to enable verbose logging

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

    def results(self, state_tuple, action_intended_tile_pos):
        """
        Returns a list of possible resulting states (tuple of tuples) 
        for a given intended action.

        MODIFIED FOR "SLIP OPPOSITE DIRECTION OF INTENDED TILE MOVE":
        1. Normal outcome: The intended tile moves into the blank.
        2. Slip outcome: The intended tile attempts to move in the exact opposite
           direction from its original position. If this target is out of bounds,
           the state does not change. The blank is not involved in the slip.
        
        Args:
            state_tuple: The current state of the puzzle.
            action_intended_tile_pos: (tr, tc) of the tile intended to move.
        """
        
        outcomes = []
        current_matrix_list_of_lists = [list(row) for row in state_tuple]

        tr, tc = action_intended_tile_pos # Tile's original row and column
        br, bc = self._find_blank(state_tuple)   # Blank's row and column

        # 1. Normal Outcome
        matrix_normal = [row[:] for row in current_matrix_list_of_lists]
        matrix_normal[br][bc], matrix_normal[tr][tc] = matrix_normal[tr][tc], matrix_normal[br][bc]
        normal_outcome = tuple(map(tuple, matrix_normal))
        outcomes.append(normal_outcome)

        # 2. Slip Outcome (Tile moves opposite to its intended move direction)
        slip_outcome = state_tuple # Default to no change if slip is invalid
        
        # Determine intended move vector for the tile (from tile to blank)
        # dr_intended = br - tr
        # dc_intended = bc - tc
        # No, this is not quite right for defining tile's own slip direction.
        # We need to determine the tile's move relative to itself based on blank's position.

        slip_target_tr, slip_target_tc = -1, -1

        if tr == br: # Tile and blank are in the same row -> horizontal move for tile
            if tc < bc: # Tile is to the LEFT of Blank, intends to move RIGHT into blank
                # Slip: Tile attempts to move further LEFT from its original position
                slip_target_tr, slip_target_tc = tr, tc - 1
            else: # Tile is to the RIGHT of Blank (tc > bc), intends to move LEFT into blank
                # Slip: Tile attempts to move further RIGHT from its original position
                slip_target_tr, slip_target_tc = tr, tc + 1
        elif tc == bc: # Tile and blank are in the same column -> vertical move for tile
            if tr < br: # Tile is ABOVE Blank, intends to move DOWN into blank
                # Slip: Tile attempts to move further UP from its original position
                slip_target_tr, slip_target_tc = tr - 1, tc
            else: # Tile is BELOW Blank (tr > br), intends to move UP into blank
                # Slip: Tile attempts to move further DOWN from its original position
                slip_target_tr, slip_target_tc = tr + 1, tc
        # Else: tile and blank are not adjacent (should not happen if action is valid)
        # This case will result in slip_target_tr, tc remaining -1, defaulting to no change.

        matrix_slip = [row[:] for row in current_matrix_list_of_lists]
        if 0 <= slip_target_tr < self.size and 0 <= slip_target_tc < self.size:
            # Valid slip target: Swap intended tile with the tile at the slip target.
            # The blank's position (br, bc) is NOT affected by this slip.
            tile_value_to_slip = matrix_slip[tr][tc]
            value_at_slip_target = matrix_slip[slip_target_tr][slip_target_tc]
            
            matrix_slip[slip_target_tr][slip_target_tc] = tile_value_to_slip
            matrix_slip[tr][tc] = value_at_slip_target
            slip_outcome = tuple(map(tuple, matrix_slip))
        else:
            # Invalid slip target (out of bounds), so slip outcome is no change from original state
            slip_outcome = state_tuple
            if DEBUG_AND_OR_SEARCH:
                print(f"    [RESULTS] Slip for tile at ({tr},{tc}) to ({slip_target_tr},{slip_target_tc}) is out of bounds.")

        outcomes.append(slip_outcome)

        if DEBUG_AND_OR_SEARCH:
            print(f"    [RESULTS] For action (move tile at {action_intended_tile_pos}) from state {state_tuple}:")
            print(f"    [RESULTS] Normal outcome: {normal_outcome}")
            print(f"    [RESULTS] Slip outcome (tile moves opposite): {slip_outcome}")
            # print(f"    [RESULTS] Final outcomes list: {outcomes}") # Redundant if shown above

        return outcomes

def and_or_search(problem):
    """
    Top-level function to start the AND-OR search.
    Args:
        problem: An instance of NonDeterministicPuzzle.
    Returns:
        A conditional plan or FAILURE (None).
    """
    return or_search(problem, problem.initial_state, [])

def or_search(problem, state, path):
    if DEBUG_AND_OR_SEARCH:
        print(f"[OR] State: {state}, Path: {path}")

    if problem.is_goal(state):
        if DEBUG_AND_OR_SEARCH:
            print(f"[OR] Goal found for state: {state}")
        return EMPTY_PLAN
    
    if state in path: # Cycle detected
        if DEBUG_AND_OR_SEARCH:
            print(f"[OR] Cycle detected for state: {state} in path: {path}")
        return FAILURE
    
    current_path_to_children = path + [state]

    possible_actions = problem.actions(state)
    if DEBUG_AND_OR_SEARCH:
        print(f"[OR] Actions for {state}: {possible_actions}")

    for action in possible_actions:
        if DEBUG_AND_OR_SEARCH:
            print(f"[OR] Trying action: {action} from state: {state}")
        
        resulting_states = problem.results(state, action)
        if DEBUG_AND_OR_SEARCH:
            print(f"[OR] Results for action {action}: {resulting_states}")
        
        conditional_plan_for_outcomes = and_search(problem, resulting_states, current_path_to_children)
        
        if conditional_plan_for_outcomes is not FAILURE:
            if DEBUG_AND_OR_SEARCH:
                print(f"[OR] Success! Action {action} from {state} leads to plan: {conditional_plan_for_outcomes}")
            return [action, conditional_plan_for_outcomes]
        else:
            if DEBUG_AND_OR_SEARCH:
                print(f"[OR] Action {action} from {state} failed (and_search returned FAILURE).")
            
    if DEBUG_AND_OR_SEARCH:
        print(f"[OR] All actions failed for state: {state}. Returning FAILURE.")
    return FAILURE

def and_search(problem, states_to_achieve, path):
    if DEBUG_AND_OR_SEARCH:
        print(f"[AND] States to achieve: {states_to_achieve}, Path: {path}")

    outcome_to_plan_map = {}

    if not states_to_achieve:
        if DEBUG_AND_OR_SEARCH:
            print("[AND] No states to achieve. This might be an issue.")
        # Depending on semantics, this could be an empty plan or failure.
        # For AND-OR, if an action has no outcomes, it might be considered unplannable.
        return FAILURE # Or an empty map {} if that's more appropriate for no outcomes.

    for s_i in states_to_achieve:
        if DEBUG_AND_OR_SEARCH:
            print(f"[AND] Processing outcome state s_i: {s_i}")
        
        plan_for_s_i = or_search(problem, s_i, path) 
        
        if plan_for_s_i is FAILURE:
            if DEBUG_AND_OR_SEARCH:
                print(f"[AND] Failure for s_i: {s_i}. Aborting AND node.")
            return FAILURE
        
        if DEBUG_AND_OR_SEARCH:
            print(f"[AND] Plan found for s_i {s_i}: {plan_for_s_i}")
        outcome_to_plan_map[s_i] = plan_for_s_i
        
    if DEBUG_AND_OR_SEARCH:
        print(f"[AND] All outcome states achieved. Returning map: {outcome_to_plan_map}")
    return outcome_to_plan_map


if __name__ == '__main__':
    DEBUG_AND_OR_SEARCH = True # Enable debugging for standalone run
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

        print("Starting AND-OR Search...")
        solution_plan = and_or_search(puzzle_problem)

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
        solution_plan_goal = and_or_search(puzzle_problem_goal)
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