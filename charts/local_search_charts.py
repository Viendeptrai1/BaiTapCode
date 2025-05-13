#!/usr/bin/env python3
"""
Script để tạo biểu đồ so sánh hiệu suất cho các thuật toán tìm kiếm địa phương
áp dụng vào bài toán 8-puzzle.
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

# ----- 1. So sánh tỷ lệ thành công của các thuật toán tìm kiếm địa phương -----
def plot_local_search_success_rate():
    algorithms = ['Hill Climbing', 'Random-restart HC', 'Simulated Annealing', 'Genetic Algorithm']
    
    # Tỷ lệ thành công (%) cho các bài toán với độ khó khác nhau
    easy_problems = np.array([85, 95, 98, 98])  # Các bài toán đơn giản (2-8 bước)
    medium_problems = np.array([40, 75, 85, 90])  # Các bài toán trung bình (10-15 bước)
    hard_problems = np.array([10, 50, 70, 75])  # Các bài toán khó (20+ bước)
    
    x = np.arange(len(algorithms))
    width = 0.25
    
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, easy_problems, width, label='Đơn giản (2-8 bước)')
    rects2 = ax.bar(x, medium_problems, width, label='Trung bình (10-15 bước)')
    rects3 = ax.bar(x + width, hard_problems, width, label='Khó (20+ bước)')
    
    ax.set_title('Tỷ lệ thành công của các thuật toán tìm kiếm địa phương')
    ax.set_xlabel('Thuật toán')
    ax.set_ylabel('Tỷ lệ thành công (%)')
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms)
    ax.set_ylim(0, 100)
    ax.legend()
    
    # Thêm nhãn giá trị
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{int(height)}%',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    
    fig.tight_layout()
    plt.savefig('charts/output/local_search_success_rate.png', dpi=300)
    plt.close()

# ----- 2. So sánh thời gian thực thi của các thuật toán tìm kiếm địa phương -----
def plot_local_search_time():
    algorithms = ['Hill Climbing', 'Random-restart HC', 'Simulated Annealing', 'Genetic Algorithm']
    
    # Thời gian thực thi (ms) cho các bài toán với độ khó khác nhau
    easy_problems = np.array([10, 30, 50, 100])  # Các bài toán đơn giản
    medium_problems = np.array([50, 150, 200, 500])  # Các bài toán trung bình
    hard_problems = np.array([100, 300, 500, 1200])  # Các bài toán khó
    
    x = np.arange(len(algorithms))
    width = 0.25
    
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, easy_problems, width, label='Đơn giản (2-8 bước)')
    rects2 = ax.bar(x, medium_problems, width, label='Trung bình (10-15 bước)')
    rects3 = ax.bar(x + width, hard_problems, width, label='Khó (20+ bước)')
    
    ax.set_title('Thời gian thực thi của các thuật toán tìm kiếm địa phương')
    ax.set_xlabel('Thuật toán')
    ax.set_ylabel('Thời gian (ms)')
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms)
    ax.legend()
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{int(height)}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    
    fig.tight_layout()
    plt.savefig('charts/output/local_search_time.png', dpi=300)
    plt.close()

# ----- 3. So sánh chất lượng lời giải của các thuật toán tìm kiếm địa phương -----
def plot_local_search_solution_quality():
    algorithms = ['Hill Climbing', 'Random-restart HC', 'Simulated Annealing', 'Genetic Algorithm']
    
    # Chất lượng lời giải (số bước trung bình so với tối ưu)
    # Ví dụ: 1.0 = tối ưu, 1.2 = 20% dài hơn tối ưu
    solution_quality = np.array([1.5, 1.25, 1.1, 1.15])
    
    fig, ax = plt.subplots()
    bars = ax.bar(algorithms, solution_quality, color='skyblue')
    
    ax.set_title('Chất lượng lời giải của các thuật toán tìm kiếm địa phương')
    ax.set_xlabel('Thuật toán')
    ax.set_ylabel('Tỷ lệ so với lời giải tối ưu')
    ax.set_ylim(1.0, 2.0)
    
    # Thêm đường tham chiếu cho lời giải tối ưu
    ax.axhline(y=1.0, color='green', linestyle='-', alpha=0.7, linewidth=2)
    ax.text(0, 1.01, 'Tối ưu', color='green', fontweight='bold')
    
    # Thêm nhãn giá trị
    for bar in bars:
        height = bar.get_height()
        ax.annotate(f'{height:.2f}x',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom')
    
    fig.tight_layout()
    plt.savefig('charts/output/local_search_solution_quality.png', dpi=300)
    plt.close()

# ----- 4. So sánh số lần đánh giá trạng thái của các thuật toán tìm kiếm địa phương -----
def plot_local_search_evaluations():
    algorithms = ['Hill Climbing', 'Random-restart HC', 'Simulated Annealing', 'Genetic Algorithm']
    
    # Số lượng đánh giá trạng thái trung bình
    easy_evaluations = np.array([20, 100, 150, 500])
    medium_evaluations = np.array([100, 500, 800, 2000])
    hard_evaluations = np.array([200, 1000, 2000, 5000])
    
    x = np.arange(len(algorithms))
    width = 0.25
    
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width, easy_evaluations, width, label='Đơn giản (2-8 bước)')
    rects2 = ax.bar(x, medium_evaluations, width, label='Trung bình (10-15 bước)')
    rects3 = ax.bar(x + width, hard_evaluations, width, label='Khó (20+ bước)')
    
    ax.set_title('Số lần đánh giá trạng thái của các thuật toán tìm kiếm địa phương')
    ax.set_xlabel('Thuật toán')
    ax.set_ylabel('Số lần đánh giá')
    ax.set_xticks(x)
    ax.set_xticklabels(algorithms)
    ax.set_yscale('log')
    ax.legend()
    
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{int(height)}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),
                        textcoords="offset points",
                        ha='center', va='bottom')
    
    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    
    fig.tight_layout()
    plt.savefig('charts/output/local_search_evaluations.png', dpi=300)
    plt.close()

# ----- 5. So sánh radar chart tổng quan các thuật toán tìm kiếm địa phương -----
def plot_local_search_radar():
    algorithms = ['Hill Climbing', 'Random-restart HC', 'Simulated Annealing', 'Genetic Algorithm']
    
    # Các tiêu chí đánh giá (thang điểm 1-10)
    # [Tốc độ, Tỷ lệ thành công, Chất lượng lời giải, Khả năng thoát cực tiểu cục bộ, Đơn giản cài đặt]
    hill_climbing = [9, 3, 4, 1, 10]
    random_restart = [7, 6, 6, 6, 8]
    simulated_annealing = [6, 8, 9, 9, 6]
    genetic_algorithm = [4, 9, 8, 9, 3]
    
    # Labels cho các tiêu chí
    categories = ['Tốc độ', 'Tỷ lệ thành công', 'Chất lượng\nlời giải', 
                  'Khả năng thoát\ncực tiểu cục bộ', 'Đơn giản\ncài đặt']
    
    # Số lượng tiêu chí
    N = len(categories)
    
    # Góc của mỗi trục
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Khép kín đồ thị
    
    # Dữ liệu cho từng thuật toán
    data = [hill_climbing, random_restart, simulated_annealing, genetic_algorithm]
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
    plt.title('So sánh tổng quan các thuật toán tìm kiếm địa phương', size=20, y=1.1)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=4)
    
    plt.tight_layout()
    plt.savefig('charts/output/local_search_radar.png', dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    # Tạo tất cả các biểu đồ
    plot_local_search_success_rate()
    plot_local_search_time()
    plot_local_search_solution_quality()
    plot_local_search_evaluations()
    plot_local_search_radar()
    
    print("Đã tạo các biểu đồ tìm kiếm địa phương trong thư mục charts/output/") 