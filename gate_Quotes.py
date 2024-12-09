#!/user/bin/env python3
# -*- coding: utf-8 -*-

# 获取行情信息的专用定时程序，每30分钟检索数据库，找到数据库中的产品列表，填写到 product 表中

#
import datetime
import time, math
from BASECLASS.gateiobase import ExchangeGatieio,Stg
from decimal import Decimal
import schedule
from BASECLASS.configfile import ReadConfigFile
from COMM.dboper import  MyDBConn
from COMM import commFunctions as func
import requests
import threading

class QuotesManager:
    def __init__(self):
        self.running = True
        self.last_run_time = None
        
    def setup_schedule(self):
        """
        设置定时任务
        """
        schedule.clear()  # 清除所有现有任务
        
        # 每30分钟执行一次行情获取和策略计算
        for minute in ['00', '30']:
            schedule.every().hour.at(f':{minute}').do(
                self.run_job_with_timeout, 
                self.get_quotes_and_calculate
            )
            
    def run_job_with_timeout(self, job_func, timeout=300):
        """
        使用超时控制运行任务
        """
        def wrapper():
            try:
                # 创建任务线程
                job_thread = threading.Thread(target=job_func)
                job_thread.daemon = True
                job_thread.start()
                
                # 等待任务完成或超时
                job_thread.join(timeout=timeout)
                
                if job_thread.is_alive():
                    print(f"任务 {job_func.__name__} 执行超时")
                    return False
                    
                self.last_run_time = datetime.datetime.now()
                return True
                
            except Exception as e:
                print(f"任务执行异常: {str(e)}")
                return False
                
        return wrapper
        
    def get_quotes_and_calculate(self):
        """
        获取行情数据并计算策略
        """
        try:
            # 原有的行情获取和策略计算代码
            self.get_quotes()
            self.calculate_strategy()
            
        except Exception as e:
            print(f"行情获取和策略计算失败: {str(e)}")
            
    def run_scheduler(self):
        """
        改进的调度器运行函数
        """
        while self.running:
            try:
                # 添加超时控制
                schedule.run_pending()
                
                # 检查是否有未完成的任务
                current_jobs = schedule.get_jobs()
                for job in current_jobs:
                    if (self.last_run_time and 
                        (datetime.datetime.now() - self.last_run_time).total_seconds() > 1800):  # 30分钟超时
                        print("任务执行超时，重新初始化...")
                        self.reinitialize()
                        
                # 使用更短的睡眠时间，提高响应性
                for _ in range(10):  # 将1秒分成10次100ms的检查
                    if not self.running:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                print(f"调度器异常: {str(e)}")
                time.sleep(5)
                
                # 尝试重新初始化调度器
                try:
                    self.reinitialize()
                except Exception as reinit_e:
                    print(f"重新初始化调度器失败: {str(reinit_e)}")
                    
    def reinitialize(self):
        """
        重新初始化所有组件
        """
        try:
            schedule.clear()
            self.setup_schedule()
            # 重新初始化数据库连接等资源
            self.init_resources()
        except Exception as e:
            print(f"重新初始化失败: {str(e)}")
            
    def stop(self):
        """
        停止调度器
        """
        self.running = False
        
    def start(self):
        """
        启动行情服务
        """
        try:
            print("启动行情服务...")
            
            # 初始化资源
            self.init_resources()
            
            # 设置定时任务
            self.setup_schedule()
            
            # 立即执行一次
            self.get_quotes_and_calculate()
            
            # 启动调度器
            self.run_scheduler()
            
        except Exception as e:
            print(f"启动行情服务失败: {str(e)}")
            raise e
            
    def init_resources(self):
        """
        初始化资源
        """
        try:
            # 初始化数据库连接
            # 初始化API客户端
            # 初始化其他必要资源
            pass
        except Exception as e:
            print(f"初始化资源失败: {str(e)}")
            raise e

