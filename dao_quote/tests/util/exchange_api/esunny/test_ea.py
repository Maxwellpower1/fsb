import time
import traceback
from ctypes import c_double, c_ulonglong

import pathmagic

from dao_quote.util.exchange_api.esunny import EsunnyApi as esapi


class EsQuote(esapi.ITapQuoteAPINotify):

    def OnRspLogin(self, errorCode, info):
        self.log('OnRspLogin errorCode: {}, info: '.format(errorCode, info))

    def OnAPIReady(self):
        self.log('API准备就绪')
        try:
            tac = esapi.TapAPIContract()
            # tac.Commodity.ExchangeNo = 'ZCE'
            # tac.Commodity.CommodityNo = 'CF'
            tac.Commodity.ExchangeNo = 'SHFE'
            tac.Commodity.CommodityNo = 'AU'
            # tac.Commodity.ExchangeNo = 'CFFEX'
            # tac.Commodity.CommodityNo = 'TF'
            tac.Commodity.CommodityType = 'F'
            tac.ContractNo1 = '2206'
            tac.CallOrPutFlag1 = 'N'
            tac.CallOrPutFlag2 = 'N'

            self.ctqa_z.SubscribeQuote(0, tac)
        except Exception as e:
            print(traceback.fromat_exc())


    def OnRspSubscribeQuote(self, sessionID, errorCode, isLast, info):
        self.log('OnRspSubscribeQuote: {} {}'.format(info.Contract.Commodity.CommodityNo, info.Contract.ContractNo1))

    def OnRtnQuote(self, info):
        QAskPrice = list((c_double * 20).from_address(int(info.QAskPrice)))
        QAskQty = list((c_ulonglong * 20).from_address(int(info.QAskQty)))
        QBidPrice = list((c_double * 20).from_address(int(info.QBidPrice)))
        QBidQty = list((c_ulonglong * 20).from_address(int(info.QBidQty)))

        tick_dict = {}
        tick_dict['ask'] = QAskPrice[0]
        tick_dict['a_v'] = QAskQty[0]
        tick_dict['bid'] = QBidPrice[0]
        tick_dict['b_v'] = QBidQty[0]

        tick_dict['last'] = info.QLastPrice
        tick_dict['open'] = info.QOpeningPrice
        tick_dict['high'] = info.QHighPrice
        tick_dict['low'] = info.QLowPrice
        tick_dict['pre_close'] = info.QPreClosingPrice
        tick_dict['vol'] = info.QTotalQty
        tick_dict['amt'] = info.QTotalTurnover
        tick_dict['inst'] = info.QPositionQty
        tick_dict['up_limit'] = info.QLimitUpPrice
        tick_dict['down_limit'] = info.QLimitDownPrice

        tick_dict['ask_2'] = QAskPrice[1]
        tick_dict['ask_3'] = QAskPrice[2]
        tick_dict['ask_4'] = QAskPrice[3]
        tick_dict['ask_5'] = QAskPrice[4]

        tick_dict['bid_2'] = QBidPrice[1]
        tick_dict['bid_3'] = QBidPrice[2]
        tick_dict['bid_4'] = QBidPrice[3]
        tick_dict['bid_5'] = QBidPrice[4]

        tick_dict['a_v_2'] = QAskQty[1]
        tick_dict['a_v_3'] = QAskQty[2]
        tick_dict['a_v_4'] = QAskQty[3]
        tick_dict['a_v_5'] = QAskQty[4]

        tick_dict['b_v_2'] = QBidQty[1]
        tick_dict['b_v_3'] = QBidQty[2]
        tick_dict['b_v_4'] = QBidQty[3]
        tick_dict['b_v_5'] = QBidQty[4]

        tick_dict['ts'] = info.DateTimeStamp
        self.log(tick_dict)

        msg = '{} {} {}'.format(info.Contract.Commodity.CommodityNo, info.Contract.ContractNo1, info.QLastPrice)
        self.log(msg)

    def log(self, msg):
        print('[*] {}'.format(msg))

    def main(self):
        taai = esapi.TapAPIApplicationInfo()
        taai.AuthCode = ''
        taai.KeyOperationLogPath = ''

        i = 0
        ctqa = esapi.CreateTapQuoteAPI(taai, i)

        taqla = esapi.TapAPIQuoteLoginAuth()
        taqla.ISModifyPassword = 'N'
        taqla.ISDDA = 'N'

        ctqa[0].SetHostAddress('61.163.243.173', 6161)
        ctqa[0].SetAPINotify(self)
        ctqa[0].Login(taqla)
        self.ctqa_z = ctqa[0]

        while True:
            time.sleep(3)


def main():
    eq = EsQuote()
    eq.main()


if __name__ == '__main__':
    main()
