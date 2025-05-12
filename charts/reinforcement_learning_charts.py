#!/usr/bin/env python3
"""
Script để tạo biểu đồ so sánh hiệu suất cho các thuật toán học tăng cường
(Reinforcement Learning) áp dụng vào bài toán 8-puzzle.
"""

import numpy as np
import matplotlib.pyplot as plt
import os

# Đảm bảo thư mục đầu ra tồn tại
os.makedirs('charts/output', exist_ok=True)

# Thiết lập style cho đồ thị
plt.style.use('ggplot')
plt.rcParams.update({
    'font.size': 12,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'figure.titlesize': 18,
    'figure.figsize': (12, 8)
})

# ----- 1. So sánh quá trình học của các thuật toán học tăng cường -----
def plot_rl_learning_curves():
    # Số tập huấn luyện
    episodes = np.arange(0, 10001, 1000)
    
    # Điểm trung bình đạt được qua các tập huấn luyện
    q_learning = [-200, -150, -90, -60, -40, -20, -15, -10, -8, -6, -5]
    value_iteration = [-200, -100, -40, -20, -10, -8, -6, -5, -4, -4, -4]
    
    fig, ax = plt.subplots()
    ax.plot(episodes, q_learning, 'o-', label='Q-Learning')
    ax.plot(episodes, value_iteration, 's-', label='Value Iteration')
    
    ax.set_title('Quá trình học của các thuật toán học tăng cường')
    ax.set_xlabel('Số tập huấn luyện')
    ax.set_ylabel('Điểm trung bình (reward)')
    ax.legend()
    ax.grid(True)
    
    plt.tight_layout()
    plt.savefig('charts/output/rl_learning_curves.png', dpi=300)
    plt.close()

# ----- 2. So sánh thời gian huấn luyện và thực thi -----
def plot_rl_training_execution_time():
    algorithms = ['Q-Learning', 'Value Iteration', 'SARSA', 'DQN']
    
    # Thời gian huấn luyện (s)
    training_time = [120, 60, 150, 300]
    # Thời gian thực thi sau khi học (ms)
    execution_time = [5, 5, 5, 8]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Biểu đồ thời gian huấn luyện
    bars1 = ax1.bar(algorithms, training_time, color='skyblue')
    ax1.set_title('Thời gian huấn luyện')
    ax1.set_xlabel('Thuật toán')
    ax1.set_ylabel('Thời gian (s)')
    
    # Thêm nhãn giá trị
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{int(height)}s',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom')
    
    # Biểu đồ thời gian thực thi
    bars2 = ax2.bar(algorithms, execution_time, color='lightgreen')
    ax2.set_title('Thời gian thực thi sau khi học')
    ax2.set_xlabel('Thuật toán')
    ax2.set_ylabel('Thời gian (ms)')
    
    # Thêm nhãn giá trị
    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'{int(height)}ms',
                     xy=(bar.get_x() + bar.get_width() / 2, height),
                     xytext=(0, 3),
                     textcoords="offset points",
                     ha='center', va='bottom')
    
    plt.suptitle('So sánh thời gian huấn luyện và thực thi của các thuật toán học tăng cường')
    plt.tight_layout()
    plt.savefig('charts/output/rl_training_execution_time.png', dpi=300)
    plt.close()

