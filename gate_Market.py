#!/user/bin/env python3
# -*- coding: utf-8 -*-
import datetime
# 获取行情信息的专用定时程序，每30分钟检索数据库，找到数据库中的产品列表，填写到 product 表中

#
import time, math
from BASECLASS.gateiobase import ExchangeGatieio,Stg
from gate_api import ApiClient, Configuration, FuturesApi, FuturesOrder, Transfer, WalletApi
import schedule
from BASECLASS.configfile import ReadConfigFile
from COMM.dboper import  MyDBConn
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
            self.config = ReadConfigFile("gate_config.ini")
            self.dc = MyDBConn(int(self.config.read_info("api","dbsource")) )

            self.exchange = None  # 初始化为None，等待账户选择后再初始化
            self.spotexchange = None
            self.coin_info_list = []
        except Exception as e:
            print(e)
    def ExceptionThrow(self, e):
        line = e.__traceback__.tb_frame.f_globals["__file__"] + " 异常发生在(行):%d " % e.__traceback__.tb_lineno + str(e)
        print(time.strftime('%y-%m-%d %H:%M:%S') + "ExceptionThrow" + line + '-------------- \n')

    def GetPubExchange(self):
        obj = ExchangeGatieio()
        defaultAcct = int(self.config.read_info("api","pub_acct"))
        acctdata = self.dc.QueryGateAcctInfoByID(defaultAcct)
        exchange = obj.GetExchangeGateioFuture(acctdata)
        self.spotexchange = obj.GetExchangeGateioSpot(acctdata)
        return exchange

    def GetWallet(self, target_acct):
        # 从数据库读取账户记录,不带参数是返回全部记录
        try:

            apiKey = target_acct['apiKey']
            secret = target_acct['secret']

            config = Configuration(key=apiKey, secret=secret)
            wallet = WalletApi(ApiClient(config))

            return wallet

        except Exception as e:
            self.ExceptionThrow(e)


    #从现货转入期货1，从期货转出现货-1
    def TransferMoney(self,wallet_api,margin):

        try:
            settle = "usdt"
            if  margin < 0:
                money = abs(margin)
                transfer_p = Transfer(settle=settle,amount=str(money), currency=settle.upper(), _from='spot', to='futures')
            else:
                transfer_p = Transfer(settle=settle,amount=str(margin), currency=settle.upper(), _from='futures', to='spot')
            info = wallet_api.transfer(transfer_p)
            print(info)
        except Exception as e:
            self.ExceptionThrow(e)


    #打印出所有期货品种的基本信息
    def ListFutureInfo(self):

        all_future = self.exchange.list_futures_contracts("usdt")
        for index,itor in enumerate(all_future,start=1):
            print(index,itor.name,func.timestamp_to_datetime(itor.create_time).strftime("%y-%m-%d"),"最新价：%.2f,每手最低金额：%.2f,合约面值：%.6f"%(float(itor.mark_price),float(itor.mark_price)*float(itor.quanto_multiplier),float(itor.quanto_multiplier)))

    def ListSpotInfo(self):
    # 打印现信息
        data = self.spotexchange.get_currency_pair(currency_pair="BTC_USDT")
        print(data)

        data = self.spotexchange.get_currency(currency="BTC")
        print(data)
        return

    def ListLatestStgInfo(self):
        print("下面开始查询策略信息：")
        stg_name = "A25"
        stg_id = 4
        data = self.dc.QueryCombProductListGateio(stg_name)
        product_list = data[1].split("#")
        print("策略的产品：",product_list)

        latest_stg_time = func.get_last_half_hour()
        comb_product_count = 0
        winner_sum = 0
        long_nums = 0
        short_nums = 0
        empty_nums = 0

        stg_list = []
        for product in product_list:

            stg_detail = self.dc.QueryStratageDetailLatestGateio(product,stg_id)
            stg_list.append(stg_detail)
            if latest_stg_time != stg_detail['stratage_time']:
                print("策略时间校验错误，最新策略时间应该是：%s,该产品%s的策略时间是：%s"%(latest_stg_time,stg_detail['symbole'],stg_detail['stratage_time']))
            else:
                comb_product_count += 1
                winner_sum += float(stg_detail['winner'])
            stg = stg_detail['stg']
            if stg == 1 or stg == 2:
                long_nums += 1
            elif stg == -1 or stg == -2:
                short_nums += 1
            else:
                empty_nums += 1

        print("策略%d，产品组合:%s，共找到产品%d,策略时间：%s - %s, 期间盈亏为：%.2f, 多头：%d,空头:%d,空仓：%d"%(stg_id,stg_name,comb_product_count,latest_stg_time,func.add_minutes(latest_stg_time,30),winner_sum,long_nums,short_nums,empty_nums))



    def ListStgInfoLastN(self,n=48):

        print("下面开始查询策过去%d个半小时的策略详细信息："%n)
        stg_name = "A25"
        stg_id = 4
        data = self.dc.QueryCombProductListGateio(stg_name)
        product_list = data[1].split("#")
        print("策略的产品是：",product_list)

        now_latest_stg_time = func.get_last_half_hour()

        for i in range(0,n-1):
            latest_stg_time = func.subtract_minutes(now_latest_stg_time,i*30)
            comb_product_count = 0
            winner_sum = 0
            long_nums = 0
            short_nums = 0
            empty_nums = 0

            stg_list = []
            for product in product_list:

                stg_detail = self.dc.QueryStratageDetailGateio(product,latest_stg_time.strftime('%y-%m-%d %H:%M:%S') ,stg_id)
                if stg_detail == 0:
                    print("%s这个时间段的略还未计算出来，请运行策略生成程序")
                    break

                stg_list.append(stg_detail)
                if latest_stg_time != stg_detail['stratage_time']:
                    print("策略时间校验错误，最新策略时间应该是：%s,该产品%s的策略时间是：%s"%(latest_stg_time,stg_detail['symbole'],stg_detail['stratage_time']))
                else:
                    comb_product_count += 1
                    winner_sum += float(stg_detail['winner'])
                stg = stg_detail['stg']
                if stg == 1 or stg == 2:
                    long_nums += 1
                elif stg == -1 or stg == -2:
                    short_nums += 1
                else:
                    empty_nums += 1

            print("策略%d，产品组合:%s，共找到产品%d,策略时间：%s - %s, 期间盈亏为：%.2f, 多头：%d,空头:%d,空仓：%d"%(stg_id,stg_name,comb_product_count,latest_stg_time,func.add_minutes(latest_stg_time,30),winner_sum,long_nums,short_nums,empty_nums))


    def GetProductList(self):
        comb = self.dc.QueryProductListFutureGateio()
        product_list = comb[0][0].split("#")
        return product_list

    def GetCoinInfoFuture(self, symbol):
        try:
            # 先查有没有历史记录，没有则重新去网上查

            data = self.exchange.get_futures_contract("usdt",symbol+"_USDT")
            cs = float(data.quanto_multiplier) #contracts size 一张合约的币数
            price = float(data.mark_price)
            coin_info = {'symbol': symbol, 'order_size_min': float(data.order_size_min), 'order_size_max':float(data.order_size_max), 'cs': cs, 'price': price, 'leverage_max':float(data.leverage_max)}
            return coin_info
        except Exception as e:
            self.ExceptionThrow(e)

    #期货下单函数
    def SendOrder(self,symbol,amt,coin_info,lever=3):
        try:
            total_amt = abs(amt)
            max_size = coin_info['order_size_max']
            leverage_max = coin_info['leverage_max']


            contract = symbol + "_USDT"
            self.exchange.update_position_leverage("usdt", contract, min(lever,leverage_max))

            while (total_amt): #分拆下单
                trade_amt = total_amt

                if trade_amt >= max_size:  # 最大交易数量
                    trade_amt = max_size

                total_amt = total_amt - trade_amt

                if amt>0:
                    coin_num = trade_amt
                else:
                    coin_num = -1 * trade_amt


                order = FuturesOrder(contract=contract, size=coin_num, price="0", tif='ioc')
                order = self.exchange.create_futures_order("usdt",order)
                if order.status == 'finished':
                    print('交易成功：', symbol + "_USDT", "差距为:", coin_num,  time.strftime('%y-%m-%d %H:%M:%S'))

        except Exception as e:
            print(symbol,amt)
            self.ExceptionThrow(e)

    def ListAcctInfo(self):
        acct_balances = self.exchange.list_positions("usdt", holding="true")
        fa = self.exchange.list_futures_accounts("usdt")
        data = []
        for itor in acct_balances:

            symbol = itor.contract.split("_")[0]
            element = [symbol,itor.leverage,itor.size,itor.value]
            data.append(element)

        return round(float(fa.available),2),data

    def plot权益列表(self,权益列表):
        """
        绘制权益折线图。

        :param 权益列表: 包含(日期, 权益)元组的列表
        """
        # 解包权益列表，分别获取日期和权益
        dates = [date for date, _ in 权益列表]
        cumulative_rights  = [权益 for _, 权益 in 权益列表]
        principal = 250000
        max_rights, max_drawdown, current_drawdown = func.calculate_performance(权益列表, principal)
        # 创建折线图
        plt.figure(figsize=(10, 5))  # 设置图表大小
        plt.plot(dates, cumulative_rights , marker='o')  # 绘制折线图，'o'表示数据点的形状

        # 设置图表标题和坐标轴标签
        plt.title('Profit of All CTA')
        plt.xlabel('date')
        plt.ylabel('profit')

        # 设置x轴的日期格式
        plt.gcf().autofmt_xdate()  # 自动旋转日期标记
        plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%y-%m-%d'))

        # 显示史最高权对应本金的收益率
        plt.text(dates[20], cumulative_rights[-1], f'max profit: {max_rights:.2f}', fontsize=9, ha='right')
        plt.text(dates[20], cumulative_rights[-1] - 0.4 * (max_rights - cumulative_rights[-1]),
                 f'profit_rate: {(max_rights - principal) / principal:.2%}', fontsize=9, ha='right')
        # 显示历史最大回撤比例
        plt.text(dates[20], cumulative_rights[-1] - 0.8 * (max_rights - cumulative_rights[-1]),
                 f'max_drawback: {max_drawdown:.2%}', fontsize=9, ha='right')
        # 显示当前相对最高点的回撤比例
        plt.text(dates[20], cumulative_rights[-1] - 1.2 * (max_rights - cumulative_rights[-1]),
                 f'current_drawback: {current_drawdown:.2%}', fontsize=9, ha='right')


        # 显示图表
        plt.show()

    def ShowStgInfo(self):
        try:
            stg_name = "A25"
            data = self.dc.QueryCombProductListGateio(stg_name)
            product_list = data[1].split("#")
            print("策略的产品：", product_list)

            self.product_cumulate = []
            self.product_value = []
            for product in product_list:
                product_data = self.dc.QueryStratageDetailGateio(product,4)
                new_list = [sublist[:2] for sublist in product_data]
                daily_data = func.calculate_daily_profit(new_list)
                cumulate = func.calculate_cumulative_profit(daily_data,10000)
                self.product_cumulate.append(cumulate)

                max_profit = round(func.get_max_equity(cumulate),2)
                new_profit = round(cumulate[-1][1],2)
                drawdown,drawdown_str = func.calculate_drawdown(new_profit,max_profit)

                product_info = {'symbol':product,'stg':func.get_stg_str(product_data[0][2]),'max':max_profit,'profit':new_profit,'rate':"%.2f"%(cumulate[-1][1]/10000),'drawdown':drawdown_str}
                self.product_value.append(product_info) #记录产品信息

                print("%s权益统计完成"%product,product_info)

            result = func.sum_cumulative_rights(self.product_cumulate)

            self.plot权益列表(result)
        except Exception as e:
            self.ExceptionThrow(e)

    def plot_candlestick(self,klines,title='CKB'):

        try:
            # 将K线数据转换为DataFrame
            df = pd.DataFrame(klines)
            df.set_index('price_time', inplace=True)
            quotes = []
            for index, row in df.iterrows():
                # 将日期转换为matplotlib的日期格式
                date_num = mdates.date2num(index)
                # 将Decimal转换为浮点数
                open_price = float(row['open'])
                high_price = float(row['high'])
                low_price = float(row['low'])
                close_price = float(row['close'])
                quotes.append([date_num, open_price, high_price, low_price, close_price])

            # 创建图表
            fig, ax = plt.subplots(figsize=(10, 5))

            # 绘制K线图
            candlestick_ohlc(ax, quotes, width=1, colorup='green', colordown='red', alpha=1)

            # 设置日期格式
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())

            # 设置标题
            plt.title(title)
            # 显示图表
            plt.show()
        except Exception as e:
            self.ExceptionThrow(e)

    def plot_daily_kline_with_max_close(self,klines_30m, window=20):
        """
        绘制日线K线图，并添加过去指定天数的最高收盘价线
        :param klines_30m: 30分钟K线数据的列表，每个元素包含开盘、最高、最低、收盘价格和datetime类型的price_time
        :param window: 过去多少天的最高收盘价线
        """
        # 确保数据时间排序
        klines_30m.sort(key=lambda x: x['price_time'])

        # 将K线数据转换为DataFrame
        df_30m = pd.DataFrame(klines_30m)
        df_30m.set_index('price_time', inplace=True)

        # 计算日线数据
        df_daily = df_30m.resample('D').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'})

        # 计算过去window天的最高收盘价
        rolling_max_close = df_daily['close'].rolling(window=window).max()

        # 创建一个额外的图表元素（addplot）来表示过去window天的最高收盘价线
        apd = mpf.make_addplot(rolling_max_close, color='red', width=0.75, label='20-Day Max Close')

        # 绘制K线图并添加过去window天的最高收盘价线
        mpf.plot(df_daily, type='candle', addplot=apd, style='charles', title='Daily K-Line Chart with Max Close Line',
                 ylabel='Price')


    def ShowKLines(self,symbol="ONDO"):

        klines = self.dc.QueryProductDataKLinesGateio(symbol)

        if klines == 0 or len(klines) == 0:
            print("k线数据没有找到，请检查：%s"%symbol)

        day_klines = func.minute_to_daily(klines)
        self.plot_candlestick(day_klines,symbol)

    def GetAcctInfo(self):
        acct_id = 55
        acct = self.dc.QueryGateAcctInfoByID(acct_id)
        return acct


    def ShowStgLatestInfo(self):
        data_list = []
        if len(self.product_value)==0:
            print("no data, 请先运行策略运算")
        else:
            for itor in self.product_value:
                data = [itor['symbol'],itor['stg'],itor['profit'],itor['max'],itor['rate'],itor['drawdown']]
                data_list.append(data)

        return data_list

    def GetAccountList(self):
        """
        获取可用账户列表
        """
        try:
            # 从acct_stg_future_gateio和acct_info表获取账户信息
            accounts = self.dc.QueryAllAcctFollowFutureGateio()
            account_list = []
            for acct in accounts:
                # 注意：accounts 返回的是元组，需要按索引访问
                acct_id = acct['acct_id']  # 第一个元素是 acct_id
                #acct_info = self.dc.QueryGateAcctInfoByID(acct_id)
                #if acct_info:
                    # 格式：账户ID - 账户名称
                account_list.append(f"{acct_id} - {acct['name']}")  # 使用 'name' 而不是 'acct_name'
            
            print(f"找到 {len(account_list)} 个账户")  # 添加日志
            return account_list
        except Exception as e:
            self.ExceptionThrow(e)
            print(f"获取账户列表失败: {str(e)}")  # 添加错误日志
            return []

    def SetAccount(self, acct_id):
        """
        设置当前账户
        """
        try:
            acct_info = self.dc.QueryGateAcctInfoByID(acct_id)
            if acct_info:
                obj = ExchangeGatieio()
                self.exchange = obj.GetExchangeGateioFuture(acct_info)
                self.spotexchange = obj.GetExchangeGateioSpot(acct_info)
                return True
            return False
        except Exception as e:
            self.ExceptionThrow(e)
            return False

