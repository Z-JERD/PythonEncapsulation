import re
import datetime
import calendar


class TimeInterval(object):
    
   """获取当前日期前后N天或N月的日期"""

    def __init__(self, show_date=None):
        """转换为字符串格式"""
        if not show_date:
            show_date = datetime.datetime.now()
        else:
            try:
                show_date = datetime.datetime.strptime(show_date, "%Y-%m-%d")
            except Exception as e:
                raise ValueError("日期有误")
        
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

        if re.match(r"\d{4}-\d{1,2}-\d{1,2}$", show_date):
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
    def str_to_month(cls,  show_date, ast=True):
        try:
            dt = cls.check_month(show_date)
        except Exception as e:
            assert False, '日期有误'
        if ast:
            assert dt, '日期有误'

        return dt

    @classmethod
    def str_to_date(cls, show_date, ast=True):
        try:
            dt = cls.check_date(show_date)
        except Exception as e:
            assert False, '日期有误'
        if ast:
            assert dt, '日期有误'

        return dt

    @classmethod
    def str_to_datetime(cls, show_date, ast=True):
        try:
            dt = cls.check_datetime(show_date)
        except Exception as e:
            assert False, '日期有误'
        if ast:
            assert dt, '日期有误'

        return dt

    @classmethod
    def str_to_showdate(cls, show_date):
        dt = cls.str_to_datetime(show_date, False)
        dt = dt if dt else cls.str_to_date(show_date, False)
        dt = dt if dt else cls.str_to_month(show_date, False)

        assert dt, '日期有误'




if __name__ == "__main__":
    
	time_obj = TimeInterval("2019-01-11")
    
	print('11 days after today is:', time_obj.get_day_of_day(11))
    print('11 days before today is:', time_obj.get_day_of_day(-11))
    print('10 months after today is:', time_obj.get_today_month(10))
    print('5 months before today is:', time_obj.get_today_month(-5))

