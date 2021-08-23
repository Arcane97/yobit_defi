from bs4 import BeautifulSoup
import logging
import requests


class YobitAPI:
    def __init__(self, proxy=None, log_name="yobit_defi"):
        self.proxy = proxy
        self._logger = logging.getLogger(f'{log_name}.yobit_api')

    def set_proxy(self, proxy):
        self.proxy = proxy

    def get_yobit_page(self, url):
        """ Получение страницы yobit
        :param url: ссылка
        :return: код страницы
        """
        try:
            req = requests.get(url, proxies=self.proxy)
        except Exception:
            self._logger.exception(f'При получении страницы yobit возникла ошибка. URL: {url}')
            return None

        return req.text

    def get_pull_value(self, url):
        """ Получение данных о количестве валюты в пуле
        :param url: ссылка
        :return: данные о пуле
        """
        page_text = self.get_yobit_page(url)
        try:
            soup = BeautifulSoup(page_text, 'lxml')
            div_quotes = soup.find_all('div', class_='top_meta_mining')[1]
            span_quotes = div_quotes.find_all('span')

            value1 = float(span_quotes[0].text)
            value2 = float(span_quotes[1].text)

        except Exception as e:
            self._logger.exception(f'При  данных о количестве валюты в пуле возникла ошибка. page_text: {page_text}')
            return None

        return value1, value2


if __name__ == "__main__":
    # text = get_yobit_page(DOGE_BTC_DEFI_URL)
    # value = get_pull_value(DOGE_BTC_DEFI_URL)
    # print(value)
    pass
