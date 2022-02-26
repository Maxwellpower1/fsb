service DaoQuote {
    string get_ticker(
        1: string sig,
        2: string exchange,
        3: string symbol
    ),
    string get_kline(
        1: string sig,
        2: string exchange,
        3: string symbol
    ),
    string get_depth(
        1: string sig,
        2: string exchange,
        3: string symbol
    ),
    string get_spread_line(
        1: string sig,
        2: string exchange_a,
        3: string symbol_a,
        4: string exchange_b,
        5: string symbol_b,
        6: string period
    ),
    string get_backtest_kline_db(
        1: string sig,
        2: string exchange,
        3: string symbol,
        4: string period,
        5: string begin_timestamp,
        6: string end_timestamp
    ),
    string get_kline_db(
        1: string sig,
        2: string exchange,
        3: string symbol,
        4: string period,
        5: string num,
        6: string end_timestamp
    ),
    string get_sqlite_klines_df(
        1: string sig,
        2: string exchange,
        3: string symbol,
        4: string begin_timestamp,
        5: string end_timestamp
    ),
    string get_hfd(
        1: string sig,
        2: string exchange,
        3: string symbol,
        4: string type_list,
        5: string begin_timestamp,
        6: string end_timestamp
    ),
    string get_trade_dict_list(
        1: string sig,
        2: string exchange,
        3: string symbol,
        4: string begin_timestamp,
        5: string end_timestamp
    ),
    string download_dao_quote(
        1: string sig,
        2: string begin_time,
        3: string end_time
    ),
}
