import json
import logging
import os

from PyQt5 import QtCore, QtWidgets

from view.yobit_defi_view import YobitDefiView
from utils.constants import SETTINGS_FILE_NAME
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
        sounding_time = 10  # float(self.ui.time_alarm_ledit.text())

        # объект звука в потоке
        self._sound_thread_obj = SoundAlarm(sounding_time)
        # пересылаем в отдеьный поток
        self._sound_thread_obj.moveToThread(self._sound_thread)
        self._sound_thread.started.connect(self._sound_thread_obj.start_alarm)

        self._connect_model_signals()
        self._view.show()
        self._load_params()

    def _load_params(self):
        if not os.path.exists(SETTINGS_FILE_NAME):
            with open(SETTINGS_FILE_NAME, "w") as file:
                data = {'pair': 'DOGEBTC',
                        'arbitrage': 1.0,
                        'sleep_time': 0.0,
                        'use_proxy': 0,
                        'proxy': 'TSFqkt:FN6vY4@194.67.198.89:8000'}

                json.dump(data, file)

        with open(SETTINGS_FILE_NAME, "r") as file:
            settings_data = json.load(file)
            if isinstance(settings_data, dict):
                pair = settings_data.get('pair')
                arbitrage = settings_data.get('arbitrage')
                sleep_time = settings_data.get('sleep_time')
                use_proxy = settings_data.get('use_proxy')
                proxy = settings_data.get('proxy')
                self._view.load_params(pair, arbitrage, sleep_time, use_proxy, proxy)
                self._set_param_model()
            else:
                # error кривой json файл
                self._logger.error(f'Кривой файл настроек. Удалите его: {SETTINGS_FILE_NAME}')
                self._view.load_params('DOGEBTC', 1.0, 0.0, 0, 'TSFqkt:FN6vY4@194.67.198.89:8000')
                self._set_param_model()

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

    def _set_param_model(self):
        self.set_pair()
        self.set_arbitrage()
        self.set_sleep_time()
        self.set_proxy()

    def start_thread(self):
        self._set_param_model()
        self._yobit_defi_thread.start()

    def stop_thread(self):
        if self._yobit_defi_thread.isRunning():
            self._model.stop_checking()
            self._yobit_defi_thread.quit()

        if self._sound_thread.isRunning():
            self._sound_thread_obj.stop_alarm()
            self._sound_thread.quit()

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
                sounding_time = 10
                # объект звука в потоке
                self._sound_thread_obj = SoundAlarm(sounding_time)
                # пересылаем в отдеьный поток
                self._sound_thread_obj.moveToThread(self._sound_thread)
                self._sound_thread.started.connect(self._sound_thread_obj.start_alarm)
                self._sound_thread.start()
            else:
                if self._sound_thread.isRunning():
                    self._sound_thread_obj.stop_alarm()
                    self._sound_thread.quit()

        except:
            self._logger.exception('При воиспроизведении звука вознилка ошибка')

    def save_params(self):
        pair = self._view.ui.pair_cmbox.currentText()
        arbitrage = float(self._view.ui.arbitrage_ledit.text())
        sleep_time = float(self._view.ui.sleep_time_ledit.text())
        proxy_chbox = self._view.ui.proxy_chbox.isChecked()
        if proxy_chbox:
            use_proxy = 1
        else:
            use_proxy = 0
        proxy_url = self._view.ui.proxy_ledit.text()

        with open(SETTINGS_FILE_NAME, "w") as file:
            data = {'pair': pair,
                    'arbitrage': arbitrage,
                    'sleep_time': sleep_time,
                    'use_proxy': use_proxy,
                    'proxy': proxy_url}

            json.dump(data, file)

    def terminate_threads(self):
        if self._yobit_defi_thread.isRunning():
            self._yobit_defi_thread.terminate()

        if self._sound_thread.isRunning():
            self._sound_thread.terminate()
