import api_key_x
import pathmagic

from dao_execute.exchange_api.okexf.api_okf_v5 import ApiOkf


class testApiOkf(object):

    def __init__(self):
        self.api_key = api_key_x.API_KEY_V5
        self.secret_key = api_key_x.SECRET_KEY_V5
        self.api_okf = ApiOkf()

    def test_instruments(self):
        instType = 'FUTURES'
        data = self.api_okf.instruments(instType)
        print(data)

    def test_tickers(self):
        data = self.api_okf.tickers()
        print(data)

    def test_ticker(self):
        symbol = 'btc_usd-quarter'
        data = self.api_okf.ticker(symbol)
        print(data)

    def test_books(self):
        symbol = 'btc_usd-quarter'
        size = 10
        data = self.api_okf.books(symbol, size)
        print(data)

    def test_candles(self):
        symbol = 'btc_usd-quarter'
        period = '1m'
        num = '100'
        data = self.api_okf.candles(symbol, period, num)
        print(data)

    def test_balances(self):
        # coin = 'BTC'
        coin = ''
        data = self.api_okf.balances(self.api_key, self.secret_key, coin)
        print(data)

    def test_balance(self):
        coin = 'BTC'
        data = self.api_okf.balance(self.api_key, self.secret_key, coin)
        print(data)

    def test_positions(self):
        symbol = 'btc_usd-quarter'
        data = self.api_okf.positions(self.api_key, self.secret_key, symbol)
        print(data)

    def test_future_trade(self):
        symbol = 'btc_usd-quarter'
        # type = 'market_going_long'
        # type = 'market_going_short'
        # type = 'market_close_long'
        # type = 'market_close_short'
        type = 'limit_close_long'
        price = '46000'
        size = '1'
        data = self.api_okf.future_trade(symbol, type, price, size, self.api_key, self.secret_key)
        print(data)
        id = int(data[0]['ordId'])
        error_code = int(data[0]['sCode'])
        print(id, error_code)

    def test_future_cancel(self):
        symbol = 'btc_usd-quarter'
        order_id = '361508075957800966'
        data = self.api_okf.future_cancel(symbol, order_id, self.api_key, self.secret_key)
        print(data)
        order_id = data[0]['ordId']
        error_code = data[0]['sCode']
        # error_code 51401 已经撤单
        print(order_id, error_code)

    def test_fetch_order(self):
        symbol = 'btc_usd-quarter'
        order_id = '361508075957800966'
        data = self.api_okf.fetch_order(symbol, order_id, self.api_key, self.secret_key)
        print(data)
        # state: live, canceled
        print(data[0]['avgPx'], data[0]['px'])

    def test_fresh_symbol_dict(self):
        print(self.api_okf.symbol_dict)
        self.api_okf.fresh_symbol_dict()
        print(self.api_okf.symbol_dict)

    def test_process_symbol(self):
        symbol_list = ['btc_usd-this_week', 'btc_usd-quarter',
                       'btc_usd-next_quarter']
        for symbol_ in symbol_list:
            symbol = self.api_okf.process_symbol(symbol_)
            print(symbol_, symbol)


def main():
    tao = testApiOkf()
    # tao.test_instruments()
    # tao.test_tickers()
    # tao.test_ticker()
    # tao.test_books()
    # tao.test_candles()
    # tao.test_balance()
    # tao.test_balances()
    # tao.test_positions()
    # tao.test_future_trade()
    # tao.test_future_cancel()
    tao.test_fetch_order()
    # tao.test_fresh_symbol_dict()
    # tao.test_process_symbol()
    pass


if __name__ == '__main__':
    main()