# ----- 3. So sánh chất lượng chính sách (policy) -----
def plot_rl_policy_quality():
    algorithms = ['Q-Learning', 'Value Iteration', 'SARSA', 'DQN']
    
    # Độ dài đường đi trung bình khi sử dụng chính sách đã học
    avg_path_length = [25, 24, 26, 23]
    # Tỷ lệ thành công (%)
    success_rate = [92, 95, 90, 98]
    # Điểm số trung bình
    avg_reward = [-23, -21, -25, -20]
    
    x = np.arange(len(algorithms))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Chuẩn hóa các giá trị để hiển thị trên cùng biểu đồ
    path_length_normalized = np.array(avg_path_length) / max(avg_path_length) * 10
    success_rate_normalized = np.array(success_rate) / 10
    reward_normalized = np.array(avg_reward) / min(avg_reward) * -5
    
    rects1 = ax.bar(x - width, path_length_normalized, width, label='Độ dài đường đi (chuẩn hóa)')
    rects2 = ax.bar(x, success_rate_normalized, width, label='Tỷ lệ thành công (%/10)')
    rects3 = ax.bar(x + width, reward_normalized, width, label='Điểm số (chuẩn hóa)')
    
    ax.set_title('Chất lượng chính sách của các thuật toán học tăng cường')
    ax.set_xlabel('Thuật toán')
    ax.set_ylabel('Giá trị chuẩn hóa')
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms)
    ax.legend()
    
    # Thêm nhãn giá trị thực tế (không chuẩn hóa)
    def add_labels(rects, values, suffix='', offset=0):
        for i, (rect, value) in enumerate(zip(rects, values)):
            ax.annotate(f'{value}{suffix}',
                       xy=(rect.get_x() + rect.get_width() / 2, rect.get_height() + offset),
                       xytext=(0, 3),
                       textcoords="offset points",
                       ha='center', va='bottom')
    
    add_labels(rects1, avg_path_length, ' bước', offset=0.2)
    add_labels(rects2, success_rate, '%', offset=0.2)
    add_labels(rects3, avg_reward, '', offset=0.2)
    
    plt.tight_layout()
    plt.savefig('charts/output/rl_policy_quality.png', dpi=300)
    plt.close()

# ----- 4. So sánh khả năng khám phá và khai thác -----
def plot_exploration_exploitation():
    # Tỷ lệ khám phá (epsilon) theo số tập huấn luyện
    episodes = np.array([0, 2000, 4000, 6000, 8000, 10000])
    
    # Tỷ lệ epsilon
    q_learning_epsilon = np.array([1.0, 0.8, 0.5, 0.3, 0.1, 0.05])
    sarsa_epsilon = np.array([1.0, 0.9, 0.7, 0.5, 0.3, 0.2])
    dqn_epsilon = np.array([1.0, 0.7, 0.3, 0.1, 0.05, 0.01])
    
    fig, ax = plt.subplots()
    
    ax.plot(episodes, q_learning_epsilon, 'o-', label='Q-Learning')
    ax.plot(episodes, sarsa_epsilon, 's-', label='SARSA')
    ax.plot(episodes, dqn_epsilon, '^-', label='DQN')
    
    ax.set_title('Thay đổi tỷ lệ khám phá (epsilon) trong quá trình huấn luyện')
    ax.set_xlabel('Số tập huấn luyện')
    ax.set_ylabel('Tỷ lệ khám phá (epsilon)')
    ax.legend()
    ax.grid(True)
    
    # Thêm vùng minh họa khám phá và khai thác
    ax.fill_between(episodes, 0.7, 1.0, color='lightblue', alpha=0.3, label='Khám phá nhiều')
    ax.fill_between(episodes, 0.0, 0.3, color='lightgreen', alpha=0.3, label='Khai thác nhiều')
    ax.legend(loc='upper right')
    
    plt.tight_layout()
    plt.savefig('charts/output/rl_exploration_exploitation.png', dpi=300)
    plt.close()

