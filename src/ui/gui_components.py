from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QLineEdit, QTextEdit,
                           QSplitter, QProgressBar, QGroupBox, QRadioButton,
                           QButtonGroup, QMessageBox, QSizePolicy)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont
import random # Cần cho random generation trong panel (nếu có)

# Import các thành phần logic và quản lý thuật toán
from src.core.buzzle_logic import Buzzle, generate_random_solvable_state, is_solvable
from src.algorithms.algorithm_manager import get_algorithm_groups, solve_puzzle
from src.algorithms.local_search_algorithms import manhattan_distance, number_of_misplaced_tiles # Fixed import path

# --- Solver Thread ---
class SolverThread(QThread):
    """Thread riêng cho việc giải puzzle để không block UI"""
    solution_ready = pyqtSignal(list, int, int) # path, nodes, fringe/pop_size
    error_occurred = pyqtSignal(str)

    def __init__(self, algorithm_key, start_state, heuristic_key=None): # Added heuristic_key
        super().__init__()
        self.algorithm_key = algorithm_key
        self.start_state = start_state # Nhận Buzzle object
        self.heuristic_key = heuristic_key # Store heuristic_key

    def run(self):
        try:
            # Gọi hàm solve_puzzle từ algorithm_manager
            result, nodes, fringe_or_pop = solve_puzzle(
                self.algorithm_key, 
                self.start_state,
                heuristic_name=self.heuristic_key # Pass heuristic_key
            )
            
            # For local search algorithms, result might be a state instead of a path
            # Convert to a path format for uniform handling
            if result is None:
                # No solution found, use empty path
                path = []
            elif not isinstance(result, list):
                # Create a path with a single step showing the final state
                path = [("final", result)]
            else:
                path = result
                
            self.solution_ready.emit(path, nodes, fringe_or_pop)
        except Exception as e:
            import traceback
            print(f"Error in SolverThread: {e}")
            traceback.print_exc() # In traceback để debug
            self.error_occurred.emit(f"Lỗi trong quá trình giải: {e}")


