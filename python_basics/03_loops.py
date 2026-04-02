import time # 引入时间库，模拟真实世界的流逝

print("--- 1. for 循环：确定的迭代次数 ---")
# 模拟执行一段规划好的 5 步轨迹
# range(5) 会生成 0, 1, 2, 3, 4
for step in range(5):
    print(f"执行第 {step} 步插值...")
    time.sleep(0.2) # 让程序暂停 0.2 秒，模拟物理耗时

print("\n--- 2. while 循环：基于条件的无限循环 ---")
# 模拟电机向目标角度逼近的过程
current_pos = 0.0
target_pos = 10.0
velocity = 2.5 # 每次循环前进 2.5 度

# 只要当前位置小于目标位置，就一直循环
while current_pos < target_pos:
    current_pos = current_pos + velocity
    print(f"电机转动中... 当前到达: {current_pos} 度")
    
print("🎯 目标已到达！")