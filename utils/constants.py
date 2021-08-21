from definitions import ROOT_DIR  # todo баг с файлом в сборке


SETTINGS_FILE_NAME = ROOT_DIR + "\\yobit_defi_settings.json"
LOG_FILE_NAME = ROOT_DIR + "\\yobit_defi_log.log"
SOUND_FILE_NAME = ROOT_DIR + "\\sound.wav"

DOGE_BTC_DEFI_URL = "https://yobit.net/ru/defi/DOGE/BTC"
ETH_BTC_DEFI_URL = "https://yobit.net/ru/defi/ETH/BTC"
TRX_BTC_DEFI_URL = "https://yobit.net/ru/defi/TRX/BTC"
XRP_BTC_DEFI_URL = "https://yobit.net/ru/defi/XRP/BTC"
WBTC_BTC_DEFI_URL = "https://yobit.net/ru/defi/WBTC/BTC"
ETH_USDT_DEFI_URL = "https://yobit.net/ru/defi/ETH/USDT"
BTC_USDT_DEFI_URL = "https://yobit.net/ru/defi/BTC/USDT"
ETH_USDC_DEFI_URL = "https://yobit.net/ru/defi/ETH/USDC"
DOGE_USDT_DEFI_URL = "https://yobit.net/ru/defi/DOGE/USDT"

pairs_urls_dict = {"DOGEBTC": DOGE_BTC_DEFI_URL,
                   "ETHBTC": ETH_BTC_DEFI_URL,
                   "TRXBTC": TRX_BTC_DEFI_URL,
                   "XRPBTC": XRP_BTC_DEFI_URL,
                   "WBTCBTC": WBTC_BTC_DEFI_URL,
                   "ETHUSDT": ETH_USDT_DEFI_URL,
                   "BTCUSDT": BTC_USDT_DEFI_URL,
                   "ETHUSDC": ETH_USDC_DEFI_URL,
                   "DOGEUSDT": DOGE_USDT_DEFI_URL,
                   }
