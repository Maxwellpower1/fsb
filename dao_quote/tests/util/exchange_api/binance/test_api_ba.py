# coding=utf-8

import asyncio
import pathmagic

from dao_quote.util.exchange_api.binance import api_ba


async def test_async_ticker():
    symbol = 'BTCUSDT'
    rst = await api_ba.async_ticker(symbol)
    print(rst)


async def test_async_depth():
    symbol = 'BTCUSDT'
    type = 'step1'
    limit = 10
    depth = await api_ba.async_depth(symbol, limit)
    print(depth)
    # print(depth['tick']['asks'])
    # depth['tick']['asks'].reverse()
    # print(depth['tick']['asks'])
    # print(depth['tick']['asks'][0])
    # print(depth['tick']['asks'][1])
    # print(depth['tick']['asks'][2])
    return None


async def test_async_klines():
    symbol = 'BTCUSDT'
    period = '1min'
    interval = period.lower()[:-2]
    time_1 = api_ba.time()['serverTime']
    interval_seconds = int(interval[:-1]) * 60
    startTime = time_1-(interval_seconds * 1000 * 70)
    endTime = time_1
    limit = 70
    kline = await api_ba.async_klines(symbol, interval, startTime, endTime, limit)
    kline = [[i[0], float(i[1]), float(i[2]), float(i[3]),
            float(i[4]), float(i[5])] for i in kline]
    print(kline)
    return None


def test_ticker():
    symbol = 'BTCUSDT'
    rst = api_ba.ticker(symbol)
    print(rst)


def test_depth():
    symbol = 'BTCUSDT'
    type = 'step1'
    limit = 10
    depth = api_ba.depth(symbol, limit)
    print(depth)
    # print(depth['tick']['asks'])
    # depth['tick']['asks'].reverse()
    # print(depth['tick']['asks'])
    # print(depth['tick']['asks'][0])
    # print(depth['tick']['asks'][1])
    # print(depth['tick']['asks'][2])
    return None


def test_klines():
    symbol = 'BTCUSDT'
    period = '1min'
    interval = period.lower()[:-2]
    time_1 = api_ba.time()['serverTime']
    interval_seconds = int(interval[:-1]) * 60
    startTime = time_1-(interval_seconds * 1000 * 70)
    endTime = time_1
    limit = 70
    kline = api_ba.klines(symbol, interval, startTime, endTime, limit)
    print(kline)
    return None


def main():
    # tasks = []
    # tasks.append(test_async_ticker())
    # tasks.append(test_async_depth())
    # tasks.append(test_async_klines())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.gather(*tasks))
    # test_ticker()
    # test_depth()
    # test_klines()
    print('pass')


if __name__ == '__main__':
    main()
