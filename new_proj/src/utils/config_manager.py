from typing import Optional
import os
import logging
from .ini_reader import IniReader

class ConfigManager:
    """配置管理器 - 单例模式"""
    _instance: Optional['ConfigManager'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self.config_path = self._get_config_path()
            self.config = IniReader(self.config_path)
            self._initialized = True
    
    def _get_config_path(self) -> str:
        """获取配置文件路径"""
        # 首先检查环境变量
        config_path = os.environ.get('GATE_CONFIG_PATH')
        if config_path:
            self.logger.info(f"从环境变量获取配置文件路径: {config_path}")
            if os.path.exists(config_path):
                return config_path
            else:
                self.logger.warning(f"环境变量指定的配置文件不存在: {config_path}")
        
        # 获取 new_proj 目录路径（当前文件所在目录的上上级）
        current_file = os.path.abspath(__file__)
        utils_dir = os.path.dirname(current_file)
        src_dir = os.path.dirname(utils_dir)
        new_proj_dir = os.path.dirname(src_dir)
        
        self.logger.info(f"当前文件: {current_file}")
        self.logger.info(f"utils目录: {utils_dir}")
        self.logger.info(f"src目录: {src_dir}")
        self.logger.info(f"项目根目录: {new_proj_dir}")
        
        # 只在 new_proj 目录内查找
        possible_paths = [
            os.path.join(new_proj_dir, 'config', 'gate_config.ini'),  # 优先检查 config 目录
            os.path.join(new_proj_dir, 'gate_config.ini'),
            os.path.join(new_proj_dir, 'src', 'config', 'gate_config.ini')
        ]
        
        # 记录日志
        self.logger.info("正在查找配置文件，检查以下路径：")
        for path in possible_paths:
            self.logger.info(f"- {path}")
            if os.path.exists(path):
                self.logger.info(f"找到配置文件: {path}")
                return path
            else:
                self.logger.info(f"文件不存在: {path}")  # 改为 info 级别以便查看
        
        error_msg = f"找不到配置文件 gate_config.ini，已检查路径:\n" + "\n".join(f"- {p}" for p in possible_paths)
        self.logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    
    @property
    def database(self) -> dict:
        """获取数据库配置"""
        try:
            return {
                'host': self.config.read_info("database", "host"),
                'port': int(self.config.read_info("database", "port")),
                'user': self.config.read_info("database", "user"),
                'password': self.config.read_info("database", "password"),
                'database': self.config.read_info("database", "database"),
                'source': int(self.config.read_info("api", "dbsource")),
                'backup': int(self.config.read_info("api", "quotesdbback")),
                'timeout': int(self.config.read_info("api", "timeout"))
            }
        except Exception as e:
            self.logger.error(f"读取数据库配置失败: {str(e)}")
            raise
    
    @property
    def server(self) -> dict:
        """获取服务器配置"""
        return {
            'is_main': self.config.read_info("api", "quotesisserver") == '1',
            'timeout': int(self.config.read_info("api", "timeout"))
        }
    
    def get_api_config(self, use_backup: bool = False) -> dict:
        """获取API配置，支持主备切换"""
        if use_backup:
            return {
                'key': self.config.read_info("api_keys", "backup_key"),
                'secret': self.config.read_info("api_keys", "backup_secret")
            }
        return {
            'key': self.config.read_info("api_keys", "main_key"),
            'secret': self.config.read_info("api_keys", "main_secret")
        } 