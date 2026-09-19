import launch
import launch_ros
import xacro
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    # 获取包的共享目录路径
    pkg_share = get_package_share_directory('my_robot_description')
    # 构建xacro文件的完整路径
    xacro_file = os.path.join(pkg_share, 'urdf', 'my_robot.urdf.xacro')
    
    # 使用xacro处理文件并获取解析后的URDF内容
    robot_description_config = xacro.process_file(xacro_file)
    # 将解析后的URDF内容转换为字符串
    robot_description = {'robot_description': robot_description_config.toxml()}
    
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'urdf_config.rviz')
    

    # 创建robot_state_publisher节点，传入解析后的URDF内容
    robot_pub = launch_ros.actions.Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[robot_description])
    
    # 创建joint_state_publisher_gui节点
    joint_pub = launch_ros.actions.Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen')
    
    # 创建rviz2节点
    rviz2 = launch_ros.actions.Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', rviz_config_file]
        )

    return launch.LaunchDescription([
        robot_pub,
        joint_pub,
        rviz2,
    ])