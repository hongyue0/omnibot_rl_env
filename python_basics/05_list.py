# 1. 创建一个列表：记录机械臂 4 个关节的当前角度
joint_angles = [0.0, 15.5, 30.0, 45.0]
print("初始关节数组:", joint_angles)

# 2. 访问列表里的元素 (索引/Index)
# 记住：第一个元素的编号是 0！
base_joint = joint_angles[0]
print("底座关节 (第0号) 的角度:", base_joint)
print("末端关节 (第3号) 的角度:", joint_angles[3])

# 3. 修改列表里的元素
print("\n指令：底座关节旋转到 90.0 度")
joint_angles[0] = 90.0
print("更新后的关节数组:", joint_angles)

# 4. 往列表末尾追加新数据 (这在录制遥操作轨迹时极常用)
# 假设我们给机械臂安装了一个新的夹爪关节
joint_angles.append(10.0) 
print("追加夹爪后的数组:", joint_angles)

# 5. 遍历列表 (结合我们上节课的 for 循环)
print("\n--- 开始依次检查所有关节状态 ---")
for i in range(len(joint_angles)): # len() 会计算列表有多长 (这里是5)
    print(f"正在检查 第 {i} 号 关节，当前角度: {joint_angles[i]}")