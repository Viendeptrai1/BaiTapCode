from collections import deque
import copy
import random
import time

# Hàm kiểm tra xem một domain có chứa giá trị còn hiệu lực không
def has_valid_values(domain):
    """Kiểm tra xem domain có chứa ít nhất một giá trị hợp lệ không."""
    return len(domain) > 0

# Thuật toán AC-3
def ac3(variables, domains, constraints, assigned=None):
    """
    Thuật toán AC-3 cho bài toán CSP.
    
    Parameters:
    - variables: Danh sách các biến (tile indices 0-8)
    - domains: Dict của các miền giá trị (vị trí có thể) cho mỗi biến
    - constraints: Danh sách các ràng buộc
    - assigned: Dict các biến đã được gán giá trị
    
    Returns:
    - success: Boolean cho biết thuật toán có thành công không
    - domains: Dict các miền đã được thu gọn
    """
    if assigned is None:
        assigned = {}
    
    # Tạo bản sao của domains để không ảnh hưởng đến đầu vào
    domains = copy.deepcopy(domains)
    
    # Khởi tạo hàng đợi với tất cả các cung (Xi, Xj) với Xi khác Xj
    queue = deque()
    for xi in variables:
        for xj in variables:
            if xi != xj:
                queue.append((xi, xj))
    
    # Xử lý các ràng buộc đã biết (các vị trí đã gán)
    for var, pos in assigned.items():
        if var in domains:
            domains[var] = {pos}  # Giới hạn domain chỉ còn vị trí đã gán
    
    # Xử lý hàng đợi
    step_count = 0
    while queue:
        step_count += 1
        xi, xj = queue.popleft()
        
        # Nếu có sự thay đổi domain của xi
        if revise(domains, xi, xj, constraints):
            # Nếu domain của xi trở thành rỗng, không có giải pháp
            if not domains[xi]:
                return False, domains, step_count
            
            # Thêm các cung (xk, xi) vào hàng đợi, với xk khác xi và xj
            for xk in variables:
                if xk != xi and xk != xj:
                    queue.append((xk, xi))
    
    return True, domains, step_count

def revise(domains, xi, xj, constraints):
    """
    Xét lại domain của xi dựa trên xj và các ràng buộc.
    Trả về True nếu domain của xi bị thay đổi.
    """
    revised = False
    
    # Trong trường hợp này, ràng buộc đơn giản là xi và xj không thể có cùng vị trí
    for pos_i in list(domains[xi]):
        # Kiểm tra nếu có một giá trị trong domain của xj mà không thỏa mãn ràng buộc với pos_i
        if all(not is_consistent(xi, pos_i, xj, pos_j, constraints) for pos_j in domains[xj]):
            domains[xi].remove(pos_i)
            revised = True
    
    return revised

def is_consistent(var1, val1, var2, val2, constraints):
    """Kiểm tra xem một cặp giá trị có thỏa mãn các ràng buộc nhị phân không."""
    # Ràng buộc mặc định: hai biến khác nhau phải có vị trí khác nhau
    if var1 != var2 and val1 == val2:
        return False
    
    # Kiểm tra các ràng buộc bổ sung
    for constraint in constraints:
        if not constraint(var1, val1, var2, val2):
            return False
    
    return True

