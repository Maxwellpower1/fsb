import re
import datetime
from contextlib import closing
from tqsdk import TqApi, TqSim
from tqsdk.tools import DataDownloader


def downloader(year, month, exchange, symbol, type_, days=''):
    symbol_, symbol_month = re.findall(r'[0-9]+|[a-zA-Z]+', symbol)
    if (symbol_month == '999'):
        symbol_download = 'KQ.m@{}.{}'.format(exchange, symbol_)
    else:
        symbol_download = '{}.{}'.format(exchange, symbol)

    if (days==0):
        if (month == 12):
            end_year = year + 1
            end_month = 1
        else:
            end_year = year
            end_month = month + 1
        begin_datetime = datetime.datetime(year, month, 1)
        end_datetime = datetime.datetime(end_year, end_month, 1)
    else:
        begin_datetime = datetime.datetime.now()
        year = begin_datetime.year
        month = begin_datetime.month
        day = begin_datetime.day
        end_datetime = datetime.datetime(year, month, day)
        begin_datetime = end_datetime - datetime.timedelta(days=days)
        end_year = end_datetime.year
        end_month = end_datetime.month

    begin_date = '{}{:02d}'.format(year, month)
    end_date = '{}{:02d}'.format(end_year, end_month)
    print('[*] downing from {} to {}, {}.{}'.format(begin_date, end_date, exchange, symbol))

    api = TqApi(TqSim())
    download_tasks = {}

    if (type_ == 'tick'):
        filename = 'docs/{}_{}_tick.csv'.format(begin_date, symbol)
        download_tasks["tick"] = DataDownloader(api, symbol_list=[symbol_download], dur_sec=0,
                            start_dt=begin_datetime, end_dt=end_datetime, csv_file_name=filename)
    elif (type_ == 'bar'):
        filename = 'docs/{}_{}_bar.csv'.format(begin_date, symbol)
        download_tasks["min"] = DataDownloader(api, symbol_list=[symbol_download], dur_sec=60,
                            start_dt=begin_datetime, end_dt=end_datetime, csv_file_name=filename)

    with closing(api):
        while not all([v.is_finished() for v in download_tasks.values()]):
            api.wait_update()
            print("progress: ", { k:("%.2f%%" % v.get_progress()) for k,v in download_tasks.items() })
