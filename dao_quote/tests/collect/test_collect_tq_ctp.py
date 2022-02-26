#coding=utf-8

import datetime
import pathmagic
from dao_quote.settings import config_x
from dao_quote.collect import collect_tq_ctp
from dao_quote.settings import config_collect


def test_download():
    days = 1
    symbols = ['c2009']
    collect_tq_ctp.download(days, symbols=symbols)


def test_collect_ctp():
    symbol = 'SHFE.au2012'

    from tqsdk import TqApi
    api = TqApi(web_gui='127.0.0.1:9099')
    quote = api.get_quote(symbol)
    klines = api.get_kline_serial(symbol, 60)
    while True:
        api.wait_update()
        # print(quote.datetime, quote.last_price)
        # print("最后一根K线收盘价", klines.close.iloc[-1])
        # print(quote)
        if api.is_changing(klines.iloc[-1], "datetime"):
            print("新K线", datetime.datetime.now(), datetime.datetime.fromtimestamp(klines.iloc[-1]["datetime"] / 1e9))
            symbol = klines.loc[0, "symbol"]
            kline_list = []
            for i in range(len(klines)):
                kline = [int(klines.loc[i, "datetime"]/1e6), klines.loc[i, "open"], klines.loc[i, "high"], klines.loc[i, "low"], klines.loc[i, "close"], klines.loc[i, "volume"], klines.loc[i, "close_oi"]-klines.loc[i, "open_oi"]]
                kline_list.append(kline)
            print(kline_list[-1])
        # print(klines.iloc[-1])


def test_main():
    collect_tq_ctp.main()


def main():
    # test_download()
    # test_collect_ctp()
    test_main()


if __name__ == '__main__':
    main()
