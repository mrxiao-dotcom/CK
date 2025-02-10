import os
import configparser

class IniReader:
    """INI配置文件读取器"""
    def __init__(self, file_path: str):
        self.config = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"配置文件不存在: {file_path}")
        self.config.read(file_path, encoding='utf-8')
        
    def read_info(self, section: str, key: str) -> str:
        """读取配置项"""
        try:
            value = self.config.get(section, key).strip()
            return value
        except Exception as e:
            raise ValueError(f"读取配置失败 - section: {section}, key: {key} - {str(e)}") 