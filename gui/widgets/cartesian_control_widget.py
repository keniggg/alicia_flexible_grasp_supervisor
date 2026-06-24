from PyQt5 import QtWidgets
import rospy
from alicia_flexible_grasp_supervisor.srv import CartesianJog

class CartesianControlWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout=QtWidgets.QVBoxLayout(self)
        self.step=QtWidgets.QDoubleSpinBox(); self.step.setDecimals(3); self.step.setSingleStep(0.001); self.step.setValue(0.005); self.step.setSuffix(' m')
        layout.addWidget(QtWidgets.QLabel('笛卡尔点动步长')); layout.addWidget(self.step)
        grid=QtWidgets.QGridLayout(); layout.addLayout(grid)
        buttons=[('X+',0.005,0,0),('X-',-0.005,0,0),('Y+',0,0.005,0),('Y-',0,-0.005,0),('Z+',0,0,0.005),('Z-',0,0,-0.005)]
        for i,(txt,dx,dy,dz) in enumerate(buttons):
            b=QtWidgets.QPushButton(txt); b.clicked.connect(lambda _,dx=dx,dy=dy,dz=dz:self.jog(dx,dy,dz)); grid.addWidget(b,i//2,i%2)
        self.status=QtWidgets.QLabel('等待操作'); layout.addWidget(self.status)
    def jog(self,dx,dy,dz):
        scale=self.step.value()/0.005
        try:
            rospy.wait_for_service('/supervisor/cartesian_jog', timeout=1.0)
            srv=rospy.ServiceProxy('/supervisor/cartesian_jog', CartesianJog)
            r=srv(dx*scale,dy*scale,dz*scale,0,0,0,True)
            self.status.setText(r.message)
        except Exception as e:
            self.status.setText(str(e))
