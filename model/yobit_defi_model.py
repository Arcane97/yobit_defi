import logging
from PyQt5.QtCore import QObject

from model.pull_value import get_pull_value
from utils.binance_spot_api import BinanceSpotAPI
from utils.constants import pairs_urls_dict


class YobitDefiModel(QObject):
    """ Класс модели
    Проверяем свопы yobit и спотовый binance на арбитраж
    """
    def __init__(self, pair, arbitrage, log_name="yobit_defi"):
        """
        :param pair: пара
        :param arbitrage: разница с binance в процентах
        """
        super().__init__()

        self.pair = pair
        self.arbitrage = arbitrage

        self._binance_api_obj = BinanceSpotAPI(self.pair)

        self._logger = logging.getLogger(f'{log_name}.model')

        self.is_running = False

    def set_pair(self, pair):
        self.pair = pair
        self._binance_api_obj.set_pair(self.pair)

    def _get_yobit_price(self):
        """ Получение цены свопа yobit
        """
        try:
            pull_qty_1, pull_qty_2 = get_pull_value(pairs_urls_dict[self.pair])
            pull_price = round(pull_qty_2 / pull_qty_1, 8)
        except Exception as e:
            # todo обработать ошибку
            return None

        return pull_price * 0.99, pull_price * 1.01

    def _get_binance_price(self):
        """ Получение цены на спотовом рынке binance
        """
        binance_glass = self._binance_api_obj.get_binance_glass()
        try:
            buy_price = float(binance_glass.get("bids")[0][0])
            sell_price = float(binance_glass.get("asks")[0][0])
        except Exception as e:
            # todo обработать ошибку
            print(e)
            return None

        return buy_price, sell_price

    def _check_arbitrage(self):
        """ Проверка арбитража
        """
        # 100 * (binance_price - self.main_price) / self.main_price
        yobit_buy_price, yobit_sell_price = self._get_yobit_price()
        binance_buy_price, binance_sell_price = self._get_binance_price()

        yobit_buy_arbitrage = 100 * (binance_sell_price - yobit_buy_price) / yobit_buy_price
        print('yobit_buy_arbitrage', yobit_buy_arbitrage)  # todo вывод в лог
        if yobit_buy_arbitrage >= self.arbitrage:
            # покупайте на yobit продавайте на binance
            pass  # todo сигнал

        binance_buy_arbitrage = 100 * (yobit_sell_price - binance_buy_price) / yobit_sell_price
        print('binance_buy_arbitrage', binance_buy_arbitrage)  # todo вывод в лог
        if binance_buy_arbitrage >= self.arbitrage:
            # покупайте на binance продавайте на yobit
            pass  # todo сигнал

    def start_checking(self):
        self.is_running = True
        while self.is_running:
            self._check_arbitrage()

    def stop_checking(self):
        self.is_running = False


if __name__ == "__main__":
    _pair = "DOGEBTC"
    # doge_pull, btc_pull = get_pull_value(pairs_urls_dict[_pair])
    # obj = BinanceSpotAPI(_pair)
    # glass = obj.get_binance_glass()
    # print(doge_pull, btc_pull, "%.8f" % round(btc_pull/doge_pull, 8))
    # print(glass)

    yobit_defi_model = YobitDefiModel(_pair, 0)
    print(yobit_defi_model._get_yobit_price())
    print(yobit_defi_model._get_binance_price())
    yobit_defi_model._check_arbitrage()