# --- Puzzle Board Widget ---
class PuzzleBoard(QWidget):
    """Một bảng puzzle đơn lẻ để hiển thị trạng thái"""
    def __init__(self, title="Puzzle", size=3):
        super().__init__()
        self.size = size # Store the size
        layout = QVBoxLayout()
        layout.setSpacing(2) # Giảm khoảng cách
        layout.setContentsMargins(5, 5, 5, 5) # Giảm margins

        # Title (Optional, có thể set bởi parent)
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        # self.title_label.setFont(QFont('Arial', 10)) # Font nhỏ hơn
        layout.addWidget(self.title_label)

        # Container cho grid puzzle với border
        puzzle_container = QWidget()
        puzzle_container.setStyleSheet("""
            QWidget {
                background-color: darkgrey; /* Nền tối hơn - Sửa lỗi CSS */
                border: 1px solid #666;
                border-radius: 3px;
            }
        """)
        container_layout = QVBoxLayout()
        container_layout.setSpacing(0) # Không cách giữa border và grid
        container_layout.setContentsMargins(1, 1, 1, 1) # Border nhỏ

        # Grid cho các ô puzzle
        grid = QGridLayout()
        grid.setSpacing(1) # Khoảng cách giữa các ô
        self.tiles = []

        for i in range(self.size):
            row = []
            for j in range(self.size):
                btn = QPushButton()
                # Adjust button size based on grid size if necessary, for now keep fixed
                # A more dynamic approach might be needed for very different sizes
                if self.size == 2:
                    btn.setFixedSize(80, 80) # Larger for 2x2
                    btn.setFont(QFont('Arial', 24, QFont.Bold)) # Larger font for 2x2
                else: # Default to 3x3 sizes
                    btn.setFixedSize(60, 60) # Kích thước nhỏ hơn
                    btn.setFont(QFont('Arial', 18, QFont.Bold)) # Font nhỏ hơn
                
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e8e8e8; /* Màu nền ô */
                        color: #333; /* Màu chữ */
                        border: 1px solid #bbb;
                        border-radius: 2px; /* Bo góc nhẹ */
                        padding: 0px;
                    }
                    QPushButton[text=""] { /* Kiểu cho ô trống */
                        background-color: #555; /* Màu ô trống */
                        border: 1px solid #444;
                    }
                    /*QPushButton:hover {
                        background-color: #d8d8d8;
                    }*/
                """)
                # btn.setDisabled(True) # Không cho click vào ô
                grid.addWidget(btn, i, j)
                row.append(btn)
            self.tiles.append(row)

        container_layout.addLayout(grid)
        puzzle_container.setLayout(container_layout)
        layout.addWidget(puzzle_container)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) # Đặt kích thước cố định

    def update_board(self, state_data):
        """Cập nhật hiển thị bảng với state_data (list of lists)"""
        if not state_data or len(state_data) != self.size or \
           not all(len(row) == self.size for row in state_data):
             # Xóa bảng nếu dữ liệu không hợp lệ
             for i in range(self.size):
                 for j in range(self.size):
                     self.tiles[i][j].setText("")
                     self.tiles[i][j].setProperty("value", 0) # Để style ô trống
                     self.tiles[i][j].setStyleSheet(self.tiles[i][j].styleSheet()) # Cập nhật style
             return

        for i in range(self.size):
            for j in range(self.size):
                value = state_data[i][j]
                self.tiles[i][j].setText(str(value) if value != 0 else "")
                # Cập nhật property để CSS selector hoạt động
                self.tiles[i][j].setProperty("value", value)
                # Re-apply stylesheet để cập nhật style dựa trên property mới
                self.tiles[i][j].setStyleSheet(self.tiles[i][j].styleSheet())

    def set_title(self, title):
        self.title_label.setText(title)


# --- Solution Navigator Widget ---
class SolutionNavigationPanel(QWidget):
    """Panel hiển thị từng bước của lời giải với nút điều hướng"""
    solution_step_changed = pyqtSignal(list) # Gửi state_data của bước hiện tại

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(5)

        # Title
        title_label = QLabel("Solution Navigator")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 11, QFont.Bold))

        # Puzzle display cho bước hiện tại
        self.current_step_board = PuzzleBoard("Current Step")

        # Step info
        self.step_info = QLabel("Step 0 / 0")
        self.step_info.setAlignment(Qt.AlignCenter)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("<< Previous")
        self.next_btn = QPushButton("Next >>")
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.prev_btn.setFixedWidth(100)
        self.next_btn.setFixedWidth(100)

        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()

        # Move description
        self.move_desc = QLabel("Load a solution to navigate")
        self.move_desc.setAlignment(Qt.AlignCenter)

        # Add all to main layout
        layout.addWidget(title_label)
        layout.addWidget(self.current_step_board)
        layout.addWidget(self.step_info)
        layout.addLayout(nav_layout)
        layout.addWidget(self.move_desc)
        layout.addStretch()

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) # Đặt kích thước cố định

        # Solution data
        self.solution_path = [] # List of (move, state_data)
        self.initial_state_data = None # Lưu trạng thái ban đầu để hiển thị step 0
        self.current_step_index = -1 # -1: chưa load, 0: initial, 1+: các bước

        # Connect signals
        self.prev_btn.clicked.connect(self.go_to_previous_step)
        self.next_btn.clicked.connect(self.go_to_next_step)

    def set_solution(self, initial_state_data, solution_path):
        """
        Set solution path và reset về trạng thái ban đầu.
        Input:
            initial_state_data: Trạng thái bắt đầu (list of lists).
            solution_path: List các (move, next_state_data).
        """
        self.initial_state_data = initial_state_data
        self.solution_path = solution_path if solution_path else []
        self.current_step_index = 0 # Bắt đầu từ trạng thái ban đầu
        self.update_display()
        self.update_navigation_state()
        # Gửi tín hiệu về trạng thái ban đầu
        if self.initial_state_data:
            self.solution_step_changed.emit(self.initial_state_data)

    def update_navigation_state(self):
        """Update button states and step info based on current position"""
        total_steps = len(self.solution_path) # Số bước di chuyển
        has_solution = self.initial_state_data is not None

        self.prev_btn.setEnabled(has_solution and self.current_step_index > 0)
        self.next_btn.setEnabled(has_solution and self.current_step_index < total_steps)

        if has_solution:
            self.step_info.setText(f"Step {self.current_step_index} / {total_steps}")
        else:
            self.step_info.setText("Step 0 / 0")

    def update_display(self):
        """Display the current step board and move description"""
        if self.current_step_index == -1 or self.initial_state_data is None:
            # Trạng thái chưa load hoặc không hợp lệ
            self.current_step_board.update_board([[0]*self.size]*self.size) # Bảng trống
            self.move_desc.setText("Load a solution to navigate")
            return

        current_state_data = None
        move_text = ""

        if self.current_step_index == 0:
            # Hiển thị trạng thái ban đầu
            current_state_data = self.initial_state_data
            move_text = "Initial State"
        elif 0 < self.current_step_index <= len(self.solution_path):
            # Hiển thị bước từ 1 trở đi
            move, state_data = self.solution_path[self.current_step_index - 1]
            
            # Verify state_data is valid
            if state_data is None:
                print(f"Warning: None state data at step {self.current_step_index}")
                current_state_data = self.initial_state_data  # Fallback to initial state
            else:
                current_state_data = state_data
                
            move_text = f"Move: {move.capitalize() if move is not None else 'None'}"
        else:
             # Index không hợp lệ (nên không xảy ra)
             print(f"Error: Invalid step index {self.current_step_index}")
             return

        self.current_step_board.update_board(current_state_data)
        self.move_desc.setText(move_text)
        # Gửi tín hiệu trạng thái hiện tại đã thay đổi
        self.solution_step_changed.emit(current_state_data)

    def go_to_next_step(self):
        """Go to next step in solution"""
        if self.initial_state_data and self.current_step_index < len(self.solution_path):
            self.current_step_index += 1
            self.update_display()
            self.update_navigation_state()

    def go_to_previous_step(self):
        """Go to previous step in solution"""
        if self.initial_state_data and self.current_step_index > 0:
            self.current_step_index -= 1
            self.update_display()
            self.update_navigation_state()

    def reset_display(self):
        """Reset the display when no solution is loaded or states are reset"""
        self.solution_path = []
        self.initial_state_data = None
        self.current_step_index = -1
        self.update_display()
        self.update_navigation_state()
        self.move_desc.setText("Load a solution to navigate")
        self.step_info.setText("Step 0 / 0")


# --- Control Panel Widget ---
class ControlPanel(QWidget):
    # Signals gửi đi khi nút được nhấn
    load_clicked = pyqtSignal(str) # Gửi nội dung input
    reset_clicked = pyqtSignal()
    solve_clicked = pyqtSignal(str, str) # Gửi key thuật toán và key heuristic (nếu có)
    random_start_clicked = pyqtSignal()

    # Heuristics for local search (not directly used in ControlPanel, but good for reference)
    # Actual map is in LocalSearchConfigPanel
    # HEURISTICS = {
    #     "manhattan": ("Manhattan Distance", manhattan_distance),
    #     "misplaced": ("Misplaced Tiles", number_of_misplaced_tiles),
    # }

    def __init__(self):
        super().__init__()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setAlignment(Qt.AlignTop)

        # Input cho trạng thái bắt đầu
        start_state_group = QGroupBox("Initial State")
        start_state_layout = QVBoxLayout()
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("e.g., 1 2 3 4 0 5 6 7 8")
        self.load_btn = QPushButton("Load State from Input")
        self.load_btn.clicked.connect(self._on_load_clicked)
        self.random_start_btn = QPushButton("Generate Random Start State")
        self.random_start_btn.clicked.connect(self._on_random_start_clicked)
        self.reset_btn = QPushButton("Reset to Default State")
        self.reset_btn.clicked.connect(self._on_reset_clicked)

        start_state_layout.addWidget(self.start_input)
        start_state_layout.addWidget(self.load_btn)
        start_state_layout.addWidget(self.random_start_btn)
        start_state_layout.addWidget(self.reset_btn)
        start_state_group.setLayout(start_state_layout)
        main_layout.addWidget(start_state_group)

        # Panel chọn thuật toán
        self.algo_select_panel = AlgorithmSelectionPanel()
        main_layout.addWidget(self.algo_select_panel)

        # Panel chọn heuristic cho Local Search (mới)
        self.local_search_config_panel = LocalSearchConfigPanel()
        main_layout.addWidget(self.local_search_config_panel) # Added to main_layout
        self.local_search_config_panel.setVisible(False) # Ẩn ban đầu

        # Kết nối signal từ AlgorithmSelectionPanel để ẩn/hiện LocalSearchConfigPanel
        self.algo_select_panel.algorithm_changed.connect(self._update_local_search_panel_visibility)

        # Nút giải
        self.solve_btn = QPushButton("Solve Puzzle")
        self.solve_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; }")
        self.solve_btn.clicked.connect(self._on_solve_clicked)
        main_layout.addWidget(self.solve_btn)

        # Text area cho thống kê (số bước, thời gian, etc.)
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()
        self.stats_display = QTextEdit() # Changed from stats_label
        self.stats_display.setReadOnly(True)
        self.stats_display.setMinimumHeight(80)
        stats_layout.addWidget(self.stats_display)
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)

        main_layout.addStretch() # Đẩy các widget lên trên
        self.setLayout(main_layout)
        self.set_stats_text("Select an algorithm and initial state.")


    def _on_load_clicked(self):
        self.load_clicked.emit(self.start_input.text())

    def _on_reset_clicked(self):
        self.start_input.clear()
        self.set_stats_text("States reset. Select an algorithm.")
        self.reset_clicked.emit()
        # Cập nhật lại visibility của local search panel nếu thuật toán đang chọn là local search
        self._update_local_search_panel_visibility(self.algo_select_panel.get_selected_algorithm())


    def _on_solve_clicked(self):
        selected_algo_key = self.algo_select_panel.get_selected_algorithm()
        if selected_algo_key:
            heuristic_key = None
            if self.local_search_config_panel.isVisible(): # Check visibility
                heuristic_key = self.local_search_config_panel.get_selected_heuristic()
            self.solve_clicked.emit(selected_algo_key, heuristic_key) # Emit both keys
            self.set_stats_text(f"Solving with {selected_algo_key.upper()}...") # Use self.set_stats_text
        else:
            QMessageBox.warning(self, "Algorithm Not Selected", "Please select a solving algorithm.")


    def _on_random_start_clicked(self):
        self.random_start_clicked.emit()
        # Cập nhật lại visibility của local search panel
        self._update_local_search_panel_visibility(self.algo_select_panel.get_selected_algorithm())


    def set_start_input_text(self, text):
        self.start_input.setText(text)

    def set_stats_text(self, text):
        self.stats_display.setText(text) # Use stats_display

    def enable_solve_button(self, enable=True):
        self.solve_btn.setEnabled(enable)

    def _update_local_search_panel_visibility(self, algo_key):
        """Hiển thị hoặc ẩn LocalSearchConfigPanel dựa trên thuật toán được chọn."""
        # Danh sách các thuật toán tìm kiếm cục bộ (cần cập nhật nếu key thay đổi)
        # These should match the keys used in algorithm_manager.py
        LOCAL_SEARCH_ALGORITHMS = [
            "hill_climbing", 
            "random_restart_hc",  # Updated to match key in algorithm_manager.py
            "simulated_annealing", 
            "genetic_algorithm"
        ]
        if algo_key in LOCAL_SEARCH_ALGORITHMS:
            self.local_search_config_panel.setVisible(True)
        else:
            self.local_search_config_panel.setVisible(False)


# --- Algorithm Selection Panel ---
class AlgorithmSelectionPanel(QGroupBox):
    """Panel chọn thuật toán theo nhóm"""
    algorithm_changed = pyqtSignal(str) # Gửi key của algo mới được chọn

    def __init__(self):
        super().__init__("Select Algorithm")
        self.algorithm_radio_buttons = {} # Store radio buttons for later access if needed
        self.button_group = QButtonGroup(self)
        
        main_layout = QVBoxLayout() # Layout chính cho group box
        
        algorithm_groups = get_algorithm_groups() # Lấy các nhóm từ manager
        
        first_button = None # Để chọn thuật toán đầu tiên làm mặc định

        for group_name, algorithms in algorithm_groups.items():
            if not algorithms: continue # Bỏ qua nhóm trống

            group_box_for_radio = QGroupBox(group_name) # Tạo group box nhỏ hơn cho radio buttons của nhóm
            group_layout = QVBoxLayout()

            for algo_key, algo_name in algorithms.items():
                # algo_name is now a string, not a dictionary with a "name" key
                radio_button = QRadioButton(algo_name)
                radio_button.setProperty("algo_key", algo_key)
                self.button_group.addButton(radio_button)
                group_layout.addWidget(radio_button)
                self.algorithm_radio_buttons[algo_key] = radio_button
                if first_button is None:
                    radio_button.setChecked(True)
                    first_button = radio_button
            
            group_box_for_radio.setLayout(group_layout)
            main_layout.addWidget(group_box_for_radio)

        self.button_group.buttonClicked.connect(self._on_algorithm_selected)
        self.setLayout(main_layout)
        
        # Emit signal cho thuật toán được chọn ban đầu
        if first_button:
            self._on_algorithm_selected(first_button)

    def _on_algorithm_selected(self, button):
        self.algorithm_changed.emit(button.property("algo_key"))

    def get_selected_algorithm(self):
        # Corrected: Method was altered in previous diff
        return self.button_group.checkedButton().property("algo_key") if self.button_group.checkedButton() else None


# --- Local Search Heuristic Selection Panel (Mới) ---
class LocalSearchConfigPanel(QGroupBox):
    """Panel chọn heuristic cho các thuật toán Local Search."""
    heuristic_changed = pyqtSignal(str) # Gửi key của heuristic mới

    HEURISTICS_MAP = {
        "manhattan": "Manhattan Distance",
        "misplaced": "Misplaced Tiles"
    }

    def __init__(self):
        super().__init__("Local Search Options")
        self.button_group = QButtonGroup(self)
        layout = QVBoxLayout()

        first_button = None
        for key, name in self.HEURISTICS_MAP.items():
            radio_button = QRadioButton(name)
            radio_button.setProperty("heuristic_key", key)
            self.button_group.addButton(radio_button)
            layout.addWidget(radio_button)
            if first_button is None: # Chọn heuristic đầu tiên làm mặc định
                radio_button.setChecked(True)
                first_button = radio_button
        
        self.button_group.buttonClicked.connect(self._on_heuristic_selected)
        self.setLayout(layout)
        
        # Emit signal cho heuristic được chọn ban đầu
        if first_button:
           self._on_heuristic_selected(first_button)


    def _on_heuristic_selected(self, button):
        self.heuristic_changed.emit(button.property("heuristic_key"))

    def get_selected_heuristic(self):
        return self.button_group.checkedButton().property("heuristic_key") if self.button_group.checkedButton() else None


# --- Result Panel Widget ---
class ResultPanel(QWidget):
    """Panel hiển thị kết quả (đường đi text) và mô tả thuật toán"""
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()

        # Tạo splitter để chia đôi panel
        splitter = QSplitter(Qt.Horizontal)

        # Group Box cho Path Display
        path_group = QGroupBox("Solution Path (Text)")
        path_layout = QVBoxLayout()
        self.path_display = QTextEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setFont(QFont('Consolas', 9)) # Font monospace
        path_layout.addWidget(self.path_display)
        path_group.setLayout(path_layout)

        # Group Box cho Algorithm Description
        desc_group = QGroupBox("Algorithm Description")
        desc_layout = QVBoxLayout()
        self.algo_desc = QTextEdit()
        self.algo_desc.setReadOnly(True)
        self.algo_desc.setFont(QFont('Arial', 9))
        desc_layout.addWidget(self.algo_desc)
        desc_group.setLayout(desc_layout)

        splitter.addWidget(path_group)
        splitter.addWidget(desc_group)
        splitter.setSizes([350, 250]) # Điều chỉnh tỉ lệ

        layout.addWidget(splitter)
        self.setLayout(layout)

        # Predefined descriptions
        self.descriptions = {
            "bfs": "Breadth-First Search (BFS):\n- Explores level by level.\n- Guarantees the shortest path (in terms of number of moves).\n- Can be memory-intensive for large state spaces.",
            "dfs": "Depth-First Search (DFS):\n- Explores as deeply as possible along each branch before backtracking.\n- Memory efficient.\n- Does not guarantee the shortest path. Often needs a depth limit.",
            "ucs": "Uniform Cost Search (UCS):\n- Explores nodes based on the lowest path cost (g-value) from the start.\n- Guarantees the cheapest path if step costs are non-negative (here, cost=1 per move, so similar to BFS).\n- Can be memory-intensive.",
            "astar": "A* Search:\n- Combines path cost (g) and heuristic estimate (h) (f = g + h).\n- Uses Manhattan distance as the heuristic.\n- Guarantees the shortest path if the heuristic is admissible (never overestimates the cost) and consistent.\n- Generally more efficient than BFS/UCS.",
            "greedy": "Greedy Best-First Search:\n- Expands the node that appears closest to the goal based solely on the heuristic (h-value).\n- Fast but does not guarantee optimality or completeness.\n- Can get stuck in loops or take suboptimal paths.",
            "ids": "Iterative Deepening Search (IDS):\n- Performs DFS with increasing depth limits (0, 1, 2,...).\n- Combines the completeness and optimality of BFS with the memory efficiency of DFS.\n- Can be slower due to re-expanding nodes at shallower depths.",
            "idastar": "Iterative Deepening A* (IDA*):\n- Uses A*'s f-value (g + h) as a cutoff bound that increases iteratively.\n- More memory-efficient than A* for large problems.\n- Guarantees optimality with an admissible heuristic.",
            "hill_climbing": "Hill Climbing:\n- Local search algorithm that always moves to the neighbor state with the best heuristic value.\n- Very fast but easily gets stuck in local minima.\n- Can use either Manhattan distance or Misplaced Tiles as heuristic.\n- Does not guarantee an optimal solution.",
            "random_restart_hc": "Random-Restart Hill Climbing:\n- Runs hill climbing multiple times from different random starting points.\n- Helps overcome the local minima problem of basic hill climbing.\n- More likely to find a good solution, though still not guaranteed to be optimal.\n- Can use either Manhattan distance or Misplaced Tiles as heuristic.",
            "simulated_annealing": "Simulated Annealing:\n- Probabilistic local search algorithm inspired by annealing in metallurgy.\n- Allows moves to worse states with a probability that decreases over time (as 'temperature' cools).\n- Helps escape local minima.\n- Can use either Manhattan distance or Misplaced Tiles as heuristic.\n- Does not guarantee optimality but often finds good solutions.",
            "genetic_algorithm": "Genetic Algorithm:\n- Evolutionary algorithm that maintains a population of candidate solutions.\n- Uses selection, crossover, and mutation operators to evolve the population.\n- Selection favors states with better heuristic values.\n- Well-suited for large search spaces.\n- Can use either Manhattan distance or Misplaced Tiles as heuristic.\n- Finds good solutions but not necessarily the optimal path.",
            "belief_bfs": "Belief State BFS (POMDP):\n- Mô hình POMDP (Partially Observable Markov Decision Process).\n- BAN ĐẦU: Chỉ biết 6 ô đầu (hàng 1 và hàng 2), không biết 3 ô cuối (hàng 3).\n- TÌM KIẾM: Duy trì một tập hợp các trạng thái có thể (belief state).\n- QUAN SÁT: Sau mỗi hành động, chỉ quan sát được 6 ô đầu, không biết trạng thái thực tế đầy đủ.\n- NIỀM TIN: Cập nhật tập trạng thái có thể dựa trên hành động và quan sát mới.\n- MỤC TIÊU: Thu hẹp niềm tin xuống còn một trạng thái duy nhất (trạng thái đích).",
            "belief_state_search": (
                "Belief State Search:\n\n"
                "- Used in partially observable environments where the agent cannot see the complete state.\n"
                "- Maintains a 'belief state' - a set of all possible states consistent with observations.\n"
                "- Observation modes:\n"
                "  * Partial: Only the first 6 cells (top 2 rows) are visible\n"
                "  * Blind: No cells are visible\n"
                "  * Custom: User-defined visibility mask\n\n"
                "- Search process:\n"
                "  1. Initialize with all possible states consistent with initial observation\n"
                "  2. For each action:\n"
                "     a. Apply the action to each possible state\n"
                "     b. Make a new observation\n"
                "     c. Filter states that would not produce this observation\n"
                "  3. Goal: Reduce belief state to only the goal state\n\n"
                "- Applications: Robotics, sensor networks, any domain with limited sensing"
            )
        }

    def update_path_display(self, initial_state_data, path):
        """Cập nhật hiển thị đường đi text."""
        if not initial_state_data:
             self.path_display.setText("No initial state loaded.")
             return

        # Special handling for backtracking search
        if hasattr(self, 'is_backtracking') and self.is_backtracking:
            node_count = len(path) if path else 0
            text = "Backtracking Search Process:\n\n"
            text += f"Total nodes explored: {node_count}\n\n"
            text += "Initial State:\n"
            for row in initial_state_data:
                text += f"  {row}\n"
            text += "-" * 30 + "\n\n"
            
            # Show the backtracking process with variable assignments and backtracks
            if path:
                # Display a representation of the search tree/process
                text += "Search Process:\n"
                current_depth = 0
                assignment_history = []
                
                for i, (move, state) in enumerate(path):
                    # We'll simulate the backtracking process based on the moves
                    if move == "assignment":  # Variable assignment
                        current_depth += 1
                        indent = "  " * current_depth
                        var_name = f"var{current_depth}" if state else "?"
                        val = f"val{current_depth}" if state else "?"
                        text += f"{indent}Assign {var_name} = {val}\n"
                        assignment_history.append((var_name, val))
                        
                    elif move == "backtrack":  # Backtracking step
                        if assignment_history:
                            var, val = assignment_history.pop()
                            text += f"{indent}Backtrack: remove {var} = {val}\n"
                            current_depth -= 1
                    
                    elif i % 10 == 0:  # Show some states periodically to avoid overwhelming
                        indent = "  " * current_depth
                        text += f"{indent}Exploring state {i}:\n"
                        if state:
                            for row in state:
                                text += f"{indent}  {row}\n"
                
                # Show final solution if available
                if path and path[-1][1]:
                    text += "\nFinal Solution Found:\n"
                    final_state = path[-1][1]
                    for row in final_state:
                        text += f"  {row}\n"
                else:
                    text += "\nNo solution found after exploring all possibilities.\n"
            else:
                text += "No search process data available."
            
            self.path_display.setText(text)
            return
        
        # Standard display for other algorithms
        text = "Solution Path:\n\n"
        text += "Step 0: Initial State\n"
        for row in initial_state_data:
            text += f"  {row}\n"
        text += "-" * 20 + "\n"

        if not path:
            text += "\n(No solution found or algorithm does not provide a path)"
        else:
            for i, (move, state) in enumerate(path, 1):
                text += f"Step {i}: Move {move.capitalize() if move is not None else 'None'}\n"
                for row in state:
                    text += f"  {row}\n"
                text += "-" * 20 + "\n"

        self.path_display.setText(text)
        self.path_display.verticalScrollBar().setValue(0) # Cuộn lên đầu

    def set_backtracking_mode(self, is_backtracking=False):
        """Set whether this panel should display backtracking results (just stats)."""
        self.is_backtracking = is_backtracking

    def update_algorithm_description(self, algo_key):
        """Cập nhật mô tả thuật toán dựa trên key."""
        description = self.descriptions.get(algo_key.lower(), "No description available for this algorithm.")
        self.algo_desc.setText(description)
        self.algo_desc.verticalScrollBar().setValue(0) # Cuộn lên đầu

    def clear_displays(self):
        self.path_display.clear()
        self.algo_desc.clear()