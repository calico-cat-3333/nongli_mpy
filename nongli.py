import time
import struct

# 公历向农历转换程序
# 基于查表法，支持 1901-2099 年的数据，数据来自著名的 nongli.c 算法有小修改
# 同时支持 micropython 和 python3
# 
# 注意：本程序中，农历年数字指的是农历年春节所在的公历年

# 农历数据及计算算法参考：
# https://github.com/lvgl/lvgl/blob/master/src/widgets/calendar/lv_calendar_chinese.c
# https://github.com/ywf-147/IIC-OLED/blob/master/nongli.c

# 农历数据，每年 3 byte
# bits:
# aaaabbbbbbbbbbbbbccddddd
# a: 4 bit，闰月月份，0 为无闰月
# b: 13 bit，每个表示农历月是大月还是小月，1 表示大月 30 天，0 表示小月 29 天
# c: 2 bit, 表示农历春节所在的公历月
# d: 5 bit, 表示农历春节所在的公历日期
nongli_data_raw = b"\x04\xaeS\nWHU&\xbd\r&P\r\x95DF\xaa\xb9\x05jM\t\xadB$\xae\xb6\x04\xaeJjM\xbe\nMR\r%F]R\xba\x0bTN\rjC)m7\t[Kt\x9b\xc1\x04\x97T\nKH[%\xbc\x06\xa5P\x06\xd4EJ\xda\xb8\x02\xb6M\tWB$\x97\xb7\x04\x97JfK>\rJQ\x0e\xa5FV\xd4\xba\x05\xadN\x02\xb6D978\t.K|\x96\xbf\x0c\x95S\rJHm\xa5;\x0bUO\x05jEJ\xad\xb9\x02]M\t-B,\x95\xb6\n\x95J{J\xbd\x06\xcaQ\x0bUFUZ\xbb\x04\xdaN\n[C5+\xb8\x05+L\x8a\x95?\x0e\x95R\x06\xaaHj\xd5<\n\xb5O\x04\xb6EJW9\nWM\x05&B>\x935\r\x95Iu\xaa\xbe\x05jQ\tmFT\xae\xbb\x04\xadO\nMCM&\xb7\r%K\x8dR\xbf\x0bTR\x0bjGim<\t[P\x04\x9bEJK\xb9\nKM\xab%\xc2\x06\xa5T\x06\xd4Ij\xda=\n\xb6Q\tWFT\x97\xbb\x04\x97O\x06KD6\xa57\x0e\xa5J\x86\xb2\xbf\x05\xacS\n\xb6GY6\xbc\t.P\x0c\x96EMJ\xb8\rJL\r\xa5A%\xaa\xb6\x05jIz\xad\xbd\x02]R\t-G\\\x95\xba\n\x95N\x0bJCKU7\n\xd5J\x95Z\xbf\x04\xbaS\n[He+\xbc\x05+P\n\x93EGJ\xb9\x06\xaaL\n\xd5A$\xda\xb6\x04\xb6JjW=\nNQ\r&F^\x93:\rSM\x05\xaaC6\xb57\tmK\xb4\xae\xbf\x04\xadS\nMHm%\xbc\r%O\rRD]\xaa8\x0bZL\x05mA$\xad\xb6\x04\x9bJzK\xbe\nKQ\n\xa5F[R\xba\x06\xd2N\n\xdaB5[7\t7K\x84\x97\xc1\x04\x97S\x06KHf\xa5<\x0e\xa5O\x06\xaaDJ\xb68\n\xaeL\t.B<\x975\x0c\x96I}J\xbd\rJQ\r\xa5EU\xaa\xba\x05jN\nmCE.\xb7\x05-K\x8a\x95\xbf\n\x95S\x0bJGkU;\n\xd5O\x05ZEJ]8\n[L\x05+B:\x93\xb6\x06\x93Iw)\xbd\x06\xaaQ\n\xd5FT\xda\xba\x04\xb6N\nWCE'8\r\x16J\x8e\x93>\rRR\r\xaaGf\xb5;\x05mO\x04\xaeEJN\xb9\n-L\r\x15A-\x92\xb5"
nongli_data = memoryview(nongli_data_raw)
# 农历数据对应的公历年范围
nongli_data_range = (1901, 2099)

month_total_days = (0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334, 365)

# 节气分段偏移量表，每段 8 Byte
# 其中前 2 Byte 这一段适用的最大年份
# 后 6 Byte 是本分段偏移量数据，偏移量数据为每节气 2 bit 按照高 bit 到低 bit 的顺序记录从 12 月（冬至）到 1 月（小寒）的节气偏移量
jieqi_offset_raw = b'\x07\x97UVefZV\x07\xbfUUUUEU\x07\xe3\x15QQQ\x05\x05\x08\x0b\x01A\x10\x11\x05\x01\x083\x00\x00\x00\x00\x00\x00'
jieqi_offset = memoryview(jieqi_offset_raw)

