import logging
import sys

from PyQt5.QtWidgets import QApplication

from contoller.yobit_defi_controller import YobitDefiController
from model.yobit_defi_model import YobitDefiModel
# from utils.constants import LOG_FILE_NAME
LOG_FILE_NAME = "./yobit_defi_log.log"


def create_log(log_name):
    # логгер
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    # обработчик файла логов
    file_handler = logging.FileHandler(LOG_FILE_NAME)
    # форматирование файла логов
    formatter_fh = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter_fh)
    # добавление обработчиков к логгеру
    logger.addHandler(file_handler)


def main():
    log_name = "yobit_defi"
    create_log(log_name)
    app = QApplication(sys.argv)

    model = YobitDefiModel("DOGEBTC", 2, log_name)

    controller = YobitDefiController(model, "yobit_defi")

    app.exec()


sys.exit(main())
