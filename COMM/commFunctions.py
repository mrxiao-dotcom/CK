import numpy as np
from datetime import datetime, timedelta
from decimal import Decimal

#### time change
def get_last_half_hour():
    # 获取当前时间
    now = datetime.now()
    minute = now.minute
    # 如果分钟在0到29之间，取上一个小时的30分钟时间点
    if 0 <= minute <= 29:
        # 计算上一个小时的30分钟时间点
        half_hour_time = now.replace(minute=30, second=0, microsecond=0) - timedelta(hours=1)
    # 如果分钟在30到59之间，取当前小时的整点时间点
    elif 30 <= minute <= 59:
        # 计算当前小时的整点时间点
        half_hour_time = now.replace(minute=0, second=0, microsecond=0)
    else:
        raise ValueError("Minute value must be between 0 and 59.")
    return half_hour_time

def get_last_half_hour_timestamp():

    half_hour_time = get_last_half_hour()
    return int(half_hour_time.timestamp())

def datetime_to_timestamp(dt):
    # 将datetime对象转换为时间戳
    timestamp = dt.timestamp()
    return int(timestamp)

def timestamp_to_datetime(timestamp):
    # 将时间戳转换为datetime对象
    dt_object = datetime.fromtimestamp(timestamp)
    return dt_object

def datetime_str_to_timestamp(datetime_str, format_str):
    # 将日期时间字符串按照给定的格式转换为datetime对象
    dt_object = datetime.strptime(datetime_str, format_str)
    # 将datetime对象转换为时间戳
    timestamp = int(dt_object.timestamp())
    return timestamp

def add_minutes(dt, minutes):
    """
    给定一个datetime对象和分钟数，返回加上指定分钟后的新datetime对象。

    :param dt: datetime对象
    :param minutes: 要加上的分钟数
    :return: 加上指定分钟后的datetime对象
    """
    new_dt = dt + timedelta(minutes=minutes)
    return new_dt

def subtract_minutes(dt, minutes):
    """
    给定一个datetime对象和分钟数，返回加上指定分钟后的新datetime对象。

    :param dt: datetime对象
    :param minutes: 要加上的分钟数
    :return: 加上指定分钟后的datetime对象
    """
    new_dt = dt - timedelta(minutes=minutes)
    return new_dt

def count_time_points(start_timestamp, end_timestamp, interval_minutes=30):
    # 将时间戳转换为datetime对象
    start_dt = datetime.fromtimestamp(start_timestamp)
    end_dt = datetime.fromtimestamp(end_timestamp)

    # 计算时间点数量
    current_dt = start_dt
    time_points = 1  # 包括开始时间点
    while current_dt < end_dt:
        current_dt += timedelta(minutes=interval_minutes)
        time_points += 1
        if current_dt >= end_dt:
            break
    return time_points

def add_minutes_to_timestamp(timestamp, minutes):
    # 将时间戳转换为datetime对象
    dt = datetime.fromtimestamp(timestamp)
    # 添加指定的分钟数
    new_dt = dt + timedelta(minutes=minutes)
    # 将新的datetime对象转换回时间戳
    new_timestamp = int(new_dt.timestamp())
    return new_timestamp


###------------------------------###
### 字符串与列表的转换

def join_list_with_comma(lst):
    """
    将列表元素合并成一个用逗号隔开的字符串。

    :param lst: 要合并的列表
    :return: 合并后的字符串
    """
    return ','.join(map(str, lst))

def join_list_with_comma_quoted(lst):
    """
    将列表元素合并成一个用逗号和单引号隔开的字符串。

    :param lst: 要合并的列表
    :return: 合并后的字符串
    """
    # 将每个元素转换为用单引号包围的字符串
    quoted_list = [f"'{item}'" for item in lst]
    # 使用逗号将转换后的字符串连接起来
    return ','.join(quoted_list)

def safe_divide(numerator, denominator):
    """
    执行除法运算，如果分母为零则抛出异常。

    :param numerator: 被除数
    :param denominator: 除数
    :return: 除法运算的结果
    """
    if denominator == 0:
        raise ZeroDivisionError("除数不能为零。")
    return numerator / denominator

###-------------------### 数据处理
def calculate_daily_profit(input_data):
    # 将输入数据转换为字典，以日期为键，盈亏列表为值
    data_by_date = {}
    for time_str,profit in input_data:
        # 将时间字符串转换为datetime对象

        date_key = time_str.strftime("%y-%m-%d")
        if date_key not in data_by_date:
            data_by_date[date_key] = []
        data_by_date[date_key].append((time_str, profit))

    # 计算每天的累计盈亏
    daily_profit = {}
    for date, records in data_by_date.items():
        daily_total = 0
        for time, profit in sorted(records):
            daily_total += profit
        daily_profit[date] = daily_total

    # 创建输出序列，包括每天的开始时间和累计盈亏
    output_data = []
    for date in sorted(daily_profit.keys()):
        start_time = datetime.strptime(date, "%y-%m-%d")
        output_data.append((start_time.strftime("%y-%m-%d"), daily_profit[date]))

    return output_data


def calculate_cumulative_profit(transactions, initial_value):
    """
    计算累计盈亏。

    :param transactions: 包含(日期, 盈亏)元组的列表
    :param initial_value: 初始累计盈亏值
    :return: 包含(日期, 累计盈亏)元组的新列表
    """
    cumulative_profit = initial_value
    result = []

    for date_str, daily_profit in transactions:

        cumulative_profit += daily_profit
        result.append((date_str, cumulative_profit))

    return result


