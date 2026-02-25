from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg = get_package_share_directory("nav_bringup")
    slam_params = os.path.join(pkg, "config", "slam_params.yaml")

    slam_toolbox_node = Node(
        package="slam_toolbox",
        executable="sync_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[slam_params]
    )

    return LaunchDescription([
        slam_toolbox_node
    ])
