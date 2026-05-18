#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
from Newrro_sensors import Arjuna
OBSTACLE_DIST = 0.5
FWD = 0.3
TURN = 0.5
REG = { 'fl': (0,130),'l': (131,230),  'r': (621,720), 'fr': (721,850)}
class OA(Node):
    def __init__(self):
        super().__init__('oa')
        self.create_subscription(LaserScan, '/scan', self.cb, 10)
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
    def d(self, msg, k):
        s,e = REG[k]
        return Arjuna.LidarRegionChecker.check_region_by_indices(msg,s,e,OBSTACLE_DIST)[0]
    def cb(self, msg):
        fl, fr = self.d(msg,'fl'), self.d(msg,'fr')
        l, r   = self.d(msg,'l'),  self.d(msg,'r')
        t = Twist()
        if min(fl, fr) > OBSTACLE_DIST:
            t.linear.x = FWD
        elif l > r:
            t.angular.z = TURN
        else:
            t.angular.z = -TURN
        self.pub.publish(t)
def main():
    rclpy.init()
    n = OA()
    try: rclpy.spin(n)
    except KeyboardInterrupt: pass
    n.pub.publish(Twist())
    rclpy.shutdown()
if __name__ == '__main__':
    main()





ros2 launch rplidar_ros sflidar_c1_launch.py

ros2 run arjuna_motor_dps motor_driver

ros2 run arjuna_sensors obstacle_avoidance
