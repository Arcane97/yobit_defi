from PyQt5.QtWidgets import QApplication, QMainWindow

from yobit_defi_view_ui import Ui_MainWindow


class YobitDefiView(QMainWindow):
    def __init__(self, controller, model):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._controller = controller
        self._model = model


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = YobitDefiView()
    w.show()
    sys.exit(app.exec_())
