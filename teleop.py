#!/usr/bin/env python3
import sys
import termios
import tty
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
class SimpleTeleop(Node):
    def __init__(self):
        super().__init__('simple_teleop')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.reset_pub = self.create_publisher(Bool, '/reset_encoders', 10)
        self.estop_pub = self.create_publisher(Bool, '/estop', 10)
        self.speed = 0.2
        self.turn = 0.5
        self.step = 0.05
        self.settings = termios.tcgetattr(sys.stdin)

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        return sys.stdin.read(1)

    def emergency_stop(self):
        self.pub.publish(Twist())                # Stop robot motion
        self.estop_pub.publish(Bool(data=True)) # Trigger emergency stop
        print("⚠️ EMERGENCY STOP")

    def run(self):
        print("W/S : Forward/Backward")
        print("A/D : Turn Left/Right")
        print("+/- : Increase/Decrease Speed")
        print("r   : Reset Encoders")
        print("e   : Emergency Stop")
        print("q   : Quit")
        try:
            while True:
                key = self.get_key()
                msg = Twist()
                if key == 'w':
                    msg.linear.x = self.speed
                elif key == 's':
                    msg.linear.x = -self.speed
                elif key == 'a':
                    msg.angular.z = self.turn
                elif key == 'd':
                    msg.angular.z = -self.turn

                elif key == '+':
                    self.speed = min(1.0, self.speed + self.step)
                    self.turn = min(2.0, self.turn + self.step)
                    print(f"Speed Increased : {self.speed:.2f}")
                elif key == '-':
                    self.speed = max(0.0, self.speed - self.step)
                    self.turn = max(0.0, self.turn - self.step)
                    print(f"Speed Decreased : {self.speed:.2f}")

                elif key == 'r':
                    self.reset_pub.publish(Bool(data=True))
                    print("🔄 Encoders Reset")

                elif key == 'e':
                    self.emergency_stop()
                    continue

                elif key == ' ':
                    pass

                elif key == 'q':
                    break

                self.pub.publish(msg)

        finally:
            self.pub.publish(Twist())
            termios.tcsetattr(sys.stdin,termios.TCSADRAIN,self.settings)

def main():
    rclpy.init()
    node = SimpleTeleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()
if __name__ == '__main__':
