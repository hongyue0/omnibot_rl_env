# Phase 1.0: OOP 物理世界映射实验

class BasicMotor:
    def __init__(self, motor_id):
        self.motor_id = motor_id
        self.angle = 0  # 初始角度

    def set_angle(self, target):
        # 简单的逻辑：直接赋值（实验 1.1 将引入安全限幅）
        self.angle = target
        print(f"电机 {self.motor_id} 角度已更新为: {self.angle}度")

if __name__ == "__main__":
    # 消融实验：证明 OOP 的隔离性
    motor_a = BasicMotor("Joint_1")
    motor_b = BasicMotor("Joint_2")

    motor_a.set_angle(90)
    
    print(f"--- 状态检查 ---")
    print(f"电机 A 角度: {motor_a.angle}") # 应该是 90
    print(f"电机 B 角度: {motor_b.angle}") # 应该是 0 (不受 A 影响)