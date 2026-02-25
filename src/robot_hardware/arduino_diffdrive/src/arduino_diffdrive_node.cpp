#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>
#include <nav_msgs/msg/odometry.hpp>
#include <tf2_ros/transform_broadcaster.h>
#include <geometry_msgs/msg/transform_stamped.hpp>

#include <termios.h>
#include <fcntl.h>
#include <unistd.h>
#include <string>
#include <cmath>
#include <chrono>

using namespace std::chrono_literals;

class ArduinoDiffDriveNode : public rclcpp::Node
{
public:
  ArduinoDiffDriveNode() : Node("arduino_diffdrive_node")
  {
    // ----------------------------
    // Parameters
    // ----------------------------
    this->declare_parameter<std::string>("port", "/dev/ttyACM0");
    this->declare_parameter<int>("baud", 115200);

    this->declare_parameter<double>("wheel_diameter", 0.07);  // 7 cm
    this->declare_parameter<double>("wheel_base", 0.30);      // 30 cm
    this->declare_parameter<int>("pwm_min", 80);
    this->declare_parameter<int>("pwm_max", 255);

    this->declare_parameter<double>("max_linear_speed", 0.5);   // m/s
    this->declare_parameter<double>("max_angular_speed", 1.0);  // rad/s

    this->get_parameter("wheel_diameter", wheel_diameter_);
    this->get_parameter("wheel_base", wheel_base_);
    this->get_parameter("pwm_min", pwm_min_);
    this->get_parameter("pwm_max", pwm_max_);
    this->get_parameter("max_linear_speed", max_linear_speed_);
    this->get_parameter("max_angular_speed", max_angular_speed_);

    std::string port;
    int baud;
    this->get_parameter("port", port);
    this->get_parameter("baud", baud);

    // ----------------------------
    // Serial Open
    // ----------------------------
    serial_fd_ = openSerial(port, baud);
    if (serial_fd_ < 0)
    {
      RCLCPP_ERROR(this->get_logger(), "Failed to open serial port: %s", port.c_str());
    }
    else
    {
      RCLCPP_INFO(this->get_logger(), "Serial connected: %s @ %d", port.c_str(), baud);
    }

    // ----------------------------
    // Publishers/Subscribers
    // ----------------------------
    cmd_sub_ = this->create_subscription<geometry_msgs::msg::Twist>(
      "/cmd_vel", 10,
      std::bind(&ArduinoDiffDriveNode::cmdVelCallback, this, std::placeholders::_1));

    odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("/odom", 10);

    tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);

    // ----------------------------
    // Timer for publishing odom + tf
    // ----------------------------
    last_time_ = this->now();
    odom_timer_ = this->create_wall_timer(
      50ms, std::bind(&ArduinoDiffDriveNode::publishOdomTF, this)); // 20Hz

    RCLCPP_INFO(this->get_logger(), "Arduino DiffDrive Node started.");
  }

  ~ArduinoDiffDriveNode()
  {
    if (serial_fd_ >= 0)
      close(serial_fd_);
  }

