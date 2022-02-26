# coding=utf-8

import asyncio
import pathmagic

from dao_quote.util.exchange_api.huobi import api_hb


async def test_async_market_detail():
    symbol = 'btcusdt'
    rst = await api_hb.async_market_detail(symbol)
    print(rst)
    # print(rst['tick']['close'])


async def test_async_market_detail_merged():
    symbol = 'btcusdt'
    rst = await api_hb.async_market_detail_merged(symbol)
    print(rst)


async def test_async_market_depth():
    symbol = 'btcusdt'
    type = 'step1'
    depth = await api_hb.async_market_depth(symbol, type)
    print(depth)
    # print(depth['tick']['asks'])
    # depth['tick']['asks'].reverse()
    # print(depth['tick']['asks'])
    # print(depth['tick']['asks'][0])
    # print(depth['tick']['asks'][1])
    # print(depth['tick']['asks'][2])
    return None


async def test_async_market_history_kline():
    symbol = 'btcusdt'
    period = '1min'
    size = '10'
    kline = await api_hb.async_market_history_kline(symbol, period, size)
    print(kline)
    return None


def test_kline():
    symbol = 'btcusdt'
    period = '1min'
    size = '10'
    return api_hb.market_history_kline(symbol, period, size)


def test_market_detail_merged():
    symbol = 'eosusdt'
    return api_hb.market_detail_merged(symbol)


def test_market_tickers():
    return api_hb.market_tickers()


def test_market_depth():
    symbol = 'btcusdt'
    type = 'step1'
    depth = api_hb.market_depth(symbol, type)
    print(depth['tick']['asks'])
    depth['tick']['asks'].reverse()
    print(depth['tick']['asks'])
    print(depth['tick']['asks'][0])
    print(depth['tick']['asks'][1])
    print(depth['tick']['asks'][2])
    return None


def test_market_trade():
    symbol = 'btcusdt'
    return api_hb.market_trade(symbol)


def test_market_history_trade():
    symbol = 'btcusdt'
    size = 10
    return api_hb.market_history_trade(symbol, size)


def test_market_detail():
    symbol = 'eosusdt'
    return api_hb.market_detail(symbol)


def main():
    # tasks = []
    # tasks.append(test_async_market_detail())
    # tasks.append(test_async_market_detail_merged())
    # tasks.append(test_async_market_depth())
    # tasks.append(test_async_market_history_kline())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.gather(*tasks))
    # print(test_kline())
    # print(test_market_detail_merged())
    # print(test_market_tickers())
    # print(test_market_trade())
    # print(test_market_history_trade())
    # print(test_market_detail())
    print('pass')


if __name__ == '__main__':
    main()
