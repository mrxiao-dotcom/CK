#version 20230224

import ccxt  # noqa: E402
from ccxt.base.exchange import Exchange  # noqa: E402
import time
import datetime

class ohlcv(Exchange):

    def fetch_instruments(self,symbol):
        # 取名称
        symbolstr = symbol[0:symbol.rfind('/', 1)]

        # 获得合约面值
        data = self.public_get_public_instruments(params={
            "instType": "SWAP",
            "uly": symbolstr + "-USDT",
            "instId": symbolstr + "-USDT-SWAP"
        })
        return  data


    def fetch_instruments_spot(self,symbol):

        # 获得合约面值
        data = self.public_get_public_instruments(params={
            "instType": "SPOT",
            "instId": symbol + "-USDT",

        })
        return  data

    def fetch_ctVal(self,symbol):
        # 取名称
        symbolstr = symbol[0:symbol.rfind('/', 1)]

        # 获得合约面值
        data = self.public_get_public_instruments(params={
            "instType": "SWAP",
            "uly": symbolstr + "-USDT",
            "instId": symbolstr + "-USDT-SWAP"
        })
        ctVal = float(data['data'][0]['ctVal'])
        return  ctVal

    def fetch_Ndays_ohlcvs(self, symbol, timeframe, starttimestamp, endtimestamp, max_retries=3):

        self.load_markets()
        limit = 100

        # 先获得时间数组格式的日期
        earliest_timestamp = starttimestamp
        end_timestamp = endtimestamp

        timeframe_duration_in_seconds = self.parse_timeframe(timeframe)
        timeframe_duration_in_ms = timeframe_duration_in_seconds * 1000

        timedelta = limit * timeframe_duration_in_ms

        ohlcv_dictionary = {}
        ohlcv_list = []

        i = 0
        done = False
        while True:
            # this printout is here for explanation purposes

            fetch_since = end_timestamp - timedelta
            num_retries = 0
            try:
                num_retries += 1
                ohlcv = self.fetch_ohlcv(symbol, timeframe, fetch_since, limit)

                if (len(ohlcv)):

                    end_timestamp = ohlcv[0][0]
                    # print('Fetched', len(ohlcv), self.id, symbol, timeframe, 'candles from', ohlcv[0][0], 'to', ohlcv[-1][0],'distance:', str(int(ohlcv[-1][0])-int(ohlcv[0][0])))
                    if earliest_timestamp > end_timestamp:
                        done = True
                else:
                    # print('Fetched', len(ohlcv), self.id, symbol, timeframe, 'candles')
                    done = True
            except Exception as e:
                print(e)
                if num_retries > max_retries:
                    raise
                else:
                    continue
            i += 1
            ohlcv_dictionary = self.extend(ohlcv_dictionary, self.indexBy(ohlcv, 0))
            ohlcv_list = self.sort_by(ohlcv_dictionary.values(), 0)

            if done:
                # print('Stored', len(ohlcv_list), self.id, symbol, timeframe, 'candles from', self.iso8601(ohlcv_list[0][0]), 'to', self.iso8601(ohlcv_list[-1][0]))
                break
        # print(ohlcv_list)
        # print(len(ohlcv_list))
        ohlcv_list = [i for i in ohlcv_list if i[0] >= earliest_timestamp]
        # print(len(ohlcv_list))
        # print('Stored', len(ohlcv_list), self.id, symbol, timeframe, 'candles from', ohlcv_list[0][0], 'to', ohlcv_list[-1][0])
        return ohlcv_list



    def fetch_total_balance(self):

        balance=[]
        try:
            balance = self.private_get_account_balance()
            #print(balance)
        except Exception as e:
            print('fetch_balance() failed')
            print(e)
            return 0
        return balance

    def fetch_account_balance(self):

        balance=[]
        try:
            balance = self.fetch_positions()
            #print(balance)
        except Exception as e:
            print('fetch_balance() failed')
            print(e)
            return 0
        return balance


    def fetch_today_open(self,symbol,max_retries=3):

        self.load_markets()
        limit = 24
        timeframe = '1h'
        since_timestamp = int(time.mktime(datetime.date.today().timetuple()))*1000

        openprice = 0.00
        done = False
        while True:
            num_retries = 0
            try:
                num_retries = num_retries + 1
                ohlcv = self.fetch_ohlcv(symbol, timeframe, since_timestamp, limit)

                if len(ohlcv)>0 :
                    openprice = ohlcv[0][1]
                    done = True
                    #print('Fetched ... '+str(num_retries))
                else:
                    print('Fetched ... none! Try again')

            except Exception as e:
                print(e)

                if num_retries > max_retries:
                    raise
                else:
                    continue
            if done:
                break
        #print('获得',symbol,'今天开盘价',openprice)
        return openprice

# Another example of OOP / class inheritance.
# This time my_okex class is inherited from two other classes
# both ohlcv and ccxt.okex, and has the methods from both classes.
# This is just an example, it is not necessary do it this way.
# You can combine classes and methods using Python's OOP how you like.

class my_okex(ohlcv, ccxt.okex):
    pass

def getExchange(acctData):
    # 从数据库读取账户记录,不带参数是返回全部记录
    apiKey = acctData[2]
    secret = acctData[3]
    password = acctData[4]

    exchange = my_okex({
        'asyncio_loop': 'loop',
        'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
        'apiKey': apiKey,  # https://github.com/ccxt/ccxt/wiki/Manual#authentication
        'secret': secret,
        'password': password,
        'options': {
            'defaultType': 'futures',
        },
    })

    return exchange

#根据参数直接查找
def getExchangeD(apiKey,secret,password):
    # 从数据库读取账户记录,不带参数是返回全部记录
    exchange = my_okex({
        'asyncio_loop': 'loop',
        'enableRateLimit': True,  # https://github.com/ccxt/ccxt/wiki/Manual#rate-limit
        'apiKey': apiKey,  # https://github.com/ccxt/ccxt/wiki/Manual#authentication
        'secret': secret,
        'password': password,
        'options': {
            'defaultType': 'futures',
        },
    })

    return exchange