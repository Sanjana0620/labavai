#!/usr/bin/env python3
import rclpy, math, time
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32
from sensor_msgs.msg import Imu
WHEEL_DIAMETER = 0.12
PULSES_PER_REV = 660
WHEEL_BASE     = 0.40
TICKS_PER_METER = PULSES_PER_REV / (math.pi * WHEEL_DIAMETER)
LINEAR_SPEED  = 0.25
ANGULAR_SPEED = 0.4
HEADING_TOL   = math.radians(2.0)
class ArjunaHybridNav(Node):
    def __init__(self):
        super().__init__('arjuna_hybrid_nav')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(Int32, '/FL_ticks', self.fl_cb, 10)
        self.create_subscription(Int32, '/FR_ticks', self.fr_cb, 10)
        self.create_subscription(Imu,   '/data',     self.imu_cb, 10)
        self.fl_ticks = 0
        self.fr_ticks = 0
        self.yaw = 0.0
        self.get_logger().info("Hybrid navigation ready")
    def fl_cb(self, msg): self.fl_ticks = msg.data
    def fr_cb(self, msg): self.fr_ticks = msg.data
    def imu_cb(self, msg):
        q = msg.orientation
        self.yaw = math.atan2( 2*(q.w*q.z + q.x*q.y), 1 - 2*(q.y*q.y + q.z*q.z))
    def spin_once(self):
        rclpy.spin_once(self, timeout_sec=0.02)
    def wrap(self, angle):
        return math.atan2(math.sin(angle), math.cos(angle))
    def move(self, distance_m):
        target = abs(distance_m) * TICKS_PER_METER
        sfl, sfr = self.fl_ticks, self.fr_ticks
        cmd = Twist()
        cmd.linear.x = LINEAR_SPEED if distance_m > 0 else -LINEAR_SPEED
        while True:
            self.spin_once()
            travelled = abs((self.fl_ticks - sfl) + (self.fr_ticks - sfr)) / 2.0
            if travelled >= target:
                break
            self.cmd_pub.publish(cmd)
        self.stop()
    def turn(self, angle_deg):
        target_yaw = self.wrap(self.yaw + math.radians(angle_deg))
        cmd = Twist()
        cmd.angular.z = ANGULAR_SPEED if angle_deg > 0 else -ANGULAR_SPEED
        while True:
            self.spin_once()
            error = self.wrap(target_yaw - self.yaw)
            if abs(error) <= HEADING_TOL:
                break
            self.cmd_pub.publish(cmd)
        self.stop()
    def stop(self):
        self.cmd_pub.publish(Twist())
    def pause(self, t):
        time.sleep(t)
def main():
    rclpy.init()
    robot = ArjunaHybridNav()
    for _ in range(30):
        robot.spin_once()
    robot.move(1.5); robot.pause(0.5)
    robot.turn(90);  robot.pause(0.5)
    robot.move(.5); robot.pause(0.5)
    robot.turn(90);  robot.pause(0.5)
    robot.move(.8); robot.pause(0.5)
    robot.turn(-90); robot.pause(0.5)
    robot.move(1.5/2); robot.pause(0.5)
    robot.turn(-90); robot.pause(0.5)
    robot.move(0.5); robot.pause(0.5)
    robot.turn(-90); robot.pause(0.5)
    robot.move(0.5); robot.pause(0.5)
    robot.turn(90);  robot.pause(0.5)
    robot.move(2.5)
    robot.stop()
    robot.get_logger().info("GOAL REACHED!")
    robot.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()
