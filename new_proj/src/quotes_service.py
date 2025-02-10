import os
import sys
import logging
from datetime import datetime
import time
import signal
import threading
# 初始化运行时环境
from runtime_hook import init_runtime
init_runtime()

from core.quotes_manager import QuotesManager
from utils.log_helper import get_logger
from utils.config_manager import ConfigManager

def main():
    """主函数"""
    logger = get_logger('QuotesService')
    quotes_manager = None
    
    try:
        logger.info("=== 行情服务启动 ===")
        logger.info(f"当前工作目录: {os.getcwd()}")
        logger.info(f"Python路径: {sys.path}")
        
        # 初始化配置管理器
        try:
            config = ConfigManager()
            _ = config.database
            logger.info("配置文件加载成功")
        except Exception as e:
            logger.error(f"配置加载失败: {str(e)}")
            return
        
        # 创建并启动行情管理器
        quotes_manager = QuotesManager()
        quotes_manager.start()
        
        # 主循环 - 使用事件等待而不是简单的 sleep
        stop_event = threading.Event()
        
        def signal_handler(signum, frame):
            logger.info("收到退出信号，开始优雅停止...")
            stop_event.set()
            
        # 注册信号处理
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # 等待停止信号
        while not stop_event.is_set():
            try:
                # 每5秒检查一次服务状态
                if stop_event.wait(timeout=5):
                    break
                    
                # 可以在这里添加服务状态检查
                if quotes_manager and not quotes_manager._thread.is_alive():
                    logger.error("行情处理线程已停止，准备重启服务...")
                    quotes_manager.stop()
                    quotes_manager.start()
                    
            except Exception as e:
                logger.error(f"主循环异常: {str(e)}")
                break
                
    except Exception as e:
        logger.error(f"服务运行异常: {str(e)}")
        logger.exception("详细错误信息：")
        
    finally:
        # 确保清理资源
        try:
            if quotes_manager:
                logger.info("正在停止行情管理器...")
                quotes_manager.stop()
                logger.info("行情管理器已停止")
        except KeyboardInterrupt:
            logger.info("再次收到中断信号，强制退出...")
        except Exception as e:
            logger.error(f"停止服务时发生异常: {str(e)}")
        finally:
            logger.info("=== 行情服务已退出 ===")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
    except Exception as e:
        print(f"程序异常退出: {str(e)}") 