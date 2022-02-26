# coding=utf-8

import os
import time

from multiprocessing import Process
from dao_quote.settings import config
from dao_quote.util.verify.sms import send_sms


def start_wss():
    COLLECT_DICT = config.COLLECT_DICT
    exchange_dict = COLLECT_DICT['wss_exchange_dict']
    type_list = COLLECT_DICT['wss_type_list']

    process_dict_list = []
    for exchange in exchange_dict:
        symbol_list = exchange_dict[exchange]
        if (exchange == 'okexf'):
            from dao_quote.util.exchange_api.okexf import wss_okexf_v5 as wss_okexf
            # wss_okexf.main(symbol_list, type_list)
            p1 = Process(target=wss_okexf.main, args=(symbol_list, type_list,))
            p1.start()
            process_dict = {'name': 'wss_okexf', 'process': p1, 'pid': p1.pid}
            process_dict_list.append(process_dict)
            pass
        elif (exchange == 'okex'):
            from dao_quote.util.exchange_api.okex import wss_okex_v5 as wss_okex
            # wss_okex.main(symbol_list, type_list)
            p2 = Process(target=wss_okex.main, args=(symbol_list, type_list,))
            p2.start()
            process_dict = {'name': 'wss_okex', 'process': p2, 'pid': p2.pid}
            process_dict_list.append(process_dict)
            pass
        elif (exchange == 'huobi'):
            from dao_quote.util.exchange_api.huobi import wss_huobi
            # wss_huobi.main(symbol_list, type_list)
            p3 = Process(target=wss_huobi.main, args=(symbol_list, type_list,))
            p3.start()
            process_dict = {'name': 'wss_huobi', 'process': p3, 'pid': p3.pid}
            process_dict_list.append(process_dict)
            pass
        elif (exchange == 'huobif'):
            from dao_quote.util.exchange_api.huobif import wss_huobif
            # wss_huobif.main(symbol_list, type_list)
            p4 = Process(target=wss_huobif.main, args=(symbol_list, type_list,))
            p4.start()
            process_dict = {'name': 'wss_huobif', 'process': p4, 'pid': p4.pid}
            process_dict_list.append(process_dict)
            pass
        elif (exchange == 'binance'):
            from dao_quote.util.exchange_api.binance import wss_binance
            # wss_binance.main(symbol_list, type_list)
            p5 = Process(target=wss_binance.main, args=(symbol_list, type_list,))
            p5.start()
            process_dict = {'name': 'wss_binance', 'process': p5, 'pid': p5.pid}
            process_dict_list.append(process_dict)
            pass
        else:
            pass

    restart_counter = 0
    sms_send = 0
    while True:
        for process_dict in process_dict_list:
            process = process_dict['process']
            if (process.is_alive() is False):
                # restart_counter +=1
                # if (restart_counter > 10):
                #     # sms alert
                #     if (sms_send == 0):
                #         nationCode = config.PHONE_ZONE
                #         phoneNumber = config.ADMIN_PHONE
                #         code = '111111'
                #         rst = send_sms.send_vcode(nationCode, phoneNumber, code)
                #         sms_send = 1
                #         print(rst)
                #     time.sleep(60*10)
                name = process_dict['name']
                pid = process_dict['pid']
                os.system('kill {}'.format(pid))
                print('{} restart {}'.format(name, '*'*100))
                if (name == 'wss_okexf'):
                    symbol_list = exchange_dict['okexf']
                    from dao_quote.util.exchange_api.okexf import wss_okexf
                    p1 = Process(target=wss_okexf.main, args=(symbol_list, type_list,))
                    p1.start()
                    process_dict['process'] = p1
                    process_dict['pid'] = p1.pid
                    print('name: {}, new_pid: {}'.format(
                          name, p1.pid))
                elif (name == 'wss_okex'):
                    symbol_list = exchange_dict['okex']
                    from dao_quote.util.exchange_api.okex import wss_okex
                    p2 = Process(target=wss_okex.main, args=(symbol_list, type_list,))
                    p2.start()
                    process_dict['process'] = p2
                    process_dict['pid'] = p2.pid
                    print('name: {}, new_pid: {}'.format(
                          name, p2.pid))
                elif (name == 'wss_huobi'):
                    symbol_list = exchange_dict['huobi']
                    from dao_quote.util.exchange_api.huobi import wss_huobi
                    p3 = Process(target=wss_huobi.main, args=(symbol_list, type_list,))
                    p3.start()
                    process_dict['process'] = p3
                    process_dict['pid'] = p3.pid
                    print('name: {}, new_pid: {}'.format(
                          name, p3.pid))
                elif (name == 'wss_huobif'):
                    symbol_list = exchange_dict['huobif']
                    from dao_quote.util.exchange_api.huobif import wss_huobif
                    p4 = Process(target=wss_huobif.main, args=(symbol_list, type_list,))
                    p4.start()
                    process_dict['process'] = p4
                    process_dict['pid'] = p4.pid
                    print('name: {}, new_pid: {}'.format(
                          name, p4.pid))
                elif (name == 'wss_binance'):
                    symbol_list = exchange_dict['binance']
                    from dao_quote.util.exchange_api.binance import wss_binance
                    p5 = Process(target=wss_binance.main, args=(symbol_list, type_list,))
                    p5.start()
                    process_dict['process'] = p5
                    process_dict['pid'] = p5.pid
                    print('name: {}, new_pid: {}'.format(
                          name, p5.pid))
                else:
                    pass
            else:
                pass
        time.sleep(0.5)


def main():
    start_wss()
