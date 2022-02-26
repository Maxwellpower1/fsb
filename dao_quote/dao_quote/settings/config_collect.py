# !/usr/bin/env python
# coding=utf-8


EXCHANGE_DICT = {
    'okex': ['btc_usdt', 'eos_usdt', 'ltc_usdt', 'eth_usdt', 'xrp_usdt',
             'okb_usdt'],
    'okexf': ['btc_usd-quarter', 'eos_usd-quarter', 'ltc_usd-quarter',
              'eth_usd-quarter', 'xrp_usd-quarter',
              'btc_usd-bi_quarter', 'eos_usd-bi_quarter', 'ltc_usd-bi_quarter',
              'eth_usd-bi_quarter', 'xrp_usd-bi_quarter',
              'btc_usd-this_week', 'eos_usd-this_week', 'ltc_usd-this_week',
              'eth_usd-this_week', 'xrp_usd-this_week',
              'btc_usd-next_week', 'eos_usd-next_week', 'ltc_usd-next_week',
              'eth_usd-next_week', 'xrp_usd-next_week',
              'btc_usdt-quarter', 'eos_usdt-quarter', 'ltc_usdt-quarter',
              'eth_usdt-quarter', 'xrp_usdt-quarter',
              'btc_usdt-bi_quarter', 'eos_usdt-bi_quarter', 'ltc_usdt-bi_quarter',
              'eth_usdt-bi_quarter', 'xrp_usdt-bi_quarter',
              'btc_usdt-this_week', 'eos_usdt-this_week', 'ltc_usdt-this_week',
              'eth_usdt-this_week', 'xrp_usdt-this_week',
              'btc_usdt-next_week', 'eos_usdt-next_week', 'ltc_usdt-next_week',
              'eth_usdt-next_week', 'xrp_usdt-next_week'],
    'huobi': ['btc_usdt', 'eos_usdt', 'ltc_usdt', 'eth_usdt', 'xrp_usdt'],
    'huobif': ['btc_usd-quarter', 'eos_usd-quarter', 'ltc_usd-quarter',
               'eth_usd-quarter',
               'btc_usd-this_week', 'eos_usd-this_week', 'ltc_usd-this_week',
               'eth_usd-this_week',
               'btc_usd-next_week', 'eos_usd-next_week', 'ltc_usd-next_week',
               'eth_usd-next_week'],
    'binance': ['btc_usdt', 'eos_usdt', 'ltc_usdt', 'eth_usdt', 'xrp_usdt']
}

IMPORTANT_KEY_NAME_LIST = ['okexf_btc_usd-quarter_kline', 'okexf_eos_usd-quarter_kline',
                           'huobif_btc_usd-quarter_kline']

TYPE_LIST = ['ticker', 'kline', 'depth']

# WSS_EXCHANGE_DICT = {
#     'okex': ['btc_usdt'],
#     'okexf': ['btc_usd-quarter', 'btc_usd-bi_quarter'],
#     'huobi': ['btc_usdt'],
#     'huobif': ['btc_usd-quarter'],
#     'binance': ['btc_usdt']
# }
#
# WSS_TYPE_LIST = ['ticker', 'depth', 'trade', 'depthall', 'kline']

WSS_EXCHANGE_DICT = {'okexf': ['btc_usd-quarter', 'eth_usd-quarter', 'xrp_usd-quarter', 'eos_usd-quarter']}
WSS_TYPE_LIST = ['kline']

HFD_EXCHANGE_DICT = {
    # 'okexf': ['btc_usd-quarter'],
    # 'okex': ['okb_usdt'],
    'ctp': ["rb2205", "rb2209", "fu2205", "fu2209", "hc2205", "hc2209",
            "sp2205", "sp2209", "a2205", "a2209", "b2205", "b2209",
            "c2205", "c2209", "cs2205", "cs2209", "i2205", "i2209",
            "j2205", "j2209", "jd2205", "jd2209", "jm2205", "jm2209",
            "l2205", "l2209", "m2205", "m2209", "p2205", "p2209",
            "pp2205", "pp2209", "v2205", "v2209", "y2205", "y2209",
            "eg2205", "eg2209", "rr2205", "eb2205", "eb2209",
            "CF205", "CF209", "CY205", "CY209", "SR205", "SR209",
            "TA205", "TA209", "OI205", "OI209", "MA205", "MA209",
            "FG205", "FG209", "RM205", "RM209", "ZC205", "ZC209",
            "SF205", "SF209", "SM205", "SM209", "AP205",
            "CJ205", "CJ209", "UR205", "UR209", "SA205", "SA209"]
}

