# coding=utf-8

import asyncio
import pathmagic

from dao_quote.util.exchange_api.okex import api_ok


async def test_async_ticker():
    symbol = 'btc_usdt'
    rst = await api_ok.async_ticker(symbol)
    print(rst)
    # print(rst['ticker']['last'])


async def test_async_depth():
    symbol = 'btc_usdt'
    size = 7
    rst = await api_ok.async_depth(symbol, size)
    # print(rst['asks'][0])
    # print(rst['asks'][-1])
    # print(rst['bids'][0])
    # print(rst['bids'][-1])
    print(rst)


async def test_async_kline():
    symbol = 'btc_usdt'
    type = '1min'
    size = 7
    since = 0
    rst = await api_ok.async_kline(symbol, type, size, since)
    rst = [[i[0], float(i[1]), float(i[2]), float(i[3]),
            float(i[4]), float(i[5])] for i in rst]
    print(rst)


def test_ticker():
    symbol = 'btc_usdt'
    rst = api_ok.ticker(symbol)
    print(rst)
    # print(rst['ticker']['last'])


def test_depth():
    symbol = 'btc_usdt'
    size = 7
    rst = api_ok.depth(symbol, size)
    # print(rst['asks'][0])
    # print(rst['asks'][-1])
    # print(rst['bids'][0])
    # print(rst['bids'][-1])
    print(rst)


def test_kline():
    symbol = 'btc_usdt'
    type = '1min'
    size = 7
    since = 0
    rst = api_ok.kline(symbol, type, size, since)
    rst = [[i[0], float(i[1]), float(i[2]), float(i[3]),
            float(i[4]), float(i[5])] for i in rst]
    print(rst)


def main():
    # tasks = []
    # tasks.append(test_async_ticker())
    # tasks.append(test_async_depth())
    # tasks.append(test_async_kline())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.gather(*tasks))
    # test_ticker()
    # test_depth()
    # test_kline()
    print('test pass')


if __name__ == '__main__':
    main()
