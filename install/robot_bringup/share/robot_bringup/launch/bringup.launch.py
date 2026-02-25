from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():

    arduino_node = Node(
        package="arduino_diffdrive",
        executable="arduino_diffdrive_node",
        name="arduino_diffdrive_node",
        output="screen",
        parameters=[
            {"port": "/dev/ttyACM0"},
            {"baud": 115200},

            {"wheel_diameter": 0.07},   # 7 cm
            {"wheel_base": 0.30},       # 30 cm

            {"pwm_min": 80},
            {"pwm_max": 255},

            {"max_linear_speed": 0.5},
            {"max_angular_speed": 1.0},
        ]
    )

    lidar_node = Node(
        package="ydlidar_ros2_driver",
        executable="ydlidar_ros2_driver_node",
        name="ydlidar",
        output="screen",
        parameters=[
            "/home/car-pi/ros2_ws/src/robot_bringup/config/ydlidar.yaml"
        ]
    )

    static_tf_laser = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="static_tf_laser",
        output="screen",
        arguments=["0.0", "0.0", "0.20", "0", "0", "0", "base_link", "laser_frame"]
    )

    return LaunchDescription([
        arduino_node,
        lidar_node,
        static_tf_laser
    ])
