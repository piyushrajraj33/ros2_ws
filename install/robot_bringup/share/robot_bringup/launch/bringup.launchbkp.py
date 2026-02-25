import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node


def generate_launch_description():

    pkg_path = get_package_share_directory("robot_bringup")

    robot_state_launch = os.path.join(pkg_path, "launch", "robot_state.launch.py")
    lidar_launch = os.path.join(pkg_path, "launch", "lidar.launch.py")
    robot_base_launch = os.path.join(pkg_path, "launch", "robot_base.launch.py")

    ekf_config = os.path.join(pkg_path, "config", "ekf.yaml")

    return LaunchDescription([

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(robot_state_launch)
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(lidar_launch)
        ),

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(robot_base_launch)
        ),

        Node(
            package="robot_localization",
            executable="ekf_node",
            name="ekf_filter_node",
            output="screen",
            parameters=[ekf_config]
        )
    ])
