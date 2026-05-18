#!/usr/bin/env python3
import rclpy, cv2, numpy as np
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
from cv2 import moments

class LF(Node):
    def __init__(self):
        super().__init__('lf')
        self.create_subscription(Image,'camera/color/image_raw',self.cb,10)
        self.pub = self.create_publisher(Twist,'/cmd_vel',10)
        self.b = CvBridge()
        self.run, self.kp, self.kd = 0, 0.007, 0.004
        self.spd, self.err, self.w = 0.08, 0, 350

    def dots(self, th, w):
        m = w//2
        ml, mr = moments(th[:,:m]), moments(th[:,m:])
        fl, fr = ml['m00']>500, mr['m00']>500
        lx = int(ml['m10']/ml['m00']) if fl else None
        rx = int(mr['m10']/mr['m00'])+m if fr else None
        if fl and fr: self.w = rx-lx; cx = (lx+rx)//2
        elif fl: cx, rx = lx+self.w//2, lx+self.w
        elif fr: cx, lx = rx-self.w//2, rx-self.w
        else: cx, lx, rx = w//2, w//2-self.w//2, w//2+self.w//2
        return cx, lx, rx

    def cb(self, msg):
        img = self.b.imgmsg_to_cv2(msg,'bgr8')
        h,w = img.shape[:2]
        g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        roi = g[int(.75*h):int(.9*h),:]
        th = cv2.threshold(cv2.GaussianBlur(roi,(5,5),0),0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)[1]
        cx,lx,rx = self.dots(th,w)
        e = w//2 - cx
        ang = self.kp*e + self.kd*(e-self.err)
        self.err = e
        if self.run:
            t = Twist()
            t.linear.x = self.spd
            t.angular.z = float(np.clip(ang,-0.8,0.8))
            self.pub.publish(t)
        y = int(.825*h)
        cv2.circle(img,(lx,y),6,(255,0,0),-1)
        cv2.circle(img,(rx,y),6,(0,0,255),-1)
        cv2.circle(img,(cx,y),4,(0,255,255),-1)
        cv2.line(img,(w//2,h),(cx,y),(0,255,0),2)
        cv2.imshow("lane",img)
        if cv2.waitKey(1)&0xFF==32: self.run ^= 1

def main():
    rclpy.init()
    n = LF()
    try: rclpy.spin(n)
    except KeyboardInterrupt: pass
    n.pub.publish(Twist())
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == '__main__': main()


##ros2 launch lane_following lane_follow.launch.py

##ros2 run arjuna_motor_dps motor_driver

##ros2 run camera_teaching teaching_node.py
