import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QFile
from ui import PackUI

def load_qss(app, qss_path="ui.css"):
    file = QFile(qss_path)
    if file.open(QFile.ReadOnly | QFile.Text):
        app.setStyleSheet(str(file.readAll(), encoding='utf-8'))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    load_qss(app)
    w = PackUI()
    w.show()
    sys.exit(app.exec_())