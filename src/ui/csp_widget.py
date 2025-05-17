import random
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QPushButton, QLabel, QRadioButton, QButtonGroup,
                            QGroupBox, QTextEdit, QComboBox, QSplitter, QDialog, QDialogButtonBox,
                            QSpinBox, QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class CSPWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Title
        title_label = QLabel("Bài toán Thoả mãn Ràng buộc (Constraint Satisfaction Problem)")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Problem statement
        problem_text = QTextEdit()
        problem_text.setReadOnly(True)
        problem_text.setMaximumHeight(120)
        problem_text.setHtml("""
        <div style='font-size: 12px; text-align: justify; margin: 5px;'>
            <p><b>Phát biểu bài toán:</b> Giải bài toán 8-puzzle bằng cách tìm các giá trị thỏa mãn ràng buộc.</p>
            <p><b>Biến:</b> Các vị trí (1-8) trên bảng và ô trống (0)</p>
            <p><b>Miền giá trị:</b> Các vị trí hợp lệ trong bảng 3x3</p>
            <p><b>Ràng buộc:</b> 
                (1) Mỗi vị trí chỉ chứa một giá trị từ 0-8; 
                (2) Mỗi giá trị từ 0-8 chỉ xuất hiện một lần; 
                (3) Các bước di chuyển phải hợp lệ (ô trống chỉ di chuyển lên/xuống/trái/phải)
            </p>
            <p><b>Mục tiêu:</b> Từ trạng thái ban đầu, sử dụng AC-3 để thu hẹp miền giá trị, sau đó dùng backtracking để tìm cấu hình hợp lệ dẫn đến trạng thái đích.</p>
        </div>
        """)
        main_layout.addWidget(problem_text)
        
        # Main content splitter
        content_splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(content_splitter)
        
        # Left section - Configuration Input
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_widget.setLayout(left_layout)
        
        # Puzzle configuration input
        config_group = QGroupBox("Cấu hình Puzzle")
        config_layout = QVBoxLayout()
        
        # Input options
        input_options_layout = QHBoxLayout()
        
        # Empty configuration button
        self.empty_btn = QPushButton("Cấu hình trống")
        self.empty_btn.clicked.connect(self.generate_empty_config)
        input_options_layout.addWidget(self.empty_btn)
        
        # Partial random button
        self.partial_random_btn = QPushButton("Cấu hình ngẫu nhiên một phần")
        self.partial_random_btn.clicked.connect(self.generate_partial_random)
        input_options_layout.addWidget(self.partial_random_btn)
        
        # Solved configuration button
        self.solved_btn = QPushButton("Cấu hình đã giải")
        self.solved_btn.clicked.connect(self.generate_solved_state)
        input_options_layout.addWidget(self.solved_btn)
        
        config_layout.addLayout(input_options_layout)
        
        # Configuration tables
        tables_layout = QGridLayout()
        
        # Puzzle table 3x3
        puzzle_group = QGroupBox("Cấu hình 8-Puzzle")
        puzzle_layout = QVBoxLayout()
        self.puzzle_table = QTableWidget(3, 3)
        self.puzzle_table.horizontalHeader().setVisible(False)
        self.puzzle_table.verticalHeader().setVisible(False)
        puzzle_layout.addWidget(self.puzzle_table)
        puzzle_group.setLayout(puzzle_layout)
        tables_layout.addWidget(puzzle_group, 0, 0, 1, 2)
        
        config_layout.addLayout(tables_layout)
        
        # Initialize tables
        self.initialize_tables()
        
        config_group.setLayout(config_layout)
        left_layout.addWidget(config_group)
        
        # Algorithm selection
        algo_group = QGroupBox("Lựa chọn thuật toán")
        algo_layout = QVBoxLayout()
        
        self.algo_group = QButtonGroup()
        self.ac3_rb = QRadioButton("AC-3 (Arc Consistency)")
        self.ac3_rb.setChecked(True)
        self.backtracking_rb = QRadioButton("Backtracking")
        self.combined_rb = QRadioButton("AC-3 + Backtracking")
        
        self.algo_group.addButton(self.ac3_rb, 1)
        self.algo_group.addButton(self.backtracking_rb, 2)
        self.algo_group.addButton(self.combined_rb, 3)
        
        algo_layout.addWidget(self.ac3_rb)
        algo_layout.addWidget(self.backtracking_rb)
        algo_layout.addWidget(self.combined_rb)
        
        # Number of solutions to find
        solutions_layout = QHBoxLayout()
        solutions_layout.addWidget(QLabel("Số lượng giải pháp cần tìm:"))
        self.solutions_spinbox = QSpinBox()
        self.solutions_spinbox.setRange(1, 10)
        self.solutions_spinbox.setValue(3)
        solutions_layout.addWidget(self.solutions_spinbox)
        algo_layout.addLayout(solutions_layout)
        
        # Execute button
        self.execute_btn = QPushButton("Thực thi thuật toán")
        self.execute_btn.clicked.connect(self.execute_algorithm)
        algo_layout.addWidget(self.execute_btn)
        
        algo_group.setLayout(algo_layout)
        left_layout.addWidget(algo_group)
        
        # Right section - Results
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)
        
        # Domain display
        domain_group = QGroupBox("Miền giá trị sau khi áp dụng AC-3")
        domain_layout = QVBoxLayout()
        
        self.domain_text = QTextEdit()
        self.domain_text.setReadOnly(True)
        domain_layout.addWidget(self.domain_text)
        
        domain_group.setLayout(domain_layout)
        right_layout.addWidget(domain_group)
        
        # Results section
        results_group = QGroupBox("Kết quả")
        results_layout = QVBoxLayout()
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("QTextEdit { font-family: monospace; }")
        results_layout.addWidget(self.result_text)
        
        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group)
        
        # Add left and right sections to splitter
        content_splitter.addWidget(left_widget)
        content_splitter.addWidget(right_widget)
        content_splitter.setSizes([600, 800])  # Initial sizes
    
    def initialize_tables(self):
        """Khởi tạo bảng puzzle với các ô nhập liệu"""
        # Initialize 3x3 puzzle table
        for i in range(3):
            self.puzzle_table.setColumnWidth(i, 60)
            self.puzzle_table.setRowHeight(i, 60)
            for j in range(3):
                combo = QComboBox()
                combo.addItem("")  # Empty option
                combo.addItems([str(x) for x in range(9)])
                self.puzzle_table.setCellWidget(i, j, combo)
        
        # Resize columns to content
        self.puzzle_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.puzzle_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def generate_empty_config(self):
        """Tạo cấu hình trống cho các bảng"""
        # Clear all selections
        for i in range(3):
            for j in range(3):
                self.puzzle_table.cellWidget(i, j).setCurrentIndex(0)
        
        self.result_text.clear()
        self.domain_text.clear()
        self.domain_text.setText("Miền giá trị ban đầu chưa được thu hẹp.\nChạy thuật toán AC-3 để thấy kết quả.")
    
    def generate_partial_random(self):
        """Tạo cấu hình ngẫu nhiên một phần"""
        # Clear first
        self.generate_empty_config()
        
        # Create a valid partial configuration
        used_values = set()
        for _ in range(3):  # Fill about 1/3 of the puzzle
            i, j = random.randint(0, 2), random.randint(0, 2)
            
            # Ensure unique values
            val = random.randint(0, 8)
            while val in used_values:
                val = random.randint(0, 8)
                
            used_values.add(val)
            self.puzzle_table.cellWidget(i, j).setCurrentIndex(val + 1)  # +1 because index 0 is empty
        
        self.domain_text.setText("Một số giá trị đã được thiết lập ngẫu nhiên.\nChạy thuật toán AC-3 để thu hẹp miền giá trị.")
    
    def generate_solved_state(self):
        """Thiết lập cấu hình trạng thái đã giải"""
        # Clear first
        self.generate_empty_config()
        
        # Set values to solved state (1-8 and 0 in bottom right)
        solved_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        
        for i in range(3):
            for j in range(3):
                val = solved_state[i][j]
                self.puzzle_table.cellWidget(i, j).setCurrentIndex(val + 1)  # +1 because index 0 is empty
        
        self.domain_text.setText("Cấu hình đã giải được thiết lập.\nĐây là một cấu hình hoàn chỉnh và hợp lệ.")
    
    def get_current_configuration(self):
        """Lấy cấu hình hiện tại từ bảng puzzle"""
        config = [[-1 for _ in range(3)] for _ in range(3)]
        
        for i in range(3):
            for j in range(3):
                combo = self.puzzle_table.cellWidget(i, j)
                text = combo.currentText()
                if text:  # Not empty
                    config[i][j] = int(text)
                    
        return config
    
    def execute_algorithm(self):
        """Thực thi thuật toán CSP đã chọn"""
        algorithm = self.get_selected_algorithm()
        
        # Lấy cấu hình hiện tại
        config = self.get_current_configuration()
        
        # Khởi tạo các biến và miền giá trị
        variables, domains = self.setup_csp_variables(config)
        
        # Thực thi thuật toán tương ứng
        if algorithm == "AC-3":
            self.run_ac3(variables, domains)
        elif algorithm == "Backtracking":
            self.run_backtracking(variables, domains)
        elif algorithm == "Combined":
            # Chạy AC-3 trước
            revised_domains = self.run_ac3(variables, domains, return_domains=True)
            # Sau đó chạy Backtracking với miền đã thu hẹp
            self.run_backtracking(variables, revised_domains)
    
    def get_selected_algorithm(self):
        """Lấy thuật toán đang được chọn"""
        if self.ac3_rb.isChecked():
            return "AC-3"
        elif self.backtracking_rb.isChecked():
            return "Backtracking"
        elif self.combined_rb.isChecked():
            return "Combined"
        return "Unknown"
    
    def setup_csp_variables(self, config):
        """Thiết lập các biến và miền giá trị dựa trên cấu hình"""
        variables = []
        domains = {}
        
        # Lấy danh sách giá trị đã được sử dụng
        used_values = set()
        for i in range(3):
            for j in range(3):
                if config[i][j] != -1:
                    used_values.add(config[i][j])
        
        # Danh sách giá trị còn lại cho các ô trống
        available_values = [v for v in range(9) if v not in used_values]
        
        # Create variables for each cell in the grid
        for i in range(3):
            for j in range(3):
                var_name = f"cell_{i}_{j}"
                variables.append(var_name)
                
                if config[i][j] != -1:  # Value already set
                    domains[var_name] = [config[i][j]]
                else:
                    # Tất cả các ô trống đều có thể chứa tất cả các giá trị còn lại
                    domains[var_name] = available_values.copy()
        
        return variables, domains
    
    def run_ac3(self, variables, domains, return_domains=False):
        """Chạy thuật toán AC-3"""
        self.result_text.clear()
        self.domain_text.clear()
        
        # Copy domains to avoid modifying the original
        domains = {var: list(values) for var, values in domains.items()}
        
        # Setup constraints (arcs)
        constraints = []
        
        # Add row constraints
        for i in range(3):
            for j in range(3):
                for k in range(j+1, 3):
                    constraints.append((f"cell_{i}_{j}", f"cell_{i}_{k}"))
        
        # Add column constraints
        for j in range(3):
            for i in range(3):
                for k in range(i+1, 3):
                    constraints.append((f"cell_{i}_{j}", f"cell_{k}_{j}"))
        
        # Add constraints for valid moves (cells that can contain the empty space)
        # In 8-puzzle, the empty space (0) can only move to adjacent cells
        for i in range(3):
            for j in range(3):
                # Get neighbors
                neighbors = []
                if i > 0: neighbors.append((i-1, j))  # Up
                if i < 2: neighbors.append((i+1, j))  # Down
                if j > 0: neighbors.append((i, j-1))  # Left
                if j < 2: neighbors.append((i, j+1))  # Right
                
                # Add constraints between this cell and its neighbors
                for ni, nj in neighbors:
                    constraints.append((f"cell_{i}_{j}", f"cell_{ni}_{nj}"))
        
        # Initialize queue with all constraints
        queue = constraints.copy()
        
        # AC-3 algorithm
        result = "<h3>Thuật toán AC-3 (Arc Consistency):</h3>\n"
        result += "<p>AC-3 sẽ loại bỏ các giá trị không thỏa mãn ràng buộc từ miền của các biến.</p>\n"
        
        steps = []
        revisions = 0
        
        while queue:
            xi, xj = queue.pop(0)
            revision_made = False
            removed_values = []
            
            # Check if we need to revise the domain of xi
            for x in list(domains[xi]):  # Create a copy to avoid modifying during iteration
                # Check if there's a value in xj that satisfies the constraint
                satisfiable = False
                
                for y in domains[xj]:
                    if self.satisfies_constraint(xi, x, xj, y):
                        satisfiable = True
                        break
                
                if not satisfiable:
                    domains[xi].remove(x)
                    removed_values.append(x)
                    revision_made = True
            
            if revision_made:
                revisions += 1
                step = f"<p>- Xét ràng buộc ({xi}, {xj}): loại bỏ {removed_values} khỏi miền của {xi}</p>\n"
                steps.append(step)
                
                # Add neighboring arcs back to the queue
                for xk, xl in constraints:
                    if xl == xi and xk != xj:
                        queue.append((xk, xi))
                    elif xk == xi and xl != xj:
                        queue.append((xi, xl))
            
            # Check for empty domains
            if not domains[xi]:
                break
        
        # Display the revised domains
        domain_text = "<h3>Miền giá trị sau khi áp dụng AC-3:</h3>\n"
        
        # Group domains by row
        for i in range(3):
            domain_text += f"<h4>Hàng {i+1}:</h4>\n<ul>\n"
            for j in range(3):
                var = f"cell_{i}_{j}"
                domain_text += f"<li>Ô ({i},{j}): {domains[var]}</li>\n"
            domain_text += "</ul>\n"
        
        # Update domain text
        self.domain_text.setHtml(domain_text)
        
        # Display AC-3 results
        result += f"<p>AC-3 đã thực hiện {revisions} lần sửa đổi miền.</p>\n"
        
        # Show steps
        result += "<h4>Các bước thực hiện:</h4>\n"
        for step in steps[:20]:  # Limit to 20 steps for display
            result += step
        
        if len(steps) > 20:
            result += f"<p><i>...và {len(steps) - 20} bước khác</i></p>\n"
        
        # Check for empty domains
        empty_domains = [var for var, domain in domains.items() if not domain]
        if empty_domains:
            result += "<h4>Kết quả:</h4>\n"
            result += f"<p style='color:red'>❌ Không tìm thấy giải pháp. Các biến sau có miền rỗng: {empty_domains}</p>\n"
        else:
            result += "<h4>Kết quả:</h4>\n"
            fixed_vars = sum(1 for domain in domains.values() if len(domain) == 1)
            result += f"<p style='color:green'>✓ AC-3 hoàn thành. {fixed_vars}/{len(variables)} biến đã xác định đầy đủ.</p>\n"
            
            # Check if all variables are fixed
            if fixed_vars == len(variables):
                result += "<p>Đã tìm thấy một giải pháp hoàn chỉnh!</p>\n"
                
                # Extract the solution
                solution = {}
                for var, domain in domains.items():
                    solution[var] = domain[0]
                
                # Verify the solution
                is_valid = self.verify_solution(solution)
                if is_valid:
                    result += "<p style='color:green'>✓ Giải pháp thỏa mãn tất cả các ràng buộc!</p>\n"
                else:
                    result += "<p style='color:red'>❌ Giải pháp không thỏa mãn tất cả các ràng buộc.</p>\n"
                
                # Display the solution
                result += self.format_solution(solution)
        
        self.result_text.setHtml(result)
        
        if return_domains:
            return domains
    
    def run_backtracking(self, variables, domains, max_solutions=None):
        """Chạy thuật toán Backtracking để tìm các giải pháp"""
        self.result_text.clear()
        if not self.backtracking_rb.isChecked():  # If combined mode, don't clear domain text
            self.domain_text.clear()
        
        # Copy domains to avoid modifying the original
        domains = {var: list(values) for var, values in domains.items()}
        
        if max_solutions is None:
            max_solutions = self.solutions_spinbox.value()
        
        result = "<h3>Thuật toán Backtracking:</h3>\n"
        result += f"<p>Tìm tối đa {max_solutions} giải pháp thỏa mãn tất cả các ràng buộc.</p>\n"
        
        # Backtracking algorithm
        solutions = []
        steps = []
        assigned_values = []  # Track assigned values for alldiff constraint
        
        def backtrack(assignment, level=0):
            if len(solutions) >= max_solutions:
                return
            
            if len(assignment) == len(variables):
                # Kiểm tra xem giải pháp có hợp lệ không
                puzzle = [[0 for _ in range(3)] for _ in range(3)]
                for var, val in assignment.items():
                    parts = var.split('_')
                    row, col = int(parts[1]), int(parts[2])
                    puzzle[row][col] = val
                
                # Đảm bảo mỗi giá trị từ 0-8 xuất hiện đúng một lần
                values = [puzzle[i][j] for i in range(3) for j in range(3)]
                if len(set(values)) == 9 and set(values) == set(range(9)):
                    # Found a valid solution
                    solutions.append(assignment.copy())
                return
            
            # Choose variable with minimum remaining values (MRV)
            unassigned = [v for v in variables if v not in assignment]
            var = min(unassigned, key=lambda v: len(domains[v]))
            
            # Try each value in the domain
            for value in domains[var]:
                # Skip values that have already been assigned (alldiff constraint)
                if value in [assignment[v] for v in assignment]:
                    continue
                
                # Check if value is consistent with current assignment
                if self.is_consistent(var, value, assignment):
                    # Add to assignment
                    assignment[var] = value
                    steps.append(f"<p>{'&nbsp;' * level * 2}- Gán {var} = {value} (mức {level})</p>\n")
                    
                    # Recursive call
                    backtrack(assignment, level + 1)
                    
                    # Backtrack
                    if len(solutions) < max_solutions:
                        assignment.pop(var)
                        steps.append(f"<p>{'&nbsp;' * level * 2}- <i>Quay lui từ {var} = {value}</i></p>\n")
        
        # Start backtracking with empty assignment
        backtrack({})
        
        # Display the results
        if not steps:
            result += "<p>Không có bước nào được thực hiện. Có thể các miền giá trị ban đầu không hợp lệ.</p>\n"
        else:
            result += "<h4>Các bước thực hiện:</h4>\n"
            for step in steps[:30]:  # Limit to 30 steps for display
                result += step
            
            if len(steps) > 30:
                result += f"<p><i>...và {len(steps) - 30} bước khác</i></p>\n"
        
        result += f"<h4>Tìm thấy {len(solutions)} giải pháp:</h4>\n"
        
        if not solutions:
            result += "<p style='color:red'>❌ Không tìm thấy giải pháp thỏa mãn.</p>\n"
        else:
            for i, solution in enumerate(solutions):
                result += f"<h5>Giải pháp {i+1}:</h5>\n"
                result += self.format_solution(solution)
        
        self.result_text.setHtml(result)
    
    def satisfies_constraint(self, xi, x, xj, y):
        """Kiểm tra xem hai biến và giá trị có thỏa mãn ràng buộc không"""
        # Parse cell positions from variable names
        xi_parts = xi.split('_')
        xj_parts = xj.split('_')
        
        xi_row, xi_col = int(xi_parts[1]), int(xi_parts[2])
        xj_row, xj_col = int(xj_parts[1]), int(xj_parts[2])
        
        # Alldiff constraint - Mỗi giá trị chỉ xuất hiện một lần
        if x == y and x != -1:
            return False
        
        # Check valid move constraint for empty space (0)
        # In 8-puzzle, the empty space (0) can only move to adjacent cells
        if (x == 0 or y == 0) and not self.are_adjacent(xi_row, xi_col, xj_row, xj_col):
            return False
        
        return True
    
    def are_adjacent(self, row1, col1, row2, col2):
        """Check if two cells are adjacent (including diagonals)"""
        return abs(row1 - row2) + abs(col1 - col2) == 1  # Manhattan distance of 1
    
    def is_consistent(self, var, value, assignment):
        """Kiểm tra xem giá trị của biến có nhất quán với các giá trị đã gán không"""
        var_parts = var.split('_')
        var_row, var_col = int(var_parts[1]), int(var_parts[2])
        
        # Kiểm tra xem giá trị đã được sử dụng ở đâu đó chưa
        for r in range(3):
            for c in range(3):
                other_var = f"cell_{r}_{c}"
                if other_var in assignment and assignment[other_var] == value:
                    return False
        
        # Check row constraints
        for j in range(3):
            other_var = f"cell_{var_row}_{j}"
            if other_var in assignment and assignment[other_var] == value:
                return False
        
        # Check column constraints
        for i in range(3):
            other_var = f"cell_{i}_{var_col}"
            if other_var in assignment and assignment[other_var] == value:
                return False
        
        # Check valid move constraint for empty space (0)
        if value == 0:
            # For the empty space, check if it can be placed here based on adjacent cells
            valid_placement = False
            
            # Check if there's an adjacent cell with empty space in the assignment
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # Up, Down, Left, Right
                new_row, new_col = var_row + di, var_col + dj
                if 0 <= new_row < 3 and 0 <= new_col < 3:
                    neighbor_var = f"cell_{new_row}_{new_col}"
                    if neighbor_var in assignment and assignment[neighbor_var] == 0:
                        valid_placement = True
                        break
            
            # If there are no assignments yet or this is the first placement of empty space,
            # allow it to be placed anywhere
            if not any(assignment.get(f"cell_{i}_{j}") == 0 for i in range(3) for j in range(3)):
                valid_placement = True
            
            if not valid_placement:
                return False
        
        return True
    
    def verify_solution(self, solution):
        """Verify if a solution satisfies all constraints"""
        # Extract puzzle state
        puzzle = [[0 for _ in range(3)] for _ in range(3)]
        for var, value in solution.items():
            parts = var.split('_')
            row, col = int(parts[1]), int(parts[2])
            puzzle[row][col] = value
        
        # Check for duplicate values
        values = [puzzle[i][j] for i in range(3) for j in range(3)]
        if len(set(values)) != 9 or set(values) != set(range(9)):
            print("Lỗi: Không chứa đúng các giá trị 0-8:", values)
            return False
        
        # Kiểm tra các ràng buộc khác (ví dụ: ô trống phải ở một vị trí cụ thể)
        # Tùy thuộc vào yêu cầu cụ thể của bài toán
        
        return True
    
    def format_solution(self, solution):
        """Format a solution for display"""
        # Extract puzzle state
        puzzle = [[0 for _ in range(3)] for _ in range(3)]
        for var, value in solution.items():
            parts = var.split('_')
            row, col = int(parts[1]), int(parts[2])
            puzzle[row][col] = value
        
        # Kiểm tra xem giải pháp có hợp lệ không
        values = [puzzle[i][j] for i in range(3) for j in range(3)]
        is_valid = len(set(values)) == 9 and set(values) == set(range(9))
        
        # Format the solution
        result = "<div style='margin-left:20px'>\n"
        if not is_valid:
            result += "<p style='color:red'>Cảnh báo: Giải pháp không hợp lệ! Các giá trị bị trùng lặp hoặc thiếu.</p>\n"
        
        result += "<table border='1' cellpadding='10' style='border-collapse:collapse; font-size:14px; margin:10px;'>\n"
        
        for i in range(3):
            result += "<tr>\n"
            for j in range(3):
                val = puzzle[i][j]
                cell_style = "background-color:#555; color:white;" if val == 0 else ""
                result += f"<td style='text-align:center; {cell_style}'>{val}</td>\n"
            result += "</tr>\n"
        
        result += "</table>\n"
        result += "</div>\n"
        
        return result 