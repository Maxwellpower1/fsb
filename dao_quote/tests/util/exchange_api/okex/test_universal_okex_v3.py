# coding=utf-8

import asyncio
import pathmagic

from dao_quote.util.exchange_api.okex import universal_okex_v3 as universal_okex


async def test_async_ticker():
    symbol = 'btc_usdt'
    rst = await universal_okex.async_ticker(symbol)
    print(rst)


async def test_async_bar():
    symbol = 'btc_usdt'
    rst = await universal_okex.async_bar(symbol)
    # print(rst)
    print(rst[-2])


async def test_async_depth():
    symbol = 'btc_usdt'
    rst = await universal_okex.async_depth(symbol)
    # print(rst['asks'][0])
    # print(rst['asks'][-1])
    # print(rst['bids'][0])
    # print(rst['bids'][-1])
    print(rst)


def test_ticker():
    symbol = 'btc_usdt'
    rst = universal_okex.ticker(symbol)
    print(rst)
    # print(rst['ticker']['last'])


def test_bar():
    symbol = 'btc_usdt'
    rst = universal_okex.bar(symbol)
    # print(rst)
    print(rst[-2])


def test_depth():
    symbol = 'btc_usdt'
    rst = universal_okex.depth(symbol)
    # print(rst['asks'][0])
    # print(rst['asks'][-1])
    # print(rst['bids'][0])
    # print(rst['bids'][-1])
    print(rst)


def main():
    tasks = []
    # tasks.append(test_async_ticker())
    # tasks.append(test_async_bar())
    tasks.append(test_async_depth())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(*tasks))
    # test_ticker()
    # test_bar()
    test_depth()
    print('test pass')


if __name__ == '__main__':
    main()
