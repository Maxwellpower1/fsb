# coding=utf-8

import time
import datetime


def combine_lines(klines, bars):
    new_klines = []
    length = int(len(klines)/bars)
    for i in range(0, length):
        klines_part = klines[i*bars:(i+1)*bars]
        klines_part_0 = klines_part[0]
        timestamp = klines_part_0[0]
        open = klines_part_0[1]
        high = klines_part_0[2]
        low = klines_part_0[3]
        close = klines_part[-1][4]
        volume = 0
        for kline in klines_part:
            high = max(high, kline[2])
            low = min(low, kline[3])
            volume += kline[5]
        new_klines.append([timestamp, open, high, low, close, volume])
    return new_klines


def combine_lines_3(klines, bars):
    new_klines = []
    if (len(klines) % bars == 0):
        length = int(len(klines)/bars)
    elif (len(klines) % bars > 0):
        length = int(len(klines)/bars) + 1
    for i in range(0, length):
        klines_part = klines[i*bars:(i+1)*bars]
        timestamp = klines_part[0][0]
        open = klines_part[0][1]
        high = klines_part[0][2]
        low = klines_part[0][3]
        close = klines_part[-1][4]
        volume = 0
        for kline in klines_part:
            if high < kline[2]:
                high = kline[2]
            if low > kline[3]:
                low = kline[3]
            volume += kline[5]
        new_klines.append([timestamp, open, high, low, close, volume])
        volume = 0
    return new_klines


def shift_time(timestamp):
    format = '%Y-%m-%d %H:%M:%S'
    value = time.localtime(timestamp)
    return time.strftime(format, value)


def to_timestamp(time_date):
    format = '%Y-%m-%d %H:%M:%S'
    timearray = time.strptime(time_date, format)
    timestamp = str(int(time.mktime(timearray)))
    return timestamp


def to_timestamp_es(time_date):
    time_date = time_date.split('.')
    ms = int(time_date[1])
    format = '%Y-%m-%d %H:%M:%S'
    timearray = time.strptime(time_date[0], format)
    timestamp = int(time.mktime(timearray))*1000+ms
    return timestamp


def to_timestamp_v3(iso_time):
    format = '%Y-%m-%dT%H:%M:%S.%fZ'
    dt = datetime.datetime.strptime(iso_time, format)
    timestamp = dt.replace(tzinfo=datetime.timezone.utc).timestamp()
    return timestamp


def to_timestamp_date(time_date):
    format = '%Y%m%d'
    timearray = time.strptime(time_date, format)
    timestamp = int(time.mktime(timearray))
    return timestamp


def ctp_timestamp(time_date):
    format = '%Y-%m-%d %H:%M:%S'
    timearray = time.strptime(time_date, format)
    timestamp = int(time.mktime(timearray))
    return timestamp


def ctp_date():
    format = '%Y-%m-%d'
    value = time.localtime()
    return time.strftime(format, value)
