from PyQt5 import QtWidgets
import rospy
from sensor_msgs.msg import JointState

class JointControlWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.names=['Joint1','Joint2','Joint3','Joint4','Joint5','Joint6','right_finger']
        self.pub=rospy.Publisher('/joint_commands', JointState, queue_size=10)
        self.sliders=[]; self.labels=[]
        layout=QtWidgets.QVBoxLayout(self)
        for name in self.names:
            row=QtWidgets.QHBoxLayout(); lab=QtWidgets.QLabel(name); val=QtWidgets.QLabel('0.000')
            s=QtWidgets.QSlider(); s.setOrientation(1); s.setMinimum(-3140); s.setMaximum(3140)
            if name=='right_finger': s.setMinimum(0); s.setMaximum(50)
            s.valueChanged.connect(self.publish)
            row.addWidget(lab); row.addWidget(s,1); row.addWidget(val)
            layout.addLayout(row); self.sliders.append(s); self.labels.append(val)
        btn=QtWidgets.QPushButton('发送当前关节命令到 /joint_commands')
        btn.clicked.connect(self.publish); layout.addWidget(btn)
    def publish(self):
        pos=[]
        for name,s,lab in zip(self.names,self.sliders,self.labels):
            if name=='right_finger': v=s.value()/1000.0
            else: v=s.value()/1000.0
            lab.setText('%.3f'%v); pos.append(v)
        msg=JointState(); msg.header.stamp=rospy.Time.now(); msg.name=self.names; msg.position=pos
        self.pub.publish(msg)
