from typing import Optional, Dict, Any, List
import logging
import pymysql
from datetime import datetime
from pymysql.cursors import DictCursor
from utils.config_manager import ConfigManager
from dbutils.pooled_db import PooledDB
import threading
import time

class DatabaseConnector:
    """数据库连接器 - 单例模式"""
    _instance: Optional['DatabaseConnector'] = None
    _pool: Optional[PooledDB] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnector, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self._config = ConfigManager()
            self._pool_lock = threading.Lock()  # 添加连接池锁
            self._initialized = True
    
    def initialize(self, data_source: int) -> bool:
        """初始化数据库连接池"""
        try:
            self.logger.info(f"正在初始化数据库连接，数据源: {data_source}")
            
            # 从配置文件获取数据库配置
            db_config = self._config.database
            
            # 创建数据库连接池
            self._pool = PooledDB(
                creator=pymysql,        # 使用pymysql作为数据库连接器
                maxconnections=10,      # 连接池最大连接数
                mincached=2,           # 初始化时创建的空闲连接数
                maxcached=5,           # 连接池最大空闲连接数
                maxshared=3,           # 共享连接的最大数量
                blocking=True,         # 连接池满时是否阻塞等待
                maxusage=None,         # 一个连接最多被使用的次数
                setsession=[],         # 开始会话前执行的命令
                ping=0,                # ping MySQL服务端确保连接有效
                host=db_config['host'],
                port=int(db_config['port']),
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                charset='utf8mb4',
                cursorclass=DictCursor
            )
            
            # 测试连接池
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    
            self.logger.info("数据库连接池初始化成功")
            return True
            
        except Exception as e:
            self.logger.error(f"数据库初始化失败: {str(e)}")
            return False
    
    def _get_connection(self):
        """从连接池获取连接（添加重试机制）"""
        max_retries = 3
        retry_delay = 1  # 秒
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if not self._pool:
                    with self._pool_lock:
                        if not self._pool:  # 双重检查
                            self.initialize(1)
                
                conn = self._pool.connection()
                conn.ping(reconnect=True)  # 确保连接有效
                return conn
                
            except Exception as e:
                last_error = e
                self.logger.warning(f"获取数据库连接失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
            
        self.logger.error(f"获取数据库连接失败，已重试 {max_retries} 次: {str(last_error)}")
        raise last_error
    
    def execute_query(self, sql: str, params: tuple = None) -> List:
        """执行查询"""
        try:
            if not self._pool:
                self.logger.error("数据库连接池未初始化")
                return []
            
            conn = self._pool.connection()
            try:
                with conn.cursor() as cursor:
                    self.logger.debug(f"执行SQL: {sql}")
                    self.logger.debug(f"参数: {params}")
                    
                    if params:
                        cursor.execute(sql, params)
                    else:
                        cursor.execute(sql)
                    
                    results = cursor.fetchall()
                    self.logger.debug(f"查询返回 {len(results)} 条记录")
                    return results
                    
            except Exception as e:
                self.logger.error(f"执行查询失败: {str(e)}")
                self.logger.error(f"SQL: {sql}")
                if params:
                    self.logger.error(f"参数: {params}")
                return []
            
            finally:
                if conn:
                    conn.close()
                
        except Exception as e:
            self.logger.error(f"数据库操作失败: {str(e)}")
            return []
    
    def execute_update(self, sql: str, params=None) -> int:
        """执行更新"""
        conn = self._pool.connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, params)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            self.logger.error(f"更新执行失败: {str(e)}\nSQL: {sql}")
            conn.rollback()
            return 0
        finally:
            conn.close()
    
    def execute_many(self, sql: str, values: List[tuple]) -> bool:
        """批量执行SQL"""
        conn = self._pool.connection()
        try:
            with conn.cursor() as cursor:
                cursor.executemany(sql, values)
                conn.commit()
                return True
        except Exception as e:
            self.logger.error(f"批量执行失败: {str(e)}\nSQL: {sql}")
            conn.rollback()
            return False
        finally:
            conn.close()
    
    def is_connected(self) -> bool:
        """检查数据库连接是否有效"""
        try:
            if not self._pool:
                return False
            conn = self._pool.connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                return True
            finally:
                conn.close()
        except Exception:
            return False
    
    def reconnect(self) -> bool:
        """重新连接数据库"""
        try:
            if self._pool:
                self._pool.close()
            return self.initialize(1)  # 重新初始化连接
        except Exception as e:
            self.logger.error(f"数据库重连失败: {str(e)}")
            return False
            
    def UpdateWatchApp(self, app_name: str) -> bool:
        """更新应用监控状态"""
        try:
            sql = """
                UPDATE watch_app 
                SET status_time = NOW() 
                WHERE app_name = %s
            """
            return self.execute_query(sql, (app_name,))
        except Exception as e:
            self.logger.error(f"更新应用监控状态失败: {str(e)}")
            return False
            
    def UpdateWatchAppBack(self, app_name: str) -> bool:
        """更新备份应用监控状态"""
        try:
            sql = """
                UPDATE watch_app_back 
                SET status_time = NOW() 
                WHERE app_name = %s
            """
            return self.execute_query(sql, (app_name,))
        except Exception as e:
            self.logger.error(f"更新备份应用监控状态失败: {str(e)}")
            return False
            
    def QueryWatchApp(self, app_name: str) -> Dict:
        """查询应用监控状态"""
        try:
            sql = """
                SELECT * FROM watch_app 
                WHERE app_name = %s
            """
            results = self.execute_query(sql, (app_name,))
            return results[0] if results else None
        except Exception as e:
            self.logger.error(f"查询应用监控状态失败: {str(e)}")
            return None
            
    def QueryGateAcctInfoByID(self, acct_id: int) -> Optional[Dict[str, Any]]:
        """根据账户ID查询Gate账户信息"""
        try:
            sql = """
                SELECT acct_id, memo, apikey, secretkey, apipass, 
                       status, acct_date, email, sendflag, acct_name 
                FROM acct_info 
                WHERE state = 1 AND acct_id = %s
            """
            results = self.execute_query(sql, (acct_id,))
            if results:
                return {
                    'acct_id': results[0][0],
                    'memo': results[0][1],
                    'apikey': results[0][2],
                    'secretkey': results[0][3],
                    'apipass': results[0][4],
                    'status': results[0][5],
                    'acct_date': results[0][6],
                    'email': results[0][7],
                    'sendflag': results[0][8],
                    'acct_name': results[0][9]
                }
            return None
        except Exception as e:
            self.logger.error(f"查询Gate账户信息失败: {str(e)}")
            return None
            
    def QueryMaxDatePrice30MGateio(self, symbol: str) -> Optional[datetime]:
        """查询指定币种的最新K线时间"""
        try:
            sql = """
                SELECT MAX(price_time) as max_time
                FROM gate_price_30m
                WHERE product_code = %s
            """
            results = self.execute_query(sql, (symbol,))
            return results[0]['max_time'] if results and results[0]['max_time'] else None
        except Exception as e:
            self.logger.error(f"查询 {symbol} 最新K线时间失败: {str(e)}")
            return None
            
    def InsertPriceDataGateio(self, symbol: str, candles: List) -> bool:
        """批量插入K线数据"""
        if not candles:
            return True
        
        try:
            sql = """
                INSERT INTO gate_price_30m 
                (product_code, price_time, `close`, frame)
                VALUES (%s, %s, %s, '30m')
                ON DUPLICATE KEY UPDATE
                `close` = VALUES(`close`)
            """
            
            # 准备批量插入的数据
            values = [(symbol, price_time, close_price) for price_time, close_price in candles]
            
            # 分批插入，每批1000条
            batch_size = 1000
            for i in range(0, len(values), batch_size):
                batch = values[i:i+batch_size]
                if not self.execute_many(sql, batch):
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"{symbol}: {str(e)}")
            return False

    def QueryStratageDetailLatestGateio(self, symbol: str) -> Optional[Dict]:
        """查询最新策略数据"""
        try:
            sql = """
                SELECT product_code, stratage_time, `close`, 
                       top, mid, but as bot, stg, num, rate, winner
                FROM stratage_latest_gate
                WHERE product_code = %s
                AND stratage_id = 4  # 使用固定的策略ID
                ORDER BY stratage_time DESC
                LIMIT 1
            """
            results = self.execute_query(sql, (symbol,))
            if not results:
                return None
            
            # 结果已经是字典格式
            row = results[0]
            
            # 转换数据类型
            try:
                return {
                    'product_code': str(row['product_code']),
                    'stratage_time': row['stratage_time'],
                    'close': float(row['close']) if row['close'] is not None else 0.0,
                    'top': float(row['top']) if row['top'] is not None else 0.0,
                    'mid': float(row['mid']) if row['mid'] is not None else 0.0,
                    'bot': float(row['bot']) if row['bot'] is not None else 0.0,
                    'stg': int(row['stg']) if row['stg'] is not None else 0,
                    'num': int(row['num']) if row['num'] is not None else 0,
                    'rate': float(row['rate']) if row['rate'] is not None else 0.0,
                    'winner': float(row['winner']) if row['winner'] is not None else 0.0
                }
            except (TypeError, ValueError, KeyError) as e:
                self.logger.error(f"处理 {symbol} 策略数据失败: {str(e)}")
                self.logger.error(f"原始数据: {row}")
                return None
        
        except Exception as e:
            self.logger.error(f"查询 {symbol} 最新策略数据失败: {str(e)}")
            return None

    def QueryStratageDetailGateio(self, symbol: str, start_time: datetime) -> List[Dict]:
        """查询策略明细数据"""
        try:
            sql = """
                SELECT product_code, stratage_time, `close`, 
                       top, mid, but, stg, num, rate, winner
                FROM stratage_detail_gate
                WHERE product_code = %s 
                AND stratage_time >= %s
                ORDER BY stratage_time ASC
            """
            results = self.execute_query(sql, (symbol, start_time))
            if not results:
                return []
            
            # 将查询结果转换为字典列表
            return [{
                'product_code': row[0],
                'stratage_time': row[1],
                'close': float(row[2]),
                'top': float(row[3]),
                'mid': float(row[4]),
                'bot': float(row[5]),
                'stg': int(row[6]),
                'num': int(row[7]),
                'rate': float(row[8]),
                'winner': float(row[9])
            } for row in results]
        
        except Exception as e:
            self.logger.error(f"查询 {symbol} 策略明细数据失败: {str(e)}")
            return []

    def InsertStratageDetailGateio(self, symbol: str, close_prices: List, close_times: List,
                                  tops: List, mids: List, bots: List, stgs: List, 
                                  nums: List, rates: List, winners: List) -> bool:
        """插入策略明细数据，确保每个时间点只有一条记录"""
        try:
            # 先删除可能重复的记录
            delete_sql = """
                DELETE FROM stratage_detail_gate 
                WHERE product_code = %s 
                AND stratage_time IN ({})
            """.format(','.join(['%s'] * len(close_times)))
            
            delete_params = [symbol] + close_times
            self.execute_update(delete_sql, delete_params)
            
            # 插入新记录
            sql = """
                INSERT INTO stratage_detail_gate 
                (stratage_id, product_code, stratage_time, `close`, 
                 top, mid, but, stg, num, rate, winner)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = []
            for i in range(len(close_prices)):
                value = (
                    4,  # 固定策略ID
                    str(symbol),
                    close_times[i],
                    float(close_prices[i]),
                    float(tops[i]),
                    float(mids[i]),
                    float(bots[i]),
                    int(stgs[i]),
                    int(nums[i]),
                    float(rates[i]),
                    float(winners[i])
                )
                values.append(value)
            
            return self.execute_many(sql, values)
            
        except Exception as e:
            self.logger.error(f"插入策略明细失败: {str(e)}")
            return False

    def UpdateStratageLatestGate(self, symbol: str, stratage_time: datetime, 
                                num: int, stg: int, close: float, rate: float, 
                                winner: float, top: float, mid: float, bot: float) -> bool:
        """更新最新策略数据，使用 REPLACE INTO 确保每个合约只有一条记录"""
        try:
            sql = """
                REPLACE INTO stratage_latest_gate 
                (stratage_id, product_code, stratage_time, num, stg, 
                 `close`, rate, winner, top, mid, but)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            params = (
                4,  # 固定策略ID
                symbol,
                stratage_time,
                num,
                stg,
                close,
                rate,
                winner,
                top,
                mid,
                bot
            )
            
            return self.execute_update(sql, params) > 0
            
        except Exception as e:
            self.logger.error(f"更新最新策略数据失败: {str(e)}")
            return False

    def QueryProductDataPartGateio(self, symbol: str, start_time: datetime, limit: int = None) -> List:
        """查询部分K线数据"""
        try:
            # 准备SQL和参数
            if limit:
                sql = """
                    SELECT `close`, price_time 
                    FROM gate_price_30m 
                    WHERE product_code = %s 
                    AND price_time >= %s 
                    ORDER BY price_time ASC 
                    LIMIT %s
                """
                params = (symbol, start_time, limit)
            else:
                sql = """
                    SELECT `close`, price_time 
                    FROM gate_price_30m 
                    WHERE product_code = %s 
                    AND price_time >= %s 
                    ORDER BY price_time ASC
                """
                params = (symbol, start_time)
            
            # 记录查询参数
            self.logger.debug(
                f"执行K线数据查询:\n"
                f"品种: {symbol}\n"
                f"开始时间: {start_time}\n"
                f"限制条数: {limit}"
            )
            
            results = self.execute_query(sql, params)
            
            # 转换结果
            converted_results = []
            for row in results:
                try:
                    # 由于使用了 DictCursor，需要用字典方式访问
                    close_price = float(row['close']) if row['close'] is not None else 0.0
                    price_time = row['price_time']
                    if close_price > 0 and price_time:
                        converted_results.append((close_price, price_time))
                except (TypeError, ValueError) as e:
                    self.logger.error(f"转换K线数据失败: {str(e)}, 数据: {row}")
                    continue
                
            # 记录查询结果
            self.logger.debug(
                f"查询 {symbol} K线数据结果:\n"
                f"原始数据条数: {len(results)}\n"
                f"有效数据条数: {len(converted_results)}"
            )
            
            return converted_results
            
        except Exception as e:
            self.logger.error(f"查询 {symbol} K线数据失败: {str(e)}")
            self.logger.error(f"参数: symbol={symbol}, start_time={start_time}, limit={limit}")
            return []

    def QueryProductDataAllGateio(self, symbol: str) -> List:
        """查询所有K线数据"""
        try:
            sql = """
                SELECT `close`, price_time 
                FROM gate_price_30m 
                WHERE product_code = %s 
                ORDER BY price_time ASC
            """
            return self.execute_query(sql, (symbol,))
        except Exception as e:
            self.logger.error(f"查询 {symbol} 所有K线数据失败: {str(e)}")
            return []

    def QueryStratageDetailLatestGateioComb(self, product_str: str, stratage_time: str) -> List:
        """查询组合策略最新数据"""
        try:
            sql = """
                SELECT product_code, stratage_time, `close`, 
                       top, mid, but, stg, num, rate, winner
                FROM stratage_latest_gate 
                WHERE product_code IN (%s) 
                AND stratage_time = %s
            """
            return self.execute_query(sql, (product_str, stratage_time))
        except Exception as e:
            self.logger.error(f"查询组合策略数据失败: {str(e)}")
            return []

    def QueryAllMaxDatePrice30MGateio(self) -> Dict[str, datetime]:
        """查询所有币种的最新K线时间"""
        try:
            sql = """
                SELECT product_code, MAX(price_time) as max_time
                FROM gate_price_30m
                GROUP BY product_code
            """
            results = self.execute_query(sql)
            
            if not results:
                return {}
            
            # 由于使用了 DictCursor，需要用字典方式访问结果
            latest_times = {}
            for row in results:
                try:
                    symbol = row['product_code']
                    max_time = row['max_time']
                    if symbol and max_time:
                        latest_times[symbol] = max_time
                except (KeyError, TypeError) as e:
                    self.logger.error(f"处理查询结果失败: {str(e)}, 数据: {row}")
                    continue
                
            return latest_times
            
        except Exception as e:
            self.logger.error(f"查询最新K线时间失败: {str(e)}")
            return {}

    def QueryStratageDetailLatestGateioAll(self) -> List[Dict]:
        """查询所有币种的最新策略数据"""
        try:
            sql = """
                SELECT product_code, stratage_time, `close`, 
                       top, mid, but, stg, num, rate, winner
                FROM stratage_latest_gate
            """
            results = self.execute_query(sql)
            if not results:
                return []
            
            return [{
                'product_code': row[0],
                'stratage_time': row[1],
                'close': float(row[2]),
                'top': float(row[3]),
                'mid': float(row[4]),
                'bot': float(row[5]),  # 注意这里是 but 映射到 bot
                'stg': int(row[6]),
                'num': int(row[7]),
                'rate': float(row[8]),
                'winner': float(row[9])
            } for row in results]
        except Exception as e:
            self.logger.error(f"查询所有币种最新策略数据失败: {str(e)}")
            return []

    def get_all_tradable_symbols(self) -> List[str]:
        """获取所有可交易品种"""
        sql = """
            SELECT DISTINCT product_code 
            FROM gate_price_30m 
            WHERE product_code IS NOT NULL
        """
        results = self.execute_query(sql)
        return [row['product_code'] for row in results if row.get('product_code')]

    def get_all_strategy_status(self) -> List[Dict]:
        """获取所有品种的策略状态"""
        sql = """
            SELECT product_code, stratage_time, `close`, top, mid, but as bot, 
                   stg, num, rate, winner
            FROM stratage_latest_gate 
            WHERE product_code IS NOT NULL
        """
        return self.execute_query(sql)

    def get_product_groups(self) -> List[Dict]:
        """获取有效的产品分组"""
        sql = """
            SELECT symbols 
            FROM product_groups 
            WHERE symbols IS NOT NULL 
            AND status = 1
        """
        return self.execute_query(sql)

    def close(self):
        """关闭数据库连接"""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
        except Exception as e:
            raise RuntimeError(f"关闭数据库连接失败: {str(e)}")