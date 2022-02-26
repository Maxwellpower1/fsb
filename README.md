# 金融街Bets（fsb）

量化交易系统

### dao_quote 行情模块

提供 tick depth bar，对外提供 Thrift RPC、Rest API、Redis sub，行情本地存储到SQLite & MongoDB
* 商品期货行情 (CTP、易盛Esunny)
* 数字货币行情 (OKEx、火币、币安...)
* 股票行情 (Tushare)

### dao_execute 交易执行模块

* 对外提供 Thrift RPC 接口
* 商品期货 (CTP) 交易
* 数字货币交易 (OKEx、火币、币安...)


### dao_strategy 策略模块

* 实盘
* 回测

### dao_web

Web 管理界面
* 查看行情，手动下单
* 管理实盘交易策略
* 网页编码，策略研究&回测
* 后台管理行情
* 后台查看日志