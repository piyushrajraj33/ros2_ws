#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"

class FleetManager : public rclcpp::Node
{
public:
    FleetManager() : Node("fleet_manager")
    {
        goal_pub_ = this->create_publisher<geometry_msgs::msg::PoseStamped>(
            "/goal_pose", 10);

        RCLCPP_INFO(this->get_logger(), "Fleet Manager Started");
    }

    void send_goal(double x, double y)
    {
        geometry_msgs::msg::PoseStamped goal;
        goal.header.frame_id = "map";
        goal.header.stamp = now();

        goal.pose.position.x = x;
        goal.pose.position.y = y;
        goal.pose.orientation.w = 1.0;

        goal_pub_->publish(goal);
        RCLCPP_INFO(this->get_logger(), "Goal Sent");
    }

private:
    rclcpp::Publisher<geometry_msgs::msg::PoseStamped>::SharedPtr goal_pub_;
};

int main(int argc, char ** argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<FleetManager>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
