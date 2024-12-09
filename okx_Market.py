#!/user/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import time, math
from BASECLASS.okexbase import ExchangeOkex, Stg
import schedule
from BASECLASS.configfile import ReadConfigFile
from COMM.dboper import MyDBConn
from COMM import commFunctions as func
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from mplfinance.original_flavor import candlestick_ohlc
import mplfinance as mpf
import pandas as pd
from decimal import Decimal
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
from queue import Queue

class MarketInfo(object):
    def __init__(self):
        try:
            self.config = ReadConfigFile("okex_config.ini")
            self.dc = MyDBConn(int(self.config.read_info("api","dbsource")))
            self.exchange = None  # 初始化为None，等待账户选择后再初始化
            self.spotexchange = None
            self.coin_info_list = []
        except Exception as e:
            print(e)

    def GetAccountList(self):
        """
        获取可用账户列表
        """
        try:
            # 从acct_info表获取账户信息，group_id = 2 表示 OKEx 账户
            accounts = self.dc.QueryAllAcctFollowFutureOkex()
            account_list = []
            for acct in accounts:
                acct_id = acct[0]
                acct_info = self.dc.QueryOkexAcctInfoByID(acct_id)
                if acct_info:
                    account_list.append(f"{acct_id} - {acct_info['name']}")
            
            print(f"找到 {len(account_list)} 个账户")
            return account_list
        except Exception as e:
            self.ExceptionThrow(e)
            print(f"获取账户列表失败: {str(e)}")
            return []

    def SetAccount(self, acct_id):
        """
        设置当前账户
        """
        try:
            acct_info = self.dc.QueryOkexAcctInfoByID(acct_id)
            if acct_info:
                obj = ExchangeOkex()
                self.exchange = obj.GetExchangeOkexFuture(acct_info)
                self.spotexchange = obj.GetExchangeOkexSpot(acct_info)
                return True
            return False
        except Exception as e:
            self.ExceptionThrow(e)
            return False

    def GetCoinInfoFuture(self, symbol):
        try:
            # 获取合约信息
            data = self.exchange.get_instrument_info(f"{symbol}-USDT-SWAP")
            contract_size = float(data['contract_val'])
            price = float(data['last'])
            coin_info = {
                'symbol': symbol,
                'order_size_min': float(data['min_size']),
                'order_size_max': float(data['max_size']),
                'cs': contract_size,
                'price': price,
                'leverage_max': float(data['max_leverage'])
            }
            return coin_info
        except Exception as e:
            self.ExceptionThrow(e)

    def ListAcctInfo(self):
        """
        获取账户持仓信息
        """
        try:
            positions = self.exchange.get_positions()
            account = self.exchange.get_account_info()
            
            data = []
            for pos in positions:
                if float(pos['position']) != 0:  # 只显示有持仓的
                    symbol = pos['instrument_id'].split('-')[0]
                    element = [
                        symbol,
                        pos['leverage'],
                        pos['position'],
                        pos['margin']
                    ]
                    data.append(element)
                    
            return float(account['equity']), data
            
        except Exception as e:
            self.ExceptionThrow(e)
            return 0, []

    def GetProductList(self):
        """
        获取产品列表
        """
        try:
            comb = self.dc.QueryProductListFutureOkex()
            product_list = comb[0][0].split("#")
            return product_list
        except Exception as e:
            self.ExceptionThrow(e)
            return []

    def ShowKLines(self, symbol="BTC"):
        """
        显示K线图
        """
        klines = self.dc.QueryProductDataKLinesOkex(symbol)
        if not klines:
            print(f"k线数据没有找到，请检查：{symbol}")
            return
            
        day_klines = func.minute_to_daily(klines)
        self.plot_candlestick(day_klines, symbol)

    # ... 其他方法保持类似，只需要替换相应的API调用 ... 