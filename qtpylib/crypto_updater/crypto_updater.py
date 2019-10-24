import requests
from websocket import create_connection
from threading import Thread
import json
import time

from qtpylib.crypto_updater import candle

abort_websocket = False
ws_thread = None


class Globals:
    api_path = "http://api.coincap.io/v2/assets/"
    rate_key = "priceUsd"


def get_crypto_rate(symbol):
    url = Globals.api_path + symbol
    response = requests.get(url)
    if response.status_code != 200:
        return -1.0

    data = response.json()
    return float(data["data"][Globals.rate_key])


def stop_websocket():
    global abort_websocket
    global ws_thread
    abort_websocket = True
    ws_thread.join()


def candles_heartbit(candles):
    loop_num = 0
    while not abort_websocket:
        loop_num += 1
        now = int(time.time())
        for cur_candle in candles.values():
            cur_candle.heartbit(now)
        # print(loop_num)
        time.sleep(1)


def websocket_data_updater(ws, symbols, interval_minutes, cb_func):
    candles = {}
    for symbol in symbols:
        candles[symbol] = candle.CandledData(symbol, interval_minutes, cb_func)

    heartbit = Thread(target=candles_heartbit, args=(candles,))

    print("STARTING updater for symbols: " + ",".join(symbols))
    heartbit.start()

    while not abort_websocket:
        res = json.loads(ws.recv())
        now = int(time.time())
        for symbol in res.keys():
            cur_candle = candles[symbol]
            cur_candle.add_value(now, res[symbol])

    print("ABORTED updater")
    ws.close()
    heartbit.join()
    for cur_candle in candles.values():
        cur_candle.close_cur_candle()
        cur_candle.dump_candles()


# cb_func will be used for DB writing
def start_websocket(interval_minutes, symbols, cb_func=None):
    global ws_thread
    ws = create_connection("wss://ws.coincap.io/prices?assets={}".format(",".join(symbols)))

    ws_thread = Thread(target=websocket_data_updater, args=(ws, symbols, interval_minutes, cb_func))
    ws_thread.start()


if __name__ == "__main__":
    # print(get_crypto_rate("bitcoin"))
    test_symbols = ["bitcoin", "monero"]
    start_websocket(1, test_symbols)
    time.sleep(30)
    stop_websocket()
    time.sleep(1)
