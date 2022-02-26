# coding=utf-8

import asyncio
import pathmagic

from dao_quote.util.exchange_api.ctp import tq_api


def test_downloader():
    year = 2020
    month = 5
    exchange = 'CZCE'
    symbol = 'FG999'
    # exchange = 'DCE'
    # symbol = 'c999'
    # type_ = 'bar'
    type_ = 'tick'
    days = 0
    days = 1
    for month in range(1, 2):
        tq_api.downloader(year, month, exchange, symbol, type_, days)


def main():
    test_downloader()


if __name__ == '__main__':
    main()
