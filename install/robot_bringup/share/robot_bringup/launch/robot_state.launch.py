from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_path = get_package_share_directory("robot_bringup")
    diff_drive_config = os.path.join(pkg_path, "config", "diff_drive.yaml")

    return LaunchDescription([

        # Start ros2_control node with robot config
        Node(
            package="controller_manager",
            executable="ros2_control_node",
            parameters=[diff_drive_config],
            output="screen"
        ),

        # Spawn joint_state_broadcaster first
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["joint_state_broadcaster"],
            output="screen"
        ),

        # Then spawn diff_drive_controller
        Node(
            package="controller_manager",
            executable="spawner",
            arguments=["diff_drive_controller"],
            output="screen"
        ),
    ])