class TickInfo(object):



    def __init__(self):

        try:
            self.config = ReadConfigFile("gate_config.ini")
            self.dc = MyDBConn(int(self.config.read_info("api","dbsource")) )

            self.exchange = self.GetPubExchange()
            self.day_k_nums = 48
            self.money = 10000
            self.coin_info_list = []

            self.server = self.config.read_info("api","quotesisserver")
            self.timeout = int(self.config.read_info("api","timeout"))
            self.allow_run = True

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
        return exchange

    def QueryCandleStick(self,symbol,start, end, limit):

    ### 注意：0-29分，获得k线，只能取上一个小时30分的，系统会返回���但数据都不准确。30-59分，获得k线，只能取当前整数小时的

        candle_list = []
        if start <= end:
            end = func.get_last_half_hour_timestamp()
            if start > end:
                print("无最新行情数据...")
                return candle_list

            count = func.count_time_points(start,end)
            from_timestamp = start

            while count > 0:
                if count > limit:
                    end_timestamp = func.add_minutes_to_timestamp(from_timestamp,limit*30)
                    count = count - limit
                else:
                    end_timestamp = end
                    count = 0

                candles = self.exchange.list_futures_candlesticks("usdt", symbol + "_USDT", _from=from_timestamp,
                                                                      to=end_timestamp, interval='30m')

                candle_list.extend(candles)

                print("fecth:",func.timestamp_to_datetime(from_timestamp),func.timestamp_to_datetime(end_timestamp), len(candles),count )
                from_timestamp = func.add_minutes_to_timestamp(end_timestamp, 30)
        return candle_list

    def LoadTickInfo(self):

        try:
            print("多线程启动，开始读取信号")
            # 获得产品列表
            product_list = self.LoadAllProduct()

            # 获得产品历史行情
            k = 1
            len_pro = len(product_list)
            for product in product_list:
                symbol = product

                max_fetch = 2000



                begin_time = self.dc.QueryMaxDatePrice30MGateio(symbol)
                if begin_time == "":
                    # 起始时间
                    from_datetime = "2024-1-1 00:00:00"
                    from_timestamp = func.datetime_str_to_timestamp(from_datetime, '%Y-%m-%d %H:%M:%S')
                else:
                    from_timestamp = func.add_minutes_to_timestamp(begin_time[0].timestamp(), 30) #加上30分钟的新时间

                end_timestamp = func.datetime_to_timestamp(datetime.datetime.now())


                candles_list = self.QueryCandleStick(symbol,from_timestamp,end_timestamp,max_fetch)
                lenofcandles = len(candles_list)
                if lenofcandles == 0:
                    print("%s 当前没有最新行情数据 当前 %d - %d \n" % (symbol,len_pro,k))
                else:
                    print("获取品种%s行情，本次更新记录数：%d 条 当前 %d - %d \n" % (symbol, lenofcandles,len_pro,k) )

                    self.dc.InsertPriceDataGateio(symbol, candles_list)
                k = k+1

                self.LoadStratageAll(symbol)


            print("\n行情装载与策略运算工作完成...30M后启动下一次"+time.strftime('%y-%m-%d %H:%M:%S')+"\n\n")
        except Exception as e:
            self.ExceptionThrow(e)
        # 校验数据

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

    def LoadAllProduct(self):
        try:

            #从表格中，读取所有有效的组合

            #分解组合
            product_list = self.dc.QueryProductListFutureGateioAll()
            from COMM.commFunctions import remove_duplicates
            product_list = remove_duplicates(product_list)

            return product_list


        except Exception as e:
            self.ExceptionThrow(e)

    def LoadStratage(self, symbol, stratage):
        # 对当前品种计算策略
        try:

            stratage_last = self.dc.QueryStratageDetailLatestGateio(symbol, stratage['stg_id'])

            # 找到策略最后时间后，开始的所有价格k线
            # 为了提高计算效率，要将收盘数据从策略开始往前找齐win_days(窗口)
            coin_info = self.GetCoinInfoFuture(symbol)
            symbol_cval = coin_info['cs']
            if symbol_cval == 0:
                raise Exception("获取信息出错，请检查,symbol_cval == 0")
                symbol_cval = 1

            if stratage_last == 0:
                print("策略数据为空，重新计算")
                symbol_data = self.dc.QueryProductDataAllGateio(symbol)

                if len(symbol_data) == 0:
                    raise Exception("QueryProductDataAllGateio 没有商品行情数据")
                # 先获取最后一个策略的数据
                top = Stg.ZERO
                mid = Stg.ZERO
                bot = Stg.MAXINT
                num = Stg.ZERO
                stg = Stg.ZERO

                last_close = Decimal(symbol_data[0][0])

                # 先获取最后一个策略的数据
                last_stg_detail = {'top':Stg.ZERO, 'mid': Stg.ZERO, 'bot': Stg.MAXINT, 'num': Stg.ZERO, 'stg': Stg.ZERO, 'rate': Stg.ZERO, 'winner': Stg.ZERO,
                                   'stg_time': symbol_data[0][1], 'last_close': symbol_data[0][0]}

                # 计算用来生成top/bot的数据

                close_time_origin = [x[1].strftime("%Y-%m-%d %H:%M:%S") for x in symbol_data]
                close_price_origin = [x[0] for x in symbol_data]
                location_start = close_time_origin.index(last_stg_detail['stg_time'].strftime("%Y-%m-%d %H:%M:%S"))

            else:
                stratage_last_time = stratage_last['stratage_time']

                str_time = stratage_last_time.strftime("%Y-%m-%d %H:%M:%S")  # 为了方便调试，列出时间
                symbol_data = self.dc.QueryProductDataPartGateio(symbol, stratage_last_time,
                                                           stratage['winsize'] + 1)  # 增加一天，用以排除特殊情况，不够时间的问题
                if str_time == symbol_data[0][1]:
                    print("策略已经是最新，跳过该策略对应的品种，%s " % symbol)
                    return 0
                else:
                    print("策略 %s 更新中..." % (stratage['name']))

                # 先获取最后一个策略的数据
                top = stratage_last['top']
                mid = stratage_last['mid']
                bot = stratage_last['bot']
                num = stratage_last['num']
                stg = stratage_last['stg']

                stg_time = stratage_last['stratage_time']
                last_close = Decimal(stratage_last['close'])

                # 计算用来生成top/bot的数据

                close_time_origin = [x[1].strftime("%Y-%m-%d %H:%M:%S") for x in symbol_data]
                close_price_origin = [x[0] for x in symbol_data]
                location_start = close_time_origin.index(stg_time.strftime("%Y-%m-%d %H:%M:%S") ) + 1

            if location_start < 0:
                raise Exception("数据异常location_start")
            else:
                close_price = [x[0] for x in symbol_data[location_start:]]
                close_time = [x[1] for x in symbol_data[location_start:]]

            data_len = len(close_price)

            top_list = []
            bot_list = []
            mid_list = []

            stg_list = []
            num_list = []
            winner_list = []
            rate_list = []

            max_close = 0
            min_close = 0
            for i in range(0, data_len):
                k_close = Decimal(close_price[i])
                if k_close<=0:
                    raise Exception("行情数据异常k_close")
                # 如果遇到跨日，重新计算top���mid，除此之外，直接等于上一个
                if close_time[i].hour == 0 and close_time[i].minute == 0:
                    # 如果跨天
                    start_k = int(location_start + i - stratage['winsize'] * self.day_k_nums)
                    end_k = int(location_start + i)
                    last_win_day_close = close_price_origin[start_k:end_k]
                    if start_k >= 0:
                        max_close = max(last_win_day_close)
                        min_close = min(last_win_day_close)

                    top = max_close
                    bot = min_close
                    mid = (top + bot) / 2

                    top_list.append(top)
                    bot_list.append(bot)
                    mid_list.append(mid)

                else:
                    if i > 0:
                        top = top_list[i - 1]
                        bot = bot_list[i - 1]
                        mid = mid_list[i - 1]

                    top_list.append(top)
                    bot_list.append(bot)
                    mid_list.append(mid)


                #如果上一组数据显示"没有持仓"
                if stg == Stg.EMPTY or stg == Stg.LONGQUIT or stg == Stg.SHORTQUIT:

                    if min_close == 0 and max_close == 0 and top == 0:  # 在没有数据前，不操作
                        num_list.append(0)
                        stg = Stg.EMPTY
                        stg_list.append(stg)
                    else:
                        # 开多
                        if k_close > top:

                            stg = Stg.LONGIN
                            stg_list.append(stg)
                            decimal_data = Decimal(symbol_cval) * k_close
                            num = math.floor(func.safe_divide(self.money, decimal_data))
                            num_list.append(num)  # 张数
                        # 开空
                        elif k_close < bot:

                            stg = Stg.SHORTIN
                            stg_list.append(stg)
                            decimal_data = Decimal(symbol_cval)*k_close
                            num = math.floor(func.safe_divide(self.money,decimal_data))
                            num_list.append(num)

                        else:
                            num_list.append(0)
                            stg_list.append(Stg.EMPTY)

                    #开仓的k线位置，不计算盈利金额和盈利比例
                    rate_list.append(0)
                    winner_list.append(0)

                elif stg == Stg.SHORTIN or stg == Stg.SHORTHOLD:
                    if k_close <= mid:
                        stg = Stg.SHORTHOLD
                        stg_list.append(stg)
                        rate = func.safe_divide(last_close - k_close ,last_close)
                        rate_list.append(rate)
                        num_list.append(num)
                        winner = Decimal(rate) * Decimal(num) * Decimal(symbol_cval) * last_close
                        winner_list.append(winner)

                    if k_close > mid:
                        stg = Stg.SHORTQUIT
                        stg_list.append(stg)
                        rate = func.safe_divide(last_close - k_close ,last_close)
                        rate_list.append(rate)

                        winner = Decimal(rate) * Decimal(num) * Decimal(symbol_cval) * last_close
                        winner_list.append(winner)
                        num = 0
                        num_list.append(num)
                elif stg == Stg.LONGIN or stg == Stg.LONGHOLD:
                    if k_close >= mid:
                        stg = Stg.LONGHOLD
                        stg_list.append(stg)
                        rate = func.safe_divide(k_close - last_close,last_close)
                        rate_list.append(rate)
                        num_list.append(num) #持仓数保持不变
                        winner = Decimal(rate) * Decimal(num) * Decimal(symbol_cval) * last_close
                        winner_list.append(winner)

                    if k_close < mid:
                        stg = Stg.LONGQUIT
                        stg_list.append(stg)
                        rate = func.safe_divide(k_close - last_close,last_close)
                        rate_list.append(rate)

                        winner = Decimal(rate) * Decimal(num) * Decimal(symbol_cval) * last_close
                        winner_list.append(winner)
                        num = 0
                        num_list.append(num)

                last_close = Decimal(k_close)


            if len(close_price)>0:
                self.dc.InsertStratageDetailGateio (stratage['stg_id'], symbol, close_price, close_time, top_list, mid_list,
                                             bot_list, stg_list, num_list, rate_list, winner_list)
                self.dc.UpdateStratageLatestGate(stratage['stg_id'], symbol, close_time[-1],num_list[-1], stg_list[-1],close_price[-1],
                                             rate_list[-1], winner_list[-1],top_list[-1], mid_list[-1],bot_list[-1])
        except Exception as e:
            self.ExceptionThrow(e)


        return 0

    def LoadStratageAll(self, symbol):
        # 装载完品种后，把各类参数策略都计算一遍
        stg = {'name': 'GD20', 'winsize': 20, 'stg_id': 4}

        ret = self.LoadStratage(symbol, stg)

        if ret != 0:
            print("加载策略遇到错误，错误原因：", ret)

    def SendWarning(self):

        try:
            title = 'Gateio-CTA 行情服务器故障'
            mydata = {
                'text': title,
                'desp': "速速检查106服务器"
            }

            #admin 1 xiaoj
            url = "http://wx.xtuis.cn/BDGGZgR856AueOk6JXoCERIyi.send"
            requests.post(url, data=mydata)

            #admin 2 gy
            url = "http://wx.xtuis.cn/DOyVyJTsYb8UfxLV4qtWPr0t6.send"
            requests.post(url, data=mydata)
        except Exception as e:
            self.ExceptionThrow(e)



