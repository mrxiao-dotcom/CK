#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time
import schedule
import threading
import requests
from datetime import datetime
from core.strategy_calculator import StrategyCalculator
from utils.log_helper import setup_module_logger
from utils.config_manager import ConfigManager
from database.db_connector import DatabaseConnector
from typing import List, Set

class StrategyService:
    """策略服务"""
    def __init__(self):
        self.logger = setup_module_logger("strategy_service")
        self.config = ConfigManager()
        self.calculator = None
        self.is_running = False
        self.last_run_time = None
        self.db = DatabaseConnector()
        
        # 修改这里：使用正确的配置键名
        self.server = self.config.config.read_info("api", "quotesisserver") == '1'  # 改用 quotesisserver
        self.timeout = int(self.config.config.read_info("api", "timeout"))
        self.allow_run = True
        
        # 新增：用于存储特定品种
        self.specific_symbols: Set[str] = set()
        
    def setup_schedule(self):
        """设置定时任务"""
        schedule.clear()  # 清除所有现有任务
        
        # 1. 特定品种策略计算时间点
        # 每小时的0分5秒、1分、30分5秒和31分
        specific_minutes = ['00:25',  '30:25']
        for minute in specific_minutes:
            schedule.every().hour.at(minute).do(
                self.run_job_with_timeout,
                self.calculate_specific_strategies
            )
        
        # 2. 全品种策略计算时间点
        # 每小时的10分、25分、40分和55分
        all_minutes = ['15:00',  '45:00']
        for minute in all_minutes:
            schedule.every().hour.at(minute).do(
                self.run_job_with_timeout,
                self.calculate_all_strategies
            )
        
        self.logger.info("定时任务设置完成")
        self.logger.info(f"特定品种计算时间: {', '.join(specific_minutes)}")
        self.logger.info(f"全品种计算时间: {', '.join(all_minutes)}")

    def load_specific_symbols(self) -> bool:
        """加载特定品种列表"""
        try:
            # 修改SQL，只查询有效的分组
            sql = """
                SELECT symbols 
                FROM product_groups 
                WHERE symbols IS NOT NULL 
                AND status = 1
            """
            
            results = self.db.execute_query(sql)
            
            # 清空当前集合
            self.specific_symbols.clear()
            
            if not results:
                self.logger.warning("未找到有效的产品分组")
                return True
            
            # 处理所有结果
            for row in results:
                symbols_str = row.get('symbols', '')
                if not symbols_str:
                    continue
                
                # 分割并处理每个品种
                symbols = symbols_str.split('#')
                # 添加到集合中（自动去重）
                self.specific_symbols.update(
                    symbol.strip() 
                    for symbol in symbols 
                    if symbol and symbol.strip()
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"加载特定品种列表失败: {str(e)}")
            return False
            
    def calculate_specific_strategies(self):
        """计算特定品种的策略"""
        if not self.allow_run:
            self.logger.info("策略计算被暂停")
            return
        
        try:
            # 重新加载特定品种列表
            if not self.load_specific_symbols():
                raise RuntimeError("无法加载特定品种列表")
                
            if not self.specific_symbols:
                self.logger.warning("没有找到需要计算的特定品种")
                return
                
            self.logger.info(f"开始计算特定品种策略: {len(self.specific_symbols)} 个品种")
            
            # 确保计算器已初始化并启动
            if not self.calculator:
                self.calculator = StrategyCalculator()
                if not self.calculator.initialize():
                    raise RuntimeError("策略计算器初始化失败")
                self.calculator.start()
                
            # 计算每个品种的策略
            success_count = 0
            failed_symbols = []
            insufficient_data_symbols = []  # 新增：记录数据不足的品种
            
            for symbol in sorted(self.specific_symbols):
                if not self.allow_run:
                    self.logger.info("策略计算被中断")
                    break
                
                try:
                    result = self.calculator.calculate_strategy(symbol)
                    if result == True:  # 计算成功
                        success_count += 1
                    elif result == False:  # 计算失败
                        failed_symbols.append(symbol)
                    elif result == 'insufficient_data':  # 数据不足
                        insufficient_data_symbols.append(symbol)
                    
                except Exception as e:
                    self.logger.error(f"计算 {symbol} 策略失败: {str(e)}")
                    failed_symbols.append(symbol)
                    
            # 汇总结果
            summary = [f"策略计算完成 - 成功: {success_count}"]
            
            if insufficient_data_symbols:
                summary.append(f"数据不足: {len(insufficient_data_symbols)}")
            
            if failed_symbols:
                summary.append(f"失败: {len(failed_symbols)}")
            
            self.logger.info(", ".join(summary))
            
            # 只有在有问题的情况下才显示详细信息
            if insufficient_data_symbols:
                self.logger.warning(f"数据不足品种: {', '.join(insufficient_data_symbols)}")
            
            if failed_symbols:
                self.logger.error(f"计算失败品种: {', '.join(failed_symbols)}")
            
            # 计算完特定品种后，立即计算全市场
            self.calculate_all_strategies()
            
        except Exception as e:
            self.logger.error(f"计算特定品种策略失败: {str(e)}")
            
    def calculate_all_strategies(self):
        """计算所有品种的策略"""
        try:
            # 1. 一次性获取所有品种的最新策略状态
            strategies = self.db.get_all_strategy_status()
            strategy_cache = {
                row['product_code']: row 
                for row in strategies 
                if row['product_code']
            }
            
            # 2. 获取所有可交易品种
            symbols = self.db.get_all_tradable_symbols()
            
            if not symbols:
                self.logger.warning("没有找到需要计算的品种")
                return
            
            self.logger.info(f"开始检查 {len(symbols)} 个品种的策略状态")
            
            # 确保计算器已初始化
            if not self.calculator:
                self.calculator = StrategyCalculator()
                if not self.calculator.initialize():
                    raise RuntimeError("策略计算器初始化失败")
            
            # 计算结果统计
            no_update_needed = []
            updated_count = 0
            failed_symbols = []
            
            # 3. 使用缓存计算每个品种的策略
            for symbol in symbols:
                try:
                    result = self.calculator.calculate_strategy(symbol, strategy_cache)
                    if result is True:
                        if not self.calculator.last_update_count:
                            no_update_needed.append(symbol)
                        else:
                            updated_count += 1
                    elif result == 'insufficient_data':
                        # 数据不足时继续计算
                        updated_count += 1
                    else:
                        failed_symbols.append(symbol)
                except Exception as e:
                    self.logger.error(f"计算 {symbol} 策略失败: {str(e)}")
                    failed_symbols.append(symbol)
            
            # 4. 汇总输出结果
            summary = []
            if no_update_needed:
                summary.append(f"{len(no_update_needed)} 个品种无需更新")
                self.logger.debug(f"无需更新的品种: {', '.join(no_update_needed)}")
            
            if updated_count > 0:
                summary.append(f"{updated_count} 个品种已更新")
            
            if failed_symbols:
                summary.append(f"{len(failed_symbols)} 个品种计算失败")
                self.logger.error(f"计算失败的品种: {', '.join(failed_symbols)}")
            
            self.logger.info(f"策略计算完成 - {', '.join(summary)}")
            
        except Exception as e:
            self.logger.error(f"计算所有品种策略失败: {str(e)}")
            
    def run_job_with_timeout(self, job_func):
        """带超时的任务执行"""
        try:
            # 检查是否有相同任务正在运行
            if hasattr(self, '_running_job') and self._running_job:
                self.logger.warning(f"任务 {job_func.__name__} 已在运行中，跳过本次执行")
                return
            
            self._running_job = True
            
            try:
                # 创建线程执行任务
                thread = threading.Thread(target=job_func)
                thread.daemon = True  # 设置为守护线程
                thread.start()
                
                # 等待任务完成，最多等待超时时间
                thread.join(timeout=self.timeout)
                
                # 如果线程还在运行，说明超时了
                if thread.is_alive():
                    self.logger.error(f"任务执行超时: {job_func.__name__}")
                    self.allow_run = False
                    # 给一个短暂的时间让线程自行结束
                    thread.join(timeout=5)
                    self.allow_run = True
                    
            finally:
                self._running_job = False
                
        except Exception as e:
            self.logger.error(f"任务执行失败: {str(e)}")
            self._running_job = False

    def calculate_strategies(self):
        """计算策略"""
        try:
            if not self.calculator:
                self.calculator = StrategyCalculator()
                if not self.calculator.initialize():
                    raise RuntimeError("策略计算器初始化失败")
            
            # 如果是服务器，则自动启动执行，并且向数据库写入正常运转的信息
            if self.server:
                try:
                    self.allow_run = True
                    self.db.UpdateWatchApp("future_strategy_gateio")
                except Exception as e:
                    self.logger.error(f"更新服务状态失败: {str(e)}")
            else:
                # 如果是备份机，先检查服务器的信息
                try:
                    # 使用正确的配置键名
                    dbback = int(self.config.config.read_info("api", "quotesdbback"))  # 改用 quotesdbback
                    remote_db = DatabaseConnector()
                    remote_db.initialize(dbback)
                    ret = remote_db.QueryWathcApp("future_strategy_gateio")
                    
                    dt1 = datetime.now()
                    dt2 = ret['status_time']
                    timedelta = dt1 - dt2
                    
                    if timedelta.total_seconds() > self.timeout:
                        self.allow_run = True
                        remote_db.UpdateWatchAppBack("future_strategy_gateio")
                        self._send_warning()
                    else:
                        self.allow_run = False
                        self.logger.info("服务器运行正常，备份程序挂起，1分钟后再检查...")
                except Exception as e:
                    self.logger.error(f"检查主服务器状态失败: {str(e)}")
                    self.allow_run = True  # 远程数据库访问遇到故障，立马启动
            
            if self.allow_run:
                self.calculator.calculate_latest_strategies()
            
        except Exception as e:
            self.logger.error(f"策略计算失败: {str(e)}")
            
    def _send_warning(self):
        """发送警告消息"""
        try:
            title = 'Gateio-CTA 策略服务器故障'
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
            
    def run_scheduler(self):
        """运行调度器"""
        self.logger.info("启动调度器...")
        last_log_time = None
        last_next_run = None  # 添加这个变量来跟踪上次的执行时间
        
        while self.is_running:
            try:
                current_time = datetime.now()
                
                # 每分钟检查一次下次执行时间
                if not last_log_time or (current_time - last_log_time).seconds >= 60:
                    next_run = schedule.next_run()
                    # 只有当下次执行时间发生变化时才打印日志
                    if next_run and (not last_next_run or next_run != last_next_run):
                        self.logger.info(f"下次任务执行时间: {next_run}")
                        last_next_run = next_run
                    last_log_time = current_time
                
                # 运行到期的任务
                schedule.run_pending()
                
                # 使用更短的睡眠时间，提高响应性
                for _ in range(10):  # 将1秒分成10次100ms的检查
                    if not self.is_running:
                        break
                    time.sleep(0.1)
                    
            except Exception as e:
                self.logger.error(f"调度器运行异常: {str(e)}")
                time.sleep(5)  # 出错后短暂等待
                
    def reinitialize(self):
        """重新初始化所有组件"""
        try:
            schedule.clear()
            self.setup_schedule()
            if self.calculator:
                self.calculator.stop()
                self.calculator = None
        except Exception as e:
            self.logger.error(f"重新初始化失败: {str(e)}")
            
    def stop(self):
        """停止服务"""
        self.is_running = False
        if self.calculator:
            self.calculator.stop()
            
    def start(self):
        """启动策略服务"""
        try:
            # 初始化数据库连接
            source = int(self.config.config.read_info("api", "dbsource"))
            if not self.db.initialize(source):
                raise RuntimeError("数据库初始化失败")
            
            # 测试数据库连接
            if not self.db.execute_query("SELECT 1"):
                raise RuntimeError("数据库连接测试失败")
            
            # 加载特定品种列表
            if not self.load_specific_symbols():
                raise RuntimeError("加载特定品种列表失败")
                
            self.is_running = True
            
            # 设置定时任务
            self.setup_schedule()
            
            # 立即执行一次特定品种策略计算
            self.calculate_specific_strategies()
            
            # 启动调度器
            self.run_scheduler()
            
        except Exception as e:
            self.logger.error(f"启动策略服务失败: {str(e)}")
            raise e
            
def main():
    """主函数"""
    try:
        service = StrategyService()
        service.start()
    except KeyboardInterrupt:
        print("\n收到退出信号，正在停止服务...")
        service.stop()
    except Exception as e:
        print(f"服务异常退出: {str(e)}")
        sys.exit(1)
        
if __name__ == '__main__':
    main() 