import logging
from PyQt5.QtCore import QObject, pyqtSignal

from model.pull_value import YobitAPI
from utils.binance_spot_api import BinanceSpotAPI
from utils.constants import pairs_urls_dict


class YobitDefiModel(QObject):
    """ Класс модели
    Проверяем свопы yobit и спотовый binance на арбитраж
    """
    yobit_buy_price_sig = pyqtSignal(float)
    yobit_sell_price_sig = pyqtSignal(float)
    binance_buy_price_sig = pyqtSignal(float)
    binance_sell_price_sig = pyqtSignal(float)
    yobit_buy_arbitrage_sig = pyqtSignal(float)
    binance_buy_arbitrage_sig = pyqtSignal(float)
    done_yobit_buy_arbitrage_sig = pyqtSignal(str)
    done_binance_buy_arbitrage_sig = pyqtSignal(str)

    def __init__(self, pair, arbitrage, log_name="yobit_defi"):
        """
        :param pair: пара
        :param arbitrage: разница с binance в процентах
        """
        super().__init__()

        self.pair = pair
        self.arbitrage = arbitrage

        self._yobit_qpi_obj = YobitAPI(log_name)
        self._binance_api_obj = BinanceSpotAPI(self.pair, log_name)

        self._logger = logging.getLogger(f'{log_name}.model')

        self.is_running = False

    def set_pair(self, pair):
        self.pair = pair
        self._binance_api_obj.set_pair(self.pair)

    def _get_yobit_price(self):
        """ Получение цены свопа yobit
        """
        try:
            pull_qty_1, pull_qty_2 = self._yobit_qpi_obj.get_pull_value(pairs_urls_dict[self.pair])
            pull_price = round(pull_qty_2 / pull_qty_1, 8)
        except Exception:
            self._logger.exception('Ошибка при получении цены свопа')
            return None

        return pull_price * 0.99, pull_price * 1.01

    def _get_binance_price(self):
        """ Получение цены на спотовом рынке binance
        """
        binance_glass = self._binance_api_obj.get_binance_glass()
        try:
            buy_price = float(binance_glass.get("bids")[0][0])
            sell_price = float(binance_glass.get("asks")[0][0])
        except Exception:
            self._logger.exception('Ошибка при получении цен из стакана')
            return None

        return buy_price, sell_price

    def _check_arbitrage(self):
        """ Проверка арбитража
        """
        # 100 * (binance_price - self.main_price) / self.main_price
        try:
            yobit_buy_price, yobit_sell_price = self._get_yobit_price()
            binance_buy_price, binance_sell_price = self._get_binance_price()
        except:
            return
        self.yobit_buy_price_sig.emit(yobit_buy_price)
        self.yobit_sell_price_sig.emit(yobit_sell_price)
        self.binance_buy_price_sig.emit(binance_buy_price)
        self.binance_sell_price_sig.emit(binance_sell_price)

        yobit_buy_arbitrage = 100 * (binance_sell_price - yobit_buy_price) / yobit_buy_price
        self._logger.info(f'Yobit buy: {yobit_buy_price:.8f} Binance sell: {binance_sell_price:.8f} '
                          f'Арбитраж: {yobit_buy_arbitrage:.3f}')
        self.yobit_buy_arbitrage_sig.emit(yobit_buy_arbitrage)

        if yobit_buy_arbitrage >= self.arbitrage:
            # покупайте на yobit продавайте на binance
            self._logger.info('Арбитраж достугнут. Покупайте на yobit, продавайте на binance')
            self.done_yobit_buy_arbitrage_sig.emit('Арбитраж достугнут. Покупайте на yobit, продавайте на binance')

        binance_buy_arbitrage = 100 * (yobit_sell_price - binance_buy_price) / yobit_sell_price
        self._logger.info(f'Binance buy: {binance_buy_price:.8f} Yobit sell: {yobit_sell_price:.8f} '
                          f'Арбитраж: {binance_buy_arbitrage:.3f}')
        self.binance_buy_arbitrage_sig.emit(binance_buy_arbitrage)

        if binance_buy_arbitrage >= self.arbitrage:
            # покупайте на binance продавайте на yobit
            self._logger.info('Арбитраж достугнут. Покупайте на binance, продавайте на yobit')
            self.done_binance_buy_arbitrage_sig.emit('Арбитраж достугнут. Покупайте на binance, продавайте на yobit')

    def start_checking(self):
        self.is_running = True
        self._logger.info('Старт')
        while self.is_running:
            self._check_arbitrage()

    def stop_checking(self):
        self._logger.info('Стоп')
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
