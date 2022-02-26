#!/usr/bin/env python
# coding=utf-8

from gevent import monkey; monkey.patch_all()
import os
import sys
import time
import datetime
import optparse
from multiprocessing import Process

from dao_quote.rpc import rpc_server
from dao_quote.clean import (auto_zip, resave)
from dao_quote.compute.compute import main as compute_main
from dao_quote.compute.record import main as record_main
from dao_quote.util.quote_save import fix_save


def async_start():
    try:
        from dao_quote.collect import collect_async
        collect_async.async_start()
    except (KeyboardInterrupt):
        filename = os.path.basename(__file__)
        print(' Stop {} !'.format(filename))


def gevent_start():
    try:
        from dao_quote.collect import collect_gevent
        collect_gevent.gevent_start()
    except (KeyboardInterrupt):
        filename = os.path.basename(__file__)
        print(' Stop {} !'.format(filename))


def start_compute():
    try:
        p2 = Process(target=compute_main, args=())
        p2.start()
        process_dict_list = [
            {'name': 'compute_main', 'process': p2, 'pid': p2.pid}
        ]
        print('compute: {}'.format(p2.pid))
        process_monitor(process_dict_list)
    except (KeyboardInterrupt):
        filename = 'compute'
        print(' Stop {} !'.format(filename))


def start_record():
    try:
        p3 = Process(target=record_main, args=())
        p3.start()
        process_dict_list = [
            {'name': 'record_main', 'process': p3, 'pid': p3.pid}
        ]
        print('record: {}'.format(p3.pid))
        process_monitor(process_dict_list)
    except Exception as e:
        filename = 'record'
        print(' Stop {} !'.format(filename))


def process_monitor(process_dict_list):
    while True:
        for process_dict in process_dict_list:
            process = process_dict['process']
            if (process.is_alive() is False):
                name = process_dict['name']
                if (name == 'compute_main'):
                    p2 = Process(target=compute_main, args=())
                    p2.start()
                    process_dict['process'] = p2
                    process_dict['pid'] = p2.pid
                    print('{}, name: {}, new_pid: {}'.format(
                          datetime.datetime.now(), name, p2.pid))
                elif (name == 'record_main'):
                    p3 = Process(target=record_main, args=())
                    p3.start()
                    process_dict['process'] = p3
                    process_dict['pid'] = p3.pid
                    print('{}, name: {}, new_pid: {}'.format(
                          datetime.datetime.now(), name, p3.pid))
                elif (name == 'esunny_main'):
                    from dao_quote.collect.collect_esunny import main as esunny_main
                    p5 = Process(target=esunny_main, args=())
                    p5.start()
                    process_dict['process'] = p5
                    process_dict['pid'] = p5.pid
                    print('{}, name: {}, new_pid: {}'.format(
                          datetime.datetime.now(), name, p5.pid))
        time.sleep(5)


def fix_bars():
    exchange = 'okexf'
    symbol = 'eos_usd-quarter'
    period = '3min'
    rst = fix_save.fix_bars(exchange, symbol, period)
    print(exchange, symbol, period, rst)
    period = '15min'
    rst = fix_save.fix_bars(exchange, symbol, period)
    print(exchange, symbol, period, rst)
    period = '30min'
    rst = fix_save.fix_bars(exchange, symbol, period)
    print(exchange, symbol, period, rst)
    symbol = 'btc_usd-quarter'
    period = '30min'
    rst = fix_save.fix_bars(exchange, symbol, period)
    print(exchange, symbol, period, rst)
    exchange = 'huobif'
    symbol = 'btc_usd-quarter'
    period = '15min'
    rst = fix_save.fix_bars(exchange, symbol, period)
    print(exchange, symbol, period, rst)
    period = '30min'
    rst = fix_save.fix_bars(exchange, symbol, period)
    print(exchange, symbol, period, rst)
    period = '1hour'
    rst = fix_save.fix_bars(exchange, symbol, period)
    print(exchange, symbol, period, rst)


def collect_save_bar():
    try:
        from dao_quote.collect import collect
        collect.collect_save_bar()
    except (KeyboardInterrupt):
        filename = os.path.basename(__file__)
        print(' Stop {} !'.format(filename))


def start_timer():
    try:
        from dao_quote.timer import timer
        timer.main()
    except Exception as e:
        print(' Stop {} !'.format(timer))


def start_ctp():
    try:
        from dao_quote.collect import collect_ctp
        collect_ctp.main()
    except (KeyboardInterrupt):
        filename = os.path.basename(__file__)
        print(' Stop {} !'.format(filename))