private:
  // ----------------------------
  // Serial Functions
  // ----------------------------
  int openSerial(const std::string &port, int baud)
  {
    int fd = open(port.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd == -1)
      return -1;

    termios options;
    tcgetattr(fd, &options);

    speed_t speed;
    switch (baud)
    {
    case 9600: speed = B9600; break;
    case 57600: speed = B57600; break;
    case 115200: speed = B115200; break;
    default: speed = B115200; break;
    }

    cfsetispeed(&options, speed);
    cfsetospeed(&options, speed);

    options.c_cflag |= (CLOCAL | CREAD);
    options.c_cflag &= ~PARENB;
    options.c_cflag &= ~CSTOPB;
    options.c_cflag &= ~CSIZE;
    options.c_cflag |= CS8;

    options.c_lflag &= ~(ICANON | ECHO | ECHOE | ISIG);
    options.c_iflag &= ~(IXON | IXOFF | IXANY);
    options.c_oflag &= ~OPOST;

    tcsetattr(fd, TCSANOW, &options);

    return fd;
  }

  void sendPWM(int left_pwm, int right_pwm)
  {
    if (serial_fd_ < 0) return;

    std::string cmd = "V " + std::to_string(left_pwm) + " " + std::to_string(right_pwm) + "\n";
    write(serial_fd_, cmd.c_str(), cmd.size());
  }

  // ----------------------------
  // PWM Mapping
  // ----------------------------
  int mapSpeedToPWM(double speed, double max_speed)
  {
    if (std::abs(speed) < 0.001)
      return 0;

    double ratio = std::abs(speed) / max_speed;
    if (ratio > 1.0) ratio = 1.0;

    int pwm = pwm_min_ + (int)((pwm_max_ - pwm_min_) * ratio);

    if (pwm > pwm_max_) pwm = pwm_max_;
    if (pwm < pwm_min_) pwm = pwm_min_;

    if (speed < 0) pwm = -pwm;

    return pwm;
  }

  // ----------------------------
  // cmd_vel callback
  // ----------------------------
  void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg)
  {
    double v = msg->linear.x;
    double w = msg->angular.z;

    // Clamp
    if (v > max_linear_speed_) v = max_linear_speed_;
    if (v < -max_linear_speed_) v = -max_linear_speed_;

    if (w > max_angular_speed_) w = max_angular_speed_;
    if (w < -max_angular_speed_) w = -max_angular_speed_;

    // Differential drive kinematics
    // v_left = v - w*(wheel_base/2)
    // v_right = v + w*(wheel_base/2)
    double v_left = v - (w * wheel_base_ / 2.0);
    double v_right = v + (w * wheel_base_ / 2.0);

    // Convert wheel linear speed -> PWM
    int left_pwm = mapSpeedToPWM(v_left, max_linear_speed_);
    int right_pwm = mapSpeedToPWM(v_right, max_linear_speed_);

    // Send to Arduino
    sendPWM(left_pwm, right_pwm);

    // Store last commanded velocities for odom simulation
    current_v_ = v;
    current_w_ = w;

    RCLCPP_INFO(this->get_logger(), "cmd_vel: v=%.2f w=%.2f => PWM L=%d R=%d",
                v, w, left_pwm, right_pwm);
  }

  // ----------------------------
  // Fake Odom + TF publisher (without encoder)
  // ----------------------------
  void publishOdomTF()
  {
    rclcpp::Time now = this->now();
    double dt = (now - last_time_).seconds();
    last_time_ = now;

    // integrate pose
    double delta_x = current_v_ * std::cos(theta_) * dt;
    double delta_y = current_v_ * std::sin(theta_) * dt;
    double delta_th = current_w_ * dt;

    x_ += delta_x;
    y_ += delta_y;
    theta_ += delta_th;

    // quaternion
    double qz = std::sin(theta_ / 2.0);
    double qw = std::cos(theta_ / 2.0);

    // ----------------------------
    // Publish Odometry
    // ----------------------------
    nav_msgs::msg::Odometry odom;
    odom.header.stamp = now;
    odom.header.frame_id = "odom";
    odom.child_frame_id = "base_link";

    odom.pose.pose.position.x = x_;
    odom.pose.pose.position.y = y_;
    odom.pose.pose.position.z = 0.0;

    odom.pose.pose.orientation.z = qz;
    odom.pose.pose.orientation.w = qw;

    odom.twist.twist.linear.x = current_v_;
    odom.twist.twist.angular.z = current_w_;

    odom_pub_->publish(odom);

    // ----------------------------
    // Publish TF (odom -> base_link)
    // ----------------------------
    geometry_msgs::msg::TransformStamped t;
    t.header.stamp = now;
    t.header.frame_id = "odom";
    t.child_frame_id = "base_link";

    t.transform.translation.x = x_;
    t.transform.translation.y = y_;
    t.transform.translation.z = 0.0;

    t.transform.rotation.z = qz;
    t.transform.rotation.w = qw;

    tf_broadcaster_->sendTransform(t);
  }

private:
  // ROS2
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_sub_;
  rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
  rclcpp::TimerBase::SharedPtr odom_timer_;
  std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

  // Serial
  int serial_fd_ = -1;

  // Robot params
  double wheel_diameter_ = 0.07;
  double wheel_base_ = 0.30;
  int pwm_min_ = 80;
  int pwm_max_ = 255;

  double max_linear_speed_ = 0.5;
  double max_angular_speed_ = 1.0;

  // Fake odom state
  double x_ = 0.0;
  double y_ = 0.0;
  double theta_ = 0.0;

  double current_v_ = 0.0;
  double current_w_ = 0.0;

  rclcpp::Time last_time_;
};

int main(int argc, char *argv[])
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<ArduinoDiffDriveNode>());
  rclcpp::shutdown();
  return 0;
}
