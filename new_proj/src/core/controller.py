from .market_data import MarketDataManager
from .strategy_processor import StrategyProcessor
from .scheduler import TaskScheduler
from database.db_connector import DatabaseConnector
import logging

class MarketController:
    """市场控制器"""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.market_data = MarketDataManager()
        self.strategy = StrategyProcessor()
        self.scheduler = TaskScheduler()
        self.db = DatabaseConnector()
        
    def initialize(self):
        """初始化系统"""
        try:
            # 初始化数据库连接
            if not self.db.initialize(1):
                raise RuntimeError("数据库初始化失败")
                
            # 设置任务
            self.scheduler.add_task(
                "market_data", 
                self.market_data._process_critical_time_data,
                critical_time=True
            )
            
            self.scheduler.add_task(
                "strategy", 
                self.strategy._process_strategy,
                critical_time=True
            )
            
            # 启动各个组件
            self.market_data.start()
            self.strategy.start()
            self.scheduler.start()
            
            return True
            
        except Exception as e:
            self.logger.error(f"系统初始化失败: {str(e)}")
            return False 