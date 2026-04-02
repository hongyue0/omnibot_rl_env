from ast import arg
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
import math
import time

class ControllerNode(Node):
    def __init__(self):
        super().__init__('brain_controller')

        self.publisher_ = self.create_publisher(JointState, 'target_joint_states', 10)

        self.timer = self.create_timer(0.01, self.timer_callback)

        self.start_time = time.time()

        self.get_logger().info('大脑节点启动！正在以 100Hz 下发 6 自由度波浪指令...')

    def timer_callback(self):

        t = time.time() - self.start_time

        msg = JointState()

        msg.name = ['joint_1', 'joint_2', 'joint_3', 'joint_4', 'joint_5', 'joint_6']

        msg.position = [
            math.sin(t) * 180.0,
            math.sin(t + 0.5) * 180.0,
            math.sin(t + 1.0) * 180.0,
            math.sin(t + 1.5) * 180.0,
            math.sin(t + 2.0) * 180.0,
            math.sin(t + 2.5) * 180.0
        ]

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = ControllerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()