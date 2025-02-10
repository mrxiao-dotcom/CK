import os
import sys
import logging
from utils.path_manager import PathManager
from core.quotes_manager import QuotesManager
import time

def setup_logging():
    """配置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/quotes.log'),
            logging.StreamHandler()
        ]
    )

def main():
    # 设置路径
    PathManager.setup_paths()
    
    # 设置日志
    setup_logging()
    
    # 创建并启动行情管理器
    quotes_manager = QuotesManager()
    
    try:
        quotes_manager.start()
        
        # 保持程序运行
        while True:
            try:
                time.sleep(1)
            except KeyboardInterrupt:
                break
                
    except Exception as e:
        logging.error(f"程序运行异常: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 