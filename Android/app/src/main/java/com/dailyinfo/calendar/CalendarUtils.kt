package com.dailyinfo.calendar

import kotlinx.datetime.LocalDate

/**
 * 日历工具类
 *
 * 对应 Shared/calendar_utils.py 中的日历标签相关函数
 */
object CalendarUtils {

    /**
     * 日历标签类型
     */
    enum class LabelKind {
        WORKDAY,    // 调休上班
        HOLIDAY,    // 节假日
        FESTIVAL,   // 节日
        SOLAR_TERM  // 节气
    }

    /**
     * 日历标签
     */
    data class CalendarLabel(
        val name: String,
        val kind: LabelKind
    )

    /**
     * 添加日历标签，避免重复显示
     */
    private fun addCalendarLabel(
        labels: MutableList<CalendarLabel>,
        name: String,
        kind: LabelKind
    ) {
        if (name.isEmpty()) return
        if (labels.any { it.name == name }) return
        labels.add(CalendarLabel(name, kind))
    }

    /**
     * 返回某月第 nth 个 weekday 日期
     * weekday 使用 ISO 标准：周一为 1，周日为 7
     */
    private fun nthWeekdayOfMonth(
        year: Int,
        month: Int,
        weekday: Int,
        nth: Int
    ): LocalDate {
        val firstDay = LocalDate(year, month, 1)
        val firstWeekday = firstDay.dayOfWeek.value
        val offset = (weekday - firstWeekday + 7) % 7
        return LocalDate(year, month, 1 + offset + (nth - 1) * 7)
    }

    /**
     * 返回按第几个星期几计算的公历节日
     */
    private fun solarWeekdayFestival(solarDate: LocalDate): String {
        // 母亲节：5月第2个周日
        if (solarDate == nthWeekdayOfMonth(solarDate.year, 5, 7, 2)) {
            return "母亲节"
        }
        // 父亲节：6月第3个周日
        if (solarDate == nthWeekdayOfMonth(solarDate.year, 6, 7, 3)) {
            return "父亲节"
        }
        return ""
    }

    /**
     * 判断是否已有等价标签
     */
    private fun hasEquivalentLabel(labels: List<CalendarLabel>, name: String): Boolean {
        return labels.any { it.name == name || it.name == "${name}节" }
    }

    /**
     * 返回节日、节气、假期和调休标签
     */
    fun calendarDayLabels(solarDate: LocalDate): List<CalendarLabel> {
        val dateStr = solarDate.toString()
        val labels = mutableListOf<CalendarLabel>()

        // 调休上班
        addCalendarLabel(labels, HolidayData.ADJUSTED_WORKDAYS[dateStr] ?: "", LabelKind.WORKDAY)

        // 法定节假日
        addCalendarLabel(labels, HolidayData.HOLIDAYS[dateStr] ?: "", LabelKind.HOLIDAY)

        // 农历节日
        val lunarInfo = LunarCalendar.solarToLunar(solarDate)
        if (lunarInfo != null && !lunarInfo.isLeapMonth) {
            val festival = HolidayData.LUNAR_FESTIVALS[Pair(lunarInfo.month, lunarInfo.day)]
            if (festival != null) {
                addCalendarLabel(labels, festival, LabelKind.FESTIVAL)
            }
        }

        // 公历节日
        addCalendarLabel(
            labels,
            HolidayData.SOLAR_FESTIVALS[Pair(solarDate.monthNumber, solarDate.dayOfMonth)] ?: "",
            LabelKind.FESTIVAL
        )

        // 按星期几计算的节日
        addCalendarLabel(labels, solarWeekdayFestival(solarDate), LabelKind.FESTIVAL)

        // 节气
        val solarTerm = HolidayData.SOLAR_TERMS[dateStr] ?: ""
        if (solarTerm.isNotEmpty() && !hasEquivalentLabel(labels, solarTerm)) {
            addCalendarLabel(labels, solarTerm, LabelKind.SOLAR_TERM)
        }

        return labels
    }

    /**
     * 返回底部日历信息文本和标签类型列表
     */
    fun formatCalendarInfo(solarDate: LocalDate): Pair<String, List<LabelKind>> {
        val lunarInfo = LunarCalendar.solarToLunar(solarDate)
            ?: return Pair("农历信息暂不支持", emptyList())

        val labels = calendarDayLabels(solarDate)
        val text = LunarCalendar.formatLunarInfo(lunarInfo)

        return if (labels.isNotEmpty()) {
            val labelText = labels.joinToString(" ") { it.name }
            val labelKinds = labels.map { it.kind }
            Pair("$text $labelText", labelKinds)
        } else {
            Pair(text, emptyList())
        }
    }
}
