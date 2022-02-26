# coding=utf-8

import time
import asyncio
import pathmagic

from dao_quote.util.exchange_api.okexf import api_okf_v5 as api_okf


async def test_async_all_ticker():
    rst = await api_okf.async_all_ticker()
    # for i in rst:
        # print(i)
    print(rst)


async def test_async_ticker():
    symbol = 'btc_usd-quarter'
    rst = await api_okf.async_ticker(symbol)
    print(rst)
    print(rst['last'])


async def test_async_depth():
    symbol = 'btc_usd-quarter'
    size = 7
    rst = await api_okf.async_depth(symbol, size)
    # print(rst['asks'][0])
    # print(rst['asks'][-1])
    # print(rst['bids'][0])
    # print(rst['bids'][-1])
    print(rst)


async def test_async_kline():
    symbol = 'btc_usd-quarter'
    type = '1min'
    size = 11
    since = 0
    rst = await api_okf.async_kline(symbol, type, size, since)
    print(rst)


def test_convert_symbol():
    symbol_dict = api_okf.convert_symbol()
    print(symbol_dict)


def test_convert_wss_symbol():
    symbol_dict, r_symbol_dict = api_okf.convert_wss_symbol()
    print(symbol_dict)
    print(r_symbol_dict)


def test_time_shift():
    timestamp = time.time()
    iso_time = api_okf.shift_time_v3(timestamp)
    timestamp_ = api_okf.to_timestamp_v3(iso_time)
    if (timestamp == timestamp_):
        print('test_time_shift pass')
    else:
        print('wrong: {} {}'.format(timestamp, timestamp_))
    return None


def test_instruments():
    rst = api_okf.instruments()
    print(rst)


def test_all_ticker():
    rst = api_okf.all_ticker()
    print(rst)


def test_ticker():
    symbol = 'btc_usd-this_week'
    symbol = 'btc_usd-next_week'
    symbol = 'btc_usd-quarter'
    symbol = 'btc_usd-bi_quarter'
    rst = api_okf.ticker(symbol)
    print(rst)


def test_depth():
    symbol = 'btc_usd-quarter'
    size = 9
    rst = api_okf.depth(symbol, size)
    print(rst)


def test_kline():
    symbol = 'btc_usd-quarter'
    type = '1min'
    size = 9
    since = 0
    rst = api_okf.kline(symbol, type, size, since)
    print(rst)



def main():
    tasks = []
    # tasks.append(test_async_all_ticker())
    # tasks.append(test_async_ticker())
    # tasks.append(test_async_depth())
    # tasks.append(test_async_kline())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.gather(*tasks))
    # test_convert_symbol()
    # test_convert_wss_symbol()
    # test_time_shift()
    # test_instruments()
    # test_all_ticker()
    # test_ticker()
    # test_depth()
    # test_kline()
    print('test pass')


if __name__ == '__main__':
    main()
