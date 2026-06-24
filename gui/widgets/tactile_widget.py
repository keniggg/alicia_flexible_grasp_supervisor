from PyQt5 import QtWidgets, QtCore
import rospy
from alicia_flexible_grasp_supervisor.msg import TactileState

class TactileWidget(QtWidgets.QWidget):
    sig = QtCore.pyqtSignal(object)
    def __init__(self, topic='/tactile/state'):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        self.info = QtWidgets.QLabel('电子皮肤：等待数据')
        self.grid = QtWidgets.QTextEdit(); self.grid.setReadOnly(True); self.grid.setMaximumHeight(180)
        layout.addWidget(self.info); layout.addWidget(self.grid)
        self.sig.connect(self.update_state)
        rospy.Subscriber(topic, TactileState, lambda m: self.sig.emit(m), queue_size=1)
    def update_state(self, msg):
        self.info.setText('总力: %.1f mN | 左: %.1f | 右: %.1f | 差值: %.1f | 接触: %s | 滑移: %s' % (
            msg.total_grip_force_mn, msg.left.total_force_mn, msg.right.total_force_mn, msg.force_diff_mn, msg.object_grasped, msg.slip_detected))
        vals = list(msg.left.values)[:30]
        rows=[]
        for i in range(0, len(vals), 6):
            rows.append(' '.join('%5.0f'%v for v in vals[i:i+6]))
        self.grid.setPlainText('\n'.join(rows))
