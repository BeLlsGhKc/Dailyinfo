package com.dailyinfo.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.core.view.WindowCompat

/**
 * 暗色主题配色方案
 */
private val DarkColorScheme = darkColorScheme(
    primary = AppColors.Primary,
    secondary = AppColors.Secondary,
    tertiary = AppColors.Info,
    background = AppColors.Background,
    surface = AppColors.Surface,
    onPrimary = AppColors.Surface,
    onSecondary = AppColors.Surface,
    onTertiary = AppColors.Surface,
    onBackground = AppColors.TextPrimary,
    onSurface = AppColors.TextPrimary,
)

/**
 * 亮色主题配色方案
 */
private val LightColorScheme = lightColorScheme(
    primary = AppColors.Primary,
    secondary = AppColors.Secondary,
    tertiary = AppColors.Info,
    background = AppColors.Background,
    surface = AppColors.Surface,
    onPrimary = AppColors.Surface,
    onSecondary = AppColors.Surface,
    onTertiary = AppColors.Surface,
    onBackground = AppColors.TextPrimary,
    onSurface = AppColors.TextPrimary,
)

/**
 * Dailyinfo 主题
 */
@Composable
fun DailyinfoTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme

    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = colorScheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).isAppearanceLightStatusBars = !darkTheme
        }
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = AppTypography,
        content = content
    )
}
