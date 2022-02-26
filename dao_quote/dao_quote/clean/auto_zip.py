#coding=utf-8

import os
import time
import datetime


def auto_zip():
    # dir_path = 'docs/'
    dir_path = './'
    while True:
        time_now = datetime.datetime.now()
        date_now = str(time_now).split(' ')[0].replace('-', '')
        db_today = 'quote_{}.db'.format(date_now)
        date_prev = str(time_now + datetime.timedelta(-1)).split(' ')[0].replace('-', '')
        db_yesterday = 'quote_{}.db'.format(date_prev)
        dir_list = os.listdir(dir_path)
        for filename in dir_list:
            if (filename == db_yesterday):
                if (db_today in dir_list):
                    cmd = 'zip -r {}{}.zip {}{} && rm -f {}{}'.format(
                          dir_path, db_yesterday, dir_path, db_yesterday,
                          dir_path, db_yesterday)
                    print('processing {}'.format(cmd))
                    os.system(cmd)
                    print('process done')
        time.sleep(300)


def main():
    auto_zip()
