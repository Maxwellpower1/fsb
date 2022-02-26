# coding=utf-8

import pathmagic

from dao_quote.util.exchange_api.okex import wss_okex_v5 as wss_okex



def main():
    symbol_list = ['btc_usdt', 'ltc_usdt']
    type_list = ['ticker', 'depth', 'trade', 'depthall', 'kline']
    type_list = ['ticker']
    # type_list = ['trade']
    # type_list = ['depth']
    # type_list = ['depthall']
    # type_list = ['kline']
    wss_okex.main(symbol_list, type_list)
    print('test pass')


if __name__ == '__main__':
    main()
