# coding=utf-8

import time
import asyncio
import sqlite3
import aiosqlite


def get_db_name(timestamp):
    format = '%Y%m%d'
    value = time.localtime(timestamp)
    date = time.strftime(format, value)
    db_name = 'quote_{}.db'.format(date)
    return db_name


# create table segment
def create_table_tick(db_name, table_name):
    conn = sqlite3.connect(db_name, timeout=21)
    c = conn.cursor()
    c.execute('''CREATE TABLE "{}" (
                  ID        INTEGER PRIMARY KEY NOT NULL,
                  TIMESTAMP FLOAT    NOT NULL,
                  ASK       FLOAT    NOT NULL,
                  BID       FLOAT    NOT NULL,
                  LAST      FLOAT    NOT NULL,
                  HIGH      FLOAT    NOT NULL,
                  LOW       FLOAT    NOT NULL,
                  VOL       FLOAT    NOT NULL
                  );'''.format(table_name))
    conn.commit()
    conn.close()


def create_table_kline(db_name, key_name):
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


def create_table_depth(db_name, table_name):
    conn = sqlite3.connect(db_name, timeout=21)
    c = conn.cursor()
    c.execute('''CREATE TABLE "{}" (
                  ID        INTEGER PRIMARY KEY NOT NULL,
                  TIMESTAMP FLOAT    NOT NULL,
                  ASKS      TEXT     NOT NULL,
                  BIDS      TEXT     NOT NULL
                  );'''.format(table_name))
    conn.commit()
    conn.close()


def wss_create_table_tick(conn, table_name):
    c = conn.cursor()
    c.execute('''CREATE TABLE "{}" (
                  ID        INTEGER PRIMARY KEY NOT NULL,
                  TIMESTAMP FLOAT    NOT NULL,
                  ASK       FLOAT    NOT NULL,
                  BID       FLOAT    NOT NULL,
                  LAST      FLOAT    NOT NULL,
                  HIGH      FLOAT    NOT NULL,
                  LOW       FLOAT    NOT NULL,
                  VOL       FLOAT    NOT NULL
                  );'''.format(table_name))
    conn.commit()


def wss_create_table_bar(conn, key_name):
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


def wss_create_table_depth(conn, table_name):
    c = conn.cursor()
    c.execute('''CREATE TABLE "{}" (
                  ID        INTEGER PRIMARY KEY NOT NULL,
                  TIMESTAMP FLOAT    NOT NULL,
                  ASKS      TEXT     NOT NULL,
                  BIDS      TEXT     NOT NULL
                  );'''.format(table_name))
    conn.commit()


async def async_create_table_tick(db_name, table_name):
    async with aiosqlite.connect(db_name, timeout=21) as db:
        await db.execute('''CREATE TABLE "{}" (
                         ID        INTEGER PRIMARY KEY NOT NULL,
                         TIMESTAMP FLOAT    NOT NULL,
                         ASK       FLOAT    NOT NULL,
                         BID       FLOAT    NOT NULL,
                         LAST      FLOAT    NOT NULL,
                         HIGH      FLOAT    NOT NULL,
                         LOW       FLOAT    NOT NULL,
                         VOL       FLOAT    NOT NULL
                         );'''.format(table_name))
        await db.commit()


async def async_create_table_kline(db_name, table_name):
    async with aiosqlite.connect(db_name, timeout=21) as db:
        await db.execute('''CREATE TABLE "{}" (
                         TIMESTAMP   INTEGER PRIMARY KEY NOT NULL,
                         OPEN        FLOAT    NOT NULL,
                         HIGH        FLOAT    NOT NULL,
                         LOW         FLOAT    NOT NULL,
                         CLOSE       FLOAT    NOT NULL,
                         VOLUME      FLOAT    NOT NULL,
                         VOLUME_COIN FLOAT    NOT NULL
                         );'''.format(table_name))
        await db.commit()


async def async_create_table_depth(db_name, table_name):
    async with aiosqlite.connect(db_name, timeout=21) as db:
        await db.execute('''CREATE TABLE "{}" (
                         ID        INTEGER PRIMARY KEY NOT NULL,
                         TIMESTAMP FLOAT    NOT NULL,
                         ASKS      TEXT     NOT NULL,
                         BIDS      TEXT     NOT NULL
                         );'''.format(table_name))
        await db.commit()


# save table data segment
async def async_save_table_tick(db_name, table_name, data):
    async with aiosqlite.connect(db_name, timeout=21) as db:
        await db.execute(('INSERT INTO "{}" (TIMESTAMP,ASK,BID,LAST,HIGH,LOW,VOL) '
                          'VALUES ({},{},{},{},{},{},{})').format(
                          table_name, data['ts'], data['ask'], data['bid'],
                          data['last'], data['high'], data['low'], data['vol']))
        await db.commit()


