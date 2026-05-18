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
        key = sys.stdin.read(1)
        if key == '\x1b':
            key += sys.stdin.read(2)
        return key
    def emergency_stop(self):
        self.pub.publish(Twist())                
        self.estop_pub.publish(Bool(data=True)) 
        print("⚠️ EMERGENCY STOP")
    def run(self):
        print("\n====== TELEOP CONTROL ======")
        print("W / ↑ : Move Forward")
        print("S / ↓ : Move Backward")
        print("A / ← : Turn Left")
        print("D / → : Turn Right")
        print("+     : Increase Speed")
        print("-     : Decrease Speed")
        print("r     : Reset Encoders")
        print("e     : Emergency Stop")
        print("SPACE : Stop")
        print("q     : Quit\n")
        try:
            while True:
                key = self.get_key()
                msg = Twist()
                if key == 'w' or key == '\x1b[A':     
                    msg.linear.x = self.speed

                elif key == 's' or key == '\x1b[B':  
                    msg.linear.x = -self.speed

                elif key == 'a' or key == '\x1b[D':   
                    msg.angular.z = self.turn

                elif key == 'd' or key == '\x1b[C':   
                    msg.angular.z = -self.turn


                elif key == '+':

                    self.speed = min(1.0, self.speed + self.step)
                    self.turn = min(2.0, self.turn + self.step)

                    print(f"⬆️ Speed Increased : {self.speed:.2f}")

                elif key == '-':

                    self.speed = max(0.0, self.speed - self.step)
                    self.turn = max(0.0, self.turn - self.step)

                    print(f"⬇️ Speed Decreased : {self.speed:.2f}")

                # ----- Reset Encoders -----

                elif key == 'r':

                    self.reset_pub.publish(Bool(data=True))

                    print("🔄 Encoders Reset")

                # ----- Emergency Stop -----

                elif key == 'e':

                    self.emergency_stop()
                    continue

                # ----- Space Bar Stop -----

                elif key == ' ':

                    msg = Twist()

                # ----- Quit -----

                elif key == 'q':

                    break

                # Publish movement command
                self.pub.publish(msg)

        finally:

            # Stop robot before exit
            self.pub.publish(Twist())

            # Restore terminal settings
            termios.tcsetattr(
                sys.stdin,
                termios.TCSADRAIN,
                self.settings
            )


def main():

    rclpy.init()

    node = SimpleTeleop()

    node.run()

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()
