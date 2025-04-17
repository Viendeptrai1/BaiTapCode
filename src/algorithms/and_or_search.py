from src.core.buzzle_logic import Buzzle, create_new_state

def and_or_graph_search(problem):
    """
    Thuật toán AND/OR graph search cho 8-puzzle
    Input: một đối tượng problem (AndOrProblemAdapter)
    Output: (plan, nodes_expanded)
        - plan: danh sách các bước di chuyển hoặc 'failure'
        - nodes_expanded: số nút đã mở rộng
    """
    # Khởi tạo từ trạng thái ban đầu của problem
    state = problem.initial_state  # state_tuple
    visited = {}  # Lưu trữ các trạng thái đã thăm
    nodes_expanded = 0
    max_frontier_size = 0  # Không áp dụng rõ ràng cho AND/OR, luôn là 1
    depth = 0  # Giới hạn độ sâu để tránh đệ quy vô hạn
    path = []  # Lưu dấu đường đi

    result = or_search(state, problem, visited, depth, path, nodes_expanded, max_frontier_size)
    plan, nodes_expanded, _ = result
    
    return plan, nodes_expanded

def extract_path(plan, depth=0):
    """
    Trích xuất đường đi từ kết quả của AND/OR search
    """
    if isinstance(plan, str):  # Case 'failure' hoặc action
        return [plan]
    
    if not plan:  # Empty dict
        return []
    
    # Nếu plan là dict, đây là OR node với các action -> children
    result = []
    for action, action_plan in plan.items():
        if action_plan == "empty_plan":  # Trạng thái đích
            return [action]
        sub_plan = extract_path(action_plan, depth + 1)
        if sub_plan and sub_plan != ["failure"]:
            return [action] + sub_plan
    
    return ["failure"]  # Không tìm thấy đường đi

def or_search(state, problem, visited, depth, path, nodes_expanded, max_frontier_size):
    """
    OR-node search trong thuật toán AND/OR graph search
    """
    # Kiểm tra đã thăm trạng thái này chưa
    if state in visited:
        return visited[state], nodes_expanded, max_frontier_size
    
    # Kiểm tra giới hạn độ sâu (tránh đệ quy vô hạn)
    if depth > 30:  # Giới hạn độ sâu tối đa
        return "failure", nodes_expanded, max_frontier_size

    # Kiểm tra trạng thái đích
    if problem.goal_test(state):
        return "empty_plan", nodes_expanded + 1, max_frontier_size
    
    # Tăng số nút đã mở rộng
    nodes_expanded += 1
    
    # Lấy danh sách các hành động có thể
    actions = problem.actions(state)
    
    # Khởi tạo từ điển cho các kết quả
    results = {}
    
    # Duyệt qua từng hành động
    for action in actions:
        # Lấy trạng thái kết quả sau khi thực hiện hành động
        next_state = problem.result(state, action)
        
        # Nếu trạng thái kế tiếp là None (hành động không hợp lệ)
        if next_state is None:
            continue
        
        # Đệ quy OR-search cho trạng thái kế tiếp
        new_path = path + [action]
        or_result, nodes_expanded, max_frontier_size = or_search(
            next_state, problem, visited, depth + 1, new_path, nodes_expanded, max_frontier_size
        )
        
        # Lưu kết quả
        if or_result != "failure":
            results[action] = or_result
    
    # Nếu không có kết quả nào thành công
    if not results:
        # Đánh dấu trạng thái này đã được thăm và kết quả là failure
        visited[state] = "failure"
        return "failure", nodes_expanded, max_frontier_size
    
    # Tìm hành động dẫn đến kết quả tốt nhất
    best_action = None
    best_plan = None
    
    for action, plan in results.items():
        if plan == "empty_plan":  # Trạng thái đích
            best_action = action
            best_plan = plan
            break
        
        # Extract path từ plan
        path_from_plan = extract_path(plan)
        if path_from_plan and path_from_plan != ["failure"]:
            if best_plan is None or len(path_from_plan) < len(extract_path(best_plan)):
                best_action = action
                best_plan = plan
    
    # Nếu không tìm thấy đường đi tốt nhất
    if best_action is None:
        visited[state] = "failure"
        return "failure", nodes_expanded, max_frontier_size
    
    # Lưu kết quả vào visited
    plan_result = {best_action: best_plan}
    visited[state] = plan_result
    
    return plan_result, nodes_expanded, max_frontier_size 