# coding=utf-8

import os
import re
import time
import json
import psutil
import socket
import datetime
import traceback
import thriftpy2

from bson.objectid import ObjectId
from thriftpy2.rpc import make_server

from dao_execute.utils import user_api
from dao_execute.settings.config import cfg
from dao_execute.db.dt_models import (User, ExAccount, Order)
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
		self.MaxOrderRef = 1
		self.tick_size_dict = cfg['tick_size_dict']
		self.close_today_ex_list = cfg['close_tyday_ex_list']
		self.init = 0
		self.error_id = 0

	def OnFrontConnected(self) -> "void":
		try:
			print("OnFrontConnected")
			# self.tapi.Init()
			# self.__init__(self.tapi, self.broker_id, self.api_key, self.secret_key,
			#               self.ctp_app_id, self.ctp_auth_code)
			self.ReqAuthenticate_local()
		except Exception as e:
			self.init = -1
			print(traceback.format_exc())

	def ReqAuthenticate_local(self):
		try:
			authfield = api.CThostFtdcReqAuthenticateField();
			authfield.BrokerID = self.broker_id
			authfield.UserID = self.api_key
			authfield.AppID = self.ctp_app_id
			authfield.AuthCode = self.ctp_auth_code
			authfield.UserProductInfo = 'daotec'
			self.tapi.ReqAuthenticate(authfield, 0)
			print("send ReqAuthenticate ok")
		except Exception as e:
			self.init = -1
			print(traceback.format_exc())

	def OnRspAuthenticate(self, pRspAuthenticateField: 'CThostFtdcRspAuthenticateField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		try:
			print("BrokerID=", pRspAuthenticateField.BrokerID)
			print("UserID=", pRspAuthenticateField.UserID)
			print("AppID=", pRspAuthenticateField.AppID)
			print("AppType=", pRspAuthenticateField.AppType)
			print("ErrorID=", pRspInfo.ErrorID)
			print("ErrorMsg=", pRspInfo.ErrorMsg)
			self.error_id = pRspInfo.ErrorID
			self.ReqUserLogin_local()
		except Exception as e:
			self.init = -1
			print(traceback.format_exc())

	def ReqUserLogin_local(self):
		try:
			loginfield = api.CThostFtdcReqUserLoginField()
			loginfield.BrokerID = self.broker_id
			loginfield.UserID = self.api_key
			loginfield.Password = self.secret_key
			loginfield.UserProductInfo = "python dll"
			self.tapi.ReqUserLogin(loginfield, 0)
			print("send login ok")
		except Exception as e:
			self.init = -1
			print(traceback.format_exc())

	def OnRspUserLogin(self, pRspUserLogin: 'CThostFtdcRspUserLoginField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		try:
			print("OnRspUserLogin")
			print("TradingDay=", pRspUserLogin.TradingDay)
			print("SessionID=", pRspUserLogin.SessionID)
			print("ErrorID=", pRspInfo.ErrorID)
			print("ErrorMsg=", pRspInfo.ErrorMsg)
			self.SessionID = pRspUserLogin.SessionID
			self.FrontID = pRspUserLogin.FrontID
			self.MaxOrderRef = int(pRspUserLogin.MaxOrderRef)
			self.init = 1

			qryinfofield = api.CThostFtdcQrySettlementInfoField()
			qryinfofield.BrokerID = self.broker_id
			qryinfofield.InvestorID = self.api_key
			qryinfofield.TradingDay = pRspUserLogin.TradingDay
			self.tapi.ReqQrySettlementInfo(qryinfofield,0)
			print ("send ReqQrySettlementInfo ok")
		except Exception as e:
			self.init = -1
			print(traceback.format_exc())

	def OnRspQrySettlementInfo(self, pSettlementInfo: 'CThostFtdcSettlementInfoField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		try:
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
		except Exception as e:
			print(traceback.format_exc())

	def OnRspSettlementInfoConfirm(self, pSettlementInfoConfirm: 'CThostFtdcSettlementInfoConfirmField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		try:
			print("OnRspSettlementInfoConfirm")
			print("ErrorID=", pRspInfo.ErrorID)
			print("ErrorMsg=", pRspInfo.ErrorMsg)
			# self.connected = True
			# ReqorderfieldInsert(self.tapi)
			# print("send ReqorderfieldInsert ok")
		except Exception as e:
			print(traceback.format_exc())

	def OnRtnOrder(self, pOrder: 'CThostFtdcOrderField') -> "void":
		try:
			print("OnRtnOrder")
			print("OrderStatus=", pOrder.OrderStatus)
			print("StatusMsg=", pOrder.StatusMsg)
			print("LimitPrice=", pOrder.LimitPrice)
			order_id = '{}.{}.{}'.format(pOrder.FrontID, pOrder.SessionID, pOrder.OrderRef)

			order_dict = {}
			order_dict['order_id'] = order_id
			order_dict['order_status'] = pOrder.OrderStatus
			order_dict['quantity'] = pOrder.VolumeTotalOriginal
			order_dict['quantity_treaded'] = pOrder.VolumeTraded
			order_dict['trading_day'] = pOrder.TradingDay
			self.on_order(order_dict)
		except Exception as e:
			print(traceback.format_exc())

	def OnRspOrderInsert(self, pInputOrder: 'CThostFtdcInputOrderField', pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
		try:
			print("OnRspOrderInsert")
			print("ErrorID=", pRspInfo.ErrorID)
			print("ErrorMsg=", pRspInfo.ErrorMsg)
			order_id = '{}.{}.{}'.format(self.FrontID, self.SessionID, pInputOrder.OrderRef)
			print(order_id)
			if (pRspInfo.ErrorID in [30, 31]):
				# margin not available
				order_status = '5'
				order_dict = {}
				order_dict['order_id'] = order_id
				order_dict['order_status'] = order_status
				self.on_order(order_dict)
		except Exception as e:
			print(traceback.format_exc())

	def execute_order(self, user_id, exchange, account_type, strategy_name, symbol, order_type, price, amount, money_num, exec_ts, strategy_instance_id, close_today):
		status = 1
		data = {}
		user = User.objects.get(id=str(user_id))
		try:
		    amount = int(amount)
		except Exception as e:
			status = 0
			data = '输入数量不是数字!'
			return status, data
		try:
			price = float(price)
		except Exception as e:
			status = 0
			data = '输入价格不是数字!'
			return status, data
		if ('.' in symbol):
			exchange_, symbol = symbol.split('.')
		else:
			exchange_ = ''
		if (order_type == 'limit_going_long'):
			price_type = api.THOST_FTDC_OPT_LimitPrice
			# offset = "0"
			offset = api.THOST_FTDC_OF_Open
			direction = api.THOST_FTDC_D_Buy
		elif (order_type == 'limit_going_short'):
			price_type = api.THOST_FTDC_OPT_LimitPrice
			# offset = "0"
			offset = api.THOST_FTDC_OF_Open
			direction = api.THOST_FTDC_D_Sell
		elif (order_type == 'market_going_long'):
			# price_type = api.THOST_FTDC_OPT_AnyPrice
			price_type = api.THOST_FTDC_OPT_LimitPrice
			tick_size = self.get_tick_size(symbol)
			price += tick_size
			# offset = "0"
			offset = api.THOST_FTDC_OF_Open
			direction = api.THOST_FTDC_D_Buy
		elif (order_type == 'market_going_short'):
			# price_type = api.THOST_FTDC_OPT_AnyPrice
			price_type = api.THOST_FTDC_OPT_LimitPrice
			tick_size = self.get_tick_size(symbol)
			price -= tick_size
			# offset = "0"
			offset = api.THOST_FTDC_OF_Open
			direction = api.THOST_FTDC_D_Sell
		elif (order_type == 'limit_close_long'):
			price_type = api.THOST_FTDC_OPT_LimitPrice
			# offset = "1"
			if ((close_today is True) and (exchange_ in self.close_today_ex_list)):
				offset = api.THOST_FTDC_OF_CloseToday
			else:
				offset = api.THOST_FTDC_OF_Close
			direction = api.THOST_FTDC_D_Sell
		elif (order_type == 'limit_close_short'):
			price_type = api.THOST_FTDC_OPT_LimitPrice
			# offset = "1"
			if ((close_today is True) and (exchange_ in self.close_today_ex_list)):
				offset = api.THOST_FTDC_OF_CloseToday
			else:
				offset = api.THOST_FTDC_OF_Close
			direction = api.THOST_FTDC_D_Buy
		elif (order_type == 'market_close_long'):
			# price_type = api.THOST_FTDC_OPT_AnyPrice
			price_type = api.THOST_FTDC_OPT_LimitPrice
			tick_size = self.get_tick_size(symbol)
			price -= tick_size
			# offset = "1"
			if ((close_today is True) and (exchange_ in self.close_today_ex_list)):
				offset = api.THOST_FTDC_OF_CloseToday
			else:
				offset = api.THOST_FTDC_OF_Close
			direction = api.THOST_FTDC_D_Sell
		elif (order_type == 'market_close_short'):
			# price_type = api.THOST_FTDC_OPT_AnyPrice
			price_type = api.THOST_FTDC_OPT_LimitPrice
			tick_size = self.get_tick_size(symbol)
			price += tick_size
			# offset = "1"
			if ((close_today is True) and (exchange_ in self.close_today_ex_list)):
				offset = api.THOST_FTDC_OF_CloseToday
			else:
				offset = api.THOST_FTDC_OF_Close
			direction = api.THOST_FTDC_D_Buy
		else:
			status = 0
			data = '输入订单类型不正确!'
			return status, data

		order_ref = str(self.MaxOrderRef)
		self.MaxOrderRef +=1
		orderfield = api.CThostFtdcInputOrderField()
		orderfield.BrokerID = self.broker_id
		orderfield.ExchangeID = exchange_
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

		order_id = '{}.{}.{}'.format(self.FrontID, self.SessionID, order_ref)
		msg = ('下单成功, 交易所: {}, 标的: {}, '
			   '价格: {}, 数量: {}').format(
			   exchange, symbol, price, amount)
		data['order_id'] = order_id
		data['data'] = msg

		order = Order()
		order.user_name = user.user_name
		order.user_id = user.id
		order.phone_num = user.phone_num
		order.exchange = exchange
		order.account_type = account_type
		if (strategy_instance_id != ''):
			order.strategy_instance_id = ObjectId(strategy_instance_id)
		order.strategy_name = strategy_name
		order.symbol = symbol
		order.order_type = order_type
		order.order_id = order_id
		order.price = str(price)
		order.avg_price = 0.0
		order.quantity = str(amount)
		order.quantity_treaded = 0.0
		order.quantity_frozen = 0.0
		order.quantity_canceled = 0.0
		order.order_cancel_timestamp = 0.0
		order.order_deal_timestamp = 0.0
		order.order_status = 'pending'
		order.save()
		return status, data

	def cancel_order(self, user_id, exchange, account_type, strategy_name, symbol, order_id):
		user = User.objects.get(id=user_id)
		if ('.' in symbol):
			exchange_, symbol = symbol.split('.')
		else:
			exchange_ = ''
		front_id, session_id, order_ref = order_id.split('.')
		front_id = int(front_id)
		session_id = int(session_id)
		orderfield = api.CThostFtdcInputOrderActionField()
		orderfield.BrokerID = self.broker_id
		orderfield.ExchangeID = exchange_
		orderfield.InstrumentID = symbol
		orderfield.UserID = self.api_key
		orderfield.InvestorID= self.api_key
		orderfield.FrontID = front_id
		orderfield.SessionID = session_id
		orderfield.OrderRef = order_ref
		orderfield.ActionFlag = api.THOST_FTDC_AF_Delete
		self.tapi.ReqOrderAction(orderfield, 1)
		status = 1
		data = '订单撤销成功, 交易所: {}, 标的: {}'.format(exchange, symbol)
		return status, data

	def on_order(self, order_dict):
		order_id = order_dict['order_id']
		order_status = order_dict.get('order_status', '3')
		quantity = order_dict.get('quantity', 0.0)
		quantity_treaded = order_dict.get('quantity_treaded', 0.0)
		trading_day = order_dict.get('trading_day', '')

		order = Order.objects.get(order_id=order_id)
		avg_price = 0.0
		quantity_frozen = 0.0
		quantity_canceled = 0.0
		order_deal_timestamp = 0.0
		order_cancel_timestamp = 0.0
		if (order_status in ['3', '4']):
			order_status = 'pending'
		elif (order_status in ['1', '2']):
			order_status = 'partial_filled'
			quantity_treaded = quantity_treaded
			quantity_frozen = quantity - quantity_treaded
			avg_price = float(order.price)
			order_deal_timestamp = time.time()
		elif (order_status == '0'):
			order_status = 'filled'
			avg_price = float(order.price)
			order_deal_timestamp = time.time()
		elif (order_status == '5'):
			order_status = 'cancelled'
			order_cancel_timestamp = time.time()
			quantity_canceled = quantity - quantity_treaded
		else:
			order_status = 'undefined'
		order.order_status = order_status
		order.quantity_treaded = quantity_treaded
		order.quantity_frozen = quantity_frozen
		order.quantity_canceled = quantity_canceled
		order.avg_price = avg_price
		order.order_deal_timestamp = order_deal_timestamp
		order.order_cancel_timestamp = order_cancel_timestamp
		order.trading_day = trading_day
		order.save()
		return True

	def get_tick_size(self, symbol):
		pre_symbol = re.findall(r'[0-9]+|[a-zA-Z]+', symbol)[0]
		return self.tick_size_dict.get(pre_symbol, 1)


def get_trade_spi(td_address, broker_id, api_key, secret_key, ctp_app_id, ctp_auth_code):
	tradeapi = api.CThostFtdcTraderApi_CreateFtdcTraderApi()
	tradespi = CTradeSpi(tradeapi, broker_id, api_key, secret_key, ctp_app_id, ctp_auth_code)
	tradeapi.RegisterFront('tcp://{}'.format(td_address))
	tradeapi.RegisterSpi(tradespi)
	tradeapi.SubscribePrivateTopic(api.THOST_TERT_QUICK)
	tradeapi.SubscribePublicTopic(api.THOST_TERT_QUICK)
	tradeapi.Init()
	while True:
		if (tradespi.init == 1):
			print('init ok')
			break
		elif (tradespi.init == -1):
			print('init failed')
			break
		time.sleep(0.3)
	return tradespi


class TradeCtpHandler(object):

	def __init__(self):
		self.trade_spi_dict = {}
		self.set_pid()
		self.ctp_ex_dict = cfg['ctp_ex_dict']
		exchange = 'ctp'
		users = User.objects.all()
		for user in users:
			user_id = user.id
			user_name = user.user_name
			ex_account_list = ExAccount.objects.filter(
				user_id=user_id, exchange=exchange)
			for ex_account in ex_account_list:
				try:
					ex_account_name = ex_account.ex_account_name
					api_dict = user_api.get_api_dict_fast(user, exchange, ex_account_name)
					td_address = api_dict['td_address']
					broker_id = api_dict['broker_id']
					api_key = api_dict['api_key']
					secret_key = api_dict['secret_key']
					ctp_app_id = api_dict['ctp_app_id']
					ctp_auth_code = api_dict['ctp_auth_code']
					if self.detect_active(td_address):
						unique_ctp_key = '{}.{}'.format(user_id, ex_account_name)
						trade_spi = get_trade_spi(td_address, broker_id, api_key, secret_key, ctp_app_id, ctp_auth_code)
						self.trade_spi_dict[unique_ctp_key] = trade_spi
					else:
						print(user_id, user_name, td_address, 'cannot connect')
				except Exception as e:
					print(user_id, user_name, traceback.format_exc())
		print(self.trade_spi_dict)

	def set_pid(self):
		pid = os.getpid()
		with open('ctps.pid', 'w') as f:
			f.write(str(pid))

	def ret_resp(self, status, data):
		resp = {}
		resp['status'] = status
		resp['data'] = data
		return json.dumps(resp)

	def detect_active(self, td_address):
		ip_addr, port = td_address.split(':')
		delay = 3
		limit = 3
		while True:
			try:
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				sock.settimeout(delay)
				sock.connect((ip_addr, int(port)))
				result = sock.send(b'9')
				sock.settimeout(None)
				sock.close()
				if result == 1:
					return True
				else:
					limit -= 1
					time.sleep(1)
					if limit < 0:
						return False
			except Exception as e:
				limit -= 1
				time.sleep(1)
				if limit < 0:
					return False

	def execute_order(self, user_id, exchange, account_type, strategy_name, symbol, order_type, price, amount, money_num=0, exec_ts=0.0, strategy_instance_id='', close_today=True):
		unique_ctp_key = '{}.{}'.format(user_id, account_type)
		trade_spi = self.trade_spi_dict.get(unique_ctp_key, None)
		if not trade_spi is None:
			symbol = self.convert_symbol(symbol)
			status, data = trade_spi.execute_order(user_id, exchange, account_type, strategy_name, symbol, order_type, price, amount, money_num, exec_ts, strategy_instance_id, close_today)
		else:
			status = 0
			data = '账户不存在'
		return self.ret_resp(status, data)

	def cancel_order(self, user_id, exchange, account_type, strategy_name, symbol, order_id):
		unique_ctp_key = '{}.{}'.format(user_id, account_type)
		trade_spi = self.trade_spi_dict.get(unique_ctp_key, None)
		if not trade_spi is None:
			symbol = self.convert_symbol(symbol)
			status, data = trade_spi.cancel_order(user_id, exchange, account_type, strategy_name, symbol, order_id)
		else:
			status = 0
			data = '账户不存在'
		return self.ret_resp(status, data)

	def convert_symbol(self, symbol):
		pre_symbol = re.findall(r'[0-9]+|[a-zA-Z]+', symbol)[0]
		for ex, symbol_list in self.ctp_ex_dict.items():
			if (pre_symbol in symbol_list):
				symbol = '{}.{}'.format(ex, symbol)
				break
		return symbol


def run():
	ctp_rpc = cfg['ctp_rpc']
	host = ctp_rpc['host']
	port = ctp_rpc['port']
	print('[*] {}:{}, TradeCtp running'.format(host, port))
	filename = 'dao_execute/exchange_api/ctp/trade_ctp.thrift'
	ctp_thrift = thriftpy2.load(filename, module_name='ctp_thrift')
	server = make_server(ctp_thrift.TradeCtp, TradeCtpHandler(), host, port, client_timeout=10000)
	server.serve()


def restart_ctps(time_now):
	print('[*] restarting ctps, time: {}'.format(time_now))
	try:
		with open('ctps.pid', 'r') as f:
			pid = f.read()
		pid_status = psutil.pid_exists(int(pid))
		if (pid_status is True):
			cmd = 'kill {}'.format(pid)
			os.system(cmd)
			print(cmd)
		else:
			pass
	except Exception as e:
		print('[*] ctps.pid not exists')

	cmd = 'python manage.py -t ctp &'
	os.system(cmd)
	print(cmd)


def monitor_trade_ctps():
    print('[*] monitoring ctps')
    time_now = datetime.datetime.now()
    day_day = time_now.day - 1
    night_day = time_now.day - 1
    restart_ctps(time_now)
    while True:
        try:
            if ('ctps.pid' in os.listdir()):
                time_now = datetime.datetime.now()
                hour = time_now.hour
                minute = time_now.minute
                day = time_now.day
                if ((hour == 8) and (minute >= 50) and (day_day < day)):
                    restart_ctps(time_now)
                    day_day = day
                elif ((hour == 20) and (minute >= 57) and (night_day < day)):
                    restart_ctps(time_now)
                    night_day = day
        except Exception as e:
            print(traceback.format_exc())
        time.sleep(60)
