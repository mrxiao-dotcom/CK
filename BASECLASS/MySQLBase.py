from COMM.trade_common import TradePool


class MSSQL:

    def __init__(self, data_source):
        self.trade_pool = TradePool(data_source)


    def __get_connect(self):
        self.conn = self.trade_pool.GetConnection()
        cur = self.conn.cursor()
        if not cur:
            raise(NameError, "连接数据库失败")
        else:
            return cur

    def ExecQuery(self, sql):
        cur = self.__get_connect()
        try:
            cur.execute(sql)
            res_list = cur.fetchall()
        finally:
            self.conn.close()
        return res_list

    def ExecNonQuery(self, sql):
        cur = self.__get_connect()
        try:
            cur.execute(sql)
            self.conn.commit()
        finally:
            self.conn.close()


    def ExecUpdate(self,sql):
        cur = self.__get_connect()
        rowcount = 0
        try:
            cur.execute(sql)
            rowcount = cur.rowcount
            self.conn.commit()
        finally:
            self.conn.close()
        return rowcount
