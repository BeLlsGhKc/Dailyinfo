# -*- coding: utf-8 -*-
"""
日历工具模块 - 农历、节假日、节气

此文件从 Code/daily_tasks.py 提取，作为 Kotlin 实现的参考源。
安卓端的 calendar/ 包下的 Kotlin 代码需与此保持一致。
"""

from datetime import date


# ========== 中国节假日数据（2026年）==========
# 正日子显示节日名，其他假期日显示"节日名假期"
HOLIDAYS = {
    # 元旦
    "2026-01-01": "元旦",
    "2026-01-02": "元旦假期",
    "2026-01-03": "元旦假期",
    # 春节
    "2026-02-15": "春节假期",
    "2026-02-16": "春节假期",
    "2026-02-17": "春节",
    "2026-02-18": "春节假期",
    "2026-02-19": "春节假期",
    "2026-02-20": "春节假期",
    "2026-02-21": "春节假期",
    "2026-02-22": "春节假期",
    "2026-02-23": "春节假期",
    # 清明节
    "2026-04-04": "清明节假期",
    "2026-04-05": "清明节",
    "2026-04-06": "清明节假期",
    # 劳动节
    "2026-05-01": "劳动节",
    "2026-05-02": "劳动节假期",
    "2026-05-03": "劳动节假期",
    "2026-05-04": "劳动节假期",
    "2026-05-05": "劳动节假期",
    # 端午节
    "2026-06-19": "端午节",
    "2026-06-20": "端午节假期",
    "2026-06-21": "端午节假期",
    # 中秋节
    "2026-09-25": "中秋节",
    "2026-09-26": "中秋节假期",
    "2026-09-27": "中秋节假期",
    # 国庆节
    "2026-10-01": "国庆节",
    "2026-10-02": "国庆节假期",
    "2026-10-03": "国庆节假期",
    "2026-10-04": "国庆节假期",
    "2026-10-05": "国庆节假期",
    "2026-10-06": "国庆节假期",
    "2026-10-07": "国庆节假期",
}


ADJUSTED_WORKDAYS = {
    "2026-01-04": "调休上班",
    "2026-02-14": "调休上班",
    "2026-02-28": "调休上班",
    "2026-05-09": "调休上班",
    "2026-09-20": "调休上班",
    "2026-10-10": "调休上班",
}


SOLAR_FESTIVALS = {
    (2, 14): "情人节",
    (3, 8): "妇女节",
    (3, 12): "植树节",
    (4, 1): "愚人节",
    (5, 4): "青年节",
    (6, 1): "儿童节",
    (9, 10): "教师节",
    (10, 31): "万圣夜",
    (12, 24): "平安夜",
    (12, 25): "圣诞节",
}


SOLAR_TERMS = {
    "2026-01-05": "小寒",
    "2026-01-20": "大寒",
    "2026-02-04": "立春",
    "2026-02-18": "雨水",
    "2026-03-05": "惊蛰",
    "2026-03-20": "春分",
    "2026-04-05": "清明",
    "2026-04-20": "谷雨",
    "2026-05-05": "立夏",
    "2026-05-21": "小满",
    "2026-06-05": "芒种",
    "2026-06-21": "夏至",
    "2026-07-07": "小暑",
    "2026-07-23": "大暑",
    "2026-08-07": "立秋",
    "2026-08-23": "处暑",
    "2026-09-07": "白露",
    "2026-09-23": "秋分",
    "2026-10-08": "寒露",
    "2026-10-23": "霜降",
    "2026-11-07": "立冬",
    "2026-11-22": "小雪",
    "2026-12-07": "大雪",
    "2026-12-22": "冬至",
}


# ========== 农历相关 ==========

