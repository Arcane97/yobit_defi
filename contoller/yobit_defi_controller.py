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

        # время звучания будильника
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
        self._model.no_arbitrage_sig.connect(self._show_msg)

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

    def set_sleep_time(self):
        try:
            sleep_time = float(self._view.ui.sleep_time_ledit.text())
            self._model.sleep_time = sleep_time
        except:
            self._logger.error('Введите время задержки числом')
        else:
            self._logger.info(f'В программу введено время задержки: {sleep_time}')

    def set_proxy(self):
        try:
            use_proxy = self._view.ui.proxy_chbox.isChecked()
            proxy_url = self._view.ui.proxy_ledit.text()
            proxy = {"https": f"https://{proxy_url}"}
            if use_proxy:
                self._model.set_proxy(proxy)
            else:
                self._model.set_proxy(None)
        except:
            self._logger.exception('Ошибка при вводе прокси')
        else:
            if use_proxy:
                self._logger.info(f'Будет использоваться прокси {proxy_url}')
            else:
                self._logger.info('Прокси не будет использоваться')

    def start_thread(self):
        self.set_pair()
        self.set_arbitrage()
        self.set_sleep_time()
        self.set_proxy()
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

    def _show_msg(self, msg, msg_type):
        try:
            self._view.ui.state_lbl.setText(msg)

            # запускаем, если запущен, останавливаем
            if self._sound_thread.isRunning():
                # self._sound_thread_obj = None
                self._sound_thread.quit()

            if msg_type != 0:
                self._sound_thread.start()

        except:
            self._logger.exception('При воиспроизведении звука вознилка ошибка')
