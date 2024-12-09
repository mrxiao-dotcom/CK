from BASECLASS.MySQLBase import MSSQL
import time
from decimal import Decimal


class MyDBConn:
    def __init__(self, data_source): #local 1
        self.data_source = data_source
        self.ms = MSSQL(data_source)

    def is_connected(self):
        """
        检查数据库连接是否有效
        """
        try:
            # 执行一个简单的查询来测试连接
            self.ms.ExecQuery("SELECT 1")
            return True
        except Exception as e:
            print(f"数据库连接检查失败: {str(e)}")
            return False

    def reconnect(self):
        """
        重新建立数据库连接
        """
        try:
            # 重新创建连接
            self.ms = MSSQL(self.data_source)
            
            # 测试新连接
            if self.is_connected():
                print("数据库重连成功")
                return True
            else:
                print("数据库重连失败")
                return False
                
        except Exception as e:
            print(f"数据库重连异常: {str(e)}")
            return False

    def ExceptionThrow(self,e):
        """
        异常处理
        """
        line = e.__traceback__.tb_frame.f_globals["__file__"] + " 异常发生在(行):%d " % e.__traceback__.tb_lineno + str(e)
        print(time.strftime('%y-%m-%d %H:%M:%S') + "ExceptionThrow" + line + '-------------- \n')


    def QueryAcctInfo(self,accName=""):

        result = []
        try:
            if accName == "":
                sqlstr = "select acct_id,memo,apikey,secretkey,apipass,status,acct_date,email,sendflag,acct_name from acct_info where state = 1"
                data = self.ms.ExecQuery(sqlstr)
                result = [itor for itor in data]
            else:
                sqlstr = "select acct_id,memo,apikey,secretkey,apipass,status,acct_date,email,sendflag,acct_name from acct_info where state = 1 and acct_name = '" + accName + "'"
                data = self.ms.ExecQuery(sqlstr)
                # print(data)
                result = data[0]

        except Exception as e:
            print("数据库查找账户acct_info表，" + accName + "出现错误,语句为：" + sqlstr)
            print(e)

        return result

    def QueryAcctInfoByID(self,acct_id=1):


        try:

            sqlstr = "select acct_id,memo,apikey,secretkey,apipass,status,acct_date,email,sendflag,acct_name from acct_info where state = 1 and acct_id= '" + str(acct_id) + "'"
            data = self.ms.ExecQuery(sqlstr)
            # print(data)
            if len(data) == 0:
                return 0
            else:
                dict_data = {'acctId':data[0][0],'name':data[0][1],'apiKey':data[0][2],'secret':data[0][3],'password':data[0][4],'token':data[0][7]}
                return dict_data

        except Exception as e:
            print(e)

    def QueryBinanceAcctInfoByID(self,acct_id=1):


        try:

            sqlstr = "select acct_id,memo,apikey,secretkey,apipass,status,acct_date,email,sendflag,acct_name from acct_info where state = 1 and group_id = 4 and acct_id= '" + str(acct_id) + "'"
            data = self.ms.ExecQuery(sqlstr)
            # print(data)
            if len(data) == 0:
                return 0
            else:
                dict_data = {'acctId':data[0][0],'name':data[0][1],'apiKey':data[0][2],'secret':data[0][3],'password':data[0][4],'token':data[0][7]}
                return dict_data

        except Exception as e:
            print(e)

    def QueryGateAcctInfoByID(self,acct_id=1):


        try:

            sqlstr = "select acct_id,memo,apikey,secretkey,apipass,status,acct_date,email,sendflag,acct_name from acct_info where state = 1 and group_id = 3 and acct_id= '" + str(acct_id) + "'"
            data = self.ms.ExecQuery(sqlstr)
            # print(data)
            if len(data) == 0:
                return 0
            else:
                dict_data = {'acctId':data[0][0],'name':data[0][1],'apiKey':data[0][2],'secret':data[0][3],'password':data[0][4],'token':data[0][7]}
                return dict_data

        except Exception as e:
            print(e)

    def QueryMaxDatePrice30M(self,symbol):
        result = 0
        try:
            sqlstr = "select max(price_time)  from okex_price_30m where product_code ='" + symbol + "'"

            retData = self.ms.ExecQuery(sqlstr)
            if retData[0][0] is None:
                result = ""
            else:
                result = retData[0]

        except Exception as e:
            print("执行queryPriceData30M抛出异常，原因是:", e)
            print(sqlstr)

        return result

    def QueryMaxDatePrice30MGateio(self,symbol):
        result = 0
        try:
            sqlstr = "select max(price_time)  from gate_price_30m where product_code ='" + symbol + "'"

            retData = self.ms.ExecQuery(sqlstr)
            if retData[0][0] is None:
                result = ""
            else:
                result = retData[0]

        except Exception as e:
            print("执行queryPriceData30M抛出异常，原因是:", e)
            print(sqlstr)

        return result

    def InsertPriceData(self,symbol,priceData):
        try:
            if len(priceData)==0:

                return
            # 生成sql语句
            str1 = ""
            sqlstr = ""
            for itor in priceData:
                sqllist = []
                sqllist.append(symbol)
                if itor[4] <= 0:
                    print("error, symbol is zero",symbol,itor[4])
                    return
                else:
                    sqllist.append(itor[4])

                sqllist.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(itor[0] / 1000)))

                sqltuple = tuple(sqllist)
                str1 += ",(0,'%s',%15f,0,0,0,'%s','30m')" % sqltuple

            sqlstr = "insert into okex_price_30m  VALUES " + str1[1:]
            self.ms.ExecNonQuery(sqlstr)

        except Exception as e:
            print("函数insertPriceData30M抛出异常",e,sqlstr)
    def InsertPriceDataGateio(self,symbol,priceData):
        try:
            if len(priceData)==0:

                return
            # 生成sql语句
            str1 = ""
            sqlstr = ""
            for itor in priceData:
                sqllist = []
                sqllist.append(symbol)
                sqllist.append(itor.c)
                sqllist.append(itor.h)
                sqllist.append(itor.l)
                sqllist.append(itor.o)
                sqllist.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(itor.t)))

                sqltuple = tuple(sqllist)
                str1 += ",(0,'%s',%s,%s,%s,%s,'%s','30m')" % sqltuple

            sqlstr = "insert into gate_price_30m  VALUES " + str1[1:]
            self.ms.ExecNonQuery(sqlstr)

        except Exception as e:
            print("函数InsertPriceDataGateio抛出异常",e,sqlstr)
    def QueryStratageDetailLatest(self,symbol,stratage_id = 1):
        #选出策略信息最新的数据
        sqlstr = ""

        try:
            #优化：新增最新策略时间表，计算完后同步更新，提高取数据的效率
            #sqlstr = "select stratage_time, winner, stg, num,rate,top,mid,but,close from stratage_detail where product_code = '" + symbol + "' and stratage_id = "+str(stratage_id)+" order by stratage_time DESC limit 1 "
            sqlstr = "select stratage_time, winner, stg, num,rate,top,mid,but,close  from stratage_latest where product_code = '" + symbol + "' and stratage_id = "+str(stratage_id)+" order by stratage_time DESC limit 1 "
            result = self.ms.ExecQuery(sqlstr)
            if len(result) == 0:
                return 0
            else:
                return result[0]


        except Exception as e:
            print("异常：queryStratageDetail函数抛出，原因：",e,sqlstr)
            self.ExceptionThrow(e)


    def QueryStratageDetailLatestGateioComb(self,product_str,stratage_time,stratage_id = 1):
        #选出策略信息最新的数据
        sqlstr = ""
        ret_data_list = []
        try:
            #优化：新增最新策略时间表，计算完后同步更新，提高取数据的效率
            sqlstr = "select stratage_time, winner, stg, num,rate,top,mid,but,close,product_code  from stratage_latest_gate where product_code in (" + product_str + ") and stratage_id = "+str(stratage_id) + " and stratage_time ='"+stratage_time + "'"
            result = self.ms.ExecQuery(sqlstr)
            if len(result) == 0:
                return 0
            else:
                for itor in result:
                    ret_data = {'stratage_time':itor[0],'winner':itor[1],'stg':itor[2],'num':itor[3],'rate':itor[4],'top':itor[5],'mid':itor[6],'bot':itor[7],'close':itor[8],'symbol':itor[9]}
                    ret_data_list.append(ret_data)
            return ret_data_list
        except Exception as e:
            print("异常：queryStratageDetail函数抛出，原因：",e,sqlstr)
            self.ExceptionThrow(e)

    def QueryStratageDetailLatestGateio(self,symbol,stratage_id = 1):
        #选出策略信息最新的数据
        sqlstr = ""

        try:
            #优化：新增最新策略时间表，计算完后同步更新，提高取数据的效率
            #sqlstr = "select stratage_time, winner, stg, num,rate,top,mid,but,close from stratage_detail where product_code = '" + symbol + "' and stratage_id = "+str(stratage_id)+" order by stratage_time DESC limit 1 "
            sqlstr = "select stratage_time, winner, stg, num,rate,top,mid,but,close,product_code  from stratage_latest_gate where product_code = '" + symbol + "' and stratage_id = "+str(stratage_id)+" order by stratage_time DESC limit 1 "
            result = self.ms.ExecQuery(sqlstr)
            if len(result) == 0:
                return 0
            else:
                itor = result[0]
                ret_data = {'stratage_time':itor[0],'winner':itor[1],'stg':itor[2],'num':itor[3],'rate':itor[4],'top':itor[5],'mid':itor[6],'bot':itor[7],'close':itor[8],'symbol':itor[9]}
                return ret_data


        except Exception as e:
            print("异常：queryStratageDetail函数抛出，原因：",e,sqlstr)
            self.ExceptionThrow(e)

    def QueryStratageDetailGateio(self,symbol,stratage_id = 1):
        #选出策略信息最新的数据
        sqlstr = ""
        try:
            #优化：新增最新策略时间表，计算完后同步更新，提高取数据的效率
            sqlstr = "select stratage_time, winner, stg, num,rate,top,mid,but,close,product_code  from stratage_detail_gate where product_code = '" + symbol + "' and stratage_id = "+str(stratage_id)+" order by stratage_time DESC  "
            result = self.ms.ExecQuery(sqlstr)
            if len(result) == 0:
                return 0
            else:
                return result


        except Exception as e:
            print("异常：queryStratageDetail函数抛出，原因：",e,sqlstr)
            self.ExceptionThrow(e)