# Thuật toán Backtracking cho CSP
def backtracking_search(variables, domains, constraints, assigned=None, order_domain_values=None, select_unassigned_variable=None):
    """
    Tìm kiếm backtracking cho bài toán CSP.
    
    Parameters:
    - variables: Danh sách các biến (0-8 cho 8-puzzle)
    - domains: Dict các miền giá trị cho mỗi biến
    - constraints: Danh sách các ràng buộc
    - assigned: Dict các biến đã được gán trước đó
    - order_domain_values: Hàm sắp xếp các giá trị trong domain
    - select_unassigned_variable: Hàm chọn biến chưa gán tiếp theo
    
    Returns:
    - solution: Dict giải pháp hoặc None nếu không tìm thấy
    - stats: Thống kê về quá trình tìm kiếm
    """
    if assigned is None:
        assigned = {}
    
    stats = {'nodes': 0, 'backtracks': 0, 'assignments': []}
    
    # Kiểm tra các biến đã gán có thỏa mãn ràng buộc không
    for var1, val1 in assigned.items():
        for var2, val2 in assigned.items():
            if var1 != var2 and val1 == val2:
                return None, stats  # Có xung đột trong các biến đã gán
    
    # Chạy AC-3 để thu gọn miền
    success, domains, _ = ac3(variables, domains, constraints, assigned)
    if not success:
        stats['backtracks'] += 1
        return None, stats  # Không có giải pháp
    
    # Nếu đã gán đủ các biến
    if len(assigned) == len(variables):
        return assigned, stats
    
    # Chọn biến chưa gán tiếp theo
    if select_unassigned_variable:
        var = select_unassigned_variable(variables, domains, assigned)
    else:
        # Mặc định: chọn biến đầu tiên chưa được gán
        unassigned = [v for v in variables if v not in assigned]
        var = unassigned[0] if unassigned else None
    
    if var is None:
        return assigned, stats  # Đã gán tất cả biến
    
    # Lấy các giá trị domain cho biến đã chọn
    domain_values = list(domains[var])
    
    # Sắp xếp các giá trị theo heuristic (nếu có)
    if order_domain_values:
        domain_values = order_domain_values(var, domain_values, domains, assigned)
    
    # Thử từng giá trị
    for value in domain_values:
        stats['nodes'] += 1
        
        # Kiểm tra giá trị này có thỏa mãn tất cả ràng buộc với các biến đã gán không
        if is_value_consistent(var, value, assigned, constraints):
            # Thêm phép gán và ghi lại
            assigned[var] = value
            stats['assignments'].append((var, value))
            
            # Đệ quy với phép gán mới
            result, new_stats = backtracking_search(
                variables, domains, constraints, assigned, 
                order_domain_values, select_unassigned_variable
            )
            
            # Cập nhật thống kê
            stats['nodes'] += new_stats['nodes']
            stats['backtracks'] += new_stats['backtracks']
            stats['assignments'].extend(new_stats['assignments'])
            
            if result is not None:
                return result, stats
            
            # Backtrack nếu không tìm thấy giải pháp
            del assigned[var]
            stats['backtracks'] += 1
    
    return None, stats

def is_value_consistent(var, value, assigned, constraints):
    """Kiểm tra xem giá trị mới có thỏa mãn tất cả ràng buộc với các biến đã gán không."""
    for other_var, other_val in assigned.items():
        if not is_consistent(var, value, other_var, other_val, constraints):
            return False
    return True

# Các heuristic chọn biến
def mrv(variables, domains, assigned):
    """Minimum Remaining Values: Chọn biến có ít giá trị hợp lệ nhất."""
    unassigned = [v for v in variables if v not in assigned]
    if not unassigned:
        return None
    return min(unassigned, key=lambda var: len(domains[var]))

def degree_heuristic(variables, domains, assigned):
    """Degree Heuristic: Chọn biến có nhiều ràng buộc với các biến chưa gán nhất."""
    unassigned = [v for v in variables if v not in assigned]
    if not unassigned:
        return None
    
    # Đơn giản hóa: chỉ đếm số biến chưa gán
    return max(unassigned, key=lambda var: sum(1 for v in unassigned if v != var))

# Hàm kết hợp MRV và Degree heuristic
def mrv_degree(variables, domains, assigned):
    """Kết hợp MRV và Degree heuristic."""
    unassigned = [v for v in variables if v not in assigned]
    if not unassigned:
        return None
    
    # Sắp xếp theo MRV
    min_remaining = min(len(domains[var]) for var in unassigned)
    min_vars = [var for var in unassigned if len(domains[var]) == min_remaining]
    
    if len(min_vars) == 1:
        return min_vars[0]
    
    # Tie-break bằng degree heuristic
    return max(min_vars, key=lambda var: sum(1 for v in unassigned if v != var))

