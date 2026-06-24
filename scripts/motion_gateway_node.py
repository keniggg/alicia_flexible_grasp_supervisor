#!/usr/bin/env python3
import rospy
from std_msgs.msg import Bool
from alicia_flexible_grasp.robot.joint_commander import JointCommander
from alicia_flexible_grasp.robot.gripper_commander import GripperCommander
from alicia_flexible_grasp.robot.moveit_planner import MoveItPlanner
from alicia_flexible_grasp.robot.cartesian_controller import CartesianJogger
from alicia_flexible_grasp_supervisor.srv import SetJointCommand, SetJointCommandResponse, SetFloat, SetFloatResponse, SetTargetPose, SetTargetPoseResponse, CartesianJog, CartesianJogResponse, TriggerZero, TriggerZeroResponse

class MotionGateway:
    def __init__(self):
        cfg = rospy.get_param('/robot', {})
        self.joint_names = cfg.get('joint_names', ['Joint1','Joint2','Joint3','Joint4','Joint5','Joint6','right_finger'])
        self.joint_cmd = JointCommander(cfg.get('joint_command_topic','/joint_commands'), self.joint_names)
        self.gripper = GripperCommander(self.joint_cmd, len(self.joint_names)-1, cfg.get('gripper_min_m',0.0), cfg.get('gripper_max_m',0.05))
        self.zero_pub = rospy.Publisher(cfg.get('zero_calibrate_topic','/zero_calibrate'), Bool, queue_size=1)
        self.demo_pub = rospy.Publisher(cfg.get('demonstration_topic','/demonstration'), Bool, queue_size=1)
        self.planner = MoveItPlanner(rospy.get_param('~manipulator_group','alicia'), rospy.get_param('~gripper_group','hand'), rospy.get_param('~velocity',0.3))
        self.jogger = CartesianJogger(self.planner)
        rospy.Service('/supervisor/move_to_joints', SetJointCommand, self.handle_joints)
        rospy.Service('/supervisor/set_gripper', SetFloat, self.handle_gripper)
        rospy.Service('/supervisor/move_to_pose', SetTargetPose, self.handle_pose)
        rospy.Service('/supervisor/cartesian_jog', CartesianJog, self.handle_jog)
        rospy.Service('/supervisor/trigger_zero', TriggerZero, self.handle_zero)
        rospy.loginfo('MotionGateway ready: commands -> %s', cfg.get('joint_command_topic','/joint_commands'))

    def handle_joints(self, req):
        if req.execute:
            self.joint_cmd.publish(req.positions)
            return SetJointCommandResponse(True, 'published to /joint_commands')
        ok,msg = self.planner.move_to_joints(req.positions, execute=False)
        return SetJointCommandResponse(ok, msg)

    def handle_gripper(self, req):
        self.gripper.set_position(req.value)
        return SetFloatResponse(True, 'gripper command published')

    def handle_pose(self, req):
        ok,msg = self.planner.move_to_pose(req.target, execute=req.execute)
        return SetTargetPoseResponse(ok, msg)

    def handle_jog(self, req):
        ok,msg = self.jogger.jog(req.dx, req.dy, req.dz, req.droll, req.dpitch, req.dyaw, execute=req.execute)
        return CartesianJogResponse(ok, msg)

    def handle_zero(self, req):
        if req.trigger:
            self.zero_pub.publish(Bool(True))
        return TriggerZeroResponse(True, 'zero command sent')

if __name__ == '__main__':
    rospy.init_node('motion_gateway_node')
    MotionGateway()
    rospy.spin()
