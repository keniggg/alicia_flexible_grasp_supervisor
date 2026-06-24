from copy import deepcopy

def make_pregrasp_pose(object_pose, pregrasp_distance=0.08):
    pose = deepcopy(object_pose)
    # 默认从 z 方向上方接近；实际项目可根据夹爪朝向改成沿 TCP approach axis 回退。
    pose.pose.position.z += float(pregrasp_distance)
    return pose

def make_lift_pose(current_pose, lift_height=0.05):
    pose = deepcopy(current_pose)
    pose.pose.position.z += float(lift_height)
    return pose