SAVE_EXCHANGE_DICT = {
    'okex': ['btc_usdt', 'eos_usdt', 'ltc_usdt', 'eth_usdt', 'xrp_usdt',
             'okb_usdt', 'etc_usdt', 'bch_usdt', 'trx_usdt', 'bsv_usdt',
             'dash_usdt', 'ada_usdt', 'xmr_usdt', 'ae_usdt', 'algo_usdt',
             'bloc_usdt', 'btm_usdt', 'btt_usdt', 'etm_usdt', 'leo_usdt',
             'zec_usdt', 'vnt_usdt', 'wxt_usdt', 'neo_usdt', 'qtum_usdt',
             'atom_usdt', 'iost_usdt', 'xlm_usdt',
             'btc_usdk', 'eos_usdk', 'ltc_usdk', 'eth_usdk', 'xrp_usdk',
             'okb_usdk', 'etc_usdk', 'bch_usdk', 'trx_usdk', 'bsv_usdk',
             'dash_usdk', 'ada_usdk', 'xmr_usdk', 'ae_usdk', 'algo_usdk',
             'bloc_usdk', 'btm_usdk', 'btt_usdk', 'etm_usdk', 'leo_usdk',
             'zec_usdk', 'vnt_usdk', 'wxt_usdk', 'neo_usdk', 'qtum_usdk',
             'atom_usdk',
             'usdt_usdk', 'gusd_usdt', 'pax_usdt', 'usdc_usdt',
             'ltc_btc', 'eth_btc', 'okb_btc', 'etc_btc', 'bch_btc', 'eos_btc',
             'xrp_btc', 'trx_btc', 'bsv_btc', 'dash_btc', 'neo_btc', 'qtum_btc',
             'xlm_btc', 'ada_btc', 'ae_btc', 'algo_btc', 'atom_btc', 'bloc_btc',
             'btm_btc', 'btt_btc', 'iost_btc', 'leo_btc','zec_btc',
             'ltc_eth', 'okb_eth', 'etc_eth', 'bch_eth', 'eos_eth',
             'xrp_eth', 'trx_eth', 'bsv_eth', 'dash_eth', 'neo_eth', 'qtum_eth',
             'xlm_eth', 'ada_eth', 'ae_eth', 'algo_eth', 'atom_eth', 'bloc_eth',
             'btm_eth', 'btt_eth', 'iost_eth', 'leo_eth','zec_eth'
            ],
    'okexf': ['btc_usd-quarter', 'eos_usd-quarter', 'ltc_usd-quarter',
              'eth_usd-quarter', 'xrp_usd-quarter', 'trx_usd-quarter',
              'etc_usd-quarter', 'bch_usd-quarter', 'bsv_usd-quarter',
              'btc_usd-this_week', 'eos_usd-this_week', 'ltc_usd-this_week',
              'eth_usd-this_week', 'xrp_usd-this_week', 'trx_usd-this_week',
              'etc_usd-this_week', 'bch_usd-this_week', 'bsv_usd-this_week',
              'btc_usd-next_week', 'eos_usd-next_week', 'ltc_usd-next_week',
              'eth_usd-next_week', 'xrp_usd-next_week', 'trx_usd-next_week',
              'etc_usd-next_week', 'bch_usd-next_week', 'bsv_usd-next_week'
             ],
    'huobi': ['btc_usdt', 'eos_usdt', 'ltc_usdt', 'eth_usdt', 'xrp_usdt',
              'ht_usdt', 'etc_usdt', 'bch_usdt', 'trx_usdt', 'bsv_usdt',
              'dash_usdt', 'ada_usdt', 'xmr_usdt', 'ae_usdt', 'algo_usdt',
              'new_usdt', 'btm_usdt', 'btt_usdt', 'top_usdt', 'doge_usdt',
              'zec_usdt', 'neo_usdt', 'qtum_usdt',
              'atom_usdt', 'xlm_usdt',
              'usdt_husd', 'btc_husd', 'eth_husd', 'xrp_husd', 'eos_husd',
              'ht_husd',
              'ltc_btc', 'eth_btc', 'ht_btc', 'etc_btc', 'bch_btc', 'eos_btc',
              'xrp_btc', 'trx_btc', 'bsv_btc', 'dash_btc', 'neo_btc', 'qtum_btc',
              'xlm_btc', 'ada_btc', 'ae_btc', 'algo_btc', 'atom_btc', 'top_btc',
              'btm_btc', 'btt_btc', 'iost_btc', 'zec_btc',
              'xmr_btc',
              'ltc_eth', 'ht_eth', 'eos_eth',
              'xrp_eth', 'trx_eth', 'bsv_eth', 'qtum_eth', 'xmr_eth',
              'xlm_eth', 'ada_eth', 'ae_eth', 'algo_eth', 'atom_eth',
              'btm_eth', 'btt_eth', 'iost_eth'
             ],
    'huobif': ['btc_usd-quarter', 'eos_usd-quarter', 'ltc_usd-quarter',
               'eth_usd-quarter', 'bch_usd-quarter', 'trx_usd-quarter',
               'btc_usd-this_week', 'eos_usd-this_week', 'ltc_usd-this_week',
               'eth_usd-this_week', 'bch_usd-this_week', 'trx_usd-this_week',
               'btc_usd-next_week', 'eos_usd-next_week', 'ltc_usd-next_week',
               'eth_usd-next_week', 'bch_usd-next_week', 'trx_usd-next_week',
              ],
    'binance': ['BTC_USDT', 'EOS_USDT', 'LTC_USDT', 'ETH_USDT', 'XRP_USDT',
                'BNB_USDT', 'ETC_USDT', 'BCHABC_USDT', 'TRX_USDT',
                'DASH_USDT', 'ADA_USDT', 'XMR_USDT', 'AE_USDT', 'ALGO_USDT',
                'CELR_USDT', 'BTT_USDT', 'XLM_USDT', 'ATOM_USDT',
                'ZEC_USDT', 'NEO_USDT', 'QTUM_USDT', 'IOST_USDT',

                'LTC_BTC', 'ETH_BTC', 'BNB_BTC', 'ETC_BTC', 'BCHABC_BTC', 'EOS_BTC',
                'XRP_BTC', 'TRX_BTC', 'DASH_BTC', 'NEO_BTC', 'QTUM_BTC',
                'XLM_BTC', 'ADA_BTC', 'AE_BTC', 'ALGO_BTC', 'ATOM_BTC', 'CELR_BTC',
                'BTT_BTC', 'IOST_BTC','ZEC_BTC',
                'LTC_ETH', 'BNB_ETH', 'ETC_ETH', 'BCHABC_ETH', 'EOS_ETH',
                'XRP_ETH', 'TRX_ETH', 'DASH_ETH', 'NEO_ETH', 'QTUM_ETH',
                'XLM_ETH', 'ADA_ETH', 'AE_ETH', 'ALGO_ETH',
                'IOST_ETH','ZEC_ETH'
               ]
}

