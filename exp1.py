#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Int32
import math, time
WHEEL_DIAMETER = 0.13
PULSES_PER_REV = 740
WHEEL_BASE     = 0.40
TICKS_PER_METER = PULSES_PER_REV / (math.pi * WHEEL_DIAMETER)
TURN_MULTIPLIER = 1.7
LINEAR_SPEED  = 0.12
ANGULAR_SPEED = 0.3
class ArjunaNav(Node):
    def __init__(self):
        super().__init__('arjuna_nav')
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.create_subscription(Int32, '/FL_ticks', self.fl_callback, 10)
        self.create_subscription(Int32, '/FR_ticks', self.fr_callback, 10)
        self.fl_ticks = 0
        self.fr_ticks = 0
        self.get_logger().info("Navigation node ready")
    def fl_callback(self, msg):
        self.fl_ticks = msg.data
    def fr_callback(self, msg):
        self.fr_ticks = msg.data
    def spin_once(self):
        rclpy.spin_once(self, timeout_sec=0.02)
    def move(self, distance_m):
        target_ticks = abs(distance_m) * TICKS_PER_METER
        start_fl = self.fl_ticks
        start_fr = self.fr_ticks
        cmd = Twist()
        cmd.linear.x = LINEAR_SPEED if distance_m > 0 else -LINEAR_SPEED
        start_time = time.time()
        while True:
            self.spin_once()
            travelled = abs((self.fl_ticks - start_fl) +
                            (self.fr_ticks - start_fr)) / 2.0
            if travelled >= target_ticks:
                break
            if time.time() - start_time > 8:
                self.get_logger().warn("Move timeout!")
                break
            self.cmd_pub.publish(cmd)
        self.stop()
    def turn(self, angle_deg):
        arc_length = (WHEEL_BASE / 2.0) * math.radians(abs(angle_deg))
        target_ticks = arc_length * TICKS_PER_METER * TURN_MULTIPLIER
        start_fl = self.fl_ticks
        start_fr = self.fr_ticks
        cmd = Twist()
        cmd.angular.z = ANGULAR_SPEED if angle_deg > 0 else -ANGULAR_SPEED
        start_time = time.time()
        while True:
            self.spin_once()
            turned = (abs(self.fl_ticks - start_fl) + abs(self.fr_ticks - start_fr)) / 2.0
            if turned >= target_ticks:
                break
            if time.time() - start_time > 5:
                self.get_logger().warn("Turn timeout!")
                break
            self.cmd_pub.publish(cmd)
        self.stop()
    def stop(self):
        self.cmd_pub.publish(Twist())
    def pause(self, seconds):
        time.sleep(seconds)
def main(args=None):
    rclpy.init(args=args)
    robot = ArjunaNav()
    for _ in range(20):
        robot.spin_once()
    robot.move(1.0)
    robot.pause(0.5)
    robot.turn(90)
    robot.pause(0.5)
    robot.move(0.5)
    robot.pause(0.5)
    robot.turn(-90)
    robot.pause(0.5)
    robot.move(1.0)
    robot.pause(0.5)
    robot.turn(90)
    robot.pause(0.5)
    robot.move(0.5)
    robot.pause(0.5)
    robot.turn(-90)
    robot.pause(0.5)
    robot.move(1.0)
    robot.stop()
    robot.get_logger().info("GOAL REACHED!")
    robot.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
    main()
