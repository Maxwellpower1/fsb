# coding=utf-8

import time
import random

from dao_execute.exchange_api.ctp import thosttraderapi as api


class CTradeSpi(api.CThostFtdcTraderSpi):
	tapi = ''
	def __init__(self, tapi, broker_id, api_key, secret_key, ctp_app_id, ctp_auth_code):
		api.CThostFtdcTraderSpi.__init__(self)

		self.connected = False
		self.tapi = tapi

		self.broker_id = broker_id
		self.api_key = api_key
		self.secret_key = secret_key
		self.ctp_app_id = ctp_app_id
		self.ctp_auth_code = ctp_auth_code

	def OnFrontConnected(self) -> "void":
		print ("OnFrontConnected")

	def ReqAuthenticate(self):
		authfield = api.CThostFtdcReqAuthenticateField();
		authfield.BrokerID = self.broker_id
		authfield.UserID = self.api_key
		authfield.AppID = self.ctp_app_id
		authfield.AuthCode = self.ctp_auth_code
		self.tapi.ReqAuthenticate(authfield, 0)
		print ("send ReqAuthenticate ok")

	def OnRspAuthenticate(self, pRspAuthenticateField: 'CThostFtdcRspAuthenticateField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		print("BrokerID=", pRspAuthenticateField.BrokerID)
		print("UserID=", pRspAuthenticateField.UserID)
		print("AppID=", pRspAuthenticateField.AppID)
		print("AppType=", pRspAuthenticateField.AppType)
		print("ErrorID=", pRspInfo.ErrorID)
		print("ErrorMsg=", pRspInfo.ErrorMsg)
		# if not pRspInfo.ErrorID :
		# 	loginfield = api.CThostFtdcReqUserLoginField()
		# 	loginfield.BrokerID = self.broker_id
		# 	loginfield.UserID = self.api_key
		# 	loginfield.Password = self.secret_key
		# 	loginfield.UserProductInfo = "python dll"
		# 	self.tapi.ReqUserLogin(loginfield, 0)
		# 	print("send login ok")

	def ReqUserLogin(self):
		loginfield = api.CThostFtdcReqUserLoginField()
		loginfield.BrokerID = self.broker_id
		loginfield.UserID = self.api_key
		loginfield.Password = self.secret_key
		loginfield.UserProductInfo = "python dll"
		self.tapi.ReqUserLogin(loginfield, 0)
		print("send login ok")

	def OnRspUserLogin(self, pRspUserLogin: 'CThostFtdcRspUserLoginField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		print("OnRspUserLogin")
		print("TradingDay=", pRspUserLogin.TradingDay)
		print("SessionID=", pRspUserLogin.SessionID)
		print("ErrorID=", pRspInfo.ErrorID)
		print("ErrorMsg=", pRspInfo.ErrorMsg)
		self.SessionID = pRspUserLogin.SessionID
		self.FrontID = pRspUserLogin.FrontID
		self.MaxOrderRef = int(pRspUserLogin.MaxOrderRef)

		qryinfofield = api.CThostFtdcQrySettlementInfoField()
		qryinfofield.BrokerID = self.broker_id
		qryinfofield.InvestorID = self.api_key
		qryinfofield.TradingDay = pRspUserLogin.TradingDay
		self.tapi.ReqQrySettlementInfo(qryinfofield,0)
		print ("send ReqQrySettlementInfo ok")

	def OnRspQrySettlementInfo(self, pSettlementInfo: 'CThostFtdcSettlementInfoField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		print("OnRspQrySettlementInfo")
		if  pSettlementInfo is not None :
			print("content:", pSettlementInfo.Content)
		else :
			print("content null")
		pSettlementInfoConfirm = api.CThostFtdcSettlementInfoConfirmField()
		pSettlementInfoConfirm.BrokerID = self.broker_id
		pSettlementInfoConfirm.InvestorID = self.api_key
		self.tapi.ReqSettlementInfoConfirm(pSettlementInfoConfirm, 0)
		print("send ReqSettlementInfoConfirm ok")

	def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm: 'CThostFtdcSettlementInfoConfirmField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		print("OnRspSettlementInfoConfirm")
		print("ErrorID=", pRspInfo.ErrorID)
		print("ErrorMsg=", pRspInfo.ErrorMsg)
		# self.connected = True
		# ReqorderfieldInsert(self.tapi)
		# print("send ReqorderfieldInsert ok")

	def OnRtnOrder(self, pOrder: 'CThostFtdcOrderField') -> "void":
		print("OnRtnOrder")
		print("OrderStatus=", pOrder.OrderStatus)
		print("StatusMsg=", pOrder.StatusMsg)
		print("LimitPrice=", pOrder.LimitPrice)

	def OnRspOrderInsert(self, pInputOrder: 'CThostFtdcInputOrderField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		print("OnRspOrderInsert")
		print("ErrorID=", pRspInfo.ErrorID)
		print("ErrorMsg=", pRspInfo.ErrorMsg)

	def execute_order(self, symbol, order_type, price, amount):
		# if not self.connected:
		# 	return {'order_id': 0}

		if (order_type == 'limit_going_long'):
			price_type = api.THOST_FTDC_OPT_LimitPrice
			offset = "0"
			direction = api.THOST_FTDC_D_Buy
		elif (order_type == 'limit_going_short'):
			price_type = api.THOST_FTDC_OPT_LimitPrice
			offset = "0"
			direction = api.THOST_FTDC_D_Sell
		elif (order_type == 'market_going_long'):
			price_type = api.THOST_FTDC_OPT_AnyPrice
			offset = "0"
			direction = api.THOST_FTDC_D_Buy
		elif (order_type == 'market_going_short'):
			price_type = api.THOST_FTDC_OPT_AnyPrice
			offset = "0"
			direction = api.THOST_FTDC_D_Sell
		elif (order_type == 'limit_close_long'):
			price_type = api.THOST_FTDC_OPT_LimitPrice
			offset = "1"
			direction = api.THOST_FTDC_D_Buy
		elif (order_type == 'limit_close_short'):
			price_type = api.THOST_FTDC_OPT_LimitPrice
			offset = "1"
			direction = api.THOST_FTDC_D_Sell
		elif (order_type == 'market_close_long'):
			price_type = api.THOST_FTDC_OPT_AnyPrice
			offset = "1"
			direction = api.THOST_FTDC_D_Buy
		elif (order_type == 'market_close_short'):
			price_type = api.THOST_FTDC_OPT_AnyPrice
			offset = "1"
			direction = api.THOST_FTDC_D_Sell

		if ('.' in symbol):
			exchange, symbol = symbol.split('.')
		else:
			exchange = ''
		order_ref = str(self.MaxOrderRef)
		self.MaxOrderRef +=1
		orderfield = api.CThostFtdcInputOrderField()
		orderfield.BrokerID = self.broker_id
		orderfield.ExchangeID = exchange
		orderfield.InstrumentID = symbol
		orderfield.UserID = self.api_key
		orderfield.InvestorID = self.api_key
		orderfield.Direction = direction
		orderfield.LimitPrice = price
		orderfield.VolumeTotalOriginal = amount
		orderfield.OrderPriceType = price_type
		orderfield.ContingentCondition = api.THOST_FTDC_CC_Immediately
		orderfield.TimeCondition = api.THOST_FTDC_TC_GFD
		orderfield.VolumeCondition = api.THOST_FTDC_VC_AV
		orderfield.CombHedgeFlag = "1"
		orderfield.CombOffsetFlag = offset
		orderfield.GTDDate = ""
		orderfield.OrderRef = order_ref
		orderfield.MinVolume = 0
		orderfield.ForceCloseReason = api.THOST_FTDC_FCC_NotForceClose
		orderfield.IsAutoSuspend = 0
		self.tapi.ReqOrderInsert(orderfield, 0)
		rst = {}
		order_id = '{}.{}.{}'.format(self.FrontID, self.SessionID, order_ref)
		rst['order_id'] = order_id
		return rst

	def cancel_order(self, symbol, order_id):
		if ('.' in symbol):
			exchange, symbol = symbol.split('.')
		else:
			exchange = ''
		front_id, session_id, order_ref = order_id.split('.')
		front_id = int(front_id)
		session_id = int(session_id)
		orderfield = api.CThostFtdcInputOrderActionField()
		orderfield.BrokerID = self.broker_id
		orderfield.ExchangeID = exchange
		orderfield.InstrumentID = symbol
		orderfield.UserID = self.api_key
		orderfield.InvestorID= self.api_key
		orderfield.FrontID = front_id
		orderfield.SessionID = session_id
		orderfield.OrderRef = order_ref
		orderfield.ActionFlag = api.THOST_FTDC_AF_Delete
		self.tapi.ReqOrderAction(orderfield, 1)
		print("cancel order")


def get_trade_spi(td_address, broker_id, api_key, secret_key, ctp_app_id, ctp_auth_code):
	tradeapi = api.CThostFtdcTraderApi_CreateFtdcTraderApi()
	tradespi = CTradeSpi(tradeapi, broker_id, api_key, secret_key, ctp_app_id, ctp_auth_code)
	tradeapi.RegisterFront('tcp://{}'.format(td_address))
	tradeapi.RegisterSpi(tradespi)
	tradeapi.SubscribePrivateTopic(api.THOST_TERT_QUICK)
	tradeapi.SubscribePublicTopic(api.THOST_TERT_QUICK)
	tradeapi.Init()
	time.sleep(3)
	tradespi.ReqAuthenticate()
	time.sleep(3)
	tradespi.ReqUserLogin()
	time.sleep(3)
	# tradeapi.Join()
	return tradespi
