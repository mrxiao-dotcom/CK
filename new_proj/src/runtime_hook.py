import os
import sys

def init_runtime():
    """初始化运行时环境"""
    # 获取当前文件所在目录的上级目录
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(current_dir, 'src')
    
    # 添加项目内的路径
    paths = [
        current_dir,  # new_proj
        src_dir,      # new_proj/src
    ]
    
    # 将路径添加到sys.path
    for path in paths:
        if path not in sys.path:
            sys.path.insert(0, path)

    # 设置工作目录为 src 目录
    os.chdir(src_dir) 