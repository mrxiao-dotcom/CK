#!/user/bin/env python3
# -*- coding: utf-8 -*-
import datetime
# 交易同步工具

#
import time, math
from BASECLASS.gateiobase import ExchangeGatieio,Stg
from gate_api import ApiClient, Configuration, FuturesApi, FuturesOrder, Transfer, WalletApi
import schedule
from BASECLASS.configfile import ReadConfigFile
from COMM.dboper import  MyDBConn
from COMM import commFunctions as func
import threading
import requests
import logging

logging.basicConfig(
    filename='trader.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

###
class Trader(object):

    def __init__(self):

        try:
            self.config = ReadConfigFile("gate_config.ini")
            self.dc = MyDBConn(int(self.config.read_info("api","dbsource")))
            
            # 检查数据库连接
            if not self.check_db_connection():
                raise Exception("初始化数据库连接失败")
                
            self.exchange = self.GetPubExchange()
            self.coin_info_list = []
            self.stg_id = 4

            self.server = self.config.read_info("api","traderisserver")
            self.timeout = int(self.config.read_info("api","timeout"))
            self.allow_run = True


        except Exception as e:
            self.ExceptionThrow(e)

    def ExceptionThrow(self, e):
        line = e.__traceback__.tb_frame.f_globals["__file__"] + " 异常发生在(行):%d " % e.__traceback__.tb_lineno + str(e)
        logging.error(line)
        print(time.strftime('%y-%m-%d %H:%M:%S') + "ExceptionThrow" + line + '-------------- \n')

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
    def GetPubExchange(self):
        obj = ExchangeGatieio()
        defaultAcct = int(self.config.read_info("api","pub_acct"))
        acctdata = self.dc.QueryGateAcctInfoByID(defaultAcct)
        exchange = obj.GetExchangeGateioFuture(acctdata)
        self.spotexchange = obj.GetExchangeGateioSpot(acctdata)
        return exchange

    def GetLatestStgInfo(self,product_info):

        stratage_time = func.get_last_half_hour()
        product_list = product_info.split('#')
        product_str = func.join_list_with_comma_quoted(product_list)
        data = self.dc.QueryStratageDetailLatestGateioComb(product_str,stratage_time.strftime('%y-%m-%d %H:%M:%S'),self.stg_id)

        return data

    def SendOrder(self, symbol, amt, coin_info, lever=3):
        """
        发送订单
        :param symbol: 交易对符号
        :param amt: 交易数量
        :param coin_info: 币种信息
        :param lever: 杠杆倍数，默认为3
        """
        try:
            total_amt = abs(amt)
            max_size = coin_info['order_size_max']
            leverage_max = coin_info['leverage_max']

            contract = symbol + "_USDT"
            
            try:
                self.exchange.set_dual_mode("usdt", False)  # False 表示全仓模式
            except Exception as e:
                if "NO_CHANGE" not in str(e):
                    print(f"设置全仓模式失败: {str(e)}")
            
            # 设置杠杆倍数
            actual_leverage = min(lever, leverage_max)
            self.exchange.update_position_leverage("usdt", contract, actual_leverage)

            while (total_amt):  # 分拆下单
                trade_amt = total_amt

                if trade_amt >= max_size:  # 最大交易数量
                    trade_amt = max_size

                total_amt = total_amt - trade_amt

                if amt > 0:
                    coin_num = trade_amt
                    side = 'buy'
                else:
                    coin_num = -1 * trade_amt
                    side = 'sell'

                order = FuturesOrder(contract=contract, size=coin_num, price="0", tif='ioc')
                order = self.exchange.create_futures_order("usdt", order)
                
                if order.status == 'finished':
                    print('交易成功：', contract, "数量:", coin_num, time.strftime('%y-%m-%d %H:%M:%S'))
                    
                    # 记录交易信息
                    try:
                        trade_record = {
                            'acct_id': self.current_account_id,
                            'symbol': symbol,
                            'side': side,
                            'size': abs(coin_num),
                            'price': float(order.fill_price),
                            'leverage': actual_leverage,
                            'trade_time': datetime.datetime.now(),
                            'order_id': order.id,
                            'trade_value': float(order.fill_price) * abs(coin_num) * coin_info['cs'],
                            'fee': 0.0,  # 简化处理，手续费直接记为0
                            'remark': f"Strategy trade: {side.upper()}"
                        }
                        
                        self.dc.InsertTradeRecord(trade_record)
                        
                    except Exception as e:
                        print(f"记录交易信息失败: {str(e)}")
                        self.log_error(e, "记录交易信息失败")

        except Exception as e:
            print(f"交易失败 {symbol} {amt}: {str(e)}")
            self.ExceptionThrow(e)

    def AcctSynch(self):
        try:
            print("\n #################### \n 再平衡检测程序开始运行...")
            
            # 检查数据库连接
            if not self.check_db_connection():
                raise Exception("数据库连接失败")
                
            # 获取账户列表
            acct_list = self.dc.QueryAllAcctFollowFutureGateio()
            if not acct_list:
                print("没有找到需要同步的账户")
                return
                
            # 处理每个账户
            for acct in acct_list:
                try:
                    print("----------------------------------------" )
                    print("开始同步账户：%s"%acct['name'])
                    self.process_single_account(acct)
                except Exception as e:
                    self.ExceptionThrow(e)
                    continue
                    
            print("本轮计算完成，下一个30分或00，将会重启计算"+time.strftime('%y-%m-%d %H:%M:%S'))
            
        except Exception as e:
            self.ExceptionThrow(e)
            self.SendWarning()

    def SendWarning(self):

        try:
            title = 'Gateio-CTA 交易服务器故障'
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

    def check_run_status(self):
        """
        检查程序是否可以运行
        """
        try:
            # 检查数据库连接和API连接
            if not self.check_db_connection():
                return False
                
            # 检查是否在允许运行的时间段
            if self.server == '1':  # 主服务器
                try:
                    # 更新主服务器状态
                    self.dc.UpdateWatchApp("future_cta_gateio")
                    print("主服务器状态更新成功")
                    return True
                except Exception as e:
                    self.log_error(e, "主服务器状态更新失败")
                    return False
            else:  # 备份服务器
                try:
                    dbback = int(self.config.read_info("api","traderdbback"))
                    remote_dc = MyDBConn(dbback)
                    ret = remote_dc.QueryWatchApp("future_cta_gateio")
                    
                    if not ret:
                        print("未找到主服务器状态记录，备份服务器接管")
                        remote_dc.UpdateWatchAppBack("future_cta_gateio")
                        return True
                        
                    dt1 = datetime.datetime.now()
                    dt2 = ret['status_time']
                    timedelta = dt1 - dt2
                    
                    if timedelta.total_seconds() > int(self.timeout):
                        remote_dc.UpdateWatchAppBack("future_cta_gateio")
                        self.SendWarning()
                        print(f"主服务器超时 {timedelta.total_seconds()}秒，备份���务器接管")
                        return True
                        
                    print(f"主务器运行正常，最后更新时间：{dt2}")
                    return False
                    
                except Exception as e:
                    self.ExceptionThrow(e)
                    return True  # 如果无法检查主服务器状态，允许备份服务器运行
                    
        except Exception as e:
            self.ExceptionThrow(e)
            return False

    def check_db_connection(self):
        """
        检查数据库和API连接
        """
        try:
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    # 检查数据库连接
                    if not self.dc.is_connected():
                        print(f"数据库连接失败，第{retry_count + 1}次重试...")
                        if not self.dc.reconnect():
                            retry_count += 1
                            time.sleep(2)
                            continue
                    
                    # 检查API连接
                    try:
                        # 确保 exchange 已初始化
                        if not hasattr(self, 'exchange'):
                            self.exchange = self.GetPubExchange()
                        
                        # 测试API连接
                        self.exchange.list_futures_accounts("usdt")
                        return True
                    except Exception as e:
                        self.log_error(e, "API连接检查失败")
                        retry_count += 1
                        time.sleep(2)
                        continue
                        
                except Exception as e:
                    self.ExceptionThrow(e)
                    retry_count += 1
                    time.sleep(2)
                    
            print("连接检查失败，已重试%d次" % max_retries)
            return False
            
        except Exception as e:
            self.ExceptionThrow(e)
            return False

    def log_error(self, e, context=""):
        """
        统一的错误日志记录
        """
        error_msg = f"{context} - {str(e)}"
        logging.error(error_msg)
        print(f"{time.strftime('%y-%m-%d %H:%M:%S')} ERROR: {error_msg}")

    def process_single_account(self, acct):
        """
        处理单个账户的同步交易
        """
        try:
            # 设置当前账户ID
            self.current_account_id = acct['acct_id']
            
            obj = ExchangeGatieio()
            acctdata = self.dc.QueryGateAcctInfoByID(acct['acct_id'])

            self.exchange = obj.GetExchangeGateioFuture(acctdata)
            acct_balances = self.exchange.list_positions("usdt", holding="true")

            product_info = acct['product_list']
            product_config = product_info.split("#")
            # 获取最新策略信息
            stg_list = self.GetLatestStgInfo(product_info)
            if len(stg_list) != len(product_config):
                print(acct['name'],"账户策略中配置的商品，与策略表计算的策略不匹配，请检查行情和策略数据,实际只有：%d，策略配置数为%d"%(len(stg_list),len(product_config)))
                return

            # 同步每个产品的持仓
            for stg_one in stg_list:
                try:
                    self.sync_single_position(stg_one, acct, acct_balances)
                except Exception as e:
                    self.log_error(e, f"同步品 {stg_one['symbol']} 失败")
                    continue

            # 清理不在策略中的持仓
            self.clear_unused_positions(stg_list, acct_balances)

        except Exception as e:
            self.log_error(e, f"处理账户 {acct['acct_id']} 失败")
            raise e

    def print_stratage_info(self):
        #遍历现有组合表，打印组合中的持仓信息
        stg_comb = self.dc.QueryAllCombGateio()

        for stg in stg_comb:
            stg_data = self.GetLatestStgInfo(stg[1])
            print("GD20-组合名：%s"%stg[0])
            x = 0
            for itor in stg_data:
                stgvalue = itor['stg']
                stgchar = ""
                if stgvalue == 1 or stgvalue == 2:
                    stgchar = "多"
                elif stgvalue == -1 or stgvalue == -2:
                    stgchar = "空"
                else:
                    stgchar = "无仓位"

                print("%d.%s,%s,%.2f,%s"%(x,itor['symbol'],stgchar,itor['num'],itor['stratage_time']))
                x += 1
            print("------------------------------------------------------------------")

    def sync_single_position(self, stg_one, acct, acct_balances):
        """
        同步单个产品的持仓
        """
        symbol = stg_one['symbol']
        coin = self.GetCoinInfoFuture(symbol)
        nums = float(stg_one['num'])
        cs = coin['cs']
        ordersizemin = coin['order_size_min']
        
        # 计算目标持仓
        value_single_product = func.safe_divide(acct['money']*acct['percentage'],acct['product_nums'])
        rate = func.safe_divide(10000,value_single_product)
        act_cs = max(1,round(func.safe_divide(nums,rate),0))
        act_money = act_cs * cs * coin['price']
        acct_lever = acct['init']
        #print("账户杠杆设置值：%d"%acct_lever)
        
        # 确定交易方向
        side = self.get_trade_side(stg_one['stg'])
        finally_size = act_cs*side
        
        # 检查现有持仓并调整
        self.adjust_position(symbol, finally_size, coin, acct_balances,acct_lever)

    def get_trade_side(self, stg):
        """
        根据策略确定交易方向
        """
        if stg == 1 or stg == 2:
            return 1
        elif stg == -1 or stg == -2:
            return -1
        return 0

    def adjust_position(self, symbol, finally_size, coin, acct_balances,lever=10):
        """
        调整持仓到目标数量
        """
        found = 0
        holding_size_found = 0
        #holding_leverage = 0
        
        # 检查现有持仓
        for holding in acct_balances:
            holding_symbol = holding.contract.split("_")[0]
            if holding_symbol == symbol:
                found = 1
                holding_size_found = holding.size
                #holding_leverage = int(holding.leverage)
                break
                
        # 调整持仓
        if found == 0:
            diff = finally_size - 0
            if diff != 0:
                print("发现:%s持仓，目标张数:%f,现有张数：%f,调整后的持仓市值:%.2f,开始同步." % (
                    symbol, finally_size, 0, finally_size * coin['cs'] * coin['price']))
                self.SendOrder(symbol, diff, coin, lever)
        else:
            diff = finally_size - holding_size_found
            if diff != 0:
                print("发现:%s持仓，目标张数:%f,现有张数：%f,调整后的持仓市值:%.2f,开始同步." % (
                    symbol, finally_size, holding_size_found, finally_size * coin['cs'] * coin['price']))
                self.SendOrder(symbol, diff, coin, lever)

    def clear_unused_positions(self, stg_list, acct_balances):
        """
        清理不在策略中的持仓
        """
        for holding in acct_balances:
            symbol = holding.contract.split("_")[0]
            if not any(stg['symbol'] == symbol for stg in stg_list):
                coin = self.GetCoinInfoFuture(symbol)
                diff = 0 - holding.size
                print("发现:%s持仓，目标张数:%f,现有张数：%f,清掉持仓市值:%.2f,开始同步." % (
                    symbol, 0, holding.size, 0))
                if diff != 0:
                    self.SendOrder(symbol, diff, coin, 10)

    def cleanup_watch_app_records(self):
        """
        清理 watch_app 表中的历史记录
        """
        try:
            # 保留7天的数，删除更早记录
            self.dc.CleanupWatchApp("future_cta_gateio", days=7)
            print("清理 watch_app 历史记录完成")
        except Exception as e:
            self.log_error(e, "清理 watch_app 记录失败")

def job():
    try:
        program = Trader()
        
        # 检查是否允许运行
        if program.check_run_status():
            if program.allow_run:
                program.AcctSynch()
            
    except Exception as e:
        program.ExceptionThrow(e)
        program.SendWarning()

def print_job():
    program = Trader()
    program.print_stratage_info()

def run_scheduler():
    """
    改进的调度器运行函数
    """
    while True:
        try:
            # 获取当前时间
            now = datetime.datetime.now()
            
            # 检查是否有需要执行的任务
            for job in schedule.jobs:
                # 检查任务是否应该执行
                if job.should_run:
                    print(f"执行定时任务: {job.job_func.__name__}")
                    # 使用超时控制运行任务
                    success = run_job_with_timeout(job.job_func, timeout=300)
                    if not success:
                        print(f"任务 {job.job_func.__name__} 执行失败，尝试重新初始化...")
                        try:
                            schedule.clear()
                            setup_schedule()
                        except Exception as reinit_e:
                            print(f"重新初始化失败: {str(reinit_e)}")
            
            # 运行调度器
            schedule.run_pending()
            
            # 使用更短的睡眠时间，提高响应性
            time.sleep(1)
                
        except Exception as e:
            print(f"调度器异常: {str(e)}")
            time.sleep(5)

def setup_schedule():
    """
    设置定时任务
    """
    try:
        schedule.clear()  # 清除所有现有任务
        
        # 每小时的 02 分和 32 分执行主任务
        for minute in ['02', '32']:
            schedule.every().hour.at(f':{minute}').do(job)
            
        # job 执行完 1 分钟后执行一次
        def delayed_job():
            time.sleep(60)  # 等待1分钟
            job()
            
        # 每小时的 02 分和 32 分执行打印任务
        for minute in ['02', '32']:
            schedule.every().hour.at(f':{minute}').do(print_job)
            schedule.every().hour.at(f':{minute}').do(delayed_job)
        
        # 添加每天凌晨清理历史记录的任务
        schedule.every().day.at("00:00").do(lambda: Trader().cleanup_watch_app_records())
        
        print("定时任务设置成功")
        
    except Exception as e:
        print(f"设置定时任务失��: {str(e)}")
        raise e

def run_job_with_timeout(job_func, timeout=300):
    """
    使用超时控制运行任务
    """
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
        return True
        
    except Exception as e:
        print(f"任务执行异常: {str(e)}")
        return False

if __name__ == '__main__':
    try:
        print(f"程序启动时间: {datetime.datetime.now()}")
        
        # 初次运行
        print("执行初始任务...")
        print_job()
        job()
        
        # 设置定时任务
        setup_schedule()
        
        # 启动调度器
        run_scheduler()
        
    except KeyboardInterrupt:
        print("程序被手动停止")
    except Exception as e:
        print(f"程序启动失败: {str(e)}")