# Các heuristic chọn giá trị
def lcv(var, values, domains, assigned):
    """Least Constraining Value: Chọn giá trị ít ràng buộc với các biến khác nhất."""
    def count_conflicts(value):
        count = 0
        for other_var in domains:
            if other_var != var and other_var not in assigned:
                # Đếm số giá trị trong domain của other_var mà xung đột với value
                count += sum(1 for other_val in domains[other_var] if other_val == value)
        return count
    
    return sorted(values, key=count_conflicts)

# Khởi tạo bài toán 8-puzzle như CSP
def init_puzzle_csp(assigned_positions=None):
    """
    Khởi tạo bài toán 8-puzzle như một CSP.
    
    Parameters:
    - assigned_positions: Dict mapping từ tile index (0-8) đến vị trí (row, col) đã biết
    
    Returns:
    - variables: Danh sách các biến (tile indices)
    - domains: Dict các domain ban đầu cho mỗi biến
    - constraints: Danh sách các ràng buộc
    - assigned: Dict các biến đã được gán
    """
    if assigned_positions is None:
        assigned_positions = {}
    
    # Biến: các tile index từ 0-8 (0 là ô trống)
    variables = list(range(9))
    
    # Domain ban đầu: tất cả các vị trí có thể trên lưới 3x3
    all_positions = [(r, c) for r in range(3) for c in range(3)]
    domains = {var: set(all_positions) for var in variables}
    
    # Ràng buộc: các tile phải ở các vị trí khác nhau
    constraints = []  # Mặc định: is_consistent đã xử lý ràng buộc alldiff
    
    # Các biến đã được gán
    assigned = {}
    
    # Áp dụng các vị trí đã biết
    for tile, position in assigned_positions.items():
        if tile in variables:
            assigned[tile] = position
            
            # Loại bỏ vị trí này khỏi domain của các biến khác
            for var in variables:
                if var != tile and var in domains:
                    domains[var].discard(position)
    
    return variables, domains, constraints, assigned

# Chuyển đổi trạng thái puzzle thành vị trí các tile
def state_to_positions(state_data):
    """
    Chuyển đổi trạng thái puzzle (matrix 3x3) thành dict của các vị trí.
    
    Parameters:
    - state_data: Matrix 3x3 chứa trạng thái puzzle
    
    Returns:
    - positions: Dict mapping từ số (0-8) đến vị trí (row, col)
    """
    positions = {}
    for r in range(len(state_data)):
        for c in range(len(state_data[r])):
            tile = state_data[r][c]
            positions[tile] = (r, c)
    return positions

# Chuyển đổi vị trí các tile thành trạng thái puzzle
def positions_to_state(positions):
    """
    Chuyển đổi dict vị trí thành matrix trạng thái puzzle.
    
    Parameters:
    - positions: Dict mapping từ số (0-8) đến vị trí (row, col)
    
    Returns:
    - state_data: Matrix 3x3 chứa trạng thái puzzle
    """
    state = [[None for _ in range(3)] for _ in range(3)]
    for tile, (r, c) in positions.items():
        state[r][c] = tile
    return state

# Kiểm tra xem trạng thái puzzle có hợp lệ không
def is_valid_puzzle_state(state_data):
    """
    Kiểm tra xem trạng thái puzzle có hợp lệ không (mỗi số xuất hiện đúng một lần).
    
    Parameters:
    - state_data: Matrix 3x3 chứa trạng thái puzzle
    
    Returns:
    - valid: Boolean cho biết trạng thái có hợp lệ không
    """
    expected_values = set(range(9))
    actual_values = set()
    
    for row in state_data:
        for val in row:
            if val is not None:
                actual_values.add(val)
    
    return actual_values == expected_values

