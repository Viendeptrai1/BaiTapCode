# 8-Puzzle Solver

Ứng dụng giải bài toán 8-Puzzle sử dụng PyQt5 với nhiều thuật toán tìm kiếm khác nhau.

## Giới thiệu

8-Puzzle là một trò chơi giải đố cổ điển, bao gồm một bảng 3x3 với 8 ô được đánh số và 1 ô trống. Mục tiêu là đưa các ô từ trạng thái ban đầu về trạng thái đích bằng cách di chuyển các ô liền kề vào ô trống.

Ứng dụng cung cấp giao diện đồ họa và triển khai nhiều thuật toán tìm kiếm khác nhau để giải bài toán này.

## Các thuật toán đã triển khai

### Tìm kiếm không có thông tin (Uninformed Search)
- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Uniform Cost Search (UCS)
- Iterative Deepening Search (IDS)

### Tìm kiếm có thông tin (Informed Search)
- A* Search (A*)
- IDA* Search (IDA*)
- Greedy Best-First Search

### Tìm kiếm cục bộ (Local Search)
- Hill Climbing Max
- Hill Climbing Random
- Simulated Annealing
- Genetic Algorithm

### Học tăng cường (Reinforcement Learning)
- Q-Learning
- Value Iteration

## Cấu trúc dự án

```
/
├── main.py                # Điểm truy cập chính của ứng dụng
├── make_model.py          # Script huấn luyện và kiểm tra mô hình RL
├── requirements.txt       # Các phụ thuộc cần thiết
├── models/                # Thư mục lưu trữ mô hình đã huấn luyện
└── src/                   # Thư mục mã nguồn
    ├── __init__.py        # Package mã nguồn
    ├── core/              # Module cho logic cốt lõi
    │   ├── __init__.py
    │   └── buzzle_logic.py            # Định nghĩa lớp Buzzle và các hàm xử lý trạng thái
    ├── algorithms/        # Module cho các thuật toán tìm kiếm
    │   ├── __init__.py
    │   ├── algorithm_manager.py       # Quản lý và cung cấp giao diện chung cho các thuật toán
    │   ├── search_algorithms.py       # Cài đặt các thuật toán tìm kiếm
    │   └── rl_algorithms.py           # Cài đặt các thuật toán học tăng cường
    ├── ui/                # Module cho giao diện người dùng
    │   ├── __init__.py
    │   ├── gui_components.py          # Các thành phần giao diện người dùng
    │   └── main_gui.py               # Cửa sổ chính của ứng dụng
    └── utils/             # Module cho các tiện ích
        └── __init__.py
```

## Cài đặt

1. Đảm bảo bạn đã cài đặt Python 3.6+
2. Cài đặt các thư viện cần thiết:

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
python main.py
```

## Huấn luyện và sử dụng mô hình RL

Để huấn luyện mô hình học tăng cường:

```bash
# Huấn luyện mô hình Q-Learning với 3000 episodes
python make_model.py --train --model q_learning --episodes 3000

# Huấn luyện mô hình Value Iteration với 500 lần lặp
python make_model.py --train --model value_iteration --iterations 500
```

Để kiểm tra mô hình trên một trạng thái cụ thể:

```bash
# Kiểm tra mô hình Q-Learning trên một trạng thái cụ thể
python make_model.py --test-specific --model q_learning --puzzle '0,1,4,6,5,8,2,3,7' --max-steps 1000

# Kiểm tra mô hình Value Iteration trên một trạng thái cụ thể
python make_model.py --test-specific --model value_iteration --puzzle '0,1,4,6,5,8,2,3,7' --max-steps 1000
```

## Hướng dẫn sử dụng

1. Khởi động ứng dụng
2. Nhập trạng thái ban đầu hoặc sử dụng nút "Random" để tạo trạng thái ngẫu nhiên
3. Chọn thuật toán bạn muốn sử dụng
4. Nhấn "Solve" để bắt đầu giải
5. Xem và điều hướng qua các bước giải trong Solution Navigator

## Giấy phép

Dự án này được phân phối dưới giấy phép MIT. 