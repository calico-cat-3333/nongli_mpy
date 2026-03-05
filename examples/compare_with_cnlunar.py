# cooperate with chatgpt

import datetime
import cnlunar
import nongli


def get_nongli(dt):
    y, m, md, leap, d = nongli.from_date(dt.year, dt.month, dt.day)
    jq = nongli.get_jieqi_str(nongli.get_jieqi(dt.year, dt.month, dt.day))
    return (y, m, d, leap, jq)


def get_cnlunar(dt):
    a = cnlunar.Lunar(dt)
    return (
        a.lunarYear,
        a.lunarMonth,
        a.lunarDay,
        a.isLunarLeapMonth,
        a.todaySolarTerms
    )


# ====== 找到 1901 年春节 ======
# cnLunar 是准确的，用它找起点
for day in range(1, 60):
    dt = datetime.datetime(1901, 1, 1) + datetime.timedelta(days=day)
    a = cnlunar.Lunar(dt)
    if a.lunarMonth == 1 and a.lunarDay == 1:
        start_date = dt.date()
        break

end_date = datetime.date(2099, 12, 31)

print("对拍区间：", start_date, "→", end_date)

cur = start_date
delta = datetime.timedelta(days=1)

count = 0
wr_cnt = 0

while cur <= end_date:
    dt = datetime.datetime(cur.year, cur.month, cur.day)

    my_res = get_nongli(dt)
    cn_res = get_cnlunar(dt)

    if my_res != cn_res:
        print("❌ 不一致：", cur)
        print("你的结果:", my_res)
        print(" cnLunar:", cn_res)
        wr_cnt += 1

    count += 1
    if count % 5000 == 0:
        print("已检查", count, "天")

    cur += delta
else:
    print("总天数：", count, '错误天数：', wr_cnt)
