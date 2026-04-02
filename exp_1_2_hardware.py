#!/usr/bin/env python3
# ==========================================
# [包引入区 - Package Imports]
# ==========================================
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from tf2_ros import TransformBroadcaster       # [种类: TF2 核心类] 作用: 空间坐标系广播电台
from geometry_msgs.msg import TransformStamped # [种类: 几何协议] 作用: 记录 3D 平移与旋转的数据包
import math
import time
import random                                  # [种类: 标准库] 作用: 生成随机数，用于模拟概率丢包

# ==========================================
# [物理装甲层 - 直接内嵌你的 Motor 类]
# ==========================================
class Motor:
    """带有物理死区拦截的 OOP 硬件图纸"""
    def __init__(self, name):
        self.name = name
        self.__angle = 0.0

    @property
    def angle(self):
        return self.__angle
    
    @angle.setter
    def angle(self, target):
        # 你的杰作：严格的上下限防爆拦截
        if target < -170 or target > 170:
            raise ValueError(f"严重警告：{self.name}目标{target:.1f}超出[-170, 170]物理死区！")
        else:
            self.__angle = target

# ==========================================
# [ROS2 节点层 - 网络与渲染接口]
# ==========================================
class HardwareInterfaceNode(Node):
    def __init__(self):
        super().__init__('hardware_interface_node')
        
        # 1. 接收器 (RX)
        self.subscription = self.create_subscription(
            JointState, 'target_joint_states', self.listener_callback, 10)
            
        # 2. 发送器 (TX)
        self.publisher_ = self.create_publisher(JointState, 'real_joint_states', 10)
        
        # 3. TF2 空间广播电台实例化
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # 4. 焊接 6 个带有防爆装甲的物理电机实体
        self.motors = {
            f'joint_{i}': Motor(f'joint_{i}') for i in range(1, 7)
        }
        
        # 记录每个关节的历史速度和上一次收到指令的时间 (用于断线外推补救)
        self.last_time = time.time()
        self.velocities = {f'joint_{i}': 0.0 for i in range(1, 7)}
        
        self.get_logger().info('硬件驱动板已通电！带 TF2 渲染的灾难模拟器就绪...')

    def listener_callback(self, msg):
        """[种类: 回调函数] 作用: 每当总线收到 target_joint_states 时触发"""
        current_time = time.time()
        dt = current_time - self.last_time  # 计算时间微分项
        
        # ==========================================
        # 🚨 灾难模拟与补救 (Ablation Study)
        # ==========================================
        # random.random() [种类: 函数] 作用: 生成 0.0~1.0 随机数
        if random.random() < 0.10:  # 10% 概率触发网络丢包
            self.get_logger().warning(f"🚨 致命丢包！执行 6 关节一阶外推补救...")
            for name, motor in self.motors.items():
                # 补救公式: 新位置 = 当前位置 + 历史速度 * 经过的时间
                extrapolated_angle = motor.angle + (self.velocities[name] * dt)
                
                # 🛡️ 就算是在补救时，依然要用 try-except 防止外推出界！
                try:
                    motor.angle = extrapolated_angle
                except ValueError as e:
                    # 默默吞下错误，保持在安全边界
                    pass 
            
            # 补救完成后，立刻刷新 3D 模型
            self.publish_real_and_tf(current_time)
            self.last_time = current_time
            return  # 丢包处理完毕，直接打断函数，不再往下走！

        # === 以下为网络正常时的逻辑 ===
        for i in range(len(msg.name)):
            name = msg.name[i]
            target_angle = msg.position[i]
            physical_motor = self.motors[name]
            
            # 计算当前关节的真实速度，并更新到字典中留作备用
            if dt > 0:
                self.velocities[name] = (target_angle - physical_motor.angle) / dt
            
            # 🛡️ 触发防爆装甲的 try-except 拦截
            try:
                physical_motor.angle = target_angle # 这里会触发你的 @angle.setter
            except ValueError as e:
                # 打印出你写的拦截日志！
                self.get_logger().error(f"防爆拦截: {e}")

        # 正常刷新 3D 模型
        self.publish_real_and_tf(current_time)
        self.last_time = current_time


    def publish_real_and_tf(self, current_time):
        """自定义函数：负责打包发布真实角度，并在 RViz2 中串联 6 个关节的 3D 坐标系"""
        real_msg = JointState()
        real_msg.name = list(self.motors.keys())
        real_msg.position = [m.angle for m in self.motors.values()]
        
        # 1. 发布回传的真实状态
        self.publisher_.publish(real_msg)
        
        # 2. 核心渲染逻辑：将 6 个电机像糖葫芦一样串联起来广播
        parent_frame = 'world'
        
        for name in real_msg.name:
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg() # 打上 ROS 统一时钟戳
            t.header.frame_id = parent_frame                 # 父坐标系
            t.child_frame_id = f"{name}_link"                # 子坐标系 (当前关节)
            
            # 平移: 每个电机都在上一个电机的 Z 轴上方 0.2 米处
            t.transform.translation.x = 0.0
            t.transform.translation.y = 0.0
            t.transform.translation.z = 0.2 if parent_frame != 'world' else 0.0
            
            # 旋转: 提取电机的真实角度并转为四元数 (绕 X 轴旋转)
            angle_rad = math.radians(self.motors[name].angle)
            t.transform.rotation.x = math.sin(angle_rad / 2.0)
            t.transform.rotation.y = 0.0
            t.transform.rotation.z = 0.0
            t.transform.rotation.w = math.cos(angle_rad / 2.0)
            
            # 发射 TF 广播！
            self.tf_broadcaster.sendTransform(t)
            
            # 把当前的子坐标系变成下一个关节的父坐标系，完成串接
            parent_frame = f"{name}_link"

def main(args=None):
    rclpy.init(args=args)
    node = HardwareInterfaceNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()