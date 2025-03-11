from collections import deque

class Buzzle:
    def __init__(self, data=None, parent=None, move=None):
        if data is None:
            self.data = [[1,2,3],
                        [4,5,6],
                        [7,8,0]]
        else:
            self.data = [row[:] for row in data]
        self.parent = parent
        self.move = move

    def is_goal(self):
        if self.data == list([[1,2,3],
                        [4,5,6],
                        [7,8,0]]):
            return True
        return False
    
    def print_state(self):
        print("Trang thai hien tai: ")
        for i in range(3):
            for j in range(3):
                print(self.data[i][j], end=" ")
            print("\n")

    def entry_state(self):
        print("Nhap trang thai: ")
        for i in range(3):
            for j in range(3):
                x = int(input(f"Nhap data[{i},{j}]: "))
             
                self.data[i][j] = x
           

def print_solution(state):
    B = Buzzle(A.data)
    steps = []
    current = state
    
    while current.parent is not None:
        steps.append(current.move)
        current = current.parent
    
    print("Các bước di chuyển:")
    for i, move in enumerate(reversed(steps), 1):
        print(f"Bước {i}: {move}")
        create_new_state(B, move)[1].print_state()
        B = create_new_state(B, move)[1]

    print(f"Tổng số bước: {len(steps)}")

def create_new_state(A: Buzzle, move):
    new_state = Buzzle([row[:] for row in A.data], parent=A, move=move)
    
    if (move == "up"):
        for i in range(3):
            for j in range(3):
                if new_state.data[i][j] == 0:
                    if (i == 0):
                        return ("No", new_state)
                    new_state.data[i][j], new_state.data[i-1][j] = new_state.data[i-1][j], new_state.data[i][j]
                    return ("Yes", new_state)

    if (move == "down"):
        for i in range(3):
            for j in range(3):
                if new_state.data[i][j] == 0:
                    if (i == 2):
                        return ("No", new_state)
                    new_state.data[i][j], new_state.data[i+1][j] = new_state.data[i+1][j], new_state.data[i][j]
                    return ("Yes", new_state)

    if (move == "left"):
        for i in range(3):
            for j in range(3):
                if new_state.data[i][j] == 0:
                    if (j == 0):
                        return ("No", new_state)
                    new_state.data[i][j], new_state.data[i][j-1] = new_state.data[i][j-1], new_state.data[i][j]
                    return ("Yes", new_state)

    if (move == "right"):
        for i in range(3):
            for j in range(3):
                if new_state.data[i][j] == 0:
                    if (j == 2):
                        return ("No", new_state)
                    new_state.data[i][j], new_state.data[i][j+1] = new_state.data[i][j+1], new_state.data[i][j]
                    return ("Yes", new_state)
                
moves = {"up", "down", "left", "right"}                
A = Buzzle()

def bfs():
    global moves, A
    Q = deque() 
    visited = set()
    visited.add(str(A.data))
    Q.append(A) 
    while (Q):
        current_state = Q.popleft()
        if (current_state.is_goal()):
            print("Đã tìm thấy trạng thái!")
            print_solution(current_state)
            return True
        
        for move in moves:
            result = create_new_state(current_state, move)
            if result[0] == "Yes":
                new_state = result[1]
                state_str = str(new_state.data)

                if state_str not in visited:
                    visited.add(state_str)
                    Q.append(new_state)
    print("Không tìm thấy giải pháp!")
    return False
            
if __name__ == "__main__":
    A.entry_state()
    A.print_state()
    bfs()