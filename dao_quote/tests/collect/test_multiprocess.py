import sys
import time
import datetime
import traceback

from multiprocessing import Process


def esunny_main():
    limit = 5
    while True:
        time.sleep(1)
        print('[*] limit: {}'.format(limit))
        limit -= 1
        if limit < 0:
            print('sys.exit')
            sys.exit(0)


def process_monitor(process_dict_list):
    while True:
        for process_dict in process_dict_list:
            process = process_dict['process']
            if (process.is_alive() is False):
                name = process_dict['name']
                if (name == 'esunny_main'):
                    p5 = Process(target=esunny_main, args=())
                    p5.start()
                    process_dict['process'] = p5
                    process_dict['pid'] = p5.pid
                    print('{}, name: {}, new_pid: {}'.format(
                          datetime.datetime.now(), name, p5.pid))
        time.sleep(5)


def start_esunny():
    try:
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
        print(traceback.format_exc())


def main():
    start_esunny()


if __name__ == '__main__':
    main()
