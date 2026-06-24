#!/usr/bin/env python3
import rospy
import tf2_ros
from geometry_msgs.msg import TransformStamped

if __name__ == '__main__':
    rospy.init_node('handeye_transform_node')
    cfg = rospy.get_param('/handeye', {})
    if not cfg.get('publish_static_tf', True):
        rospy.spin()
    br = tf2_ros.StaticTransformBroadcaster()
    t = TransformStamped()
    t.header.stamp = rospy.Time.now()
    t.header.frame_id = cfg.get('base_frame','base_link')
    t.child_frame_id = cfg.get('camera_frame','camera_color_optical_frame')
    xyz = cfg.get('translation_xyz',[0,0,0]); q = cfg.get('rotation_xyzw',[0,0,0,1])
    t.transform.translation.x, t.transform.translation.y, t.transform.translation.z = map(float, xyz)
    t.transform.rotation.x, t.transform.rotation.y, t.transform.rotation.z, t.transform.rotation.w = map(float, q)
    br.sendTransform(t)
    rospy.loginfo('Published static handeye TF %s -> %s', t.header.frame_id, t.child_frame_id)
    rospy.spin()
