from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QTextEdit, QRadioButton,
                           QButtonGroup, QMessageBox, QGroupBox, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from PyQt5.QtGui import QFont
import threading
import time
from src.algorithms.algorithm_manager import solve_puzzle
from src.algorithms.csp_algorithms import create_puzzle_state_from_known_positions

class CSPConfigPanel(QWidget):
    """Panel chứa cấu hình cho các thuật toán CSP."""
    
    def __init__(self, parent, on_solve_callback):
        super().__init__(parent)
        self.parent = parent
        self.on_solve_callback = on_solve_callback
        
        # Lưu trữ các vị trí đã biết
        self.known_positions = {}  # Dict mapping từ tile index (0-8) đến vị trí (row, col)
        
        # Tạo giao diện
        self._create_widgets()
        
    def _create_widgets(self):
        """Tạo các thành phần giao diện."""
        main_layout = QVBoxLayout(self)
        
        # Tiêu đề
        title_label = QLabel("Cấu hình CSP")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # Layout chính chứa panel trái và phải
        content_layout = QHBoxLayout()
        
        # Panel trái: Lưới vị trí và nút điều khiển
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Frame chứa lưới bố trí các ô
        grid_group = QGroupBox("Đặt các ô đã biết vị trí")
        grid_layout = QGridLayout()
        
        # Tạo lưới 3x3 các nút để đặt vị trí
        self.position_buttons = {}
        for row in range(3):
            for col in range(3):
                position = (row, col)
                button = QPushButton("")
                button.setFixedSize(60, 60)
                button.setFont(QFont('Arial', 18, QFont.Bold))
                button.clicked.connect(lambda checked, pos=position: self._on_position_click(pos))
                grid_layout.addWidget(button, row, col)
                self.position_buttons[position] = button
        
        grid_group.setLayout(grid_layout)
        left_layout.addWidget(grid_group)
        
        # Frame chứa các nút điều khiển
        control_group = QGroupBox("Điều khiển")
        control_layout = QVBoxLayout()
        
        # Layout cho các nút giải
        solve_layout = QGridLayout()
        
        # Nút giải
        ac3_button = QPushButton("Giải bằng AC-3")
        ac3_button.clicked.connect(lambda: self._solve("ac3"))
        solve_layout.addWidget(ac3_button, 0, 0)
        
        backtracking_button = QPushButton("Giải bằng Backtracking")
        backtracking_button.clicked.connect(lambda: self._solve("backtracking"))
        solve_layout.addWidget(backtracking_button, 0, 1)
        
        backtracking_mrv_button = QPushButton("Backtracking với MRV")
        backtracking_mrv_button.clicked.connect(lambda: self._solve("backtracking_with_mrv"))
        solve_layout.addWidget(backtracking_mrv_button, 1, 0)
        
        backtracking_mrv_lcv_button = QPushButton("Backtracking với MRV & LCV")
        backtracking_mrv_lcv_button.clicked.connect(lambda: self._solve("backtracking_with_mrv_lcv"))
        solve_layout.addWidget(backtracking_mrv_lcv_button, 1, 1)
        
        # Nút xóa tất cả
        clear_button = QPushButton("Xóa tất cả")
        clear_button.clicked.connect(self._clear_all)
        solve_layout.addWidget(clear_button, 2, 0, 1, 2)  # span 2 columns
        
        control_layout.addLayout(solve_layout)
        
        # Nhãn trạng thái
        self.status_label = QLabel("Sẵn sàng")
        control_layout.addWidget(self.status_label)
        
        control_group.setLayout(control_layout)
        left_layout.addWidget(control_group)
        
        # Panel phải: Chọn ô và thông tin
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Frame chọn ô cần đặt
        tile_selection_group = QGroupBox("Chọn ô cần đặt")
        tile_layout = QVBoxLayout()
        
        # Tạo các nút radio để chọn ô
        self.button_group = QButtonGroup(self)
        for i in range(9):
            name = "Trống" if i == 0 else str(i)
            radio_button = QRadioButton(name)
            radio_button.setProperty("tile_index", i)
            self.button_group.addButton(radio_button)
            tile_layout.addWidget(radio_button)
            if i == 0:  # Mặc định chọn ô trống
                radio_button.setChecked(True)
        
        tile_selection_group.setLayout(tile_layout)
        right_layout.addWidget(tile_selection_group)
        
        # Thêm panel trái và phải vào layout chính
        content_layout.addWidget(left_panel)
        content_layout.addWidget(right_panel)
        main_layout.addLayout(content_layout)
        
        # Thêm khung hiển thị thông tin thuật toán
        info_group = QGroupBox("Thông tin về thuật toán CSP")
        info_layout = QVBoxLayout()
        
        # Text widget để hiển thị thông tin
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)
        
        # Hiển thị thông tin mặc định
        self._show_algorithm_info()
        
    def _on_position_click(self, position):
        """Xử lý khi người dùng nhấp vào một ô trên lưới."""
        checked_button = self.button_group.checkedButton()
        if not checked_button:
            return
            
        tile_index = checked_button.property("tile_index")
        
        # Kiểm tra nếu vị trí này đã được gán cho một ô khác
        for existing_tile, existing_pos in list(self.known_positions.items()):
            if existing_pos == position:
                del self.known_positions[existing_tile]
                
        # Kiểm tra nếu ô này đã được gán một vị trí khác
        if tile_index in self.known_positions:
            old_position = self.known_positions[tile_index]
            self.position_buttons[old_position].setText("")
            
        # Cập nhật vị trí mới
        self.known_positions[tile_index] = position
        
        # Cập nhật giao diện
        self._update_grid_display()
        
    def _update_grid_display(self):
        """Cập nhật hiển thị lưới với các vị trí đã biết."""
        # Xóa tất cả hiển thị
        for button in self.position_buttons.values():
            button.setText("")
            
        # Hiển thị các vị trí đã biết
        for tile, position in self.known_positions.items():
            text = "" if tile == 0 else str(tile)
            self.position_buttons[position].setText(text)
            # Thêm style đặc biệt cho ô trống
            if tile == 0:
                self.position_buttons[position].setStyleSheet("background-color: #555; color: white;")
            else:
                self.position_buttons[position].setStyleSheet("")
    
    def _clear_all(self):
        """Xóa tất cả các vị trí đã biết."""
        self.known_positions.clear()
        self._update_grid_display()
        self.status_label.setText("Đã xóa tất cả vị trí")
    
    def _solve(self, algorithm_key):
        """Giải bài toán với thuật toán đã chọn."""
        if not self.known_positions:
            QMessageBox.warning(self, "Cảnh báo", "Bạn chưa đặt vị trí cho bất kỳ ô nào!")
            return
            
        # Kiểm tra vị trí đã đặt cho cùng một ô
        positions_set = set(self.known_positions.values())
        if len(positions_set) != len(self.known_positions):
            QMessageBox.critical(self, "Lỗi", "Có nhiều ô được đặt vào cùng một vị trí!")
            return
            
        # Cập nhật trạng thái
        self.status_label.setText(f"Đang giải bằng {algorithm_key}...")
        
        # Tạo trạng thái puzzle từ các vị trí đã biết
        initial_state = create_puzzle_state_from_known_positions(self.known_positions)
        
        # Gọi callback để giải
        self.on_solve_callback(algorithm_key, initial_state, known_positions=self.known_positions)
    
    def _show_algorithm_info(self):
        """Hiển thị thông tin về các thuật toán CSP."""
        info = """
Cách tiếp cận CSP (Constraint Satisfaction Problem) cho 8-Puzzle:

1. Biến (Variables):
   - 9 biến từ T0 đến T8, mỗi biến đại diện cho một ô số hoặc ô trống.
   - T0 là ô trống, T1 đến T8 là các ô số từ 1 đến 8.

2. Miền giá trị (Domains):
   - Miền giá trị cho mỗi biến là tập hợp các vị trí có thể trên lưới 3x3.
   - Mỗi biến có thể có vị trí từ (0,0) đến (2,2).

3. Ràng buộc (Constraints):
   - Ràng buộc chính: Tất cả các ô phải ở các vị trí khác nhau (Alldiff).

4. Thuật toán AC-3:
   - Thuật toán tuyền ràng buộc cung.
   - Thu gọn miền giá trị của các biến dựa trên các ràng buộc.
   - Có thể tìm ra giải pháp duy nhất trong một số trường hợp.

5. Thuật toán Backtracking:
   - Thuật toán tìm kiếm có hệ thống.
   - Gán giá trị cho các biến theo thứ tự và quay lui khi gặp xung đột.
   - Hỗ trợ heuristic MRV (Minimum Remaining Values) và LCV (Least Constraining Value).

Cách sử dụng:
1. Đặt vị trí cho một số ô trên lưới bằng cách:
   - Chọn số ô bên phải (0 là ô trống)
   - Nhấp vào vị trí trên lưới 3x3 bên trái
2. Nhấn nút giải với thuật toán mong muốn
3. Kết quả sẽ hiển thị trên bảng puzzle
"""
        self.info_text.setText(info)
    
    def update_result(self, is_success, stats):
        """Cập nhật kết quả giải."""
        if is_success:
            self.status_label.setText("Đã tìm thấy giải pháp!")
        else:
            self.status_label.setText("Không tìm thấy giải pháp.")
            
        # Hiển thị thống kê
        if stats:
            info = "Thống kê:\n"
            if 'time' in stats:
                info += f"- Thời gian thực thi: {stats['time']:.4f} giây\n"
            if 'nodes' in stats:
                info += f"- Số nút đã duyệt: {stats['nodes']}\n"
            if 'backtracks' in stats:
                info += f"- Số lần backtrack: {stats['backtracks']}\n"
            if 'steps' in stats:
                info += f"- Số bước thực hiện: {stats['steps']}\n"
                
            if not is_success and 'domains' in stats:
                # Hiển thị thông tin về domain còn lại nếu không tìm thấy giải pháp duy nhất
                info += "\nCác giá trị domain còn lại:\n"
                for var, domain in stats['domains'].items():
                    if len(domain) > 1:  # Chỉ hiển thị các domain có nhiều giá trị
                        tile_name = "Trống" if var == 0 else f"Ô {var}"
                        info += f"- {tile_name}: {len(domain)} vị trí có thể\n"
            
            # Thêm thông tin vào text widget
            self.info_text.setText(info) 