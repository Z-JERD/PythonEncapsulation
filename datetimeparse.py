import re
import datetime
import calendar


class TimeInterval(object):
    """获取当前日期前后N天或N月的日期"""

    def __init__(self, show_date=None):
        """转换为字符串格式"""
        if not show_date:
            show_date = datetime.datetime.now()

        if isinstance(show_date, str):
            try:
                show_date = datetime.datetime.strptime(show_date, "%Y-%m-%d")
            except Exception as e:
                raise ValueError("日期有误")

        assert isinstance(show_date, datetime.datetime), "日期有误"

        self.show_date = show_date
        self.year = show_date.strftime('%Y')
        self.month = show_date.strftime('%m')
        self.day = show_date.strftime('%d')
        self.hour = show_date.strftime('%H')
        self.min = show_date.strftime('%M')
        self.sec = show_date.strftime('%S')

    @staticmethod
    def get_days_of_month(year, month):
        '''
        get days of month
        calender.monthrange()计算每个月的天数,返回一个元祖(0,31),此为2018年1月,
        第一个参数代表当月第一天是星期几,第二个参数代表是这个月的天数
        '''

        return calendar.monthrange(year, month)[1]

    @staticmethod
    def addzero(n):
        '''
            用0左补齐成两位数
            add 0 before 0-9  return 01-09
        '''
        nabs = abs(int(n))
        if nabs < 10:
            return "0" + str(nabs)
        else:
            return nabs

    def get_year_and_month(self, n=0):
        '''
            get the year,month,days from today
            befor or after n months
        '''
        thisyear, thismon = int(self.year), int(self.month)
        totalmon = thismon + n

        if n >= 0:
            if totalmon <= 12:
                # 计算totalmon月的总天数
                days = str(self.get_days_of_month(thisyear, totalmon))
                # 月份用0左补齐成两位数
                totalmon = self.addzero(totalmon)
                return self.year, totalmon, days
            else:
                # //取整除,返回商的整数部分,也就是一年
                i = totalmon // 12
                # %取模:返回除法的余数
                j = totalmon % 12
                if j == 0:
                    i -= 1
                    j = 12
                thisyear += i
                days = str(self.get_days_of_month(thisyear, j))
                j = self.addzero(j)
                return str(thisyear), str(j), days
        else:
            if totalmon > 0 and totalmon < 12:
                days = str(self.get_days_of_month(thisyear, totalmon))
                totalmon = self.addzero(totalmon)
                return self.year, totalmon, days
            else:
                i = totalmon // 12
                j = totalmon % 12
                if j == 0:
                    i -= 1
                    j = 12
                thisyear += i
                days = str(self.get_days_of_month(thisyear, j))
                j = self.addzero(j)
                return str(thisyear), str(j), days

    def get_today_month(self, n=0):
        '''
        获取当前日期前后N月的日期
        if n > 0 获取当前日期前N月的日期
        if n < 0 获取当前日期后N月的日期
        date format = "YYYY-MM-DD"
        '''
        (y, m, d) = self.get_year_and_month(n)
        arr = (y, m, d)

        if int(self.day) < int(d):
            arr = (y, m, self.day)

        return "-".join("%s" % i for i in arr)

    def get_day_of_day(self, n=0):
        """计算N天之前/之后的日期"""
        if n < 0:
            n = abs(n)
            return self.show_date.date() - datetime.timedelta(days=n)
        else:
            return self.show_date.date() + datetime.timedelta(days=n)