REDIS_HOST = '127.0.0.1'
REDIS_PORT = 6379
CHANNEL = 'quote'
LPUSH_RECORD_MQ = 'wss_record_mq'
TIMER_PERIOD_LIST = [1, 3, 5, 60]

CTP_MD_SYMBOLS = ["rb2205", "rb2209", "fu2205", "fu2209", "hc2205", "hc2209",
                  "sp2205", "sp2209", "a2205", "a2209", "b2205", "b2209",
                  "c2205", "c2209", "cs2205", "cs2209", "i2205", "i2209",
                  "j2205", "j2209", "jd2205", "jd2209", "jm2205", "jm2209",
                  "l2205", "l2209", "m2205", "m2209", "p2205", "p2209",
                  "pp2205", "pp2209", "v2205", "v2209", "y2205", "y2209",
                  "eg2205", "eg2209", "rr2205", "eb2205", "eb2209",
                  "CF205", "CF209", "CY205", "CY209", "SR205", "SR209",
                  "TA205", "TA209", "OI205", "OI209", "MA205", "MA209",
                  "FG205", "FG209", "RM205", "RM209", "ZC205", "ZC209",
                  "SF205", "SF209", "SM205", "SM209", "AP205",
                  "CJ205", "CJ209", "UR205", "UR209", "SA205", "SA209",
                  "au2012", 'ag2012'
                  ]


CTP_TQ_SYMBOLS = ['rb999', 'fu999', 'hc999', 'sp999', 'a999', 'b999', 'm999',
                  'bu999', 'y999', 'c999', 'p999', 'j999', 'jm999', 'l999',
                  'v999', 'pp999', 'jd999', 'cs999', 'i999', 'eg999', 'rr999',
                  'eb999', 'CF999', 'CY999', 'SR999', 'TA999', 'OI999',
                  'MA999', 'FG999', 'RM999', 'ZC999', 'SF999', 'SM999',
                  'AP999', 'CJ999', 'UR999', 'SA999', 'IF999', 'IC999',
                  'IH999', 'sc999']


CTP_EX_DICT = {
    'SHFE': ['rb', 'fu', 'hc', 'sp', 'bu', 'au', 'ag'],
    'DCE': ['a', 'b', 'm', 'y', 'c', 'p', 'j', 'jm', 'l', 'v', 'pp', 'jd',
            'cs', 'i', 'eg', 'rr', 'eb'],
    'CZCE': ['CF', 'CY', 'SR', 'TA', 'OI', 'MA', 'FG', 'RM', 'ZC', 'SF',
             'SM', 'AP', 'CJ', 'UR', 'SA'],
    'CFFEX': ['IF', 'IC', 'IH'],
    'INE': ['sc']
}

TQ_CTP_DATES = {'begin_date': '2020.01', 'end_date': '2020.05', 'date': 'now'}
