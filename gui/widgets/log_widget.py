from PyQt5 import QtWidgets
class LogWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        layout=QtWidgets.QVBoxLayout(self)
        self.text=QtWidgets.QTextEdit(); self.text.setReadOnly(True)
        self.text.setPlainText('ROS 日志请同时查看终端输出。')
        layout.addWidget(self.text)
