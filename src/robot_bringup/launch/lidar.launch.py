from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    # Replace with your lidar driver node package
    # Example: rplidar_ros, ydlidar_ros2_driver, etc.

    return LaunchDescription([

        # Example placeholder node (REMOVE this when using real lidar driver)
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            name="lidar_tf",
            arguments=["0.15", "0", "0.15", "0", "0", "0", "base_link", "lidar_link"]
        )
    ])
