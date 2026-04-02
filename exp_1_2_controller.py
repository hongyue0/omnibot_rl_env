#!/usr/bin/env python3
# ==========================================
# [包引入区 - Package Imports]
# ==========================================
import rclpy                                # [种类: 客户端库] 作用: ROS2 的 Python 核心底层总线
from rclpy.node import Node                 # [种类: 核心类]   作用: 所有 ROS2 节点的父类图纸
from sensor_msgs.msg import JointState      # [种类: 通信协议] 作用: 工业级多关节状态标准数据包
import math                                 # [种类: 标准库]   作用: 提供 sin, cos 等数学运算
import time                                 # [种类: 标准库]   作用: 提供系统时间戳获取功能

class ControllerNode(Node):
    def __init__(self):
        # 1. 初始化器官，接入 ROS2 网络
        # super().__init__() 调用父类构造函数，相当于在网络上注册自己
        super().__init__('brain_controller')
        
        # 2. self.create_publisher [种类: 节点方法] 
        # 作用: 创建发送端。参数依次为：(数据协议, 话题血管名称, 队列缓存长度)
        self.publisher_ = self.create_publisher(JointState, 'target_joint_states', 10)
        
        # 3. self.create_timer [种类: 节点方法] 
        # 作用: 硬件时钟中断。每隔 0.01 秒，强制调用一次 self.timer_callback
        self.timer = self.create_timer(0.01, self.timer_callback)
        
        self.start_time = time.time()       # 记录开机时间
        self.get_logger().info('大脑节点启动！正在以 100Hz 下发 6 自由度波浪指令...')

    def timer_callback(self):
        """[种类: 回调函数] 作用: 被 Timer 事件驱动，定期执行的核心逻辑"""
        # 计算系统运行了多久
        t = time.time() - self.start_time
        
        # 实例化一个标准的工业级通信包
        msg = JointState()
        
        # 构造 6 个关节的名字 (必须和硬件端严格对齐)
        msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']
        
        # 为 6 个关节生成具有相位差的正弦波（模拟蛇形或波浪形运动）
        # math.sin() 生成 -1 到 1 的波浪，乘以 180 放大到 -180度 到 180度
        # 注意：这里故意放大到 180 度，就是为了触发你硬件端 [-170, 170] 的物理死区报警！
        msg.position = [
            math.sin(t) * 180.0,           
            math.sin(t + 0.5) * 180.0,     
            math.sin(t + 1.0) * 180.0,     
            math.sin(t + 1.5) * 180.0,
            math.sin(t + 2.0) * 180.0,
            math.sin(t + 2.5) * 180.0
        ]
        
        # self.publisher_.publish() [种类: 发布方法] 作用: 将填好数据的包裹扔进网络
        self.publisher_.publish(msg)

# ================= 主程序电源开关 =================
def main(args=None):
    rclpy.init(args=args)           # [种类: 系统函数] 作用: 初始化 DDS 网络底层
    node = ControllerNode()         # [种类: 对象实例化] 作用: 按图纸制造大脑节点
    try:
        rclpy.spin(node)            # [种类: 阻塞器] 作用: 挂起线程，死守事件(Timer)触发
    except KeyboardInterrupt:
        pass                        # 捕获 Ctrl+C，优雅退出
    finally:
        node.destroy_node()         # [种类: 析构方法] 作用: 释放节点内存
        rclpy.shutdown()            # [种类: 系统函数] 作用: 关闭 DDS 网络

if __name__ == '__main__':
    main()