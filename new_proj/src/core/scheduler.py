from datetime import datetime, timedelta
import threading
import time
import logging
from typing import Callable, Dict

class TaskScheduler:
    """任务调度器"""
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._tasks: Dict[str, Callable] = {}
        self._lock = threading.Lock()
        self.is_running = False
        
    def add_task(self, name: str, task: Callable, 
                 critical_time: bool = False):
        """添加任务"""
        with self._lock:
            self._tasks[name] = {
                'func': task,
                'critical': critical_time
            }
            
    def start(self):
        """启动调度器"""
        with self._lock:
            if not self.is_running:
                self.is_running = True
                threading.Thread(target=self._scheduler_loop, 
                               daemon=True).start()
                
    def _scheduler_loop(self):
        """调度器主循环"""
        while self.is_running:
            now = datetime.now()
            
            # 处理关键时间点任务
            if now.minute in (0, 30):
                self._run_critical_tasks()
                
            # 处理数据补充任务
            elif (5 <= now.minute <= 25) or (35 <= now.minute <= 55):
                self._run_补充_tasks()
                
            time.sleep(1)  # 避免过度消耗CPU
            
    def _run_critical_tasks(self):
        """运行关键时间点任务"""
        for name, task in self._tasks.items():
            if task['critical']:
                try:
                    task['func']()
                except Exception as e:
                    self.logger.error(f"关键任务 {name} 执行失败: {str(e)}") 