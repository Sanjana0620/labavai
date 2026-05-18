#!/usr/bin/env python3
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
from ament_index_python.packages import get_package_share_directory
import os
def include(pkg, file):
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([FindPackageShare(pkg), 'launch', file])
        ])
    )
def generate_launch_description():
    pkg_dir = get_package_share_directory('arjuna_slam')
    slam_params = os.path.join(pkg_dir, 'config', 'slam_toolbox_config.yaml')
    rviz_config = os.path.join(pkg_dir, 'rviz', 'arjuna_slam.rviz')
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='false'),
        Node(package='arjuna_motor_ops', executable='motor_driver'),
        include('arjuna_odometry', 'odometry.launch.py'),
        include('rplidar_ros', 'rplidar_c1_launch.py'),
        Node(
            package='slam_toolbox',
            executable='async_slam_toolbox_node',
            parameters=[slam_params, {'use_sim_time': use_sim_time}],
            output='screen'
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', rviz_config],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'
        ),
    ])




ros2 run arjuna_motor_dps motor_driver

ros2 run arjuna_controllers teleop-keyboard

ros2 launch arjuna_slam slam_mapping_launch.py

ros2 run nav2_map_server map_saver_cli -f my_map
