import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    urdf_path = os.path.join(get_package_share_directory('megabot'), 'urdf', 'mws.urdf')

    spwan_mws = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-entity', 'RISE_WheelChair',  
            '-file', urdf_path,
            '-timeout', '300'   
        ],
        output='screen',  
    )

    transformation=Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_transform_publisher',
            output='screen',
            arguments=['0', '0', '0', '0', '0', '0', 'base_footprint', 'base_link']
        )
    
    transformation1=Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_transform_publisher',
            output='screen',
            arguments=['0', '0', '0', '0', '0', '0', 'odom', 'base_footprint']
        )

    ld = LaunchDescription()
    ld.add_action(spwan_mws) 
   # ld.add_action(transformation)
    # ld.add_action(transformation1) 

    return ld
