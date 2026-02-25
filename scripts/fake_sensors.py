#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from sensor_msgs.msg import LaserScan, Imu
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Quaternion

import math


def yaw_to_quat(yaw):
    q = Quaternion()
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q


class FakeSensors(Node):
    def __init__(self):
        super().__init__('fake_sensors')

        self.scan_pub = self.create_publisher(LaserScan, '/scan', 10)
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        self.imu_pub  = self.create_publisher(Imu, '/imu/data', 10)

        self.timer = self.create_timer(0.05, self.publish_all)  # 20 Hz

        # Robot motion simulation
        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.v = 0.2   # linear velocity m/s
        self.w = 0.2   # angular velocity rad/s

        self.dt = 0.05

        self.get_logger().info("Fake sensors started: publishing /scan, /odom, /imu/data")

    def publish_all(self):
        now = self.get_clock().now().to_msg()

        # -----------------------------
        # Fake Odom
        # -----------------------------
        self.yaw += self.w * self.dt
        self.x += self.v * math.cos(self.yaw) * self.dt
        self.y += self.v * math.sin(self.yaw) * self.dt

        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = "odom"
        odom.child_frame_id = "base_link"

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.orientation = yaw_to_quat(self.yaw)

        odom.twist.twist.linear.x = self.v
        odom.twist.twist.angular.z = self.w

        self.odom_pub.publish(odom)

        # -----------------------------
        # Fake IMU
        # -----------------------------
        imu = Imu()
        imu.header.stamp = now
        imu.header.frame_id = "imu_link"

        imu.orientation = yaw_to_quat(self.yaw)
        imu.angular_velocity.z = self.w

        self.imu_pub.publish(imu)

        # -----------------------------
        # Fake LiDAR Scan
        # -----------------------------
        scan = LaserScan()
        scan.header.stamp = now
        scan.header.frame_id = "lidar_link"

        scan.angle_min = -math.pi
        scan.angle_max = math.pi
        scan.angle_increment = math.radians(1.0)

        scan.time_increment = 0.0
        scan.scan_time = self.dt

        scan.range_min = 0.12
        scan.range_max = 10.0

        n = int((scan.angle_max - scan.angle_min) / scan.angle_increment)

        # Simple scan pattern (circle wall)
        scan.ranges = [2.0] * n

        self.scan_pub.publish(scan)


def main():
    rclpy.init()
    node = FakeSensors()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
