# coding=utf-8

import pathmagic

from dao_quote.util.exchange_api.okexf import wss_okexf_v5 as wss_okexf



def main():
    symbol_list = ['btc_usd-quarter']
    type_list = ['ticker', 'depth', 'trade', 'depthall', 'kline']
    # type_list = ['ticker']
    # type_list = ['trade']
    # type_list = ['depth']
    # type_list = ['depthall']
    # type_list = ['kline']
    wss_okexf.main(symbol_list, type_list)
    print('test pass')


if __name__ == '__main__':
    main()
