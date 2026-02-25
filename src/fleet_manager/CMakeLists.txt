cmake_minimum_required(VERSION 3.8)
project(fleet_manager)

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)

add_executable(fleet_manager_node src/fleet_manager_node.cpp)

ament_target_dependencies(fleet_manager_node
  rclcpp
  geometry_msgs
)

install(TARGETS
  fleet_manager_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
