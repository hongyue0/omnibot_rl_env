# 1. 创建一个字典：定义 1 号电机的物理配置
motor_config = {
    "id": 1,
    "name": "Shoulder_Pitch",
    "is_online": True,
    "temperature": 35.5,
    "max_speed": 3.14
}

print("电机完整配置单:", motor_config)

# 2. 通过“标签 (Key)”精准提取数据
current_temp = motor_config["temperature"]
print(f"\n查询到电机 {motor_config['name']} 的当前温度是: {current_temp}℃")

# 3. 修改字典里的值
# 假设电机运转了一会，温度升高了
motor_config["temperature"] = 39.0
print("更新后的温度:", motor_config["temperature"])

# 4. 动态增加新的标签
# 假设系统突然需要记录电机的固件版本
motor_config["firmware_version"] = "v2.1.4"
print("\n新增固件版本后的配置单:", motor_config)

# 5. 结合 if-else 做安全诊断
print("\n--- 开始温度诊断 ---")
if motor_config["temperature"] > 40.0:
    print("⚠️ 警告：电机过热！尝试自动降低最大速度...")
    motor_config["max_speed"] = 1.0  # 动态修改降速
    print(f"当前最大速度已限制为: {motor_config['max_speed']} rad/s")
else:
    print("✅ 温度正常。")