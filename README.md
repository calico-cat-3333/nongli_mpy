# 适用于 MicroPython 的精简农历库

一个适用于 MicroPython 的精简农历库，支持公历到农历转换和节气判断，同时也支持 Python3。

基于查表法进行转换，支持 1901～2099 年的数据。农历数据来自著名的 nongli.c 代码（有修正），节气数据来自 cnLunar 项目。

考虑到 MicroPython 设备通常具有有限的内存，代码中使用了压缩存储并保存为 bytes 的查找表，因此牺牲了部分可读性，并且仅注重农历公历间的简单转换和节气的判断，没有提供更多复杂功能。

可以执行 [gen_lut.py](./gen_lut.py) 程序生成更小的数据范围，并替换到原始代码中的对应变量中，以进一步减小内存占用。

本项目的数据已使用 [cnLunar](https://github.com/OPN48/cnlunar) 项目进行验证。

## 使用

```
import nongli
import time

now = time.localtime()

y = now[0]
m = now[1]
d = now[2]

year, month, month_days, is_leap_month, day = nongli.from_date(y, m, d)
year_str, shengxiao = nongli.get_year_str(year)
month_str = nongli.get_month_str(month, is_leap_month)
day_str = nongli.get_day_str(day)
jieqi = nongli.get_jieqi(y, m, d)
jieqi_str = nongli.get_jieqi_str(jieqi)
print(y, m, d, ': 农历', year_str + shengxiao + '年', month_str, day_str, '节气：', jieqi_str)
```

## API 文档

### 基本信息获取

#### get_nongli_year_info(year)

* 功能：获取指定公历年份对应的农历年信息（闰月、大小月、春节偏移）。
* 参数：
  * year (int): 公历年份。
* 返回值：(leap_month, mon_days, sprf_date)
  * leap_month (int): 闰月月份（0 表示无闰月）。
  * mon_days (int): 13 位二进制数，每位表示对应农历月是否为大月（1 为大月 30 天，0 为小月 29 天）。
  * sprf_date (int): 春节到元旦的天数（即春节在公历中的日期偏移量，1 月 1 日为 0）。


#### is_leap_year(year)

* 功能：判断公历年份是否为闰年。
* 参数：
  * year (int): 公历年份。
* 返回值：bool，闰年返回 True，否则 False。

---

### 农历字符串表示

#### get_year_str(year)

* 功能：根据农历年份返回干支纪年和生肖。
* 参数：
  * year (int): 农历年份。
* 返回值：(tiangan_dizhi, shengxiao)
  * tiangan_dizhi (str): 干支纪年，如“甲子”。
  * shengxiao (str): 生肖，如“鼠”。

#### get_month_str(month, is_leap_month)

* 功能：返回农历月份的中文表示。
* 参数：
  * month (int): 农历月份（1–12）。
  * is_leap_month (bool): 是否为闰月。
* 返回值：str，如“正月”、“闰五月”。

#### get_day_str(day)

* 功能：返回农历日期的中文表示。
* 参数：
  * day (int): 农历日（1–30）。
* 返回值：str，如“初一”、“廿三”、“三十”。

#### get_jieqi_str(jieqi_code)

* 功能：根据节气编号返回节气名称，若为 None 则返回“无”。
* 参数：
  * jieqi_code (int or None): 节气编号（0 表示立春，23 表示大寒）。
* 返回值：str，如“立春”。

---

### 公历农历转换

#### from_date(year, month, day)

* 功能：根据公历年月日计算对应的农历信息。
* 参数：
  * year (int): 公历年。
  * month (int): 公历月（1–12）。
  * day (int): 公历日。
* 返回值：(nongli_year, nongli_month, month_days, is_leap_month, nongli_day)
  * nongli_year (int): 农历年份（春节所在公历年）。
  * nongli_month (int): 农历月份（1–12）。
  * month_days (int): 该农历月的总天数（29 或 30）。
  * is_leap_month (bool): 是否为闰月。
  * nongli_day (int): 农历日（1–30）。

#### from_timestamp(timestamp)

* 功能：根据 Unix 时间戳（秒）返回对应的农历信息。
* 参数：
  * timestamp (float or int): Unix 时间戳（自 1970-01-01 00:00:00 UTC 的秒数）。
* 返回值：同 from_date()。

#### today()

* 功能：返回当前系统时间对应的农历信息。
* 返回值：同 from_date()。

#### to_gregorian(nongli_year, nongli_month, is_leap_month, nongli_day):

* 功能：根据农历年月日计算对应的公历信息。
* 参数：
  * nongli_year (int): 农历年份。
  * nongli_month (int): 农历月份（1-12）。
  * is_leap_month (bool): 是否为闰月。
  * nongli_day (int): 农历日（1-30）。
* 返回值：(year, month, day)
  * year (int): 公历年。
  * month (int): 公历月（1–12）。
  * day (int): 公历日。

---

### 节气相关

#### get_jieqi_month(year, month)

* 功能：获取指定公历月份的两个节气信息。
* 参数：
  * year (int): 公历年。
  * month (int): 公历月（1–12）。
* 返回值：((day1, code1), (day2, code2))
  * day1 (int): 当月第一个节气的日期。
  * code1 (int): 当月第一个节气的编号（0–23）。
  * day2 (int): 当月第二个节气的日期。
  * code2 (int): 当月第二个节气的编号。

#### get_jieqi(year, month, day)

* 功能：判断指定公历日期是否为节气，若是则返回节气编号。
* 参数：
  * year (int): 公历年。
  * month (int): 公历月（1–12）。
  * day (int): 公历日。
* 返回值：int or None
  * 若该日是节气，返回对应的节气编号（0–23）。
  * 否则返回 None。

---

### 异常

* ValueError: 当传入的年份超出支持的范围或日期不合法时抛出。

## 数据

这里并没有直接使用来自 nongli.c 和 cnLunar 的原始数据，而是对其进行了进一步处理和修正。这里记录处理步骤。

nongli.c 的数据经检查存在以下错误，现已修正：

* 1960 年应为闰六月。
* 1989 年六月应为大月，七月应为小月。
* 2025 年三月应为大月，四月应为小月。
* 2057 年八月应为小月，九月应为大月。
* 2089 年七月应为小月，八月应为大月。
* 2097 年六月应为小月，七月应为大月。

数据修正后，直接转换为 bytes 存储，总长度 597 字节。

cnLunar 中提供的节气查找表使用节气基本日期和偏移量(2 bit 每节气)的方式存储，偏移量共占用 1194 字节，在查看偏移量数据时，可以发现发现在很长一段时间内，偏移量都只有两个值，而且两个值的差为 1，因此可以将偏移量拆分为两个表，进一步减少占用。

拆分出的第一个表为分段偏移量表，他描述多个年份共有的偏移量(2 bit 每节气)，该表使用程序自动分析生成，代码见 gen_lut.py。经分析，1901-2099 之间仅需要 5 个分段，占用 40 字节。

第二个表为按年存储的偏移量表，每个节气 1 bit，共占用 597 字节。

节气基本日期数据中，可以发现第一个日期均小于等于 7，即最大 3 bit，第二个日期均小于 32 即最大 5 bit 因此可以压缩存储在 1 字节中。这里将每月的第一个节气存储在 1 字节的高 3 bit 中，第二个节气存储在低 5 bit 中，共占用 12 字节。

完整的数据处理步骤见 [gen_lut.py](./gen_lut.py)，可以再次执行该文件，它会要求输入开始和结束年份，然后输出转换后两个年份之间的数据。通过输入一个较小的范围并将输出的数据对应替换到 nongl.py 中，可以进一步减小内存占用。

## 参考与鸣谢：

赖皮，Campo - nongli.c：

农历数据和最初的算法设计，由于我没有找到文件的原始出处，所以这里贴一个 GitHub 上找到的副本：[https://github.com/ywf-147/IIC-OLED/blob/master/nongli.c](https://github.com/ywf-147/IIC-OLED/blob/master/nongli.c)

cuba3 - [cnLunar](https://github.com/OPN48/cnlunar)：

节气数据和算法设计思路，农历数据验证。

[GB/T 33661-2017 农历的编算和颁行](https://openstd.samr.gov.cn/bzgk/gb/newGbInfo?hcno=E107EA4DE9725EDF819F33C60A44B296)：

农历规则的规范。

ytliu0 - [农历编算法则](https://ytliu0.github.io/ChineseCalendar/rules_simp.html) ：

农历规则的解读。
