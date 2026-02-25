#!/usr/bin/env python3
import subprocess
import time

def run_cmd(cmd):
    try:
        result = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        return result.strip()
    except subprocess.CalledProcessError as e:
        return f"[ERROR]\n{e.output.strip()}"

def section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def main():
    section("ROS2 ROBOT HEALTH CHECK REPORT")
    print("Timestamp:", time.strftime("%Y-%m-%d %H:%M:%S"))

    section("ROS2 ENVIRONMENT CHECK")
    print(run_cmd("printenv | grep ROS"))

    section("NODE LIST")
    print(run_cmd("ros2 node list"))

    section("TOPIC LIST")
    print(run_cmd("ros2 topic list"))

    section("IMPORTANT TOPICS CHECK")
    print(run_cmd("ros2 topic list | egrep 'scan|cmd_vel|odom|tf|tf_static'"))

    section("SCAN TOPIC (one message)")
    print(run_cmd("ros2 topic echo /scan --once"))

    section("SCAN RATE CHECK (5 seconds)")
    print(run_cmd("timeout 6 ros2 topic hz /scan"))

    section("ODOM TOPIC (one message)")
    # print(run_cmd("ros2 topic echo /odom --once"))
    print(run_cmd("timeout 3 ros2 topic echo /odom --once"))
    
    section("CMD_VEL TOPIC (one message)")
    # print(run_cmd("ros2 topic echo /cmd_vel --once"))
    print(run_cmd("timeout 3 ros2 topic echo /cmd_vel --once"))

    section("TF_STATIC CHECK (one message)")
    print(run_cmd("ros2 topic echo /tf_static --once"))

    section("TF CHECK (one message)")
    print(run_cmd("ros2 topic echo /tf --once"))

    section("TF TRANSFORM CHECK base_link -> laser_frame")
    print(run_cmd("timeout 3 ros2 run tf2_ros tf2_echo base_link laser_frame"))

    section("FINAL SUMMARY CHECK")
    nodes = run_cmd("ros2 node list")
    topics = run_cmd("ros2 topic list")

    required_nodes = ["/ydlidar", "/arduino_diffdrive_node"]
    required_topics = ["/scan", "/cmd_vel", "/tf_static"]

    print("Required Nodes:")
    for n in required_nodes:
        print(f"  {n}: {'OK' if n in nodes else 'MISSING'}")

    print("\nRequired Topics:")
    for t in required_topics:
        print(f"  {t}: {'OK' if t in topics else 'MISSING'}")

    section("HEALTH CHECK COMPLETED")

if __name__ == "__main__":
    main()
