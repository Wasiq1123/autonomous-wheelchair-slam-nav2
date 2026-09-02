# WheelChair_Slam — An Autonomous Wheelchair, From CAD to Navigation

**A differential-drive wheelchair, designed entirely in SolidWorks and exported into ROS 2, taught to map its environment, localize within it, navigate autonomously through Nav2, and see — via onboard YOLOv8 and TensorFlow perception.**

---

## What this project is

Most wheelchairs are manually operated. This project takes a wheelchair from mechanical CAD design through to a fully autonomous mobile robot, entirely in open-source ROS 2 tooling:

1. **Mechanical design → kinematic model.** The wheelchair was modeled from scratch in SolidWorks — chassis, drive wheels, casters, camera mount — with accurate per-link mass and inertia, then exported into a ROS 2 URDF (`mws.urdf`) with matching STL collision/visual meshes for every link.
2. **Simulation.** The URDF is spawned in Gazebo Classic as `RISE_WheelChair`, driven by a differential-drive plugin, sensing the world through a 2D LiDAR and an RGB camera.
3. **Mapping.** GMapping builds a 2D occupancy grid of the environment from LiDAR scans while the robot is driven around.
4. **Localization + navigation.** AMCL localizes the robot against the saved map, and the full Nav2 stack (planner, controller, behavior server, BT navigator) drives it autonomously to goals.
5. **Perception.** Two onboard vision nodes — a YOLOv8 object detector and a TensorFlow/ResNet50 image classifier — run over the live camera feed, laying the groundwork for obstacle- and person-aware navigation.

Every one of these five stages required debugging real integration problems along the way — not just wiring packages together. The sections below describe what those problems were and how they were solved, since that's most of the actual engineering work in a project like this.

---

## Problems solved

Over the course of this project, several TF2/frame-tree issues, Nav2 integration issues, and a perception topic-wiring issue came up and were resolved. A detailed write-up of each problem and its fix is being compiled separately and will be linked here once it's ready.

---

## System overview

| Stage | Approach | Package |
|---|---|---|
| **Mechanical design** | SolidWorks CAD assembly, exported per-link as STL meshes | `megabot/meshes` |
| **Kinematic model** | URDF, differential drive over 4 coupled wheels | `megabot/urdf/mws.urdf` |
| **Simulation** | Gazebo Classic, LiDAR + RGB camera | `megabot/worlds`, `megabot/launch/mws.launch.py` |
| **Mapping** | GMapping (Rao-Blackwellized particle filter SLAM) | `slam_gmapping`, `megabot_nav/launch/gmapping.launch.py` |
| **Localization** | AMCL (adaptive Monte Carlo localization) | `nav2_amcl` via `megabot_nav/launch/localization.launch.py` |
| **Planning & control** | Nav2 — global planner, local controller, behavior server, BT navigator | `megabot_nav/launch/navigation.launch.py` |
| **Mission-level behavior** | Behavior Tree layer over Nav2 goals (patrol, interrupts, snapshots) | `bt_ros2` |
| **Perception** | YOLOv8 object detection + ResNet50/TensorFlow image classification over `/camera/color/image_raw` | `detection` |
| **Perception (reference)** | Earlier YOLOv5 (PyTorch) detection pipeline, kept for comparison | `yolobot_recognition` |

---

## Robot model

| | |
|---|---|
| **Entity name** | `RISE_WheelChair` |
| **Drive** | 4-wheel differential drive, coupled left/right (`libgazebo_ros_diff_drive`) |
| **Wheel separation** | 0.3 m |
| **Wheel diameter** | 0.1 m |
| **Max wheel torque** | 20 N·m |
| **Sensors** | 2D LiDAR, RGB camera |
| **Frames** | `base_link` (root, physical body) → `base_footprint` (fixed) → wheel links → `camera_depth_link` |
| **Source geometry** | SolidWorks assembly (`Modified_Wheelchair111.SLDASM`), exported per-link to STL |

