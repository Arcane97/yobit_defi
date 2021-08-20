from bs4 import BeautifulSoup
import requests

from utils.constants import DOGE_BTC_DEFI_URL


def get_yobit_page(url):
    """ Получение страницы yobit
    :param url: ссылка
    :return: код страницы
    """
    try:
        req = requests.get(url)
    except Exception as e:
        # todo доавить обработку ошибки
        print(e)
        return None

    return req.text


def get_pull_value(url):
    """ Получение данных о количестве валюты в пуле
    :param url: ссылка
    :return: данные о пуле
    """
    page_text = get_yobit_page(url)
    try:
        soup = BeautifulSoup(page_text, 'lxml')
        div_quotes = soup.find_all('div', class_='top_meta_mining')[1]
        span_quotes = div_quotes.find_all('span')

        value1 = float(span_quotes[0].text)
        value2 = float(span_quotes[1].text)

    except Exception as e:
        # todo обработать ошибку
        print(e)
        return None

    return value1, value2


if __name__ == "__main__":
    # text = get_yobit_page(DOGE_BTC_DEFI_URL)
    value = get_pull_value(DOGE_BTC_DEFI_URL)
    print(value)
