motor_config = {
    "id": 1,
    "name": "Shoulder_Pitch",
    "is_online": True,
    "temperature": 35.5,
    "max_speed": 3.14
}

print("电机完整配置单：", motor_config)

current_temp = motor_config["temperature"]
print(f"\n查询到电机 {motor_config['name']} 的当前温度是：{current_temp}℃")

motor_config["temperature"] = 42.0
print("更新后的温度：", motor_config["temperature"])

motor_config["firmware_version"] = "v2.1.4"
print("\n新增固件版本后的配置单：", motor_config)

print("\n--- 开始温度判断 ---")
if motor_config["temperature"] > 40.0:
    print("警告：电机过热！尝试自动降低最大速度...")
    motor_config["max_speed"] = 1.0
    print(f"当前最大速度已限制为：{motor_config['max_speed']} rad/s")
else:
    print("温度正常。")