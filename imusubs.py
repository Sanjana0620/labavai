#!/usr/bin/env python3
import math
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Imu
class ImuHeading(Node):
    def __init__(self):
        super().__init__('imu_heading')
        self.create_subscription(Imu, '/data', self.cb, 10)
        self.initial = None
    def cb(self, msg):
        q = msg.orientation
        yaw = math.degrees(math.atan2(2 * (q.w*q.z + q.x*q.y), 1 - 2 * (q.y*q.y + q.z*q.z)))
        yaw = yaw + 360 if yaw < 0 else yaw
        if self.initial is None:
            self.initial = yaw
        relative = yaw - self.initial
        if relative > 180:
            relative -= 360
        if relative < -180:
            relative += 360
        direction = self.direction(relative)
        self.get_logger().info(f"Heading: {direction} ({relative:.1f}°)")
    def direction(self, angle):
        if abs(angle) < 10:
            return "Straight"
        elif angle > 0:
            return "Right"
        else:
            return "Left"
def main():
    rclpy.init()
    node = ImuHeading()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
if __name__ == '__main__':
    main()





ros2 launch rplidar_ros rplidar_c1_launch.py

ros2 run imu-bno055 bno055_i2c_node

ros2 launch camera_teaching teaching_launch.py

ros2 run arjuna_sensors imu_subscriber

rviz2
