# !/usr/bin/env python
# coding=utf-8

import time
import hashlib
import sqlite3
import optparse


def create_table_bar(db_name, key_name):
    conn = sqlite3.connect(db_name, timeout=21)
    c = conn.cursor()
    c.execute('''CREATE TABLE "{}" (
                  TIMESTAMP   INTEGER PRIMARY KEY NOT NULL,
                  OPEN        FLOAT    NOT NULL,
                  HIGH        FLOAT    NOT NULL,
                  LOW         FLOAT    NOT NULL,
                  CLOSE       FLOAT    NOT NULL,
                  VOLUME      FLOAT    NOT NULL,
                  VOLUME_COIN FLOAT    NOT NULL
                  );'''.format(key_name))
    conn.commit()
    conn.close()


def save_table_bar(db_name, key_name, data):
    conn = sqlite3.connect(db_name, timeout=21)
    c = conn.cursor()
    # data.reverse()
    for i in data:
        if (len(i) < 7):
            volume_coin = 0
        else:
            volume_coin = i[6]
        try:
            c.execute(('REPLACE INTO "{}" (TIMESTAMP,OPEN,HIGH,LOW,'
                       'CLOSE,VOLUME,VOLUME_COIN) VALUES '
                       '({},{},{},{},{},{},{})').format(
                       key_name, i[0], i[1], i[2], i[3], i[4], i[5],
                       volume_coin))
        except Exception as e:
            if 'UNIQUE constraint' in str(e):
                # break
                pass
            else:
                raise
    conn.commit()
    conn.close()


def save_bar(db_name, key_name, data):
    table_name = key_name
    try:
        save_table_bar(db_name, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                create_table_bar(db_name, table_name)
                save_table_bar(db_name, table_name, data)
            except Exception as e:
                pass
        else:
            print(e)


def get_backtest_kline_db(conn, key_name, begin_timestamp, end_timestamp):
    c = conn.cursor()
    s = c.execute(('SELECT * FROM "{}" WHERE {}<=timestamp and '
                   'timestamp<={} ORDER BY timestamp').format(
                   key_name, begin_timestamp, end_timestamp))
    # the result kline timestamp is ms
    data = []
    for k in s:
        data.append([k[0], k[1], k[2], k[3], k[4], k[5], k[6]])
    return data


def get_backtest_kline_db_all(conn, key_name):
    c = conn.cursor()
    s = c.execute(('SELECT * FROM "{}" ORDER BY timestamp').format(key_name))
    # the result kline timestamp is ms
    data = []
    for k in s:
        data.append([k[0], k[1], k[2], k[3], k[4], k[5], k[6]])
    return data


def get_db(begin_timestamp, end_timestamp):
    conn = sqlite3.connect('dao_quote.db', timeout=21)
    db_name = 'temp_quote.db'
    c = conn.cursor()
    s = c.execute(('''SELECT name FROM sqlite_master WHERE type='table' and name like '%kline%' ORDER BY name;'''))
    for i in s:
        key_name = i[0]
        data = get_backtest_kline_db(conn, key_name, begin_timestamp, end_timestamp)
        save_bar(db_name, key_name, data)
    BUF_SIZE = 65536
    sha256 = hashlib.sha256()
    with open(db_name, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)
    shasum = sha256.hexdigest()
    return db_name, shasum


def set_db(param):
    conn = sqlite3.connect('temp_quote.db', timeout=21)
    db_name = 'dao_quote.db'
    c = conn.cursor()
    s = c.execute(('''SELECT name FROM sqlite_master WHERE type='table' and name like '%kline%' ORDER BY name;'''))
    for i in s:
        key_name = i[0]
        print('setting: {}'.format(key_name))
        data = get_backtest_kline_db_all(conn, key_name)
        save_bar(db_name, key_name, data)