def calculate_drawdown(current_value, peak_value):
    """
    计算回撤率
    :param current_value: 当前值
    :param peak_value: 最高值
    :return: 回撤率
    """
    if peak_value == 0:
        raise ValueError("最高值不能为0，以避免除以零的错误。")

    drawdown = (peak_value - current_value) / peak_value
    drawdown_str = "%.2f%%"%(drawdown*100)
    return drawdown,drawdown_str


def get_max_equity(equity_list):
    """
    获取权益最大值
    :param equity_list: 包含(时间, 权益)元组的列表
    :return: 权益的最大值
    """
    # 使用max函数和生成器表达式获取权益的最大值
    max_equity = max(equity for _, equity in equity_list)
    return max_equity

def get_stg_str(stg):
    stg_str = ""
    if stg == 1 or stg == 2:
        stg_str = "多"
    elif stg == -1 or stg == -2:
        stg_str = "空"
    else:
        stg_str = "无"

    return stg_str

def sum_cumulative_rights(three_d_list):
    """
    合并三维列表，计算每个日期的累计权益总和。

    :param three_d_list: 三维列表，其中每个元素是一个二维列表，二维列表的元素是日期和累计权益的一维列表
    :return: 列表，包含日期和对应累计权益总和的元组
    """
    # 使用字典来累加累计权益
    rights_sum = {}
    for two_d_list in three_d_list:
        for sub_list in two_d_list:
            date_str, rights = sub_list
            date_obj = datetime.strptime(date_str, "%y-%m-%d").date()  # 转换为日期对象
            if date_obj in rights_sum:
                rights_sum[date_obj] += rights
            else:
                rights_sum[date_obj] = rights

    # 将字典转换为列表
    merged_list = [(date, rights_sum[date]) for date in sorted(rights_sum.keys())]
    return merged_list

def calculate_performance(rights_list, principal=250000):
    # 计算历史最高权益
    max_rights = max(rights for _, rights in rights_list)
    # 计算历史最大回撤比例
    max_drawdown = (max_rights - min(rights for _, rights in rights_list)) / principal
    # 计算当前回撤比例
    current_drawdown = (max_rights - rights_list[-1][1]) / principal if rights_list[-1][1] < max_rights else 0

    return max_rights, max_drawdown, current_drawdown


def minute_to_daily(klines_30m):
    """
    将30分钟K线数据转换为日线数据
    :param klines_30m: 30分钟K线数据的列表，每个元素包含开盘、最高、最低、收盘价格和datetime类型的time时间
    :return: 日线K线数据的列表
    """
    # 确保数据按时间排序
    klines_30m.sort(key=lambda x: x['price_time'])

    daily_klines = []
    daily_open = None
    daily_high = None
    daily_low = None
    daily_close = None
    current_day = None

    for kline in klines_30m:
        # 检查是否是新的一天
        if current_day is None or kline['price_time'].date() != current_day:
            if daily_open is not None:
                # 保存前一天的数据
                daily_kline = {
                    'price_time': current_day,
                    'open': daily_open,
                    'high': daily_high,
                    'low': daily_low,
                    'close': daily_close
                }
                daily_klines.append(daily_kline)
            # 重置日线变量
            daily_open = kline['open']
            daily_high = kline['high']
            daily_low = kline['low']
            daily_close = kline['close']
            current_day = kline['price_time'].date()
        else:
            # 更新最高和最低价格
            daily_high = max(daily_high, kline['high']) if daily_high is not None else kline['high']
            daily_low = min(daily_low, kline['low']) if daily_low is not None else kline['low']
            daily_close = kline['close']

    # 添加最后一天的数据
    if daily_open is not None:
        daily_kline = {
            'price_time': current_day,
            'open': daily_open,
            'high': daily_high,
            'low': daily_low,
            'close': daily_close
        }
        daily_klines.append(daily_kline)

    return daily_klines


def check_and_convert_to_uppercase(s):
    if not s.isalpha():  # 检查字符串是否全为字母
        raise ValueError("字符串包含非字母字符")

    if not s.isupper():  # 检查字符串是否全为大写字母
        return s.upper()  # 不是大写则转换为大写
    else:
        return s  # 已经是大写则返回原字符串

def MaxDrawdown(return_list):
    '''最大回撤率'''
    '''
    return_list：是每日资金的变化曲线
    np.maximum.accumulate(return_list)：找到return_list中的累计最大值，例如：
    d = np.array([2, 0, 3, -4, -2, 7, 9])
	c = np.maximum.accumulate(d)
	#c = array([2, 2, 3, 3, 3, 7, 9])
	i：为最大回撤截止的时间
	j：为最大回撤开始的时间
	drawdown_max：最大回撤
	drawdown_rate：最大回撤对应的回撤率
	drawdown_tian：回撤持续天数
    '''
    i = np.argmax((np.maximum.accumulate(return_list) - return_list))
    if i == 0:
        return 0
    j = np.argmax(return_list[:i])  # 开始位置
    k = np.argmax(return_list) #最高点
    drawdown_max = return_list[j] - return_list[i]
    drawdown_rate = (return_list[j] - return_list[i]) / return_list[j]
    #drawdown_tian = i - j
    #drawdown_tian = len(return_list) - j
    drawdown_tian = len(return_list) - k
    drawdown_new = (return_list[k] - return_list[-1]) / return_list[k]
    #drawdown_new = (return_list[j] - return_list[-1]) / return_list[j] #当前位置，回撤幅度
    drawdown_new_rate = (len(return_list) - j) / (i - j) #现在的回撤距离最高点，相对最低回撤的比例，如果接近 1，则表示当前接近最大回撤，越大越说明离最大回撤越远
    return drawdown_rate, drawdown_max, drawdown_tian, drawdown_new,drawdown_new_rate

def remove_duplicates(input_list):
    return list(set(input_list))