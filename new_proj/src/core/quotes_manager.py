import os
import sys
import threading
import time
import logging
from datetime import datetime

# 初始化运行时环境
from runtime_hook import init_runtime
init_runtime()

from typing import Optional
from utils.log_helper import get_logger
from utils.config_manager import ConfigManager
from database.db_connector import DatabaseConnector
from .market_data import MarketDataManager
import requests

class QuotesManager:
    """行情管理器"""
    _instance: Optional['QuotesManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(QuotesManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.logger = get_logger(__name__)
            self.config = ConfigManager()
            self.db = DatabaseConnector()
            self.market_data = None
            self.allow_run = True
            
            # 添加服务器配置
            try:
                server_config = self.config.server
                self.server = server_config.get('is_main', False)  # 是否为主服务器
                self.timeout = server_config.get('timeout', 300)   # 超时时间，默认300秒
                self.db_backup = server_config.get('db_backup')    # 备份数据库配置
            except Exception as e:
                self.logger.error(f"读取服务器配置失败: {str(e)}")
                raise
            
            # 初始化数据库连接
            if not self.db.initialize(self.config.database['source']):
                self.logger.error("数据库初始化失败")
                raise RuntimeError("数据库初始化失败")
            
            # 初始化市场数据管理器
            try:
                self.market_data = MarketDataManager()
                if not self.market_data.initialize():
                    raise RuntimeError("市场数据管理器初始化失败")
                self.logger.info("市场数据管理器初始化成功")
            except Exception as e:
                self.logger.error(f"市场数据管理器初始化失败: {str(e)}")
                raise
            
            self.is_running = False
            self._lock = threading.Lock()
            self._last_update_minute = -1  # 记录上次更新的分钟
            
            self._initialized = True
            
    def start(self):
        """启动行情管理器"""
        try:
            # 检查是否允许运行
            if not self._check_run_status():
                self.logger.info("当前为备份服务器，等待主服务器状态...")
                return
            
            # 启动市场数据管理器
            if self.market_data:
                self.market_data.start()
                self._check_historical_data()
                
                # 启动行情处理线程
                if not self._start_processing_thread():
                    raise RuntimeError("行情处理线程启动失败")
            
            return True
            
        except Exception as e:
            self.logger.error(f"启动失败: {str(e)}")
            return False
    
    def stop(self):
        """停止行情管理器"""
        try:
            self.logger.info("正在停止行情管理器...")
            
            # 1. 设置停止标志
            self.allow_run = False
            
            # 2. 停止行情处理线程
            if self._thread and self._thread.is_alive():
                try:
                    self._thread.join(timeout=5)  # 减少超时时间
                    if self._thread.is_alive():
                        self.logger.warning("行情处理线程未能在5秒内停止")
                except Exception as e:
                    self.logger.error(f"停止行情处理线程失败: {str(e)}")
            
            # 3. 停止市场数据管理器
            if self.market_data:
                self.market_data.stop()
                self.logger.info("市场数据管理器停止成功")
            
            # 4. 清理资源
            try:
                if self.db:
                    self.db.close()
            except Exception as e:
                self.logger.error(f"清理资源失败: {str(e)}")
            
            self.logger.info("行情管理器停止成功")
            
        except Exception as e:
            self.logger.error(f"行情管理器停止失败: {str(e)}")
            raise
            
    def _check_run_status(self) -> bool:
        """检查是否允许运行"""
        try:
            if self.server:  # 主服务器
                self.allow_run = True
                self.db.UpdateWatchApp("future_quotes_gateio")
                return True
            else:  # 备份服务器
                try:
                    remote_db = DatabaseConnector()
                    if not remote_db.initialize(self.db_backup):
                        self.logger.error("备份数据库初始化失败")
                        return False
                    
                    ret = remote_db.QueryWatchApp("future_quotes_gateio")
                    if not ret:
                        self.allow_run = True
                        return True
                    
                    dt1 = datetime.now()
                    dt2 = ret['status_time']
                    timedelta = dt1 - dt2
                    
                    if timedelta.total_seconds() > self.timeout:
                        self.allow_run = True
                        remote_db.UpdateWatchAppBack("future_quotes_gateio")
                        self._send_warning()
                        return True
                        
                    self.allow_run = False
                    self.logger.info("服务器运行正常，备份程序挂起，1分钟后再检查...")
                    return False
                    
                except Exception as e:
                    self.logger.error(f"检查主服务器状态失败: {str(e)}")
                    self.allow_run = True  # 远程数据库访问遇到故障，立马启动
                    return True
                    
        except Exception as e:
            self.logger.error(f"检查运行状态失败: {str(e)}")
            return False
            
    def _initialize_resources(self) -> bool:
        """初始化资源"""
        try:
            # 初始化市场数据管理器
            if not self.market_data.initialize():
                raise RuntimeError("市场数据管理器初始化失败")
                
            return True
            
        except Exception as e:
            self.logger.error(f"初始化资源失败: {str(e)}")
            return False
            
    def _process_quotes(self):
        """处理行情数据"""
        try:
            last_check_time = time.time()
            last_update_minute = -1
            
            while self.allow_run:
                try:
                    current_time = datetime.now()
                    current_minute = current_time.minute
                    current_hour = current_time.hour
                    
                    # 避免在同一分钟重复更新
                    if current_minute != last_update_minute:  # 每分钟都检查一次
                        # 在整点和半点更新行情
                        if current_minute in (0, 30):
                            self.logger.info(f"{current_hour:02d}:{current_minute:02d} 开始更新行情...")
                            self.market_data.update_latest_data()
                            last_update_minute = current_minute
                            last_check_time = time.time()
                            self.logger.info(f"{current_hour:02d}:{current_minute:02d} 行情更新完成")
                        
                        # 在5分和35分检查历史数据
                        elif current_minute in (5, 35):
                            self.logger.info(f"{current_hour:02d}:{current_minute:02d} 开始检查历史数据...")
                            self._check_historical_data()
                            last_update_minute = current_minute
                            last_check_time = time.time()
                            self.logger.info(f"{current_hour:02d}:{current_minute:02d} 历史数据检查完成")
                        
                        # 每10分钟记录一次心跳
                        elif current_minute % 10 == 0:
                            self.logger.info(f"行情服务运行正常 - {current_hour:02d}:{current_minute:02d}")
                            last_update_minute = current_minute
                    
                    time.sleep(1)  # 每秒检查一次
                    
                except Exception as e:
                    self.logger.error(f"行情处理异常: {str(e)}")
                    time.sleep(5)  # 出错后等待5秒
                
        except Exception as e:
            self.logger.error(f"行情处理线程异常: {str(e)}")
        finally:
            self.allow_run = False
            self.logger.warning("行情处理线程已停止")

    def _update_latest_data(self):
        """更新最新行情数据"""
        try:
            if not self.market_data:
                raise RuntimeError("市场数据管理器未初始化")
            
            # 直接调用 market_data 的更新方法
            self.market_data.update_latest_data()
            
        except Exception as e:
            self.logger.error(f"更新最新数据失败: {str(e)}")

    def _process_update_queue(self):
        """处理数据补充队列"""
        try:
            if not self.market_data:
                raise RuntimeError("市场数据管理器未初始化")
            
            # 直接调用 market_data 的处理方法
            self.market_data.process_update_queue()
            
        except Exception as e:
            self.logger.error(f"处理数据补充队列失败: {str(e)}")
            
    def _send_warning(self):
        """发送警告消息"""
        try:
            title = 'Gateio-CTA 行情服务器故障'
            mydata = {
                'text': title,
                'desp': "速速检查106服务器"
            }
            
            # admin 1 xiaoj
            url = "http://wx.xtuis.cn/BDGGZgR856AueOk6JXoCERIyi.send"
            requests.post(url, data=mydata)
            
            # admin 2 gy
            url = "http://wx.xtuis.cn/DOyVyJTsYb8UfxLV4qtWPr0t6.send"
            requests.post(url, data=mydata)
            
        except Exception as e:
            self.logger.error(f"发送警告失败: {str(e)}")

    def _start_processing_thread(self):
        """启动行情处理线程"""
        try:
            self._thread = threading.Thread(target=self._process_quotes, daemon=True)
            self._thread.start()
            return True
        except Exception as e:
            self.logger.error(f"启动处理线程失败: {str(e)}")
            return False

    def _stop_processing_thread(self):
        """停止行情处理线程"""
        try:
            if self._thread and self._thread.is_alive():
                self.allow_run = False
                self._thread.join(timeout=10)
                if self._thread.is_alive():
                    self.logger.warning("行情处理线程未能在10秒内停止")
                else:
                    self.logger.info("行情处理线程已停止")
        except Exception as e:
            self.logger.error(f"停止行情处理线程失败: {str(e)}")

    def _check_historical_data(self):
        """检查历史数据连续性"""
        try:
            if not self.market_data:
                raise RuntimeError("市场数据管理器未初始化")
            
            # 获取所有品种
            symbols = self.market_data.get_all_symbols()
            if not symbols:
                self.logger.warning("无可交易品种")
                return
            
            discontinuous_symbols = []
            for symbol in symbols:
                try:
                    # 检查每个品种的数据状态
                    need_update, _ = self.market_data._check_symbol_data_status(symbol)
                    if need_update:
                        discontinuous_symbols.append(symbol)
                except Exception as e:
                    self.logger.error(f"检查 {symbol} 历史数据状态失败: {str(e)}")
            
            if discontinuous_symbols:
                self.logger.warning(
                    f"检测到 {len(discontinuous_symbols)} 个品种数据不连续: "
                    f"{', '.join(discontinuous_symbols)}\n"
                    "这些品种将在下一次数据补充时进行处理"
                )
            else:
                self.logger.info("所有品种历史数据连续")
            
        except Exception as e:
            self.logger.error(f"检查历史数据失败: {str(e)}") 