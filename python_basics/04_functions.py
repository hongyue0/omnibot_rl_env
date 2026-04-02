# 定义一个函数，名为 apply_safety_limit
# 括号里是它需要的“原材料 (输入参数)”
def apply_safety_limit(input_angle):
    limit = 180.0
    
    if input_angle > limit:
        result = limit
    elif input_angle < 0:
        result = 0.0
    else:
        result = input_angle
        
    # return 是把处理完的结果“吐”出来给调用者
    return result

# --- 以下是调用函数的演示 ---
print("测试 1：")
final_angle_1 = apply_safe_limit(200.5)
print(f"结果：", final_angle_1)

print("测试 2：")
final_angle_2 = apply_safe_limit(-10.5)
print(f"结果：", final_angle_2)

print("测试 3：")
final_angle_3 = apply_safe_limit(45)
print(f"结果：", final_angle_3)