LUNAR_YEAR_INFO = {
    2024: 0x04b60,
    2025: 0x0a6e6,
    2026: 0x0a4e0,
    2027: 0x0d260,
}
LUNAR_BASE_DATE = date(2024, 2, 10)  # 甲辰年正月初一
HEAVENLY_STEMS = "甲乙丙丁戊己庚辛壬癸"
EARTHLY_BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
LUNAR_MONTH_NAMES = ["正月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "冬月", "腊月"]
LUNAR_DAY_NAMES = [
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十",
]
LUNAR_FESTIVALS = {
    (1, 1): "春节",
    (1, 15): "元宵节",
    (2, 2): "龙抬头",
    (5, 5): "端午节",
    (7, 7): "七夕",
    (7, 15): "中元节",
    (8, 15): "中秋节",
    (9, 9): "重阳节",
    (12, 8): "腊八节",
}


def lunar_leap_month(year):
    """返回农历闰月，0 表示无闰月。"""
    return LUNAR_YEAR_INFO[year] & 0xF


def lunar_leap_days(year):
    """返回农历闰月天数。"""
    if lunar_leap_month(year) == 0:
        return 0
    return 30 if LUNAR_YEAR_INFO[year] & 0x10000 else 29


def lunar_month_days(year, month):
    """返回农历指定月份天数。"""
    return 30 if LUNAR_YEAR_INFO[year] & (0x10000 >> month) else 29


def lunar_year_days(year):
    """返回农历年份总天数。"""
    total = 0
    for month in range(1, 13):
        total += lunar_month_days(year, month)
    return total + lunar_leap_days(year)


def solar_to_lunar(solar_date):
    """把公历日期转换为 2024-2027 日历范围内的农历日期。"""
    offset = (solar_date - LUNAR_BASE_DATE).days
    if offset < 0:
        return None

    lunar_year = 2024
    while lunar_year in LUNAR_YEAR_INFO:
        year_days = lunar_year_days(lunar_year)
        if offset < year_days:
            break
        offset -= year_days
        lunar_year += 1

    if lunar_year not in LUNAR_YEAR_INFO:
        return None

    leap_month = lunar_leap_month(lunar_year)
    lunar_month = 1
    is_leap_month = False

    while lunar_month <= 12:
        month_days = lunar_leap_days(lunar_year) if is_leap_month else lunar_month_days(lunar_year, lunar_month)
        if offset < month_days:
            return {
                "year": lunar_year,
                "month": lunar_month,
                "day": offset + 1,
                "is_leap_month": is_leap_month,
            }

        offset -= month_days
        if leap_month == lunar_month and not is_leap_month:
            is_leap_month = True
        else:
            is_leap_month = False
            lunar_month += 1

    return None


def lunar_ganzhi_year(year):
    """返回农历干支年。"""
    return f"{HEAVENLY_STEMS[(year - 4) % 10]}{EARTHLY_BRANCHES[(year - 4) % 12]}"


def format_lunar_info(lunar_info):
    """格式化农历信息。"""
    month_name = LUNAR_MONTH_NAMES[lunar_info["month"] - 1]
    if lunar_info["is_leap_month"]:
        month_name = f"闰{month_name}"
    day_name = LUNAR_DAY_NAMES[lunar_info["day"] - 1]
    return f"{lunar_ganzhi_year(lunar_info['year'])}年 农历 {month_name}{day_name}"


def add_calendar_label(labels, name, kind):
    """追加日历标签，避免重复显示。"""
    if not name:
        return
    for existing_name, _ in labels:
        if existing_name == name:
            return
    labels.append((name, kind))


def nth_weekday_of_month(year, month, weekday, nth):
    """返回某月第 nth 个 weekday 日期，weekday 使用 Python 标准：周一为 0。"""
    current = date(year, month, 1)
    offset = (weekday - current.weekday()) % 7
    return current.replace(day=1 + offset + (nth - 1) * 7)


def solar_weekday_festival(solar_date):
    """返回按第几个星期几计算的公历节日。"""
    if solar_date == nth_weekday_of_month(solar_date.year, 5, 6, 2):
        return "母亲节"
    if solar_date == nth_weekday_of_month(solar_date.year, 6, 6, 3):
        return "父亲节"
    return ""


def has_equivalent_label(labels, name):
    """判断是否已有等价标签，例如清明节已覆盖清明。"""
    for existing_name, _ in labels:
        if existing_name == name or existing_name == f"{name}节":
            return True
    return False


def calendar_day_labels(solar_date, lunar_info):
    """返回节日、节气、假期和调休标签。"""
    date_str = solar_date.strftime("%Y-%m-%d")
    labels = []

    add_calendar_label(labels, ADJUSTED_WORKDAYS.get(date_str, ""), "workday")
    add_calendar_label(labels, HOLIDAYS.get(date_str, ""), "holiday")

    if not lunar_info["is_leap_month"]:
        festival = LUNAR_FESTIVALS.get((lunar_info["month"], lunar_info["day"]))
        if festival:
            add_calendar_label(labels, festival, "festival")

    add_calendar_label(labels, SOLAR_FESTIVALS.get((solar_date.month, solar_date.day), ""), "festival")
    add_calendar_label(labels, solar_weekday_festival(solar_date), "festival")

    solar_term = SOLAR_TERMS.get(date_str, "")
    if solar_term and not has_equivalent_label(labels, solar_term):
        add_calendar_label(labels, solar_term, "solar_term")

    return labels


def format_calendar_info(solar_date):
    """返回底部日历信息文本和标签类型列表。"""
    lunar_info = solar_to_lunar(solar_date)
    if lunar_info is None:
        return "农历信息暂不支持", []

    labels = calendar_day_labels(solar_date, lunar_info)
    text = format_lunar_info(lunar_info)
    if labels:
        label_text = " ".join(name for name, _ in labels)
        return f"{text} {label_text}", [kind for _, kind in labels]
    return text, []
