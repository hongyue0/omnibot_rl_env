# 1. 整数 (Integer) - 通常用于计数或离散状态
motor_id = 1
print("电机编号:", motor_id)

# 2. 浮点数 (Float) - 带有小数点的数，机器人控制中最常用的类型！(如角度、速度)
current_angle = 45.5
max_speed = 3.14159
print("当前角度:", current_angle)

# 3. 字符串 (String) - 文本信息，用单引号或双引号括起来
robot_name = "OmniBot-Alpha"
print("启动机器人:", robot_name)

# 4. 布尔值 (Boolean) - 只有两个值：True (真/开) 或 False (假/关)
is_motor_powered_on = True
is_error_triggered = False
print("电机是否通电?", is_motor_powered_on)

# 5. 基础数学运算
new_angle = current_angle + 10.0  # 加法
print("增加10度后的角度:", new_angle)