class MyApplication:
    def __init__(self, window):
        self.window = window
        self.window.title("Gate.io 交易监控系统")
        self.market = MarketInfo()
        
        # 设置窗口的初始大小和位置
        self.window.geometry("1200x800")
        self.window.minsize(1000, 600)
        
        # 创建主框架
        self.create_main_layout()
        
        self.current_account = None  # 添加当前账户标记
        self.auto_refresh = False
        self.refresh_interval = 30000  # 30秒刷新一次
        self.data_queue = Queue()  # 添加数据队列
        self.start_loading_animation()  # 添加加载动画
        
    def create_main_layout(self):
        """创建主布局"""
        # 顶部工具栏 - 第一行
        self.create_toolbar_frame()
        
        # 账户信息区 - 第二行
        self.create_account_frame()
        
        # 持仓信息区 - 第三行
        self.create_position_frame()
        
    def create_toolbar_frame(self):
        """创建顶部工具栏"""
        toolbar = ttk.LabelFrame(self.window, text="操作区", padding=5)
        toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # 账户选择区
        account_frame = ttk.Frame(toolbar)
        account_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(account_frame, text="账户：").pack(side=tk.LEFT)
        account_list = self.market.GetAccountList()
        self.account_combo = ttk.Combobox(account_frame, values=account_list, width=20)
        self.account_combo.pack(side=tk.LEFT, padx=5)
        self.account_button = ttk.Button(account_frame, text="确认选择", 
                                       command=self.confirm_account, 
                                       style='primary.TButton')
        self.account_button.pack(side=tk.LEFT, padx=5)
        
        if account_list:  # 如果有账户，默认选择第一个
            self.account_combo.set(account_list[0])
        
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        
        # 币种选择区
        select_frame = ttk.Frame(toolbar)
        select_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(select_frame, text="币种：").pack(side=tk.LEFT)
        product_list = self.market.GetProductList()
        self.combo_box = ttk.Combobox(select_frame, values=product_list, width=10)
        self.combo_box.pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        
        # K线查看区
        kline_frame = ttk.Frame(toolbar)
        kline_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(kline_frame, text="显示K线", command=self.method1, style='primary.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(kline_frame, text="显示净值曲线", command=self.method2, style='info.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        
        # 账户信息区
        account_frame = ttk.Frame(toolbar)
        account_frame.pack(side=tk.LEFT, padx=20)
        ttk.Button(account_frame, text="显示账户信息", command=self.method3, style='success.TButton').pack(side=tk.LEFT, padx=5)
        
        ttk.Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill='y', padx=10)
        
        # 资金操作区
        money_frame = ttk.Frame(toolbar)
        money_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Label(money_frame, text="金额：").pack(side=tk.LEFT)
        self.entry_money = ttk.Entry(money_frame, width=12)
        self.entry_money.pack(side=tk.LEFT, padx=5)
        ttk.Button(money_frame, text="转入资金", command=self.transfer_money, style='success.TButton').pack(side=tk.LEFT, padx=5)
        
        # 添加自动刷新控制
        refresh_frame = ttk.Frame(toolbar)
        refresh_frame.pack(side=tk.LEFT, padx=20)
        
        self.auto_refresh_var = tk.BooleanVar()
        ttk.Checkbutton(refresh_frame, text="自动刷新", 
                       variable=self.auto_refresh_var,
                       command=self.toggle_auto_refresh).pack(side=tk.LEFT)
                       
        # 添加导出按钮
        export_frame = ttk.Frame(toolbar)
        export_frame.pack(side=tk.LEFT, padx=20)
        
        ttk.Button(export_frame, text="导出数据", 
                  command=self.export_data,
                  style='info.TButton').pack(side=tk.LEFT)
                  
    def toggle_auto_refresh(self):
        """
        切换自动刷新状态
        """
        self.auto_refresh = self.auto_refresh_var.get()
        if self.auto_refresh:
            self.schedule_refresh()
        
    def schedule_refresh(self):
        """
        安排下一次刷新
        """
        if self.auto_refresh and self.current_account is not None:
            self.method3()  # 刷新数据
            self.window.after(self.refresh_interval, self.schedule_refresh)
        
    def create_account_frame(self):
        """创建账户信息区"""
        account_frame = ttk.LabelFrame(self.window, text="账户信息", padding=5)
        account_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 账户余额
        self.value_label = ttk.Label(account_frame, text="账户余额：0.00")
        self.value_label.pack(side=tk.LEFT, padx=20)
        
        # 净值总和
        self.summary_label = ttk.Label(account_frame, text="净值总和：0.00")
        self.summary_label.pack(side=tk.LEFT, padx=20)
        
    def create_position_frame(self):
        """创建持仓信息区"""
        position_frame = ttk.LabelFrame(self.window, text="持仓信息", padding=5)
        position_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 创建表格
        columns = ("序号","名称", "杠杆倍数", "数量", "净值", "浮盈")
        self.tree = ttk.Treeview(position_frame, columns=columns, show="headings")
        
        # 设置列
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")
            
        # 创建滚动条
        scrollbar = ttk.Scrollbar(position_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 放置表格和滚动条
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        
    def update_table(self, data):
        """更新表格数据"""
        # 清空现有数据
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        total_pnl = 0  # 总浮盈
        
        # 插入数据
        for item in data:
            symbol = item[0]
            leverage = item[1]
            size = item[2]
            value = item[3]
            
            # 计算浮盈
            try:
                contract = symbol + "_USDT"
                position_info = self.market.exchange.get_position("usdt", contract)
                entry_price = float(position_info.entry_price) if position_info.entry_price else 0
                current_price = float(position_info.mark_price) if position_info.mark_price else 0
                
                coin_info = self.market.GetCoinInfoFuture(symbol)
                contract_size = float(coin_info['cs'])
                
                if entry_price > 0 and size != 0:
                    if size > 0:
                        pnl = abs(size) * contract_size * (current_price - entry_price)
                    else:
                        pnl = abs(size) * contract_size * (entry_price - current_price)
                    
                    total_pnl += pnl
                    pnl_str = f"{pnl:+,.2f}"
                else:
                    pnl_str = "0.00"
                    
            except Exception as e:
                print(f"计算{symbol}浮盈失败: {str(e)}")
                pnl_str = "N/A"
                
            self.tree.insert("", "end", values=(symbol, leverage, size, value, pnl_str))
            
        # 添加总计行
        self.tree.insert("", "end", values=("总计", "", "", "", f"{total_pnl:+,.2f}"))

    def method1(self):
        try:
            symbol = self.combo_box.get()
            print("选择了：",symbol)
            ret = func.check_and_convert_to_uppercase(symbol)
            self.market.ShowKLines(ret)
        except Exception as e:
            messagebox.showinfo("异常","输入非法：币名字应该是纯大写字母%s"%e)

    def method2(self):
        self.market.ShowStgInfo()

    def method3(self):
        """
        显示账户信息 - 多线程版本
        """
        if not hasattr(self.market, 'exchange') or self.market.exchange is None:
            messagebox.showwarning("警", "请先选择账户")
            return
        
        # 显示加载动画
        self.show_loading(True)
        
        # 禁用按钮，防止重复点击
        for widget in self.window.winfo_children():
            if isinstance(widget, ttk.Button):
                widget.configure(state='disabled')
        
        # 启动数据获取线程
        thread = threading.Thread(target=self.fetch_account_data)
        thread.daemon = True  # 设置为守护线程
        thread.start()
        
        # 启动数据处理检查
        self.window.after(100, self.check_data_queue)

    def fetch_account_data(self):
        """
        在新线程中获取账户数据
        """
        try:
            fa, data = self.market.ListAcctInfo()
            self.data_queue.put(('success', (fa, data)))
        except Exception as e:
            self.data_queue.put(('error', str(e)))

    def check_data_queue(self):
        """
        检查数据队列并更新UI
        """
        try:
            if not self.data_queue.empty():
                status, data = self.data_queue.get()
                
                if status == 'success':
                    fa, account_data = data
                    self.create_table(account_data)
                    self.create_value_display(fa)
                    self.create_summary(account_data)
                else:
                    messagebox.showerror("错误", f"获取数据失败: {data}")
                
                # 恢复按钮状态
                for widget in self.window.winfo_children():
                    if isinstance(widget, ttk.Button):
                        widget.configure(state='normal')
                
                # 隐藏加载动画
                self.show_loading(False)
            else:
                # 继续检查队列
                self.window.after(100, self.check_data_queue)
        except Exception as e:
            messagebox.showerror("错误", f"处理数据失败: {str(e)}")
            # 恢复按钮状态
            for widget in self.window.winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.configure(state='normal')
            # 隐藏加载动画
            self.show_loading(False)

    def show_table(self):
        # 创建一个新的窗口来显示表格
        table_window = tk.Toplevel(self.window)
        table_window.title("表格显示")
        table_window.geometry("600x400")  # 设置表格窗口的大小

        # 在新窗口中创建表格
        self.create_table_1(table_window)

    def transfer_money(self):
        money = float(self.entry_money.get())
        acct = self.market.GetAcctInfo()
        wallet = self.market.GetWallet(acct)
        self.market.TransferMoney(wallet,-1*money)

    def create_table_1(self, window):
        # 创建表格控件
        columns = ("名称", "多空", "最新盈利", "最大盈利","盈利率","最大回撤")
        tree = ttk.Treeview(window, columns=columns, show="headings")

        # 定义表头
        for col in columns:
            tree.heading(col, text=col)

        # 定义列的宽度和对齐方式
        for col in columns:
            tree.column(col, width=100, anchor="center")

        # 插入数据到表格

        data = self.market.ShowStgLatestInfo()


        for row in data:
            tree.insert("", "end", values=row)

        # 打包表格控件
        tree.pack(side="top", fill="both", expand=True)


    def create_table(self, data):
        # 如果表格控件已存在，则先清空现有数据
        if hasattr(self, 'tree'):
            for item in self.tree.get_children():
                self.tree.delete(item)
        else:
            # 创建表格控件，添加序号列
            self.tree = ttk.Treeview(self.window, columns=("序号", "名称", "杠杆倍数", "数量", "净值", "浮盈"), show="headings")
            self.tree.heading("序号", text="序号")
            self.tree.heading("名称", text="名称")
            self.tree.heading("杠杆倍数", text="杠杆倍数")
            self.tree.heading("数量", text="数量")
            self.tree.heading("净值", text="净值")
            self.tree.heading("浮盈", text="浮盈")

            # 创建滚动条
            scrollbar = ttk.Scrollbar(self.window, orient="vertical", command=self.tree.yview)
            self.tree.configure(yscrollcommand=scrollbar.set)

            # 放置滚动条和表格
            scrollbar.pack(side="right", fill="y")
            self.tree.pack(side="left", fill="both", expand=True)

            # 调整列宽以适应内容
            self.tree.column("序号", width=50, anchor="center")  # 序号列宽度较小
            self.tree.column("名称", width=100, anchor="center")
            self.tree.column("杠杆倍数", width=100, anchor="center")
            self.tree.column("数量", width=100, anchor="center")
            self.tree.column("净值", width=100, anchor="center")
            self.tree.column("浮盈", width=100, anchor="center")

        # 插入新数据到表格，包括浮盈信息
        for index, item in enumerate(data, 1):  # 使用 enumerate 添加序号
            symbol = item[0]
            leverage = item[1]
            size = item[2]
            value = round(float(item[3]), 2)  # 修改这里：净值四舍五入保留2位小数
            
            # 计算浮盈
            try:
                # 获取持仓均价和当前价格
                contract = symbol + "_USDT"
                position_info = self.market.exchange.get_position("usdt", contract)
                entry_price = float(position_info.entry_price) if position_info.entry_price else 0
                current_price = float(position_info.mark_price) if position_info.mark_price else 0
                
                # 获取合约面值
                coin_info = self.market.GetCoinInfoFuture(symbol)
                contract_size = float(coin_info['cs'])  # 合约面值
                
                if entry_price > 0 and size != 0:
                    # 计算浮盈 = 持仓数量 * 合约面值 * (当前价格 - 开仓均价)
                    if size > 0:  # 多仓
                        pnl = abs(size) * contract_size * (current_price - entry_price)
                    else:  # 空仓
                        pnl = abs(size) * contract_size * (entry_price - current_price)
                        
                    pnl_str = f"{pnl:,.2f}"
                    # 添加颜色标记
                    if pnl > 0:
                        pnl_str = "+" + pnl_str
                else:
                    pnl_str = "0.00"
                    
            except Exception as e:
                print(f"计算{symbol}浮盈失败: {str(e)}")
                pnl_str = "N/A"
                
            self.tree.insert("", "end", values=(index, symbol, leverage, size, value, pnl_str))

    def create_value_display(self,fa):
        if hasattr(self, 'value_label'):
            self.value_label.config(text=f"账户余额：{round(fa,2)}")
        else:

            # 创建一个标签来显示数值
            self.value_label = ttk.Label(self.window, text=f"账户余额：{round(fa,2)}")
            self.value_label.pack(pady=5)



    def create_summary(self, data):
        """创建汇总信息显示"""
        if hasattr(self, 'summary_label'):
            # 计算净值列的总和
            total_net_value = round(sum(float(item[3]) for item in data), 2)  # 修改这里：总净值四舍五入保留2位小数
            
            # 计算总浮盈
            total_pnl = 0
            for item in data:
                symbol = item[0]
                size = float(item[2])
                try:
                    contract = symbol + "_USDT"
                    position_info = self.market.exchange.get_position("usdt", contract)
                    entry_price = float(position_info.entry_price) if position_info.entry_price else 0
                    current_price = float(position_info.mark_price) if position_info.mark_price else 0
                    
                    coin_info = self.market.GetCoinInfoFuture(symbol)
                    contract_size = float(coin_info['cs'])
                    
                    if entry_price > 0 and size != 0:
                        if size > 0:  # 多仓
                            pnl = abs(size) * contract_size * (current_price - entry_price)
                        else:  # 空仓
                            pnl = abs(size) * contract_size * (entry_price - current_price)
                        total_pnl += pnl
                except Exception as e:
                    print(f"计算{symbol}浮盈失败: {str(e)}")

            # 更新显示文本，添加浮盈信息
            summary_text = f"净值总和：{total_net_value}    浮盈：{total_pnl:+,.2f}"
            self.summary_label.config(text=summary_text)
        else:
            # 计算净值列的总和
            total_net_value = round(sum(float(item[3]) for item in data), 2)  # 修改这里：总净值四舍五入保留2位小数
            
            # 计算总浮盈（与上面相同的计算逻辑）
            total_pnl = 0
            for item in data:
                symbol = item[0]
                size = float(item[2])
                try:
                    contract = symbol + "_USDT"
                    position_info = self.market.exchange.get_position("usdt", contract)
                    entry_price = float(position_info.entry_price) if position_info.entry_price else 0
                    current_price = float(position_info.mark_price) if position_info.mark_price else 0
                    
                    coin_info = self.market.GetCoinInfoFuture(symbol)
                    contract_size = float(coin_info['cs'])
                    
                    if entry_price > 0 and size != 0:
                        if size > 0:  # 多仓
                            pnl = abs(size) * contract_size * (current_price - entry_price)
                        else:  # 空仓
                            pnl = abs(size) * contract_size * (entry_price - current_price)
                        total_pnl += pnl
                except Exception as e:
                    print(f"计算{symbol}浮盈失败: {str(e)}")

            # 创建标签，显示净值总和和浮盈
            summary_text = f"净值总和：{total_net_value}    浮盈：{total_pnl:+,.2f}"
            self.summary_label = ttk.Label(self.window, text=summary_text)
            self.summary_label.pack(pady=5)

    def confirm_account(self):
        """
        确认选择账户
        """
        try:
            selected = self.account_combo.get()
            if not selected:
                messagebox.showwarning("警告", "请先选择账户")
                return
            
            acct_id = int(selected.split(' - ')[0])
            
            if self.market.SetAccount(acct_id):
                self.current_account = acct_id  # 保存当前账户ID
                messagebox.showinfo("成功", f"已切换到账户: {selected}")
                # 刷新账户信息显示
                self.method3()
                # 禁用账户选择框，直到用户点击"切换账户"
                self.account_combo.configure(state='disabled')
                # 修改按钮文本
                self.account_button.configure(text="切换账户", command=self.switch_account)
            else:
                messagebox.showerror("错误", "账户切换失败")
            
        except Exception as e:
            messagebox.showerror("错误", f"账户切换异常: {str(e)}")

    def switch_account(self):
        """
        切换到其他账户
        """
        self.account_combo.configure(state='normal')
        self.account_combo.set('')  # 清空选择
        self.account_button.configure(text="确认选择", command=self.confirm_account)
        self.current_account = None

    def export_data(self):
        """
        导出当前数据到Excel
        """
        if not self.current_account:
            messagebox.showwarning("警告", "请先选择账户")
            return
            
        try:
            from datetime import datetime
            import pandas as pd
            
            # 获取当前数据
            fa, data = self.market.ListAcctInfo()
            
            # 创建DataFrame
            df = pd.DataFrame(data, columns=["币种", "杠杆倍数", "数量", "净值", "浮盈"])
            
            # 生成文件名
            filename = f"account_{self.current_account}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # 保存到Excel
            df.to_excel(filename, index=False)
            messagebox.showinfo("成功", f"数据已导出到: {filename}")
            
        except Exception as e:
            messagebox.showerror("错误", f"导出失败: {str(e)}")

    def start_loading_animation(self):
        """
        创建加载动画标签
        """
        self.loading_label = ttk.Label(self.window, text="Loading...")
        self.loading_label.pack_forget()  # 初始时隐藏

    def show_loading(self, show=True):
        """
        显示/隐藏加载动画
        """
        if show:
            self.loading_label.pack(pady=5)
            self.window.update()
        else:
            self.loading_label.pack_forget()

if __name__ == '__main__':
    # 创建窗口
    window = tk.Tk()

    # 创建类的实例
    app = MyApplication(window)

    # 运行GUI事件循环
    window.mainloop()
