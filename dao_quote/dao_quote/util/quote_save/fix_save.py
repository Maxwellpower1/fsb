# coding=utf-8

from dao_quote.util.quote_save import quote_save
from dao_quote.util.exchange_api.okexf import universal_okexf
from dao_quote.util.exchange_api.huobif import universal_huobif


def fix_bars(exchange, symbol, period):
    db_name = 'dao_quote.db'
    conn_bar = quote_save.get_db_conn(db_name)

    if (exchange == 'okexf'):
        data = universal_okexf.bars(symbol, period)
    elif (exchange == 'huobif'):
        if (period == '1hour'):
            period_ = '60min'
        else:
            period_ = period
        data = universal_huobif.bars(symbol, period_)
    else:
        pass
    key_name = '{}_{}_{}.{}'.format(exchange, symbol, 'kline', period)
    data = data[:-1]
    quote_save.save_bar(conn_bar, key_name, data)
    # print(key_name)
    # for i in data[-10:]:
    #     print(i)
    # print('*' * 50)
    return True
