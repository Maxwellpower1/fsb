# coding=utf-8

import asyncio
import pathmagic

from dao_quote.util.exchange_api.fcoin import api_fc


async def test_async_ticker():
    symbol = 'btc_usdt'
    rst = await api_fc.async_ticker(symbol)
    print(rst)


async def test_async_depth():
    symbol = 'btc_usdt'
    level = 'L20'
    rst = await api_fc.async_depth(symbol, level)
    print(rst)


async def test_async_kline():
    symbol = 'btc_usdt'
    period = 'M1'
    rst = await api_fc.async_kline(symbol, period)
    print(rst)


def test_ticker():
    symbol = 'btc_usdt'
    rst = api_fc.ticker(symbol)
    print(rst)


def test_depth():
    symbol = 'btc_usdt'
    level = 'L20'
    rst = api_fc.depth(symbol, level)
    print(rst)


def test_kline():
    symbol = 'btc_usdt'
    period = 'M1'
    rst = api_fc.kline(symbol, period)
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
