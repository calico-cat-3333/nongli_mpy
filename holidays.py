import time
import nongli

# 简单的节日判定
# 直接遍历节日表，没什么技术含量
# 简单添加了几个比较常见，名字也比较短的节日当作示例，实际使用时应根据需要自行增删

# 公历月长度
def _month_length(y, m):
    if m <= 7:
        if m == 2:
            return 28 + int(nongli.is_leap_year(y))
        return 30 + (m % 2)
    return 30 + ((m + 1) % 2)

# 处理发生在几月的第几个星期几的节日
# 参数：公历年，公历月，该月的第几周(-4～4，负数表示倒数第几个，正数表示第几个，0 无效)，该月的周几(0-6 表示周一到周日)
# 返回值：公历年，公历月，公历日
def _nth_weekday_of_month(year, month, weeknum, weekday):
    if weeknum < -4 or weeknum > 4 or weeknum == 0:
        raise ValueError('weeknum invalid')
    if weeknum > 0:
        date = 1
        day1_of_month = time.localtime(time.mktime((year, month, 1, 1, 0, 0, 0, 0, -1)))
        day1_weekday = day1_of_month[6]
        date += (weekday - day1_weekday) % 7
        date += 7 * (weeknum - 1)
    else:
        date = _month_length(year, month)
        lastday_of_month = time.localtime(time.mktime((year, month, date, 1, 0, 0, 0, 0, -1)))
        lastday_weekday = lastday_of_month[6]
        date -= (lastday_weekday - weekday) % 7
        date -= 7 * ((-weeknum) - 1)
    return year, month, date

# 有确定日期的公历节日，格式：(公历月, 公历日, 节日名)
gregorian_holidays = (
    (1, 1, '元旦'),
    (2, 14, '情人节'),
    (3, 8, '妇女节'),
    (3, 12, '植树节'),
    (4, 1, '愚人节'),
    (5, 1, '劳动节'),
    (5, 4, '青年节'),
    (6, 1, '儿童节'),
    (7, 1, '建党节'),
    (8, 1, '建军节'),
    (9, 10, '教师节'),
    (10, 1, '国庆节'),
    (11, 1, '万圣节'),
    (12, 24, '平安夜'),
    (12, 25, '圣诞节'),
)

# 有确定农历日期的农历节日，格式：(农历月, 农历日, 节日名)
nongli_holidays = (
    (1, 1, '春节'),
    (1, 15, '元宵节'),
    (2, 2, '龙抬头'),
    (5, 5, '端午节'),
    (7, 7, '七夕节'),
    (7, 15, '中元节'),
    (8, 15, '中秋节'),
    (9, 9, '重阳节'),
    (10, 1, '寒衣节'),
    (12, 23, '北方小年'),
    (12, 24, '南方小年'),
    (12, 8, '腊八节'),
)

# 其他需要特殊判定规则的节日，格式：(判定函数, 节日名)
# 判定函数是一个函数对象，接受一个元组作为参数
# 元组为：(0公历年，1公历月，2公历日，3农历年，4农历月，5农历月长度，6是否闰月，7农历日)
# 如果当天是这个节日则返回 True 否则返回 False
special_holidays = (
    (lambda dt: (dt[4] == 12 and dt[5] == dt[7] and not dt[6]), '除夕'), # 农历腊月最后一天，而且不是闰腊月的最后一天（实际上闰腊月极其罕见，1900-2099 年间也没有闰腊月）
    (lambda dt: (nongli.get_jieqi(dt[0], dt[1], dt[2]) == 4), '清明节'),
    (lambda dt: (dt[:3] == _nth_weekday_of_month(dt[0], 5, 2, 6)), '母亲节'), # 五月的第二个周日
    (lambda dt: (dt[:3] == _nth_weekday_of_month(dt[0], 6, 3, 6)), '父亲节'), # 六月的第三个周日
    (lambda dt: (dt[:3] == _nth_weekday_of_month(dt[0], 11, -1, 3)), '感恩节'), # 十一月的最后一个周四
)


def is_holiday(year, month, day):
    ret = []
    for holi in gregorian_holidays:
        if month == holi[0] and day == holi[1]:
            ret.append(holi[2])

    nlyear, nlmonth, nlmonth_len, isleap, nlday = nongli.from_date(year, month, day)
    for holi in nongli_holidays:
        if nlmonth == holi[0] and nlday == holi[1] and not isleap: # 闰月不过节
            ret.append(holi[2])

    for holi in special_holidays:
        if holi[0]((year, month, day, nlyear, nlmonth, nlmonth_len, isleap, nlday)):
            ret.append(holi[1])

    return ret
