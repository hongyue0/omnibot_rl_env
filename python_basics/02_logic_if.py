target_angle = 190.0
mechanical_limit = 180.0

print(f"尝试将电机转动到 {target_angle} 度...") # f-string: 可以把变量直接塞进字符串里打印

# 如果目标角度大于机械限位
if target_angle > mechanical_limit:
    # 这里的代码只有在上面条件成立时才会执行 (注意前面的缩进)
    print("⚠️ 警告：指令超过机械限位！")
    safe_angle = mechanical_limit
    print(f"已强制截断为安全角度: {safe_angle} 度")

# elif 意思是 else if (否则如果)
elif target_angle < 0:
    print("⚠️ 警告：角度不能为负数！")
    safe_angle = 0.0

# 如果以上条件都不满足
else:
    print("✅ 指令安全，准备执行。")
    safe_angle = target_angle

print("最终下发的真实角度:", safe_angle)