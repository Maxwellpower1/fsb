# coding=utf-8

import time
import asyncio

from dao_quote.util.exchange_api.okex import api_ok
from dao_quote.util.exchange_api.okexf import api_okf
from dao_quote.util.exchange_api.huobi import api_hb
from dao_quote.util.exchange_api.huobif import api_hbf
from dao_quote.util.exchange_api.binance import api_ba


async def set_async_ticker(db_name, exchange, symbol):
    if (exchange == 'OKEX'):
        try:
            data = await api_ok.async_ticker(symbol)
            data = data['ticker']
            data['ask'] = data['sell']
            data['bid'] = data['buy']
        except Exception as e:
            data = {}
    elif (exchange == 'okexf'):
        try:
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('-')[0]
            data = await api_okf.async_future_ticker(symbol_, contract_type)
            data = data['ticker']
            data['ask'] = data['sell']
            data['bid'] = data['buy']
        except Exception as e:
            data = {}
    elif (exchange == 'Huobi'):
        try:
            data = await api_hb.async_market_detail_merged(symbol)
            data = data['tick']
            data['last'] = data['close']
            data['ask'] = data['ask'][0]
            data['bid'] = data['bid'][0]
        except Exception as e:
            data = {}
    elif (exchange == 'huobif'):
        try:
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('_')[0].upper()
            if (contract_type == 'this_week'):
                contract_type = 'CW'
            elif (contract_type == 'next_week'):
                contract_type = 'NW'
            elif (contract_type == 'quarter'):
                contract_type = 'CQ'
            symbol_ = '{}_{}'.format(symbol_, contract_type)
            data = await api_hbf.async_market_detail_merged(symbol_)
            data = data['tick']
            data['last'] = data['close']
            data['ask'] = data['ask'][0]
            data['bid'] = data['bid'][0]
        except Exception as e:
            data = {}
    elif (exchange == 'Binance'):
        try:
            data = await api_ba.async_ticker(symbol)
            tick_dict = {}
            tick_dict['last'] = data['lastPrice']
            tick_dict['high'] = data['highPrice']
            tick_dict['low'] = data['lowPrice']
            tick_dict['vol'] = data['volume']
            tick_dict['ask'] = data['askPrice']
            tick_dict['bid'] = data['bidPrice']
            data = tick_dict
        except Exception as e:
            data = {}
    else:
        data = {}
    return data


async def set_async_kline(db_name, exchange, symbol):
    data = {}
    if (exchange == 'OKEX'):
        try:
            type = '1min'
            size = '500'
            since = ''
            data_ = await api_ok.async_kline(symbol, type, size, since)
            data = [[i[0], float(i[1]), float(i[2]), float(i[3]),
                    float(i[4]), float(i[5])] for i in data_]
            del data_
        except Exception as e:
            print(e)
            data = {}
    elif (exchange == 'okexf'):
        try:
            type = '1min'
            size = '500'
            since = ''
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('-')[0]
            data = await api_okf.async_future_kline(symbol_, type, contract_type, size, since)
        except Exception as e:
            data = {}
    elif (exchange == 'Huobi'):
        try:
            period = '1min'
            size = '500'
            data_ = await api_hb.async_market_history_kline(symbol, period, size)
            data = []
            for k in data_['data']:
                data.append([k['id']*1000, k['open'], k['high'], k['low'], k['close'], k['amount'], k['vol']])
            del data_
            data.reverse()
        except Exception as e:
            data = {}
    elif (exchange == 'huobif'):
        try:
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('_')[0].upper()
            if (contract_type == 'this_week'):
                contract_type = 'CW'
            elif (contract_type == 'next_week'):
                contract_type = 'NW'
            elif (contract_type == 'quarter'):
                contract_type = 'CQ'
            symbol_ = '{}_{}'.format(symbol_, contract_type)
            period = '1min'
            size = '500'
            data_ = await api_hbf.async_market_history_kline(symbol_, period, size)
            data = []
            for k in data_['data']:
                data.append([k['id']*1000, k['open'], k['high'], k['low'], k['close'], k['vol'], k['amount']])
            # data.reverse()
            del data_
        except Exception as e:
            data = {}
    elif (exchange == 'Binance'):
        try:
            period = '1min'
            interval = period.lower()[:-2]
            # time_1 = await api_ba.async_time()
            # time_1 = time_1['serverTime']
            time_1 = int(time.time()) * 1000
            interval_seconds = int(interval[:-1]) * 60
            limit = 500
            startTime = time_1 - (interval_seconds * 1000 * limit)
            endTime = time_1
            data_ = await api_ba.async_klines(symbol, interval,
                   startTime, endTime, limit)
            data_ = data_[-limit:]
            data = [[i[0], float(i[1]), float(i[2]), float(i[3]),
                    float(i[4]), float(i[5])] for i in data_]
            del data_
        except Exception as e:
            print(e)
            data = {}
    else:
        data = {}
    return data


