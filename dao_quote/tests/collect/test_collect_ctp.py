#coding=utf-8

import pathmagic
from dao_quote.settings import config_x
from dao_quote.collect import collect_ctp
from dao_quote.settings import config_collect
from dao_quote.util.exchange_api.ctp import thostmduserapi as mdapi


def test_main():
    collect_ctp.main()


def testCFtdcMdSpi():
    subID = ['eg2005']
    md_address = config_x.CTP_MD_ADDRESS
    BrokerID = config_x.CTP_MD_BROKER_ID
    UserID = config_x.CTP_MD_USER_ID
    Password = config_x.CTP_MD_PASSWORD
    redis_host = config_collect.REDIS_HOST
    redis_port = config_collect.REDIS_PORT
    channel = config_collect.CHANNEL

    mduserapi = mdapi.CThostFtdcMdApi_CreateFtdcMdApi()
    mduserspi = collect_ctp.CFtdcMdSpi(mduserapi, subID, BrokerID, UserID, Password,
                redis_host, redis_port, channel)
    mduserapi.RegisterFront(md_address)
    mduserapi.RegisterSpi(mduserspi)
    mduserapi.Init()
    mduserapi.Join()


def main():
    # test_main()
    testCFtdcMdSpi()


if __name__ == '__main__':
    main()
