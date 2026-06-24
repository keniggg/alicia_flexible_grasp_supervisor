#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Image
try:
    from cv_bridge import CvBridge
except Exception:
    CvBridge = None
from alicia_flexible_grasp.vision.realsense_manager import RealSenseManager

class CameraNode:
    def __init__(self):
        cfg = rospy.get_param('/camera', {})
        self.color_topic = cfg.get('color_topic', '/supervisor/camera/color/image_raw')
        self.depth_topic = cfg.get('depth_topic', '/supervisor/camera/depth/image_raw')
        self.frame_id = cfg.get('frame_id', 'camera_color_optical_frame')
        self.bridge = CvBridge() if CvBridge else None
        self.pub_color = rospy.Publisher(self.color_topic, Image, queue_size=2)
        self.pub_depth = rospy.Publisher(self.depth_topic, Image, queue_size=2)
        simulate = bool(cfg.get('simulate', False))
        self.cam = RealSenseManager(cfg.get('width',640), cfg.get('height',480), cfg.get('fps',30), cfg.get('align_depth_to_color',True), simulate=simulate)
        try:
            self.cam.start()
            rospy.loginfo('Camera started: color=%s depth=%s', self.color_topic, self.depth_topic)
        except Exception as exc:
            rospy.logerr('Camera start failed: %s. Falling back to simulated camera.', exc)
            self.cam = RealSenseManager(cfg.get('width',640), cfg.get('height',480), cfg.get('fps',30), True, simulate=True)
            self.cam.start()
        self.rate = rospy.Rate(float(cfg.get('fps',30)))

    def publish_image(self, pub, cv_img, encoding):
        if self.bridge is None:
            return
        msg = self.bridge.cv2_to_imgmsg(cv_img, encoding=encoding)
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = self.frame_id
        pub.publish(msg)

    def spin(self):
        while not rospy.is_shutdown():
            color, depth = self.cam.read()
            if color is not None:
                self.publish_image(self.pub_color, color, 'bgr8')
            if depth is not None:
                self.publish_image(self.pub_depth, depth, '16UC1')
            self.rate.sleep()

if __name__ == '__main__':
    rospy.init_node('camera_node')
    node = CameraNode()
    rospy.on_shutdown(node.cam.stop)
    node.spin()