async def async_save_tick(db_name, key_name, data):
    table_name = key_name
    try:
        await async_save_table_tick(db_name, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                await async_create_table_tick(db_name, table_name)
                await async_save_table_tick(db_name, table_name, data)
            except Exception as e:
                print(e)
        else:
            print(e)


async def async_save_table_kline(db_name, table_name, data):
    async with aiosqlite.connect(db_name, timeout=21) as db:
        # data = data[-60:-1]
        # data.reverse()
        for i in data:
            if (len(i) < 7):
                volume_coin = 0
            else:
                volume_coin = i[6]
            try:
                await db.execute(('REPLACE INTO "{}" (TIMESTAMP,OPEN,HIGH,LOW,'
                                  'CLOSE,VOLUME,VOLUME_COIN) VALUES '
                                  '({},{},{},{},{},{},{})').format(
                                  table_name, i[0], i[1], i[2], i[3],
                                  i[4], i[5], volume_coin))
            except Exception as e:
                if 'UNIQUE constraint' in str(e):
                    # break
                    pass
                else:
                    raise
        await db.commit()


async def async_save_kline(db_name, key_name, data):
    table_name = key_name
    try:
        await async_save_table_kline(db_name, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                await async_create_table_kline(db_name, table_name)
                await async_save_table_kline(db_name, table_name, data)
            except Exception as e:
                pass
        else:
            print(e)


async def async_save_table_depth(db_name, table_name, data):
    async with aiosqlite.connect(db_name, timeout=21) as db:
        await db.execute(('INSERT INTO "{}" (TIMESTAMP,ASKS,BIDS) '
                          'VALUES ({},"{}","{}")').format(
                          table_name, data['ts'], data['asks'], data['bids']))
        await db.commit()


async def async_save_depth(db_name, key_name, data):
    table_name = key_name
    try:
        await async_save_table_depth(db_name, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                await async_create_table_depth(db_name, table_name)
                await async_save_table_depth(db_name, table_name, data)
            except Exception as e:
                pass
        else:
            print(e)


def save_table_tick(db_name, table_name, data):
    conn = sqlite3.connect(db_name, timeout=21)
    c = conn.cursor()
    c.execute(('INSERT INTO "{}" (TIMESTAMP,ASK,BID,LAST,HIGH,LOW,VOL) '
               'VALUES ({},{},{},{},{},{},{})').format(
               table_name, data['ts'], data['ask'], data['bid'],
               data['last'], data['high'], data['low'], data['vol']))
    conn.commit()
    conn.close()


def save_tick(db_name, key_name, data):
    table_name = key_name
    try:
        save_table_tick(db_name, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            create_table_tick(db_name, table_name)
            save_table_tick(db_name, table_name, data)
        else:
            print(e)


def save_table_depth(db_name, table_name, data):
    conn = sqlite3.connect(db_name, timeout=21)
    c = conn.cursor()
    c.execute(('INSERT INTO "{}" (TIMESTAMP,ASKS,BIDS) '
               'VALUES ({},"{}","{}")').format(
               table_name, data['ts'], data['asks'], data['bids']))
    conn.commit()
    conn.close()


def save_depth(db_name, key_name, data):
    table_name = key_name
    try:
        save_table_depth(db_name, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                create_table_depth(db_name, table_name)
                save_table_depth(db_name, table_name, data)
            except Exception as e:
                pass
        else:
            print(e)


def save_table_kline(db_name, key_name, data):
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


def save_kline(db_name, key_name, data):
    table_name = key_name
    try:
        save_table_kline(db_name, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                create_table_kline(db_name, table_name)
                save_table_kline(db_name, table_name, data)
            except Exception as e:
                pass
        else:
            print(e)


def wss_save_table_tick(conn, table_name, timestamp, data):
    c = conn.cursor()
    c.execute(('INSERT INTO "{}" (TIMESTAMP,ASK,BID,LAST,HIGH,LOW,VOL) '
               'VALUES ({},{},{},{},{},{},{})').format(
               table_name, timestamp, data['ask'], data['bid'],
               data['last'], data['high'], data['low'], data['vol']))
    conn.commit()


def wss_save_tick(conn, key_name, timestamp, data):
    table_name = key_name
    try:
        wss_save_table_tick(conn, table_name, timestamp, data)
    except Exception as e:
        if ('no such table' in str(e)):
            wss_create_table_tick(conn, table_name)
            wss_save_table_tick(conn, table_name, timestamp, data)
        else:
            print(e)


def wss_save_table_depth(conn, table_name, timestamp, data):
    c = conn.cursor()
    c.execute(('INSERT INTO "{}" (TIMESTAMP,ASKS,BIDS) '
               'VALUES ({},"{}","{}")').format(
               table_name, timestamp, data['asks'], data['bids']))
    conn.commit()


def wss_save_depth(conn, key_name, timestamp, data):
    table_name = key_name
    try:
        wss_save_table_depth(conn, table_name, timestamp, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                wss_create_table_depth(conn, table_name)
                wss_save_table_depth(conn, table_name, timestamp, data)
            except Exception as e:
                pass
        else:
            print(e)


def wss_save_table_bar(conn, key_name, data):
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


def wss_save_bar(conn, key_name, data):
    table_name = key_name
    try:
        wss_save_table_bar(conn, table_name, data)
    except Exception as e:
        if ('no such table' in str(e)):
            try:
                wss_create_table_bar(conn, table_name)
                wss_save_table_bar(conn, table_name, data)
            except Exception as e:
                pass
        else:
            print(e)


def main():
    pass


if __name__ == '__main__':
    main()
