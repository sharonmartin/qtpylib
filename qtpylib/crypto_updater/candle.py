import threading
import time
import sys


def timestamp_to_str(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(timestamp)))


class Globals:
    candle_keys = ("datetime", "open", "high", "low", "close", "volume")


class Candle(object):
    def __init__(self, timestamp, low, high, open, close, volume):
        self._timestamp = timestamp
        self._low = low
        self._high = high
        self._open = open
        self._close = close
        self._volume = volume

    def to_string(self):
        time_str = timestamp_to_str(self._timestamp)
        return "{} Open: {}, Close: {}, Low: {}, High: {}".format(time_str, self._open, self._close, self._low, self._high)


def _get_minutes(timestamp):
    return int(timestamp / 60)


class CandledData(object):
    def __init__(self, symbol, interval_minutes, cb_func):
        self._open = self._close = self._low = self._high = None
        self._candles = []
        self._interval_minutes = interval_minutes
        self._ref_time = 0
        self._symbol = symbol
        self.cb_func = cb_func
        self._cur_val = 0
        self._lock = threading.Lock()
        self._volume = 1

    def _add_first_value(self, timestamp, value):
        self._set_ref_time(timestamp)
        self._low = self._high = self._open = value

    def _set_ref_time(self, timestamp):
        self._ref_time = _get_minutes(timestamp) * 60

    def _write_candle(self):
        self._candles[-1].to_string()

    def close_cur_candle(self):
        with self._lock:
            self._on_candle_done(int(time.time()), None)

    def _on_candle_done(self, timestamp, value):
        self._candles.append(Candle(self._ref_time, self._low, self._high, self._open, self._cur_val, 1))
        self._write_candle()

        self._open = self._cur_val
        self._low = None
        self._high = None
        self._set_ref_time(timestamp)

    def heartbit(self, timestamp):
        self.add_value(timestamp, None)

    def add_value(self, timestamp, value):
        with self._lock:
            if not self._ref_time:
                self._add_first_value(timestamp, value)

            if _get_minutes(timestamp - self._ref_time) >= self._interval_minutes:
                self._on_candle_done(timestamp, value)

            if value:
                if not self._open:
                    self._open = value

                if self._low:
                    self._low = min(self._low, value)
                else:
                    self._low = value

                if self._high:
                    self._high = max(self._high, value)
                else:
                    self._high = value

                self._cur_val = value

                if self.cb_func:
                    self.cb_func(timestamp, value)

    # returns open, last, low, high
    def get_cur_value(self):
        with self._lock:
            return self._open, self._high, self._low, self._cur_val, self._volume

    def dump_candles(self):
        with self._lock:
            print("============= \"{}\" Candles  -- Start ==============".format(self._symbol))
            print(Globals.candle_keys)
            for candle in self._candles:
                print(candle.to_string())
            print("============= \"{}\" Candles -- End ==============".format(self._symbol))
