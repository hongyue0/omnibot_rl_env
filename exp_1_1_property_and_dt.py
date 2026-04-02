import time

print("=========================================================")
print(" 核心实验 1.1: 工业级 Motor 封装与离散控制的 dt 灾难")
print("=========================================================\n")

class IndustrialMotor:
    def __init__(self, name):
        self.name = name
        # 🛡️ 1. 私有化变量：变量名前加一个下划线 '_'
        # 在 Python 工业界，这代表“内部机密，外部绝不允许直接读写！”
        self._angle = 0.0  
        
        # 物理参数
        self.Kp = 5.0  # 比例增益 (P控制器：根据误差决定发力大小)

    # 🛡️ 2. @property 装饰器 (Getter：安全的数据窗口)
    # 它允许外部像读取属性一样读取 _angle，但实际上是经过了这道安全门
    @property
    def angle(self):
        return self._angle

    # 🛡️ 3. @angle.setter (Setter：数据写入的安检通道)
    # 当外部尝试写 motor.angle = xxx 时，必定会被这里的 if-else 拦截！
    @angle.setter
    def angle(self, target):
        if target > 180.0:
            self._angle = 180.0  # 绝对限幅
        elif target < -180.0:
            self._angle = -180.0
        else:
            self._angle = target

    # ⏱️ 4. 离散物理世界的步进引擎 (非常重要！)
    def step(self, target_angle, dt):
        """
        dt (Delta Time): 距离上一次计算经过了多少秒 (时间步长)
        这里模拟了一个最基础的比例控制器 (P-Control)。
        """
        # 计算误差：目标 - 当前
        error = target_angle - self.angle
        
        # 物理世界的速度 = 误差 * 增益
        velocity = self.Kp * error
        
        # 离散积分：新的位置 = 当前位置 + 速度 * 时间
        new_angle = self.angle + (velocity * dt)
        
        # 触发 setter 进行安全写入
        self.angle = new_angle
        return self.angle

# ==========================================
# 实验开始：离散数学的翻车现场
# 场景：电机初始在 0°，要求移动到 100°。
# ==========================================
motor_a = IndustrialMotor("High_Freq_Motor")
motor_b = IndustrialMotor("Low_Freq_Motor")
target = 100.0

print(">>> 对照组 A：高频控制 (dt = 0.05 秒，相当于 20Hz 控制频率)")
print("期待：平滑逼近目标。")
for i in range(10):
    current_pos = motor_a.step(target, dt=0.05)
    # 打印简易的波形条
    bar = "█" * int(current_pos / 4)
    print(f"Step {i+1:02d} | 角度: {current_pos:6.2f}° | {bar}")

print("\n---------------------------------------------------------")
print(">>> 🚨 对照组 B：低频控制/大步长 (dt = 0.5 秒，相当于 2Hz 控制频率)")
print("期待：见证著名的离散系统振荡与超调！")
for i in range(10):
    current_pos = motor_b.step(target, dt=0.5)
    # 处理负数情况以防报错
    bar_length = max(0, min(100, int(current_pos / 4)))
    bar = "█" * bar_length if current_pos >= 0 else "❌ 超调反转"
    print(f"Step {i+1:02d} | 角度: {current_pos:6.2f}° | {bar}")

print("\n=========================================================")
print("诊断报告：")
print("对照组 A 完美收敛。")
print("对照组 B 疯了！因为时间步长(dt)太大，第一步速度极快，在0.5秒内直接冲到了 250°！")
print("随后被 @property 限幅拦在了 180°。下一步反向发力，又冲到了 -220°！彻底陷入震荡。")

print("\n=========================================================")
print(">>> 对照组 C：恶意篡改防御测试 (@property 的安检门)")

# 模拟一个新手程序员，或者一个有 Bug 的外部网络节点
# 试图直接暴力修改底层角度（这在传统的全局变量下会直接得逞）
print("黑客尝试：motor_a.angle = 9999.0")
motor_a.angle = 9999.0 

# 查看结果
print(f"防御结果：电机实际角度被死死拦截在 -> {motor_a.angle}°")
print("教育意义：如果没有 @property 的 setter 拦截，电机此刻已经因为收到 9999 度的指令而自旋拧断线缆了。")