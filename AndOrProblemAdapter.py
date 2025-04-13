from buzzle_logic import Buzzle, create_new_state

class AndOrProblemAdapter:
    """
    Lớp adapter để chuyển đổi Buzzle thành Problem phù hợp với thuật toán AND/OR search
    """
    def __init__(self, initial_buzzle_state):
        """
        Khởi tạo vấn đề với trạng thái Buzzle ban đầu
        """
        self.initial_state = tuple(map(tuple, initial_buzzle_state.data))
    
    def goal_test(self, state_tuple):
        """
        Kiểm tra xem trạng thái có phải là đích không
        """
        # Chuyển tuple state thành list state để tương thích với Buzzle
        state_data = [list(row) for row in state_tuple]
        return Buzzle(state_data).is_goal()
    
    def actions(self, state_tuple):
        """
        Trả về danh sách các hành động hợp lệ cho trạng thái
        """
        valid_actions = []
        state_data = [list(row) for row in state_tuple]
        
        for move in ["up", "down", "left", "right"]:
            success, _ = create_new_state(state_data, move)
            if success:
                valid_actions.append(move)
        
        return valid_actions
    
    def result(self, state_tuple, action):
        """
        Trả về trạng thái mới sau khi thực hiện hành động
        """
        state_data = [list(row) for row in state_tuple]
        success, new_data = create_new_state(state_data, action)
        
        if success:
            return tuple(map(tuple, new_data))
        return None  # Nếu hành động không hợp lệ 