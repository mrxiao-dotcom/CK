from configparser import ConfigParser
import os

class ReadConfigFile(object):

    def __init__(self, filename="config.ini"):
        self.filename = filename

    def read_info(self,group,title):
        conn = ConfigParser()
        file_path = os.path.join(os.path.abspath('.'),self.filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError("文件不存在")

        conn.read(file_path)
        result = conn.get(group,title)

        return result