async def set_async_depth(db_name, exchange, symbol):
    data = {}
    if (exchange == 'OKEX'):
        try:
            size = 9
            data = await api_ok.async_depth(symbol, size)
        except Exception as e:
            data = {}
    elif (exchange == 'okexf'):
        try:
            size = 9
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('-')[0]
            data = await api_okf.async_future_depth(symbol_, contract_type, size)
        except Exception as e:
            data = {}
    elif (exchange == 'Huobi'):
        try:
            type = 'step0'
            data = await api_hb.async_market_depth(symbol, type)
            data = data['tick']
            data['asks'].reverse()
            data['asks'] = data['asks'][-9:]
            data['bids'] = data['bids'][0:9]
        except Exception as e:
            data = {}
    elif (exchange == 'huobif'):
        try:
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('_')[0].upper()
            if (contract_type == 'this_week'):
                contract_type = 'CW'
            elif (contract_type == 'next_week'):
                contract_type = 'NW'
            elif (contract_type == 'quarter'):
                contract_type = 'CQ'
            symbol_ = '{}_{}'.format(symbol_, contract_type)
            type = 'step6'
            data = await api_hbf.async_market_depth(symbol_, type)
            data = data['tick']
            data['asks'].reverse()
        except Exception as e:
            data = {}
    elif (exchange == 'Binance'):
        try:
            limit = 10
            data = await api_ba.async_depth(symbol, limit)
            data['asks'].reverse()
        except Exception as e:
            data = {}
    else:
        data = {}
    return data


def set_ticker(db_name, exchange, symbol):
    if (exchange == 'OKEX'):
        try:
            data = api_ok.ticker(symbol)
            data = data['ticker']
            data['ask'] = data['sell']
            data['bid'] = data['buy']
        except Exception as e:
            data = {}
    elif (exchange == 'okexf'):
        try:
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('-')[0]
            data = api_okf.future_ticker(symbol_, contract_type)
            data = data['ticker']
            data['ask'] = data['sell']
            data['bid'] = data['buy']
        except Exception as e:
            data = {}
    elif (exchange == 'Huobi'):
        try:
            data = api_hb.market_detail_merged(symbol)
            data = data['tick']
            data['last'] = data['close']
            data['ask'] = data['ask'][0]
            data['bid'] = data['bid'][0]
        except Exception as e:
            data = {}
    elif (exchange == 'huobif'):
        try:
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('_')[0].upper()
            if (contract_type == 'this_week'):
                contract_type = 'CW'
            elif (contract_type == 'next_week'):
                contract_type = 'NW'
            elif (contract_type == 'quarter'):
                contract_type = 'CQ'
            symbol_ = '{}_{}'.format(symbol_, contract_type)
            data = api_hbf.market_detail_merged(symbol_)
            data = data['tick']
            data['last'] = data['close']
            data['ask'] = data['ask'][0]
            data['bid'] = data['bid'][0]
        except Exception as e:
            data = {}
    elif (exchange == 'Binance'):
        try:
            data = api_ba.ticker(symbol)
            tick_dict = {}
            tick_dict['last'] = data['lastPrice']
            tick_dict['high'] = data['highPrice']
            tick_dict['low'] = data['lowPrice']
            tick_dict['vol'] = data['volume']
            tick_dict['ask'] = data['askPrice']
            tick_dict['bid'] = data['bidPrice']
            data = tick_dict
        except Exception as e:
            data = {}
    else:
        data = {}
    return data