class ParseDate(object):
    """解析日期时间"""

    @staticmethod
    def check_month(show_date):
        """年月转换成datetime类型"""
        dt = None
        if re.match(r"\d{4}-\d{1,2}$", show_date):
            dt = datetime.datetime.strptime(show_date, '%Y-%m')
        elif re.match(r"\d{4}/\d{1,2}$", show_date):
            dt = datetime.datetime.strptime(show_date, '%Y/%m')
        elif re.match(r"\d{4}/\d{1,2}/$", show_date):
            dt = datetime.datetime.strptime(show_date, '%Y/%m/')
        elif re.match(r"\d{4}年\d{1,2}$", show_date):
            dt = datetime.datetime.strptime(show_date, '%Y年%m')
        elif re.match(r"\d{4}年\d{1,2}月$", show_date):
            dt = datetime.datetime.strptime(show_date, '%Y年%m月')

        return dt

    @staticmethod
    def check_date(show_date):
        """年月日转换成datetime类型"""
        dt = None

        if show_date.isdigit():
            if len(show_date) == 8:
                dt = datetime.datetime.strptime(show_date, '%Y%m%d').date()
            else:
                settle_date = int(show_date)
                dt = datetime.date(1900, 1, 1) + datetime.timedelta(settle_date - 2)
        elif re.match(r"\d{4}-\d{1,2}-\d{1,2}$", show_date):
            dt = datetime.datetime.strptime(show_date, "%Y-%m-%d")
        elif re.match(r"\d{4}/\d{1,2}/\d{1,2}$", show_date):
            dt = datetime.datetime.strptime(show_date, "%Y/%m/%d")
        elif re.match(r"\d{4}/\d{1,2}/\d{1,2}/$", show_date):
            dt = datetime.datetime.strptime(show_date, "%Y/%m/%d/")
        elif re.match(r"\d{4}.\d{1,2}.\d{1,2}$", show_date):
            dt = datetime.datetime.strptime(show_date, "%Y.%m.%d")
        elif re.match(r"\d{4}年\d{1,2}月\d{1,2}日$", show_date):
            dt = datetime.datetime.strptime(show_date, "%Y年%m月%d日")

        return dt

    @staticmethod
    def check_datetime(show_date):
        """年月日时分秒转成datetime类型"""
        dt = None
        if re.match(r'\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y-%m-%d %H:%M:%S')
        elif re.match(r'\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y/%m/%d %H:%M:%S')
        elif re.match(r'\d{4}/\d{1,2}/\d{1,2}/\s+\d{1,2}:\d{1,2}:\d{1,2}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y/%m/%d/ %H:%M:%S')
        elif re.match(r'\d{4}.\d{1,2}.\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y.%m.%d %H:%M:%S')
        elif re.match(r'\d{4}年\d{1,2}月\d{1,2}日\s+\d{1,2}:\d{1,2}:\d{1,2}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y年%m月%d日 %H:%M:%S')
        elif re.match(r'\d{4}-\d{1,2}-\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y-%m-%d %H:%M:%S.%f')
        elif re.match(r'\d{4}/\d{1,2}/\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y/%m/%d %H:%M:%S.%f')
        elif re.match(r'\d{4}/\d{1,2}/\d{1,2}/\s+\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y/%m/%d/ %H:%M:%S.%f')
        elif re.match(r'\d{4}.\d{1,2}.\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y.%m.%d %H:%M:%S.%f')
        elif re.match(r'\d{4}年\d{1,2}月\d{1,2}日\s+\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y年%m月%d日 %H:%M:%S.%f')
        elif re.match(r'\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y-%m-%dT%H:%M:%S')
        elif re.match(r'\d{4}/\d{1,2}/\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y/%m/%dT%H:%M:%S')
        elif re.match(r'\d{4}/\d{1,2}/\d{1,2}/T\d{1,2}:\d{1,2}:\d{1,2}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y/%m/%d/T%H:%M:%S')
        elif re.match(r'\d{4}.\d{1,2}.\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y.%m.%dT%H:%M:%S')
        elif re.match(r'\d{4}年\d{1,2}月\d{1,2}日T\d{1,2}:\d{1,2}:\d{1,2}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y年%m月%d日T%H:%M:%S')
        elif re.match(r'\d{4}-\d{1,2}-\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y-%m-%dT%H:%M:%S.%f')
        elif re.match(r'\d{4}/\d{1,2}/\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y/%m/%dT%H:%M:%S.%f')
        elif re.match(r'\d{4}/\d{1,2}/\d{1,2}/T\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y/%m/%d/T%H:%M:%S.%f')
        elif re.match(r'\d{4}.\d{1,2}.\d{1,2}T\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y.%m.%dT%H:%M:%S.%f')
        elif re.match(r'\d{4}年\d{1,2}月\d{1,2}日T\d{1,2}:\d{1,2}:\d{1,2}.\d{1,6}$', show_date):
            dt = datetime.datetime.strptime(show_date, '%Y年%m月%d日T%H:%M:%S.%f')

        return dt

    @classmethod
    def str_to_month(cls, show_date, ast=True):
        assert isinstance(show_date, str), '日期类型有误'

        try:
            dt = cls.check_month(show_date)
        except Exception as e:
            assert False, '日期有误'
        if ast:
            assert dt, '日期有误'

        return dt

    @classmethod
    def str_to_date(cls, show_date, ast=True):
        assert isinstance(show_date, str), '日期类型有误'
        try:
            dt = cls.check_date(show_date)
        except Exception as e:
            assert False, '日期有误'
        if ast:
            assert dt, '日期有误'

        return dt

    @classmethod
    def str_to_datetime(cls, show_date, ast=True):
        assert isinstance(show_date, str), '日期类型有误'
        try:
            dt = cls.check_datetime(show_date)
        except Exception as e:
            assert False, '日期有误'
        if ast:
            assert dt, '日期有误'

        return dt

    @classmethod
    def str_to_showdate(cls, show_date):
        assert isinstance(show_date, str), '日期类型有误'
        dt = cls.str_to_datetime(show_date, False)
        dt = dt if dt else cls.str_to_date(show_date, False)
        dt = dt if dt else cls.str_to_month(show_date, False)

        assert dt, '日期有误'

    @classmethod
    def get_days_of_month(cls, show_date):
        """获取某年某月的天数"""

        assert isinstance(show_date, datetime.date), '日期类型有误'
        year, month = show_date.year, show_date.month

        if month in (1, 3, 5, 7, 8, 10, 12):
            return 31
        elif month in (4, 6, 9, 11):
            return 30
        elif month == 2 and ((year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)):
            return 29
        else:
            return 28

    @classmethod
    def get_date_of_days(cls,  n=0, show_date=None):
        """"计算N天之前/之后的日期"""

        expected_date = TimeInterval(show_date).get_day_of_day(n)

        return expected_date

    @classmethod
    def get_date_of_month(cls, n=0, show_date=None):
        """获取当前日期前后N月的日期"""

        expected_date = TimeInterval(show_date).get_today_month(n)

        return expected_date

    @classmethod
    def get_last_month(cls, show_date=None):
        """
        得到上个月的月份
        :return: <string>
        """
        if not show_date:
            show_date = datetime.date.today()

        if isinstance(show_date, str):
            try:
                show_date = datetime.datetime.strptime(show_date, "%Y-%m-%d").date()
            except Exception as e:
                raise ValueError("日期有误")

        assert isinstance(show_date, datetime.date), "日期有误"

        first_day = show_date.replace(day=1)
        month_last_day = first_day - datetime.timedelta(days=1)

        return month_last_day.strftime('%Y-%m')

    @classmethod
    def get_next_month(cls, show_date=None):
        """
        得到下个月的月份
        :return: <string>
        """
        if not show_date:
            show_date = datetime.date.today()

        if isinstance(show_date, str):
            try:
                show_date = datetime.datetime.strptime(show_date, "%Y-%m-%d").date()
            except Exception as e:
                raise ValueError("日期有误")

        assert isinstance(show_date, datetime.date), "日期有误"

        month_days = cls.get_days_of_month(show_date)

        last_day = show_date.replace(day=month_days)
        month_next_day = last_day + datetime.timedelta(days=1)

        return month_next_day.strftime('%Y-%m')

    @classmethod
    def date_list_generator(cls, start, end):
        """
        得到两个日期之间的所有日期
        :param start: <datetime>
        :param end: <datetime>
        :return: <list>
        """

        if isinstance(start, str):
            try:
                start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
            except Exception as e:
                raise ValueError("开始日期有误")

        if isinstance(end, str):
            try:
                end = datetime.datetime.strptime(end, "%Y-%m-%d").date()
            except Exception as e:
                raise ValueError("结束日期有误")

        assert isinstance(start, datetime.date), "开始日期类型有误"
        assert isinstance(end, datetime.date), "结束日期类型有误"

        (s, e) = (start, end) if start < end else (end, start)

        date_list = [str(s)]

        while s < e:
            s = s + datetime.timedelta(days=1)
            date_list.append(str(s))

        return date_list

    @classmethod
    def month_list_generate(cls, start, end, date_day=False):
        """
        得到两个日期之间的所有月份
        :param start:
        :param end:
        :param date_day:
        :return:
        """

        if isinstance(start, str):
            try:
                start = datetime.datetime.strptime(start, "%Y-%m-%d").date()
            except Exception as e:
                raise ValueError("开始日期有误")

        if isinstance(end, str):
            try:
                end = datetime.datetime.strptime(end, "%Y-%m-%d").date()
            except Exception as e:
                raise ValueError("结束日期有误")

        assert isinstance(start, datetime.date), "开始日期类型有误"
        assert isinstance(end, datetime.date), "结束日期类型有误"

        if start > end:
           start, end = end, start

        months = abs((start.year - end.year) * 12 + start.month - end.month)

        if date_day:
            month_range = ['%s-%02d-01' % (start.year + mon // 12, mon % 12 + 1)
                           for mon in range(start.month, start.month + months)]

        else:
            month_range = ['%s-%02d' % (start.year + mon // 12, mon % 12 + 1)
                           for mon in range(start.month, start.month + months)]

        return month_range

    @classmethod
    def month_list_year(cls, show_date=None, date_day=False):
        """
        获取一年前的所有月份
        """
        if not show_date:
            show_date = datetime.datetime.now().date()
        elif isinstance(show_date, str):
            try:
                show_date = datetime.datetime.strptime(show_date, "%Y-%m-%d").date()
            except Exception as e:
                raise ValueError("日期有误")

        assert isinstance(show_date, datetime.date), "结束日期类型有误"

        current_year, current_month = show_date.year, show_date.month

        if current_month == 12:
            start_date = "%s-01" % current_year
        else:
            start_date = '%s-%s' % ((current_year - 1), (current_month + 1))

        start_datetime = datetime.datetime.strptime(start_date, '%Y-%m')

        if date_day:
            month_range = [
                '%s-%s-01' % (start_datetime.year + mon // 12, str(mon % 12 + 1).zfill(2))
                for mon in range(start_datetime.month - 1, start_datetime.month + 11)
            ]
        else:
            month_range = [
                '%s-%s' % (start_datetime.year + mon // 12, str(mon % 12 + 1).zfill(2))
                for mon in range(start_datetime.month - 1, start_datetime.month + 11)
            ]

        return month_range

    @classmethod
    def date_to_datetime(cls, date_time, trans=False):
        """
        日期转时间
        :param date_time:
        :param trans:时间转为23:59:59
        :return:
        """
        if isinstance(date_time, str):
            try:
                date_time = datetime.datetime.strptime(date_time, "%Y-%m-%d").date()
            except Exception as e:
                raise ValueError("日期有误")

        assert isinstance(date_time, datetime.date), '日期有误'

        if not trans:
            date_time = datetime.datetime(date_time.year, date_time.month, date_time.day, 0, 0, 0)
        else:
            date_time = datetime.datetime(date_time.year, date_time.month, date_time.day, 23, 59, 59)

        return date_time


if __name__ == "__main__":
    # time_obj = TimeInterval("2019-01-11")
    # print('11 days after today is:', time_obj.get_day_of_day(11))
    # print('11 days before today is:', time_obj.get_day_of_day(-11))
    # print('10 months after today is:', time_obj.get_today_month(10))
    # print('5 months before today is:', time_obj.get_today_month(-5))

    print(ParseDate.month_list_year())
