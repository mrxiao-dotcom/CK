import json
import datetime
import traceback
import pymysql as mysql
from dbutils.pooled_db import PooledDB

#数据库源对象
class DataSource:
    def __init__(self, data_source):
        self.data_source = data_source
        self.GetDataSource()

    def GetDataSource(self):
        if self.data_source == 1:
            self.host = "127.0.0.1"
            self.user = "autotrader"
            self.passwd = "Xj774913@"
            self.port = 3306
            self.db = "autotrader"

        elif self.data_source == 2:
            self.host = "82.157.29.40"
            self.user = "dynbb"
            self.passwd = "XJdynbb@)@!999"
            self.port = 3306
            self.db = "autotrader"

        elif self.data_source == 3:
            self.host = "1.117.138.190"
            self.user = "dynbb"
            self.passwd = "XJdynbb@)@!999"
            self.port = 3306
            self.db = "autotrader"

        elif self.data_source == 4:
            self.host = "172.21.0.14"
            self.user = "autotrader"
            self.passwd = "XJdynbb@)@!999"
            self.port = 3306
            self.db = "autotrader"

        elif self.data_source == 5:
            self.host = "10.17.31.47"
            self.user = "root"
            self.passwd = "fsR6Hf$"
            self.port = 3306
            self.db = "autotrader"

        elif self.data_source == 6:
            self.host = "10.17.31.101"
            self.user = "xiaojian"
            self.passwd = "LszWvLxLMh"
            self.port = 33060
            self.db = "ynquantdb"

        elif self.data_source == 7:
            self.host = "127.0.0.1"
            self.user = "root"
            self.passwd = "Xj774913@"
            self.port = 3306
            self.db = "autotrader"

        elif self.data_source == 8:
            self.host = "123.207.82.73"
            self.user = "root"
            self.passwd = "Xj774913@"
            self.port = 3306
            self.db = "autotrader"
        elif self.data_source == 9:
            self.host = "82.157.29.40"
            self.user = "dynbb"
            self.passwd = "XJdynbb@)@!999"
            self.port = 3306
            self.db = "dynbb"
        elif self.data_source == 10: # 香港2号
            self.host = "45.153.131.230"
            self.user = "root"
            self.passwd = "Xj774913@"
            self.port = 3306
            self.db = "autotrader"
        elif self.data_source == 11: # 香港3号
            self.host = "203.160.54.188"
            self.user = "root"
            self.passwd = "Xj774913@"
            self.port = 3306
            self.db = "autotrader"
        elif self.data_source == 12: # 香港2号
            self.host = "45.153.131.217"
            self.user = "root"
            self.passwd = "Xj774913@"
            self.port = 3306
            self.db = "autotrader"
        elif self.data_source == 13: # 香港3号
            self.host = "185.242.235.85"
            self.user = "root"
            self.passwd = "Xj774913@"
            self.port = 3306
            self.db = "autotrader"
        elif self.data_source == 14:
            self.host = "10.17.31.104"
            self.user = "root"
            self.passwd = "Xj774913@"
            self.port = 3306
            self.db = "autotrader"
        elif self.data_source == 15:
            self.host = "10.17.31.106"
            self.user = "root"
            self.passwd = "Xj774913@"
            self.port = 3306
            self.db = "autotrader"

# 全局数据库连接池
class TradePool:
    # 获取连接
    def GetConnection(self):
        return self.POOL.connection()

    def __init__(self,data_source):
        self.data_source = DataSource(data_source)
        self.POOL = PooledDB(
            creator=mysql,  # 使用链接数据库的模块
            mincached=10,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
            maxcached=10,  # 链接池中最多闲置的链接，0和None不限制
            maxshared=0,  # 链接池中最多共享的链接数量，0和None表示全部共享。
            # PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxcached永远为0，所以永远是所有链接都共享。
            maxconnections=100,  # 连接池允许的最大连接数，0和None表示不限制连接数
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=['SET AUTOCOMMIT = 1'],  # 开始会话前执行的命令列表。如：["set datestyle to ...", "set time zone ..."]
            host=self.data_source.host,
            port=self.data_source.port,
            user=self.data_source.user,
            passwd=self.data_source.passwd,
            db=self.data_source.db,
            use_unicode=True,
            charset="GBK")




    # 执行数据库查询
    def ExecuteQuery(self, sql, dict_flag=False):
        conn = self.POOL.connection()
        try:
            if dict_flag:
                cursor = conn.cursor(cursor=mysql.cursors.DictCursor)
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
            else:
                cursor = conn.cursor()
                cursor.execute(sql)
                result = cursor.fetchall()
                return result
        except:
            pass
            print(traceback.format_exc())
        finally:
            conn.close()
        return []


    # 执行数据库查询
    def PrepareQuery(self,sql, params, dict_flag=False):
        conn = self.POOL.connection()
        try:
            if dict_flag:
                cursor = conn.cursor(cursor=mysql.cursors.DictCursor)
                cursor.execute(sql, params)
                result = cursor.fetchall()
                return result
            else:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                result = cursor.fetchall()
                return result
        except:
            pass
            print(traceback.format_exc())
        finally:
            conn.close()
        return []


    # 执行数据库更新操作，包括新增、修改、删除
    def ExecuteUpdate(self,sql):
        conn = self.POOL.connection()
        try:
            cursor = conn.cursor()
            result = cursor.execute(sql)
            conn.commit()
            return result
        except:
            conn.rollback()
            print(traceback.format_exc())
        finally:
            conn.close()
        return 0


    # 执行数据库更新操作，包括新增、修改、删除
    def PrepareUpdate(self,sql, obj):
        conn = self.POOL.connection()
        try:
            if isinstance(obj, list):
                cursor = conn.cursor()
                result = cursor.executemany(sql, obj)
            else:
                cursor = conn.cursor()
                result = cursor.execute(sql, obj)
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            print(traceback.format_exc())
            print(traceback.print_exc())
            print('str(Exception):%s' % (str(Exception)))
        finally:
            conn.close()
        return 0


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, cls=DateEncoder)
