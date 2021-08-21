import logging

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

        self._load_params()
        self._connect_signals()

    def _load_params(self):
        for pair in pairs_urls_dict.keys():
            self.ui.pair_cmbox.addItem(pair)

        arbitrage = str(2)
        self.ui.arbitrage_ledit.setText(arbitrage)

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

    def _working_btn_clicked(self):
        if self._model.is_running:
            self._controller.stop_thread()
            self.ui.working_btn.setText('Старт')
        else:
            self._controller.start_thread()
            self.ui.working_btn.setText('Стоп')


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = YobitDefiView(None, None)
    w.show()
    sys.exit(app.exec_())
