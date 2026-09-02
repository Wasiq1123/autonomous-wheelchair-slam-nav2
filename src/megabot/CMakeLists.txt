cmake_minimum_required(VERSION 3.5)
project(megabot)

# Set compiler options
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(gazebo_ros_pkgs REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(robot_state_publisher REQUIRED)

# Uncomment the following section in order to fill in further dependencies manually.
# find_package(<dependency> REQUIRED)

# Find and configure linters for source code
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # The following line skips the linter which checks for copyrights
  # Comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # The following line skips cpplint (only works in a git repo)
  # Comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

## Install
install(DIRECTORY launch worlds urdf config meshes
  DESTINATION share/${PROJECT_NAME}/
)

ament_package()
