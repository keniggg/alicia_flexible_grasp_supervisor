import sys
import rospy

class MoveItPlanner:
    def __init__(self, manipulator_group='alicia', gripper_group='hand', velocity=0.3):
        self.ready = False
        self.error = None
        try:
            import moveit_commander
            self.moveit_commander = moveit_commander
            moveit_commander.roscpp_initialize(sys.argv)
            self.robot = moveit_commander.RobotCommander()
            self.scene = moveit_commander.PlanningSceneInterface()
            self.manipulator = moveit_commander.MoveGroupCommander(manipulator_group)
            self.gripper = moveit_commander.MoveGroupCommander(gripper_group)
            self.manipulator.set_max_velocity_scaling_factor(float(velocity))
            self.manipulator.set_max_acceleration_scaling_factor(0.5)
            self.manipulator.set_planning_time(8.0)
            self.manipulator.set_num_planning_attempts(5)
            self.ready = True
        except Exception as exc:
            self.error = str(exc)
            rospy.logwarn('MoveItPlanner not ready: %s', self.error)

    def move_to_pose(self, pose_stamped_or_pose, execute=True):
        if not self.ready:
            return False, self.error or 'MoveIt not ready'
        pose = getattr(pose_stamped_or_pose, 'pose', pose_stamped_or_pose)
        try:
            self.manipulator.set_pose_target(pose)
            if execute:
                ok = self.manipulator.go(wait=True)
                self.manipulator.stop()
                self.manipulator.clear_pose_targets()
                return bool(ok), 'executed' if ok else 'failed'
            plan = self.manipulator.plan()
            self.manipulator.clear_pose_targets()
            return True, 'planned'
        except Exception as exc:
            return False, str(exc)

    def move_to_joints(self, joints, execute=True):
        if not self.ready:
            return False, self.error or 'MoveIt not ready'
        try:
            self.manipulator.set_joint_value_target(list(joints[:6]))
            ok = self.manipulator.go(wait=True) if execute else True
            self.manipulator.stop()
            return bool(ok), 'joint target done' if ok else 'joint target failed'
        except Exception as exc:
            return False, str(exc)

    def get_current_pose(self):
        if not self.ready:
            return None
        return self.manipulator.get_current_pose()
