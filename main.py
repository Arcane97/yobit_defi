import sys

from PyQt5.QtWidgets import QApplication

from model.yobit_defi_model import YobitDefiModel
from contoller.yobit_defi_controller import YobitDefiController


def main():
    app = QApplication(sys.argv)

    model = YobitDefiModel("DOGEBTC", 2)

    controller = YobitDefiController(model)

    app.exec()


sys.exit(main())
