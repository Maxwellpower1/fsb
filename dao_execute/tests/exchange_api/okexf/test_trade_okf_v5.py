import api_key_x
import pathmagic

from dao_execute.exchange_api.okexf import trade_okf_v5 as trade_okf


class testTradeOkf(object):

    def __init__(self):
        self.api_key = api_key_x.API_KEY_V5
        self.secret_key = api_key_x.SECRET_KEY_V5

    def test_future_trade(self):
        symbol = 'btc_usd-quarter'
        # order_type = 'market_going_long'
        # order_type = 'market_going_short'
        order_type = 'market_close_long'
        # order_type = 'market_close_short'
        # order_type = 'limit_close_long'
        amount = '1'
        price = '96000'
        order_id = trade_okf.future_trade(symbol, order_type, self.api_key, self.secret_key, amount, price)
        print(order_id)

    def test_future_cancel(self):
        symbol = 'btc_usd-quarter'
        # order_id = '396076776430129157' # filled
        order_id = '396081748303564801'
        data = trade_okf.future_cancel(symbol, order_id, self.api_key, self.secret_key)
        print(data)

    def test_fetch_order(self):
        symbol = 'btc_usd-quarter'
        # order_id = '396076776430129157' # filled
        order_id = '396082694853120002'
        order_dict = trade_okf.fetch_order(symbol, order_id, self.api_key, self.secret_key)
        order_dict = order_dict['orders'][0]
        print(order_dict)


def main():
    tto = testTradeOkf()
    tto.test_future_trade()
    # tto.test_future_cancel()
    tto.test_fetch_order()
    pass


if __name__ == '__main__':
    main()
