import time

# 公历向农历转换程序
# 基于查表法，支持 1901-2099 年的数据
# 同时支持 micropython 和 python3
# 
# 注意：本程序中，农历年数字指的是农历年春节所在的公历年

# 1901 - 2099 年的农历数据，每年 3 byte
# bits:
# aaaabbbbbbbbbbbbbccddddd
# a: 4 bit，闰月月份，0 为无闰月
# b: 13 bit，每个表示农历月是大月还是小月，1 表示大月 30 天，0 表示小月 29 天
# c: 2 bit, 表示农历春节所在的公历月
# d: 5 bit, 表示农历春节所在的公历日期
nongli_data_raw = b"\x04\xaeS\nWHU&\xbd\r&P\r\x95DF\xaa\xb9\x05jM\t\xadB$\xae\xb6\x04\xaeJjM\xbe\nMR\r%F]R\xba\x0bTN\rjC)m7\t[Kt\x9b\xc1\x04\x97T\nKH[%\xbc\x06\xa5P\x06\xd4EJ\xda\xb8\x02\xb6M\tWB$\x97\xb7\x04\x97JfK>\rJQ\x0e\xa5FV\xd4\xba\x05\xadN\x02\xb6D978\t.K|\x96\xbf\x0c\x95S\rJHm\xa5;\x0bUO\x05jEJ\xad\xb9\x02]M\t-B,\x95\xb6\n\x95J{J\xbd\x06\xcaQ\x0bUFUZ\xbb\x04\xdaN\n[C5+\xb8\x05+L\x8a\x95?\x0e\x95R\x06\xaaHz\xd5<\n\xb5O\x04\xb6EJW9\nWM\x05&B>\x935\r\x95Iu\xaa\xbe\x05jQ\tmFT\xae\xbb\x04\xadO\nMCM&\xb7\r%K\x8dR\xbf\x0bTR\x0bjGim<\t[P\x04\x9bEJK\xb9\nKM\xab%\xc2\x06\xa5T\x06\xd4Ij\xda=\n\xb6Q\t7FT\x97\xbb\x04\x97O\x06KD6\xa57\x0e\xa5J\x86\xb2\xbf\x05\xacS\n\xb6GY6\xbc\t.P\x0c\x96EMJ\xb8\rJL\r\xa5A%\xaa\xb6\x05jIz\xad\xbd\x02]R\t-G\\\x95\xba\n\x95N\x0bJCKU7\n\xd5J\x95Z\xbf\x04\xbaS\n[He+\xbc\x05+P\n\x93EGJ\xb9\x06\xaaL\n\xd5A$\xda\xb6\x04\xb6JiW=\nNQ\r&F^\x93:\rSM\x05\xaaC6\xb57\tmK\xb4\xae\xbf\x04\xadS\nMHm%\xbc\r%O\rRD]\xaa8\x0bZL\x05mA$\xad\xb6\x04\x9bJzK\xbe\nKQ\n\xa5F[R\xba\x06\xd2N\n\xdaB5[7\t7K\x84\x97\xc1\x04\x97S\x06KHf\xa5<\x0e\xa5O\x06\xb2DJ\xb68\n\xaeL\t.B<\x975\x0c\x96I}J\xbd\rJQ\r\xa5EU\xaa\xba\x05jN\nmCE.\xb7\x05-K\x8a\x95\xbf\n\x95S\x0bJGkU;\n\xd5O\x05ZEJ]8\n[L\x05+B:\x93\xb6\x06\x93Iw)\xbd\x06\xaaQ\n\xd5FT\xda\xba\x04\xb6N\nWCE'8\r&J\x8e\x93>\rRR\r\xaaGf\xb5;\x05mO\x04\xaeEJN\xb9\nML\r\x15A-\x92\xb5"
nongli_data = memoryview(nongli_data_raw)

month_total_days = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365)

nongli_month_strs = ('正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月')
nongli_day_strsL = '一二三四五六七八九' # day % 10 - 1
nongli_day_strsH = '初十廿' # day // 10
nongli_day_strs_ten = ('初十', '二十', '三十') # day % 10 == 0; day // 10 - 1

tiangan_str = '甲乙丙丁戊己庚辛壬癸'
dizhi_str = '子丑寅卯辰巳午未申酉戌亥'
shengxiao_str = '鼠牛虎兔龙蛇马羊猴鸡狗猪'

