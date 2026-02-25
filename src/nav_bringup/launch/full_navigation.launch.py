from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg_nav_bringup = get_package_share_directory("nav_bringup")

    slam_params = os.path.join(pkg_nav_bringup, "config", "slam_params.yaml")
    nav2_params = os.path.join(pkg_nav_bringup, "config", "nav2_params.yaml")
    rviz_config = os.path.join(pkg_nav_bringup, "config", "rviz_config.rviz")

    # ---------------- SLAM TOOLBOX ----------------
    slam_toolbox_node = Node(
        package="slam_toolbox",
        executable="sync_slam_toolbox_node",
        name="slam_toolbox",
        output="screen",
        parameters=[slam_params]
    )

    # ---------------- NAV2 ----------------
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("nav2_bringup"),
                "launch",
                "navigation_launch.py"
            )
        ),
        launch_arguments={
            "use_sim_time": "false",
            "params_file": nav2_params,
            "autostart": "true"
        }.items()
    )

    # ---------------- RVIZ ----------------
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_config]
    )

    return LaunchDescription([
        slam_toolbox_node,
        nav2_launch,
        rviz_node
    ])
