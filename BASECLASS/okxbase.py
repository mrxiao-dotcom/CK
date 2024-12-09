#!/user/bin/env python3
# -*- coding: utf-8 -*-
from BASECLASS import baseclass
import okx.Funding_api as Funding
import okx.Market_api as MarketData
import okx.Account_api as Account
import okx.Public_api as PublicData

class ExchangeGatieio(baseClass):
    def __init__(self):
        pass

    def GetfundingAPI (self, target_acct):
        try:

            api_key = target_acct['apiKey']
            secret_key = target_acct['secret']
            passphrase = target_acct['password']
            flag = "0"  # live trading:0
            fundingAPI  = Funding.FundingAPI(api_key, secret_key, passphrase, False, flag)
            return fundingAPI
        except Exception as e:
            self.ExceptionThrow(e)

    def GetmarketDataAPI (self):
        try:

            flag = "0"  # live trading:0
            marketDataAPI  = MarketData.MarketAPI(flag = flag)
            return marketDataAPI
        except Exception as e:
            self.ExceptionThrow(e)

    def GetaccountAPI (self,target_acct):
        try:
            api_key = target_acct['apiKey']
            secret_key = target_acct['secret']
            passphrase = target_acct['password']
            flag = "0"  # live trading:0
            accountAPI  = Account.AccountAPI(api_key, secret_key, passphrase, False, flag)
            return accountAPI
        except Exception as e:
            self.ExceptionThrow(e)

    def GetpublicDataAPI (self):
        try:

            flag = "0"  # live trading:0
            publicDataAPI  = PublicData.PublicAPI(flag = flag)
            return publicDataAPI
        except Exception as e:
            self.ExceptionThrow(e)
