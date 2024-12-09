from gate_api import ApiClient, Configuration, SpotApi, FuturesApi
from BASECLASS.baseclass import BaseClass
from enum import Enum

# 定义一个枚举类
class Stg:
    EMPTY = 0
    LONGIN = 1
    LONGHOLD = 2
    LONGQUIT = 3
    SHORTIN = -1
    SHORTHOLD = -2
    SHORTQUIT = -3
    ZERO = 0
    MAXINT = 9999999
class ExchangeGatieio(BaseClass):
    def __init__(self):
        pass

    def GetExchangeGateioSpot(self, target_acct):
        # 从数据库读取账户记录,不带参数是返回全部记录
        try:

            apiKey = target_acct['apiKey']
            secret = target_acct['secret']

            config = Configuration(key=apiKey, secret=secret)
            exchange = SpotApi(ApiClient(config))

            return exchange

        except Exception as e:
            self.ExceptionThrow(e)

    def GetExchangeGateioFuture(self, target_acct):
        # 从数据库读取账户记录,不带参数是返回全部记录
        try:

            apiKey = target_acct['apiKey']
            secret = target_acct['secret']

            config = Configuration(key=apiKey, secret=secret)
            exchange = FuturesApi(ApiClient(config))

            return exchange

        except Exception as e:
            self.ExceptionThrow(e)