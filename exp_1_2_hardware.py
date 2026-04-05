#!/usr/bin/env python3
# ==========================================
# [包引入区 - 基础材料库]
# ==========================================
import rclpy                                   # ROS2 Python 客户端核心总线
from rclpy.node import Node                    # ROS2 节点基类（提供生命周期和通信机制）
from sensor_msgs.msg import JointState         # 机器人标准多关节状态消息协议
from tf2_ros import TransformBroadcaster       # 空间坐标系广播天线，负责向全网发送 3D 位姿
from geometry_msgs.msg import TransformStamped # 带有时间戳的 3D 几何变换（平移+旋转）协议包
import math                                    # 数学库，用于角度转弧度和三角函数计算
import time                                    # 时间库，用于获取系统绝对时间戳，计算 dt
import random                                  # 随机数生成器，用于模拟工厂环境中恶劣的丢包率

# ==========================================
# [物理装甲层 - 直接内嵌防爆电机实体图纸]
# ==========================================
class Motor:
    """带有物理死区拦截的 OOP 硬件图纸。
    作用：确保无论外部网络发来什么垃圾数据，物理电机绝对不会越界。"""
    def __init__(self, name):
        self.name = name
        self.__angle = 0.0 # 私有变量，双下划线表示极度机密，外部绝对不可见

    @property
    def angle(self):
        """只读窗口：允许外部查看当前角度"""
        return self.__angle
    
    @angle.setter
    def angle(self, target):
        """写入安检门：任何试图修改电机角度的操作都必须经过这里的数学审查"""
        # 严格的上下限防爆拦截
        if target < -170 or target > 170:
            # raise 会抛出异常，如果外层没有 try-except 接住，程序就会崩溃（紧急熔断）
            raise ValueError(f"严重警告：{self.name}目标{target:.1f}超出[-170, 170]物理死区！")
        else:
            self.__angle = target # 审查通过，放行写入

