package com.dailyinfo.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.unit.dp
import com.dailyinfo.ui.theme.AppColors

/**
 * 优先级标签组件
 */
@Composable
fun PriorityChip(
    priority: String,
    modifier: Modifier = Modifier
) {
    val bgColor = AppColors.getPriorityBgColor(priority)
    val textColor = AppColors.getPriorityColor(priority)

    Box(
        modifier = modifier
            .clip(RoundedCornerShape(6.dp))
            .background(bgColor)
            .padding(horizontal = 8.dp, vertical = 4.dp)
    ) {
        Text(
            text = priority,
            style = MaterialTheme.typography.labelMedium,
            color = textColor
        )
    }
}
