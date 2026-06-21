package com.dailyinfo.ui.components

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.combinedClickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.DateRange
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.dailyinfo.data.Task
import com.dailyinfo.ui.theme.AppColors

/**
 * 任务列表项组件
 *
 * @param task 任务数据
 * @param isHistory 是否为历史页面
 * @param isOverdue 是否过期
 * @param isNormalOverdue 普通任务是否过期（创建日期早于今天）
 * @param onToggleComplete 切换完成状态
 * @param onTogglePin 切换置顶（仅历史页面）
 * @param onDelete 删除任务
 * @param onClick 点击跳转详情
 */
@OptIn(ExperimentalFoundationApi::class)
@Composable
fun TaskItem(
    task: Task,
    isHistory: Boolean = false,
    isOverdue: Boolean = false,
    isNormalOverdue: Boolean = false,
    onToggleComplete: () -> Unit,
    onTogglePin: () -> Unit = {},
    onDelete: () -> Unit = {},
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    var showContextMenu by remember { mutableStateOf(false) }

    // 长按上下文菜单
    DropdownMenu(
        expanded = showContextMenu,
        onDismissRequest = { showContextMenu = false }
    ) {
        if (isHistory) {
            DropdownMenuItem(
                text = { Text("取消完成") },
                onClick = {
                    showContextMenu = false
                    onToggleComplete()
                },
                leadingIcon = {
                    Icon(Icons.Default.Check, contentDescription = null)
                }
            )
            DropdownMenuItem(
                text = { Text(if (task.pinned) "取消置顶" else "置顶") },
                onClick = {
                    showContextMenu = false
                    onTogglePin()
                },
                leadingIcon = {
                    Icon(
                        Icons.Default.Star,
                        contentDescription = null,
                        tint = if (task.pinned) AppColors.Primary else AppColors.TextSecondary
                    )
                }
            )
        }
        DropdownMenuItem(
            text = { Text("删除", color = AppColors.Error) },
            onClick = {
                showContextMenu = false
                onDelete()
            },
            leadingIcon = {
                Icon(
                    Icons.Default.Edit,
                    contentDescription = null,
                    tint = AppColors.Error
                )
            }
        )
    }

    Card(
        modifier = modifier
            .fillMaxWidth()
            .combinedClickable(
                onClick = onClick,
                onLongClick = { showContextMenu = true }
            ),
        shape = RoundedCornerShape(12.dp),
        colors = CardDefaults.cardColors(
            containerColor = if (isOverdue) AppColors.OverdueBackground else AppColors.CardBackground
        ),
        border = if (isOverdue) BorderStroke(0.5.dp, AppColors.OverdueBorder) else null,
        elevation = CardDefaults.cardElevation(
            defaultElevation = if (isOverdue) 0.dp else 1.dp
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            // 完成勾选按钮
            Box(
                modifier = Modifier
                    .size(28.dp)
                    .clip(CircleShape)
                    .background(
                        if (task.isCompleted) AppColors.Success
                        else AppColors.getPriorityBgColor(task.priority)
                    )
                    .clip(CircleShape)
                    .combinedClickable(
                        onClick = onToggleComplete
                    ),
                contentAlignment = Alignment.Center
            ) {
                if (task.isCompleted) {
                    Icon(
                        imageVector = Icons.Default.Check,
                        contentDescription = "已完成",
                        tint = AppColors.Surface,
                        modifier = Modifier.size(16.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.width(12.dp))

            // 任务内容
            Column(
                modifier = Modifier.weight(1f)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    // 计划任务图标
                    if (task.isPlanned) {
                        Icon(
                            imageVector = Icons.Default.DateRange,
                            contentDescription = "计划任务",
                            tint = AppColors.PriorityPlan,
                            modifier = Modifier.size(16.dp)
                        )
                        Spacer(modifier = Modifier.width(4.dp))
                    }

                    // 优先级标签
                    PriorityChip(priority = task.priority)

                    Spacer(modifier = Modifier.width(8.dp))

                    // 任务标题
                    Text(
                        text = task.title,
                        style = MaterialTheme.typography.bodyLarge,
                        color = if (task.isCompleted) AppColors.TextSecondary
                               else if (isOverdue) AppColors.OverdueText
                               else AppColors.TextPrimary,
                        maxLines = 1,
                        overflow = TextOverflow.Ellipsis,
                        modifier = Modifier.weight(1f, fill = false)
                    )
                }

                // 内容预览
                if (task.content.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(2.dp))
                    Text(
                        text = task.content,
                        style = MaterialTheme.typography.bodySmall,
                        color = AppColors.TextTertiary,
                        maxLines = 2,
                        overflow = TextOverflow.Ellipsis
                    )
                }

                // 截止日期
                if (task.deadline.isNotEmpty()) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "截止: ${task.deadline}",
                        style = MaterialTheme.typography.bodySmall,
                        color = if (isOverdue) AppColors.OverdueText else AppColors.TextSecondary
                    )
                }
            }

            // 右侧信息
            Column(
                horizontalAlignment = Alignment.End
            ) {
                Text(
                    text = task.createdAt,
                    style = MaterialTheme.typography.bodySmall,
                    color = if (isNormalOverdue) AppColors.OverdueText else AppColors.TextTertiary
                )

                // 置顶图标（仅历史页面）
                if (isHistory && task.pinned) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Icon(
                        imageVector = Icons.Default.Star,
                        contentDescription = "已置顶",
                        tint = AppColors.Primary,
                        modifier = Modifier.size(16.dp)
                    )
                }
            }
        }
    }
}