def set_kline(db_name, exchange, symbol):
    global kline_dict
    global period_list
    data = {}
    if (exchange == 'OKEX'):
        try:
            type = '1min'
            size = '500'
            since = ''
            data_ = api_ok.kline(symbol, type, size, since)
            data = [[i[0], float(i[1]), float(i[2]), float(i[3]),
                    float(i[4]), float(i[5])] for i in data_]
            del data_
        except Exception as e:
            print(e)
            data = {}
    elif (exchange == 'okexf'):
        try:
            type = '1min'
            size = '500'
            since = ''
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('-')[0]
            data = api_okf.future_kline(symbol_, type, contract_type, size, since)
        except Exception as e:
            data = {}
    elif (exchange == 'Huobi'):
        try:
            period = '1min'
            size = '500'
            data_ = api_hb.market_history_kline(symbol, period, size)
            data = []
            for k in data_['data']:
                data.append([k['id']*1000, k['open'], k['high'], k['low'], k['close'], k['amount'], k['vol']])
            del data_
            data.reverse()
        except Exception as e:
            data = {}
    elif (exchange == 'huobif'):
        try:
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('_')[0].upper()
            if (contract_type == 'this_week'):
                contract_type = 'CW'
            elif (contract_type == 'next_week'):
                contract_type = 'NW'
            elif (contract_type == 'quarter'):
                contract_type = 'CQ'
            symbol_ = '{}_{}'.format(symbol_, contract_type)
            period = '1min'
            size = '500'
            data_ = api_hbf.market_history_kline(symbol_, period, size)
            data = []
            for k in data_['data']:
                data.append([k['id']*1000, k['open'], k['high'], k['low'], k['close'], k['vol'], k['amount']])
            # data.reverse()
            del data_
        except Exception as e:
            data = {}
    elif (exchange == 'Binance'):
        try:
            period = '1min'
            interval = period.lower()[:-2]
            time_1 = int(time.time()) * 1000
            interval_seconds = int(interval[:-1]) * 60
            limit = 500
            startTime = time_1 - (interval_seconds * 1000 * limit)
            endTime = time_1
            data_ = api_ba.klines(symbol, interval,
                   startTime, endTime, limit)
            data_ = data_[-limit:]
            data = [[i[0], float(i[1]), float(i[2]), float(i[3]),
                    float(i[4]), float(i[5])] for i in data_]
            del data_
        except Exception as e:
            print(e)
            data = {}
    else:
        data = {}
    return data


def set_depth(db_name, exchange, symbol):
    data = {}
    if (exchange == 'OKEX'):
        try:
            size = 9
            data = api_ok.depth(symbol, size)
        except Exception as e:
            data = {}
    elif (exchange == 'okexf'):
        try:
            size = 9
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('-')[0]
            data = api_okf.future_depth(symbol_, contract_type, size)
        except Exception as e:
            data = {}
    elif (exchange == 'Huobi'):
        try:
            type = 'step0'
            data = api_hb.market_depth(symbol, type)
            data = data['tick']
            data['asks'].reverse()
            data['asks'] = data['asks'][-9:]
            data['bids'] = data['bids'][0:9]
        except Exception as e:
            data = {}
    elif (exchange == 'huobif'):
        try:
            contract_type = symbol.split('-')[1]
            symbol_ = symbol.split('_')[0].upper()
            if (contract_type == 'this_week'):
                contract_type = 'CW'
            elif (contract_type == 'next_week'):
                contract_type = 'NW'
            elif (contract_type == 'quarter'):
                contract_type = 'CQ'
            symbol_ = '{}_{}'.format(symbol_, contract_type)
            type = 'step6'
            data = api_hbf.market_depth(symbol_, type)
            data = data['tick']
            data['asks'].reverse()
        except Exception as e:
            data = {}
    elif (exchange == 'Binance'):
        try:
            limit = 10
            data = api_ba.depth(symbol, limit)
            data['asks'].reverse()
        except Exception as e:
            data = {}
    else:
        data = {}
    return data


def main():
    pass


if __name__ == '__main__':
    main()
