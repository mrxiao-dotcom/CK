import os
import sys

def setup_environment():
    """设置运行环境"""
    # 获取项目根目录
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # 添加必要的路径
    sys.path.insert(0, project_root)
    sys.path.insert(0, os.path.join(project_root, 'src'))
    
    # 添加原有代码的路径
    sys.path.insert(0, os.path.join(project_root, 'BASECLASS'))
    sys.path.insert(0, os.path.join(project_root, 'COMM'))
    sys.path.insert(0, os.path.join(project_root, 'gate_api'))

if __name__ == "__main__":
    setup_environment()
    
    # 导入并运行服务
    from src.quotes_service import run_quotes_service
    run_quotes_service() 