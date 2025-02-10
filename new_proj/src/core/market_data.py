from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import threading
from queue import Queue
import logging
from gate_api import ApiClient, Configuration, FuturesApi
from utils.config_manager import ConfigManager
from utils.log_helper import setup_module_logger, log_exception
from database.db_connector import DatabaseConnector
import time
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from decimal import Decimal
import math
import requests
import os

class StrategyState:
    """策略状态常量"""
    EMPTY = 0       # 空仓
    LONGIN = 1      # 开多
    LONGHOLD = 2    # 持多
    LONGQUIT = 3    # 平多
    SHORTIN = -1    # 开空
    SHORTHOLD = -2  # 持空
    SHORTQUIT = -3  # 平空
    
    MAXINT = float('inf')  # 最大值
    ZERO = 0       # 零值

class StrategyConfig:
    """策略配置"""
    DEFAULT_STG_ID = 4      # 默认策略ID
    WIN_SIZE = 20          # 窗口大小
    DAY_K_NUMS = 48       # 一天K线数量
    MONEY_PER_SYMBOL = 10000  # 每个品种资金额度
    MAX_LEVERAGE = 3      # 最大杠杆倍数
    
    # 时间窗口配置
    CALC_MINUTES = (2, 32)  # 策略计算时间点
    UPDATE_MINUTES = (0, 30)  # 数据更新时间点
    SUPPLEMENT_MINUTES = (5, 35)  # 数据补充时间点

