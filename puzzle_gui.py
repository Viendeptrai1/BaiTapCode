from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                           QGridLayout, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QComboBox, QLineEdit,
                           QMessageBox, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont
import sys
from Solve import Buzzle, solve_puzzle

class PuzzleBoard(QWidget):
    """Một bảng puzzle đơn lẻ"""
    def __init__(self, title="Puzzle"):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Container cho grid puzzle với border
        puzzle_container = QWidget()
        puzzle_container.setStyleSheet("""
            QWidget {
                background-color: #333;
                border: 2px solid #666;
                border-radius: 5px;
            }
        """)
        container_layout = QVBoxLayout()
        container_layout.setSpacing(0)
        container_layout.setContentsMargins(2, 2, 2, 2)
        
        # Grid cho các ô puzzle
        grid = QGridLayout()
        grid.setSpacing(1)
        self.tiles = []
        
        for i in range(3):
            row = []
            for j in range(3):
                btn = QPushButton()
                btn.setFixedSize(80, 80)
                btn.setFont(QFont('Arial', 24, QFont.Bold))
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;
                        border: 1px solid #999;
                        border-radius: 0px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                """)
                grid.addWidget(btn, i, j)
                row.append(btn)
            self.tiles.append(row)
        
        container_layout.addLayout(grid)
        puzzle_container.setLayout(container_layout)
        layout.addWidget(puzzle_container)
        
        self.setLayout(layout)
    
    def update_board(self, state):
        for i in range(3):
            for j in range(3):
                value = state[i][j]
                self.tiles[i][j].setText(str(value) if value != 0 else "")

class ControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        # Input trạng thái
        input_group = QWidget()
        input_layout = QHBoxLayout()
        
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Initial state (e.g: 1 2 0 3 4 5 6 7 8)")
        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("Goal state (optional)")
        
        input_layout.addWidget(self.start_input)
        input_layout.addWidget(self.goal_input)
        input_group.setLayout(input_layout)
        
        # Nút điều khiển
        button_group = QWidget()
        button_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("Load States")
        self.reset_btn = QPushButton("Reset")
        self.solve_btn = QPushButton("Solve")
        
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.solve_btn)
        button_group.setLayout(button_layout)
        
        # Chọn thuật toán
        algo_group = QWidget()
        algo_layout = QHBoxLayout()
        
        self.algo_select = QComboBox()
        self.algo_select.addItems(["BFS", "DFS", "UCS", "A*", "Greedy", "IDS"])
        self.stats_label = QLabel("Ready")
        
        algo_layout.addWidget(QLabel("Algorithm:"))
        algo_layout.addWidget(self.algo_select)
        algo_layout.addWidget(self.stats_label)
        algo_group.setLayout(algo_layout)
        
        # Thêm vào layout chính
        layout.addWidget(input_group)
        layout.addWidget(button_group)
        layout.addWidget(algo_group)
        layout.addStretch()
        
        self.setLayout(layout)

class ResultPanel(QWidget):
    """Panel hiển thị kết quả và mô tả thuật toán"""
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        
        # Phần hiển thị đường đi
        self.path_display = QTextEdit()
        self.path_display.setReadOnly(True)
        self.path_display.setFixedHeight(200)
        
        # Phần hiển thị mô tả thuật toán
        self.algo_desc = QTextEdit()
        self.algo_desc.setReadOnly(True)
        self.algo_desc.setFixedHeight(200)
        
        # Tạo splitter để chia đôi panel
        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.path_display)
        splitter.addWidget(self.algo_desc)
        splitter.setSizes([300, 300])  # Chia đều không gian
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
    def update_path(self, path):
        """Cập nhật hiển thị đường đi"""
        text = "Solution path:\n\n"
        for i, (move, state) in enumerate(path, 1):
            text += f"Step {i}: {move}\n"
            for row in state:
                text += f"{row}\n"
            text += "\n"
        self.path_display.setText(text)
        
    def update_algo_desc(self, algo_name):
        """Cập nhật mô tả thuật toán"""
        descriptions = {
            "bfs": "Breadth-First Search:\n- Tìm kiếm theo chiều rộng\n- Duyệt tất cả các trạng thái ở cùng độ sâu\n- Đảm bảo tìm ra đường đi ngắn nhất",
            "dfs": "Depth-First Search:\n- Tìm kiếm theo chiều sâu\n- Duyệt hết một nhánh trước khi quay lui\n- Không đảm bảo đường đi ngắn nhất",
            "ucs": "Uniform Cost Search:\n- Tìm kiếm theo chi phí đồng nhất\n- Mở rộng node có chi phí thấp nhất\n- Đảm bảo tìm ra đường đi tối ưu",
            "astar": "A* Search:\n- Kết hợp chi phí đường đi và heuristic\n- Sử dụng hàm f(n) = g(n) + h(n)\n- Đảm bảo tối ưu với heuristic admissible",
            "greedy": "Greedy Best-First Search:\n- Chỉ dựa vào heuristic\n- Luôn mở rộng node có h(n) nhỏ nhất\n- Nhanh nhưng không đảm bảo tối ưu",
            "ids": "Iterative Deepening Search:\n- DFS với độ sâu tăng dần\n- Kết hợp ưu điểm của BFS và DFS\n- Đảm bảo tìm ra đường đi ngắn nhất"
        }
        self.algo_desc.setText(descriptions.get(algo_name, ""))

class PuzzleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("8-Puzzle Solver")
        
        # Widget chính với tỷ lệ 16:9
        main_widget = QWidget()
        main_layout = QHBoxLayout()  # Chia layout theo chiều ngang
        
        # Panel trái (chiếm 70% chiều ngang)
        left_panel = QWidget()
        left_layout = QVBoxLayout()
        
        # Container cho 2 bảng puzzle
        boards_container = QWidget()
        boards_layout = QHBoxLayout()
        boards_layout.setSpacing(10)
        
        self.start_board = PuzzleBoard("Initial State")
        self.goal_board = PuzzleBoard("Goal State")
        boards_layout.addWidget(self.start_board)
        boards_layout.addWidget(self.goal_board)
        boards_container.setLayout(boards_layout)
        
        # Thêm Result Panel vào panel trái
        self.result_panel = ResultPanel()
        
        left_layout.addWidget(boards_container, stretch=3)  # Chiếm 3/4 chiều cao
        left_layout.addWidget(self.result_panel, stretch=1) # Chiếm 1/4 chiều cao
        left_panel.setLayout(left_layout)
        
        # Panel phải cho điều khiển (chiếm 30% chiều ngang)
        self.control_panel = ControlPanel()
        
        # Thêm vào layout chính với tỷ lệ 7:3
        main_layout.addWidget(left_panel, stretch=7)
        main_layout.addWidget(self.control_panel, stretch=3)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # Set kích thước cửa sổ tỷ lệ 16:9
        self.resize(1280, 720)
        
        # Kết nối signals
        self.control_panel.load_btn.clicked.connect(self.load_states)
        self.control_panel.reset_btn.clicked.connect(self.reset_states)
        self.control_panel.solve_btn.clicked.connect(self.solve_puzzle)
        
        # Khởi tạo states
        self.start_state = Buzzle()
        self.goal_state = Buzzle()
        self.update_display()
    
    def load_states(self):
        """Load cả 2 trạng thái từ input"""
        try:
            # Load start state
            start_input = self.control_panel.start_input.text()
            start_numbers = [int(x) for x in start_input.split()]
            if len(start_numbers) != 9 or set(start_numbers) != set(range(9)):
                raise ValueError("Invalid start state")
            self.start_state.data = [start_numbers[i:i+3] for i in range(0, 9, 3)]
            
            # Load goal state nếu có
            goal_input = self.control_panel.goal_input.text()
            if goal_input.strip():
                goal_numbers = [int(x) for x in goal_input.split()]
                if len(goal_numbers) != 9 or set(goal_numbers) != set(range(9)):
                    raise ValueError("Invalid goal state")
                self.goal_state.data = [goal_numbers[i:i+3] for i in range(0, 9, 3)]
            
            self.update_display()
            
        except (ValueError, IndexError) as e:
            QMessageBox.warning(self, "Error", str(e))
    
    def update_display(self):
        """Cập nhật hiển thị cả 2 bảng"""
        self.start_board.update_board(self.start_state.data)
        self.goal_board.update_board(self.goal_state.data)
    
    def solve_puzzle(self):
        """Xử lý khi nhấn nút Solve"""
        algorithm = self.control_panel.algo_select.currentText().lower()
        path, nodes, max_fringe = solve_puzzle(algorithm, self.start_state)
        
        # Cập nhật kết quả
        self.result_panel.update_path(path)
        self.result_panel.update_algo_desc(algorithm)
        
        # Cập nhật thống kê
        stats = f"Nodes expanded: {nodes}\nMax fringe size: {max_fringe}"
        self.control_panel.stats_label.setText(stats)
        
    def reset_states(self):
        """Reset về trạng thái ban đầu"""
        self.start_state = Buzzle()
        self.goal_state = Buzzle()
        self.update_display()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PuzzleWindow()
    window.show()
    sys.exit(app.exec())
