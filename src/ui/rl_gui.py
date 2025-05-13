from PyQt5.QtWidgets import (QWidget, QGridLayout, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLabel, QTextEdit, QRadioButton,
                           QButtonGroup, QDoubleSpinBox, QSpinBox, QFrame,
                           QGroupBox, QSplitter, QProgressBar, QTabWidget, QCheckBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import networkx as nx

class RLConfigPanel(QWidget):
    """Panel cấu hình cho thuật toán học tăng cường (RL)."""
    
    def __init__(self, parent, on_solve_callback):
        super().__init__(parent)
        self.parent = parent
        self.on_solve_callback = on_solve_callback
        
        # Tạo giao diện
        self._create_widgets()
        
    def _create_widgets(self):
        """Tạo các thành phần giao diện."""
        main_layout = QVBoxLayout(self)
        
        # Tiêu đề
        title_label = QLabel("Cấu hình Reinforcement Learning")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        main_layout.addWidget(title_label)
        
        # --- Tham số RL ---
        params_group = QGroupBox("Tham số")
        params_layout = QGridLayout()
        
        # Learning rate (alpha)
        params_layout.addWidget(QLabel("Tỷ lệ học tập (α):"), 0, 0)
        self.alpha_spin = QDoubleSpinBox()
        self.alpha_spin.setRange(0.01, 1.0)
        self.alpha_spin.setSingleStep(0.05)
        self.alpha_spin.setValue(0.1)
        params_layout.addWidget(self.alpha_spin, 0, 1)
        
        # Discount factor (gamma)
        params_layout.addWidget(QLabel("Hệ số giảm (γ):"), 1, 0)
        self.gamma_spin = QDoubleSpinBox()
        self.gamma_spin.setRange(0.1, 0.99)
        self.gamma_spin.setSingleStep(0.05)
        self.gamma_spin.setValue(0.95)
        params_layout.addWidget(self.gamma_spin, 1, 1)
        
        # Exploration rate (epsilon)
        params_layout.addWidget(QLabel("Tỷ lệ khám phá (ε):"), 2, 0)
        self.epsilon_spin = QDoubleSpinBox()
        self.epsilon_spin.setRange(0.01, 0.5)
        self.epsilon_spin.setSingleStep(0.05)
        self.epsilon_spin.setValue(0.2)
        params_layout.addWidget(self.epsilon_spin, 2, 1)
        
        # Alpha decay rate
        params_layout.addWidget(QLabel("Tỷ lệ giảm α:"), 3, 0)
        self.alpha_decay_spin = QDoubleSpinBox()
        self.alpha_decay_spin.setRange(0.8, 0.999)
        self.alpha_decay_spin.setSingleStep(0.005)
        self.alpha_decay_spin.setValue(0.995)
        params_layout.addWidget(self.alpha_decay_spin, 3, 1)
        
        # Epsilon decay rate
        params_layout.addWidget(QLabel("Tỷ lệ giảm ε:"), 4, 0)
        self.epsilon_decay_spin = QDoubleSpinBox()
        self.epsilon_decay_spin.setRange(0.8, 0.999)
        self.epsilon_decay_spin.setSingleStep(0.005)
        self.epsilon_decay_spin.setValue(0.99)
        params_layout.addWidget(self.epsilon_decay_spin, 4, 1)
        
        # Episodes
        params_layout.addWidget(QLabel("Số episodes:"), 5, 0)
        self.episodes_spin = QSpinBox()
        self.episodes_spin.setRange(100, 10000)
        self.episodes_spin.setSingleStep(100)
        self.episodes_spin.setValue(1000)
        params_layout.addWidget(self.episodes_spin, 5, 1)
        
        # Experience replay
        params_layout.addWidget(QLabel("Experience Replay:"), 6, 0)
        self.experience_replay_check = QCheckBox("Sử dụng")
        self.experience_replay_check.setChecked(True)
        params_layout.addWidget(self.experience_replay_check, 6, 1)
        
        params_group.setLayout(params_layout)
        main_layout.addWidget(params_group)
        
        # --- Chọn thuật toán ---
        algo_group = QGroupBox("Thuật toán")
        algo_layout = QVBoxLayout()
        
        self.algo_button_group = QButtonGroup(self)
        
        # Q-Learning
        self.q_learning_radio = QRadioButton("Q-Learning")
        self.q_learning_radio.setChecked(True)
        self.algo_button_group.addButton(self.q_learning_radio)
        algo_layout.addWidget(self.q_learning_radio)
        
        # Value Iteration
        self.value_iteration_radio = QRadioButton("Value Iteration")
        self.algo_button_group.addButton(self.value_iteration_radio)
        algo_layout.addWidget(self.value_iteration_radio)
        
        # Thêm nút train và solve
        train_solve_layout = QHBoxLayout()
        
        self.train_button = QPushButton("Huấn luyện")
        self.train_button.clicked.connect(self._on_train)
        train_solve_layout.addWidget(self.train_button)
        
        self.solve_button = QPushButton("Giải")
        self.solve_button.clicked.connect(self._on_solve)
        train_solve_layout.addWidget(self.solve_button)
        
        algo_layout.addLayout(train_solve_layout)
        algo_group.setLayout(algo_layout)
        main_layout.addWidget(algo_group)
        
        # --- Tiến trình ---
        progress_group = QGroupBox("Tiến trình")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Sẵn sàng")
        progress_layout.addWidget(self.status_label)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Thêm khoảng trống co giãn ở cuối để đẩy các widget lên trên
        main_layout.addStretch()
        
        # Thêm mô tả thuật toán
        description_group = QGroupBox("Mô tả thuật toán")
        description_layout = QVBoxLayout()
        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMinimumHeight(150)
        description_layout.addWidget(self.description_text)
        description_group.setLayout(description_layout)
        main_layout.addWidget(description_group)
        
        # Hiển thị mô tả mặc định
        self._update_algorithm_description()
        
        # Kết nối sự kiện thay đổi thuật toán
        self.algo_button_group.buttonClicked.connect(self._update_algorithm_description)
    
    def _update_algorithm_description(self):
        """Cập nhật mô tả thuật toán dựa trên radio button được chọn."""
        if self.q_learning_radio.isChecked():
            description = """
Q-Learning là một thuật toán học tăng cường không cần mô hình (model-free).

Công thức cập nhật Q:
Q(s,a) = Q(s,a) + α * [R + γ * max_a' Q(s',a') - Q(s,a)]

trong đó:
- s, a: Trạng thái và hành động hiện tại
- s', a': Trạng thái tiếp theo và các hành động có thể từ đó
- α (alpha): Tỷ lệ học tập, quyết định mức độ thay thế thông tin cũ
- γ (gamma): Hệ số giảm, quyết định tầm quan trọng của phần thưởng tương lai
- R: Phần thưởng nhận được từ hành động a tại trạng thái s
- max_a' Q(s',a'): Giá trị Q tối đa có thể đạt được từ trạng thái tiếp theo

Quá trình:
1. Khởi tạo bảng Q với giá trị 0 cho tất cả cặp (trạng thái, hành động)
2. Chọn hành động bằng chiến lược epsilon-greedy
3. Thực hiện hành động, quan sát phần thưởng và trạng thái tiếp theo
4. Cập nhật giá trị Q sử dụng công thức trên
5. Lặp lại cho đến khi hội tụ
"""
        else:  # Value Iteration
            description = """
Value Iteration là một thuật toán quy hoạch động giải bài toán MDP.

Công thức cập nhật Utility:
U(s) = max_a [R(s,a) + γ * Σ_s' P(s'|s,a) * U(s')]

trong đó:
- s: Trạng thái hiện tại
- a: Hành động có thể từ trạng thái s
- R(s,a): Phần thưởng trung bình khi thực hiện hành động a tại trạng thái s
- γ (gamma): Hệ số giảm, quyết định tầm quan trọng của phần thưởng tương lai
- P(s'|s,a): Xác suất chuyển tiếp từ s sang s' khi thực hiện hành động a
- U(s'): Giá trị utility của trạng thái tiếp theo s'

Quá trình:
1. Khởi tạo U(s) = 0 cho tất cả trạng thái (ngoại trừ trạng thái đích)
2. Lặp lại đến khi hội tụ (thay đổi giá trị U nhỏ hơn ngưỡng):
   - Đối với mỗi trạng thái s, cập nhật U(s) sử dụng công thức trên
3. Trích xuất chính sách π(s) = argmax_a [R(s,a) + γ * Σ_s' P(s'|s,a) * U(s')]
"""
        self.description_text.setText(description)
    
    def _on_train(self):
        """Xử lý khi người dùng nhấn nút Train."""
        algo_key = "q_learning" if self.q_learning_radio.isChecked() else "value_iteration"
        
        # Lấy các tham số
        params = {
            "alpha": self.alpha_spin.value(),
            "gamma": self.gamma_spin.value(),
            "epsilon": self.epsilon_spin.value(),
            "episodes": self.episodes_spin.value(),
            "alpha_decay": self.alpha_decay_spin.value(),
            "epsilon_decay": self.epsilon_decay_spin.value(),
            "use_experience_replay": self.experience_replay_check.isChecked()
        }
        
        # Cập nhật giao diện
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Đang huấn luyện {algo_key}...")
        
        # Gọi callback cho quá trình huấn luyện
        self.on_solve_callback(algo_key, None, is_training=True, params=params)
    
    def _on_solve(self):
        """Xử lý khi người dùng nhấn nút Solve."""
        algo_key = "q_learning" if self.q_learning_radio.isChecked() else "value_iteration"
        
        # Cập nhật giao diện
        self.progress_bar.setVisible(True)
        self.status_label.setText(f"Đang giải với {algo_key}...")
        
        # Gọi callback cho quá trình giải
        self.on_solve_callback(algo_key, None, is_training=False)
    
    def update_training_status(self, is_complete, stats=None):
        """Cập nhật trạng thái huấn luyện."""
        self.progress_bar.setVisible(not is_complete)
        
        if is_complete:
            algo_name = "Q-Learning" if self.q_learning_radio.isChecked() else "Value Iteration"
            self.status_label.setText(f"Huấn luyện {algo_name} hoàn tất")
            
            if stats:
                # Hiển thị thống kê
                if 'training_time' in stats:
                    training_time = f"{stats['training_time']:.2f}"
                    self.status_label.setText(f"Huấn luyện hoàn tất trong {training_time}s")
    
    def update_solving_status(self, is_complete, stats=None):
        """Cập nhật trạng thái giải."""
        self.progress_bar.setVisible(not is_complete)
        
        if is_complete:
            algo_name = "Q-Learning" if self.q_learning_radio.isChecked() else "Value Iteration"
            
            if stats and 'steps' in stats:
                self.status_label.setText(f"Đã giải trong {stats['steps']} bước")
            else:
                self.status_label.setText(f"Đã giải với {algo_name}")

class StateGraphVisualization(QWidget):
    """Widget để hiển thị đồ thị trạng thái và giá trị Q/Utility."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Tạo layout chính
        layout = QVBoxLayout(self)
        
        # Tạo figure cho matplotlib
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(350)
        layout.addWidget(self.canvas)
        
        # Tạo label mô tả
        self.description_label = QLabel("Đồ thị trạng thái và giá trị")
        layout.addWidget(self.description_label)
        
        # Tạo một nút để làm mới biểu đồ
        self.refresh_button = QPushButton("Làm mới biểu đồ")
        self.refresh_button.clicked.connect(self.refresh_visualization)
        layout.addWidget(self.refresh_button)
        
        # Khởi tạo đồ thị trống
        self.graph = nx.DiGraph()
        self.utilities = {}
        self.selected_states = []
        
    def refresh_visualization(self):
        """Làm mới biểu đồ."""
        self.update_graph_visualization()
    
    def set_utilities(self, utilities, states_to_show=None):
        """
        Đặt các giá trị utility để hiển thị.
        
        Parameters:
        - utilities: Dict mapping từ state_tuple đến giá trị utility
        - states_to_show: Danh sách các state_tuple cần hiển thị (nếu None, hiển thị tất cả)
        """
        self.utilities = utilities
        
        if states_to_show is None:
            # Nếu không có danh sách cụ thể, lấy ngẫu nhiên một số trạng thái (tối đa 10)
            all_states = list(utilities.keys())
            if len(all_states) > 10:
                self.selected_states = np.random.choice(all_states, 10, replace=False)
            else:
                self.selected_states = all_states
        else:
            self.selected_states = states_to_show
            
        # Cập nhật đồ thị
        self.update_graph()
        
    def update_graph(self):
        """Cập nhật đồ thị dựa trên các trạng thái đã chọn và các giá trị utility."""
        # Xóa đồ thị cũ
        self.graph.clear()
        
        # Thêm các nút và cạnh
        for state in self.selected_states:
            # Chuyển đổi state tuple thành matrix để dễ hiển thị
            state_matrix = [list(row) for row in state]
            
            # Chuyển đổi matrix thành string để hiển thị
            state_str = '\n'.join([' '.join(map(str, row)) for row in state_matrix])
            
            # Lấy giá trị utility
            utility = self.utilities.get(state, 0)
            
            # Thêm nút với thuộc tính utility
            self.graph.add_node(state, label=state_str, utility=utility)
            
        # Cập nhật biểu đồ
        self.update_graph_visualization()
    
    def update_graph_visualization(self):
        """Cập nhật biểu đồ visualization."""
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if not self.graph.nodes:
            ax.text(0.5, 0.5, "Chưa có dữ liệu để hiển thị", 
                   horizontalalignment='center', verticalalignment='center')
            self.canvas.draw()
            return
        
        # Tạo layout cho đồ thị
        pos = nx.spring_layout(self.graph)
        
        # Lấy giá trị utility cho colormap
        utilities = [data.get('utility', 0) for _, data in self.graph.nodes(data=True)]
        
        # Vẽ các nút với màu dựa trên giá trị utility
        nx.draw_networkx_nodes(self.graph, pos, 
                              node_color=utilities, 
                              cmap=plt.cm.YlOrRd, 
                              node_size=500,
                              alpha=0.8,
                              ax=ax)
        
        # Vẽ các cạnh
        nx.draw_networkx_edges(self.graph, pos, arrows=True, ax=ax)
        
        # Vẽ nhãn nút (state string)
        labels = {node: data.get('label', '') for node, data in self.graph.nodes(data=True)}
        nx.draw_networkx_labels(self.graph, pos, labels=labels, font_size=8, ax=ax)
        
        # Thêm colorbar
        sm = plt.cm.ScalarMappable(cmap=plt.cm.YlOrRd, norm=plt.Normalize(min(utilities), max(utilities)))
        sm.set_array([])
        cbar = self.figure.colorbar(sm, ax=ax)
        cbar.set_label('Giá trị Utility/Q')
        
        # Tắt các trục
        ax.set_axis_off()
        
        # Cập nhật canvas
        self.canvas.draw()

class TrainingStatsVisualization(QWidget):
    """Widget để hiển thị thống kê huấn luyện."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Tạo layout chính
        layout = QVBoxLayout(self)
        
        # Tạo figure cho matplotlib
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(350)
        layout.addWidget(self.canvas)
        
        # Tạo label mô tả
        self.description_label = QLabel("Thống kê huấn luyện")
        layout.addWidget(self.description_label)
        
        # Khởi tạo dữ liệu trống
        self.training_stats = None
        
    def set_training_stats(self, stats):
        """Đặt thống kê huấn luyện để hiển thị."""
        self.training_stats = stats
        self.update_visualization()
        
    def update_visualization(self):
        """Cập nhật biểu đồ thống kê."""
        self.figure.clear()
        
        if not self.training_stats:
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "Chưa có dữ liệu huấn luyện", 
                   horizontalalignment='center', verticalalignment='center')
            self.canvas.draw()
            return
        
        # Tạo subplot grid
        gs = self.figure.add_gridspec(2, 2)
        
        # Q-Learning specific stats
        if 'episode_lengths' in self.training_stats and 'episode_rewards' in self.training_stats:
            # Plot episode lengths
            ax1 = self.figure.add_subplot(gs[0, 0])
            episode_lengths = self.training_stats['episode_lengths']
            ax1.plot(range(1, len(episode_lengths) + 1), episode_lengths)
            ax1.set_title('Độ dài Episode')
            ax1.set_xlabel('Episode')
            ax1.set_ylabel('Số bước')
            
            # Plot episode rewards
            ax2 = self.figure.add_subplot(gs[0, 1])
            episode_rewards = self.training_stats['episode_rewards']
            ax2.plot(range(1, len(episode_rewards) + 1), episode_rewards)
            ax2.set_title('Phần thưởng Episode')
            ax2.set_xlabel('Episode')
            ax2.set_ylabel('Phần thưởng')
            
            # Plot learning rate and exploration rate decay
            if 'alpha_history' in self.training_stats and 'epsilon_history' in self.training_stats:
                ax3 = self.figure.add_subplot(gs[1, 0])
                alpha_history = self.training_stats['alpha_history']
                epsilon_history = self.training_stats['epsilon_history']
                
                episodes = range(1, len(alpha_history) + 1)
                ax3.plot(episodes, alpha_history, 'b-', label='Alpha')
                ax3.set_ylabel('Alpha', color='b')
                ax3.tick_params(axis='y', labelcolor='b')
                
                ax3_twin = ax3.twinx()
                ax3_twin.plot(episodes, epsilon_history, 'r-', label='Epsilon')
                ax3_twin.set_ylabel('Epsilon', color='r')
                ax3_twin.tick_params(axis='y', labelcolor='r')
                
                ax3.set_title('Tỷ lệ học tập & khám phá')
                ax3.set_xlabel('Episode')
                
                lines1, labels1 = ax3.get_legend_handles_labels()
                lines2, labels2 = ax3_twin.get_legend_handles_labels()
                ax3.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
            
            # Plot steps to goal (if available)
            elif 'steps_to_goal' in self.training_stats and self.training_stats['steps_to_goal']:
                ax3 = self.figure.add_subplot(gs[1, 0])
                steps_to_goal = self.training_stats['steps_to_goal']
                ax3.plot(range(1, len(steps_to_goal) + 1), steps_to_goal)
                ax3.set_title('Số bước đến đích')
                ax3.set_xlabel('Lần tìm thấy đích')
                ax3.set_ylabel('Số bước')
        
        # Value Iteration specific stats
        elif 'delta_history' in self.training_stats:
            # Plot delta history
            ax1 = self.figure.add_subplot(gs[0, 0])
            delta_history = self.training_stats['delta_history']
            ax1.plot(range(1, len(delta_history) + 1), delta_history)
            ax1.set_title('Lịch sử Delta')
            ax1.set_xlabel('Lần lặp')
            ax1.set_ylabel('Delta')
            
            # Plot semi-log delta history
            ax2 = self.figure.add_subplot(gs[0, 1])
            ax2.semilogy(range(1, len(delta_history) + 1), delta_history)
            ax2.set_title('Lịch sử Delta (log scale)')
            ax2.set_xlabel('Lần lặp')
            ax2.set_ylabel('Log(Delta)')
            
        # General stats as text
        ax_text = self.figure.add_subplot(gs[1, 1])
        stats_text = ""
        
        if 'training_time' in self.training_stats:
            stats_text += f"Thời gian huấn luyện: {self.training_stats['training_time']:.2f}s\n"
        
        if 'episodes' in self.training_stats:
            stats_text += f"Số episodes: {self.training_stats['episodes']}\n"
            
        if 'unique_states' in self.training_stats:
            stats_text += f"Số trạng thái duy nhất: {self.training_stats['unique_states']}\n"
            
        if 'q_table_size' in self.training_stats:
            stats_text += f"Kích thước bảng Q: {self.training_stats['q_table_size']}\n"
        
        if 'final_alpha' in self.training_stats:
            stats_text += f"Alpha cuối: {self.training_stats['final_alpha']:.4f}\n"
            
        if 'final_epsilon' in self.training_stats:
            stats_text += f"Epsilon cuối: {self.training_stats['final_epsilon']:.4f}\n"
            
        if 'iterations' in self.training_stats:
            stats_text += f"Số lần lặp: {self.training_stats['iterations']}\n"
            
        if 'states_explored' in self.training_stats:
            stats_text += f"Số trạng thái đã khám phá: {self.training_stats['states_explored']}\n"
            
        if 'convergence' in self.training_stats:
            conv_text = "Đã" if self.training_stats['convergence'] else "Chưa"
            stats_text += f"Hội tụ: {conv_text}\n"
            
        ax_text.text(0.5, 0.5, stats_text, 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax_text.transAxes)
        ax_text.set_title('Thống kê tổng hợp')
        ax_text.axis('off')
        
        self.figure.tight_layout()
        self.canvas.draw()

