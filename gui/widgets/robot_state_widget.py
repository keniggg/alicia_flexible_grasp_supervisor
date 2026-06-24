from PyQt5 import QtWidgets, QtCore
import rospy
from sensor_msgs.msg import JointState

class RobotStateWidget(QtWidgets.QWidget):
    sig = QtCore.pyqtSignal(object)
    def __init__(self, topic='/joint_states'):
        super().__init__()
        layout=QtWidgets.QVBoxLayout(self)
        self.text=QtWidgets.QTextEdit(); self.text.setReadOnly(True); self.text.setMaximumHeight(190)
        layout.addWidget(QtWidgets.QLabel('机械臂关节状态：%s'%topic)); layout.addWidget(self.text)
        self.sig.connect(self.update_state)
        rospy.Subscriber(topic, JointState, lambda m:self.sig.emit(m), queue_size=1)
    def update_state(self,msg):
        lines=[]
        for n,p in zip(msg.name,msg.position):
            lines.append('%s: %.4f'%(n,p))
        self.text.setPlainText('\n'.join(lines))
