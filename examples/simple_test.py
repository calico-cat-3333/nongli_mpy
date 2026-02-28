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
