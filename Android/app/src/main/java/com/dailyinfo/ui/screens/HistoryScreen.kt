package com.dailyinfo.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.dailyinfo.data.TaskManager
import com.dailyinfo.ui.components.EmptyState
import com.dailyinfo.ui.components.TaskItem
import com.dailyinfo.ui.theme.AppColors

/**
 * 历史页面
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HistoryScreen(
    onNavigateBack: () -> Unit,
    onNavigateToDetail: (String) -> Unit
) {
    val context = LocalContext.current
    val taskManager = remember { TaskManager(context) }
    var tasks by remember { mutableStateOf(taskManager.tasks) }

    fun refresh() {
        taskManager.refresh()
        tasks = taskManager.tasks
    }

    val sortedTasks = tasks.completed.sortedWith(
        compareByDescending<com.dailyinfo.data.Task> { it.pinned }
            .thenByDescending { it.completedAt }
    )

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "Dailyinfo",
                            style = MaterialTheme.typography.headlineSmall
                        )
                        Text(
                            text = "已完成任务",
                            style = MaterialTheme.typography.bodyMedium,
                            color = AppColors.TextSecondary
                        )
                    }
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "返回"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = AppColors.Background
                )
            )
        }
    ) { paddingValues ->
        if (sortedTasks.isEmpty()) {
            EmptyState(
                message = "暂无历史任务",
                modifier = Modifier.padding(paddingValues)
            )
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(sortedTasks) { task ->
                    TaskItem(
                        task = task,
                        isHistory = true,
                        onToggleComplete = {
                            taskManager.uncompleteTask(task.id)
                            refresh()
                        },
                        onTogglePin = {
                            taskManager.togglePinTask(task.id)
                            refresh()
                        },
                        onDelete = {
                            taskManager.deleteCompletedTask(task.id)
                            refresh()
                        },
                        onClick = {
                            onNavigateToDetail(task.id)
                        }
                    )
                }
            }
        }
    }
}
