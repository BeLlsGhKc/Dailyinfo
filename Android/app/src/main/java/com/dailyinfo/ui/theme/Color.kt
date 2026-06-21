package com.dailyinfo.ui.theme

import androidx.compose.ui.graphics.Color

/**
 * 颜色配置
 *
 * 对应 Shared/task_model.py 的 PRIORITY_CONFIG
 */
object AppColors {
    // 主色调
    val Primary = Color(0xFF007AFF)          // 蓝色
    val PrimaryVariant = Color(0xFF0056CC)   // 深蓝色
    val Secondary = Color(0xFF5856D6)        // 紫色

    // 背景色
    val Background = Color(0xFFF2F2F7)       // 浅灰色背景
    val Surface = Color(0xFFFFFFFF)          // 白色表面
    val CardBackground = Color(0xFFFFFFFF)   // 卡片背景

    // 文字色
    val TextPrimary = Color(0xFF1D1D1F)      // 主要文字
    val TextSecondary = Color(0xFF8E8E93)    // 次要文字
    val TextTertiary = Color(0xFFAEAEB2)     // 辅助文字

    // 状态色
    val Success = Color(0xFF34C759)          // 成功/完成
    val Warning = Color(0xFFFF9500)          // 警告
    val Error = Color(0xFFFF3B30)            // 错误
    val Info = Color(0xFF5AC8FA)             // 信息

    // 优先级颜色 - 对应 PRIORITY_CONFIG
    val PriorityPlan = Color(0xFFAF52DE)     // 计划 - 紫色
    val PriorityHigh = Color(0xFFFF3B30)     // 高 - 红色
    val PriorityMedium = Color(0xFFFF9500)   // 中 - 橙色
    val PriorityLow = Color(0xFF34C759)      // 低 - 绿色

    // 优先级背景色
    val PriorityPlanBg = Color(0x1FAF52DE)   // 计划背景
    val PriorityHighBg = Color(0x1FFF3B30)   // 高背景
    val PriorityMediumBg = Color(0x1FFF9500) // 中背景
    val PriorityLowBg = Color(0x1F34C759)    // 低背景

    // 日历标签颜色
    val HolidayText = Color(0xFFFF3B30)      // 节假日文字（红色）
    val WorkdayText = Color(0xFFC76A00)      // 调休上班文字（橙色）
    val FestivalText = Color(0xFF00C7BE)     // 节日文字（青色）
    val SolarTermText = Color(0xFF00C7BE)    // 节气文字（青色）

    // 过期任务颜色
    val OverdueBackground = Color(0x0DFF3B30) // 过期任务背景（极淡红色）
    val OverdueBorder = Color(0x1AFF3B30)     // 过期任务边框（淡红色）
    val OverdueText = Color(0xFFD84A40)       // 过期文字（柔和红色）

    // 获取优先级颜色
    fun getPriorityColor(priority: String): Color {
        return when (priority) {
            "计划" -> PriorityPlan
            "高" -> PriorityHigh
            "中" -> PriorityMedium
            "低" -> PriorityLow
            else -> TextSecondary
        }
    }

    // 获取优先级背景色
    fun getPriorityBgColor(priority: String): Color {
        return when (priority) {
            "计划" -> PriorityPlanBg
            "高" -> PriorityHighBg
            "中" -> PriorityMediumBg
            "低" -> PriorityLowBg
            else -> Color(0x1F8E8E93)
        }
    }
}
