import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default=False)
    launch_file_dir = os.path.join(get_package_share_directory('megabot'), 'launch')
    urdf_path = os.path.join(get_package_share_directory('megabot'), 'urdf', 'mws.urdf')

    return LaunchDescription([
        DeclareLaunchArgument(
            name='use_sim_time',
            default_value='false',  # Default value should be a string
            description='Flag to enable ROS2 sim time'
        ),

        DeclareLaunchArgument(
            name='rviz_config',
            default_value=os.path.join(get_package_share_directory('megabot'), 'rviz', 'mws1.rviz'),
            description='RViz configuration file path'
        ),


        Node(
            package='rviz2',
            executable='rviz2',
            output='screen',
            arguments=['-d', LaunchConfiguration('rviz_config')]
            ),


        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
            arguments=[urdf_path]  # Pass URDF file path as an argument
        )
    ])
