import traceback
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
    """Thread riêng để chạy thuật toán, tránh đóng băng giao diện"""
    
    solution_ready = pyqtSignal(list, int, object)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, algorithm_key, start_state, heuristic_key=None):
        super().__init__()
        self.algorithm_key = algorithm_key
        self.start_state = start_state
        self.heuristic_key = heuristic_key
    
    def run(self):
        """Chạy thread"""
        try:
            path, nodes, maxf = solve_puzzle(
                self.algorithm_key, 
                self.start_state, 
                heuristic_name=self.heuristic_key
            )
            # Add a check for path being None before emitting the signal
            if path is not None:
                self.solution_ready.emit(path, nodes, maxf)
            else:
                # Handle case where path is None
                self.error_occurred.emit(f"Không thể tìm thấy đường đi. Thuật toán {self.algorithm_key} không tìm thấy giải pháp.")
        except Exception as e:
            traceback.print_exc()
            self.error_occurred.emit(str(e))


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

        # Kích thước bảng, mặc định là 3x3
        self.board_size = 3  # Thêm thuộc tính size cho bảng
        
        # Title
        title_label = QLabel("Điều Hướng Giải Pháp")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 11, QFont.Bold))

        # Puzzle display cho bước hiện tại
        self.current_step_board = PuzzleBoard("Bước Hiện Tại")

        # Step info
        self.step_info = QLabel("Bước 0 / 0")
        self.step_info.setAlignment(Qt.AlignCenter)

        # Navigation buttons
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("<< Trước")
        self.next_btn = QPushButton("Sau >>")
        self.prev_btn.setEnabled(False)
        self.next_btn.setEnabled(False)
        self.prev_btn.setFixedWidth(100)
        self.next_btn.setFixedWidth(100)

        nav_layout.addStretch()
        nav_layout.addWidget(self.prev_btn)
        nav_layout.addWidget(self.next_btn)
        nav_layout.addStretch()

        # Move description
        self.move_desc = QLabel("Tải giải pháp để điều hướng")
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
        
        # Cập nhật kích thước bảng dựa vào initial_state_data
        if initial_state_data:
            self.board_size = len(initial_state_data)
            
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
            self.step_info.setText(f"Bước {self.current_step_index} / {total_steps}")
        else:
            self.step_info.setText("Bước 0 / 0")

    def update_display(self):
        """Display the current step board and move description"""
        if self.current_step_index == -1 or self.initial_state_data is None:
            # Trạng thái chưa load hoặc không hợp lệ
            self.current_step_board.update_board([[0]*self.board_size for _ in range(self.board_size)]) # Bảng trống
            self.move_desc.setText("Tải giải pháp để điều hướng")
            return

        current_state_data = None
        move_text = ""

        if self.current_step_index == 0:
            # Hiển thị trạng thái ban đầu
            current_state_data = self.initial_state_data
            move_text = "Trạng Thái Ban Đầu"
        elif 0 < self.current_step_index <= len(self.solution_path):
            # Hiển thị bước từ 1 trở đi
            move, state_data = self.solution_path[self.current_step_index - 1]
            
            # Verify state_data is valid
            if state_data is None:
                print(f"Warning: None state data at step {self.current_step_index}")
                current_state_data = self.initial_state_data  # Fallback to initial state
            else:
                current_state_data = state_data
                
            # Translate direction if it's one of the standard directions
            move_translation = {
                "up": "Lên", 
                "down": "Xuống", 
                "left": "Trái", 
                "right": "Phải",
                "final": "Cuối cùng"
            }
            translated_move = move_translation.get(move.lower() if move else "", move.capitalize() if move else "None")
            move_text = f"Di chuyển: {translated_move}"
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
        self.move_desc.setText("Tải giải pháp để điều hướng")
        self.step_info.setText("Bước 0 / 0")


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
        start_state_group = QGroupBox("Trạng Thái Ban Đầu")
        start_state_layout = QVBoxLayout()
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("ví dụ: 1 2 3 4 0 5 6 7 8")
        self.load_btn = QPushButton("Tải Trạng Thái Từ Đầu Vào")
        self.load_btn.clicked.connect(self._on_load_clicked)
        self.random_start_btn = QPushButton("Tạo Trạng Thái Bắt Đầu Ngẫu Nhiên")
        self.random_start_btn.clicked.connect(self._on_random_start_clicked)
        self.reset_btn = QPushButton("Đặt Lại Về Trạng Thái Mặc Định")
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
        self.solve_btn = QPushButton("Giải Puzzle")
        self.solve_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 10px; }")
        self.solve_btn.clicked.connect(self._on_solve_clicked)
        main_layout.addWidget(self.solve_btn)

        # Text area cho thống kê (số bước, thời gian, etc.)
        stats_group = QGroupBox("Thống Kê")
        stats_layout = QVBoxLayout()
        self.stats_display = QTextEdit() # Changed from stats_label
        self.stats_display.setReadOnly(True)
        self.stats_display.setMinimumHeight(80)
        stats_layout.addWidget(self.stats_display)
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)

        main_layout.addStretch() # Đẩy các widget lên trên
        self.setLayout(main_layout)
        self.set_stats_text("Chọn thuật toán và trạng thái ban đầu.")


    def _on_load_clicked(self):
        self.load_clicked.emit(self.start_input.text())

    def _on_reset_clicked(self):
        self.start_input.clear()
        self.set_stats_text("Đã đặt lại trạng thái. Chọn thuật toán.")
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
            self.set_stats_text(f"Đang giải với {selected_algo_key.upper()}...") # Use self.set_stats_text
        else:
            QMessageBox.warning(self, "Chưa Chọn Thuật Toán", "Vui lòng chọn một thuật toán giải.")


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
        super().__init__("Chọn Thuật Toán")
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
        "manhattan": "Khoảng Cách Manhattan",
        "misplaced": "Số Ô Sai Vị Trí"
    }

    def __init__(self):
        super().__init__("Tùy Chọn Tìm Kiếm Cục Bộ")
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
        path_group = QGroupBox("Đường Đi Giải Pháp (Văn Bản)")
        path_layout = QVBoxLayout()
        self.path_display = QTextEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setFont(QFont('Consolas', 9)) # Font monospace
        path_layout.addWidget(self.path_display)
        path_group.setLayout(path_layout)

        # Group Box cho Algorithm Description
        desc_group = QGroupBox("Mô Tả Thuật Toán")
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
            "bfs": "Tìm Kiếm Theo Chiều Rộng (BFS):\n- Khám phá từng lớp một.\n- Đảm bảo đường đi ngắn nhất (về số bước đi).\n- Có thể tốn nhiều bộ nhớ cho không gian trạng thái lớn.",
            "dfs": "Tìm Kiếm Theo Chiều Sâu (DFS):\n- Khám phá sâu nhất có thể trên mỗi nhánh trước khi quay lui.\n- Tiết kiệm bộ nhớ.\n- Không đảm bảo đường đi ngắn nhất. Thường cần giới hạn độ sâu.",
            "ucs": "Tìm Kiếm Chi Phí Đồng Nhất (UCS):\n- Khám phá các nút dựa trên chi phí đường đi thấp nhất (giá trị g) từ điểm bắt đầu.\n- Đảm bảo đường đi chi phí thấp nhất nếu chi phí bước đi không âm (ở đây, chi phí=1 cho mỗi bước đi, nên tương tự BFS).\n- Có thể tốn nhiều bộ nhớ.",
            "astar": "Tìm Kiếm A*:\n- Kết hợp chi phí đường đi (g) và ước lượng heuristic (h) (f = g + h).\n- Sử dụng khoảng cách Manhattan làm heuristic.\n- Đảm bảo đường đi ngắn nhất nếu heuristic tối ưu (không bao giờ ước lượng quá chi phí thực tế) và nhất quán.\n- Thường hiệu quả hơn BFS/UCS.",
            "greedy": "Tìm Kiếm Tham Lam Best-First:\n- Mở rộng nút có vẻ gần nhất với đích dựa chỉ trên heuristic (giá trị h).\n- Nhanh nhưng không đảm bảo tối ưu hoặc đầy đủ.\n- Có thể bị mắc kẹt trong vòng lặp hoặc đi theo đường không tối ưu.",
            "ids": "Tìm Kiếm Sâu Dần (IDS):\n- Thực hiện DFS với giới hạn độ sâu tăng dần (0, 1, 2,...).\n- Kết hợp tính đầy đủ và tối ưu của BFS với hiệu quả bộ nhớ của DFS.\n- Có thể chậm hơn do phải mở rộng lại các nút ở độ sâu nông.",
            "idastar": "IDA* (Iterative Deepening A*):\n- Sử dụng giá trị f của A* (g + h) như một ngưỡng cắt tăng dần.\n- Hiệu quả bộ nhớ hơn A* cho các bài toán lớn.\n- Đảm bảo tối ưu với heuristic tối ưu.",
            "hill_climbing": "Leo Đồi (Hill Climbing):\n- Thuật toán tìm kiếm cục bộ luôn di chuyển đến trạng thái lân cận có giá trị heuristic tốt nhất.\n- Rất nhanh nhưng dễ bị mắc kẹt tại các cực tiểu cục bộ.\n- Có thể sử dụng khoảng cách Manhattan hoặc Số ô sai vị trí làm heuristic.\n- Không đảm bảo giải pháp tối ưu.",
            "random_restart_hc": "Leo Đồi Khởi Động Lại Ngẫu Nhiên:\n- Chạy leo đồi nhiều lần từ các điểm bắt đầu ngẫu nhiên khác nhau.\n- Giúp vượt qua vấn đề cực tiểu cục bộ của leo đồi cơ bản.\n- Có nhiều khả năng tìm ra giải pháp tốt, tuy vẫn không đảm bảo tối ưu.\n- Có thể sử dụng khoảng cách Manhattan hoặc Số ô sai vị trí làm heuristic.",
            "simulated_annealing": "Mô Phỏng Luyện Kim (Simulated Annealing):\n- Thuật toán tìm kiếm cục bộ xác suất lấy cảm hứng từ quá trình luyện kim.\n- Cho phép di chuyển đến trạng thái tệ hơn với xác suất giảm dần theo thời gian (khi 'nhiệt độ' giảm).\n- Giúp thoát khỏi cực tiểu cục bộ.\n- Có thể sử dụng khoảng cách Manhattan hoặc Số ô sai vị trí làm heuristic.\n- Không đảm bảo tối ưu nhưng thường tìm ra giải pháp tốt.",
            "genetic_algorithm": "Thuật Toán Di Truyền:\n- Thuật toán tiến hóa duy trì một quần thể các giải pháp ứng viên.\n- Sử dụng các toán tử chọn lọc, lai ghép và đột biến để phát triển quần thể.\n- Chọn lọc ưu tiên các trạng thái có giá trị heuristic tốt hơn.\n- Phù hợp cho không gian tìm kiếm lớn.\n- Có thể sử dụng khoảng cách Manhattan hoặc Số ô sai vị trí làm heuristic.\n- Tìm ra giải pháp tốt nhưng không nhất thiết là đường đi tối ưu.",
            "belief_bfs": "Tìm Kiếm BFS Trạng Thái Niềm Tin (POMDP):\n- Mô hình POMDP (Partially Observable Markov Decision Process).\n- BAN ĐẦU: Chỉ biết 6 ô đầu (hàng 1 và hàng 2), không biết 3 ô cuối (hàng 3).\n- TÌM KIẾM: Duy trì một tập hợp các trạng thái có thể (belief state).\n- QUAN SÁT: Sau mỗi hành động, chỉ quan sát được 6 ô đầu, không biết trạng thái thực tế đầy đủ.\n- NIỀM TIN: Cập nhật tập trạng thái có thể dựa trên hành động và quan sát mới.\n- MỤC TIÊU: Thu hẹp niềm tin xuống còn một trạng thái duy nhất (trạng thái đích).",
            "belief_state_search": (
                "Tìm Kiếm Trạng Thái Niềm Tin:\n\n"
                "- Sử dụng trong môi trường quan sát một phần, nơi tác nhân không thể thấy trạng thái đầy đủ.\n"
                "- Duy trì 'trạng thái niềm tin' - một tập hợp tất cả trạng thái có thể phù hợp với quan sát.\n"
                "- Chế độ quan sát:\n"
                "  * Một phần: Chỉ 6 ô đầu tiên (2 hàng đầu) là có thể nhìn thấy\n"
                "  * Mù hoàn toàn: Không thể nhìn thấy ô nào\n"
                "  * Tùy chỉnh: Mặt nạ hiển thị do người dùng xác định\n\n"
                "- Quá trình tìm kiếm:\n"
                "  1. Khởi tạo với tất cả trạng thái có thể phù hợp với quan sát ban đầu\n"
                "  2. Với mỗi hành động:\n"
                "     a. Áp dụng hành động cho mỗi trạng thái có thể\n"
                "     b. Tạo quan sát mới\n"
                "     c. Lọc các trạng thái không tạo ra quan sát này\n"
                "  3. Mục tiêu: Thu hẹp trạng thái niềm tin xuống chỉ còn trạng thái đích\n\n"
                "- Ứng dụng: Robot, mạng cảm biến, bất kỳ lĩnh vực nào có khả năng cảm biến hạn chế"
            ),
            # Thuật toán RL
            "q_learning": (
                "Q-Learning:\n\n"
                "- Thuật toán học tăng cường không cần mô hình (model-free).\n"
                "- Học các giá trị cặp (trạng thái, hành động) thông qua tương tác với môi trường.\n"
                "- Công thức cập nhật Q:\n"
                "    Q(s,a) = Q(s,a) + α * [R + γ * max_a' Q(s',a') - Q(s,a)]\n"
                "  trong đó:\n"
                "    * α (alpha): Tỷ lệ học tập\n"
                "    * γ (gamma): Hệ số giảm của phần thưởng tương lai\n"
                "    * R: Phần thưởng tức thời\n"
                "    * s, a: Trạng thái và hành động hiện tại\n"
                "    * s': Trạng thái tiếp theo\n"
                "    * max_a' Q(s',a'): Giá trị Q tối đa có thể từ trạng thái tiếp theo\n"
                "- Sử dụng chiến lược epsilon-greedy để cân bằng giữa thăm dò và khai thác.\n"
                "- Hội tụ đến chính sách tối ưu khi thăm đủ tất cả các cặp (s,a).\n"
                "- Ứng dụng trong 8-puzzle: Học cách di chuyển từ bất kỳ trạng thái nào để đạt đến trạng thái đích."
            ),
            "value_iteration": (
                "Value Iteration:\n\n"
                "- Thuật toán quy hoạch động giải bài toán MDP (Markov Decision Process).\n"
                "- Tính toán hàm giá trị tối ưu U*(s) cho mỗi trạng thái.\n"
                "- Công thức cập nhật hàm giá trị Bellman:\n"
                "    U(s) = max_a [R(s,a) + γ * Σ_s' P(s'|s,a) * U(s')]\n"
                "  trong đó:\n"
                "    * R(s,a): Phần thưởng trung bình khi thực hiện hành động a tại s\n"
                "    * γ (gamma): Hệ số giảm của phần thưởng tương lai\n"
                "    * P(s'|s,a): Xác suất chuyển từ s đến s' khi thực hiện a\n"
                "    * U(s'): Giá trị hiện tại của trạng thái s'\n"
                "- Lặp lại quá trình cập nhật cho đến khi hội tụ (thay đổi giá trị nhỏ hơn ngưỡng).\n"
                "- Trích xuất chính sách π*(s) từ hàm giá trị tối ưu.\n"
                "- Đảm bảo tìm ra chính sách tối ưu.\n"
                "- Ứng dụng trong 8-puzzle: Tìm chính sách tối ưu để di chuyển từ bất kỳ trạng thái nào đến trạng thái đích."
            )
        }

    def update_path_display(self, initial_state_data, path):
        """Cập nhật hiển thị đường đi text."""
        if not initial_state_data:
             self.path_display.setText("Chưa tải trạng thái ban đầu.")
             return

        # Special handling for backtracking search
        if hasattr(self, 'is_backtracking') and self.is_backtracking:
            node_count = len(path) if path else 0
            text = "Quá Trình Tìm Kiếm Backtracking:\n\n"
            text += f"Tổng số nút đã khám phá: {node_count}\n\n"
            text += "Trạng Thái Ban Đầu:\n"
            for row in initial_state_data:
                text += f"  {row}\n"
            text += "-" * 30 + "\n\n"
            
            # Show the backtracking process with variable assignments and backtracks
            if path:
                # Display a representation of the search tree/process
                text += "Quá Trình Tìm Kiếm:\n"
                current_depth = 0
                assignment_history = []
                
                for i, (move, state) in enumerate(path):
                    # We'll simulate the backtracking process based on the moves
                    if move == "assignment":  # Variable assignment
                        current_depth += 1
                        indent = "  " * current_depth
                        var_name = f"var{current_depth}" if state else "?"
                        val = f"val{current_depth}" if state else "?"
                        text += f"{indent}Gán {var_name} = {val}\n"
                        assignment_history.append((var_name, val))
                        
                    elif move == "backtrack":  # Backtracking step
                        if assignment_history:
                            var, val = assignment_history.pop()
                            text += f"{indent}Quay lui: xóa {var} = {val}\n"
                            current_depth -= 1
                    
                    elif i % 10 == 0:  # Show some states periodically to avoid overwhelming
                        indent = "  " * current_depth
                        text += f"{indent}Khám phá trạng thái {i}:\n"
                        if state:
                            for row in state:
                                text += f"{indent}  {row}\n"
                
                # Show final solution if available
                if path and path[-1][1]:
                    text += "\nĐã Tìm Thấy Giải Pháp:\n"
                    final_state = path[-1][1]
                    for row in final_state:
                        text += f"  {row}\n"
                else:
                    text += "\nKhông tìm thấy giải pháp sau khi khám phá tất cả khả năng.\n"
            else:
                text += "Không có dữ liệu quá trình tìm kiếm."
            
            self.path_display.setText(text)
            return
        
        # Standard display for other algorithms
        text = "Đường Đi Giải Pháp:\n\n"
        text += "Bước 0: Trạng Thái Ban Đầu\n"
        for row in initial_state_data:
            text += f"  {row}\n"
        text += "-" * 20 + "\n"

        if not path:
            text += "\n(Không tìm thấy giải pháp hoặc thuật toán không cung cấp đường đi)"
        else:
            # Check if path contains a special format from genetic algorithm
            if len(path) == 1 and path[0][0] == "final":
                text += "\nTrạng Thái Cuối Cùng (Thuật Toán Di Truyền hoặc Mô Phỏng Luyện Kim):\n"
                for row in path[0][1]:
                    text += f"  {row}\n"
                text += "\nLưu ý: Các thuật toán tìm kiếm cục bộ thường chỉ trả về trạng thái cuối cùng,\nkhông phải toàn bộ đường đi từng bước di chuyển.\n"
            else:
                # Regular path display for traditional search algorithms
                for i, (move, state) in enumerate(path, 1):
                    # Translate direction if it's one of the standard directions
                    move_translation = {
                        "up": "Lên", 
                        "down": "Xuống", 
                        "left": "Trái", 
                        "right": "Phải",
                        "final": "Cuối cùng"
                    }
                    translated_move = move_translation.get(move.lower() if move else "", move.capitalize() if move else "None")
                    text += f"Bước {i}: Di chuyển {translated_move}\n"
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
        description = self.descriptions.get(algo_key.lower(), "Không có mô tả nào cho thuật toán này.")
        self.algo_desc.setText(description)
        self.algo_desc.verticalScrollBar().setValue(0) # Cuộn lên đầu

    def clear_displays(self):
        self.path_display.clear()
        self.algo_desc.clear()