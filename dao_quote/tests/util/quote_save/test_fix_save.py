# coding=utf-8

import pathmagic

from dao_quote.util.quote_save import fix_save


def test_fix_bars():
    exchange = 'okexf'
    symbol = 'eos_usd-quarter'
    period = '3min'
    rst = fix_save.fix_bars(exchange, symbol, period)
    print(exchange, symbol, period, rst)
    period = '15min'
    rst = fix_save.fix_bars(exchange, symbol, period)
    print(exchange, symbol, period, rst)
    exchange = 'huobif'
    symbol = 'btc_usd-quarter'
    period = '15min'
    rst = fix_save.fix_bars(exchange, symbol, period)
    print(exchange, symbol, period, rst)
    period = '1hour'
    rst = fix_save.fix_bars(exchange, symbol, period)
    print(exchange, symbol, period, rst)


def main():
    test_fix_bars()


if __name__ == '__main__':
    main()
