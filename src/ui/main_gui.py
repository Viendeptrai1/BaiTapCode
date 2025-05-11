import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout,
                           QVBoxLayout, QMessageBox, QProgressBar, QLabel,
                           QTabWidget, QPushButton, QGroupBox, QGridLayout,
                           QLineEdit, QTextEdit, QComboBox, QScrollArea, QSpinBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import time
import traceback
import itertools
import random # Added for random selection
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
        
        # Create and add the blind search tab
        self.blind_search_tab = QWidget()
        self.init_blind_search_tab()
        self.tab_widget.addTab(self.blind_search_tab, "Tìm kiếm với Quan sát Mù Hoàn toàn")
        
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
        elif current_tab_name == "Tìm kiếm với Quan sát Mù Hoàn toàn":
            print("Switched to Blind Search Tab")
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

    def init_blind_search_tab(self):
        """Khởi tạo tab cho tìm kiếm mù hoàn toàn."""
        layout = QVBoxLayout(self.blind_search_tab)
        
        # Header with description
        description_label = QLabel("Tìm kiếm với Quan sát Mù Hoàn toàn (Không Cảm biến)")
        description_label.setFont(QFont("Arial", 12, QFont.Bold))
        description_label.setAlignment(Qt.AlignCenter)
        description_text = QLabel(
            "Tìm kiếm mù hoàn toàn cho puzzle 2x2 với 12 trạng thái có thể.\n"
            "Mỗi hành động sẽ tạo ra tập trạng thái niềm tin mới.")
        description_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(description_label)
        layout.addWidget(description_text)
        layout.addSpacing(10)
        
        # Main content layout: action selection on top, belief states display below
        content_layout = QHBoxLayout()
        
        # Left panel: Controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Actions group
        actions_group = QGroupBox("Hành động & Thiết lập") # Renamed group
        actions_layout = QVBoxLayout(actions_group)
        
        # Action selection
        actions_layout.addWidget(QLabel("Chọn hành động để thực hiện:"))
        self.action_combo = QComboBox()
        self.action_combo.addItems(["Chọn hành động", "Di chuyển Phải", "Di chuyển Trái", "Di chuyển Lên", "Di chuyển Xuống"])
        actions_layout.addWidget(self.action_combo)
        
        # Apply action button
        self.apply_action_button = QPushButton("Áp dụng Hành động")
        actions_layout.addWidget(self.apply_action_button)
        actions_layout.addSpacing(10)

        # Belief state initialization
        actions_layout.addWidget(QLabel("Khởi tạo Tập Niềm tin Ban đầu:"))
        self.reset_beliefs_button = QPushButton("Khởi tạo (12 Trạng thái)")
        actions_layout.addWidget(self.reset_beliefs_button)

        # Input for N random states
        n_states_layout = QHBoxLayout()
        n_states_layout.addWidget(QLabel("Chọn ngẫu nhiên:"))
        self.num_random_states_input = QSpinBox()
        self.num_random_states_input.setRange(1, 12) # Min 1, Max 12 states
        self.num_random_states_input.setValue(8)    # Default to 8
        self.num_random_states_input.setFixedWidth(50)
        n_states_layout.addWidget(self.num_random_states_input)
        n_states_layout.addWidget(QLabel("trạng thái"))
        self.initialize_n_random_button = QPushButton("Khởi tạo N")
        n_states_layout.addWidget(self.initialize_n_random_button)
        actions_layout.addLayout(n_states_layout)
        actions_layout.addSpacing(10)
        
        # Solution finding
        actions_layout.addWidget(QLabel("Tìm kiếm Giải pháp:"))
        self.find_solution_button = QPushButton("Tìm Chuỗi Giải Pháp")
        actions_layout.addWidget(self.find_solution_button)
        
        self.execute_solution_button = QPushButton("Thực hiện Từng Bước")
        self.execute_solution_button.setEnabled(False)  # Initially disabled
        actions_layout.addWidget(self.execute_solution_button)
        
        left_layout.addWidget(actions_group)
        
        # Add current belief state summary
        belief_summary_group = QGroupBox("Thống kê")
        belief_summary_layout = QVBoxLayout(belief_summary_group)
        self.belief_count_label = QLabel("Số lượng trạng thái niềm tin hiện tại: 12")
        belief_summary_layout.addWidget(self.belief_count_label)
        
        self.goal_state_label = QLabel(f"Trạng thái đích: {[[1, 2], [3, 0]]}")
        belief_summary_layout.addWidget(self.goal_state_label)
        
        self.solution_status_label = QLabel("Giải pháp: Chưa tìm thấy")
        belief_summary_layout.addWidget(self.solution_status_label)
        
        left_layout.addWidget(belief_summary_group)
        
        left_layout.addStretch()
        content_layout.addWidget(left_panel, 1) # 1/4 width
        
        # Right panel: Belief states display
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        right_layout.addWidget(QLabel("Tập Trạng thái Niềm tin Hiện tại:"))
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.belief_states_layout = QGridLayout(scroll_widget)
        
        self.belief_states_widgets = []
        for i in range(12): # Max 12 widgets for display
            belief_state_widget = PuzzleBoard(title=f"Trạng thái #{i+1}", size=2)
            self.belief_states_widgets.append(belief_state_widget)
            row, col = divmod(i, 4)
            self.belief_states_layout.addWidget(belief_state_widget, row, col)
        
        scroll_area.setWidget(scroll_widget)
        right_layout.addWidget(scroll_area)
        
        self.blind_search_log = QTextEdit()
        self.blind_search_log.setReadOnly(True)
        self.blind_search_log.setFont(QFont("Courier New", 10))
        self.blind_search_log.setPlaceholderText("Các hành động và kết quả sẽ được hiển thị ở đây.")
        self.blind_search_log.setMaximumHeight(150)
        right_layout.addWidget(QLabel("Nhật ký Hành động:"))
        right_layout.addWidget(self.blind_search_log)
        
        content_layout.addWidget(right_panel, 3)
        layout.addLayout(content_layout)
        
        self.apply_action_button.clicked.connect(self.apply_blind_action)
        self.reset_beliefs_button.clicked.connect(self.reset_belief_states_to_full)
        self.initialize_n_random_button.clicked.connect(self.initialize_n_random_belief_states) # New connection
        self.find_solution_button.clicked.connect(self.find_blind_search_solution)
        self.execute_solution_button.clicked.connect(self.execute_next_solution_step)
        
        self.all_possible_2x2_states = self._generate_all_solvable_2x2_states()
        self.blind_goal_state = [[1, 2], [3, 0]]
        self.solution_sequence = []
        self.current_solution_step = 0
        
        self.reset_belief_states_to_full() # Initialize with all 12 states

    def _generate_all_solvable_2x2_states(self):
        """Tạo tất cả 12 trạng thái 2x2 có thể giải được."""
        # For 2x2 puzzle, there are 24 possible permutations (4!)
        # But only 12 are solvable (4!/2)
        all_states = []
        
        # Permutations of [0,1,2,3]
        base_state = [0, 1, 2, 3]
        # Get all permutations
        for perm in itertools.permutations(base_state):
            # Convert to 2x2 matrix
            matrix = [list(perm[:2]), list(perm[2:])]
            
            # Check if permutation is solvable
            # For 2x2, a state is solvable if the number of inversions is even
            # (0 doesn't count in inversions)
            flat_without_blank = [num for num in perm if num != 0]
            inversions = 0
            for i in range(len(flat_without_blank)):
                for j in range(i+1, len(flat_without_blank)):
                    if flat_without_blank[i] > flat_without_blank[j]:
                        inversions += 1
            
            if inversions % 2 == 0:  # Solvable if even number of inversions
                all_states.append(matrix)
        
        return all_states[:12]  # Should be exactly 12 states

    def update_belief_state_display(self):
        """Cập nhật hiển thị các trạng thái niềm tin."""
        count = len(self.current_belief_states)
        self.belief_count_label.setText(f"Số lượng trạng thái niềm tin hiện tại: {count}")
        
        for i in range(len(self.belief_states_widgets)):
            if i < count:
                self.belief_states_widgets[i].setVisible(True)
                self.belief_states_widgets[i].update_board(self.current_belief_states[i])
                self.belief_states_widgets[i].set_title(f"Trạng thái #{i+1}")
            else:
                self.belief_states_widgets[i].setVisible(False)

    def apply_blind_action(self):
        """Áp dụng hành động được chọn lên tập trạng thái niềm tin hiện tại."""
        action = self.action_combo.currentText()
        if action == "Chọn hành động":
            QMessageBox.warning(self, "Lỗi", "Vui lòng chọn một hành động để thực hiện.")
            return
        
        # Map action to direction
        direction_map = {
            "Di chuyển Phải": "Phải",
            "Di chuyển Trái": "Trái", 
            "Di chuyển Lên": "Lên",
            "Di chuyển Xuống": "Xuống"
        }
        direction = direction_map[action]
        
        # Apply the action to each state in current belief state
        new_belief_states = []
        for state in self.current_belief_states:
            # Find blank position
            blank_pos = None
            for r in range(2):
                for c in range(2):
                    if state[r][c] == 0:
                        blank_pos = (r, c)
                        break
                if blank_pos:
                    break
            
            # Calculate new position based on direction
            dr, dc = 0, 0
            if direction == "Phải":
                dc = 1  # Blank moves right
            elif direction == "Trái":
                dc = -1  # Blank moves left
            elif direction == "Lên":
                dr = -1  # Blank moves up
            elif direction == "Xuống":
                dr = 1  # Blank moves down
            
            new_blank_r, new_blank_c = blank_pos[0] + dr, blank_pos[1] + dc
            
            # Check if new position is valid
            if 0 <= new_blank_r < 2 and 0 <= new_blank_c < 2:
                # Create new state with moved tile
                new_state = [row[:] for row in state]  # Deep copy
                new_state[blank_pos[0]][blank_pos[1]] = new_state[new_blank_r][new_blank_c]
                new_state[new_blank_r][new_blank_c] = 0
                new_belief_states.append(new_state)
        
        # Update current belief states
        if new_belief_states:
            self.current_belief_states = new_belief_states
            self.update_belief_state_display()
            self.log_to_blind_search(f"Áp dụng hành động '{action}': Tập niềm tin mới gồm {len(new_belief_states)} trạng thái.")
        else:
            self.log_to_blind_search(f"Không thể áp dụng hành động '{action}' cho bất kỳ trạng thái nào trong tập niềm tin hiện tại.")

    def reset_belief_states_to_full(self):
        """Khởi tạo lại tập niềm tin về ban đầu với 12 trạng thái."""
        self.current_belief_states = [list(row) for row in self.all_possible_2x2_states]
        self.update_belief_state_display()
        self.log_to_blind_search("Đã khởi tạo lại tập niềm tin về 12 trạng thái ban đầu.")
        self._reset_solution_related_ui()
        self.num_random_states_input.setValue(len(self.all_possible_2x2_states) if self.all_possible_2x2_states else 8) # Reset spinbox

    def initialize_n_random_belief_states(self):
        """Chọn ngẫu nhiên N trạng thái ban đầu từ QSpinBox."""
        num_to_select = self.num_random_states_input.value()

        if not self.all_possible_2x2_states or len(self.all_possible_2x2_states) == 0:
            QMessageBox.warning(self, "Lỗi", "Không có trạng thái gốc nào được tạo.")
            self.log_to_blind_search("Lỗi: Danh sách trạng thái gốc trống rỗng.")
            return

        if num_to_select < 1 or num_to_select > len(self.all_possible_2x2_states):
            QMessageBox.warning(self, "Số lượng không hợp lệ", 
                                f"Vui lòng chọn số lượng từ 1 đến {len(self.all_possible_2x2_states)}.\n")
            self.log_to_blind_search(f"Lỗi: Số lượng chọn ({num_to_select}) không hợp lệ.")
            return

        selected_states_tuples = random.sample(self.all_possible_2x2_states, num_to_select)
        self.current_belief_states = [list(row) for row in selected_states_tuples]
        
        self.update_belief_state_display()
        self.log_to_blind_search(f"Đã chọn ngẫu nhiên {num_to_select} trạng thái làm tập niềm tin ban đầu.")
        self._reset_solution_related_ui()

    def _reset_solution_related_ui(self):
        """Helper to reset UI elements related to solution finding/execution."""
        self.solution_sequence = []
        self.current_solution_step = 0
        self.solution_status_label.setText("Giải pháp: Chưa tìm thấy")
        self.execute_solution_button.setText("Thực hiện Từng Bước")
        self.execute_solution_button.setEnabled(False)
        self.find_solution_button.setEnabled(True)
        self.action_combo.setCurrentIndex(0)
        self._initial_belief_state_for_current_solution = None # Clear stored initial state

    def log_to_blind_search(self, message):
        """Ghi log vào vùng nhật ký của tab tìm kiếm mù."""
        self.blind_search_log.append(f"[{time.strftime('%H:%M:%S')}] {message}")
        # Scroll to bottom
        self.blind_search_log.verticalScrollBar().setValue(
            self.blind_search_log.verticalScrollBar().maximum()
        )

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

    def find_blind_search_solution(self):
        """Tìm chuỗi giải pháp cho tìm kiếm mù hoàn toàn."""
        self.log_to_blind_search("Đang tìm chuỗi giải pháp...")
        self.find_solution_button.setEnabled(False)
        self.solution_status_label.setText("Giải pháp: Đang tìm...")
        QApplication.processEvents()  # Update UI
        
        if not self.current_belief_states:
            self.log_to_blind_search("Lỗi: Tập trạng thái niềm tin ban đầu trống rỗng. Không thể tìm giải pháp.")
            self.solution_status_label.setText("Giải pháp: Lỗi (tập rỗng)")
            self.find_solution_button.setEnabled(True)
            return
            
        # Store the initial belief state from which the solution is found
        # This is important so that execute_next_solution_step starts correctly.
        # We will reset current_belief_states to this before starting execution if needed,
        # or ensure execute_next_solution_step uses a copy.
        # For now, we rely on the user not changing the belief state between find and execute.
        # The _reset_solution_related_ui method already handles resetting action_combo and current_solution_step.

        goal_state_as_tuple = tuple(map(tuple, self.blind_goal_state))
        belief_states_as_tuples = [tuple(map(tuple, state)) for state in self.current_belief_states]
        initial_belief_state_fs_for_search = frozenset(belief_states_as_tuples)
        
        visited = {}
        # Store the initial belief state for this search instance
        # This is used to reset the display if the user wants to re-run the found solution
        self._initial_belief_state_for_current_solution = [list(row) for row in self.current_belief_states]

        queue = [(initial_belief_state_fs_for_search, [])] 
        
        solution_found = False
        final_belief_state_at_solution = None # To store the belief state when solution is found
        
        while queue and not solution_found:
            current_belief_state_fs, actions = queue.pop(0)
            
            if current_belief_state_fs in visited:
                continue
            
            visited[current_belief_state_fs] = actions
            
            if len(current_belief_state_fs) == 1 and goal_state_as_tuple in current_belief_state_fs:
                self.solution_sequence = actions
                solution_found = True
                final_belief_state_at_solution = current_belief_state_fs
                # DO NOT update self.current_belief_states here.
                # self.current_belief_states should remain what it was when "Find Solution" was clicked.
                # The display of current_belief_states should not change at this point.
                break
            
            for direction, action_text in [
                ("Phải", "Di chuyển Phải"), 
                ("Trái", "Di chuyển Trái"), 
                ("Lên", "Di chuyển Lên"), 
                ("Xuống", "Di chuyển Xuống")
            ]:
                next_belief_state_fs = self._apply_action_to_belief_state(current_belief_state_fs, direction)
                
                if next_belief_state_fs and next_belief_state_fs not in visited:
                    queue.append((next_belief_state_fs, actions + [action_text]))
        
        if solution_found:
            num_steps = len(self.solution_sequence)
            self.solution_status_label.setText(f"Giải pháp: Tìm thấy ({num_steps} bước)")
            self.execute_solution_button.setEnabled(True if num_steps > 0 else False)
            self.current_solution_step = 0 # Reset step counter for execution
            if num_steps > 0:
                solution_text = ", ".join(self.solution_sequence)
                self.log_to_blind_search(f"Tìm thấy giải pháp: {solution_text}")
                self.execute_solution_button.setText(f"Bước Tiếp Theo ({num_steps} còn lại)")
            else:
                self.log_to_blind_search("Tìm thấy giải pháp: Trạng thái ban đầu đã là đích (0 bước).")
                self.execute_solution_button.setText("Thực hiện Từng Bước")
        else:
            self.solution_status_label.setText("Giải pháp: Không tìm thấy")
            self.log_to_blind_search("Không tìm thấy giải pháp.")
            self.execute_solution_button.setEnabled(False)
            self._initial_belief_state_for_current_solution = None # No solution, no specific initial state
        
        self.find_solution_button.setEnabled(True)

    def _apply_action_to_belief_state(self, belief_state, direction):
        """Áp dụng hành động cho tập trạng thái niềm tin và trả về tập mới."""
        # Convert belief state from frozenset of tuples to list of lists for processing
        belief_state_as_list = [[list(row) for row in state] for state in belief_state]
        
        # Apply action to each state
        new_belief_states = []
        for state in belief_state_as_list:
            # Find blank position
            blank_pos = None
            for r in range(2):
                for c in range(2):
                    if state[r][c] == 0:
                        blank_pos = (r, c)
                        break
                if blank_pos:
                    break
            
            # Calculate new position based on direction
            dr, dc = 0, 0
            if direction == "Phải":
                dc = 1  # Blank moves right
            elif direction == "Trái":
                dc = -1  # Blank moves left
            elif direction == "Lên":
                dr = -1  # Blank moves up
            elif direction == "Xuống":
                dr = 1  # Blank moves down
            
            new_blank_r, new_blank_c = blank_pos[0] + dr, blank_pos[1] + dc
            
            # Check if new position is valid
            if 0 <= new_blank_r < 2 and 0 <= new_blank_c < 2:
                # Create new state with moved tile
                new_state = [row[:] for row in state]  # Deep copy
                new_state[blank_pos[0]][blank_pos[1]] = new_state[new_blank_r][new_blank_c]
                new_state[new_blank_r][new_blank_c] = 0
                new_belief_states.append(new_state)
        
        if new_belief_states:
            # Convert back to frozenset of tuples for hashability
            return frozenset(tuple(map(tuple, state)) for state in new_belief_states)
        return None
    
    def execute_next_solution_step(self):
        """Thực hiện bước tiếp theo trong chuỗi giải pháp."""
        if self.current_solution_step == 0 and hasattr(self, '_initial_belief_state_for_current_solution') and self._initial_belief_state_for_current_solution:
            # If this is the first step of execution, reset current_belief_states to what it was when the solution was found.
            self.current_belief_states = [list(row) for row in self._initial_belief_state_for_current_solution]
            self.update_belief_state_display()
            self.log_to_blind_search("Bắt đầu thực hiện giải pháp từ trạng thái niềm tin ban đầu (khi tìm giải pháp). ")

        if not self.solution_sequence or self.current_solution_step >= len(self.solution_sequence):
            self.log_to_blind_search("Đã thực hiện hết các bước trong giải pháp hoặc không có giải pháp.")
            self.execute_solution_button.setEnabled(False)
            self.execute_solution_button.setText("Thực hiện Từng Bước")
            # self._initial_belief_state_for_current_solution = None # Clear after full execution
            return
            
        action = self.solution_sequence[self.current_solution_step]
        
        # Log before applying, so it's clear which action is for current display state
        self.log_to_blind_search(f"Bước {self.current_solution_step + 1}/{len(self.solution_sequence)}: Áp dụng hành động '{action}'")
        
        self.action_combo.setCurrentText(action) # Visually select in combo
        self.apply_blind_action() # This will update current_belief_states and log its own message
        
        self.current_solution_step += 1 # Increment after applying
        
        remaining = len(self.solution_sequence) - self.current_solution_step
        if remaining > 0:
            self.execute_solution_button.setText(f"Bước Tiếp Theo ({remaining} còn lại)")
        else:
            self.execute_solution_button.setText("Thực hiện Từng Bước")
            self.execute_solution_button.setEnabled(False)
            self.log_to_blind_search("Đã thực hiện hết các bước giải pháp.")
            # self._initial_belief_state_for_current_solution = None # Clear after full execution

if __name__ == '__main__':
    # Bắt buộc dùng QApplication
    app = QApplication(sys.argv)
    window = PuzzleWindow()
    window.show()
    sys.exit(app.exec())
