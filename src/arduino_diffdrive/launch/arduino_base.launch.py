from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    return LaunchDescription([

        Node(
            package="arduino_diffdrive",
            executable="arduino_diffdrive_node",
            name="arduino_diffdrive_node",
            output="screen",
            parameters=[
                {"port": "/dev/ttyUSB0"},
                {"baud": 115200},

                {"wheel_radius": 0.05},
                {"wheel_separation": 0.30},
                {"ticks_per_rev": 600},

                {"base_frame": "base_link"},
                {"odom_frame": "odom"},

                {"publish_tf": True},
                {"rate_hz": 20.0}
            ]
        )

    ])
