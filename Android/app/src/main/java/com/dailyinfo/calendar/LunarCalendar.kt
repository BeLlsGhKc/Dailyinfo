package com.dailyinfo.calendar

import kotlinx.datetime.LocalDate
import kotlinx.datetime.TimeZone
import kotlinx.datetime.atStartOfDayIn

/**
 * 农历转换工具
 *
 * 对应 Shared/calendar_utils.py 中的农历相关函数
 */
object LunarCalendar {

    /** 农历年份信息 */
    private val LUNAR_YEAR_INFO = mapOf(
        2024 to 0x04b60,
        2025 to 0x0a6e6,
        2026 to 0x0a4e0,
        2027 to 0x0d260
    )

    /** 农历基准日期：甲辰年正月初一 */
    private val LUNAR_BASE_DATE = LocalDate(2024, 2, 10)

    /** 天干 */
    private const val HEAVENLY_STEMS = "甲乙丙丁戊己庚辛壬癸"

    /** 地支 */
    private const val EARTHLY_BRANCHES = "子丑寅卯辰巳午未申酉戌亥"

    /** 农历月份名称 */
    private val LUNAR_MONTH_NAMES = arrayOf(
        "正月", "二月", "三月", "四月", "五月", "六月",
        "七月", "八月", "九月", "十月", "冬月", "腊月"
    )

    /** 农历日期名称 */
    private val LUNAR_DAY_NAMES = arrayOf(
        "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
        "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
        "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十"
    )

    /**
     * 农历信息
     */
    data class LunarInfo(
        val year: Int,
        val month: Int,
        val day: Int,
        val isLeapMonth: Boolean
    )

    /**
     * 返回农历闰月，0 表示无闰月
     */
    private fun lunarLeapMonth(year: Int): Int {
        return LUNAR_YEAR_INFO[year]?.and(0xF) ?: 0
    }

    /**
     * 返回农历闰月天数
     */
    private fun lunarLeapDays(year: Int): Int {
        if (lunarLeapMonth(year) == 0) return 0
        return if (LUNAR_YEAR_INFO[year]?.and(0x10000) != 0) 30 else 29
    }

    /**
     * 返回农历指定月份天数
     */
    private fun lunarMonthDays(year: Int, month: Int): Int {
        return if (LUNAR_YEAR_INFO[year]?.and(0x10000 shr month) != 0) 30 else 29
    }

    /**
     * 返回农历年份总天数
     */
    private fun lunarYearDays(year: Int): Int {
        var total = 0
        for (month in 1..12) {
            total += lunarMonthDays(year, month)
        }
        return total + lunarLeapDays(year)
    }

    /**
     * 把公历日期转换为 2024-2027 日历范围内的农历日期
     */
    fun solarToLunar(solarDate: LocalDate): LunarInfo? {
        val offset = ((solarDate.atStartOfDayIn(TimeZone.UTC).toEpochMilliseconds() -
            LUNAR_BASE_DATE.atStartOfDayIn(TimeZone.UTC).toEpochMilliseconds()) / 86400000).toInt()
        if (offset < 0) return null

        var lunarYear = 2024
        var remainingDays = offset

        while (lunarYear in LUNAR_YEAR_INFO) {
            val yearDays = lunarYearDays(lunarYear)
            if (remainingDays < yearDays) break
            remainingDays -= yearDays
            lunarYear++
        }

        if (lunarYear !in LUNAR_YEAR_INFO) return null

        val leapMonth = lunarLeapMonth(lunarYear)
        var lunarMonth = 1
        var isLeapMonth = false

        while (lunarMonth <= 12) {
            val monthDays = if (isLeapMonth) {
                lunarLeapDays(lunarYear)
            } else {
                lunarMonthDays(lunarYear, lunarMonth)
            }

            if (remainingDays < monthDays) {
                return LunarInfo(
                    year = lunarYear,
                    month = lunarMonth,
                    day = remainingDays + 1,
                    isLeapMonth = isLeapMonth
                )
            }

            remainingDays -= monthDays
            if (leapMonth == lunarMonth && !isLeapMonth) {
                isLeapMonth = true
            } else {
                isLeapMonth = false
                lunarMonth++
            }
        }

        return null
    }

    /**
     * 返回农历干支年
     */
    fun lunarGanzhiYear(year: Int): String {
        val stemIndex = (year - 4) % 10
        val branchIndex = (year - 4) % 12
        return "${HEAVENLY_STEMS[stemIndex]}${EARTHLY_BRANCHES[branchIndex]}"
    }

    /**
     * 格式化农历信息
     */
    fun formatLunarInfo(lunarInfo: LunarInfo): String {
        var monthName = LUNAR_MONTH_NAMES[lunarInfo.month - 1]
        if (lunarInfo.isLeapMonth) {
            monthName = "闰$monthName"
        }
        val dayName = LUNAR_DAY_NAMES[lunarInfo.day - 1]
        return "${lunarGanzhiYear(lunarInfo.year)}年 农历 $monthName$dayName"
    }
}