# Tạo trạng thái puzzle từ các vị trí đã biết
def create_puzzle_state_from_known_positions(known_positions):
    """
    Tạo trạng thái puzzle từ các vị trí đã biết.
    
    Parameters:
    - known_positions: Dict mapping từ tile index đến vị trí đã biết
    
    Returns:
    - state_data: Matrix 3x3 chứa trạng thái puzzle (None cho các vị trí chưa biết)
    """
    state = [[None for _ in range(3)] for _ in range(3)]
    for tile, (r, c) in known_positions.items():
        state[r][c] = tile
    return state

# Giải bài toán 8-puzzle bằng backtracking với các vị trí đã biết
def solve_puzzle_with_backtracking(known_positions, use_mrv=True, use_lcv=True):
    """
    Giải bài toán 8-puzzle bằng backtracking với các vị trí đã biết.
    
    Parameters:
    - known_positions: Dict mapping từ tile index đến vị trí đã biết
    - use_mrv: Boolean cho biết có sử dụng MRV không
    - use_lcv: Boolean cho biết có sử dụng LCV không
    
    Returns:
    - solution: Matrix 3x3 chứa giải pháp hoặc None nếu không tìm thấy
    - stats: Thống kê về quá trình tìm kiếm
    """
    # Khởi tạo CSP
    variables, domains, constraints, assigned = init_puzzle_csp(known_positions)
    
    # Chọn heuristic
    select_var = None
    if use_mrv:
        select_var = mrv_degree  # Kết hợp MRV và degree heuristic
    
    order_values = None
    if use_lcv:
        order_values = lcv
    
    # Chạy backtracking
    start_time = time.time()
    solution, stats = backtracking_search(
        variables, domains, constraints, assigned,
        order_domain_values=order_values,
        select_unassigned_variable=select_var
    )
    end_time = time.time()
    
    # Bổ sung thông tin về thời gian
    stats['time'] = end_time - start_time
    
    if solution:
        # Chuyển giải pháp thành trạng thái puzzle
        puzzle_state = positions_to_state(solution)
        return puzzle_state, stats
    else:
        return None, stats

# Giải bài toán 8-puzzle bằng AC-3 với các vị trí đã biết
def solve_puzzle_with_ac3(known_positions):
    """
    Giải bài toán 8-puzzle bằng AC-3 với các vị trí đã biết.
    
    Parameters:
    - known_positions: Dict mapping từ tile index đến vị trí đã biết
    
    Returns:
    - solution: Matrix 3x3 chứa giải pháp hoặc None nếu không tìm thấy
    - stats: Thống kê về quá trình tìm kiếm
    """
    # Khởi tạo CSP
    variables, domains, constraints, assigned = init_puzzle_csp(known_positions)
    
    # Chạy AC-3
    start_time = time.time()
    success, reduced_domains, step_count = ac3(variables, domains, constraints, assigned)
    end_time = time.time()
    
    stats = {
        'time': end_time - start_time,
        'steps': step_count,
        'domains': reduced_domains
    }
    
    # Nếu có giải pháp duy nhất từ AC-3
    if success:
        # Kiểm tra xem mỗi domain có chính xác một giá trị không
        unique_solution = all(len(domain) == 1 for domain in reduced_domains.values())
        
        if unique_solution:
            solution = {}
            for var, domain in reduced_domains.items():
                solution[var] = next(iter(domain))
            
            # Chuyển giải pháp thành trạng thái puzzle
            puzzle_state = positions_to_state(solution)
            return puzzle_state, stats
        else:
            # AC-3 không đủ để tìm giải pháp duy nhất
            stats['unique_solution'] = False
            stats['domains'] = reduced_domains
            return None, stats
    else:
        # Không có giải pháp
        return None, stats 