###
    def QueryStratageDetailTimeGateio(self,symbol,stratage_time,stratage_id = 1):
        #选出策略信息最新的数据
        sqlstr = ""

        try:
            #优化：新增最新策略时间表，计算完后同步更，提高取数据的效率
            sqlstr = "select stratage_time, winner, stg, num,rate,top,mid,but,close,product_code  from stratage_detail_gate where product_code = '" + symbol + "' and stratage_id = "+str(stratage_id)+" and stratage_time = '"+stratage_time+"'"
            result = self.ms.ExecQuery(sqlstr)
            if len(result) == 0:
                return 0
            else:
                itor = result[0]
                ret_data = {'stratage_time':itor[0],'winner':itor[1],'stg':itor[2],'num':itor[3],'rate':itor[4],'top':itor[5],'mid':itor[6],'bot':itor[7],'close':itor[8],'symbol':itor[9]}
                return ret_data


        except Exception as e:
            print("异常：queryStratageDetail函数抛出，原因：",e,sqlstr)
            self.ExceptionThrow(e)


    def QueryLatestIndex(self,stratage_id = 1):
        result = []
        try:
            sqlstr = "select count(*) from okex_index_30m where stratage_id =  "+str(stratage_id)+" order by index_time desc limit 1"
            result = self.ms.ExecQuery(sqlstr)
            if result[0][0]==0:
                return 0
            else:

                sqlstr = "select index_time from okex_index_30m where stratage_id =  "+str(stratage_id)+" order by index_time desc limit 1"
                result = self.ms.ExecQuery(sqlstr)
                return result[0]


        except Exception as e:
            print("异常：QueryLatestIndex函数抛出，原因：",e,sqlstr)
            self.ExceptionThrow(e)


    def QueryProductList(self):
        try:

            sqlstr = "select product_code from product"
            data = self.ms.ExecQuery(sqlstr)
            ret = [x[0] for x in data]
            return ret


        except Exception as e:
            print("数据库查找queryProductData表，出现错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)

    def QueryProductListFutureGateio(self):
        try:

            sqlstr = "select comb_name from stg_comb_product_gateio where product_comb = 'A25' "
            data = self.ms.ExecQuery(sqlstr)

            return data


        except Exception as e:
            print("数据库查找QueryProductListFutureGateio，出错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)

    def QueryProductListFutureGateioAll(self):
        try:

            sqlstr = "select comb_name from stg_comb_product_gateio where product_comb in (select product_list from acct_stg_future_gateio )"
            data = self.ms.ExecQuery(sqlstr)
            product_list = []
            for line in data:
                product = line[0].split("#")
                product_list.extend(product)

            return product_list


        except Exception as e:
            print("数据库查找QueryProductListFutureGateio，出错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)

    def QueryGateioProductList(self):
        try:

            sqlstr = "select product_code from product_gateio"
            data = self.ms.ExecQuery(sqlstr)
            ret = [x[0] for x in data]
            return ret


        except Exception as e:
            print("数据库查找queryProductData表，出现错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)

    def QueryCombProductListGateio(self,comb_name):
        try:

            sqlstr = "select product_comb,comb_name from stg_comb_product_gateio where product_comb = '"+comb_name+"'"
            data = self.ms.ExecQuery(sqlstr)
            return data[0]

        except Exception as e:
            print("数据库查找QueryCombProductListGateio表，出现错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)

    def QueryAllCombGateio(self):
        try:

            sqlstr = "select  product_comb,comb_name from stg_comb_product_gateio"
            data = self.ms.ExecQuery(sqlstr)
            return data

        except Exception as e:
            print("数据库查找QueryAllCombGateio表，出现错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)

    def QueryProductDataAll(self,symbol_code):

        try:

            sqlstr = "select close, price_time from okex_price_30m where product_code = '"+ symbol_code + "' order by price_time asc"
            data = self.ms.ExecQuery(sqlstr)
            ret = [x for x in data]
            return ret


        except Exception as e:
            print("数据库查找queryProductData表，出现错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)

    def QueryProductDataAllGateio(self,symbol_code):

        try:

            sqlstr = "select close, price_time from gate_price_30m where product_code = '"+ symbol_code + "' order by price_time asc"
            data = self.ms.ExecQuery(sqlstr)
            return data


        except Exception as e:
            print("数据库查找queryProductData表，出现错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)
    def QueryProductDataPart(self,symbol,begin_time,win_days=0,include=0):

        try:
            sqlstr = ""
            if include == 1:
                sqlstr = "select close, price_time from okex_price_30m where product_code = '" + symbol + "' and price_time >= DATE_SUB('" + begin_time.strftime(
                    "%Y-%m-%d %H:%M:%S") + "' ,INTERVAL " + str(win_days) + " DAY) order by price_time asc"
            else:
                sqlstr = "select close, price_time from okex_price_30m where product_code = '"+ symbol + "' and price_time > DATE_SUB('"+begin_time.strftime("%Y-%m-%d %H:%M:%S")+"' ,INTERVAL "+str(win_days)+" DAY) order by price_time asc"
            data = self.ms.ExecQuery(sqlstr)

            return data


        except Exception as e:
            print("数据库查找queryProductData表，出现错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)

    def QueryProductDataPartGateio(self,symbol,begin_time,win_days=0,include=0):

        try:
            sqlstr = ""
            if include == 1:
                sqlstr = "select close, price_time from gate_price_30m where product_code = '" + symbol + "' and price_time >= DATE_SUB('" + begin_time.strftime(
                    "%Y-%m-%d %H:%M:%S") + "' ,INTERVAL " + str(win_days) + " DAY) order by price_time asc"
            else:
                sqlstr = "select close, price_time from gate_price_30m where product_code = '"+ symbol + "' and price_time > DATE_SUB('"+begin_time.strftime("%Y-%m-%d %H:%M:%S")+"' ,INTERVAL "+str(win_days)+" DAY) order by price_time asc"
            data = self.ms.ExecQuery(sqlstr)

            return data


        except Exception as e:
            print("数据库查找queryProductData表，出现错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)

    def QueryFirstPrice(self):
        try:

            sqlstr = "select close,product_code from okex_price_30m where price_time = (select min(price_time) from okex_price_30m )"
            data = self.ms.ExecQuery(sqlstr)
            ret = [x for x in data]
            return ret


        except Exception as e:
            print("数据库查找queryProductData表，出现错误,语句为： 异常代码：",e,sqlstr)
            return 0

    def QueryProductDataNum(self,symbol,num):

        try:
            num = num if num>0 else 1 #最少取一个数据出来
            sqlstr = "select close, price_time from okex_price_30m where product_code = '"+ symbol + "' order by price_time desc limit "+str(num)
            #print(sqlstr)
            data = self.ms.ExecQuery(sqlstr)
            ret = data[::-1]
            return ret


        except Exception as e:
            print("数据库查找queryProductData表，出现错误,语句为： 异常代码：",e)
            return 0
            #print(e)


    def QueryMaxClose(self,symbol,close_time,win_days):

        try:

            sqlstr = "select max(close) from okex_price_30m where product_code = '"+ symbol + "' and price_time < '" + close_time.strftime("%Y-%m-%d %H:%M:%S")+ "' and  price_time >= DATE_SUB('"+close_time.strftime("%Y-%m-%d %H:%M:%S")+"',INTERVAL "+str(win_days)+" DAY) "
            data = self.ms.ExecQuery(sqlstr)

            return data[0]


        except Exception as e:
            print("数据库查找queryProductData表，出现错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)

    def QueryMinClose(self,symbol,close_time,win_days):

        try:

            sqlstr = "select min(close) from okex_price_30m where product_code = '"+ symbol + "' and price_time < '" + close_time.strftime("%Y-%m-%d %H:%M:%S")+ "' and  price_time >= DATE_SUB('"+close_time.strftime("%Y-%m-%d %H:%M:%S")+"',INTERVAL "+str(win_days)+" DAY) "

            data = self.ms.ExecQuery(sqlstr)

            return data[0]


        except Exception as e:
            print("数据库查找queryProductData表，出现错误,语句为： 异常代码：",e,sqlstr)
            return 0
            #print(e)

    def InsertStratageDetail(self,stratage_id, symbol_code, close_price, close_time, top_list, mid_list, bot_list, stg_list,
                             num_list, rate_list, winner_list):

        try:

            list_len = len(close_price)
            if list_len == 0:
                return

            str1 = ""
            sqlstr = ""
            for i in range(0, list_len):
                sqllist = []
                sqllist.append(stratage_id)
                sqllist.append(symbol_code)
                sqllist.append(close_price[i])
                sqllist.append(close_time[i])
                sqllist.append(num_list[i])
                sqllist.append(stg_list[i])
                sqllist.append(rate_list[i])
                sqllist.append(winner_list[i])
                sqllist.append(top_list[i])
                sqllist.append(mid_list[i])
                sqllist.append(bot_list[i])

                sqltuple = tuple(sqllist)
                str1 += ",(%d,'%s',%f,'%s',%d,%d,%f,%f,%f,%f,%f)" % sqltuple

            sqlstr = "insert into stratage_detail  VALUES " + str1[1:]
            self.ms.ExecNonQuery(sqlstr)
        except Exception as e:
            # print(sqlstr)
            print("执行InsertStratageDetail报异常：", e)
            self.ExceptionThrow(e)


    def InsertStratageDetailGateio(self, stratage_id, symbol_code, close_price, close_time, top_list, mid_list, bot_list,
                             stg_list,
                             num_list, rate_list, winner_list):
        try:

            list_len = len(close_price)
            if list_len == 0:
                return

            str1 = ""
            sqlstr = ""
            for i in range(0, list_len):
                sqllist = []
                sqllist.append(stratage_id)
                sqllist.append(symbol_code)
                sqllist.append(f"{close_price[i]:.15f}")
                sqllist.append(close_time[i])
                sqllist.append(num_list[i])
                sqllist.append(stg_list[i])
                sqllist.append(rate_list[i])
                sqllist.append(winner_list[i])
                sqllist.append(top_list[i])
                sqllist.append(mid_list[i])
                sqllist.append(bot_list[i])

                sqltuple = tuple(sqllist)
                str1 += ",(%d,'%s',%s,'%s',%d,%d,%f,%f,%f,%f,%f)" % sqltuple

            sqlstr = "insert into stratage_detail_gate  VALUES " + str1[1:]
            self.ms.ExecNonQuery(sqlstr)
        except Exception as e:
            # print(sqlstr)
            print("执行stratage_detail_gate报异常：", e)
            self.ExceptionThrow(e)

    def UpdateBuyerStatusGateio(self,acct_id):
        try:
            #up ���加仓，对应 l，down是减仓，对应u
            sqlstr = "update acct_stg_buyer_gateio set init = 1 where acct_id = %d " % (acct_id)
            self.ms.ExecNonQuery(sqlstr)

        except Exception as e:
            print(e, "UpdateBuyerStatusGateio error...",sqlstr)
            self.ExceptionThrow(e)
    def UpdateBuyerStatusBinance(self,acct_id):
        try:
            #up 是加仓，对应 l，down是减仓，对应u
            sqlstr = "update acct_stg_buyer_binance set init = 1 where acct_id = %d " % (acct_id)
            self.ms.ExecNonQuery(sqlstr)

        except Exception as e:
            print(e, "UpdateBuyerStatusGateio error...",sqlstr)
            self.ExceptionThrow(e)
    def UpdateBuyerStatusOkex(self,acct_id):
        try:
            #up 是加仓，对应 l，down是减仓，对应u
            sqlstr = "update acct_stg_buyer_okex set init = 1 where acct_id = %d " % (acct_id)
            self.ms.ExecNonQuery(sqlstr)

        except Exception as e:
            print(e, "UpdateBuyerStatusOkex error...",sqlstr)
            self.ExceptionThrow(e)

    def UpdateBuyerStatusFuture(self,acct_id):
        try:
            #up 是加仓，对应 l，down是减仓，对应u
            sqlstr = "update acct_stg_future set init = 1 where acct_id = %d " % (acct_id)
            self.ms.ExecNonQuery(sqlstr)

        except Exception as e:
            print(e, "UpdateBuyerStatusGateio error...",sqlstr)
            self.ExceptionThrow(e)

    def UpdateStratageLatest(self,stratage_id, symbol,close_time, num,stg,close,rate,winner,top,mid,bot):

        try:
            sqlstr = "delete from stratage_latest  where product_code = '" + symbol + "' and stratage_id = "+str(stratage_id)
            self.ms.ExecNonQuery(sqlstr)

            str1 = ""
            sqllist = []
            sqllist.append(stratage_id)
            sqllist.append(symbol)

            sqllist.append(close_time)
            sqllist.append(num)
            sqllist.append(stg)
            sqllist.append(close)

            sqllist.append(rate)
            sqllist.append(winner)
            sqllist.append(top)
            sqllist.append(mid)
            sqllist.append(bot)

            sqltuple = tuple(sqllist)
            str1 += ",(%d,'%s','%s',%d,%d,%f,%f,%f,%f,%f,%f)" % sqltuple

            sqlstr = "insert into stratage_latest  VALUES " + str1[1:]
            self.ms.ExecNonQuery(sqlstr)
        except Exception as e:
            # print(sqlstr)
            print("执行UpdateStratageLatest报异常：", e)
            self.ExceptionThrow(e)

    def UpdateStratageLatestGate(self, stratage_id, symbol, close_time, num, stg, close, rate, winner, top, mid, bot):
        try:
            # 先尝试删除已存在的记录
            delete_sql = f"DELETE FROM stratage_latest_gate WHERE product_code = '{symbol}' AND stratage_id = {stratage_id}"
            self.ms.ExecNonQuery(delete_sql)

            # 然后插入新记录
            insert_sql = """
                INSERT INTO stratage_latest_gate 
                (stratage_id, product_code, stratage_time, num, stg, close, rate, winner, top, mid, but) 
                VALUES (%d, '%s', '%s', %d, %d, %s, %f, %f, %f, %f, %f)
            """
            params = (stratage_id, symbol, close_time, num, stg, f"{close:.15f}", 
                     rate, winner, top, mid, bot)
            
            self.ms.ExecNonQuery(insert_sql % params)

        except Exception as e:
            print(f"执行UpdateStratageLatestGate报异常：{str(e)}")
            self.ExceptionThrow(e)


    def QueryStratageProduct(self,stgID=1):
        result = []
        try:

            sqlstr = "select b.product_id,b.product_code,b.ctVal from stratage a , product b, stratage_product c where a.stratage_id = c.stratage_id and c.product_id = b.product_id and a.stratage_id = " + str(
                stgID)
            data = self.ms.ExecQuery(sqlstr)

            result = [itor for itor in data]
            return result
        except Exception as e:
            print("数据库查找QueryStratageProduct表，出现错误,语句为：" + sqlstr + "异常代码：", e)
            # print(e)
            self.ExceptionThrow(e)




    def DeleteIndex30MById(self,stratageID):
        try:
            sqlstr = "delete  from okex_index_30m where stratage_id = " + str(stratageID)
            self.ms.ExecNonQuery(sqlstr)

            sqlstr = "delete  from product_index where stratage_id = " + str(stratageID)
            self.ms.ExecNonQuery(sqlstr)

            #print("删除okex_index_30m/product_index 数据成功")
        except Exception as e:
            print("异常：DeleteIndex30MById，原因：", e,sqlstr)
            self.ExceptionThrow(e)


    def InsertPriceIndex(self,stratage_id,symbol_code,index_list,time_list):

        try:

            list_len = len(time_list)
            if list_len == 0:
                return

            str1 = ""
            sqlstr = ""
            for i in range(0, list_len):
                sqllist = []
                sqllist.append(stratage_id)
                sqllist.append(symbol_code)
                sqllist.append(index_list[i])
                sqllist.append(time_list[i])


                sqltuple = tuple(sqllist)
                str1 += ",(0,%d,'%s',%f,'%s')" % sqltuple

            sqlstr = "insert into product_index  VALUES " + str1[1:]
            self.ms.ExecNonQuery(sqlstr)
        except Exception as e:
            # print(sqlstr)
            print("执行InsertPriceIndex报异常：", e)
            self.ExceptionThrow(e)



    def InsertIndex30M(self,stratage_id,index_list,time_list):
        try:

            data_len = len(time_list)
            if data_len ==0 :
                return
            # 生成sql语句
            str1 = ""
            sqlstr = ""
            for i in range(0,data_len):
                sqllist = []
                sqllist.append(stratage_id)
                sqllist.append(index_list[i])
                sqllist.append(time_list[i])


                sqltuple = tuple(sqllist)
                str1 += ",(0,'%d',%f,'%s' )" % sqltuple

            sqlstr = "insert into okex_index_30m  VALUES " + str1[1:]
            self.ms.ExecNonQuery(sqlstr)

        except Exception as e:
            print("函数insertIndex30M抛出异常",e,sqlstr)
            self.ExceptionThrow(e)

    def QueryStratageDetailByID(self,symbol,stratage_id=1):
        # 选出策略信息最新的数据

        try:

            sqlstr = "select stratage_time, winner, stg, num from stratage_detail where product_code = '" + symbol + "' and stratage_id = " + str(
                stratage_id) + " order by stratage_time ASC"
            result = self.ms.ExecQuery(sqlstr)
            return result
        except Exception as e:
            print("异常：queryStratageDetailByID函数抛出，原因：", e, sqlstr)
            self.ExceptionThrow(e)
            return 0

    def QueryStratageDetailFromTime(self,symbol,max_time,stratage_id=1):
        # 选出策略信息最新的数据
        try:

            sqlstr = "select stratage_time, winner, stg, num from stratage_detail where product_code = '" + symbol + "' and stratage_id = " + str(
                stratage_id) + " and stratage_time > '" + max_time + "' order by stratage_time ASC"
            result = self.ms.ExecQuery(sqlstr)
            return result
        except Exception as e:
            print("异常：queryStratageDetailByID函数抛出，原因：", e, sqlstr)
            self.ExceptionThrow(e)
            return 0

    def InsertProfit30M(self,stratage_id,profit_time,long_num,short_num,total_num,total,sum,max_drawdown,current_drawdown,drawdown_time,risk):
        try:

            list_len = len(profit_time)
            if list_len == 0:
                return

            str1 = ""
            sqlstr = ""
            for i in range(0, list_len):
                sqllist = []
                sqllist.append(stratage_id)
                sqllist.append(profit_time[i])
                sqllist.append(long_num[i])
                sqllist.append(short_num[i])
                sqllist.append(total_num[i])
                sqllist.append(total[i])
                sqllist.append(sum[i])
                sqllist.append(max_drawdown[i])
                sqllist.append(current_drawdown[i])
                sqllist.append(drawdown_time[i])
                sqllist.append(risk[i])

                sqltuple = tuple(sqllist)
                str1 += ",(0,%d,'%s',%d,%d,%d,%f,%f,%f,%f,%f,%f)" % sqltuple

            sqlstr = "insert into okex_profit_30m  VALUES " + str1[1:]
            self.ms.ExecNonQuery(sqlstr)

            """
            list_len = len(profit_time)
            if list_len == 0:
                return
            update_data = []
            for i in range(0, list_len):
                line_data = [0,stratage_id,profit_time[i],long_num[i],short_num[i],total_num[i],total[i],sum[i],max_drawdown[i],current_drawdown[i],drawdown_time[i],risk[i]]
                update_data.append(line_data)
            sqlstr = "insert into okex_profit_30m(profit_id,stratage_id,profit_time,long_num,short_num,total_num,total,sum,max_drawdown,current_drawdown,drawdown_time,risk)  VALUES (0,%s,%s,%s,%s,%s,0,0,0,0,0,0)"
            print(sqlstr)
            print(update_data)
            self.ms.ExecNonQueryMany(sqlstr,update_data)
            """
        except Exception as e:

            line = e.__traceback__.tb_frame.f_globals[
                       "__file__"] + "异常发生在(行):%d," % e.__traceback__.tb_lineno + "错误原因:" + str(e)
            print(line)
            self.ExceptionThrow(e)

    def QueryMaxDateProfit30M(self,stratage_id):
        try:
            sqlstr = "SELECT max(profit_time) from okex_profit_30m where stratage_id = %d" % stratage_id

            ret_data = self.ms.ExecQuery(sqlstr)
            ret = [x[0] for x in ret_data]
            return ret
        except Exception as e:
            # print(sqlstr)
            print("QueryMaxDateProfit30M：", e)
            self.ExceptionThrow(e)

    def DeleteProfit30MById(self,stratageID):
        try:
            sqlstr = "delete  from okex_profit_30m where stratage_id = " + str(stratageID)
            self.ms.ExecNonQuery(sqlstr)

            print("删除Profit30数据成功")
        except Exception as e:
            print("异常：DeleteIndex30MById原因：", e,sqlstr)
            self.ExceptionThrow(e)

    def QueryIndex30M(self,stratage_id):

        try:
            sqlstr = "select index_data,index_time  from okex_index_30m where stratage_id = " + str(stratage_id) + " order by index_time asc "

            retData = self.ms.ExecQuery(sqlstr)
            ret = [x for x in retData]
            return ret
        except Exception as e:
            print("执行queryIndex30M抛出异常，原因是:",e)
            self.ExceptionThrow(e)
            #print(sqlstr)


    def QueryProductIndex30M(self,symbol_code,stratage_id=1):
        result = 0
        try:
            sqlstr = "select index_price,index_time  from product_index where stratage_id = " + str(stratage_id) + " and product_code ='"+symbol_code+"' order by index_time asc "

            retData = self.ms.ExecQuery(sqlstr)
            result = retData
        except Exception as e:
            print("执行queryIndex30M抛出异常，原因是:",e)
            self.ExceptionThrow(e)
            #print(sqlstr)

        return result

    def QueryProfit30M(self,stratage_id):
        try:
            sqlstr = "select profit_time,long_num,short_num,total_num,total,sum,max_drawdown,current_drawdown,drawdown_time,risk from okex_profit_30m where stratage_id ="+str(stratage_id)+" order by profit_time ASC"
            retData = self.ms.ExecQuery(sqlstr)
            ret = [x for x in retData]
            return ret
        except Exception as e:
            print("执行QueryProfit30M抛出异常，原因是:",e,sqlstr)

    def QueryLevelLastest(self,stratage_id):
        try:
            sqlstr = "select day,rate_time,level from acct_level where rate_time = (select max(rate_time) from acct_level where stratage_id ="+str(stratage_id) + ") and stratage_id = " +  str(stratage_id)
            retData = self.ms.ExecQuery(sqlstr)
            ret = retData
            return ret
        except Exception as e:
            print("执行QueryLevelLastest，原因是:",e,sqlstr)
            self.ExceptionThrow(e)

    def InsertlevelInfo(self,stratage_id, day_list, target_list, level_list, last_level_list, rate_list,rate_time_list):
        try:
            list_len = len(day_list)
            if list_len == 0:
                return

            str1 = ""
            sqlstr = ""
            for i in range(0, list_len):
                sqllist = []
                sqllist.append(day_list[i])
                sqllist.append(target_list[i])
                sqllist.append(level_list[i])
                sqllist.append(last_level_list[i])
                sqllist.append(rate_list[i])
                sqllist.append(rate_time_list[i])
                sqllist.append(stratage_id)

                sqltuple = tuple(sqllist)
                str1 += ",(%d,%d,%d,%d,%f,'%s',%d)" % sqltuple

            sqlstr = "insert into acct_level  VALUES " + str1[1:]
            self.ms.ExecNonQuery(sqlstr)
        except Exception as e:
            print("InsertlevelInfo：" + sqlstr + "异常代码：", e)
            self.ExceptionThrow(e)


    def QueryStratageDetailProduct(self,stratage_id=1):

        result = []
        try:

            sqlstr = "select product_code, stg,num, mid  from stratage_detail where stratage_time = (select max(stratage_time) from stratage_detail) and stg in (1,-1,2,-2) and stratage_id = " + str(stratage_id)

            data = self.ms.ExecQuery(sqlstr)

            result = [itor for itor in data]

        except Exception as e:
            print("数据库查找queryStratageDetailProduct，出现错误,语句为：" + sqlstr + "异常代码：", e)
            self.ExceptionThrow(e)
            # print(e)

        return result

    def QueryLatestStratage(self,stg_id=1):

        try:

            sqlstr = "select stratage_id,product_code,stratage_time,close, stg,num, winner  from stratage_latest where stratage_id = "+str(stg_id)+" order by product_code DESC"

            result = self.ms.ExecQuery(sqlstr)
            return result

        except Exception as e:
            self.ExceptionThrow(e)




    def UpdateAcctStratage(self,acct_id, money,level,l_m,l_l,u_m,u_l,status):
        try:
            #up 是加仓，对应 l，down是减仓，对应u
            sqlstr = "update acct_stratage set money = %f,level = %f,up_money= %f,up_level=%f,down_money = %f,down_level = %f,status = %d where acct_id = %d " % (money,level,l_m,l_l,u_m,u_l,status,acct_id)
            #print(sqlstr)
            self.ms.ExecNonQuery(sqlstr)

        except Exception as e:
            print(e, "UpdateAcctStratage error...",sqlstr)
            self.ExceptionThrow(e)


    def QueryAllAcctInfoDetail(self):
        result = []
        try:

            sqlstr = "SELECT	a.memo,	a.apikey,	a.secretkey,	a.apipass,	b.money,	b.`level`,b.up_money,	b.up_level,b.down_money,	b.down_level,	b.STATUS,	a.acct_id,	c.total_eq,	c.afterlevel_eq,	c.future_eq FROM	acct_info a	LEFT JOIN acct_stratage b ON a.acct_id = b.acct_id	LEFT JOIN acct_money c ON a.acct_id = c.acct_id WHERE	b.stratage_id = 1 	AND a.state = 1"
            data = self.ms.ExecQuery(sqlstr)
            result = data

        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e, "queryAllAcctInfoByGroup error...",sqlstr)
            self.ExceptionThrow(e)

        return result

    def QueryAllAcctFollow(self):
        result = []
        try:

            sqlstr = "select acct_id,stratage_list,product_list,money,product_nums from acct_stg_comb "
            data = self.ms.ExecQuery(sqlstr)
            result = data

        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e, "queryAllAcctInfoByGroup error...",sqlstr)
            self.ExceptionThrow(e)

        return result

    def QueryAllAcctFollowBuyer(self):
        result = []
        try:

            sqlstr = "select acct_id,product_list,discount,money,win_rate,init,dixi,dixi_rate,name,isolate_mode from acct_stg_buyer_okex where status = 1"
            ret = self.ms.ExecQuery(sqlstr)
            for data in ret:
                record = {'acct_id':data[0],'product_list':data[1],'discount':data[2],'money':data[3],'win_rate':data[4],'init':data[5],'dixi':data[6],'dixi_rate':data[7],'name':data[8],'isolate_mode':data[9]}
                result.append(record)


        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e, "QueryAllAcctFollowBuyer error...",sqlstr)
            self.ExceptionThrow(e)

        return result

    def InsertInfoRecord(self, info_list):
        try:
            # 生成sql语句
            str1 = ""
            sqlstr = ""
            for itor in info_list:
                sqllist = []
                sqllist.append(itor[0])
                sqllist.append(itor[1])
                sqllist.append(itor[2])
                sqllist.append(itor[3])
                sqllist.append(itor[4])
                sqltuple = tuple(sqllist)
                str1 += ",(%d,'%s','%s',%f,%f)" % sqltuple

            sqlstr = "insert into info_record  VALUES " + str1[1:]
            self.ms.ExecNonQuery(sqlstr)
        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e, "InsertInfoRecord error...", sqlstr)
            self.ExceptionThrow(e)


    def QueryProductInfoRecord(self,acct_id,symbol):
        result = []
        try:

            sqlstr = "select change_time,nums from info_record where acct_id = "+str(acct_id)+" and symbol='"+symbol+"' order by change_time asc"
            data = self.ms.ExecQuery(sqlstr)
            result = data

        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e, "QueryProductInfoRecord error...",sqlstr)
            self.ExceptionThrow(e)

        return result

    def QueryAllAcctFollowBuyerDixi(self):
        result = []
        try:

            sqlstr = "select acct_id,product_list,min_days,rate_days,money_days,win_rate_days,big_cycle,small_cycle,rate_cycle,win_rate_cycle,money_cycle from acct_stg_buyer_dixi "
            data = self.ms.ExecQuery(sqlstr)
            for itor in data:
                record = {'acct_id':itor[0],'product_list':itor[1],'min_days':itor[2],'rate_days':itor[3],'money_dyas':itor[4],'win_rate_days':itor[5],'big_cycle':itor[6],'small_cycle':itor[7],'rate_cycle':itor[8],'win_rate_cycle':itor[9],'money_cycle':itor[10]}
                result.append(record)

        except Exception as e:

            print(e, "QueryAllAcctFollowBuyerDixi error...", sqlstr)
            self.ExceptionThrow(e)

        return result

    def QueryProductTimeList(self,stg_id=1):
        result = []
        try:

            sqlstr = "select distinct stratage_time  from stratage_detail where stratage_id = "+str(stg_id)+" order by stratage_time asc "
            data = self.ms.ExecQuery(sqlstr)
            result = data

        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e, "QueryProductTimeList error...",sqlstr)
            self.ExceptionThrow(e)

        return result

    def QueryAllAcctFollowBuyerBinance(self):
        result = []
        try:

            sqlstr = "select acct_id,discount,product_list,money,win_rate,init,dixi,dixi_rate,name,isolate_mode from acct_stg_buyer_binance  where status = 1"
            data = self.ms.ExecQuery(sqlstr)
            result = data

        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错,语句为："+sqlstr)
            print(e, "QueryAllAcctFollowBuyerBinance error...",sqlstr)
            self.ExceptionThrow(e)

        return result

    def QueryProductDataKLinesGateio(self,symbol):

        result = []
        try:

            sqlstr = "select price_time,open,high,low,close from gate_price_30m where product_code = '%s' order by price_time asc"%symbol
            data = self.ms.ExecQuery(sqlstr)
            for itor in data:
                data_map = {'price_time': itor[0], 'open': itor[1], 'high': itor[2], 'low': itor[3],
                            'close': itor[4]}
                result.append(data_map)

        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e, "QueryProductDataKLinesGateio error...", sqlstr)
            self.ExceptionThrow(e)


        return result


    def QueryAllAcctFollowBuyerGateio(self):
        result = []
        try:

            sqlstr = "select acct_id,discount,product_list,money,win_rate,init,dixi,dixi_rate,name,isolate_mode from acct_stg_buyer_gateio  where status = 1"
            data = self.ms.ExecQuery(sqlstr)
            result = data

        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e, "QueryAllAcctFollowBuyerGateio error...",sqlstr)
            self.ExceptionThrow(e)

        return result

    def QueryAllAcctFollowSellerGateio(self):
        result = []
        try:

            sqlstr = "select acct_id,discount,product_list,money,win_rate,init,dixi,dixi_rate,name from acct_stg_seller_gateio  where status = 1"
            data = self.ms.ExecQuery(sqlstr)
            result = data

        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e, "QueryAllAcctFollowSellerGateio error...",sqlstr)
            self.ExceptionThrow(e)

        return result

    def QueryAllAcctFollowFutureGateio(self):
        result = []
        try:

            sqlstr = "select a.acct_id,b.comb_name,a.money,a.name,a.discount,a.product_nums,a.init from acct_stg_future_gateio a, stg_comb_product_gateio b  where a.status = 1 and b.product_comb = a.product_list"
            data = self.ms.ExecQuery(sqlstr)
            for itor in data:
                data_map = {'acct_id':itor[0],'product_list':itor[1],'money':itor[2],'name':itor[3],'percentage':itor[4],'product_nums':itor[5],'init':itor[6]}
                result.append(data_map)

        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e, "QueryAllAcctFollowFutureGateio error...",sqlstr)
            self.ExceptionThrow(e)

        return result

    def QueryAllAcctFollowFuture(self):
        result = []
        try:

            sqlstr = "select acct_id,leverage,product_list,money,product_nums,discout,init from acct_stg_future "
            data = self.ms.ExecQuery(sqlstr)
            result = data

        except Exception as e:
            # print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e, "queryAllAcctInfoByGroup error...",sqlstr)
            self.ExceptionThrow(e)

        return result

    def QueryAllAcctInfo(self):

        result = []
        try:

            sqlstr = "select c.acct_id,c.memo,c.apikey,c.secretkey,c.apipass,c.acct_name,d.init_money, d.money, a.total_eq,a.afterlevel_eq, a.record_time,a.future_eq  from acct_info c,acct_stratage d,acct_money a, (select acct_id, max(record_time) max_time from acct_money group by acct_id ) b where c.state = 1 and c.group_id =  2 and d.stratage_id = 1 and c.acct_id = d.acct_id and a.acct_id = b.acct_id and a.record_time = b.max_time and a.acct_id = c.acct_id order by a.acct_id ASC "
            data = self.ms.ExecQuery(sqlstr)
            #print(data)
            result = data

        except Exception as e:
            #print("queryAcctInfoByGroup，"+groupID+"出现错误,语句为："+sqlstr)
            print(e,"queryAllAcctInfoByGroup error...")
            self.ExceptionThrow(e)

        return result

    def QueryStratageHolding(self):

        result = []
        try:

            sqlstr = "select a.product_code, a.stg,a.num, b.ctVal,a.stratage_time  from stratage_detail a,product b  where stratage_time = (select max(stratage_time) from stratage_detail)  and a.product_code = b.product_code"

            data = self.ms.ExecQuery(sqlstr)

            result = [itor for itor in data]

        except Exception as e:
            print("数据库查找queryStratageHolding，出现错误,语句为：" + sqlstr + "异常代码：", e)
            # print(e)
            self.ExceptionThrow(e)

        return result

    def InsertAcctMoney(self,newData, del_old=False):
        try:
            if del_old:
                pass
                #deleteAcctMoney(False)

            # 生成sql语句
            str1 = ""
            sqlstr = ""
            for itor in newData:
                sqllist = []
                sqllist.append(itor[0])
                sqllist.append(itor[1])
                sqllist.append(itor[2])
                sqllist.append(itor[3])
                sqllist.append(itor[4])
                sqltuple = tuple(sqllist)
                str1 += ",(0,%d,'%s',%f,%f,%f)" % sqltuple

            sqlstr = "replace into acct_money  VALUES " + str1[1:]
            self.ms.ExecNonQuery(sqlstr)
        except Exception as e:
            #print(sqlstr)
            print("执行insertAcctMoney抛出异常，原因是:", e)
            self.ExceptionThrow(e)

    def QueryProductGroup(self,group_name="A25"):
        try:
            sqlstr = "select name, product_list from product_group where name = '" + group_name +"'"
            ret = self.ms.ExecQuery(sqlstr)

            detail_dict = {'name':ret[0][0],'product_list':ret[0][1]}

            return detail_dict
        except Exception as e:
            print("执行QueryStratageDetail抛出异常，原因是:", e,sqlstr)

    def QueryStratageDetail(self,stg_id= 1,product_str="" ):
        try:
            sqlstr = "select sum(winner) sum_win, stratage_time  from stratage_detail where stratage_id ="+str(stg_id)+" and product_code in ( "+product_str+" )  group by stratage_time "
            ret = self.ms.ExecQuery(sqlstr)
            ret_list = []
            for itor in ret:
                detail_dict = {'stratage_time':itor[1],'winner_sum':itor[0]}
                ret_list.append(detail_dict)
            return ret_list
        except Exception as e:
            print("执行QueryStratageDetail抛出异常，原因是:", e,sqlstr)

    def DeleteAcctMoney(self,bDelAll=True, fieldname="", rawData=[]):

        try:
            if bDelAll:
                sqlstr = "delete  from acct_money where record_time <= UNIX_TIMESTAMP(DATE_ADD(CURRENT_DATE,INTERVAL -2 DAY))"
                # print(sqlstr)
                self.ms.ExecNonQuery(sqlstr)
            else:
                # 删除指定字段
                str1 = ""
                for itor in rawData:
                    sqllist = []
                    sqllist.append(itor[0])

                    sqltuple = tuple(sqllist)
                    str1 += ", '%s'" % sqltuple
                sqlstr = "delete from acct_money where " + fieldname + " in (" + str1[1:] + ")"
                # print(sqlstr)
                self.ms.ExecNonQuery(sqlstr)

            print("删除历史数据成功")
        except Exception as e:
            print("执行deleteAcctMoney抛出异常，原因是:", e)
            self.ExceptionThrow(e)

    def QueryAllAcctMoney(self):
        try:
            sqlstr = "select b.acct_name,a.afterlevel_eq,a.total_eq,a.record_time,round(a.afterlevel_eq/a.total_eq,2) as rate from acct_info b left join acct_money a on a.acct_id = b.acct_id where  b.state = 1 order by b.acct_name "
            ret = self.ms.ExecQuery(sqlstr)
            return ret
        except Exception as e:
            print("执行queryAcctMoney抛出异常，原因是:", e,sqlstr)

    def QueryLatestProfit(self,stratage_id=1,nums=1):
        try:

            sqlstr = "select long_num,short_num,current_drawdown,risk,max_drawdown,sum,profit_time from okex_profit_30m where stratage_id = "+str(stratage_id)+" order by profit_time desc limit "+str(nums)
            ret = self.ms.ExecQuery(sqlstr)
            return ret
        except Exception as e:
            print("执行QueryLatestProfit抛出异常，原因是:", e, sqlstr)

    def QueryMaxDateAcctMoney(self):
        result = 0
        try:
            sqlstr = "select max(record_time)  from acct_money"

            retData = self.ms.ExecQuery(sqlstr)
            if retData[0][0] is None:
                result = ""
            else:
                result = retData[0]

        except Exception as e:
            print("执行queryMaxDateAcctMoney抛出异常，原因是:",e)
            print(sqlstr)

        return result

    def UpdateWatchApp(self, app_name):
        """
        更新应用运行状态，如果记录不存在则创建新记录
        """
        try:
            # 首先检查记录是否存在
            check_sql = f"SELECT COUNT(*) FROM watch_app WHERE app_name = '{app_name}'"
            result = self.ms.ExecQuery(check_sql)
            
            if result[0][0] > 0:
                # 记录存在，更新状态和时间
                update_sql = f"""
                    UPDATE watch_app 
                    SET status = 1, 
                        status_time = NOW(),
                        back_status = 0,
                        back_status_time = NOW()
                    WHERE app_name = '{app_name}'
                """
                self.ms.ExecNonQuery(update_sql)
            else:
                # 记录不存在，创建新记录
                insert_sql = f"""
                    INSERT INTO watch_app 
                    (server_name, app_name, status, status_time, back_server_name, back_status, back_status_time)
                    VALUES 
                    ('main', '{app_name}', 1, NOW(), 'backup', 0, NOW())
                """
                self.ms.ExecNonQuery(insert_sql)
                
            #print(f"更新 {app_name} 状态成功")
                
        except Exception as e:
            print(f"UpdateWatchApp error: {str(e)}")
            raise e

    def QueryWatchApp(self, app_name):
        """
        查询应用运行状态
        """
        try:
            sqlstr = f"""
                SELECT server_name, app_name, status, status_time, 
                       back_server_name, back_status, back_status_time 
                FROM watch_app 
                WHERE app_name = '{app_name}'
            """
            ret = self.ms.ExecQuery(sqlstr)
            if not ret:
                return None
                
            return {
                'server': ret[0][0],
                'app_name': ret[0][1],
                'status': ret[0][2],
                'status_time': ret[0][3],
                'back_server': ret[0][4],
                'back_status': ret[0][5],
                'back_status_time': ret[0][6]
            }
            
        except Exception as e:
            print(f"QueryWatchApp error: {str(e)}")
            raise e

    def CleanupWatchApp(self, app_name, days=7):
        """
        清理 watch_app 表中的历史记录
        """
        try:
            # 删除旧记录
            sqlstr = f"""
                DELETE FROM watch_app 
                WHERE app_name = '{app_name}'
                AND status_time < DATE_SUB(NOW(), INTERVAL {days} DAY)
            """
            self.ms.ExecNonQuery(sqlstr)
            
            # 只保留最新的一条记录
            sqlstr = f"""
                DELETE w1 FROM watch_app w1
                INNER JOIN watch_app w2
                WHERE w1.app_name = '{app_name}'
                AND w2.app_name = w1.app_name
                AND w1.status_time < w2.status_time
            """
            self.ms.ExecNonQuery(sqlstr)
            
            print(f"清理 {app_name} 历史记录完成")
            
        except Exception as e:
            print(f"CleanupWatchApp error: {str(e)}")
            raise e

    def UpdateWatchAppBack(self, app_name):
        """
        更新备份服务器的运行状态
        """
        try:
            # 首先检查记录是否存在
            check_sql = "SELECT COUNT(*) FROM watch_app WHERE app_name = %s"
            result = self.ms.ExecQuery(check_sql, (app_name,))
            
            if result[0][0] > 0:
                # 记录存在，更新备份状态和时间
                update_sql = """
                    UPDATE watch_app 
                    SET back_status = 1, 
                        back_status_time = NOW(),
                        status = 0,
                        status_time = NOW()
                    WHERE app_name = %s
                """
                self.ms.ExecNonQuery(update_sql, (app_name,))
            else:
                # 记录不存在，创建新记录
                insert_sql = """
                    INSERT INTO watch_app 
                    (server_name, app_name, status, status_time, back_server_name, back_status, back_status_time)
                    VALUES 
                    ('main', %s, 0, NOW(), 'backup', 1, NOW())
                """
                self.ms.ExecNonQuery(insert_sql, (app_name,))
                
            print(f"更新备份服务器 {app_name} 状态成功")
                
        except Exception as e:
            print(f"UpdateWatchAppBack error: {str(e)}")
            raise e

