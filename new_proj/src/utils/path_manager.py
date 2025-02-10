import os
import sys
import shutil
from typing import List, Optional

class PathManager:
    @staticmethod
    def setup_paths():
        """设置Python路径"""
        # 获取当前文件的绝对路径
        current_file = os.path.abspath(__file__)
        
        # 尝试确定项目根目录
        # 1. 首先检查是否在 new_proj/src/utils 下
        if 'new_proj/src/utils' in current_file or 'new_proj\\src\\utils' in current_file:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        # 2. 然后检查是否在 src/utils 下
        elif 'src/utils' in current_file or 'src\\utils' in current_file:
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        # 3. 最后假设在 utils 下
        else:
            project_root = os.path.dirname(os.path.dirname(current_file))
            
        # 获取 src 目录
        src_dir = os.path.join(project_root, 'src')
        if not os.path.exists(src_dir):
            src_dir = project_root  # 如果没有 src 目录，就用项目根目录
            
        # 需要添加到Python路径的目录
        base_paths = [
            project_root,
            src_dir,
            'BASECLASS',
            'COMM',
            'gate_api'
        ]
        
        # 尝试不同的路径组合
        for base in [project_root, os.path.dirname(project_root)]:
            for path in base_paths:
                full_path = path if os.path.isabs(path) else os.path.join(base, path)
                if os.path.exists(full_path) and full_path not in sys.path:
                    sys.path.insert(0, full_path)
                    print(f"Added path: {full_path}")
        
        # 处理配置文件
        PathManager._setup_config(project_root)
        
        # 打印环境信息
        PathManager._print_environment_info()
    
    @staticmethod
    def _setup_config(project_root: str) -> None:
        """设置配置文件"""
        config_file = 'gate_config.ini'
        
        # 尝试多个可能的配置文件位置
        config_paths = [
            os.path.join(project_root, 'config', config_file),
            os.path.join(project_root, config_file),
            os.path.join(os.getcwd(), config_file),
            os.path.join(os.path.dirname(project_root), 'config', config_file),
            os.path.join(os.path.dirname(project_root), config_file)
        ]
        
        # 找到有效的配置文件
        valid_config = PathManager._find_valid_config(config_paths)
        if not valid_config:
            raise FileNotFoundError(f"找不到配置文件: {config_file}，已检查路径: {', '.join(config_paths)}")
            
        # 确保工作目录有配置文件
        work_dir_config = os.path.join(os.getcwd(), config_file)
        if valid_config != work_dir_config:
            shutil.copy2(valid_config, work_dir_config)
            print(f"已复制配置文件到工作目录: {work_dir_config}")
    
    @staticmethod
    def _find_valid_config(paths: List[str]) -> Optional[str]:
        """查找有效的配置文件"""
        for path in paths:
            if os.path.exists(path):
                print(f"找到配置文件: {path}")
                return path
        return None
    
    @staticmethod
    def _print_environment_info() -> None:
        """打印环境信息"""
        print("\nEnvironment Information:")
        print("-" * 50)
        
        print("\nPython Path:")
        for path in sys.path:
            print(f"  {path}")
            
        print("\nWorking Directory:")
        print(f"  {os.getcwd()}")
        
        print("\nDirectory Contents:")
        try:
            contents = os.listdir(os.getcwd())
            for item in contents:
                print(f"  {item}")
        except Exception as e:
            print(f"  Error listing directory: {str(e)}")
            
        print("\nEnvironment Variables:")
        relevant_vars = ['PYTHONPATH', 'GATE_CONFIG_PATH']
        for var in relevant_vars:
            value = os.environ.get(var, 'Not Set')
            print(f"  {var}: {value}")
            
        print("-" * 50) 