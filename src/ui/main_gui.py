import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                           QVBoxLayout, QMessageBox, QProgressBar, QLabel)
from PyQt5.QtCore import Qt

# Import các thành phần GUI và logic từ các module khác
from src.core.buzzle_logic import Buzzle, generate_random_solvable_state, is_solvable
from .gui_components import (PuzzleBoard, SolutionNavigationPanel, ControlPanel,
                            ResultPanel, SolverThread)
# algorithm_manager không cần import trực tiếp vào đây vì ControlPanel/SolverThread đã dùng

class PuzzleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("8-Puzzle Solver")
        self.setGeometry(100, 100, 1200, 700) # Kích thước cửa sổ ban đầu

        # --- Widget chính và Layout chính ---
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget) # Chia ngang: Left (Boards+Results), Right (Controls)

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
        main_layout.addWidget(left_panel, stretch=7) # Panel trái chiếm nhiều hơn
        main_layout.addWidget(self.control_panel, stretch=3) # Panel phải ít hơn

        self.setCentralWidget(main_widget)

        # --- Status Bar ---
        self.status_label = QLabel("Ready")
        self.statusBar().addWidget(self.status_label)
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 0) # Indeterminate
        self.progress_bar.setFixedHeight(15)
        self.progress_bar.setVisible(False) # Ẩn ban đầu
        self.statusBar().addPermanentWidget(self.progress_bar)

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


    def update_status(self, message, show_progress=False):
        """Cập nhật status bar"""
        self.status_label.setText(message)
        self.progress_bar.setVisible(show_progress)

    def update_display(self):
        """Cập nhật hiển thị bảng Start và Goal"""
        self.start_board.update_board(self.start_state.data)
        self.goal_board.update_board(self.goal_state.data)
        # Khi cập nhật display, cũng nên reset navigator và result nếu chưa có solution
        # self.solution_navigator.reset_display() # Reset navigator về trạng thái chưa load
        # self.result_panel.clear_displays() # Xóa text path và description cũ
        # self.control_panel.set_stats_text("Ready.")

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

    def on_solver_error(self, error_msg):
        """Xử lý khi có lỗi trong thread giải"""
        QMessageBox.critical(self, "Solver Error", error_msg)
        self.update_status(f"Error during solving: {error_msg}", False)
        self.control_panel.set_stats_text("Solver error occurred.")

    def on_solver_finished(self):
        """Dọn dẹp UI sau khi thread giải kết thúc (thành công hoặc lỗi)"""
        self.control_panel.enable_solve_button(True) # Bật lại nút Solve
        self.progress_bar.setVisible(False) # Ẩn progress bar
        # Không xóa status message ở đây để người dùng còn đọc được

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
