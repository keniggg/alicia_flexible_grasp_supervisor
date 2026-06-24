#!/usr/bin/env python3
import rospy
import numpy as np
from sensor_msgs.msg import Image
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Bool
from alicia_flexible_grasp_supervisor.msg import ObjectPose
try:
    from cv_bridge import CvBridge
except Exception:
    CvBridge = None
from alicia_flexible_grasp.vision.object_detector import HSVObjectDetector
from alicia_flexible_grasp.vision.depth_projector import project_pixel_to_3d
from alicia_flexible_grasp.vision.pose_estimator import PoseEstimator

class PerceptionNode:
    def __init__(self):
        cam_cfg = rospy.get_param('/camera', {})
        pcfg = rospy.get_param('/perception', {})
        hcfg = rospy.get_param('/handeye', {})
        gcfg = rospy.get_param('/grasp', {})
        self.bridge = CvBridge() if CvBridge else None
        self.color = None
        self.depth = None
        self.detector = HSVObjectDetector(pcfg.get('hsv_lower',[35,40,40]), pcfg.get('hsv_upper',[85,255,255]), pcfg.get('min_area',300))
        self.fx = float(cam_cfg.get('fx', 615.0)); self.fy = float(cam_cfg.get('fy', 615.0))
        self.cx = float(cam_cfg.get('cx', cam_cfg.get('width',640)/2.0)); self.cy = float(cam_cfg.get('cy', cam_cfg.get('height',480)/2.0))
        self.depth_scale = float(cam_cfg.get('depth_scale', 0.001))
        self.pose_estimator = PoseEstimator(
            hcfg.get('camera_frame','camera_color_optical_frame'),
            hcfg.get('base_frame','base_link'),
            hcfg.get('translation_xyz',[0,0,0]),
            hcfg.get('rotation_xyzw',[0,0,0,1]),
            gcfg.get('default_orientation_xyzw',[0,0.7071,0,0.7071])
        )
        rospy.Subscriber(cam_cfg.get('color_topic','/supervisor/camera/color/image_raw'), Image, self.color_cb, queue_size=1)
        rospy.Subscriber(cam_cfg.get('depth_topic','/supervisor/camera/depth/image_raw'), Image, self.depth_cb, queue_size=1)
        self.pub_obj = rospy.Publisher(pcfg.get('output_object_topic','/perception/object'), ObjectPose, queue_size=10)
        self.pub_cam = rospy.Publisher(pcfg.get('output_pose_camera_topic','/perception/object_pose_camera'), PoseStamped, queue_size=10)
        self.pub_base = rospy.Publisher(pcfg.get('output_pose_base_topic','/perception/object_pose_base'), PoseStamped, queue_size=10)
        self.pub_detected = rospy.Publisher('/perception/object_detected', Bool, queue_size=10)
        self.label = pcfg.get('object_label','target')

    def color_cb(self, msg):
        if not self.bridge: return
        self.color = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        self.try_detect(msg.header.stamp)

    def depth_cb(self, msg):
        if not self.bridge: return
        self.depth = self.bridge.imgmsg_to_cv2(msg, desired_encoding='passthrough')

    def try_detect(self, stamp):
        if self.color is None or self.depth is None:
            return
        det, mask = self.detector.detect(self.color)
        obj = ObjectPose(); obj.header.stamp = stamp; obj.header.frame_id = 'base_link'; obj.label = self.label
        if det is None:
            obj.detected = False
            self.pub_obj.publish(obj); self.pub_detected.publish(Bool(False)); return
        u, v = det['u'], det['v']
        if v >= self.depth.shape[0] or u >= self.depth.shape[1]:
            return
        z = float(self.depth[v, u]) * self.depth_scale
        if z <= 0.01:
            return
        p_cam = project_pixel_to_3d(u, v, z, self.fx, self.fy, self.cx, self.cy)
        pose_cam, pose_base = self.pose_estimator.make_poses(p_cam, stamp)
        obj.detected = True; obj.confidence = float(det.get('confidence', 1.0)); obj.u = u; obj.v = v; obj.depth_m = z
        obj.pose_camera = pose_cam; obj.pose_base = pose_base
        self.pub_cam.publish(pose_cam); self.pub_base.publish(pose_base); self.pub_obj.publish(obj); self.pub_detected.publish(Bool(True))

if __name__ == '__main__':
    rospy.init_node('perception_node')
    node = PerceptionNode()
    rospy.spin()
