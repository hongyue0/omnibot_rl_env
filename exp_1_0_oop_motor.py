import time

print("==============================================")
print(" 核心实验 1.0: 为什么机器人必须用 OOP？")
print("==============================================\n")

# ==========================================
# ❌ 对照组 A：面向过程（状态外露的灾难）
# 场景：硬件要求单次移动指令的角度差（Delta）不能超过 50 度，否则触发急停断电！
# ==========================================
print(">>> 启动对照组 A：面向过程（致命的复制粘贴）")

motor_A_pos = 0.0
motor_B_pos = 0.0

def safe_move_procedural(motor_name, current_pos, target_pos):
    """
    一个普通的移动函数，它需要你手动把'当前状态'传进来才能计算差值。
    """
    delta = abs(target_pos - current_pos) # 计算单次移动的跨度
    
    if delta > 50.0:
        print(f"  🚨 [系统死锁] {motor_name} 试图瞬间移动 {delta}°！电机面临烧毁，已切断整机电源！")
        return "ERROR_LOCKED"
    else:
        print(f"  ✅ {motor_name} 动作执行成功。当前停留在: {target_pos}°")
        return target_pos

# 正常操作
print("\n[指令 1] A 关节移动到 40°")
motor_A_pos = safe_move_procedural("Joint_A", motor_A_pos, 40.0)

print("[指令 2] A 关节继续移动到 90°")
motor_A_pos = safe_move_procedural("Joint_A", motor_A_pos, 90.0)

# 🚨 灾难发生：你想让一直没动过的 B 关节移动到 30°。
# 因为代码很长，你顺手复制了上面的代码，改了名字和目标，却忘了改 current_pos 参数！
print("[指令 3] B 关节移动到 30° (发生 copy-paste 漏改)")
motor_B_pos = safe_move_procedural("Joint_B", motor_A_pos, 30.0)

print(f"\n对照组 A 最终状态 -> A: {motor_A_pos}, B: {motor_B_pos}")
print("总结：B明明停在 0°，安全跨度只有 30°。但因为你传错了状态参数，系统以为B在 90°！")
print("60°的虚假误差直接导致整机急停。如果这是在天上飞的无人机，它已经掉下来了。\n")

time.sleep(2)


# ==========================================
# ✅ 对照组 B：面向对象（状态内聚的绝对安全）
# 场景：用 OOP 重写同样的逻辑
# ==========================================
print("----------------------------------------------")
print(">>> 启动对照组 B：面向对象（状态的绝对内聚）")

class SafeMotor:
    def __init__(self, name):
        self.name = name
        self.pos = 0.0  # 核心：当前状态被死死锁在实例内部！
        
    def safe_move(self, target_pos):
        # 魔法就在这里：不需要外部传 current_pos！它自己知道自己的位置 (self.pos)
        delta = abs(target_pos - self.pos)
        
        if delta > 50.0:
            print(f"  🚨 [系统死锁] {self.name} 试图瞬间移动 {delta}°！已切断电源！")
        else:
            self.pos = target_pos
            print(f"  ✅ {self.name} 动作执行成功。当前停留在: {self.pos}°")

# 1. 实例化
motor_a = SafeMotor("Joint_A_OOP")
motor_b = SafeMotor("Joint_B_OOP")

# 2. 调用逻辑（体验降维打击）
print("\n[指令 1] A 关节移动到 40°")
motor_a.safe_move(40.0)

print("[指令 2] A 关节继续移动到 90°")
motor_a.safe_move(90.0)

# 哪怕你闭着眼睛复制粘贴调用函数，也不可能污染状态！
print("[指令 3] B 关节移动到 30° (就算复制粘贴，也绝对安全)")
motor_b.safe_move(30.0) # 你只需要传入 target。它自动提取 B 自己的位置 (0°)。

print(f"\n对照组 B 最终状态 -> A: {motor_a.pos}°, B: {motor_b.pos}°")
print("总结：OOP 消灭了把 A 的状态传给 B 的可能性。这叫【高内聚，低耦合】。")
print("==============================================")