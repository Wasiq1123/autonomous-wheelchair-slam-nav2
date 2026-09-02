# Copyright (c) 2021 Samsung Research America
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node


def generate_launch_description():
    warehouse_dir = get_package_share_directory('neuronbot2_nav')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    map_yaml_file = os.path.join(warehouse_dir, 'map','mememan.yaml')
    # Launch configuration variables
    use_rviz = LaunchConfiguration('use_rviz')

    # Declare the launch arguments
    declare_use_rviz_cmd = DeclareLaunchArgument(
        'use_rviz',
        default_value='True',
        description='Whether to start RVIZ')


    # start the visualization
    rviz_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'rviz_launch.py')),
        condition=IfCondition(use_rviz),
        launch_arguments={'namespace': '',
                          'use_namespace': 'False'}.items())

    # start navigation
    bringup_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(nav2_bringup_dir, 'launch', 'bringup_launch.py')),
        launch_arguments={'map': map_yaml_file}.items())

    # start the demo autonomy task
    demo_cmd = Node(
        package='nav2_simple_commander',
        executable='example_nav_through_poses',
        emulate_tty=True,
        output='screen')

    ld = LaunchDescription()
    ld.add_action(declare_use_rviz_cmd)
    ld.add_action(rviz_cmd)
    ld.add_action(bringup_cmd)
    ld.add_action(demo_cmd)
    return ld
