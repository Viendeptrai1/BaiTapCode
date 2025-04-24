import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                           QVBoxLayout, QMessageBox, QProgressBar, QLabel,
                           QTabWidget, QPushButton, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import time
import traceback
import itertools

# Import các thành phần GUI và logic từ các module khác
from src.core.buzzle_logic import Buzzle, generate_random_solvable_state, is_solvable
from .gui_components import (PuzzleBoard, SolutionNavigationPanel, ControlPanel,
                            ResultPanel, SolverThread)
# algorithm_manager không cần import trực tiếp vào đây vì ControlPanel/SolverThread đã dùng

class PuzzleWindow(QMainWindow):
    def random_backtracking_start_state(self):
        random_data = generate_random_solvable_state()
        self.backtracking_start_board.update_board(random_data)
        # Optionally reset navigator and result panel for CSP tab
        self.backtracking_navigator.reset_display()
        self.backtracking_result_panel.clear_displays()
        self.backtracking_stats_label.setText("Ready. Randomized a new start state for CSP.")
        self.update_status("Randomized CSP start state.")

    def start_backtracking_search(self):
        initial_state = Buzzle()  # Or get from UI if needed
        goal_state = Buzzle([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.backtracking_start_board.update_board(initial_state.data)
        self.backtracking_goal_board.update_board(goal_state.data)
        self.progress_bar.setVisible(True)
        self.backtracking_solve_btn.setEnabled(False)
        self.update_status("Solving with Backtracking Search (CSP)...", True)
        self.backtracking_thread = SolverThread("backtracking_search", initial_state)
        self.backtracking_thread.solution_ready.connect(self.on_backtracking_solution_ready)
        self.backtracking_thread.error_occurred.connect(self.on_solver_error)
        self.backtracking_thread.finished.connect(self.on_backtracking_solver_finished)
        self.backtracking_thread.start()

    def on_backtracking_solution_ready(self, path, nodes, fringe):
        formatted_path = path
        self.backtracking_result_panel.update_path_display(Buzzle().data, formatted_path)
        self.backtracking_navigator.set_solution(Buzzle().data, formatted_path)
        if path:
            stats = f"Backtracking search hoàn thành với {len(path)} bước.\nSố trạng thái kiểm tra: {nodes}\nKích thước hàng đợi tối đa: {fringe}"
            self.update_status("Backtracking search hoàn thành thành công.", False)
        else:
            stats = f"Không tìm thấy giải pháp trong không gian CSP.\nSố trạng thái kiểm tra: {nodes}\nKích thước hàng đợi tối đa: {fringe}"
            self.update_status("Backtracking search không tìm được giải pháp.", False)
        self.backtracking_stats_label.setText(stats)

    def on_backtracking_solver_finished(self):
        self.backtracking_solve_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def init_backtracking_tab(self):
        layout = QHBoxLayout(self.backtracking_tab)

        # --- Panel trái (Bảng hiển thị) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # Bảng hiển thị
        boards_container = QWidget()
        boards_layout = QHBoxLayout(boards_container)

        self.backtracking_start_board = PuzzleBoard("Initial State (CSP)")
        self.backtracking_goal_board = PuzzleBoard("Goal State")
        self.backtracking_navigator = SolutionNavigationPanel()

        boards_layout.addWidget(self.backtracking_start_board, stretch=1)
        boards_layout.addWidget(self.backtracking_goal_board, stretch=1)
        boards_layout.addWidget(self.backtracking_navigator, stretch=1)

        boards_container.setLayout(boards_layout)

        # Panel kết quả và mô tả
        self.backtracking_result_panel = ResultPanel()

        left_layout.addWidget(boards_container, stretch=3)
        left_layout.addWidget(self.backtracking_result_panel, stretch=2)

        # --- Panel phải (Điều khiển) ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Control Panel cho Backtracking Search
        input_group = QGroupBox("Backtracking Search (CSP) Input")
        input_layout = QVBoxLayout()

        # Giải thích về thuật toán
        explanation = QLabel("This tab uses Backtracking Search to solve the 8-puzzle as a Constraint Satisfaction Problem (CSP). The algorithm explores possible assignments for each tile, backtracking when constraints are violated.")
        explanation.setWordWrap(True)
        input_layout.addWidget(explanation)

        # Nút điều khiển
        self.backtracking_solve_btn = QPushButton("Run Backtracking Search (CSP)")
        self.backtracking_solve_btn.setStyleSheet("QPushButton { background-color: #a8dda8; font-weight: bold; }")
        input_layout.addWidget(self.backtracking_solve_btn)

        # Nút random state cho CSP
        self.backtracking_random_btn = QPushButton("Random State (CSP)")
        self.backtracking_random_btn.setStyleSheet("QPushButton { background-color: #b8d6ff; font-weight: bold; }")
        input_layout.addWidget(self.backtracking_random_btn)

        # Thống kê
        stats_group = QGroupBox("Solver Statistics")
        stats_layout = QVBoxLayout()
        self.backtracking_stats_label = QLabel("Ready. Click 'Run Backtracking Search (CSP)' to begin.")
        self.backtracking_stats_label.setWordWrap(True)
        self.backtracking_stats_label.setAlignment(Qt.AlignTop)
        self.backtracking_stats_label.setMinimumHeight(60)
        stats_layout.addWidget(self.backtracking_stats_label)
        stats_group.setLayout(stats_layout)

        input_group.setLayout(input_layout)
        right_layout.addWidget(input_group)
        right_layout.addWidget(stats_group)
        right_layout.addStretch()

        # Thêm vào layout chính
        layout.addWidget(left_panel, stretch=7)
        layout.addWidget(right_panel, stretch=3)

        # Kết nối sự kiện
        self.backtracking_solve_btn.clicked.connect(self.start_backtracking_search)
        self.backtracking_random_btn.clicked.connect(self.random_backtracking_start_state)

        # Cập nhật mô tả thuật toán trong panel kết quả
        self.backtracking_result_panel.update_algorithm_description("backtracking_search")

        # Khởi tạo trạng thái đích giống tab thông thường
        self.backtracking_goal_state = Buzzle([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.backtracking_goal_board.update_board(self.backtracking_goal_state.data)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("8-Puzzle Solver")
        self.setGeometry(100, 100, 1200, 700) # Kích thước cửa sổ ban đầu

        # --- Widget chính và Layout chính ---
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)

        # --- Tab Widget ---
        self.tab_widget = QTabWidget()
        
        # Tạo tab cho các thuật toán thông thường
        self.normal_tab = QWidget()
        self.init_normal_tab()
        self.tab_widget.addTab(self.normal_tab, "Standard Algorithms")
        
        # Tạo tab cho Backtracking Search (CSP)
        self.backtracking_tab = QWidget()
        self.init_backtracking_tab()
        self.tab_widget.addTab(self.backtracking_tab, "Backtracking Search (CSP)")
        
        main_layout.addWidget(self.tab_widget)
        self.setCentralWidget(main_widget)

        # --- Status Bar ---
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.setFixedHeight(15)
        self.progress_bar.setVisible(False) # Ẩn ban đầu
        self.statusBar().addPermanentWidget(self.progress_bar)

    def init_normal_tab(self):
        """Khởi tạo tab cho các thuật toán thông thường"""
        layout = QHBoxLayout(self.normal_tab) # Chia ngang: Left (Boards+Results), Right (Controls)

        # --- Panel Trái ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel) # Chia dọc: Top (Boards), Bottom (Results)

        # Container cho các bảng Puzzle (Start, Goal, Navigator)
        boards_container = QWidget()
        boards_layout = QHBoxLayout(boards_container)
        boards_layout.setSpacing(15)

        self.start_board = PuzzleBoard("Initial State")
        self.goal_board = PuzzleBoard("Goal State")
        self.solution_navigator = SolutionNavigationPanel()

        boards_layout.addWidget(self.start_board, stretch=1)
        boards_layout.addWidget(self.goal_board, stretch=1)
        boards_layout.addWidget(self.solution_navigator, stretch=1)

        # Panel kết quả (Text path + Description)
        self.result_panel = ResultPanel()

        # Thêm vào layout trái
        left_layout.addWidget(boards_container, stretch=3) # Boards chiếm nhiều hơn
        left_layout.addWidget(self.result_panel, stretch=2) # Result ít hơn

        # --- Panel Phải ---
        self.control_panel = ControlPanel()

        # --- Thêm vào layout chính ---
        layout.addWidget(left_panel, stretch=7) # Panel trái chiếm nhiều hơn
        layout.addWidget(self.control_panel, stretch=3) # Panel phải ít hơn

        # --- Khởi tạo trạng thái ---
        self.start_state = Buzzle() # Trạng thái mặc định
        self.goal_state = Buzzle([[1, 2, 3], [4, 5, 6], [7, 8, 0]]) # Đích cố định
        self.current_solution_path = [] # Lưu path hiện tại
        self.update_display() # Cập nhật hiển thị ban đầu

        # --- Kết nối signals từ ControlPanel ---
        self.control_panel.load_clicked.connect(self.load_state_from_input)
        self.control_panel.reset_clicked.connect(self.reset_all)
        self.control_panel.solve_clicked.connect(self.start_solving)
        self.control_panel.random_start_clicked.connect(self.generate_random_start)

        # --- Kết nối signal từ AlgorithmSelectionPanel (trong ControlPanel) ---
        self.control_panel.algo_select_panel.algorithm_changed.connect(
            self.update_algorithm_description
        )
        # Cập nhật mô tả cho thuật toán mặc định ban đầu
        self.update_algorithm_description(self.control_panel.algo_select_panel.get_selected_algorithm())

    def init_belief_tab(self):
        """Khởi tạo tab cho thuật toán Belief-based Search"""
        layout = QHBoxLayout(self.belief_tab)
        
        # --- Panel trái (Bảng hiển thị) ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Bảng hiển thị
        boards_container = QWidget()
        boards_layout = QHBoxLayout(boards_container)
        
        self.belief_start_board = PuzzleBoard("Initial Belief State")
        self.belief_goal_board = PuzzleBoard("Goal State")
        self.belief_navigator = SolutionNavigationPanel()
        
        boards_layout.addWidget(self.belief_start_board, stretch=1)
        boards_layout.addWidget(self.belief_goal_board, stretch=1)
        boards_layout.addWidget(self.belief_navigator, stretch=1)
        
        boards_container.setLayout(boards_layout)
        
        # Panel kết quả và mô tả
        self.belief_result_panel = ResultPanel()
        
        left_layout.addWidget(boards_container, stretch=3)
        left_layout.addWidget(self.belief_result_panel, stretch=2)
        
        # --- Panel phải (Điều khiển) ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Control Panel cho Belief-based Search
        input_group = QGroupBox("Belief Search Input")
        input_layout = QVBoxLayout()
        
        # Giải thích về thuật toán
        explanation = QLabel("This algorithm simulates a Partially Observable MDP where only the first 6 cells [1,2,3,4,5,6] (first and second rows) are visible. We maintain a 'belief state' - a set of all possible states consistent with our observation. The algorithm performs search without further observations after the initial state.")
        explanation.setWordWrap(True)
        input_layout.addWidget(explanation)
        
        # Nút điều khiển
        self.belief_solve_btn = QPushButton("Run Belief-based Search")
        self.belief_solve_btn.setStyleSheet("QPushButton { background-color: #a8dda8; font-weight: bold; }")
        input_layout.addWidget(self.belief_solve_btn)
        
        # Thống kê
        stats_group = QGroupBox("Solver Statistics")
        stats_layout = QVBoxLayout()
        self.belief_stats_label = QLabel("Ready. Click 'Run Belief-based Search' to begin.")
        self.belief_stats_label.setWordWrap(True)
        self.belief_stats_label.setAlignment(Qt.AlignTop)
        self.belief_stats_label.setMinimumHeight(60)
        stats_layout.addWidget(self.belief_stats_label)
        stats_group.setLayout(stats_layout)
        
        input_group.setLayout(input_layout)
        right_layout.addWidget(input_group)
        right_layout.addWidget(stats_group)
        right_layout.addStretch()
        
        # Thêm vào layout chính
        layout.addWidget(left_panel, stretch=7)
        layout.addWidget(right_panel, stretch=3)
        
        # Kết nối sự kiện
        self.belief_solve_btn.clicked.connect(self.start_belief_search)
        
        # Cập nhật mô tả thuật toán trong panel kết quả
        self.belief_result_panel.update_algorithm_description("belief_bfs")
        
        # Khởi tạo trạng thái đích giống tab thông thường
        self.belief_goal_state = Buzzle([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.belief_goal_board.update_board(self.belief_goal_state.data)

    def update_status(self, message, show_progress=False):
        """Cập nhật status bar"""
        self.status_label.setText(message)
        self.progress_bar.setVisible(show_progress)

    def update_display(self):
        """Cập nhật hiển thị bảng Start và Goal"""
        self.start_board.update_board(self.start_state.data)
        self.goal_board.update_board(self.goal_state.data)

    def load_state_from_input(self, input_text):
        """Load start state từ text input của ControlPanel"""
        try:
            numbers = [int(x) for x in input_text.split()]
            if len(numbers) != 9 or set(numbers) != set(range(9)):
                raise ValueError("Input must contain 9 unique numbers from 0 to 8.")

            new_data = [numbers[i:i+3] for i in range(0, 9, 3)]
            # Cập nhật trạng thái bắt đầu
            self.start_state = Buzzle(new_data)
            self.current_solution_path = [] # Xóa solution cũ khi load state mới

            self.update_display() # Cập nhật bảng start
            self.solution_navigator.reset_display() # Reset navigator
            self.result_panel.clear_displays() # Xóa kết quả cũ
            self.update_algorithm_description(self.control_panel.algo_select_panel.get_selected_algorithm()) # Cập nhật lại desc
            self.control_panel.set_stats_text("Ready. Select algorithm and click Solve.")
            self.update_status("Start state loaded from input.")

        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
            self.update_status(f"Input Error: {e}", False)

    def reset_all(self):
        """Reset về trạng thái mặc định và xóa các hiển thị liên quan"""
        self.start_state = Buzzle() # Trạng thái mặc định
        self.current_solution_path = []
        self.update_display()
        self.solution_navigator.reset_display()
        self.result_panel.clear_displays()
        # Control panel đã tự reset input và stats text qua signal nội bộ
        self.update_algorithm_description(self.control_panel.algo_select_panel.get_selected_algorithm())
        self.update_status("States reset to default.")

    def generate_random_start(self):
        """Tạo trạng thái bắt đầu ngẫu nhiên (solvable)"""
        random_data = generate_random_solvable_state()
        self.start_state = Buzzle(random_data)
        self.current_solution_path = []

        # Cập nhật input field trong control panel
        flat_numbers = [str(num) for row in random_data for num in row]
        self.control_panel.set_start_input_text(' '.join(flat_numbers))

        self.update_display()
        self.solution_navigator.reset_display()
        self.result_panel.clear_displays()
        self.update_algorithm_description(self.control_panel.algo_select_panel.get_selected_algorithm())
        self.control_panel.set_stats_text("Ready. Select algorithm and click Solve.")
        self.update_status("Generated random solvable start state.")

    def start_solving(self, algorithm_key):
        """Bắt đầu quá trình giải bằng thuật toán được chọn"""
        self.current_solution_path = [] # Xóa solution cũ
        self.solution_navigator.reset_display() # Reset navigator
        self.result_panel.update_path_display(self.start_state.data, []) # Xóa text path cũ

        algo_name = self.control_panel.algo_select_panel.algorithm_radio_buttons.get(algorithm_key).text()
        self.update_status(f"Solving with {algo_name}...", True)
        self.control_panel.enable_solve_button(False) # Tắt nút Solve

        # Chạy thuật toán trong thread riêng
        # Truyền Buzzle object vào thread
        self.solver_thread = SolverThread(algorithm_key, self.start_state)
        self.solver_thread.solution_ready.connect(self.on_solution_ready)
        self.solver_thread.error_occurred.connect(self.on_solver_error)
        self.solver_thread.finished.connect(self.on_solver_finished)
        self.solver_thread.start()

    def start_belief_search(self):
        """Bắt đầu quá trình giải bằng thuật toán Belief-based Search"""
        # Reset các hiển thị
        self.belief_navigator.reset_display()
        self.belief_result_panel.update_path_display(None, [])
        
        # Trạng thái cục bộ cho belief search với 6 ô đầu tiên đã biết [1,2,3,4,5,6]
        belief_initial_state = Buzzle([[1, 2, 3], [4, 5, 6], [0, 0, 0]])  # Biết 6 ô đầu tiên
        self.belief_start_board.update_board(belief_initial_state.data)
        
        # Cập nhật status
        self.update_status("Running Belief-based Search (without further observations)...", True)
        self.belief_solve_btn.setEnabled(False)
        self.belief_stats_label.setText("Searching in belief space... This may take a moment.")
        
        # Chạy thuật toán trong thread riêng
        class BeliefSolverThread(QThread):
            solution_ready = pyqtSignal(list, int, int, dict)  # Thay đổi signal để nhận debug_info là dict
            error_occurred = pyqtSignal(str)
            
            def __init__(self, initial_state, goal_state, debug=True):
                super().__init__()
                self.initial_state = initial_state
                self.goal_state = goal_state
                self.debug = debug
            
            def run(self):
                try:
                    # Tạo trạng thái niềm tin ban đầu dựa trên các ô đã biết
                    # Với 6 ô đầu tiên đã biết [1,2,3,4,5,6], tạo tất cả các trạng thái khả thi
                    initial_observation = self.initial_state.data[0] + self.initial_state.data[1]  # Lấy 6 số đầu tiên
                    
                    # Tìm số còn thiếu trong observation (0, 7, 8)
                    missing = [i for i in range(9) if i not in initial_observation]
                    
                    # Tạo tất cả các trạng thái khả thi (lưu ý: số 0 phải có đúng 1 lần)
                    initial_belief_states = []
                    
                    # Tạo tất cả các hoán vị của missing
                    for p in itertools.permutations(missing):
                        # Tạo trạng thái mới với các ô đã quan sát và các ô còn lại
                        state_data = [
                            self.initial_state.data[0][:],  # Hàng 1
                            self.initial_state.data[1][:],  # Hàng 2
                            list(p)  # Hàng 3 với các phần tử thiếu
                        ]
                        
                        # Kiểm tra xem trạng thái có hợp lệ không (chỉ có một số 0)
                        if sum(row.count(0) for row in state_data) == 1:
                            # Kiểm tra xem có giải được không
                            if is_solvable(state_data):
                                initial_belief_states.append(Buzzle(state_data))
                    
                    if not initial_belief_states:
                        self.error_occurred.emit("Không tìm thấy trạng thái niềm tin ban đầu phù hợp.")
                        return
                    
                    # Kiểm tra tình trạng goal để truyền vào belief_bfs
                    goal_test = lambda state: state == self.goal_state
                    
                    # Chạy thuật toán belief_bfs
                    result = belief_bfs(
                        initial_belief_states,
                        goal_test,
                        debug=self.debug
                    )
                    
                    path, visited_nodes, max_fringe, debug_info = result
                    
                    # Trả về kết quả
                    self.solution_ready.emit(path if path is not None else [], visited_nodes, max_fringe, debug_info)
                    
                except Exception as e:
                    self.error_occurred.emit(f"Lỗi: {str(e)}")
                    traceback.print_exc()
        
        # Khởi tạo và chạy thread
        self.belief_solver_thread = BeliefSolverThread(
            belief_initial_state,
            self.belief_goal_state,
            debug=True
        )
        
        self.belief_solver_thread.solution_ready.connect(self.on_belief_search_finished)
        self.belief_solver_thread.error_occurred.connect(self.on_solver_error)
        self.belief_solver_thread.finished.connect(self.on_belief_solver_finished)
        self.belief_solver_thread.start()

    def on_solution_ready(self, path, nodes, fringe_or_pop):
        """Xử lý khi thread giải xong và có kết quả"""
        self.current_solution_path = path

        # Cập nhật Solution Navigator
        self.solution_navigator.set_solution(self.start_state.data, path)

        # Cập nhật Result Panel (Text Path)
        self.result_panel.update_path_display(self.start_state.data, path)

        # Cập nhật thống kê trên Control Panel
        algo_key = self.control_panel.algo_select_panel.get_selected_algorithm()
        if path:
            stats = f"Solved in {len(path)} steps.\nNodes evaluated/expanded: {nodes}\nMax fringe/population size: {fringe_or_pop}"
            self.update_status(f"Solution found ({len(path)} steps).", False)
        elif algo_key.lower() in ["genetic_algorithm", "simulated_annealing", "hill_climbing_max", "hill_climbing_random"]:
             # Các thuật toán này có thể không tìm thấy goal hoặc không tối ưu path
             stats = f"Algorithm finished.\nGoal state reached: {Buzzle(self.solution_navigator.current_step_board.tiles).is_goal() if self.solution_navigator.current_step_index > -1 else 'N/A'}\nNodes evaluated: {nodes}\nMax neighbors/population: {fringe_or_pop}"
             self.update_status(f"{algo_key.upper()} finished. Goal not guaranteed.", False)
        else:
            # Các thuật toán tìm kiếm khác không tìm thấy đường đi
            stats = f"No solution found.\nNodes expanded: {nodes}\nMax fringe size: {fringe_or_pop}"
            self.update_status("No solution found.", False)

        self.control_panel.set_stats_text(stats)

    def on_belief_search_finished(self, path, nodes, fringe, debug_info):
        """Xử lý khi thread giải belief search xong và có kết quả"""
        # Trạng thái ban đầu với 6 ô đầu biết trước [1,2,3,4,5,6]
        initial_state_data = [[1, 2, 3], [4, 5, 6], [0, 0, 0]]
        
        # Cập nhật Solution Navigator
        self.belief_navigator.set_solution(initial_state_data, path)
        
        # Chuẩn bị debug text chi tiết cho ô kết quả 
        debug_text = "==================================================\n"
        debug_text += "      KẾT QUẢ CHI TIẾT TÌM KIẾM BELIEF STATE\n"
        debug_text += "==================================================\n\n"
        
        # Xử lý debug_info thành văn bản có cấu trúc
        if debug_info and "belief_states" in debug_info:
            for i, info in enumerate(debug_info["belief_states"]):
                debug_text += f"{info}\n"
        
        # Thêm tóm tắt đường đi tìm được vào cuối
        if path:
            debug_text += f"\n{'='*50}\n"
            debug_text += "TÓM TẮT ĐƯỜNG ĐI\n"
            debug_text += f"{'='*50}\n"
            debug_text += f"Tìm thấy đường đi với {len(path)} bước.\n\n"
            for i, action in enumerate(path):
                debug_text += f"Bước {i+1}: {action.upper()}\n"
        
        # Tạo định dạng đúng cho đường đi hiển thị trong ResultPanel
        # Path đã là danh sách các hành động, không cần xử lý thêm
        formatted_path = path
        
        # Lưu debug text vào file
        import os
        import datetime
        
        # Tạo thư mục debug nếu chưa tồn tại
        debug_dir = "debug_logs"
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
        
        # Tạo tên file với timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        debug_file = os.path.join(debug_dir, f"belief_search_debug_{timestamp}.txt")
        
        # Lưu nội dung vào file
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(debug_text)
        
        # Chuẩn bị đường dẫn tuyệt đối để hiển thị
        abs_path = os.path.abspath(debug_file)
        
        # Cập nhật ResultPanel và hiển thị thông báo
        self.belief_result_panel.update_path_display(initial_state_data, formatted_path)
        
        # Hiển thị summary text trong path_display
        summary_text = f"Đã lưu thông tin debug đầy đủ vào file:\n{abs_path}\n\n"
        summary_text += f"=== TÓM TẮT ===\n"
        if path:
            summary_text += f"Đã tìm thấy đường đi với {len(path)} bước.\n"
            summary_text += f"Số trạng thái niềm tin đã kiểm tra: {nodes}\n"
            summary_text += f"Kích thước hàng đợi tối đa: {fringe}\n\n"
        else:
            summary_text += f"Không tìm thấy giải pháp sau khi kiểm tra {nodes} trạng thái niềm tin.\n\n"
        
        summary_text += "Xem file debug để biết thông tin chi tiết về tất cả các trạng thái niềm tin."
        self.belief_result_panel.path_display.setText(summary_text)
        
        # Cập nhật thống kê
        if path:
            stats = f"Belief search hoàn thành với {len(path)} bước.\nSố trạng thái kiểm tra: {nodes}\nKích thước hàng đợi tối đa: {fringe}\n\nĐã lưu thông tin debug đầy đủ vào file:\n{debug_file}"
            self.update_status("Belief-based search hoàn thành thành công.", False)
        else:
            stats = f"Không tìm thấy giải pháp trong không gian niềm tin.\nSố trạng thái kiểm tra: {nodes}\nKích thước hàng đợi tối đa: {fringe}\n\nĐã lưu thông tin debug đầy đủ vào file:\n{debug_file}"
            self.update_status("Belief-based search không tìm được giải pháp.", False)
        
        self.belief_stats_label.setText(stats)
        
        # Hiển thị thông báo popup cho người dùng
        QMessageBox.information(self, "Debug Info", f"Đã lưu thông tin debug đầy đủ vào file:\n{abs_path}")

    def on_solver_error(self, error_msg):
        """Xử lý khi có lỗi trong thread giải"""
        QMessageBox.critical(self, "Solver Error", error_msg)
        self.update_status(f"Error during solving: {error_msg}", False)
        self.control_panel.set_stats_text("Solver error occurred.")

    def on_solver_finished(self):
        """Dọn dẹp UI sau khi thread giải kết thúc (thành công hoặc lỗi)"""
        self.control_panel.enable_solve_button(True) # Bật lại nút Solve
        self.progress_bar.setVisible(False) # Ẩn progress bar

    def on_belief_solver_finished(self):
        """Dọn dẹp UI sau khi thread giải belief search kết thúc"""
        self.belief_solve_btn.setEnabled(True)
        self.progress_bar.setVisible(False)

    def update_algorithm_description(self, algo_key):
        """Cập nhật mô tả thuật toán trong ResultPanel khi algo được chọn"""
        if algo_key:
            self.result_panel.update_algorithm_description(algo_key)


if __name__ == '__main__':
    # Bắt buộc dùng QApplication
    app = QApplication(sys.argv)
    window = PuzzleWindow()
    window.show()
    sys.exit(app.exec())
