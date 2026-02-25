from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():

    pkg_nav_bringup = get_package_share_directory("nav_bringup")
    nav2_params = os.path.join(pkg_nav_bringup, "config", "nav2_params.yaml")

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

    return LaunchDescription([
        nav2_launch
    ])