class MarketDataManager:
    """市场数据管理器"""
    UPDATE_MINUTES = (0, 30)  # 数据更新时间点
    SUPPLEMENT_MINUTES = (5, 35)  # 数据补充时间点
    CHECK_INTERVAL = 300  # 状态检查间隔（5分钟）
    
    def __init__(self):
        self.logger = setup_module_logger(__name__)
        self.data_queue = Queue()
        self.is_running = False
        self._lock = threading.Lock()
        self.db = DatabaseConnector()
        self.exchange = None
        self.all_symbols = []  # 所有可交易品种
        self._thread = None  # 行情处理线程
        
        # 使用配置管理器
        self.config = ConfigManager()
        self.server = self.config.server
        self.db_config = self.config.database
        self.use_backup_api = False  # 是否使用备用API
        
        self._api_lock = threading.Lock()  # 用于API调用的锁
        self._running_lock = threading.Lock()  # 用于运行状态检查的锁
        self._update_lock = threading.Lock()  # 用于数据更新的锁
        
        # 策略相关配置
        self.day_k_nums = 48  # 一天的K线数量
        self.strategy_money = 10000  # 每个品种的资金额度
        self.strategy_queue = Queue()  # 策略计算队列
        
        self._last_check_time = time.time()
        self._last_update_minute = -1
        
    def _initialize_exchange(self):
        """初始化交易所API"""
        try:
            api_config = self.config.get_api_config(self.use_backup_api)
            configuration = Configuration(
                key=api_config['key'],
                secret=api_config['secret'],
                host="https://api.gateio.ws/api/v4"
            )
            api_client = ApiClient(configuration)
            return FuturesApi(api_client)
            
        except Exception as e:
            self.logger.error(f"API初始化失败: {str(e)}")
            return None
            
    def initialize(self):
        """初始化市场数据管理器"""
        try:
            # 初始化数据库连接
            if not self.db.initialize(self.db_config['source']):
                raise RuntimeError("数据库初始化失败")
                
            # 初始化交易所API
            self.exchange = self._initialize_exchange()
            if not self.exchange:
                raise RuntimeError("交易所API初始化失败")
                
            # 获取所有可交易品种
            self.all_symbols = self._get_all_tradable_symbols()
            if not self.all_symbols:
                raise RuntimeError("无法获取可交易品种")
                
            return True
            
        except Exception as e:
            self.logger.error(f"初始化失败: {str(e)}")
            return False
            
    def _get_latest_kline_time(self) -> datetime:
        """获取最新K线时间
        0-29分，取上一个小时的30分
        30-59分，取当前小时的0分
        """
        now = datetime.now()
        current_minute = now.minute
        
        if current_minute < 30:
            # 0-29分，取上一个小时的30分
            if now.hour == 0:
                # 如果是凌晨0点前30分钟，需要取前一天23:30
                target_time = now.replace(hour=23, minute=30, second=0, microsecond=0) - timedelta(days=1)
            else:
                # 否则取上一个小时的30分
                target_time = now.replace(minute=30, second=0, microsecond=0) - timedelta(hours=1)
        else:
            # 30-59分，取当前小时的0分
            target_time = now.replace(minute=0, second=0, microsecond=0)
        
        return target_time
        
    def _get_all_tradable_symbols(self) -> List[str]:
        """获取所有可交易品种"""
        try:
            contracts = self.exchange.list_futures_contracts("usdt")
            return [c.name.split('_')[0] for c in contracts if c.name.endswith('_USDT')]
        except Exception as e:
            self.logger.error(f"获取可交易品种失败: {str(e)}")
            return []
            
    def _check_symbol_data_status(self, symbol: str) -> Tuple[bool, Optional[datetime]]:
        """检查品种数据状态"""
        try:
            latest_time = self._get_latest_kline_time()
            db_time = self.db.QueryMaxDatePrice30MGateio(symbol)
            
            if not db_time:
                # 数据库中没有数据，需要补充近一年的数据
                start_time = latest_time - timedelta(days=365)
                return True, start_time
                
            # 计算时间差
            time_diff = latest_time - db_time
            minutes_diff = time_diff.total_seconds() / 60
            
            if minutes_diff >= 30:  # 如果差距超过30分钟
                next_time = db_time + timedelta(minutes=30)
                if next_time <= latest_time:  # 确保下一个时间点不超过最新时间
                    return True, next_time
            
            return False, db_time
            
        except Exception as e:
            self.logger.error(f"{symbol}: {str(e)}")
            return True, None
            
    def _get_kline_data(self, symbol: str, start_time: datetime, end_time: datetime) -> List:
        """获取K线数据（添加重试机制）"""
        max_retries = 3
        retry_delay = 2  # 初始延迟2秒
        
        for attempt in range(max_retries):
            try:
                with self._api_lock:  # 避免并发API调用超过限制
                    if start_time == end_time:
                        end_time = end_time + timedelta(minutes=30)
                    elif start_time > end_time:
                        self.logger.warning(f"{symbol} 开始时间 {start_time} 大于结束时间 {end_time}，跳过")
                        return []
                    
                    start_ts = int(start_time.timestamp())
                    end_ts = int(end_time.timestamp())
                    contract = f"{symbol}_USDT"
                    
                    # 检查API限流
                    if hasattr(self, '_last_api_call'):
                        time_since_last_call = time.time() - self._last_api_call
                        if time_since_last_call < 0.5:  # 确保API调用间隔至少0.5秒
                            time.sleep(0.5 - time_since_last_call)
                    
                    try:
                        result = self.exchange.list_futures_candlesticks(
                            settle="usdt",
                            contract=contract,
                            _from=start_ts,
                            to=end_ts,
                            interval='30m'
                        )
                        self._last_api_call = time.time()
                        
                        # 处理空结果
                        if not result:
                            self.logger.debug(f"{symbol} 在时间段 {start_time} -> {end_time} 无数据")
                            return []
                        
                        # 转换数据
                        candles = []
                        for candle in result:
                            try:
                                candles.append([
                                    int(candle.t),
                                    float(candle.o),
                                    float(candle.h),
                                    float(candle.l),
                                    float(candle.c),
                                    float(candle.v),
                                ])
                            except (ValueError, AttributeError) as e:
                                self.logger.error(f"K线数据转换失败: {str(e)}, 数据: {candle}")
                                continue
                        
                        return candles
                        
                    except Exception as api_e:
                        # 检查是否是限流错误
                        if "429" in str(api_e):
                            wait_time = 60  # 限流时等待更长时间
                            self.logger.warning(f"{symbol}: API限流，等待{wait_time}秒")
                            time.sleep(wait_time)
                            continue
                        raise  # 重新抛出其他类型的错误
                
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)  # 指数退避
                    self.logger.warning(f"{symbol}: 获取K线数据失败 (尝试 {attempt + 1}/{max_retries}) - {str(e)}")
                    self.logger.warning(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    continue
                else:
                    self.logger.error(f"{symbol}: 获取K线数据失败，已重试 {max_retries} 次 - {str(e)}")
                    return []
        
        return []  # 所有重试都失败后返回空列表

    def _process_market_data(self):
        """处理市场数据"""
        try:
            while self.is_running:
                try:
                    current_time = time.time()
                    current_minute = datetime.now().minute
                    
                    # 每5分钟检查一次状态
                    if current_time - self._last_check_time >= self.CHECK_INTERVAL:
                        self._check_data_continuity()
                        self._last_check_time = current_time
                    
                    # 检查是否需要补充数据
                    if (current_minute in self.SUPPLEMENT_MINUTES and 
                        current_minute != self._last_update_minute):
                        self._check_data_continuity()
                        self._last_update_minute = current_minute
                    
                    # 更短的睡眠时间，提高响应性
                    time.sleep(0.1)
                    
                except Exception as e:
                    self.logger.error(f"行情处理异常: {str(e)}")
                    time.sleep(1)  # 出错时短暂等待
                
        except Exception as e:
            self.logger.error(f"行情处理线程异常: {str(e)}")
        finally:
            self.is_running = False

    def _update_historical_data(self):
        """更新历史数据"""
        try:
            start_time = datetime.now()
            success_count = 0
            fail_count = 0
            skip_count = 0
            
            # 遍历所有品种
            for symbol in self.all_symbols:
                try:
                    # 检查数据状态
                    need_update, db_time = self._check_symbol_data_status(symbol)
                    if not need_update:
                        skip_count += 1
                        continue
                    
                    # 获取最新K线时间
                    latest_time = self._get_latest_kline_time()
                    
                    # 获取并保存K线数据
                    klines = self._get_kline_data(symbol, db_time, latest_time)
                    if klines:
                        if self._save_kline_data(symbol, klines):
                            success_count += 1
                        else:
                            fail_count += 1
                    else:
                        fail_count += 1
                    
                except Exception as e:
                    fail_count += 1
                    self.logger.error(f"{symbol}: {str(e)}")
                
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"历史数据更新完成 - 耗时: {duration:.1f}秒, "
                f"成功: {success_count}, 失败: {fail_count}, 跳过: {skip_count}"
            )
            
        except Exception as e:
            self.logger.error(f"更新历史数据失败: {str(e)}")

    def _update_latest_prices(self):
        """更新最新价格"""
        try:
            # 1. 获取所有可交易合约的最新价格
            tickers = self.exchange.list_futures_tickers("usdt")
            if not tickers:
                raise RuntimeError("无法获取最新价格")
            
            # 2. 获取最新K线时间
            latest_time = self._get_latest_kline_time()
            
            # 3. 批量更新数据库
            for ticker in tickers:
                try:
                    symbol = ticker.contract.split('_')[0]
                    kline = [
                        int(latest_time.timestamp()),
                        float(ticker.last),  # 最新价格作为这根K线的收盘价
                        float(ticker.last),  # 暂时用最新价格填充
                        float(ticker.last),  # 暂时用最新价格填充
                        float(ticker.last),  # 最新价格
                        float(ticker.volume_24h) if hasattr(ticker, 'volume_24h') else 0
                    ]
                    self.db.InsertPriceDataGateio(symbol, [kline])
                    
                except Exception as e:
                    self.logger.error(f"更新 {symbol} 最新价格失败: {str(e)}")
            
            self.logger.info(f"已更新 {len(tickers)} 个品种的最新价格")
            
        except Exception as e:
            self.logger.error(f"更新最新价格失败: {str(e)}")

    def start(self):
        """启动市场数据管理器"""
        try:
            # 检查初始化状态
            if not self.exchange or not self.all_symbols:
                raise RuntimeError("市场数据管理器未正确初始化")
            
            self.is_running = True
            
            # 启动时立即检查一次数据状态
            self._check_data_continuity()
            
            # 创建并启动行情处理线程
            self._thread = threading.Thread(target=self._process_market_data, daemon=True)
            self._thread.start()
            
        except Exception as e:
            self.logger.error(f"启动失败: {str(e)}")
            raise
    
    def stop(self):
        """停止市场数据管理器"""
        try:
            self.is_running = False
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=5)
            if self.db:
                self.db.close()
        except Exception as e:
            self.logger.error(f"停止失败: {str(e)}")

    def _get_coin_info(self, symbol: str) -> Optional[Dict]:
        """获取合约信息"""
        try:
            contract = f"{symbol}_USDT"
            contracts = self.exchange.list_futures_contracts("usdt")
            for c in contracts:
                if c.name == contract:
                    try:
                        return {
                            'cs': float(c.quanto_multiplier or 1),  # 合约大小，默认为1
                            'min_amount': float(c.order_size_min or 1),  # 最小下单数量，默认为1
                            'leverage_min': float(c.leverage_min or 1),  # 最小杠杆，默认为1
                            'leverage_max': float(c.leverage_max or 20),  # 最大杠杆，默认为20
                            'maintenance_rate': float(c.maintenance_rate or 0.01),  # 维持保证金率，默认为0.01
                            'mark_type': c.mark_type or 'index'  # 标记价格类型，默认为index
                        }
                    except (TypeError, ValueError) as e:
                        self.logger.error(f"解析 {symbol} 合约信息失败: {str(e)}")
                        return None
            self.logger.warning(f"未找到合约 {contract}")
            return None
        except Exception as e:
            self.logger.error(f"获取 {symbol} 合约信息失败: {str(e)}")
            return None

    def _add_to_update_queue(self, symbol: str, priority: bool = False):
        """添加到数据补充队列"""
        try:
            if not hasattr(self, '_update_queue'):
                self._update_queue = Queue()
            
            # 避免重复添加
            if symbol not in [item[1] for item in self._update_queue.queue]:
                self._update_queue.put((priority, symbol))
                self.logger.debug(f"将 {symbol} 添加到数据补充队列 (优先级: {'高' if priority else '普通'})")
            
        except Exception as e:
            self.logger.error(f"添加 {symbol} 到补充队列失败: {str(e)}")

    def _check_data_continuity(self):
        """检查数据连续性"""
        try:
            latest_time = self._get_latest_kline_time()
            db_times = self._get_all_latest_kline_times()
            
            need_update_symbols = []
            # 检查所有可交易品种
            for symbol in self.all_symbols:
                try:
                    db_time = db_times.get(symbol)
                    if db_time:
                        # 如果数据库时间不等于最新时间，需要补充
                        if db_time != latest_time:
                            need_update_symbols.append(symbol)
                    else:
                        # 如果没有数据，也需要补充
                        need_update_symbols.append(symbol)
                        
                except Exception as e:
                    self.logger.error(f"{symbol}: {str(e)}")
                    need_update_symbols.append(symbol)  # 出错时也加入补充列表
            
            # 如果有需要更新的币种，进行更新
            if need_update_symbols:
                self.logger.info(f"开始补充 {len(need_update_symbols)} 个品种的数据")
                for symbol in need_update_symbols:
                    self._add_to_update_queue(symbol)
                # 立即处理补充队列
                self._process_update_queue()
            
        except Exception as e:
            self.logger.error(f"检查数据连续性失败: {str(e)}")

    def _process_update_queue(self):
        """处理数据补充队列"""
        try:
            if not hasattr(self, '_update_queue'):
                return
            
            processed_count = 0
            success_count = 0
            fail_count = 0
            
            # 获取最新K线时间和一年前的时间
            latest_time = self._get_latest_kline_time()
            one_year_ago = latest_time - timedelta(days=365)
            BATCH_SIZE = 1999  # 设置为1999，确保不会超过2000条
            
            while not self._update_queue.empty():
                priority, symbol = self._update_queue.get()
                try:
                    # 获取数据库中最新时间
                    db_time = self.db.QueryMaxDatePrice30MGateio(symbol)
                    
                    if not db_time:
                        # 如果没有数据，从最新时间开始往前补充，但不超过一年
                        current_end = latest_time
                        has_more_data = True
                        
                        while has_more_data:
                            # 计算当前批次的开始时间
                            current_start = current_end - timedelta(minutes=30 * BATCH_SIZE)
                            # 确保不会获取超过一年前的数据
                            if current_start < one_year_ago:
                                current_start = one_year_ago
                                has_more_data = False  # 到达一年前就停止
                            
                            # 获取并保存数据
                            klines = self._get_kline_data(symbol, current_start, current_end)
                            if klines and len(klines) > 0:
                                if self._save_kline_data(symbol, klines):
                                    success_count += 1
                                else:
                                    fail_count += 1
                                
                                # 如果获取的数据量小于请求量，或者已经到达一年前，就停止
                                if len(klines) < BATCH_SIZE or not has_more_data:
                                    break
                                
                                # 更新结束时间为当前开始时间，减去一个时间单位避免重复
                                current_end = current_start - timedelta(minutes=30)
                                time.sleep(0.1)  # 避免API调用过于频繁
                            else:
                                # 如果获取不到数据，说明到达历史数据边界
                                break
                    else:
                        # 从最后一条数据的下一个时间点开始补充
                        start_time = db_time + timedelta(minutes=30)
                        if start_time <= latest_time:
                            if self._update_symbol_data(symbol, start_time, latest_time):
                                success_count += 1
                            else:
                                fail_count += 1
                
                    processed_count += 1
                    
                except Exception as e:
                    self.logger.error(f"{symbol}: {str(e)}")
                    fail_count += 1
                    # 如果是高优先级任务，重新加入队列
                    if priority:
                        self._add_to_update_queue(symbol, True)
                
                finally:
                    self._update_queue.task_done()
            
            if processed_count > 0:
                self.logger.info(f"数据补充完成 - 成功: {success_count}, 失败: {fail_count}")
            
        except Exception as e:
            self.logger.error(f"处理数据补充队列失败: {str(e)}")

    def LoadStratageAll(self, symbol: str):
        """装载所有策略"""
        try:
            # 使用固定的策略参数
            stg = {
                'name': 'GD20',
                'winsize': 20,
                'stg_id': 4
            }
            
            ret = self._calculate_historical_strategy(symbol, stg)
            if ret is False:
                self.logger.error(f"加载 {symbol} 策略失败")
            
        except Exception as e:
            self.logger.error(f"装载 {symbol} 所有策略失败: {str(e)}")

    def _get_priority_symbols(self) -> List[str]:
        """获取优先计算策略的品种列表"""
        try:
            # 从数据库获取产品组信息
            sql = """
                SELECT DISTINCT pg.symbols 
                FROM account_product_groups apg 
                JOIN product_groups pg ON apg.group_id = pg.id 
                WHERE pg.state = 1
            """
            results = self.db.execute_query(sql)
            
            # 解析所有品种并去重
            priority_symbols = set()
            for row in results:
                if row[0]:  # symbols字段不为空
                    symbols = row[0].split('#')
                    priority_symbols.update(s.strip() for s in symbols if s.strip())
                    
            self.logger.info(f"获取到 {len(priority_symbols)} 个优先计算品种")
            return list(priority_symbols)
            
        except Exception as e:
            self.logger.error(f"获取优先计算品种失败: {str(e)}")
            return []

    def _calculate_latest_strategies(self):
        """计算最新策略"""
        try:
            start_time = time.time()
            success_count = 0
            fail_count = 0
            skip_count = 0
            
            # 判断当前时间点
            now = datetime.now()
            current_minute = now.minute
            
            # 确定要计算的品种列表
            if current_minute in (0, 30):  # 整点和30分时只计算优先品种
                symbols_to_calc = self._get_priority_symbols()
                self.logger.info("当前为整点或30分，只计算优先品种")
            else:  # 其他时间计算所有品种
                symbols_to_calc = self.all_symbols
                self.logger.info("计算所有品种策略")
                
            if not symbols_to_calc:
                self.logger.warning("无可计算品种")
                return
                
            # 使用线程池计算策略
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for symbol in symbols_to_calc:
                    futures.append(executor.submit(self._process_single_strategy, symbol))
                    
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result is True:
                            success_count += 1
                        elif result is False:
                            fail_count += 1
                        else:  # None
                            skip_count += 1
                    except Exception as e:
                        self.logger.error(f"策略计算失败: {str(e)}")
                        fail_count += 1
                        
            end_time = time.time()
            self.logger.info(
                f"策略计算完成:\n"
                f"计算品种数: {len(symbols_to_calc)}\n"
                f"总耗时: {end_time - start_time:.2f}秒\n"
                f"成功: {success_count}\n"
                f"失败: {fail_count}\n"
                f"跳过: {skip_count}"
            )
            
        except Exception as e:
            self.logger.error(f"计算最新策略失败: {str(e)}")

    def _process_single_strategy(self, symbol: str) -> Optional[bool]:
        """处理单个品种的策略计算"""
        try:
            # 先获取合约信息，如果获取失败就使用默认值
            coin_info = self._get_coin_info(symbol)
            if not coin_info:
                coin_info = {
                    'cs': 1.0,  # 默认合约大小
                    'min_amount': 1.0,  # 默认最小下单数量
                    'leverage_min': 1.0,  # 默认最小杠杆
                    'leverage_max': 20.0,  # 默认最大杠杆
                    'maintenance_rate': 0.01,  # 默认维持保证金率
                    'mark_type': 'index'  # 默认标记价格类型
                }
                self.logger.warning(f"{symbol} 使用默认合约参数")
            
            # 检查策略状态
            if not self._check_strategy_status(symbol):
                self.logger.warning(f"{symbol} 无历史策略数据，加入历史计算队列")
                self._add_to_update_queue(symbol)  # 使用新的方法名
                return None
            
            # 获取最新K线数据
            latest_time = self._get_latest_kline_time()
            start_time = latest_time - timedelta(minutes=30 * StrategyConfig.WIN_SIZE)
            
            # 获取策略数据
            strategy_data = self._get_strategy_data(symbol, start_time)
            if not strategy_data:
                self.logger.warning(f"{symbol} 无策略数据")
                return None
            
            # 计算策略
            return self._calculate_strategy(
                symbol,
                strategy_data,
                {
                    'top': strategy_data['tops'][-1],
                    'mid': strategy_data['mids'][-1],
                    'bot': strategy_data['bots'][-1],
                    'num': strategy_data['nums'][-1],
                    'stg': strategy_data['stgs'][-1],
                    'last_close': Decimal(str(strategy_data['close_prices'][-1])),
                    'stg_time': strategy_data['times'][-1]
                },
                coin_info
            )
            
        except Exception as e:
            self.logger.error(f"计算 {symbol} 最新策略失败: {str(e)}")
            return False

    def _calculate_strategy(self, symbol: str, kline_data: List, strategy_params: Dict, coin_info: Dict) -> bool:
        """计算策略"""
        try:
            if not kline_data:
                return False
            
            # 准备数据列表
            close_prices = []
            close_times = []
            tops = []
            mids = []
            bots = []
            stgs = []
            nums = []
            rates = []
            winners = []
            
            # 使用策略参数
            top = strategy_params['top']
            mid = strategy_params['mid']
            bot = strategy_params['bot']
            num = strategy_params['num']
            stg = strategy_params['stg']
            last_close = strategy_params['last_close']
            
            # 获取合约大小
            symbol_cval = coin_info['cs']
            if symbol_cval == 0:
                self.logger.error(f"{symbol} 合约大小为0")
                return False
            
            # 遍历K线数据
            for k_data in kline_data:
                k_close = Decimal(str(k_data[0]))
                k_time = k_data[1]
                
                close_prices.append(float(k_close))
                close_times.append(k_time)
                
                # 跨日处理
                if k_time.hour == 0 and k_time.minute == 0:
                    # 获取历史数据计算通道
                    start_idx = len(close_prices) - StrategyConfig.WIN_SIZE * self.day_k_nums
                    if start_idx >= 0:
                        window_data = close_prices[start_idx:]
                        max_close = max(window_data)
                        min_close = min(window_data)
                        
                        top = max_close
                        bot = min_close
                        mid = (top + bot) / 2
                
                tops.append(float(top))
                mids.append(float(mid))
                bots.append(float(bot))
                
                # 策略逻辑
                if stg == StrategyState.EMPTY or stg == StrategyState.LONGQUIT or stg == StrategyState.SHORTQUIT:
                    if bot == float('inf') and top == 0:  # 初始状态
                        nums.append(0)
                        stg = StrategyState.EMPTY
                        stgs.append(stg)
                    else:
                        if k_close > top:  # 开多
                            stg = StrategyState.LONGIN
                            decimal_data = Decimal(str(symbol_cval)) * k_close
                            num = math.floor(float(self.strategy_money / decimal_data))
                            nums.append(num)
                            stgs.append(stg)
                        elif k_close < bot:  # 开空
                            stg = StrategyState.SHORTIN
                            decimal_data = Decimal(str(symbol_cval)) * k_close
                            num = math.floor(float(self.strategy_money / decimal_data))
                            nums.append(num)
                            stgs.append(stg)
                        else:  # 区间内
                            nums.append(0)
                            stgs.append(StrategyState.EMPTY)
                
                    rates.append(0)
                    winners.append(0)
                
                elif stg == StrategyState.SHORTIN or stg == StrategyState.SHORTHOLD:
                    if k_close <= mid:  # 继续持空
                        stg = StrategyState.SHORTHOLD
                        stgs.append(stg)
                        rate = float((last_close - k_close) / last_close)
                        rates.append(rate)
                        nums.append(num)
                        winner = rate * Decimal(str(num)) * Decimal(str(symbol_cval)) * last_close
                        winners.append(float(winner))
                    else:  # 平空
                        stg = StrategyState.SHORTQUIT
                        stgs.append(stg)
                        rate = float((last_close - k_close) / last_close)
                        rates.append(rate)
                        winner = rate * Decimal(str(num)) * Decimal(str(symbol_cval)) * last_close
                        winners.append(float(winner))
                        num = 0
                        nums.append(num)
                    
                elif stg == StrategyState.LONGIN or stg == StrategyState.LONGHOLD:
                    if k_close >= mid:  # 继续持多
                        stg = StrategyState.LONGHOLD
                        stgs.append(stg)
                        rate = float((k_close - last_close) / last_close)
                        rates.append(rate)
                        nums.append(num)
                        winner = rate * Decimal(str(num)) * Decimal(str(symbol_cval)) * last_close
                        winners.append(float(winner))
                    else:  # 平多
                        stg = StrategyState.LONGQUIT
                        stgs.append(stg)
                        rate = float((k_close - last_close) / last_close)
                        rates.append(rate)
                        winner = rate * Decimal(str(num)) * Decimal(str(symbol_cval)) * last_close
                        winners.append(float(winner))
                        num = 0
                        nums.append(num)
                
                last_close = k_close
            
            # 保存策略结果
            if close_prices:
                try:
                    # 保存明细
                    if not self.db.InsertStratageDetailGateio(
                        symbol, 
                        close_prices, close_times,
                        tops, mids, bots, 
                        stgs, nums, rates, winners
                    ):
                        raise Exception("保存策略明细失败")
                        
                    # 更新最新状态
                    if not self.db.UpdateStratageLatestGate(
                        symbol, 
                        close_times[-1], nums[-1], stgs[-1],
                        close_prices[-1], rates[-1], winners[-1],
                        tops[-1], mids[-1], bots[-1]
                    ):
                        raise Exception("更新最新策略状态失败")
                        
                    return True
                    
                except Exception as e:
                    self.logger.error(f"{symbol} 保存策略数据失败: {str(e)}")
                    return False
                
            return False
            
        except Exception as e:
            self.logger.error(f"计算 {symbol} 策略失败: {str(e)}")
            return False

    def _check_and_switch_api(self):
        """检查API状态并在必要时切换"""
        try:
            if self.exchange:
                # 测试API连接
                self.exchange.list_futures_contracts("usdt")
                return True
        except Exception as e:
            self.logger.error(f"API检查失败: {str(e)}")
            if not self.use_backup_api:
                self.logger.info("切换到备用API")
                self.use_backup_api = True
                self.exchange = self._initialize_exchange()
                return self.exchange is not None
            return False 

    def _check_server_status(self) -> bool:
        """检查服务器状态"""
        try:
            if self.server['is_main']:  # 主服务器
                self.db.UpdateWatchApp("future_quotes_gateio")
                return True
            else:  # 备份服务器
                # 检查主服务器状态
                status = self.db.QueryWatchApp("future_quotes_gateio")
                if not status:
                    return True
                    
                time_diff = datetime.now() - status['status_time']
                if time_diff.total_seconds() > self.server['timeout']:
                    self.db.UpdateWatchAppBack("future_quotes_gateio")
                    self._send_warning()
                    return True
                    
                self.logger.info("主服务器运行正常，备份程序等待...")
                return False
                
        except Exception as e:
            self.logger.error(f"检查服务器状态失败: {str(e)}")
            return True  # 出错时允许运行

    def _send_warning(self):
        """发送警告消息"""
        try:
            title = 'Gateio-CTA 行情服务器故障'
            data = {
                'text': title,
                'desp': "速速检查106服务器"
            }
            
            # 发送给管理员1
            requests.post(
                "http://wx.xtuis.cn/BDGGZgR856AueOk6JXoCERIyi.send",
                data=data
            )
            
            # 发送给管理员2
            requests.post(
                "http://wx.xtuis.cn/DOyVyJTsYb8UfxLV4qtWPr0t6.send",
                data=data
            )
            
        except Exception as e:
            self.logger.error(f"发送警告失败: {str(e)}") 

    def _get_strategy_data(self, symbol: str, start_time: datetime) -> Optional[Dict]:
        """获取策略数据"""
        try:
            # 获取K线数据
            kline_data = self.db.QueryProductDataPartGateio(
                symbol,
                start_time,
                StrategyConfig.WIN_SIZE * 2  # 获取足够的数据用于计算
            )
            
            if not kline_data or len(kline_data) < StrategyConfig.WIN_SIZE:
                self.logger.warning(f"{symbol} K线数据不足")
                return None
            
            # 计算策略参数
            close_prices = []
            times = []
            tops = []
            mids = []
            bots = []
            stgs = []
            nums = []
            rates = []
            winners = []
            
            # 初始化参数
            win_size = StrategyConfig.WIN_SIZE
            for row in kline_data:
                try:
                    close = float(row[0])  # 收盘价
                    time = row[1]  # 时间
                    
                    close_prices.append(close)
                    times.append(time)
                    
                    if len(close_prices) >= win_size:
                        # 计算布林带
                        window = close_prices[-win_size:]
                        ma = sum(window) / win_size
                        std = (sum((x - ma) ** 2 for x in window) / win_size) ** 0.5
                        
                        top = ma + 2 * std
                        mid = ma
                        bot = ma - 2 * std
                        
                        tops.append(top)
                        mids.append(mid)
                        bots.append(bot)
                        
                        # 初始化其他参数
                        stgs.append(0)
                        nums.append(0)
                        rates.append(0)
                        winners.append(0)
                    else:
                        # 数据不足时使用初始值
                        tops.append(0)
                        mids.append(0)
                        bots.append(float('inf'))
                        stgs.append(0)
                        nums.append(0)
                        rates.append(0)
                        winners.append(0)
                    
                except (TypeError, ValueError, IndexError) as e:
                    self.logger.error(f"处理 {symbol} K线数据失败: {str(e)}")
                    self.logger.error(f"问题数据: {row}")
                    continue
            
            if not close_prices:
                self.logger.error(f"{symbol} 无有效K线数据")
                return None
            
            return {
                'close_prices': close_prices,
                'times': times,
                'tops': tops,
                'mids': mids,
                'bots': bots,
                'stgs': stgs,
                'nums': nums,
                'rates': rates,
                'winners': winners
            }
            
        except Exception as e:
            self.logger.error(f"获取 {symbol} 策略数据失败: {str(e)}")
            return None

    def _check_strategy_status(self, symbol: str) -> bool:
        """检查策略状态"""
        try:
            # 获取最新策略数据
            latest = self.db.QueryStratageDetailLatestGateio(symbol)
            
            if not latest:
                return False
            
            # 验证数据格式
            required_fields = ['stratage_time', 'top', 'mid', 'bot', 'num', 'stg', 'close']
            for field in required_fields:
                if field not in latest:
                    self.logger.error(f"{symbol} 策略数据缺少字段: {field}")
                    return False
                
            # 检查时间是否连续
            time_diff = datetime.now() - latest['stratage_time']
            if time_diff.total_seconds() > 1800:  # 超过30分钟
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查 {symbol} 策略状态失败: {str(e)}")
            return False 

    def _get_all_latest_kline_times(self) -> Dict[str, datetime]:
        """获取所有币种的最新K线时间"""
        try:
            latest_times = self.db.QueryAllMaxDatePrice30MGateio()
            if not latest_times:
                self.logger.info("数据库中暂无K线数据")
                return {}
            return latest_times
        except Exception as e:
            self.logger.error(f"获取最新K线时间失败: {str(e)}")
            return {}

    def _calculate_historical_strategies(self):
        """计算历史策略"""
        try:
            start_time = time.time()
            success_count = 0
            fail_count = 0
            skip_count = 0
            
            # 获取所有品种的最新策略时间
            latest_times = {}
            for symbol in self.all_symbols:
                latest = self.db.QueryStratageDetailLatestGateio(symbol)
                if latest:
                    latest_times[symbol] = latest['stratage_time']
            
            # 获取最新K线时间
            latest_kline_time = self._get_latest_kline_time()
            
            # 使用线程池计算策略
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = []
                for symbol in self.all_symbols:
                    # 确定计算的起始时间
                    if symbol in latest_times:
                        start_time = latest_times[symbol]
                    else:
                        # 如果没有历史策略数据，从一年前开始计算
                        start_time = latest_kline_time - timedelta(days=365)
                    
                    # 提交计算任务
                    futures.append(executor.submit(
                        self._calculate_historical_strategy,
                        symbol,
                        start_time,
                        latest_kline_time
                    ))
                
                # 等待所有任务完成
                for future in as_completed(futures):
                    try:
                        result = future.result()
                        if result is True:
                            success_count += 1
                        elif result is False:
                            fail_count += 1
                        else:  # None
                            skip_count += 1
                    except Exception as e:
                        self.logger.error(f"历史策略计算失败: {str(e)}")
                        fail_count += 1
            
            end_time = time.time()
            self.logger.info(
                f"历史策略计算完成:\n"
                f"总耗时: {end_time - start_time:.2f}秒\n"
                f"成功: {success_count}\n"
                f"失败: {fail_count}\n"
                f"跳过: {skip_count}"
            )
            
        except Exception as e:
            self.logger.error(f"计算历史策略失败: {str(e)}")

    def _calculate_historical_strategy(self, symbol: str, start_time: datetime, end_time: datetime) -> Optional[bool]:
        """计算单个品种的历史策略"""
        try:
            # 获取合约信息
            coin_info = self._get_coin_info(symbol)
            if not coin_info:
                coin_info = {
                    'cs': 1.0,  # 默认合约大小
                    'min_amount': 1.0,  # 默认最小下单数量
                    'leverage_min': 1.0,  # 默认最小杠杆
                    'leverage_max': 20.0,  # 默认最大杠杆
                    'maintenance_rate': 0.01,  # 默认维持保证金率
                    'mark_type': 'index'  # 默认标记价格类型
                }
                self.logger.warning(f"{symbol} 使用默认合约参数")
            
            # 获取历史K线数据
            kline_data = self.db.QueryProductDataPartGateio(
                symbol,
                start_time,
                StrategyConfig.WIN_SIZE * 2
            )
            
            if not kline_data or len(kline_data) < StrategyConfig.WIN_SIZE:
                self.logger.warning(f"{symbol} 历史K线数据不足")
                return None
            
            # 计算策略
            strategy_data = self._get_strategy_data(symbol, start_time)
            if not strategy_data:
                self.logger.warning(f"{symbol} 无法获取策略数据")
                return None
            
            # 使用初始策略参数
            strategy_params = {
                'top': 0,
                'mid': 0,
                'bot': float('inf'),
                'num': 0,
                'stg': 0,
                'last_close': Decimal(str(strategy_data['close_prices'][0])),
                'stg_time': strategy_data['times'][0]
            }
            
            # 计算策略
            return self._calculate_strategy(
                symbol,
                kline_data,
                strategy_params,
                coin_info
            )
            
        except Exception as e:
            self.logger.error(f"计算 {symbol} 历史策略失败: {str(e)}")
            return False 

    def _get_market_ticks(self) -> Dict[str, float]:
        """快速获取全市场tick数据"""
        try:
            ticks = {}
            with self._api_lock:
                # 使用Gate.io的批量行情接口
                contracts = self.exchange.list_futures_tickers('usdt')
                for contract in contracts:
                    try:
                        symbol = contract.contract.split('_')[0]
                        last_price = float(contract.last)
                        if last_price > 0:
                            ticks[symbol] = last_price
                    except (ValueError, AttributeError, IndexError):
                        continue
            return ticks
        except Exception as e:
            self.logger.error(f"获取市场tick数据失败: {str(e)}")
            return {}

    def _save_tick_as_kline(self, symbol: str, price: float, k_time: datetime) -> bool:
        """将tick数据保存为K线"""
        try:
            data = [(k_time, price)]  # 使用tick价格作为K线收盘价
            return self.db.InsertPriceDataGateio(symbol, data)
        except Exception as e:
            self.logger.error(f"{symbol}: 保存tick数据失败 - {str(e)}")
            return False

    def update_latest_data(self):
        """更新最新行情数据"""
        try:
            # 获取当前K线时间
            now = datetime.now()
            current_minute = now.minute
            
            # 确定应该更新的K线时间点
            if current_minute < 30:
                # 0-29分，应该更新上一个小时的30分K线
                if now.hour == 0:
                    # 如果是凌晨0点前30分钟，需要更新前一天23:30的K线
                    k_time = now.replace(hour=23, minute=30, second=0, microsecond=0) - timedelta(days=1)
                else:
                    # 否则更新上一个小时的30分K线
                    k_time = now.replace(minute=30, second=0, microsecond=0) - timedelta(hours=1)
            else:
                # 30-59分，更新当前小时的0分K线
                k_time = now.replace(minute=0, second=0, microsecond=0)
            
            # 快速获取全市场tick数据
            ticks = self._get_market_ticks()
            if not ticks:
                self.logger.error("获取市场tick数据失败")
                return
            
            # 批量保存数据
            success_count = 0
            fail_count = 0
            
            self.logger.info(f"更新K线时间点: {k_time}")
            
            for symbol, price in ticks.items():
                try:
                    if self._save_tick_as_kline(symbol, price, k_time):
                        success_count += 1
                    else:
                        fail_count += 1
                except Exception as e:
                    self.logger.error(f"{symbol}: {str(e)}")
                    fail_count += 1
            
            self.logger.info(f"市场数据更新完成 - 成功: {success_count}, 失败: {fail_count}")
            
        except Exception as e:
            self.logger.error(f"更新市场数据失败: {str(e)}")

    def get_all_symbols(self) -> List[str]:
        """获取所有可交易品种"""
        return self.all_symbols

    def _save_kline_data(self, symbol: str, kline_data: List) -> bool:
        """保存K线数据到数据库"""
        try:
            if not kline_data:
                return False
            
            # 转换数据格式
            formatted_data = []
            for candle in kline_data:
                try:
                    # 确保数据完整性
                    if len(candle) < 5:  # 至少需要时间戳和收盘价
                        continue
                    
                    # 数据转换
                    timestamp = int(candle[0])  # 时间戳
                    close_price = float(candle[4])  # 收盘价
                    
                    # 数据验证
                    if close_price <= 0:
                        continue
                        
                    # 转换时间戳为datetime
                    price_time = datetime.fromtimestamp(timestamp)
                    
                    # 添加到格式化数据列表
                    formatted_data.append((price_time, close_price))  # 使用元组而不是列表
                    
                except Exception as e:
                    self.logger.error(f"{symbol}: 数据格式错误 - {str(e)}")
                    continue
            
            if not formatted_data:
                self.logger.error(f"{symbol}: 无有效K线数据")
                return False
            
            # 保存到数据库
            if self.db.InsertPriceDataGateio(symbol, formatted_data):
                self.logger.info(f"{symbol}: 成功获取 {len(formatted_data)} 条K线数据")
                return True
            else:
                self.logger.error(f"{symbol}: 数据保存失败")
                return False
            
        except Exception as e:
            self.logger.error(f"{symbol}: {str(e)}")
            return False

    def _update_symbol_data(self, symbol: str, start_time: datetime, end_time: datetime) -> bool:
        """更新单个品种的历史数据"""
        try:
            # 获取并保存K线数据
            klines = self._get_kline_data(symbol, start_time, end_time)
            if klines and self._save_kline_data(symbol, klines):
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"{symbol}: {str(e)}")
            return False 