def start_esunny():
    try:
        from dao_quote.collect.collect_esunny import main as esunny_main
        p5 = Process(target=esunny_main, args=())
        p5.start()
        process_dict_list = [
            {'name': 'esunny_main', 'process': p5, 'pid': p5.pid}
        ]
        print('esunny: {}'.format(p5.pid))
        process_monitor(process_dict_list)
    except Exception as e:
        filename = 'esunny'
        print(' Stop {} !'.format(filename))


def start_tushare():
    try:
        from dao_quote.collect.collect_tushare import main as tushare_main
        p5 = Process(target=tushare_main, args=())
        p5.start()
    except Exception as e:
        filename = 'tushare_main'
        print(' Stop {} !'.format(filename))


def start_tqq():
    try:
        from dao_quote.collect import collect_tq_ctp
        collect_tq_ctp.main()
    except (KeyboardInterrupt):
        filename = os.path.basename(__file__)
        print(' Stop {} !'.format(filename))


def start_wss():
    try:
        from dao_quote.collect import collect_wss
        collect_wss.main()
    except (KeyboardInterrupt):
        print(' Stop {} !'.format('collect_wss'))


def start_vision(key_name):
    try:
        from dao_quote.vision.order_flow import OrderFlow
        of = OrderFlow()
        of.main(key_name)
    except (KeyboardInterrupt):
        print(' Stop {} !'.format('order_flow'))


def start_rpc():
    rpc_server.run()


def print_info():
    filename = os.path.basename(__file__)
    print('need set param, such as:')
    print('python {} -t a'.format(filename))
    print('python {} -t g'.format(filename))
    print('python {} -t c'.format(filename))
    print('python {} -t r'.format(filename))
    print('python {} -t f'.format(filename))
    print('python {} -t b'.format(filename))
    print('python {} -t t'.format(filename))
    print('python {} -t ctp'.format(filename))
    print('python {} -t esunny'.format(filename))
    print('python {} -t wss'.format(filename))
    print('python {} -t rpc'.format(filename))
    print('python {} -t resave -d db_name'.format(filename))
    print('python {} -t index'.format(filename))
    print('python {} -t zip'.format(filename))
    print('python {} -t vision -k key_name'.format(filename))


def main():
    parser = optparse.OptionParser()
    parser.add_option("-t", "--type", dest="run_type",
                      help="f[fix_bars]/s[save]/c[combine]")
    parser.add_option("-d", "--db_name", dest="db_name",
                      help="db_name")
    parser.add_option("-k", "--key_name", dest="key_name",
                      help="ctp_FG105_trade")
    (options, args) = parser.parse_args()
    if options.run_type != None:
        param = options.run_type

        if (param == 'g'):
            gevent_start()
        elif (param == 'a'):
            async_start()
        elif (param == 'c'):
            start_compute()
        elif (param == 'r'):
            start_record()
        elif (param == 'f'):
            try:
                fix_bars()
            except (KeyboardInterrupt):
                filename = os.path.basename(__file__)
                print(' Stop {} !'.format(filename))
        elif (param == 'b'):
            collect_save_bar()
        elif (param == 't'):
            start_timer()
        elif (param == 'ctp'):
            start_ctp()
        elif (param == 'esunny'):
            start_esunny()
        elif (param == 'tushare'):
            start_tushare()
        elif (param == 'tqq'):
            start_tqq()
        elif (param == 'wss'):
            start_wss()
        elif (param == 'rpc'):
            start_rpc()
        elif (param == 'resave'):
            try:
                db_name = options.db_name
                resave.resave(db_name)
            except (KeyboardInterrupt):
                filename = os.path.basename(__file__)
                print(' Stop {} !'.format(filename))
        elif (param == 'tqctp'):
            try:
                db_name = options.db_name
                from dao_quote.collect import collect_tq_ctp
                collect_tq_ctp.download(db_name)
            except (KeyboardInterrupt):
                filename = os.path.basename(__file__)
                print(' Stop {} !'.format(filename))
        elif (param == 'tqctpbar'):
            try:
                db_name = options.db_name
                from dao_quote.collect import collect_tq_ctp
                type_list = ['bar']
                collect_tq_ctp.download(db_name, type_list=type_list)
            except (KeyboardInterrupt):
                filename = os.path.basename(__file__)
                print(' Stop {} !'.format(filename))
        elif (param == 'index'):
            try:
                resave.create_index()
            except (KeyboardInterrupt):
                filename = os.path.basename(__file__)
                print(' Stop {} !'.format(filename))
        elif (param == 'zip'):
            try:
                auto_zip.main()
            except (KeyboardInterrupt):
                filename = os.path.basename(__file__)
                print(' Stop {} !'.format(filename))
        elif (param == 'vision'):
            key_name = options.key_name
            start_vision(key_name)
        else:
            print_info()
            sys.exit(0)
    else:
        print_info()
        sys.exit(0)


if __name__ == '__main__':
    main()