# 每年的节气偏移量表，每年 3 Byte
# 每个节气 1 bit 按照从高 bit 到低 bit 的顺序存储从从 12 月（冬至）到 1 月（小寒）的节气偏移量数据
jieqi_year_offset_raw = b'~\x9a\x82\xfe\xbe\xc6\xff\xff\xfe<\x08\x0f~\x9a\x82\xfe\xba\xc6\xff\xff\xfe<\x08\x0f~\x9a\x82\xfe\xba\xc6\xff\xff\xfe<\x08\x0f~\x9a\x80\xfe\xba\x82\xff\xbe\xee\x18\x08\x0e<\x98\x80~\xba\x82\xff\xbe\xee\x18\x08\x0e<\x98\x00~\xba\x82\xff\xbe\xc6\x18\x08\x0e<\x98\x00~\x9a\x82\xfe\xbe\xc6\x00\x00\x0e<\x08\x00~\x9a\x82\xfe\xbe\xc6\x00\x00\x0e<\x08\x00~\x9a\x82\xfe\xba\xc6\x00\x00\x0e<\x08\x00~\x9a\x82\xfe\xba\xc6\x00\x00\x0e<\x08\x00~\x9a\x82\xfe\xba\xc6\x01D\x7f\x19Mq}\xdf\xf1\xff\xff\xf3\x01\x04o\x19Mp}\xddq\xff\xff\xf3\x01\x04o\x19Mp=\xddq\x7f\xdf\xf3\x01\x04O\x19Mp=Mq\x7f\xdf\xf3\x00\x04G\x01Ep=Mq\x7f\xdf\xf3\x00\x04G\x01Ep=Mq\x7f\xdf\xf3\x00\x00G\x01Ep=Mq\x7f\xdf\xf3\x00\x00G\x01Dp=Mq}\xdf\xf3\x00\x00\x07\x01\x04p9Mq}\xdd\xf3\x00\x00\x07\x01\x04p\x19Mq}\xddq\x82\x02\x8f\x83&\xec\x9bo\xfc\xbf\xef\xfd\x02\x02\x8f\x82&\xcc\x9bg\xfc\xbfo\xfd\x02\x02\x8f\x82&\xc4\x83g\xfc\xbfo\xfd\x02\x02\x8f\x82"\xc4\x83g\xfc\xbfo\xfd\x02\x02\x8f\x82"\xc4\x83g\xfc\xbfo\xfd\x02\x02\x8f\x82"\xc4\x83&\xfc\xbfo\xfd\x00\x02\x8f\x82"\x84\x83&\xfc\xbbo\xfd\x00\x00\x8f\x82\x02\x84\x83&\xfc\x9bo\xfd\x00\x00\r\x82\x02\x80\x83&\xec\x9bg\xfcd\x08\x0ff\x9a\x82\xe6\xbe\xce\xff\xff\xfe$\x08\x0ff\x9a\x82\xe6\xba\xc6\xe7\xff\xfe$\x08\x0ff\x9a\x82\xe6\xba\xc6\xe7\xff\xfe$\x08\x0ff\x9a\x82\xe6\xba\xc6\xe7\xbe\xfe$\x08\x0ff\x9a\x82\xe6\xba\xc6\xe7\xbe\xfe$\x08\x0fd\x98\x82\xe6\xba\x86\xe7\xbe\xfe \x08\x0fd\x98\x02\xe6\x9a\x86\xe7\xbe\xfe\x00\x00\x0fd\x08\x00\xe6\x9a\x82\xe6\xbe\xce\x00\x00\x0ed\x08\x00\xe6\x9a\x82\xe6\xba\xce\x00\x00\x0e$\x08\x00f\x9a\x82\xe6\xba\xce\x01E?=M1\x7f\xdf\xb3\xff\xff\xf7\x01E?=M1\x7f\xdf\xb3\xff\xff\xf7\x01\x04?=M1}\xdd\xb3\xff\xff\xf7\x01\x04?9M1}\xdd\xb3\xff\xdf\xb7\x01\x04?9M1}\xcd3\xff\xdf\xb7\x01\x04?\x19E1}M3\xff\xdf\xb3\x00\x04\x0f\x19E0}M1\xff\xdf\xb3\x00\x00\x0f\x19E0=M1\x7f\xdf\xb3\x00\x00\x0f\x01E0=M1\x7f\xdf\xb3\x00\x00\x07\x01\x050=M1\x7f\xdf\xb3'
jieqi_year_offset = memoryview(jieqi_year_offset_raw)

