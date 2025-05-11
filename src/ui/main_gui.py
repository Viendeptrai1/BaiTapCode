import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                           QVBoxLayout, QMessageBox, QProgressBar, QLabel,
                           QTabWidget, QPushButton, QGroupBox, QGridLayout,
                           QLineEdit, QTextEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import time
import traceback
import itertools
from PyQt5.QtGui import QFont

# Import các thành phần GUI và logic từ các module khác
from src.core.buzzle_logic import Buzzle, generate_random_solvable_state, is_solvable, parse_puzzle_input
from .gui_components import (PuzzleBoard, SolutionNavigationPanel, ControlPanel,
                            ResultPanel, SolverThread)
# Import the new algorithm
from src.algorithms.and_or_graph_search import NonDeterministicPuzzle, and_or_search, FAILURE, EMPTY_PLAN

class PuzzleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("8-Puzzle Solver")
        self.setGeometry(100, 100, 1200, 700)  # Wider to accommodate tabs
        
        # Create tab widget for different solving methods
        self.tab_widget = QTabWidget()
        
        # Create and add the informed search tab
        self.normal_tab = QWidget()
        self.init_normal_tab()
        self.tab_widget.addTab(self.normal_tab, "Standard Algorithms")

        # Create and add the uninformed search tab
        self.uninformed_search_tab = QWidget()
        self.init_uninformed_search_tab()
        self.tab_widget.addTab(self.uninformed_search_tab, "Tìm kiếm trong môi trường không xác định")
        
        # Set the tab widget as the central widget
        self.setCentralWidget(self.tab_widget)
        
        # Initialize puzzle state
        self.start_state = Buzzle()
        self.goal_state = Buzzle([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.default_state = self.start_state
        
        # Connect tab change signals
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # --- Status Bar ---
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setFixedHeight(15)
        self.progress_bar.setVisible(False)  # Ẩn ban đầu
        self.statusBar().addPermanentWidget(self.progress_bar)

    def on_tab_changed(self, index):
        """Handle tab change events"""
        # You can update tab-specific content here if needed
        current_tab_name = self.tab_widget.tabText(index)
        if current_tab_name == "Tìm kiếm trong môi trường không xác định":
            # Placeholder for actions specific to the new tab
            print("Switched to Uninformed Search Tab") 
            # You might want to initialize or refresh elements specific to this tab here
            pass
        pass

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

    def init_uninformed_search_tab(self):
        """Khởi tạo tab cho các thuật toán tìm kiếm trong môi trường không xác định."""
        # Main layout for this tab
        main_tab_layout = QHBoxLayout(self.uninformed_search_tab)

        # --- Left Panel: States and Controls ---
        left_panel_widget = QWidget()
        left_panel_layout = QVBoxLayout(left_panel_widget)

        # States Group (Initial and Goal Boards)
        states_group = QGroupBox("Puzzle States (2x2)")
        states_group_layout = QHBoxLayout()
        
        self.initial_state_board_uninformed = PuzzleBoard(title="Initial State", size=2)
        self.goal_state_board_uninformed = PuzzleBoard(title="Goal State", size=2)
        self.fixed_goal_state_2x2 = [[1, 2], [3, 0]]
        self.goal_state_board_uninformed.update_board(self.fixed_goal_state_2x2)
        self.goal_state_board_uninformed.setEnabled(False) # Goal state is fixed

        states_group_layout.addWidget(self.initial_state_board_uninformed)
        states_group_layout.addWidget(self.goal_state_board_uninformed)
        states_group.setLayout(states_group_layout)

        # Input and Controls Group
        controls_group = QGroupBox("Input and Controls")
        controls_layout = QGridLayout(controls_group) # Using QGridLayout for better alignment

        label_input = QLabel("Initial state (4 numbers, 0 for blank, e.g., 1 0 2 3):")
        self.initial_state_input_uninformed = QLineEdit()
        self.initial_state_input_uninformed.setPlaceholderText("e.g., 1 0 2 3")
        self.initial_state_input_uninformed.setText("0 1 2 3") # Default example
        self.load_button_uninformed = QPushButton("Load State")
        self.solve_button_uninformed = QPushButton("Solve (AND-OR Search)")
        self.reset_button_uninformed = QPushButton("Reset Input")

        controls_layout.addWidget(label_input, 0, 0, 1, 2) # Span 2 columns
        controls_layout.addWidget(self.initial_state_input_uninformed, 1, 0, 1, 2) # Span 2 columns
        controls_layout.addWidget(self.load_button_uninformed, 2, 0)
        controls_layout.addWidget(self.reset_button_uninformed, 2, 1)
        controls_layout.addWidget(self.solve_button_uninformed, 3, 0, 1, 2) # Span 2 columns
        
        # Add groups to left panel
        left_panel_layout.addWidget(states_group)
        left_panel_layout.addWidget(controls_group)
        left_panel_layout.addStretch() # Push controls to the top

        # --- Right Panel: Plan Display ---
        right_panel_widget = QWidget()
        right_panel_layout = QVBoxLayout(right_panel_widget)
        
        plan_display_group = QGroupBox("Conditional Plan")
        plan_display_layout = QVBoxLayout(plan_display_group)
        self.plan_display_area_uninformed = QTextEdit()
        self.plan_display_area_uninformed.setReadOnly(True)
        self.plan_display_area_uninformed.setFont(QFont("Courier New", 10))
        self.plan_display_area_uninformed.setPlaceholderText("Conditional plan will be displayed here.")
        plan_display_layout.addWidget(self.plan_display_area_uninformed)
        
        right_panel_layout.addWidget(plan_display_group)

        # Add panels to the main tab layout
        main_tab_layout.addWidget(left_panel_widget, stretch=1)
        main_tab_layout.addWidget(right_panel_widget, stretch=2) # Plan display gets more space

        self.uninformed_search_tab.setLayout(main_tab_layout)

        # --- Connect signals for this tab ---
        self.load_button_uninformed.clicked.connect(self.load_state_uninformed)
        self.solve_button_uninformed.clicked.connect(self.solve_uninformed)
        self.reset_button_uninformed.clicked.connect(self.reset_input_uninformed)

        self.load_state_uninformed() # Load initial default state for the 2x2 board

    def _parse_2x2_input(self, input_text):
        """Parses a 4-number string into a 2x2 list of lists."""
        try:
            numbers = [int(x) for x in input_text.split()]
            if len(numbers) != 4:
                raise ValueError("Input must contain exactly 4 numbers.")
            if set(numbers) != set(range(4)):
                raise ValueError("Input must contain numbers 0, 1, 2, 3 exactly once.")
            return [numbers[0:2], numbers[2:4]]
        except ValueError as e:
            QMessageBox.warning(self, "Input Error", str(e))
            return None

    def load_state_uninformed(self):
        """Loads the initial state from input for the uninformed search tab."""
        input_text = self.initial_state_input_uninformed.text()
        parsed_matrix = self._parse_2x2_input(input_text)
        if parsed_matrix:
            self.initial_state_board_uninformed.update_board(parsed_matrix)
            self.plan_display_area_uninformed.setText("State loaded. Click Solve to find a plan.")
        else:
            self.initial_state_board_uninformed.update_board([[0,0],[0,0]]) # Clear board on error
            self.plan_display_area_uninformed.setText("Invalid input. Please enter 4 unique numbers (0-3).")

    def log_to_plan_display(self, message):
        """Appends a message to the plan display area in the uninformed search tab."""
        self.plan_display_area_uninformed.append(message)
        QApplication.processEvents() # Ensure the UI updates with each message

    def reset_input_uninformed(self):
        """Resets the input field and clears displays for the uninformed search tab."""
        self.initial_state_input_uninformed.setText("0 1 2 3")
        self.initial_state_board_uninformed.update_board([[0,1],[2,3]])
        self.plan_display_area_uninformed.clear()
        self.plan_display_area_uninformed.setPlaceholderText("Conditional plan will be displayed here.")

    def _format_plan_for_display(self, plan, current_state_matrix, indent_level=0):
        """Recursively formats the conditional plan for display in QTextEdit."""
        indent = "  " * indent_level
        if plan == EMPTY_PLAN:
            return indent + "<ĐÃ ĐẠT ĐÍCH (Kế hoạch rỗng)>\n"
        if plan == FAILURE:
            return indent + "<THẤT BẠI TRONG KẾ HOẠCH CON>\n"
        if not isinstance(plan, list) or len(plan) != 2:
            return indent + f"<CẤU TRÚC KẾ HOẠCH KHÔNG HỢP LỆ: {plan}>\n"

        action_coord = plan[0] # (row, col) of tile intended to move
        outcomes_map = plan[1]

        # Chuyển đổi tọa độ hành động thành hướng di chuyển
        current_state_tuple = tuple(map(tuple, current_state_matrix))
        direction = self._get_direction_from_action(action_coord, current_state_matrix)
        
        tile_value = "?"
        # Check conditions for safely accessing tile_value
        if current_state_matrix:
            if 0 <= action_coord[0] < len(current_state_matrix) and \
               0 <= action_coord[1] < len(current_state_matrix[0]):
                tile_value = current_state_matrix[action_coord[0]][action_coord[1]]
        
        plan_str = indent + f"NẾU Thực hiện hành động (di chuyển ô {tile_value} {direction}):\n"
        
        for outcome_state_tuple, sub_plan in outcomes_map.items():
            # Convert outcome_state_tuple (tuple of tuples) to list of lists for display
            outcome_state_list_of_lists = [list(row) for row in outcome_state_tuple]
            plan_str += indent + "  " + f"NẾU Kết quả là {outcome_state_list_of_lists}:\n"
            # The sub-plan starts from this outcome_state
            plan_str += self._format_plan_for_display(sub_plan, outcome_state_list_of_lists, indent_level + 2)
        return plan_str
        
    def _get_direction_from_action(self, action_pos, current_state_matrix):
        """Xác định hướng di chuyển dựa trên hành động và trạng thái hiện tại."""
        # Tìm vị trí ô trống
        blank_pos = None
        for r in range(len(current_state_matrix)):
            for c in range(len(current_state_matrix[r])):
                if current_state_matrix[r][c] == 0:
                    blank_pos = (r, c)
                    break
            if blank_pos:
                break
                
        if not blank_pos:
            return "(không xác định)"
            
        tr, tc = action_pos  # Ô được di chuyển
        br, bc = blank_pos   # Ô trống
        
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
        
        return "(không xác định)"

    def solve_uninformed(self):
        """Handles the solving process for the AND-OR search."""
        input_text = self.initial_state_input_uninformed.text()
        initial_matrix = self._parse_2x2_input(input_text)

        if not initial_matrix:
            self.plan_display_area_uninformed.setText("Không thể giải: Trạng thái ban đầu không hợp lệ.")
            return

        self.initial_state_board_uninformed.update_board(initial_matrix)
        self.plan_display_area_uninformed.setText("Đang giải với tìm kiếm AND-OR...")
        QApplication.processEvents() # Update UI before long computation

        try:
            problem = NonDeterministicPuzzle(initial_matrix=initial_matrix, 
                                           goal_matrix=self.fixed_goal_state_2x2,
                                           size=2)
            
            # For AND-OR search, we typically don't run it in a separate thread 
            # in this simple example unless it becomes very slow. 
            # If it can be long, a thread like SolverThread would be needed.
            solution_plan = and_or_search(problem, log_func=self.log_to_plan_display, p_slip=0.1)

            if solution_plan == FAILURE:
                self.log_to_plan_display("Không tìm thấy giải pháp bằng tìm kiếm AND-OR.")
            elif solution_plan == EMPTY_PLAN:
                self.log_to_plan_display("Trạng thái ban đầu đã là trạng thái đích.")
            else:
                formatted_plan = self._format_plan_for_display(solution_plan, initial_matrix)
                self.log_to_plan_display("\n--- Kế Hoạch Có Điều Kiện Cuối Cùng ---")
                self.log_to_plan_display(formatted_plan)
        
        except ValueError as ve:
            QMessageBox.critical(self, "Lỗi Thiết Lập Puzzle", str(ve))
            self.plan_display_area_uninformed.setText(f"Lỗi: {str(ve)}")
        except Exception as e:
            import traceback
            QMessageBox.critical(self, "Lỗi Giải Thuật", f"Đã xảy ra lỗi không mong muốn: {str(e)}")
            self.plan_display_area_uninformed.setText(f"Lỗi: {str(e)}\n{traceback.format_exc()}")

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

    def start_solving(self, algorithm_key, heuristic_key=None):
        """Bắt đầu quá trình giải bằng thuật toán được chọn"""
        if not self.start_state or not hasattr(self.start_state, 'data'):
            QMessageBox.warning(self, "Invalid State", "The start state is not valid.")
            return
            
        self.current_solution_path = [] # Xóa solution cũ
        self.solution_navigator.reset_display() # Reset navigator
        self.result_panel.update_path_display(self.start_state.data, []) # Xóa text path cũ

        # Validate that algorithm exists
        if algorithm_key not in self.control_panel.algo_select_panel.algorithm_radio_buttons:
            QMessageBox.warning(self, "Algorithm Error", f"Unknown algorithm: {algorithm_key}")
            return
            
        algo_name = self.control_panel.algo_select_panel.algorithm_radio_buttons.get(algorithm_key).text()
        
        # Show heuristic in status if used
        if heuristic_key:
            heuristic_name = self.control_panel.local_search_config_panel.HEURISTICS_MAP.get(heuristic_key, "Unknown")
            self.update_status(f"Solving with {algo_name} using {heuristic_name}...", True)
        else:
            self.update_status(f"Solving with {algo_name}...", True)
            
        self.control_panel.enable_solve_button(False) # Tắt nút Solve

        # Chạy thuật toán trong thread riêng
        # Truyền Buzzle object vào thread
        self.solver_thread = SolverThread(algorithm_key, self.start_state, heuristic_key)
        self.solver_thread.solution_ready.connect(self.on_solution_ready)
        self.solver_thread.error_occurred.connect(self.on_solver_error)
        self.solver_thread.finished.connect(self.on_solver_finished)
        self.solver_thread.start()

    def on_solution_ready(self, path, nodes, fringe_or_pop):
        """Xử lý khi thread giải xong và có kết quả"""
        self.current_solution_path = path
        # Cập nhật Solution Navigator
        self.solution_navigator.set_solution(self.start_state.data, path)
        # Cập nhật Result Panel (Text Path)
        self.result_panel.update_path_display(self.start_state.data, path)
        # Cập nhật thống kê trên Control Panel
        algo_key = self.control_panel.algo_select_panel.get_selected_algorithm()
        
        # Get the heuristic used (if any)
        heuristic_key = None
        if self.control_panel.local_search_config_panel.isVisible():
            heuristic_key = self.control_panel.local_search_config_panel.get_selected_heuristic()
            
        if path:
            stats = f"Solved in {len(path)} steps.\nNodes evaluated/expanded: {nodes}\nMax fringe/population size: {fringe_or_pop}"
            self.update_status(f"Solution found ({len(path)} steps).", False)
        elif algo_key.lower() in ["genetic_algorithm", "simulated_annealing", "hill_climbing", "random_restart_hc"]:
            # Các thuật toán local search này có thể không tìm thấy goal
            final_state = self.solution_navigator.current_step_board.tiles
            heuristic_info = ""
            if heuristic_key:
                heuristic_name = self.control_panel.local_search_config_panel.HEURISTICS_MAP.get(heuristic_key, "Unknown")
                heuristic_info = f" using {heuristic_name}"
                
            stats = f"{algo_key}{heuristic_info} finished.\nGoal state reached: {Buzzle(final_state).is_goal() if self.solution_navigator.current_step_index > -1 else 'N/A'}\nNodes evaluated: {nodes}\nMax neighbors/population: {fringe_or_pop}"
            self.update_status(f"{algo_key.upper()} finished. Goal not guaranteed.", False)
        else:
            # Các thuật toán tìm kiếm khác không tìm thấy đường đi
            stats = f"No solution found.\nNodes expanded: {nodes}\nMax fringe size: {fringe_or_pop}"
            self.update_status("No solution found.", False)
        self.control_panel.set_stats_text(stats)

    def on_solver_error(self, error_msg):
        """Xử lý khi có lỗi trong thread giải"""
        QMessageBox.critical(self, "Solver Error", error_msg)
        self.update_status(f"Error during solving: {error_msg}", False)
        self.control_panel.set_stats_text("Solver error occurred.")

    def on_solver_finished(self):
        """Dọn dẹp UI sau khi thread giải kết thúc (thành công hoặc lỗi)"""
        self.control_panel.enable_solve_button(True) # Bật lại nút Solve
        self.progress_bar.setVisible(False) # Ẩn progress bar

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
