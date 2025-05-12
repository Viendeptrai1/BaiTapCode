#!/usr/bin/env python3
"""
Script to train Reinforcement Learning models for 8-puzzle solver
and save them to disk for later use in the main application.
"""

import os
import pickle
import time
import argparse
import numpy as np
from tqdm import tqdm
import random

# Import the RL algorithms
from src.algorithms.rl_algorithms import QLearningAgent, value_iteration, solve_with_value_iteration
from src.core.buzzle_logic import Buzzle, create_new_state

def ensure_model_dir():
    """Ensure the model directory exists."""
    os.makedirs("models", exist_ok=True)
    
def train_q_learning(episodes=10000, alpha=0.2, gamma=0.99, epsilon=0.3, 
                    alpha_decay=0.9995, epsilon_decay=0.9995, save_path="models/q_learning_model.pkl"):
    """
    Train a Q-Learning agent and save it to disk.
    
    Parameters:
    - episodes: Number of training episodes
    - alpha: Learning rate
    - gamma: Discount factor
    - epsilon: Exploration parameter
    - alpha_decay: Alpha decay rate
    - epsilon_decay: Epsilon decay rate
    - save_path: Path to save the model
    
    Returns:
    - agent: Trained Q-Learning agent
    """
    print(f"Training Q-Learning agent with {episodes} episodes...")
    agent = QLearningAgent(
        alpha=alpha, 
        gamma=gamma, 
        epsilon=epsilon,
        alpha_decay=alpha_decay,
        epsilon_decay=epsilon_decay,
        min_alpha=0.01,
        min_epsilon=0.01
    )
    
    # Tạo các puzzle đơn giản để huấn luyện trước
    simple_puzzles = []
    for _ in range(min(1000, episodes // 10)):
        # Tạo puzzle gần với goal state (chỉ cần vài bước để giải)
        goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        simple_puzzle = Buzzle(goal_state)
        
        # Thực hiện một số bước ngẫu nhiên từ goal state
        steps = random.randint(1, 5)  # 1-5 bước
        for _ in range(steps):
            moves = ["up", "down", "left", "right"]
            random.shuffle(moves)
            for move in moves:
                success, new_data = create_new_state(simple_puzzle.data, move)
                if success:
                    simple_puzzle = Buzzle(new_data)
                    break
        
        simple_puzzles.append(simple_puzzle)
    
    # Huấn luyện với các puzzle đơn giản trước
    print("Pre-training with simple puzzles...")
    for i, puzzle in enumerate(simple_puzzles):
        if i % 100 == 0:
            print(f"  Pre-training puzzle {i+1}/{len(simple_puzzles)}")
        agent.train(episodes=10, max_steps=20, use_experience_replay=True, batch_size=32)
    
    print("Main training phase...")
    # Initialize stats tracking
    stats = agent.train(
        episodes=episodes, 
        max_steps=300,  # Increased from default
        use_experience_replay=True,
        batch_size=128   # Increased batch size
    )
    
    # Save the trained agent
    with open(save_path, "wb") as f:
        pickle.dump(agent, f)
    
    print(f"Q-Learning model saved to {save_path}")
    print(f"Model stats: {len(agent.q_table)} states in Q-table")
    
    return agent

def train_value_iteration(iterations=500, gamma=0.99, max_states=10000, 
                        save_path="models/value_iteration_model.pkl"):
    """
    Train a Value Iteration model and save it to disk.
    
    Parameters:
    - iterations: Number of iterations for value iteration
    - gamma: Discount factor
    - max_states: Maximum number of states to explore
    - save_path: Path to save the model
    
    Returns:
    - utilities: Value function mapping
    - policy: Policy mapping
    """
    print(f"Training Value Iteration model with {iterations} iterations and {max_states} max states...")
    utilities, policy, stats = value_iteration(
        gamma=gamma,
        iterations=iterations,
        max_states_to_explore=max_states,
        theta=0.0001  # Lowered convergence threshold for more precise convergence
    )
    
    # Thêm trạng thái đặc biệt cho puzzle đơn giản
    print("Adding extra states for simple puzzles...")
    goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
    goal_puzzle = Buzzle(goal_state)
    goal_tuple = tuple(map(tuple, goal_puzzle.data))
    
    # Tạo các trạng thái đơn giản gần với goal
    simple_states = set([goal_tuple])
    frontier = [goal_tuple]
    
    # Khám phá không gian trạng thái gần goal (BFS đến độ sâu 5)
    depth = 0
    max_depth = 5
    level_size = 1
    next_level_size = 0
    
    while frontier and depth < max_depth:
        state_tuple = frontier.pop(0)
        level_size -= 1
        
        # Chuyển thành list of lists để làm việc
        state_data = [list(row) for row in state_tuple]
        
        # Thử tất cả các hành động
        for move in ["up", "down", "left", "right"]:
            success, next_data = create_new_state(state_data, move)
            if success:
                next_tuple = tuple(map(tuple, next_data))
                
                # Nếu là trạng thái mới, thêm vào frontier
                if next_tuple not in simple_states:
                    simple_states.add(next_tuple)
                    frontier.append(next_tuple)
                    next_level_size += 1
                    
                    # Tính toán phần thưởng và giá trị
                    reward = -1
                    if depth == 0:  # Trực tiếp từ goal
                        utilities[next_tuple] = 90
                        policy[next_tuple] = get_opposite_move(move)
                    else:
                        # Trạng thái càng xa goal, giá trị càng thấp
                        u_value = 100 - (depth + 1) * 10
                        if next_tuple not in utilities or utilities[next_tuple] < u_value:
                            utilities[next_tuple] = u_value
                            policy[next_tuple] = get_opposite_move(move)
        
        # Nếu hết level hiện tại, chuyển sang level tiếp theo
        if level_size == 0:
            depth += 1
            level_size = next_level_size
            next_level_size = 0
    
    print(f"Added {len(simple_states)} simple states near the goal")
    
    # Save the model
    with open(save_path, "wb") as f:
        model = {"utilities": utilities, "policy": policy, "stats": stats}
        pickle.dump(model, f)
    
    print(f"Value Iteration model saved to {save_path}")
    print(f"Model stats: {len(utilities)} states explored")
    
    return utilities, policy

def get_opposite_move(move):
    """Trả về hành động ngược lại."""
    opposites = {"up": "down", "down": "up", "left": "right", "right": "left"}
    return opposites.get(move)

def test_model(model_type="q_learning", model_path=None, num_tests=10):
    """
    Test a model on random puzzles.
    
    Parameters:
    - model_type: 'q_learning' or 'value_iteration'
    - model_path: Path to the model file
    - num_tests: Number of random puzzles to test
    
    Returns:
    - results: Dictionary of test results
    """
    if model_path is None:
        model_path = f"models/{model_type}_model.pkl"
        
    print(f"Testing {model_type} model from {model_path} on {num_tests} random puzzles...")
    
    # Load the model
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
    except FileNotFoundError:
        print(f"Error: Model file {model_path} not found.")
        return None
        
    # Prepare test puzzles
    puzzles = []
    for _ in range(num_tests):
        # Generate a random solvable puzzle
        state = Buzzle.generate_random_state()
        puzzles.append(Buzzle(state))
    
    results = {
        'solved': 0,
        'unsolved': 0,
        'avg_steps': 0,
        'max_steps': 0,
        'min_steps': float('inf'),
        'total_time': 0
    }
    
    # Test each puzzle
    for i, puzzle in enumerate(puzzles):
        print(f"Testing puzzle {i+1}/{num_tests}...")
        start_time = time.time()
        
        if model_type == "q_learning":
            agent = model
            path, steps, _ = agent.solve(puzzle, max_steps=150)
        else:  # value_iteration
            utilities = model['utilities']
            policy = model['policy']
            path, steps = solve_with_value_iteration(puzzle, utilities, policy)
        
        solve_time = time.time() - start_time
        results['total_time'] += solve_time
        
        # Check if solved
        if path and len(path) > 0:
            final_state = path[-1][1]
            final_puzzle = Buzzle(final_state)
            if final_puzzle.is_goal():
                results['solved'] += 1
                results['avg_steps'] += steps
                results['max_steps'] = max(results['max_steps'], steps)
                results['min_steps'] = min(results['min_steps'], steps)
                print(f"  Solved in {steps} steps ({solve_time:.2f}s)")
            else:
                results['unsolved'] += 1
                print(f"  Failed to reach goal state")
        else:
            results['unsolved'] += 1
            print(f"  No valid path found")
    
    # Calculate final stats
    if results['solved'] > 0:
        results['avg_steps'] /= results['solved']
    
    # Print summary
    print("\nTest Results Summary:")
    print(f"Solved: {results['solved']}/{num_tests} ({results['solved']/num_tests*100:.1f}%)")
    print(f"Avg steps for solved puzzles: {results['avg_steps']:.1f}")
    print(f"Min steps: {results['min_steps'] if results['min_steps'] != float('inf') else 'N/A'}")
    print(f"Max steps: {results['max_steps']}")
    print(f"Avg time per puzzle: {results['total_time']/num_tests:.2f}s")
    
    return results

def test_specific_puzzle(model_type="q_learning", puzzle_data=None, model_path=None, max_steps=200):
    """
    Test a model on a specific puzzle.
    
    Parameters:
    - model_type: 'q_learning' or 'value_iteration'
    - puzzle_data: The specific puzzle to test
    - model_path: Path to the model file
    - max_steps: Maximum steps to allow for solving
    
    Returns:
    - solution_path: List of actions and states
    - steps: Number of steps taken
    """
    if puzzle_data is None:
        # Sử dụng puzzle đơn giản để test
        puzzle_data = [
            [1, 2, 3],
            [4, 0, 6],
            [7, 5, 8]
        ]
    
    # Load the model
    if model_path is None:
        model_path = f"models/{model_type}_model.pkl"
    
    print(f"Testing {model_type} model from {model_path} on specific puzzle...")
    print("Puzzle:")
    for row in puzzle_data:
        print("  " + " ".join(str(tile) for tile in row))
    
    # Create puzzle object
    puzzle = Buzzle(puzzle_data)
    
    # Load model
    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
    except FileNotFoundError:
        print(f"Model file {model_path} not found.")
        return None, 0
        
    # Solve puzzle using the model
    start_time = time.time()
    if model_type == 'q_learning':
        solution_path, steps, _ = model.solve(puzzle, max_steps=max_steps)
    elif model_type == 'value_iteration':
        solution_path, steps = solve_with_value_iteration(puzzle, model["utilities"], model["policy"], max_steps=max_steps)
    else:
        print(f"Unknown model type: {model_type}")
        return None, 0
    
    solve_time = time.time() - start_time
    
    # Print solution
    if solution_path:
        print(f"\nĐường Đi Giải Pháp:")
        print(f"Bước 0: Trạng Thái Ban Đầu")
        for r in puzzle_data:
            print(f"  {r}")
        print("-" * 20)
        
        for i, (action, state) in enumerate(solution_path):
            print(f"Bước {i+1}: Di chuyển {action.capitalize()}")
            for r in state:
                print(f"  {r}")
            print("-" * 20)
            
        if Buzzle(solution_path[-1][1]).is_goal():
            print(f"Đã giải thành công trong {steps} bước và {solve_time:.2f} giây.")
        else:
            print(f"Không tìm thấy giải pháp sau {steps} bước.")
    else:
        print("Không tìm được đường đi giải pháp.")
    
    return solution_path, steps

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Train and test RL models for 8-puzzle.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--train", action="store_true", help="Train a model")
    group.add_argument("--test", action="store_true", help="Test a model on random puzzles")
    group.add_argument("--test-specific", action="store_true", help="Test a model on a specific puzzle")
    
    parser.add_argument("--model", choices=["q_learning", "value_iteration", "both"], 
                      default="q_learning", help="Model type to train or test")
    parser.add_argument("--episodes", type=int, default=1000, 
                      help="Number of episodes for Q-Learning training")
    parser.add_argument("--iterations", type=int, default=200, 
                      help="Number of iterations for Value Iteration")
    parser.add_argument("--num-tests", type=int, default=10,
                      help="Number of puzzles to test")
    parser.add_argument("--puzzle", type=str, 
                      help="Specific puzzle to test in format '0,1,2,3,4,5,6,7,8'")
    parser.add_argument("--max-steps", type=int, default=200,
                      help="Maximum steps for solving puzzles")
    
    args = parser.parse_args()
    
    # Load existing models if available
    models = {}
    q_learning_path = "models/q_learning_model.pkl"
    vi_path = "models/value_iteration_model.pkl"
    
    try:
        with open(q_learning_path, 'rb') as f:
            models["q_learning"] = pickle.load(f)
            print(f"Loaded Q-Learning model from {q_learning_path}")
    except FileNotFoundError:
        models["q_learning"] = None
    
    try:
        with open(vi_path, 'rb') as f:
            models["value_iteration"] = pickle.load(f)
            print(f"Loaded Value Iteration model from {vi_path}")
    except FileNotFoundError:
        models["value_iteration"] = None
    
    # Ensure the models directory exists
    ensure_model_dir()
    
    if args.train:
        if args.model in ["q_learning", "both"]:
            train_q_learning(episodes=args.episodes)
        
        if args.model in ["value_iteration", "both"]:
            train_value_iteration(iterations=args.iterations)
    
    elif args.test:
        if args.model in ["q_learning", "both"]:
            test_model("q_learning", num_tests=args.num_tests)
        
        if args.model in ["value_iteration", "both"]:
            test_model("value_iteration", num_tests=args.num_tests)
    
    elif args.test_specific:
        # Convert puzzle string to 2D array if provided
        puzzle_data = None
        if args.puzzle:
            try:
                # Parse '0,1,2,3,4,5,6,7,8' format
                flat_puzzle = [int(x) for x in args.puzzle.split(',')]
                if len(flat_puzzle) != 9:
                    raise ValueError("Puzzle must have exactly 9 values")
                
                # Convert to 2D array
                puzzle_data = [
                    flat_puzzle[0:3],
                    flat_puzzle[3:6],
                    flat_puzzle[6:9]
                ]
                
                # Validate puzzle
                if sorted(flat_puzzle) != list(range(9)):
                    raise ValueError("Puzzle must contain numbers 0-8 exactly once")
                    
            except (ValueError, IndexError) as e:
                print(f"Error parsing puzzle: {e}")
                print("Expected format: '0,1,2,3,4,5,6,7,8' where 0 represents the blank")
                return
        else:
            # Use the sample puzzle from the user's example
            puzzle_data = [
                [0, 1, 4],
                [6, 5, 8],
                [2, 3, 7]
            ]
        
        if args.model in ["q_learning", "both"]:
            test_specific_puzzle("q_learning", puzzle_data, max_steps=args.max_steps)
        
        if args.model in ["value_iteration", "both"]:
            test_specific_puzzle("value_iteration", puzzle_data, max_steps=args.max_steps)

if __name__ == '__main__':
    main()
