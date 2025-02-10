import configparser
import os

class ReadConfigFile:
    def __init__(self, file_path):
        self.file_path = file_path
        self.conn = configparser.ConfigParser(
            inline_comment_prefixes=('#', ';'),  # 支持 # 和 ; 作为注释
            allow_no_value=True,                 # 允许没有值的配置项
            delimiters=('=', ':')                # 支持 = 和 : 作为分隔符
        )
        # 使用 UTF-8 编码读取配置文件
        with open(file_path, 'r', encoding='utf-8') as f:
            self.conn.read_file(f)

    def read_info(self, section, key):
        try:
            value = self.conn.get(section, key)
            # 去除可能的行尾注释
            value = value.split('#')[0].split(';')[0].strip()
            return value
        except Exception as e:
            print(f"读取配置文件失败: {str(e)}")
            return None