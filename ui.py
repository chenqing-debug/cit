import pathlib, cit
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QRadioButton, QSpinBox, QLabel,
                             QFileDialog, QMessageBox, QInputDialog)
from PyQt5.QtCore import pyqtSignal
from PIL import Image
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

class PackUI(QWidget):
    done = pyqtSignal(pathlib.Path, pathlib.Path)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("图集打包器")
        self.resize(360, 240)
        self.imgs = []          # PIL.Image
        self.out_folder = None

        self.btn_pick = QPushButton("选择图片")
        self.btn_pick.clicked.connect(self.pick_images)

        self.radio_h = QRadioButton("长条（水平）")
        self.radio_v = QRadioButton("竖条（垂直）")
        self.radio_g = QRadioButton("图集（行列）")
        self.radio_g.setChecked(True)

        self.sp_rows = QSpinBox()
        self.sp_cols = QSpinBox()
        self.sp_rows.setMinimum(1)
        self.sp_cols.setMinimum(1)
        self.sp_rows.setValue(3)
        self.sp_cols.setValue(3)

        self.btn_out = QPushButton("选择输出目录")
        self.btn_out.clicked.connect(self.pick_out)

        self.btn_run = QPushButton("生成")
        self.btn_run.clicked.connect(self.run)

        lay = QVBoxLayout(self)
        lay.addWidget(self.btn_pick)

        mode_lay = QHBoxLayout()
        mode_lay.addWidget(self.radio_h)
        mode_lay.addWidget(self.radio_v)
        mode_lay.addWidget(self.radio_g)
        lay.addLayout(mode_lay)

        grid_lay = QHBoxLayout()
        grid_lay.addWidget(QLabel("行"))
        grid_lay.addWidget(self.sp_rows)
        grid_lay.addWidget(QLabel("列"))
        grid_lay.addWidget(self.sp_cols)
        lay.addLayout(grid_lay)

        lay.addWidget(self.btn_out)
        lay.addWidget(self.btn_run)

    def pick_images(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择图片（可多选）", "",
            "Image Files (*.png *.jpg *.jpeg);;All Files (*)")
        if files:
            self.imgs = [Image.open(f).convert("RGBA") for f in sorted(files)]
            QMessageBox.information(self, "提示", f"已加载 {len(self.imgs)} 张图")
            self.refresh_grid_rc()

    def pick_out(self):
        fd = QFileDialog.getExistingDirectory(self, "输出目录")
        if fd:
            self.out_folder = pathlib.Path(fd)

    def run(self):
        if not self.imgs:
            QMessageBox.warning(self, "警告", "请先选择图片！")
            return
        if not self.out_folder:
            QMessageBox.warning(self, "警告", "请选择输出目录！")
            return

        mode = 'h' if self.radio_h.isChecked() else 'v' if self.radio_v.isChecked() else 'grid'
        rows, cols = self.sp_rows.value(), self.sp_cols.value()

        stem, ok = QInputDialog.getText(self, "命名", "输出主文件名（不含扩展）：", text="atlas")
        if not ok or not stem:
            return

        png, txt = cit.build_atlas(self.imgs, mode, rows, cols, self.out_folder, stem)
        self.done.emit(png, txt)
        QMessageBox.information(self, "完成", f"已生成\n{png}\n{txt}")

    def nearest_square(self, n: int):
        cols = int(n**0.5 + 0.5)
        rows = (n + cols - 1) // cols
        return rows, cols

    def refresh_grid_rc(self):
        if not self.imgs:
            return
        rows, cols = self.nearest_square(len(self.imgs))
        self.sp_rows.setValue(rows)
        self.sp_cols.setValue(cols)