# 从数据表中提取信息
# 输入 year 为公历年
# 返回闰月月份，大小月信息，当年春节到元旦天数
def get_nongli_year_info(year):
    if year < 1901 or year > 2099:
        raise ValueError('year out of range')
    table_addr = (year - 1901) * 3
    data = int.from_bytes(nongli_data[table_addr:table_addr + 3], 'big')
    sprf_date = (data & 0x1f) - 1 # 春节到元旦的天数
    if (data & 0x60) >> 5 != 1:
        sprf_date += 31 # 二月春节
    leap_month = data >> 20 # 闰月
    mon_days = (data >> 7) & 0x1fff # 大小月
    return leap_month, mon_days, sprf_date # 闰月，大小月，春节到元旦天数

# 判断公历年是否为闰年
def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or year % 400 == 0

# 返回农历年干支纪年法字符串和生肖
# 输入 year 为农历年数字
def get_year_str(year):
    tg = (year - 3) % 10 - 1
    dz = (year - 3) % 12 - 1
    return tiangan_str[tg] + dizhi_str[dz], shengxiao_str[dz]

# 返回农历月的中文表示
# 输入 month 为农历月，is_leap_month 为是否为闰月
def get_month_str(month, is_leap_month):
    month_str = nongli_month_strs[month - 1]
    if is_leap_month:
        month_str = '闰' + month_str
    return month_str

# 返回农历日的中文表示
# 输入 day 为农历日
def get_day_str(day):
    if day % 10 == 0:
        return nongli_day_strs_ten[day // 10 - 1]
    else:
        return nongli_day_strsH[day // 10] + nongli_day_strsL[day % 10 - 1]

# 从公历日期得到农历
# 输入：
# year: 公历年
# month: 公历月
# day: 公历日
# 返回值：
# 农历年数字，农历月数字，是否为闰月，农历日
def from_date(year, month, day):
    leap_month, mon_days, sprf_date = get_nongli_year_info(year)
    cur_date = month_total_days[month - 1] + day - 1 # 日期到当年元旦的天数
    if is_leap_year(year) and month > 2:
        # 闰年
        cur_date += 1
    if (cur_date >= sprf_date):
        # 当前日期在农历春节之后
        cur_date -= sprf_date # 日期到当年春节的天数
        m_idx = 1 # 当前农历月 id
        days_cur_month = 29 + ((mon_days >> (13 - m_idx)) & 1) # 当前农历月天数
        while cur_date >= days_cur_month:
            m_idx += 1
            cur_date -= days_cur_month # 日期到当前月一日的天数
            days_cur_month = 29 + ((mon_days >> (13 - m_idx)) & 1) # 当前农历月天数
        cur_date += 1 # 农历日
    else:
        # 当前日期在农历春节之前，使用上一年的闰月和大小月数据
        year -= 1
        leap_month, mon_days, _ = get_nongli_year_info(year)
        cur_date = sprf_date - cur_date # 日期到当年春节的天数
        if leap_month == 0:
            m_idx = 12
        else:
            m_idx = 13
        days_cur_month = 29 + ((mon_days >> (13 - m_idx)) & 1) # 当前农历月天数
        while cur_date > days_cur_month:
            m_idx -= 1
            cur_date -= days_cur_month # 日期到当前月月末的天数
            days_cur_month = 29 + ((mon_days >> (13 - m_idx)) & 1) # 当前农历月天数
        cur_date = days_cur_month - cur_date + 1

    is_leap_month = False
    if leap_month != 0 and m_idx > leap_month:
        if m_idx == leap_month + 1:
            is_leap_month = True
        m_idx -= 1
    return year, m_idx, is_leap_month, cur_date # 农历年，月，是否闰月，日

# 从 unix 时间戳到农历
# 输入：
# timestamp: unix 时间戳
# 返回值：
# 农历年数字，农历月数字，是否为闰月，农历日
def from_timestamp(timestamp):
    t = time.localtime(timestamp)
    return from_date(t[0], t[1], t[2])

# 当前的农历
# 输入：
# timestamp: unix 时间戳
# 返回值：
# 农历年数字，农历月数字，是否为闰月，农历日
def today():
    t = time.localtime()
    return from_date(t[0], t[1], t[2])