> **Before you build:** `mws.urdf`'s 8 mesh references currently point at an absolute local path — `file:///home/wasiq/testing_model/WheelChair_Slam/src/megabot/meshes/<name>.STL`. That path is specific to the original development machine and won't resolve on a different clone (yours included, once the repo lives at a different location). Before building, either:
> - replace `/home/wasiq/testing_model/WheelChair_Slam/src/megabot/meshes/` in each of the 8 `<mesh filename="file://...">` entries with the actual absolute path to `megabot/meshes/` on your machine, **or** (recommended, and portable across any machine/clone)
> - replace the whole `file:///.../meshes/<name>.STL` prefix with `package://megabot/meshes/<name>.STL` instead — ROS resolves that from the installed package share directory automatically, so it keeps working no matter where the workspace is checked out.

---

## Repository layout

```
src/
├── megabot/            # Robot description, world, sim bring-up
│   ├── config/           ekf.yaml
│   ├── launch/            mws.launch.py, robot_description.launch.py, spwan.launch.py
│   ├── meshes/             SolidWorks-exported STL links
│   ├── urdf/                mws.urdf   ← update mesh paths here, see above
│   └── worlds/                mws.world, mws1.world, mws2.world, sonoma.sdf
├── megabot_nav/        # SLAM, localization, and Nav2 bring-up
│   ├── launch/            gmapping.launch.py, localization.launch.py, navigation.launch.py, rtabmap.launch.py
│   ├── map/                mememan.pgm / .yaml
│   └── param/                mws_params.yaml
├── detection/           # YOLOv8 + TensorFlow/ResNet50 perception nodes, subscribing to /camera/color/image_raw
├── yolobot_recognition/  # YOLOv5 (PyTorch) reference detection pipeline
├── slam_gmapping/         # GMapping SLAM (ROS 2 port of OpenSLAM)
├── nav2_bringup/            # Upstream Nav2 bring-up reference package
├── nav2_simple_commander/     # Python API for scripting Nav2 goals
├── bt_ros2/                     # Behavior Tree layer over Nav2
└── aws_robomaker_small_warehouse_world/  # Extra Gazebo world for testing
```

`build/`, `install/`, and `log/` are colcon-generated — add a `.gitignore` for these before pushing.

---

## Usage

```bash
# 1. Simulation + robot spawn
ros2 launch megabot mws.launch.py

# 2. Mapping — drive the robot around with teleop, GMapping builds the map
#    (use_sim_time:=true is required here — see "TF2 and frame-tree issues" above)
ros2 launch megabot_nav gmapping.launch.py open_rviz:=true use_sim_time:=true
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# 3. Save the map once you're happy with coverage
ros2 run nav2_map_server map_saver_cli -f ~/maps/my_room

# 4. Localization + navigation against the saved map — two terminals
ros2 launch megabot_nav localization.launch.py use_sim_time:=true map:=/home/you/maps/my_room.yaml
ros2 launch megabot_nav navigation.launch.py use_sim_time:=true

# 5. Onboard perception, over the live camera feed
ros2 run detection yolov8
ros2 run detection tensorflow_detection
```

---

## Acknowledgments

The SLAM and Nav2 launch/parameter structure in `megabot_nav` (mapping → localization → navigation as separate, composable launch files; the AMCL/costmap/BT-navigator parameter layout in `mws_params.yaml`) builds on the pattern established by ADLINK Technology's **[NeuronBot2](https://github.com/Adlink-ROS/neuronbot2)** project — `bt_ros2`, included in this repo, is NeuronBot2's Behavior Tree layer over Nav2, adapted here to drive this wheelchair's own goals instead. `nav2_bringup` and `nav2_simple_commander` are from the [Nav2 project](https://github.com/ros-navigation/navigation2). `slam_gmapping`/`openslam_gmapping` is the standard ROS 2 port of OpenSLAM's GMapping. `aws_robomaker_small_warehouse_world` is from [AWS RoboMaker](https://github.com/aws-robotics/aws-robomaker-small-warehouse-world). The YOLOv8 detection node builds on [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics); `yolobot_recognition` builds on [Ultralytics YOLOv5](https://github.com/ultralytics/yolov5) (GPL-3.0 — check licensing terms before redistributing).

## License

`megabot`, `megabot_nav`, `detection` — add your preferred license before publishing. Vendored packages retain their original upstream licenses (Apache-2.0 / GPL-3.0 per package).