# ==========================================
# [ROS2 节点层 - 驱动板大脑与网络接口]
# ==========================================
class HardwareInterfaceNode(Node):
    def __init__(self):
        # 初始化节点，给这块驱动板命名
        super().__init__('hardware_interface_node')
        
        # 1. 焊接 RX 接收引脚 (订阅大脑下发的期望指令)
        self.subscription = self.create_subscription(
            JointState, 'target_joint_states', self.listener_callback, 10)
            
        # 2. 焊接 TX 发送引脚 (向外报告电机真实的、经过限幅的安全角度)
        self.publisher_ = self.create_publisher(JointState, 'real_joint_states', 10)
        
        # 3. 焊接 TF2 空间广播电台 (负责告诉 RViz2 这 6 个关节在空间里怎么摆)
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # 4. 实例化 6 个带有防爆装甲的物理电机，并用字典(Dict)装起来方便查找
        # 键是 'joint_1' 到 'joint_6'，值是 Motor 类的实体对象
        self.motors = {
            f'joint_{i}': Motor(f'joint_{i}') for i in range(1, 7)
        }
        
        # 5. 灾难应对缓存：记录历史时间戳和历史速度，为了在断网时做一阶外推
        self.last_time = time.time()
        self.velocities = {f'joint_{i}': 0.0 for i in range(1, 7)}
        
        self.get_logger().info('硬件驱动板已通电！带 TF2 渲染的灾难模拟器就绪...')

    def listener_callback(self, msg):
        """核心中断：每次收到指令都会触发。这里包含了网络抖动测算、丢包模拟和安全写入"""
        current_time = time.time()
        # dt = 本次收到指令的时间 - 上次收到指令的时间
        # 理想情况下大脑是 100Hz 发送，dt 应该是 0.01 秒。但实际由于网络抖动，dt 是波动的！
        dt = current_time - self.last_time  
        
        # ==========================================
        # 🚨 灾难模拟与一阶外推补救
        # ==========================================
        # 产生一个 0~1 的随机数。如果有 10% 的几率（< 0.10），我们假装没收到网络信号
        if random.random() < 0.10:  
            self.get_logger().warning(f"🚨 致命丢包！执行 6 关节一阶外推补救...")
            # 既然没收到新指令，就利用历史速度预测它应该在哪
            for name, motor in self.motors.items():
                # S = S0 + V * dt (当前位置 = 历史位置 + 历史速度 * 经历的时间)
                extrapolated_angle = motor.angle + (self.velocities[name] * dt)
                
                # 🛡️ 极其严谨：即便是自己算出来的补救角度，也要过安检门！防止外推越界
                try:
                    motor.angle = extrapolated_angle
                except ValueError as e:
                    pass # 超过死区了就原地不动，无视错误
            
            # 补救完了，赶紧刷新一下 3D 渲染，然后退出本次中断
            self.publish_real_and_tf(current_time)
            self.last_time = current_time
            return  

        # ==========================================
        # ✅ 网络正常时的处理逻辑
        # ==========================================
        # 遍历大脑发来的目标数组
        for i in range(len(msg.name)):
            name = msg.name[i]
            target_angle = msg.position[i]
            physical_motor = self.motors[name] # 拿到对应的电机实体
            
            # 测算真实速度 (当前目标位置 - 历史真实位置) / dt，存入备用池
            if dt > 0:
                self.velocities[name] = (target_angle - physical_motor.angle) / dt
            
            # 🛡️ 尝试把大脑的指令塞进电机（必定会经过 @angle.setter）
            try:
                physical_motor.angle = target_angle 
            except ValueError as e:
                # 大脑发了疯狗指令，被电机内置的装甲弹开了！打印日志警告。
                self.get_logger().error(f"防爆拦截: {e}")

        # 所有电机处理完毕，打包真实状态发送给 RViz2
        self.publish_real_and_tf(current_time)
        self.last_time = current_time

    def publish_real_and_tf(self, current_time):
        """打包并渲染：把干瘪的数字变成 3D 空间里的运动学链条"""
        # 1. 组装真实状态包
        real_msg = JointState()
        real_msg.name = list(self.motors.keys())
        real_msg.position = [m.angle for m in self.motors.values()] # 提取所有安全角度
        self.publisher_.publish(real_msg) # 通过 TX 引脚发出去
        
        # 2. 串联空间坐标系 (TF Tree)
        # 第一个关节挂载在地球(world)上
        parent_frame = 'world'
        
        for name in real_msg.name:
            t = TransformStamped()
            t.header.stamp = self.get_clock().now().to_msg() # 统一的相对时间戳
            t.header.frame_id = parent_frame                 # 父坐标是谁
            t.child_frame_id = f"{name}_link"                # 我是谁
            
            # 空间平移：我距离我爸爸有多远？
            # 设定：除了 joint_1 在地球原点，其余每个关节都在上一个关节 Z 轴正上方 0.2 米
            t.transform.translation.x = 0.0
            t.transform.translation.y = 0.0
            t.transform.translation.z = 0.2 if parent_frame != 'world' else 0.0
            
            # 空间旋转：我相对于我爸爸转了多少度？
            # RViz2 底层使用四元数 (Quaternion)，需要把角度拆解成 x,y,z,w 四个分量
            # 我们假设所有电机都是绕着 X 轴旋转的
            angle_rad = math.radians(self.motors[name].angle) # 必须转成弧度
            t.transform.rotation.x = math.sin(angle_rad / 2.0)
            t.transform.rotation.y = 0.0
            t.transform.rotation.z = 0.0
            t.transform.rotation.w = math.cos(angle_rad / 2.0)
            
            # 广播这根连杆！
            self.tf_broadcaster.sendTransform(t)
            
            # 精髓：把我变成下一个关节的爸爸，从而把 6 个关节像锁链一样串起来
            parent_frame = f"{name}_link"

# ==========================================
# [主程序入口 - 系统上下电]
# ==========================================
def main(args=None):
    rclpy.init(args=args)                # ROS2 系统通电
    node = HardwareInterfaceNode()       # 制造驱动板实例
    try:
        rclpy.spin(node)                 # 死守中断，让程序不要退出
    except KeyboardInterrupt:
        pass                             # 按 Ctrl+C 准备下电
    finally:
        node.destroy_node()              # 销毁内存
        rclpy.shutdown()                 # ROS2 系统断电

if __name__ == '__main__':
    main()