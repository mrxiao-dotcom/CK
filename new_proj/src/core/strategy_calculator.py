#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List, Dict, Optional, Tuple, Union
from datetime import datetime, timedelta
import threading
from queue import Queue
import logging
from utils.config_manager import ConfigManager
from utils.log_helper import setup_module_logger
from database.db_connector import DatabaseConnector
import time
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from decimal import Decimal
import math
import requests
from gate_api import ApiClient, Configuration, FuturesApi

class StrategyType:
    """策略状态枚举"""
    EMPTY = 0      # 空仓
    LONG_IN = 1    # 多头开仓
    LONG_HOLD = 2  # 多头持仓
    LONG_OUT = 3   # 多头平仓
    SHORT_IN = -1  # 空头开仓
    SHORT_HOLD = -2  # 空头持仓
    SHORT_OUT = -3  # 空头平仓
    ZERO = Decimal('0')
    MAXINT = Decimal('999999')

class StrategyCalculator:
    """策略计算器"""
    # 类变量，用于缓存合约面值
    _contract_sizes_cache = {}
    _default_contract_size = 1.0
    _is_cache_initialized = False
    _cache_lock = threading.Lock()
    
    # 默认合约面值配置
    _default_sizes = {
        'BTC': 0.0001,  # 0.0001 BTC
        'ETH': 0.01,    # 0.01 ETH
        'BNB': 0.1,     # 0.1 BNB
        'ADA': 10,      # 10 ADA
        'DOGE': 100,    # 100 DOGE
        'XRP': 10,      # 10 XRP
        'DOT': 1,       # 1 DOT
        'SOL': 1,       # 1 SOL
        'MATIC': 10,    # 10 MATIC
        'BTT': 1000000  # 100万 BTT
    }
    
    def __init__(self):
        self.logger = setup_module_logger("strategy_calculator")
        self.is_running = False
        self._lock = threading.Lock()
        self.db = DatabaseConnector()
        self.all_symbols = []
        
        # 使用配置管理器
        self.config = ConfigManager()
        self.server = self.config.server
        self.db_config = self.config.database
        
        # 初始化交易所API
        try:
            api_config = self.config.get_api_config()
            configuration = Configuration(
                key=api_config['key'],
                secret=api_config['secret'],
                host="https://api.gateio.ws/api/v4"
            )
            api_client = ApiClient(configuration)
            self.exchange = FuturesApi(api_client)
        except Exception as e:
            self.logger.error(f"初始化交易所API失败: {str(e)}")
            self.exchange = None
        
        # 策略相关配置
        self.day_k_nums = 48  # 一天的K线数量
        self.strategy_money = 10000  # 每个品种的资金额度
        self.strategy_queue = Queue()  # 策略计算队列
        self.last_update_count = 0  # 新增：记录最近一次更新的K线数量
        
    def start(self):
        """启动策略计算器"""
        try:
            self.logger.info("正在启动策略计算器...")
            
            # 初始化数据库连接
            if not self.db.initialize(self.db_config['source']):
                raise RuntimeError("数据库初始化失败")
            
            # 获取所有可交易品种
            self.all_symbols = self._get_all_symbols()
            
            # 启动策略计算
            self.is_running = True
            
            self.logger.info("策略计算器启动成功")
            return True
            
        except Exception as e:
            self.logger.error(f"策略计算器启动失败: {str(e)}")
            return False
            
    def _get_all_symbols(self) -> List[str]:
        """从数据库获取所有可交易品种"""
        try:
            self.logger.info("正在查询可交易品种...")
            symbols = self.db.get_all_tradable_symbols()
            
            if not symbols:
                self.logger.warning("未找到任何可交易品种")
                return []
            
            self.logger.info(f"找到 {len(symbols)} 个可交易品种: {sorted(symbols)}")
            return symbols
            
        except Exception as e:
            self.logger.error(f"获取可交易品种失败: {str(e)}")
            return []
            
    def initialize(self) -> bool:
        """初始化计算器"""
        try:
            if not self.db.initialize(1):
                self.logger.error("数据库初始化失败")
                return False
                
            # 加载合约面值信息
            self._load_contract_sizes()
            
            self.is_running = True
            return True
        except Exception as e:
            self.logger.error(f"初始化失败: {str(e)}")
            return False
            
    def _load_contract_sizes(self):
        """加载合约面值信息（只在第一次调用时执行）"""
        with self._cache_lock:
            if self._is_cache_initialized:
                self.logger.debug("使用缓存的合约面值数据")
                return
            
            try:
                # 从 Gate.io API 获取合约信息
                if self.exchange:
                    try:
                        contracts = self.exchange.list_futures_contracts("usdt")
                        for contract in contracts:
                            symbol = contract.name.split('_')[0]
                            # 使用合约的最小交易单位作为面值
                            contract_size = float(contract.quanto_multiplier or 1.0)
                            self._contract_sizes_cache[symbol] = contract_size
                            self.logger.debug(f"从API获取合约面值 - {symbol}: {contract_size}")
                    except Exception as e:
                        self.logger.error(f"从API获取合约信息失败: {str(e)}")
                
                # 对于未能从API获取到的合约，使用默认值
                for symbol, size in self._default_sizes.items():
                    if symbol not in self._contract_sizes_cache:
                        self._contract_sizes_cache[symbol] = size
                        self.logger.debug(f"使用默认合约面值 - {symbol}: {size}")
                
                self.logger.info(f"已加载 {len(self._contract_sizes_cache)} 个合约面值信息")
                self._is_cache_initialized = True
                
            except Exception as e:
                self.logger.error(f"加载合约面值信息失败: {str(e)}")
                self._contract_sizes_cache = {}
            
    def _calculate_contract_num(self, symbol: str, price: Decimal) -> int:
        """计算合约数量
        合约数量 = 策略资金 / (合约面值 * 当前价格)
        例如：
        - 资金 10000 USDT
        - CRV 价格 0.654 USDT
        - 面值 0.1 CRV
        - 计算: 10000 / (0.654 * 0.1) = 152905 张
        """
        try:
            # 确保合约面值数据已加载
            if not self._is_cache_initialized:
                self._load_contract_sizes()
            
            # 获取合约面值，使用默认值作为后备
            contract_size = self._contract_sizes_cache.get(symbol, self._default_contract_size)
            
            # 计算合约数量前先检查价格和面值
            if price <= 0 or contract_size <= 0:
                self.logger.warning(f"{symbol}: 价格或面值异常 (价格: {price}, 面值: {contract_size})")
                return 0
            
            # 计算名义价值（一张合约的价值）
            nominal_value = float(price) * contract_size
            
            # 计算合约数量
            # 策略资金 / (合约面值 * 当前价格) = 可买合约数量
            num = int(self.strategy_money / nominal_value)
            
            return num
            
        except Exception as e:
            self.logger.error(f"{symbol}: 计算合约数量失败 - {str(e)}")
            return 0
            
    def calculate_batch_strategies(self, symbols: List[str], strategy_cache: Dict = None) -> Dict[str, Union[bool, str]]:
        """批量计算多个品种的策略"""
        try:
            if not self.is_running:
                raise RuntimeError("策略计算器未启动")
            
            # 1. 获取当前最新K线时间
            now = datetime.now()
            current_minute = now.minute
            
            if current_minute < 30:
                latest_k_time = now.replace(minute=30, second=0, microsecond=0) - timedelta(hours=1)
                if now.hour == 0:
                    latest_k_time = latest_k_time.replace(hour=23) - timedelta(days=1)
            else:
                latest_k_time = now.replace(minute=0, second=0, microsecond=0)
            
            # 2. 使用线程池并行处理
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = {
                    executor.submit(self._process_single_strategy, 
                                  symbol, strategy_cache, latest_k_time): symbol 
                    for symbol in symbols
                }
                
                # 收集结果
                results = {}
                for future in as_completed(futures):
                    symbol = futures[future]
                    try:
                        result, update_count = future.result()
                        results[symbol] = result
                        if result is True:
                            self.last_update_count = update_count
                    except Exception as e:
                        self.logger.error(f"处理 {symbol} 失败: {str(e)}")
                        results[symbol] = False
                    
            return results
            
        except Exception as e:
            self.logger.error(f"批量计算策略失败: {str(e)}")
            return {symbol: False for symbol in symbols}

    def _process_single_strategy(self, symbol: str, strategy_cache: Dict, latest_k_time: datetime) -> Tuple[Union[bool, str], int]:
        """处理单个品种的策略计算"""
        try:
            # 1. 从缓存或数据库获取策略状态
            last_strategy = strategy_cache.get(symbol) if strategy_cache else None
            if not last_strategy:
                last_strategy = self.db.QueryStratageDetailLatestGateio(symbol)
            
            # 2. 检查是否需要更新
            if last_strategy and last_strategy['stratage_time'] >= latest_k_time:
                return True, 0  # 策略已是最新，静默返回
            
            # 3. 获取K线数据
            start_time = last_strategy['stratage_time'] if last_strategy else None
            candles = self.db.QueryProductDataPartGateio(symbol, start_time, None)
            
            if not candles:
                return True, 0  # 没有新数据，静默返回
            
            # 4. 处理首次计算的情况
            if not last_strategy:
                skip_days = 20
                skip_bars = skip_days * self.day_k_nums
                if len(candles) <= skip_bars:
                    return 'insufficient_data', 0
                start_idx = skip_bars
            else:
                start_idx = 1
            
            # 5. 计算更新的K线数量
            update_count = len(candles) - start_idx
            
            # 6. 计算并保存策略结果
            result = self._calculate_and_save_strategy(symbol, candles, start_idx, last_strategy)
            return result, update_count
            
        except Exception as e:
            self.logger.error(f"处理 {symbol} 策略失败: {str(e)}")
            return False, 0
            
    def _calculate_and_save_strategy(self, symbol: str, candles: List, start_idx: int, 
                                   last_strategy: Optional[Dict]) -> bool:
        """计算并保存策略结果"""
        try:
            # 初始化状态
            if last_strategy:
                # 使用上次策略的状态
                top = Decimal(str(last_strategy['top']))
                mid = Decimal(str(last_strategy['mid']))
                bot = Decimal(str(last_strategy['bot']))
                num = int(last_strategy['num'])
                stg = int(last_strategy['stg'])
                last_close = Decimal(str(last_strategy['close']))
            else:
                # 首次计算，使用前20天的数据计算初始状态
                history_prices = [Decimal(str(p[0])) for p in candles[start_idx-20*self.day_k_nums:start_idx]]
                top = max(history_prices)
                bot = min(history_prices)
                mid = (top + bot) / 2
                num = 0
                stg = StrategyType.EMPTY
                last_close = Decimal(str(candles[start_idx-1][0]))
                
            # 准备结果列表
            results = []
            
            # 计算每个K线的策略
            for i in range(start_idx, len(candles)):
                k_close = Decimal(str(candles[i][0]))
                k_time = candles[i][1]
                
                # 如果遇到跨日，重新计算top、mid、bot
                if k_time.hour == 0 and k_time.minute == 0:
                    history_prices = [Decimal(str(p[0])) for p in candles[max(0, i-20*self.day_k_nums):i]]
                    if history_prices:
                        top = max(history_prices)
                        bot = min(history_prices)
                        mid = (top + bot) / 2
                        
                # 计算策略
                result = {
                    'close': float(k_close),
                    'time': k_time,
                    'top': float(top),
                    'mid': float(mid),
                    'bot': float(bot),
                    'num': num,  # 使用当前持仓数量
                    'stg': int(stg),
                    'rate': 0.0,
                    'winner': 0.0
                }
                
                # 策略计算逻辑
                if stg == StrategyType.EMPTY:
                    if k_close > top:  # 突破上轨，开多
                        result['stg'] = StrategyType.LONG_IN
                        result['num'] = self._calculate_contract_num(symbol, k_close)
                    elif k_close < bot:  # 突破下轨，开空
                        result['stg'] = StrategyType.SHORT_IN
                        result['num'] = self._calculate_contract_num(symbol, k_close)
                        
                elif stg == StrategyType.LONG_IN or stg == StrategyType.LONG_HOLD:
                    if k_close >= mid:  # 价格在中轨以上，持多
                        result['stg'] = StrategyType.LONG_HOLD
                        result['rate'] = float((k_close - last_close) / last_close)
                        result['winner'] = result['rate'] * num * float(k_close)
                        result['num'] = num
                    else:  # 价格跌破中轨，平多
                        result['stg'] = StrategyType.LONG_OUT
                        result['rate'] = float((k_close - last_close) / last_close)
                        result['winner'] = result['rate'] * num * float(k_close)
                        result['num'] = 0
                        
                elif stg == StrategyType.SHORT_IN or stg == StrategyType.SHORT_HOLD:
                    if k_close <= mid:  # 价格在中轨以下，持空
                        result['stg'] = StrategyType.SHORT_HOLD
                        result['rate'] = float((last_close - k_close) / last_close)
                        result['winner'] = result['rate'] * num * float(k_close)
                        result['num'] = num
                    else:  # 价格突破中轨，平空
                        result['stg'] = StrategyType.SHORT_OUT
                        result['rate'] = float((last_close - k_close) / last_close)
                        result['winner'] = result['rate'] * num * float(k_close)
                        result['num'] = 0
                        
                elif stg == StrategyType.LONG_OUT or stg == StrategyType.SHORT_OUT:
                    result['stg'] = StrategyType.EMPTY  # 平仓后回到空仓状态
                    result['num'] = 0
                    
                results.append(result)
                
                # 更新状态
                stg = result['stg']
                num = result['num']
                last_close = k_close
                
            # 保存策略结果
            if results:
                return self._save_strategy_results(symbol, results)
            
            return True
            
        except Exception as e:
            self.logger.error(f"计算并保存策略失败: {str(e)}")
            return False
            
    def _save_strategy_results(self, symbol: str, results: List[Dict]) -> bool:
        """保存策略结果"""
        try:
            # 确保所有数值在合理范围内
            for result in results:
                # 限制 num 在 INT 范围内
                raw_num = result['num']
                result['num'] = max(-2147483648, min(2147483647, raw_num))
                if raw_num != result['num']:
                    self.logger.warning(
                        f"数量超出范围 - symbol: {symbol}, "
                        f"time: {result['time']}, "
                        f"原始数量: {raw_num}, 调整后: {result['num']}"
                    )
            
            # 保存策略明细
            if not self.db.InsertStratageDetailGateio(
                symbol, 
                [r['close'] for r in results],
                [r['time'] for r in results],
                [r['top'] for r in results],
                [r['mid'] for r in results],
                [r['bot'] for r in results],
                [r['stg'] for r in results],
                [r['num'] for r in results],
                [r['rate'] for r in results],
                [r['winner'] for r in results]
            ):
                raise RuntimeError("保存策略明细失败")
                
            # 更新最新策略状态
            last_result = results[-1]
            if not self.db.UpdateStratageLatestGate(
                symbol, 
                last_result['time'],
                last_result['num'],  # 已经在上面限制过范围
                last_result['stg'],
                last_result['close'],
                last_result['rate'],
                last_result['winner'],
                last_result['top'],
                last_result['mid'],
                last_result['bot']
            ):
                raise RuntimeError("更新最新策略状态失败")
                
            return True
            
        except Exception as e:
            self.logger.error(f"保存策略数据失败: {str(e)}")
            return False
            
    def stop(self):
        """停止策略计算器"""
        if self.db:
            self.db.close() 