# !/usr/bin/env python
# coding=utf-8

import time
import json
import redis
import datetime
import pathmagic

from dao_quote.util.convert import convert
from dao_quote.compute.depth_local import ComputeDepth


def test_compute_depth():
    setting_dict = {}
    setting_dict['exchange'] = 'okexf'
    setting_dict['symbol'] = 'btc_usd-quarter'
    setting_dict['depth'] = 10
    compute_depth = ComputeDepth(setting_dict)
    compute_depth.main()


def main():
    test_compute_depth()


if __name__ == '__main__':
    main()
