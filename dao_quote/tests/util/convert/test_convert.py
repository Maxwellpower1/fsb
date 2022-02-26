# coding=utf-8

import unittest
import pathmagic

from dao_quote.util.convert import convert


class testConvert(unittest.TestCase):

    def test_combine_lines(self):
        klines = [
            [111, 2, 3, 1, 2, 1],
            [222, 2, 3.1, 0.7, 1.9, 1.7],
            [333, 1.9, 2.7, 0.9, 2.1, 0.9],
            [444, 2.1, 2.9, 1, 2, 1.1],
        ]
        klines = convert.combine_lines(klines, 2)
        rst = [
            [111, 2, 3.1, 0.7, 1.9, 2.7],
            [333, 1.9, 2.9, 0.9, 2, 2]
        ]
        self.assertTrue(klines, rst)

    def test_shift_time(self):
        timestamp = 1567267200
        time_date = convert.shift_time(timestamp)
        self.assertEqual(time_date, '2019-09-01 00:00:00')

    def test_to_timestamp(self):
        time_date = '2019-09-01 00:00:00'
        timestamp = convert.to_timestamp(time_date)
        self.assertEqual(timestamp, '1567267200')

    def test_to_timestamp_es(self):
        time_date = '2021-11-16 13:51:53.309'
        timestamp = convert.to_timestamp_es(time_date)
        self.assertEqual(timestamp, 1637041913309)


def main():
    unittest.main()


if __name__ == '__main__':
    main()
