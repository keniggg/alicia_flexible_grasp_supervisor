from PyQt5 import QtWidgets, QtGui, QtCore
import rospy
from sensor_msgs.msg import Image
try:
    from cv_bridge import CvBridge
    import cv2
except Exception:
    CvBridge = None
    cv2 = None

class CameraWidget(QtWidgets.QWidget):
    image_signal = QtCore.pyqtSignal(object)
    def __init__(self, topic='/supervisor/camera/color/image_raw'):
        super().__init__()
        self.topic = topic
        self.bridge = CvBridge() if CvBridge else None
        layout = QtWidgets.QVBoxLayout(self)
        self.title = QtWidgets.QLabel('摄像头实时画面：%s' % topic)
        self.title.setStyleSheet('font-weight: bold; font-size: 16px;')
        self.label = QtWidgets.QLabel('等待图像...')
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setMinimumSize(640, 480)
        self.label.setStyleSheet('background:#111; color:#ccc; border:1px solid #333;')
        layout.addWidget(self.title); layout.addWidget(self.label, 1)
        self.image_signal.connect(self.update_image)
        rospy.Subscriber(topic, Image, self.cb, queue_size=1)
    def cb(self, msg):
        if self.bridge is None or cv2 is None:
            return
        try:
            img = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            self.image_signal.emit(rgb)
        except Exception as exc:
            rospy.logwarn_throttle(2.0, 'CameraWidget convert failed: %s', exc)
    def update_image(self, rgb):
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QtGui.QImage(rgb.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap.fromImage(qimg).scaled(self.label.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
        self.label.setPixmap(pix)
