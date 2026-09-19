# ROS 2 MoveIt 2 机械臂控制

这是一个基于 ROS 2 Jazzy 和 MoveIt 2 的六自由度机械臂示例工程，包含机械臂 URDF/Xacro 描述、MoveIt 配置、ros2_control 仿真控制器，以及 C++ 控制节点。

当前工程使用 `mock_components/GenericSystem` 作为 ros2_control 硬件，因此可以在没有真实机械臂的情况下完成运动规划和轨迹执行测试。

## 功能

- 六个关节的机械臂模型和一个平行夹爪
- URDF/Xacro 模型描述和 RViz 可视化
- MoveIt 2 运动规划
- `ros2_control` 模拟硬件和关节轨迹控制器
- 机械臂关节目标、位姿目标和笛卡尔路径控制
- 夹爪打开与关闭控制
- 自定义 `PoseCommand` 消息

## 环境

- Ubuntu 24.04
- ROS 2 Jazzy
- MoveIt 2
- `colcon`
- C++ 编译器和 CMake

安装常用依赖：

```bash
sudo apt update
sudo apt install \
  ros-jazzy-moveit \
  ros-jazzy-xacro \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-controller-manager \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-example-interfaces
```

## 工作区结构

```text
src/
├── my_robot_description/       # URDF/Xacro、RViz 配置和模型展示启动文件
├── my_robot_interfaces/        # 自定义 ROS 2 消息
├── my_robot_moveit_config/     # SRDF、运动学、规划器和 MoveIt 启动文件
├── my_robot_bringup/            # 一键启动机器人、控制器、MoveIt 和 RViz
├── my_robot_commander_cpp/      # C++ MoveIt 控制节点
└── my_robot_commander_py/       # Python 控制节点模板
```

## 编译

本仓库的 Git 根目录是 `src`，但编译命令应在工作区根目录 `~/ros2_ws` 执行。

如果当前终端显示 `(base)`，建议先退出 Conda，避免 Conda 的 Python 或动态库覆盖 ROS 2 Jazzy 的系统依赖：

```bash
conda deactivate
source /opt/ros/jazzy/setup.bash
```

然后编译：

```bash
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash
```

如果只修改了接口包或 C++ 控制节点，可以使用：

```bash
colcon build --packages-up-to my_robot_commander_cpp --symlink-install
source install/setup.bash
```

## 一键启动

一键启动机器人模型、ros2_control 控制器、MoveIt、C++ commander 和 RViz：

```bash
cd ~/ros2_ws
source install/setup.bash
ros2 launch my_robot_bringup robot.launch.xml
```

启动后可以检查控制器：

```bash
ros2 control list_controllers
```

正常情况下应包含以下活动控制器：

```text
joint_state_broadcaster
arm_controller
gripper_controller
```

检查 MoveIt 使用的轨迹 action：

```bash
ros2 action list | grep follow_joint_trajectory
```

## 分开启动

只查看机械臂模型：

```bash
ros2 launch my_robot_description display.launch.py
```

只启动 MoveIt 的演示配置：

```bash
ros2 launch my_robot_moveit_config demo.launch.py
```

也可以分别启动 MoveIt 和 RViz：

```bash
ros2 launch my_robot_moveit_config move_group.launch.py
ros2 launch my_robot_moveit_config moveit_rviz.launch.py
```

不要在已经运行 `robot.launch.xml` 时再次启动这些节点，否则可能出现重复的 RViz、robot state publisher 或 MoveIt 节点。

## 控制接口

### 打开和关闭夹爪

`/open_gripper` 使用 `example_interfaces/msg/Bool`：

```bash
# 关闭夹爪
ros2 topic pub --once /open_gripper example_interfaces/msg/Bool "{data: false}"

# 打开夹爪
ros2 topic pub --once /open_gripper example_interfaces/msg/Bool "{data: true}"
```

### 发送关节目标

`/joint_command` 使用 `example_interfaces/msg/Float64MultiArray`，数组顺序为 `joint1` 到 `joint6`：

```bash
ros2 topic pub --once /joint_command \
  example_interfaces/msg/Float64MultiArray \
  "{data: [0.0, 0.3, 0.5, 0.0, 0.2, 0.0]}"
```

### 发送位姿目标

`/pose_command` 使用自定义消息 `my_robot_interfaces/msg/PoseCommand`，位置单位为米，角度单位为弧度：

```bash
ros2 topic pub --once /pose_command \
  my_robot_interfaces/msg/PoseCommand \
  "{x: 0.7, y: 0.0, z: 0.4, roll: 3.14, pitch: 0.0, yaw: 0.0, cartesian_path: false}"
```

设置 `cartesian_path: true` 时，控制节点会尝试使用笛卡尔路径执行目标。

查看自定义消息定义：

```bash
ros2 interface show my_robot_interfaces/msg/PoseCommand
```

## C++ 控制节点

启动 C++ commander：

```bash
ros2 run my_robot_commander_cpp commander
```

该节点订阅以下话题：

| 话题 | 消息类型 | 用途 |
| --- | --- | --- |
| `/open_gripper` | `example_interfaces/msg/Bool` | 打开或关闭夹爪 |
| `/joint_command` | `example_interfaces/msg/Float64MultiArray` | 发送六个关节目标 |
| `/pose_command` | `my_robot_interfaces/msg/PoseCommand` | 发送末端位姿目标 |

## 常见问题

### `my_robot_interfaces` 找不到

确认接口包已经编译，并重新加载工作区环境：

```bash
colcon build --packages-select my_robot_interfaces my_robot_commander_cpp
source install/setup.bash
```

### `Action client not connected to action server: arm_controller/follow_joint_trajectory`

这表示 MoveIt 已经完成规划，但没有找到轨迹控制器。确认 `ros2_control` 正在运行，并且 `arm_controller` 的类型是：

```yaml
joint_trajectory_controller/JointTrajectoryController
```

### CMake 找到了 Conda Python 或 Conda 动态库

先执行：

```bash
conda deactivate
source /opt/ros/jazzy/setup.bash
colcon build --symlink-install
```

### 只运行 `robot_state_publisher`

直接把多行 xacro 输出放进 `-p robot_description:=...` 可能触发 ROS 2 YAML 解析错误。推荐使用本项目的 launch 文件，或先生成 URDF 文件：

```bash
xacro src/my_robot_description/urdf/my_robot.urdf.xacro -o /tmp/my_robot.urdf
ros2 run robot_state_publisher robot_state_publisher /tmp/my_robot.urdf
```

## 许可证

本项目目前用于学习和实验。各 ROS 2 依赖包的许可证以其官方项目声明为准。