class RLMainPanel(QWidget):
    """Panel chính cho tab học tăng cường."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # Tạo layout chính
        main_layout = QHBoxLayout(self)
        
        # --- Panel trái: Cấu hình và điều khiển ---
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Panel cấu hình RL
        self.rl_config_panel = RLConfigPanel(self, self.on_solve_or_train)
        left_layout.addWidget(self.rl_config_panel)
        
        # --- Panel phải: Visualization ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Tạo tab widget cho các loại visualization
        self.viz_tabs = QTabWidget()
        
        # Tab cho đồ thị trạng thái
        self.state_graph_viz = StateGraphVisualization(self)
        self.viz_tabs.addTab(self.state_graph_viz, "Đồ thị trạng thái")
        
        # Tab cho thống kê huấn luyện
        self.training_stats_viz = TrainingStatsVisualization(self)
        self.viz_tabs.addTab(self.training_stats_viz, "Thống kê huấn luyện")
        
        right_layout.addWidget(self.viz_tabs)
        
        # Thêm các panel vào layout chính
        main_layout.addWidget(left_panel, 1)  # 1/3 width
        main_layout.addWidget(right_panel, 2)  # 2/3 width
    
    def on_solve_or_train(self, algorithm_key, puzzle_state, is_training=False, params=None):
        """
        Xử lý khi người dùng nhấn nút Train hoặc Solve.
        
        Parameters:
        - algorithm_key: Key của thuật toán ("q_learning" hoặc "value_iteration")
        - puzzle_state: Trạng thái puzzle ban đầu (có thể None nếu dùng trạng thái mặc định)
        - is_training: Boolean cho biết đây là quá trình huấn luyện hay giải
        - params: Dict các tham số nếu cần
        """
        # Chuyển dữ liệu sang parent (main_gui) để xử lý
        if hasattr(self.parent, 'start_rl_solving'):
            self.parent.start_rl_solving(algorithm_key, puzzle_state, is_training, params)
    
    def update_training_result(self, is_complete, stats=None, utilities=None):
        """
        Cập nhật kết quả huấn luyện.
        
        Parameters:
        - is_complete: Boolean cho biết quá trình huấn luyện đã hoàn tất chưa
        - stats: Dict thống kê huấn luyện
        - utilities: Dict giá trị utility cho mỗi trạng thái
        """
        # Cập nhật trạng thái huấn luyện trên config panel
        self.rl_config_panel.update_training_status(is_complete, stats)
        
        # Cập nhật visualization nếu có dữ liệu
        if stats:
            self.training_stats_viz.set_training_stats(stats)
            self.viz_tabs.setCurrentWidget(self.training_stats_viz)
            
        if utilities:
            self.state_graph_viz.set_utilities(utilities)
    
    def update_solving_result(self, is_complete, path=None, stats=None):
        """
        Cập nhật kết quả giải.
        
        Parameters:
        - is_complete: Boolean cho biết quá trình giải đã hoàn tất chưa
        - path: Đường đi giải pháp (list các tuple (move, state_data))
        - stats: Dict thống kê giải
        """
        # Cập nhật trạng thái giải trên config panel
        self.rl_config_panel.update_solving_status(is_complete, stats)
        
        # Chuyển đến tab thống kê
        self.viz_tabs.setCurrentWidget(self.training_stats_viz) 