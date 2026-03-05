import nongli
import time
import sys


def get_month_days(y, m):
    if m <= 7:
        if m % 2 == 1:
            return 31
        elif m == 2:
            if nongli.is_leap_year(y):
                return 29
            else:
                return 28
        else:
            return 30
    else:
        if m % 2 == 0:
            return 31
        else:
            return 30

def print_calendar(year, month):
    day1_time = time.localtime(time.mktime((year, month, 1, 1, 0, 0, 0, 0, -1)))

    day1 = day1_time[2]
    day1weekday = day1_time[6]

    day1nl = nongli.from_date(year, month, day1)
    nlyear, sx = nongli.get_year_str(day1nl[0])

    jq = nongli.get_jieqi_month(year, month)

    print(year, '年', month, '月，农历' + nlyear + sx + '年' + nongli.get_month_str(day1nl[1], day1nl[3]) + nongli.get_day_str(day1nl[4]) + '日始')
    print('星期一       星期二       星期三       星期四       星期五       星期六       星期天')

    for i in range(day1weekday):
        print(' ' * 12, end=' ')
    current_weekday = day1weekday

    for i in range(get_month_days(year, month)):
        if i < 9:
            print('0', end='')
        print(i + 1, end=' ')
        nlday = (day1nl[4] - 1 + i) % day1nl[2] + 1
        if i + 1 == jq[0][0]:
            print(nongli.get_jieqi_str(jq[0][1]), end=' ' * 6)
        elif i + 1 == jq[1][0]:
            print(nongli.get_jieqi_str(jq[1][1]), end=' ' * 6)
        elif nlday == 1:
            _, nlmonth, _, isleap, _ = nongli.from_date(year, month, i + 1)
            mstr = nongli.get_month_str(nlmonth, isleap)
            mstrlen = 10 - len(mstr) * 2
            print(mstr, end=' ' * mstrlen)
        else:
            print(nongli.get_day_str(nlday), end=' ' * 6)
        current_weekday += 1
        if current_weekday == 7:
            current_weekday = 0
            print('')
    print('')


ct = time.localtime()
year = ct[0]
month = ct[1]

for k in sys.argv:
    if k.startswith('y='):
        year=int(k[2:])
    if k.startswith('m='):
        month=int(k[2:])

print_calendar(year, month)
