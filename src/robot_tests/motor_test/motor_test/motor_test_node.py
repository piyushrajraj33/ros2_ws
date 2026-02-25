import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time


class MotorTestNode(Node):
    def __init__(self):
        super().__init__('motor_test_node')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

    def send_cmd(self, lin, ang, duration):
        msg = Twist()
        msg.linear.x = lin
        msg.angular.z = ang

        self.get_logger().info(f"Sending cmd_vel: linear={lin} angular={ang} for {duration} sec")

        start = time.time()
        while time.time() - start < duration:
            self.pub.publish(msg)
            time.sleep(0.1)  # 10 Hz

    def stop(self, duration=2.0):
        self.send_cmd(0.0, 0.0, duration)


def main(args=None):
    rclpy.init(args=args)
    node = MotorTestNode()

    time.sleep(1)

    # Forward
    node.send_cmd(0.15, 0.0, 5.0)
    node.stop(2.0)

    # Backward
    node.send_cmd(-0.15, 0.0, 5.0)
    node.stop(2.0)

    # Rotate Left
    node.send_cmd(0.0, 0.5, 5.0)
    node.stop(2.0)

    # Rotate Right
    node.send_cmd(0.0, -0.5, 5.0)
    node.stop(2.0)

    node.get_logger().info("Motor test finished.")
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