# ----- 5. So sánh khả năng mở rộng cho không gian trạng thái lớn -----
def plot_scalability():
    # Kích thước không gian trạng thái (puzzle size)
    puzzle_sizes = ['2x2', '3x3', '4x4']
    
    # Thời gian hội tụ (phút)
    q_learning = [5, 120, "Không hội tụ"]
    value_iteration = [2, 60, "Không hội tụ"]
    dqn = [10, 180, 600]
    
    # Chuyển đổi dữ liệu sang dạng số nơi có thể
    q_learning_plot = [5, 120, 1000]  # Giá trị giả định cho "không hội tụ"
    value_iteration_plot = [2, 60, 1000]  # Giá trị giả định cho "không hội tụ"
    dqn_plot = [10, 180, 600]
    
    x = np.arange(len(puzzle_sizes))
    width = 0.25
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    rects1 = ax.bar(x - width, q_learning_plot, width, label='Q-Learning')
    rects2 = ax.bar(x, value_iteration_plot, width, label='Value Iteration')
    rects3 = ax.bar(x + width, dqn_plot, width, label='DQN')
    
    ax.set_title('Khả năng mở rộng của các thuật toán học tăng cường')
    ax.set_xlabel('Kích thước puzzle')
    ax.set_ylabel('Thời gian hội tụ (phút)')
    ax.set_xticks(x)
    ax.set_xticklabels(puzzle_sizes)
    ax.set_yticks([0, 60, 120, 180, 600, 1000])
    ax.set_yticklabels(['0', '60', '120', '180', '600', 'Không hội tụ'])
    ax.legend()
    
    # Thêm nhãn giá trị
    def add_value_labels(rects, values):
        for i, (rect, value) in enumerate(zip(rects, values)):
            height = rect.get_height()
            if isinstance(value, str):
                ax.text(rect.get_x() + rect.get_width()/2., height * 0.9,
                        value,
                        ha='center', va='bottom', rotation=0)
            else:
                ax.text(rect.get_x() + rect.get_width()/2., height * 0.9,
                        f'{value} phút',
                        ha='center', va='bottom', rotation=0)
    
    add_value_labels(rects1, q_learning)
    add_value_labels(rects2, value_iteration)
    add_value_labels(rects3, dqn)
    
    plt.tight_layout()
    plt.savefig('charts/output/rl_scalability.png', dpi=300)
    plt.close()

# ----- 6. Radar Chart tổng quan các thuật toán học tăng cường -----
def plot_rl_radar():
    algorithms = ['Q-Learning', 'Value Iteration', 'SARSA', 'DQN']
    
    # Các tiêu chí đánh giá (thang điểm 1-10)
    # [Tốc độ học, Chất lượng chính sách, Hiệu quả bộ nhớ, Khả năng mở rộng, Đơn giản cài đặt]
    q_learning = [6, 7, 8, 5, 9]
    value_iteration = [8, 8, 7, 4, 8]
    sarsa = [5, 7, 8, 5, 8]
    dqn = [4, 9, 5, 9, 4]
    
    # Labels cho các tiêu chí
    categories = ['Tốc độ học', 'Chất lượng\nchính sách', 'Hiệu quả\nbộ nhớ', 
                  'Khả năng\nmở rộng', 'Đơn giản\ncài đặt']
    
    # Số lượng tiêu chí
    N = len(categories)
    
    # Góc của mỗi trục
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Khép kín đồ thị
    
    # Dữ liệu cho từng thuật toán
    data = [q_learning, value_iteration, sarsa, dqn]
    for i in range(len(data)):
        data[i] = data[i] + data[i][:1]  # Khép kín dữ liệu
    
    # Tạo hình và các trục
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Màu sắc cho từng thuật toán
    colors = ['#FF9999', '#66B2FF', '#99FF99', '#FFCC99']
    
    # Vẽ các đường biểu diễn cho từng thuật toán
    for i, alg in enumerate(algorithms):
        ax.plot(angles, data[i], color=colors[i], linewidth=2, linestyle='solid', label=alg)
        ax.fill(angles, data[i], color=colors[i], alpha=0.25)
    
    # Thiết lập các thuộc tính của đồ thị
    ax.set_theta_offset(np.pi / 2)  # Bắt đầu từ đỉnh
    ax.set_theta_direction(-1)  # Theo chiều kim đồng hồ
    
    # Đặt nhãn cho các trục
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    
    # Đặt nhãn cho các đường đồng tâm (1-10)
    ax.set_yticks(np.arange(2, 11, 2))
    ax.set_ylim(0, 10)
    
    # Thêm tiêu đề và chú thích
    plt.title('So sánh tổng quan các thuật toán học tăng cường', size=20, y=1.1)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4)
    
    plt.tight_layout()
    plt.savefig('charts/output/rl_radar.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    # Tạo tất cả các biểu đồ
    plot_rl_learning_curves()
    plot_rl_training_execution_time()
    plot_rl_policy_quality()
    plot_exploration_exploitation()
    plot_scalability()
    plot_rl_radar()
    
    print("Đã tạo các biểu đồ học tăng cường trong thư mục charts/output/") 