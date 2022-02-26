# coding=utf-8

import asyncio
import pathmagic

from dao_quote.util.exchange_api.okexf import api_okf


async def test_async_future_ticker():
    symbol = 'btc_usd'
    contract_type = 'quarter'
    rst = await api_okf.async_future_ticker(symbol, contract_type)
    print(rst['ticker']['last'])


async def test_async_future_depth():
    symbol = 'btc_usd'
    size = 7
    contract_type = 'quarter'
    rst = await api_okf.async_future_depth(symbol, contract_type, size)
    # print(rst['asks'][0])
    # print(rst['asks'][-1])
    # print(rst['bids'][0])
    # print(rst['bids'][-1])
    print(rst)


async def test_async_future_kline():
    symbol = 'btc_usd'
    type = '1min'
    contract_type = 'quarter'
    size = 7
    since = 0
    rst = await api_okf.async_future_kline(symbol, type, contract_type, size, since)
    print(rst)


def test_future_ticker():
    symbol = 'btc_usd'
    contract_type = 'quarter'
    rst = api_okf.future_ticker(symbol, contract_type)
    print(rst['ticker']['last'])


def test_future_depth():
    symbol = 'btc_usd'
    size = 7
    contract_type = 'quarter'
    rst = api_okf.future_depth(symbol, contract_type, size)
    # print(rst['asks'][0])
    # print(rst['asks'][-1])
    # print(rst['bids'][0])
    # print(rst['bids'][-1])
    print(rst)


def test_future_kline():
    symbol = 'btc_usd'
    type = '1min'
    contract_type = 'quarter'
    size = 7
    since = 0
    rst = api_okf.future_kline(symbol, type, contract_type, size, since)
    print(rst)


def main():
    # tasks = []
    # tasks.append(test_async_future_ticker())
    # tasks.append(test_async_future_depth())
    # tasks.append(test_async_future_kline())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.gather(*tasks))
    # test_future_ticker()
    # test_future_depth()
    # test_future_kline()
    print('test pass')


if __name__ == '__main__':
    main()
