import logging

from PyQt5.QtWidgets import QApplication, QMainWindow

from view.yobit_defi_view_ui import Ui_MainWindow


class YobitDefiView(QMainWindow):
    def __init__(self, controller, model, log_name="yobit_defi"):
        super().__init__()
        self._logger = logging.getLogger(f'{log_name}.view')

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._controller = controller
        self._model = model


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = YobitDefiView(None, None)
    w.show()
    sys.exit(app.exec_())
