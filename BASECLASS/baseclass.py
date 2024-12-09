# !/user/bin/env python3
# -*- coding: utf-8 -*-
import time

### pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt ###
class BaseClass(object):
    def __init__(self):
        pass

    def ExceptionThrow(self, e):
        line = e.__traceback__.tb_frame.f_globals["__file__"] + " 异常发生在(行):%d " % e.__traceback__.tb_lineno + str(e)
        print(time.strftime('%y-%m-%d %H:%M:%S') + " ExceptionThrow " + line + '-------------- \n')
