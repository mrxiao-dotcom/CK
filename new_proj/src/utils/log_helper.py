import os
import logging
import traceback
from typing import Optional
from datetime import datetime

def setup_module_logger(module_name: str) -> logging.Logger:
    """为模块创建logger"""
    # 直接使用 get_logger，确保所有模块使用相同的日志配置
    return get_logger(module_name)

def log_exception(logger: logging.Logger, e: Exception, msg: str):
    """记录异常信息"""
    logger.error(f"{msg}: {type(e).__name__}: {str(e)}")
    logger.exception("详细错误信息：")

def get_logger(name: str) -> logging.Logger:
    """获取日志记录器"""
    logger = logging.getLogger(name)
    
    # 如果已经有处理器，说明已经初始化过，直接返回
    if logger.handlers:
        return logger
        
    # 设置日志级别
    logger.setLevel(logging.DEBUG)
    
    # 创建格式化器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - [%(filename)s:%(lineno)d] - %(levelname)s - %(message)s'
    )
    
    # 创建文件处理器
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, f'quotes_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)  # 控制台只显示 INFO 及以上级别
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def set_log_level(logger: logging.Logger, level: str):
    """设置日志级别"""
    level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level) 