def job():

    program = TickInfo()
    # 如果是服务器，则自动启动执行，并且向数据库写入正常运转的信息
    if program.server == '1':
        try:
            program.allow_run = True
            program.dc.UpdateWatchApp("future_quotes_gateio")
        except Exception as e:
            program.ExceptionThrow(e)
    else:
        # 如果是备份机，先检查服务器的信息，如果数据库无法访问、信息已经5分钟未更新，则自动启动
        try:
            dbback = int(program.config.read_info("api","quotesdbback"))
            remote_dc = MyDBConn(dbback)  # gate - 10 okx - 12 binance - 13
            ret = remote_dc.QueryWathcApp("future_quotes_gateio")
            dt1 = datetime.datetime.now()
            dt2 = ret['status_time']
            timedelta = dt1 - dt2
            if timedelta.total_seconds() > int(program.timeout):
                program.allow_run = True
                remote_dc.UpdateWatchAppBack("future_quotes_gateio")
                program.SendWarning()
            else:
                program.allow_run = False
                print("服务器运行正常，备份程序挂起，1分钟后再检查...")
                # 如果服务器有反馈了，就继续阻塞自己
        except Exception as e:
            print(e)  # 远程数据库访问遇到故障，立马启动
            program.allow_run = True

    if program.allow_run:

        threading.Thread(target=program.LoadTickInfo).start()

        #program.LoadAllProduct()


if __name__ == '__main__':


    job()


    schedule.every().hour.at(':30').do(job)

    schedule.every().hour.at(':00').do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)



"""
        candles = self.exchange.list_futures_candlesticks("usdt", "CEL" + "_USDT", _from=1726903800,
                                                          to=1726919000, interval='30m')
        for index,itor in enumerate(candles,start=1):
            print(index, itor.c,func.timestamp_to_datetime(itor.t))

        return
"""