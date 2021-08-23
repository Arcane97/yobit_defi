import logging

from PyQt5 import QtCore, QtWidgets

from view.yobit_defi_view import YobitDefiView
from utils.sound_alarm import SoundAlarm


class YobitDefiController:
    def __init__(self, model, log_name="yobit_defi"):
        self._logger = logging.getLogger(f'{log_name}.controller')

        self._model = model

        self._view = YobitDefiView(self, model, log_name)

        # отдельный поток
        self._yobit_defi_thread = QtCore.QThread()
        self._model.moveToThread(self._yobit_defi_thread)
        self._yobit_defi_thread.started.connect(self._model.start_checking)

        # отдельный поток для звука
        self._sound_thread = QtCore.QThread()

        # время звучания будильника  # todo добавить в модель
        sounding_time = 2  # float(self.ui.time_alarm_ledit.text())

        # объект звука в потоке
        self._sound_thread_obj = SoundAlarm(sounding_time)
        # пересылаем в отдеьный поток
        self._sound_thread_obj.moveToThread(self._sound_thread)
        self._sound_thread.started.connect(self._sound_thread_obj.start_alarm)

        self._connect_model_signals()
        self._view.show()

    def _connect_model_signals(self):
        self._model.yobit_buy_price_sig.connect(self._change_yobit_buy_lbl)
        self._model.yobit_sell_price_sig.connect(self._change_yobit_sell_lbl)
        self._model.binance_buy_price_sig.connect(self._change_binance_buy_lbl)
        self._model.binance_sell_price_sig.connect(self._change_binance_sell_lbl)
        self._model.yobit_buy_arbitrage_sig.connect(self._change_yobit_buy_arbitrage_lbl)
        self._model.binance_buy_arbitrage_sig.connect(self._change_binance_buy_arbitrage_lbl)
        self._model.done_yobit_buy_arbitrage_sig.connect(self._show_msg)
        self._model.done_binance_buy_arbitrage_sig.connect(self._show_msg)

    def set_pair(self):
        try:
            pair = self._view.ui.pair_cmbox.currentText()
            self._model.set_pair(pair)
        except Exception:
            self._logger.exception('Ошибка при попытке считать комбобокс с парами')
        else:
            self._logger.info(f'В программу введена пара: {pair}')

    def set_arbitrage(self):
        try:
            arbitrage = float(self._view.ui.arbitrage_ledit.text())
            self._model.arbitrage = arbitrage
        except:
            self._logger.error('Введите арбитраж числом')
        else:
            self._logger.info(f'В программу введен арбитраж: {arbitrage}')

    def start_thread(self):
        self._yobit_defi_thread.start()

    def stop_thread(self):
        if self._yobit_defi_thread.isRunning():
            self._model.stop_checking()
            self._yobit_defi_thread.quit()

    def _change_yobit_buy_lbl(self, value):
        self._view.ui.yobit_buy_lbl.setText('%.8f' % value)

    def _change_yobit_sell_lbl(self, value):
        self._view.ui.yobit_sell_lbl.setText('%.8f' % value)

    def _change_binance_buy_lbl(self, value):
        self._view.ui.binance_buy_lbl.setText('%.8f' % value)

    def _change_binance_sell_lbl(self, value):
        self._view.ui.binance_sell_lbl.setText('%.8f' % value)

    def _change_yobit_buy_arbitrage_lbl(self, value):
        self._view.ui.yobit_buy_arbitrage_lbl.setText('%.3f' % value)

    def _change_binance_buy_arbitrage_lbl(self, value):
        self._view.ui.binance_buy_arbitrage_lbl.setText('%.3f' % value)

    def _show_msg(self, msg):
        try:
            # запускаем, если запущен, останавливаем
            if self._sound_thread.isRunning():
                # self._sound_thread_obj = None
                self._sound_thread.quit()

            self._sound_thread.start()

            if self._view.msg_box is not None:  # todo баг если арбитраж достигнут и не прекращается, программу не остановить
                return

            if self._view.msg_box is not None:
                self._view.msg_box.close()
                self._view.msg_box = None
            self._view.msg_box = QtWidgets.QMessageBox(self._view)
            self._view.msg_box.setWindowTitle('Внимание!')
            self._view.msg_box.setText(msg)
            if self._view.msg_box.exec_():
                self._view.msg_box = None
                if self._sound_thread_obj is not None:
                    self._sound_thread_obj.stop_alarm()
                    self._sound_thread.quit()

            self._view.msg_box = None

        except:
            self._logger.exception('При воиспроизведении звука вознилка ошибка')
