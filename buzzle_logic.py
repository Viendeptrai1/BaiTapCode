import random

class Buzzle:
    def __init__(self, data=None):
        if data is None:
            self.data = [[1, 2, 3],
                        [4, 5, 6],
                        [7, 8, 0]]
        else:
            # Đảm bảo data là một bản sao độc lập
            self.data = [list(row) for row in data]

    def is_goal(self, goal_state=None):
        if goal_state is None:
            goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
        return self.data == goal_state

    def print_state(self):
        print("Trang thai hien tai: ")
        for i in range(3):
            for j in range(3):
                print(self.data[i][j], end=" ")
            print("\n")

    def entry_state(self):
        """Get puzzle state from user input with error handling"""
        print("Nhập trạng thái (0-8, mỗi số xuất hiện đúng 1 lần, 0 đại diện cho ô trống):")
        print("Chọn cách nhập:")
        print("1. Nhập thủ công từng ô")
        print("2. Sử dụng trạng thái mẫu (để kiểm thử)")

        choice = input("Lựa chọn của bạn (1/2): ").strip()

        if choice == "2":
            # Sử dụng một trạng thái mẫu dễ giải
            self.data = [[1, 2, 3], [4, 0, 6], [7, 5, 8]]
            return

        # Danh sách để kiểm tra tính hợp lệ
        used_numbers = set()
        new_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]] # Tạo bảng mới

        for i in range(3):
            for j in range(3):
                while True:
                    try:
                        x = int(input(f"Nhập giá trị cho ô [{i},{j}] (0-8): "))
                        if 0 <= x <= 8 and x not in used_numbers:
                            new_data[i][j] = x
                            used_numbers.add(x)
                            break
                        else:
                            if x in used_numbers:
                                print(f"Lỗi: Số {x} đã được sử dụng. Mỗi số chỉ được dùng một lần.")
                            else:
                                print("Lỗi: Vui lòng nhập số từ 0 đến 8.")
                    except ValueError:
                        print("Lỗi: Vui lòng nhập một số nguyên.")
        self.data = new_data # Gán dữ liệu mới sau khi nhập xong

    def get_blank_position(self):
        """Return position (row, col) of blank space (0)"""
        for i in range(3):
            for j in range(3):
                if self.data[i][j] == 0:
                    return (i, j)
        return (-1, -1)  # Should never happen in a valid puzzle

def create_new_state(data, move):
    """Tạo trạng thái mới từ data và move. Trả về (True, new_data) hoặc (False, None)."""
    # Tạo bản sao sâu để tránh thay đổi trạng thái gốc
    new_data = [list(row) for row in data]
    blank_pos = None

    # Tìm vị trí ô trống
    for i in range(3):
        for j in range(3):
            if new_data[i][j] == 0:
                blank_pos = (i, j)
                break
        if blank_pos:
            break

    if blank_pos is None:
        # Trường hợp không tìm thấy ô trống (dữ liệu không hợp lệ)
        return False, None

    i, j = blank_pos
    ni, nj = i, j

    if move == "up" and i > 0:
        ni = i - 1
    elif move == "down" and i < 2:
        ni = i + 1
    elif move == "left" and j > 0:
        nj = j - 1
    elif move == "right" and j < 2:
        nj = j + 1
    else:
        # Nước đi không hợp lệ tại vị trí này
        return False, None

    # Hoán đổi ô trống với ô đích
    new_data[i][j], new_data[ni][nj] = new_data[ni][nj], new_data[i][j]
    return True, new_data

def is_solvable(state_data):
    """
    Kiểm tra xem một trạng thái puzzle có giải được không.
    Trong 8-puzzle, tính số inversions trong danh sách trạng thái.
    Puzzle có thể giải được nếu số inversions là chẵn.
    Input: state_data (list of lists)
    """
    # Flatten state để đếm inversions
    flat_state = [num for row in state_data for num in row if num != 0]

    inversions = 0
    for i in range(len(flat_state)):
        for j in range(i+1, len(flat_state)):
            if flat_state[i] > flat_state[j]:
                inversions += 1

    return inversions % 2 == 0

def manhattan_distance(buzzle_instance):
    """
    Calculate Manhattan distance heuristic.
    Input: buzzle_instance (một đối tượng của lớp Buzzle)
    """
    distance = 0
    goal_positions = {1:(0,0), 2:(0,1), 3:(0,2),
                     4:(1,0), 5:(1,1), 6:(1,2),
                     7:(2,0), 8:(2,1), 0:(2,2)} # Ô trống không cần tính

    for i in range(3):
        for j in range(3):
            value = buzzle_instance.data[i][j]
            if value != 0:
                goal_i, goal_j = goal_positions[value]
                distance += abs(i - goal_i) + abs(j - goal_j)
    return distance

def generate_random_solvable_state():
    """Tạo một trạng thái ngẫu nhiên và đảm bảo nó có thể giải được."""
    while True:
        numbers = list(range(9))  # Số từ 0-8
        random.shuffle(numbers)
        state_data = [numbers[i:i+3] for i in range(0, 9, 3)]
        if is_solvable(state_data):
            return state_data
