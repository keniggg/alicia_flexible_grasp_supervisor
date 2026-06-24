from alicia_flexible_grasp.utils.transform_utils import transform_point, make_pose_stamped

class PoseEstimator:
    def __init__(self, camera_frame, base_frame, translation_xyz, rotation_xyzw, default_orientation_xyzw):
        self.camera_frame = camera_frame
        self.base_frame = base_frame
        self.translation_xyz = translation_xyz
        self.rotation_xyzw = rotation_xyzw
        self.default_orientation_xyzw = default_orientation_xyzw

    def make_poses(self, p_camera_xyz, stamp=None):
        p_base_xyz = transform_point(p_camera_xyz, self.translation_xyz, self.rotation_xyzw)
        pose_cam = make_pose_stamped(self.camera_frame, p_camera_xyz, self.default_orientation_xyzw, stamp)
        pose_base = make_pose_stamped(self.base_frame, p_base_xyz, self.default_orientation_xyzw, stamp)
        return pose_cam, pose_base
