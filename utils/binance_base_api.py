import hashlib
import hmac
import json
import logging
import requests
import time
import urllib.parse

from requests.packages.urllib3.util.retry import Retry
from utils.timeout_http_adapter import TimeoutHTTPAdapter

# from utils.constants import SETTINGS_FILE_NAME


class BinanceBaseAPI:
    def __init__(self, dict_key_prefix='binance', logger_name="binance_base_api"):
        self._api_key = None
        self._api_secret = None

        self._dict_key_prefix = dict_key_prefix

        self._logger = logging.getLogger(logger_name)

    # def _read_api_keys_from_file(self):  # todo подумать над реализацией сохранения api ключей
    #     """ Считывание апи ключей из файла
    #     """
    #     with open(SETTINGS_FILE_NAME, "r") as file:
    #         settings_data = json.load(file)
    #         if isinstance(settings_data, dict):
    #             self._api_key = settings_data.get(self._dict_key_prefix + '_api_key')
    #             self._api_secret = settings_data.get(self._dict_key_prefix + '_api_secret')
    #         else:
    #             # error кривой json файл
    #             pass

    def _create_payload(self, data: dict):
        """ Создание тела запроса
        :return тело запроса в URL (str)
        """
        # создание Timing security
        timestamp = int(round(time.time() * 1000) - 300)
        data['timestamp'] = timestamp
        data['recvWindow'] = 10000

        # создание sha256 подписи
        payload = urllib.parse.urlencode(data)
        api_secret = str.encode(self._api_secret)
        secret_hash = hmac.new(key=api_secret, digestmod=hashlib.sha256)
        secret_hash.update(payload.encode('utf-8'))
        sign = secret_hash.hexdigest()

        # добавление подписи в тело запроса
        data['signature'] = sign

        # парсинг словаря в строку тела url запроса
        return urllib.parse.urlencode(data)

    def _make_get_request(self, url):
        try:
            s = requests.Session()
            retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
                            method_whitelist=["HEAD", "GET", "PUT", "DELETE", "OPTIONS", "TRACE", "POST"])
            s.mount('http://', TimeoutHTTPAdapter(max_retries=retries))
            s.mount('https://', TimeoutHTTPAdapter(max_retries=retries))

            req = s.get(url)

        except Exception:
            self._logger.error('Ошибка при запросе в публичный апи ', exc_info=True)
            return None

        # попытка расшифровать json файл
        try:
            req_result = req.json()

        except Exception:
            self._logger.error('Ошибка в попытке расшифровать json файл бинанс', exc_info=True)
            self._logger.error(f'Ответ: {req}')
            return None

        return req_result
