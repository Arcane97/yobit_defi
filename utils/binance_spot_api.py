import logging
import requests
import time

from utils.binance_base_api import BinanceBaseAPI

BINANCE_SPOT_API_URL = "https://api.binance.com"
# BINANCE_SPOT_API_URL = "https://testnet.binance.vision"

BINANCE_PRIVATE_API_SPOT_URL = 'https://testnet.binance.vision'  # https://api.binance.com/api   https://testnet.binance.vision/api


class BinanceSpotAPI(BinanceBaseAPI):
    def __init__(self, currency_pair, logger_name="binance_spot_api"):
        super().__init__(dict_key_prefix='binance_spot', logger_name=f'{logger_name}.binance_spot_api')

        # тип сделки (покупка или продажа)
        self._deal_type = None
        # валютная пара
        self._currency_pair = currency_pair

        self._api_key = None
        self._api_secret = None

        # self._read_api_keys_from_file()

        self._logger = logging.getLogger(f'{logger_name}.binance_spot_api')

    def get_average_price(self):
        """ Получение средней цены за 5 минут
        """
        url = f'{BINANCE_SPOT_API_URL}/api/v3/avgPrice?symbol={self._currency_pair}'
        average_price_req_result = self._make_get_request(url)

        if 'price' in average_price_req_result:
            return float(average_price_req_result.get('price'))
        return None

    def get_binance_glass(self):
        """ Получение стакана на бинансе
        :return: стакан на бинансе
        """
        url = f'{BINANCE_SPOT_API_URL}/api/v1/depth?symbol={self._currency_pair}&limit=5'
        glass_req_result = self._make_get_request(url)

        if not isinstance(glass_req_result, dict):
            return None

        return glass_req_result

    def get_satisfy_price(self):
        """ Получение удовлетворяющей цены для точной покупки или продажи
        Чтобы ордер сразу совершился
        """
        # multiplierDown 0.2
        # multiplierUp 5
        # получение стакана
        glass = self.get_binance_glass()
        if glass is None:
            return None
        # получение средней цены
        average_price = self.get_average_price()
        if average_price is None:
            return None
        # ограничение цены сверху
        top_limit = average_price * 5
        # ограничение цены снизу
        bottom_limit = average_price * 0.2

        # лямбда функция фильтра: убирает из стакана не удовлетворяющие ордера в интервале цен [bottom_limit, top_limit]
        mapping_percent_price_filter = lambda order: bottom_limit < float(order[0]) < top_limit
        # отфильтрованный стакан
        filtered_glass = list(filter(mapping_percent_price_filter, glass))

        if len(filtered_glass) == 0:
            self._logger.error('Ни один из ордеров в стакане не подходит под фильтр')
            return None
        if len(filtered_glass) == 1:
            return float(filtered_glass[0][0])

        return float(filtered_glass[len(filtered_glass)//2][0])

    def place_order(self, quantity):
        """ Постановка ордера
        """
        # Получение цены
        is_complete = False
        price = None
        while not is_complete:
            price = self.get_satisfy_price()
            is_complete = True if price else False

        url = BINANCE_PRIVATE_API_SPOT_URL + '/api/v3/order'
        headers = {'X-MBX-APIKEY': self._api_key}
        data = {
            'symbol': self._currency_pair,
            'side': self._deal_type,
            'type': 'LIMIT',
            'timeInForce': "GTC",
            'price': price,
            'quantity': quantity,
        }
        # 'positionSide': 'LONG',
        # 'timeInForce': "GTC",
        # 'price': price,
        payload = self._create_payload(data)

        is_complete = False
        response = None
        while not is_complete:  # todo подумать над остановкой бесконечного цикла принудительно
            self._logger.info(f'Попытка поставить позицию: цена {price}, количество: {quantity}, тип: {self._deal_type}')
            try:
                response = requests.request(method='POST', url=url, params=payload, headers=headers)
                is_complete = True
            except Exception:
                self._logger.error('При попытке поставить позицию произошла ошибка', exc_info=True)
                time.sleep(2)
                self._logger.info('Снова посылаем запрос')

        try:
            result = response.json()
        except Exception:
            self._logger.error('Ошибка в попытке расшифровать json файл', exc_info=True)
            self._logger.error(f'Ответ: {response}')
            return str(response)

        return result

    def get_balance(self):
        """ Получение баланса
        :return: список валюты (list), при ошибке текст ответа (str)
        """
        url = BINANCE_PRIVATE_API_SPOT_URL + '/api/v3/account'
        headers = {'X-MBX-APIKEY': self._api_key}
        payload = self._create_payload({})

        is_complete = False
        response = None
        while not is_complete:
            self._logger.info('Попытка получить баланс')
            try:
                response = requests.request(method='GET', url=url, params=payload, headers=headers)
                is_complete = True
            except Exception:
                self._logger.error('При попытке получить баланс произошла ошибка', exc_info=True)
                time.sleep(2)
                self._logger.info('Снова посылаем запрос')
        try:
            result = response.json()
        except Exception:
            self._logger.error('Ошибка в попытке расшифровать json файл', exc_info=True)
            self._logger.error(f'Ответ: {response}')
            return str(response)

        if 'balances' in result:
            return result['balances']

        return result

    def get_trade_list(self):
        """ Получение трейд листа
        :return: list
        """
        url = BINANCE_PRIVATE_API_SPOT_URL + '/api/v3/myTrades'
        headers = {'X-MBX-APIKEY': self._api_key}
        data = {'symbol': self._currency_pair}
        payload = self._create_payload(data)

        is_complete = False
        response = None
        while not is_complete:
            self._logger.info(f'Попытка получения трейд листа. Пара: {self._currency_pair}')
            try:
                response = requests.request(method='GET', url=url, params=payload, headers=headers)
                is_complete = True
            except Exception:
                self._logger.error('При попытке получения трейд листа.произошла ошибка', exc_info=True)
                time.sleep(2)
                self._logger.info('Снова посылаем запрос')

        try:
            result = response.json()
        except Exception:
            self._logger.error('Ошибка в попытке расшифровать json файл', exc_info=True)
            self._logger.error(f'Ответ: {response}')
            return str(response)

        return result

    def get_exchange_info(self):
        """ Получение общей информации
        :return:
        """
        url = BINANCE_PRIVATE_API_SPOT_URL + '/api/v3/exchangeInfo'
        headers = {'X-MBX-APIKEY': self._api_key}
        payload = ''

        is_complete = False
        response = None
        while not is_complete:
            self._logger.info('Попытка получения общей информации')
            try:
                response = requests.request(method='GET', url=url, params=payload, headers=headers)
                is_complete = True
            except Exception:
                self._logger.error('При попытке получения общей информации произошла ошибка', exc_info=True)
                time.sleep(2)
                self._logger.info('Снова посылаем запрос')

        try:
            result = response.json()
        except Exception:
            self._logger.error('Ошибка в попытке расшифровать json файл', exc_info=True)
            self._logger.error(f'Ответ: {response}')
            return str(response)

        return result


if __name__ == "__main__":
    import json, os
    # from utils.constants import SETTINGS_FILE_NAME

    # def create_test_json_file():
    #     if not os.path.exists(SETTINGS_FILE_NAME):
    #         with open(SETTINGS_FILE_NAME, "w") as file:
    #             data = {'binance_spot_api_key': 'sasfasfq231312sasd',
    #                     'binance_spot_api_secret': 'dasdasdasdasd'}
    #
    #             json.dump(data, file)
    #     else:
    #         with open(SETTINGS_FILE_NAME, "r") as read_file:
    #             data = json.load(read_file)
    #             data['binance_spot_api_key'] = 'sasfasfq231312sasd'
    #             data['binance_spot_api_secret'] = 'dasdasdasdasd'
    #
    #             with open(SETTINGS_FILE_NAME, "w") as out_file:
    #                 json.dump(data, out_file)

    # create_test_json_file()

    obj = BinanceSpotAPI("DOGEBTC")
    glass = obj.get_binance_glass()
    print(glass)
