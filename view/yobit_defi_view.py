import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow

from view.yobit_defi_view_ui import Ui_MainWindow
from utils.constants import pairs_urls_dict
from utils.text_editor_logger import QTextEditLogger


class YobitDefiView(QMainWindow):
    def __init__(self, controller, model, log_name="yobit_defi"):
        super().__init__()
        self._logger = logging.getLogger(f'{log_name}.view')

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._controller = controller
        self._model = model

        self.msg_box = None

        self._create_log(log_name)

        self._connect_signals()

    def _create_log(self, log_name):
        main_logger = logging.getLogger(log_name)
        # обработчик окна логов
        log_window_handler = QTextEditLogger(self.ui.log_tedit)
        formatter_wh = logging.Formatter('%(asctime)s -split- %(levelname)s -split- %(message)s')
        log_window_handler.setFormatter(formatter_wh)
        # добавление обработчиков к логгеру
        main_logger.addHandler(log_window_handler)

    def _connect_signals(self):
        self.ui.working_btn.clicked.connect(self._working_btn_clicked)
        self.ui.pair_cmbox.currentTextChanged.connect(self._controller.set_pair)
        self.ui.arbitrage_ledit.editingFinished.connect(self._controller.set_arbitrage)
        self.ui.sleep_time_ledit.editingFinished.connect(self._controller.set_sleep_time)
        self.ui.proxy_chbox.stateChanged.connect(self._controller.set_proxy)
        self.ui.proxy_ledit.editingFinished.connect(self._controller.set_proxy)

    def _working_btn_clicked(self):
        if self._model.is_running:
            self._controller.stop_thread()
            self.ui.working_btn.setText('Старт')
        else:
            self._controller.start_thread()
            self.ui.working_btn.setText('Стоп')

    def load_params(self, pair, arbitrage, sleep_time, use_proxy, proxy):
        try:
            for p in pairs_urls_dict.keys():
                self.ui.pair_cmbox.addItem(p)
            self.ui.pair_cmbox.setCurrentText(pair)
        except:
            self._logger.exception('При загрузке пары в интерфейс произошла ошибка')

        try:
            str_arbitrage = str(arbitrage)
            self.ui.arbitrage_ledit.setText(str_arbitrage)
        except:
            self._logger.exception('При загрузке арбитража в интерфейс произошла ошибка')

        try:
            str_sleep_time = str(sleep_time)
            self.ui.sleep_time_ledit.setText(str_sleep_time)
        except:
            self._logger.exception('При загрузке времени задержки в интерфейс произошла ошибка')

        try:
            if use_proxy:
                self.ui.proxy_chbox.setChecked(True)
            else:
                self.ui.proxy_chbox.setChecked(False)
            self.ui.proxy_ledit.setText(proxy)
        except:
            self._logger.exception('При загрузке прокси в интерфейс произошла ошибка')

    def closeEvent(self, e):
        self._controller.save_params()
        self._controller.terminate_threads()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = YobitDefiView(None, None)
    w.show()
    sys.exit(app.exec_())
