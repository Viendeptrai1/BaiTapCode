

class Buzzle:
    def __init__(self, data = [[]]):
        self.data = [[1,2,3],
                    [4,5,6],
                    [7,8,0]]
    def is_goal(self):
        if self.data == list([[1,2,3],
                        [4,5,6],
                        [7,8,0]]):
            return True
        return False
    def print_state(self):
        print("Trang thai hien tai: ")
        print(self.data)

    def entry_state(self):
        print("Nhap trang thai: ")
        for i in range(3):
            for j in range(3):
                x = int(input(f"Nhap data[{i},{j}]: "))
             
                self.data[i][j] = x
           


def create_new_state(A: Buzzle, move):
    if (move == "up"):
        for i in range(3):
            for j in range(3):
                if A.data[i][j] == 0:
                    if (i == 0):
                        return {"No", A}
                    A.data[i][j], A.data[i-1][j] = A.data[i-1][j], A.data[i][j]
                    return {"Yes", A}

    if (move == "down"):
        for i in range(3):
            for j in range(3):
                if A.data[i][j] == 0:
                    if (i == 2):
                        return {"No", A}
                    A.data[i][j], A.data[i+1][j] = A.data[i+1][j], A.data[i][j]
                    return {"Yes", A}
    if (move == "left"):
        for i in range(3):
            for j in range(3):
                if A.data[i][j] == 0:
                    if (j == 0):
                        return {"No", A}
                    A.data[i][j], A.data[i][j-1] = A.data[i][j-1], A.data[i][j]
                    return {"Yes", A}
    if (move == "right"):
        for i in range(3):
            for j in range(3):
                if A.data[i][j] == 0:
                    if (j == 2):
                        return {"No", A}
                    A.data[i][j], A.data[i][j+1] = A.data[i][j+1], A.data[i][j]
                    return {"Yes", A}
                
A = Buzzle()

A.entry_state()
A.print_state()

if (A.is_goal()):
    print("Dat trang thai cuoi cung!")