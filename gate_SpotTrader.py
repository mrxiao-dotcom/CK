# !/user/bin/env python3
# -*- coding: utf-8 -*-


# 同步现货账户的持仓
"""
1、在 acct_stg_buyer 中配置：账号id，持仓品种（注意必须全部是现货),每个品种配置的金额，1，ATOM#WLD#GALA#SAND,10，意思就是给上述4个币每个配10元
2、定时程序，将会自动补仓，原来多出来的，不卖出
3、读取对应品种的当前价格，盈利超过30%之后，自动卖出盈利部分对应的数量，并对其他持仓进行补充
"""

import time, math
from BASECLASS.gateiobase import ExchangeGatieio,Stg
from gate_api import ApiClient, Configuration, FuturesApi, FuturesOrder, Transfer, WalletApi
import schedule
from BASECLASS.configfile import ReadConfigFile
from COMM.dboper import  MyDBConn
from COMM import commFunctions as func
import requests
from queue import Queue


g_queue=Queue(maxsize=20)

class BuyAndHoldGateio(object):
    def __init__(self):
        self.config = ReadConfigFile("gate_config.ini")
        self.dc = MyDBConn(int(self.config.read_info("api", "dbsource")))

        self.exchange = self.GetPubExchange()
        self.coin_info_list = []
        self.stg_id = 4

        self.server = self.config.read_info("api", "spotisserver")
        self.timeout = int(self.config.read_info("api", "spottimeout"))
        self.allow_run = True

    def GetPubExchange(self):
        obj = ExchangeGatieio()
        defaultAcct = int(self.config.read_info("api","pub_acct"))
        acctdata = self.dc.QueryGateAcctInfoByID(defaultAcct)
        exchange = obj.GetExchangeGateioFuture(acctdata)
        self.spotexchange = obj.GetExchangeGateioSpot(acctdata)
        return exchange

    def SendOrder(self,symbol,side,nums,coin_info):
        try:
            total_nums = nums
            min_quote_amount = float(coin_info['min_quote_amount'])


            if nums < min_quote_amount :
                print("下单量小于系统要求，最低为",min_quote_amount)
            else:


                while (total_nums):  # 分拆下单
                    trade_num = abs(total_nums)
                    coin_limit = coin_info['limit']
                    if trade_num >= coin_limit:  # 最大交易数量
                        trade_num = coin_limit

                    total_nums = total_nums - trade_num

                    if side == "sell":
                        coin_num = trade_num / float(coin_info['price'])  # 卖最少1个
                    else:
                        coin_num = trade_num  # 买用金额，卖用数量

                    order = Order(amount=str(coin_num), type='market', side=side, time_in_force='ioc',
                                  currency_pair=symbol + "_USDT")
                    order = self.exchange.create_order(order)
                    if order.status == 'closed':
                        print('交易成功：', side, symbol + "_USDT", "差距为:",
                              trade_num,
                              time.strftime('%y-%m-%d %H:%M:%S'))
                    else:
                        print('交易失败：')

        except Exception as e:
            print(e,symbol,side,nums)
            self.ExceptionThrow(e)

    def FollowStratage(self):

        # 找到要同步的账户
        try:
            acct_list = self.dc.QueryAllAcctFollowBuyerGateio()
        except Exception as e:
            self.ExceptionThrow(e)


        for acct in acct_list:
            try:
                ### 第一步，读取配置 账户余额情况
                acct_id = acct[0]

                product_str = acct[2]
                product_list = product_str.split("#")
                product_money = acct[3]
                acct_info = self.dc.QueryGateAcctInfoByID(acct_id)
                init_flag = acct[5]
                if init_flag == 1:
                    #已经做过初始化，不再初始化
                    continue
                # 开始同步
                print("开始同步账户:", acct_info['name'], "共", len(product_list),"个品种")

                obj = ExchangeGatieio()
                exchange = obj.GetExchangeGateioSpot(acct_info)
                # 现货账户余额查询
                self.exchange = exchange
                acct_balances = exchange.list_spot_accounts()

                ### 第二步，获取品种交易所信息，以及账户中持仓情况
                # 先对策略品种的信息进行查询
                product_detail_list = [] #需要调仓的列表
                product_delete_list = [] #需要删除的列表
                total_value = 0
                acct_usdt = 0#账户可用U

                for prod in product_list:
                    prod_symbol = prod
                    #在交易所查询产品信息
                    coin = self.GetCoinInfoSpot(prod_symbol)
                    #在账户中查询产品信息
                    acct_value = 0#记录账户中该品种的市值
                    for acct_coin in acct_balances:
                        acct_symbol = acct_coin.currency

                        if prod_symbol == acct_symbol:
                            acct_value = float(acct_coin.available) * float(coin['price'])
                            total_value += acct_value
                        elif acct_symbol == "USDT":
                            acct_usdt = float(acct_coin.available)

                    product_info = {'symbol': prod_symbol, 'limit':coin['limit'],'min_quote_amount':coin['min_quote_amount'],'price': float(coin['price']),'acct_value':acct_value}
                    product_detail_list.append(product_info)

                if init_flag == -1: #不但需要同步，还需要把不在列表内的给清理掉
                    print("清理多余的配置外币种...")
                    for acct_coin in acct_balances:
                        acct_symbol = acct_coin.currency
                        found = 0
                        for prod in product_list:

                            if acct_symbol == prod :
                                found = 1
                                break
                        if found == 0 and acct_symbol != "USDT":
                            coin = self.GetCoinInfoSpot(acct_symbol)
                            acct_value = float(acct_coin.available) * float(coin['price'])
                            if acct_value > 10:
                                product_info = {'symbol':acct_symbol, 'limit':coin['limit'],'min_quote_amount':coin['min_quote_amount'],'price': float(coin['price']),'acct_value':acct_value}
                                product_delete_list.append(product_info)

                    for delete_coin in product_delete_list:

                        if delete_coin['acct_value'] > 0:
                            diff = delete_coin['acct_value']
                            self.SendOrder(delete_coin['symbol'], "sell", diff, delete_coin)

                total_nums = len(product_detail_list)
                if total_nums == 0:
                    print("账户:",acct_info['name'],"没有找到产品列表,请检查")
                    return
                avg_value = round((total_value + acct_usdt )*0.999/len(product_detail_list), 2) #预留x%的资金，防止价格波动而导致无法配置
                final_money = min(avg_value,product_money)
                print("当前账户持仓市值",round(total_value,2),"账户可用USDT：",round(acct_usdt,2),"总均值为：", avg_value, "配置品种资金为:", product_money, "理论均值：",final_money)

                ### 第三步，对账户资金进行同步

                # 开始循环进行同步,先把持仓的处理，主要可以用于腾出资金
                for config_coin in product_detail_list:
                    config_symbol = config_coin['symbol']
                    if config_coin['acct_value']>final_money:
                        diff = config_coin['acct_value'] - final_money
                        self.SendOrder(config_symbol,"sell",diff,config_coin)

                for config_coin in product_detail_list:
                    config_symbol = config_coin['symbol']
                    if config_coin['acct_value']<final_money:
                        diff = final_money - config_coin['acct_value']
                        self.SendOrder(config_symbol,"buy",diff,config_coin)

                self.dc.UpdateBuyerStatusGateio(acct_id)

            except Exception as e:
                self.ExceptionThrow(e)
                continue

        print("账号同步工作全部完成")

    def Balance(self):

        # 对各个账户进行持仓再平衡
        # 找到要同步的账户
        try:
            acct_list = self.dc.QueryAllAcctFollowBuyerGateio()
            print("\n #################### \n 再平衡检测程序开始运行..."+time.strftime('%y-%m-%d %H:%M:%S'))
        except Exception as e:
            self.ExceptionThrow(e)




        for acct in acct_list:
            try:
                acct_id = acct[0]
                discount = float(acct[1])
                product_str = acct[2]
                product_list = product_str.split("#")
                acct_name = acct[8]
                rate = float(acct[4])
                isolate_mode = float(acct[9])

                dixi = acct[6] #是否使用余额进行低吸
                dixi_rate = acct[7] #低吸的触发比例
                acct_info = self.dc.QueryAcctInfoByID(acct_id)
                # 开始同步
                print("检测账户:", acct_name, "共", len(product_list),"个品种")
                obj = ExchangeGatieio()
                exchange = obj.GetExchangeGateioSpot(acct_info)
                # 现货账户余额查询
                self.exchange = exchange
                acct_balances = exchange.list_spot_accounts()

                ### 第二步，获取品种交易所信息，以及账户中持仓情况
                # 先对策略品种的信息进行查询
                product_detail_list = []
                total_value = 0
                acct_usdt = 0  # 账户可用U

                for prod in product_list:
                    prod_symbol = prod
                    # 在交易所查询产品信息
                    coin = self.GetCoinInfoSpot(prod_symbol)
                    # 在账户中查询产品信息
                    acct_value = 0  # 记录账户中该品种的市值
                    for acct_coin in acct_balances:
                        acct_symbol = acct_coin.currency

                        if prod_symbol == acct_symbol:
                            acct_value = float(acct_coin.available) * float(coin['price'])
                            total_value += acct_value
                        elif acct_symbol == "USDT":
                            acct_usdt = float(acct_coin.available)

                    product_info = {'symbol': prod_symbol, 'limit': float(coin['limit']), 'min_quote_amount': float(coin['min_quote_amount']),
                                    'price': float(coin['price']), 'acct_value': acct_value,'up24':coin['up24'],'down24':coin['down24']}
                    product_detail_list.append(product_info)

                total_nums = len(product_detail_list)
                if total_nums == 0:
                    print("账户:", acct_info['name'], "没有找到产品列表,请检查")
                    return
                avg_value = round(total_value/total_nums, 2)  # 预留x%的资金，防止价格波动而导致无法配置


                # 找出最高的，平掉补给最低的
                high_value = 0
                low_value = 999999999
                for config_coin in product_detail_list:
                    if config_coin['acct_value'] > high_value:
                        high_value = config_coin['acct_value']
                    if config_coin['acct_value'] < low_value:
                        low_value = config_coin['acct_value']

                print("当前账户持仓市值", round(total_value,2), "账户可用USDT：", round(acct_usdt,2), "总均值为：", avg_value,rate)

                action = 0  # 行动 代码
                avail_usdt = acct_usdt
                average_discount = avg_value
                line = ""

                for config_coin in product_detail_list:
                    acct_coin_eq = config_coin['acct_value']
                    if action ==0 :
                        if acct_coin_eq > avg_value * (1 + rate) :
                            action = 1
                            line = "权益超过均值一定比例，进行再平衡，平衡模式为：%d, 权益:%.2f, 均值:%.2f, 预设比例：%.2f " % (dixi, high_value, avg_value, rate)
                            print(line)
                            if discount >0:
                                if dixi == 1:
                                    line = line + "\n" + "%s本次超出金额：%f,平均权益为：%f,保留资金：%f"%(config_coin['symbol'],round((acct_coin_eq - avg_value),2),avg_value,(acct_coin_eq - avg_value)*discount)
                                    print(line)
                                    average_discount = avg_value - (acct_coin_eq - avg_value)*discount/total_nums
                                elif dixi == 2:
                                    average_discount = avg_value - ((acct_coin_eq - avg_value)*discount + (high_value-low_value))/total_nums
                        elif config_coin['up24']> isolate_mode and acct_coin_eq > avg_value * (1 + isolate_mode/2) and isolate_mode >0 :
                            action = 1
                            line = "%s单币种24小时涨幅%.2f,超过设定比例%.2f,且最新权益%.2f超过未来均值的比例%.2f,超出为:%.2f,占比：%.2f"%(config_coin['symbol'],config_coin['up24'],isolate_mode,acct_coin_eq,isolate_mode/2,acct_coin_eq-avg_value * (1 + isolate_mode/2),(acct_coin_eq-avg_value * (1 + isolate_mode/2))/avg_value)
                            #print(line)
                            if discount > 0:
                                if dixi == 1:
                                    line = line + "\n" + "%s本次超出金额：%f,平均权益为：%f,保留资金：%f" % (
                                    config_coin['symbol'], round((acct_coin_eq - avg_value), 2), avg_value,
                                    (acct_coin_eq - avg_value) * discount)
                                    print(line)
                                    average_discount = avg_value - (acct_coin_eq - avg_value) * discount / total_nums
                                elif dixi == 2:



                                    average_discount = avg_value - ((acct_coin_eq - avg_value) * discount + (
                                                high_value + low_value - 2*avg_value)) / total_nums
                                    line = line + "\n" + "%s本次保留资金%.2f,填补差值超出：%.2f,平均权益为：%f,共保留资金：%f,未来均值:%.2f" % (
                                        config_coin['symbol'], (acct_coin_eq - avg_value) * discount,( high_value + low_value - 2*avg_value), avg_value,
                                        (acct_coin_eq - avg_value) * discount + (high_value + low_value - 2 * avg_value),average_discount)

                                    print(line)


                                    # 检查：如果有品种，盈利超过10%，那么做一次全品种平衡，把盈利部分补充到其他品种去
                if action == 1:
                    ### 第三步，对账户资金进行同步
                    if dixi==2: #


                        #削峰填谷
                        for config_coin in product_detail_list:
                            config_symbol = config_coin['symbol']

                            if config_coin['acct_value']==high_value:
                                diff = config_coin['acct_value'] - average_discount
                                self.SendOrder(config_symbol, "sell", diff, config_coin)

                            if config_coin['acct_value']==low_value:
                                diff = average_discount - config_coin['acct_value']
                                avail_usdt_latest = exchange.list_spot_accounts(currency="USDT")
                                avail_u = float(avail_usdt_latest[0].available)
                                self.SendOrder(config_symbol, "buy", min(avail_u,diff), config_coin)
                    else:
                        # 开始循环进行同步,先把持仓的处理，主要可以用于腾出资金
                        for config_coin in product_detail_list:
                            config_symbol = config_coin['symbol']
                            if config_coin['acct_value'] > average_discount:
                                diff = config_coin['acct_value'] - average_discount
                                self.SendOrder(config_symbol, "sell", diff, config_coin)

                        for config_coin in product_detail_list:
                            config_symbol = config_coin['symbol']
                            if config_coin['acct_value'] < average_discount:
                                diff = average_discount - config_coin['acct_value']
                                self.SendOrder(config_symbol, "buy", diff, config_coin)

                    self.SendAcctInfo(acct_id, "再平衡通知:" + acct_name, line)

                else:
                    #低吸开关判断，如果低吸标志为1，那么检查，如果检查结果成立，则对该品种进行补仓
                    if dixi > 0 :
                        for config_coin in product_detail_list:
                            acct_coin_eq = config_coin['acct_value']
                            cond1 = (acct_coin_eq <= avg_value * (1 - float(dixi_rate)))
                            cond2 = (isolate_mode > 0 and config_coin['down24'] > isolate_mode and acct_coin_eq <= avg_value * (1 - float(isolate_mode) / 3))
                            if cond2:
                                print(round(acct_coin_eq,2),avg_value,round((isolate_mode) / 3,2),avg_value * (1 - float(isolate_mode) / 2),round(config_coin[
                                'down24'],2),isolate_mode)
                            if  cond1 or cond2:
                                if  avail_usdt > 10 :
                                    #补仓
                                    diff = avg_value - acct_coin_eq
                                    self.SendOrder(config_coin['symbol'], "buy", min(diff,avail_usdt), config_coin)

                                    line = "%s 低吸触发，且余额大于10 ,差额：%f,均值：%f,当前值：%f"%(config_coin['symbol'],min(diff,avail_usdt),avg_value,acct_coin_eq)
                                    avail_usdt = avail_usdt - diff
                                    print(line)
                                    self.SendAcctInfo(acct_id,"低吸通知:"+acct_name,line)
                                else:
                                    print("可用余额不足最低成交额10")


            except Exception as e:
                self.ExceptionThrow(e)
                continue

    def ExceptionThrow(self, e):
        line = e.__traceback__.tb_frame.f_globals["__file__"] + " 异常发生在(行):%d " % e.__traceback__.tb_lineno + str(e)
        print(time.strftime('%y-%m-%d %H:%M:%S') + "ExceptionThrow" + line + '-------------- \n')


    def GetCoinInfoSpot(self, symbol):
        try:
            # 先查有没有历史记录，没有则重新去网上查

            data = self.exchange.get_currency_pair(symbol+"_USDT")
            limit = float(data.max_quote_amount)
            min_quote_amount = float(data.min_quote_amount)
            data = self.exchange.list_tickers(currency_pair=symbol + "_USDT")
            price = data[0].last
            up24,down24 = self.GetCandleSpot(symbol)
            coin_info = {'symbol': symbol, 'limit': limit, 'min_quote_amount': min_quote_amount, 'price': price, 'up24':up24,'down24':down24}
            return coin_info

        except Exception as e:
            self.ExceptionThrow(e)

    def GetCandleSpot(self,symbol):
        try:
            data = self.exchange.list_candlesticks(symbol+"_USDT",limit=24,interval='1h')
            highest = 0
            lowest = 99999999
            for candle in data:
                high = float(candle[3])
                if high > highest:
                    highest = high

                low = float(candle[4])
                if low < lowest:
                    lowest = low

            close = float(data[len(data)-1][5])
            draw_rate = (highest - close)/highest
            up_rate = (close-lowest)/lowest

            return up_rate,draw_rate
        except Exception as e:
            self.ExceptionThrow(e)


    def SendAcctInfo(self, acct_id,title="",msg=""):
        try:

            context = "[名称]|持仓数量|权益\n"

            acct_info = self.dc.QueryAcctInfoByID(acct_id)
            exchange = self.GetExchangeGateio(acct_info)
            sender_token = acct_info['token']
            balances_total = exchange.list_spot_accounts()
        except Exception as e:
            self.ExceptionThrow(e)

        spot_eq = 0
        future_eq = 0 #可用

        # 获得期货权益
        info_list = []
        for itor in balances_total:
            try:
                if itor.currency == 'USDT':
                    # print(acctInfo[1],"余额查询成功，更新最新数据...")
                    future_eq = round(float(itor.available), 2)
                else:

                    availBal = round(float(itor.available), 2)
                    currency_pair = itor.currency+"_USDT"
                    if currency_pair == "POINT_USDT":
                        print("出现异常数据：",currency_pair,itor.currency)
                        continue
                    else:
                        tickers = self.exchange.list_tickers(currency_pair=currency_pair)
                    last_price = float(tickers[0].last)
                    eqUsd = round(availBal*last_price,2)
                    if availBal < 1:  # 自动过滤小于1的资产
                        continue
                    line = itor.currency + "|" + str(availBal) + "|" + str(round(eqUsd,2)) + "\n"
                    context += line
                    spot_eq += eqUsd
                record = [acct_id,time.strftime('%y-%m-%d %H:%M:%S'),itor.currency,availBal,future_eq]
                info_list.append(record)
            except Exception as e:
                self.ExceptionThrow(e)
                continue

        try:
            if title != "每日信息汇总":
                self.dc.InsertInfoRecord(info_list)

            line = "权益:" + str(round(future_eq+spot_eq,2)) + "|可用余额:" + str(future_eq) + "|现货:" + str(round(spot_eq, 2)) + "\n"
            context += line
            if msg!="":
                context += msg
            #print(context)

            if title =="":
                title = '账户调整通知'
            mydata = {
                'text': title,
                'desp': context
            }

            if len(sender_token)>0:
                url = "http://wx.xtuis.cn/" + sender_token + ".send"
                information = {'url':url,'info':mydata}
                g_queue.put(information)
            #requests.post(url, data=mydata)

        except Exception as e:
            self.ExceptionThrow(e)

    def SendInfoAll(self):

        try:
            acct_list = self.dc.QueryAllAcctFollowBuyerGateio()
            for acct in acct_list:

                self.SendAcctInfo(acct[0],"每日汇总信息")
        except Exception as e:

            self.ExceptionThrow(e)


    def SendWarning(self):

        try:
            title = 'Gateio程序运行故障'
            mydata = {
                'text': title,
                'desp': "速速检查230服务器"
            }

            #admin 1 xiaoj
            url = "http://wx.xtuis.cn/BDGGZgR856AueOk6JXoCERIyi.send"
            requests.post(url, data=mydata)

            #admin 2 gyuangy
            url = "http://wx.xtuis.cn/DOyVyJTsYb8UfxLV4qtWPr0t6.send"
            requests.post(url, data=mydata)
        except Exception as e:
            self.ExceptionThrow(e)