# 节气基础日期，12 Byte
# 每个字节为一个公历月，每个字节的高 3 bit 为改月的第一个节气的基础日期，低 5 bit 为该月的第二个节气的基础日期
# 按照从高字节到低字节顺序存储 1 月到 12 月的数据
jieqi_date_base = b'\x93r\x93\x93\x94\x94\xd6\xd6\xd6\xf6\xd5\xd5'

nongli_month_strs = ('正月', '二月', '三月', '四月', '五月', '六月', '七月', '八月', '九月', '十月', '十一月', '十二月')
nongli_day_strsL = '一二三四五六七八九' # day % 10 - 1
nongli_day_strsH = '初十廿' # day // 10
nongli_day_strs_ten = ('初十', '二十', '三十') # day % 10 == 0; day // 10 - 1

tiangan_str = '甲乙丙丁戊己庚辛壬癸'
dizhi_str = '子丑寅卯辰巳午未申酉戌亥'
shengxiao_str = '鼠牛虎兔龙蛇马羊猴鸡狗猪'

jieqi_strs = ('立春', '雨水', '惊蛰', '春分', '清明', '谷雨', '立夏', '小满', '芒种', '夏至', '小暑', '大暑', '立秋', '处暑', '白露', '秋分', '寒露', '霜降', '立冬', '小雪', '大雪', '冬至', '小寒', '大寒')

# 从数据表中提取信息
# 输入 year 为公历年
# 返回闰月月份，大小月信息，当年春节到元旦天数
def get_nongli_year_info(year):
    if year < nongli_data_range[0] or year > nongli_data_range[1]:
        raise ValueError('year out of range')
    table_addr = (year - nongli_data_range[0]) * 3
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

# 返回节气的中文表示
# 输入 jieqi_code 为节气代码，如果为 None 则返回 '无'
def get_jieqi_str(jieqi_code):
    if jieqi_code == None:
        return '无'
    return jieqi_strs[jieqi_code]

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

# 获取某年某月的节气信息
# year 为公历年
# month 为公历月
# 返回值为当月第一个节气的日期和编号，第二个节气的日期和编号，节气编号从 0 开始，0 表示立春
def get_jieqi_month(year, month):
    if year < nongli_data_range[0] or year > nongli_data_range[1]:
        raise ValueError('year out of range!')
    jq_bases = jieqi_date_base[month - 1]
    jq1 = jq_bases >> 5
    jq2 = jq_bases & 0x1f
    for i in range(len(jieqi_offset) // 8):
        yearend = struct.unpack('>H', jieqi_offset[i * 8:i * 8 + 2])[0]
        if year <= yearend:
            ofs1 = jieqi_offset[i * 8 + 2 + (5 - (month - 1) // 2)] >> (((month - 1) % 2) * 4)
            jq2 += (ofs1 >> 2) & 0b11
            jq1 += ofs1 & 0b11
            break
    year_idx = (year - nongli_data_range[0]) * 3
    ofs2 = jieqi_year_offset[year_idx + (2 - (month - 1) // 4)] >> (((month - 1) % 4) * 2)
    jq2 += (ofs2 >> 1) & 1
    jq1 += ofs2 & 1
    if month == 1:
        jq1_code = 22 # 小寒
    else:
        jq1_code = (month - 2) * 2
    return (jq1, jq1_code), (jq2, jq1_code + 1)

# 判断是否为节气
# 输入公历年月日
# 输出节气编号，输出为 None 表示日期非节气
def get_jieqi(year, month, day):
    if year < nongli_data_range[0] or year > nongli_data_range[1]:
        raise ValueError('year out of range!')
    jq = jieqi_date_base[month - 1]
    jqn = 1 if day > 15 else 0 # 在上半个月则用当月第一个节气的数据
    if jqn:
        jq = jq & 0x1f
    else:
        jq = jq >> 5
    for i in range(len(jieqi_offset) // 8):
        yearend = struct.unpack('>H', jieqi_offset[i * 8:i * 8 + 2])[0]
        if year <= yearend:
            ofs1 = jieqi_offset[i * 8 + 2 + (5 - (month - 1) // 2)] >> (((month - 1) % 2) * 4)
            jq += (ofs1 >> (2 * jqn)) & 0b11
            break
    year_idx = (year - nongli_data_range[0]) * 3
    ofs2 = jieqi_year_offset[year_idx + (2 - (month - 1) // 4)] >> (((month - 1) % 4) * 2)
    jq += (ofs2 >> jqn) & 1
    if month == 1:
        jq_code = 22
    else:
        jq_code = (month - 2) * 2
    jq_code += jqn
    if jq == day:
        return jq_code
    else:
        return None
