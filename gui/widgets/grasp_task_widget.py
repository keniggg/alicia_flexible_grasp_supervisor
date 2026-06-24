from PyQt5 import QtWidgets, QtCore
import rospy
from alicia_flexible_grasp_supervisor.msg import GraspState
from alicia_flexible_grasp_supervisor.srv import StartGrasp, StopGrasp

class GraspTaskWidget(QtWidgets.QWidget):
    sig=QtCore.pyqtSignal(object)
    def __init__(self, topic='/grasp/state'):
        super().__init__()
        layout=QtWidgets.QVBoxLayout(self)
        self.state=QtWidgets.QLabel('抓取状态：IDLE')
        start=QtWidgets.QPushButton('开始自主柔顺抓取')
        stop=QtWidgets.QPushButton('停止')
        start.clicked.connect(self.start); stop.clicked.connect(self.stop)
        layout.addWidget(self.state); layout.addWidget(start); layout.addWidget(stop)
        self.sig.connect(self.update)
        rospy.Subscriber(topic, GraspState, lambda m:self.sig.emit(m), queue_size=1)
    def update(self,msg):
        self.state.setText('抓取状态：%s | %s'%(msg.state,msg.message))
    def start(self):
        try:
            rospy.wait_for_service('/grasp/start', timeout=1)
            r=rospy.ServiceProxy('/grasp/start', StartGrasp)(True)
            self.state.setText('启动结果：%s %s'%(r.success,r.message))
        except Exception as e:
            self.state.setText(str(e))
    def stop(self):
        try:
            rospy.wait_for_service('/grasp/stop', timeout=1)
            r=rospy.ServiceProxy('/grasp/stop', StopGrasp)(False)
            self.state.setText('停止结果：%s'%r.message)
        except Exception as e:
            self.state.setText(str(e))
