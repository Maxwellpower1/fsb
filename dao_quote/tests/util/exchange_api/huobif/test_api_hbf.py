# coding=utf-8

import asyncio
import pathmagic

from dao_quote.util.exchange_api.huobif import api_hbf


async def test_async_market_detail_merged():
    symbol = 'BTC_CQ'
    rst = await api_hbf.async_market_detail_merged(symbol)
    print(rst)


async def test_async_market_depth():
    symbol = 'BTC_CQ'
    type = 'step11'
    depth = await api_hbf.async_market_depth(symbol, type)
    # print(depth)
    depth = depth['tick']
    print(depth['asks'])
    print(depth['bids'])



async def test_async_market_history_kline():
    symbol = 'BTC_CQ'
    period = '1min'
    size = '10'
    kline = await api_hbf.async_market_history_kline(symbol, period, size)
    print(kline)
    return None


def test_contract_contract_info():
    symbol = ''
    contract_type = ''
    contract_code = ''
    # symbol = 'BTC'
    # contract_type = 'quarter'
    # contract_code = 'BTC190927'
    rst = api_hbf.contract_contract_info(symbol, contract_type, contract_code)
    print(rst)


def test_contract_index():
    symbol = 'BTC'
    rst = api_hbf.contract_index(symbol)
    print(rst)


def test_contract_price_limit():
    # symbol = 'BTC'
    # contract_type = 'quarter'
    # contract_code = ''

    symbol = ''
    contract_type = ''
    contract_code = 'BTC190927'
    rst = api_hbf.contract_price_limit(symbol, contract_type, contract_code)
    print(rst)


def test_contract_open_interest():
    # symbol = 'BTC'
    # contract_type = 'quarter'
    # contract_code = ''

    symbol = ''
    contract_type = ''
    contract_code = 'BTC190927'
    rst = api_hbf.contract_open_interest(symbol, contract_type, contract_code)
    print(rst)


def test_contract_delivery_price():
    symbol = 'BTC'
    rst = api_hbf.contract_delivery_price(symbol)
    print(rst)


def test_market_depth():
    symbol = 'BTC_CQ'  # BTC_CW; BTC_NW
    type = 'step11'
    rst = api_hbf.market_depth(symbol, type)
    print(rst)


def test_kline():
    symbol = 'BTC_CQ'
    period = '1min'
    size = '10'
    rst = api_hbf.market_history_kline(symbol, period, size)
    # for i in rst['data']:
    #     print(i)
    print(rst)


def test_market_detail_merged():
    symbol = 'BTC_CQ'
    rst = api_hbf.market_detail_merged(symbol)
    print(rst)


def test_market_trade():
    symbol = 'BTC_CQ'
    rst = api_hbf.market_trade(symbol)
    print(rst)


def test_market_history_trade():
    symbol = 'BTC_CW'
    size = 10
    rst = api_hbf.market_history_trade(symbol, size)
    print(rst)


def main():
    # tasks = []
    # tasks.append(test_async_market_detail_merged())
    # tasks.append(test_async_market_depth())
    # tasks.append(test_async_market_history_kline())
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(asyncio.gather(*tasks))
    # test_contract_contract_info()
    # test_contract_index()
    # test_contract_price_limit()
    # test_contract_open_interest()
    # test_contract_delivery_price()
    # test_market_depth()
    # test_kline()
    # test_market_detail_merged()
    # test_market_trade()
    # test_market_history_trade()
    print('test pass')


if __name__ == '__main__':
    main()