buyers = BuyAndHoldGateio()



"""
buyers.Show()
"""



def job():

    #如果是服务器，则自动启动执行，并且向数据库写入正常运转的信息
    if buyers.server == '1':
        try:
            buyers.allow_run = True
            buyers.dc.UpdateWatchApp("buyer_gateio")
        except Exception as e:
            buyers.ExceptionThrow(e)
    else:
        #如果是备份机，先检查服务器的信息，如果数据库无法访问、信息已经5分钟未更新，则自动启动
        try:
            remote_dc = MyDBConn(10)  #gate - 10 okx - 12 binance - 13
            ret = remote_dc.QueryWathcApp("buyer_gateio")
            dt1 = datetime.datetime.now()
            dt2 = ret['status_time']
            timedelta = dt1 - dt2
            if timedelta.total_seconds() > int(buyers.timeout) :
                buyers.allow_run = True
                remote_dc.UpdateWatchAppBack("buyer_gateio")

                if buyers.sendkg == 0:
                    buyers.SendWarning()
                    buyers.sendkg = 1
            else:
                buyers.allow_run = False
                print("服务器运行正常，备份程序挂起，1分钟后再检查...")
                buyers.sendkg = 0
                #如果服务器有反馈了，就继续阻塞自己
        except Exception as e:
            print(e) #远程数据库访问遇到故障，立马启动
            buyers.allow_run = True


    if buyers.allow_run:
        buyers.FollowStratage()
        buyers.Balance()



def msg():


    if buyers.allow_run:

        if g_queue.qsize() > 0 and buyers.allow_run:
            info = g_queue.get()
            requests.post(info['url'], data=info['info'])
            print("消息推送成功，队列中还有消息条数：",g_queue.qsize())

def sendall():
    if buyers.allow_run:
        buyers.SendInfoAll()

if __name__ == '__main__':

    job()

    schedule.every(1).minutes.do(job)
    schedule.every(15).minutes.do(msg)
    schedule.every(24).hours.do(sendall)
    while True:
        schedule.run_pending()
        time.sleep(1)

