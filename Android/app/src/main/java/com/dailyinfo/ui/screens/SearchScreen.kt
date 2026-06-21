package com.dailyinfo.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.dailyinfo.data.Task
import com.dailyinfo.data.TaskManager
import com.dailyinfo.ui.components.EmptyState
import com.dailyinfo.ui.components.TaskItem
import com.dailyinfo.ui.theme.AppColors

/**
 * 搜索页面
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SearchScreen(
    initialQuery: String,
    onNavigateBack: () -> Unit,
    onNavigateToDetail: (String) -> Unit
) {
    val context = LocalContext.current
    val taskManager = remember { TaskManager(context) }
    var searchQuery by remember { mutableStateOf(initialQuery) }
    var searchResults by remember { mutableStateOf<List<Pair<String, Task>>>(emptyList()) }

    // 实时搜索
    LaunchedEffect(searchQuery) {
        if (searchQuery.isNotBlank()) {
            searchResults = taskManager.searchTasks(searchQuery)
        } else {
            searchResults = emptyList()
        }
    }

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
                            text = "搜索结果",
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
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // 搜索输入框
            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                label = { Text("搜索任务...") },
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                singleLine = true,
                shape = RoundedCornerShape(12.dp),
                trailingIcon = {
                    if (searchQuery.isNotBlank()) {
                        IconButton(onClick = { searchQuery = "" }) {
                            Icon(
                                imageVector = Icons.Default.Clear,
                                contentDescription = "清除"
                            )
                        }
                    }
                }
            )

            // 搜索结果统计
            if (searchQuery.isNotBlank()) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = AppColors.getPriorityBgColor(Task.PRIORITY_MEDIUM)
                    )
                ) {
                    Text(
                        text = "搜索: $searchQuery (${searchResults.size}条结果)",
                        style = MaterialTheme.typography.bodySmall,
                        color = AppColors.TextSecondary,
                        modifier = Modifier.padding(12.dp)
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // 搜索结果列表
            if (searchQuery.isBlank()) {
                EmptyState(
                    message = "请输入搜索关键词",
                    modifier = Modifier.padding(paddingValues)
                )
            } else if (searchResults.isEmpty()) {
                EmptyState(
                    message = "未找到匹配任务",
                    modifier = Modifier.padding(paddingValues)
                )
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(horizontal = 16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(searchResults) { (status, task) ->
                        TaskItem(
                            task = task,
                            isHistory = status == "completed",
                            onToggleComplete = {
                                if (status == "pending") {
                                    taskManager.completeTask(task.id)
                                } else {
                                    taskManager.uncompleteTask(task.id)
                                }
                                searchResults = taskManager.searchTasks(searchQuery)
                            },
                            onDelete = {
                                if (status == "pending") {
                                    taskManager.deleteTask(task.id)
                                } else {
                                    taskManager.deleteCompletedTask(task.id)
                                }
                                searchResults = taskManager.searchTasks(searchQuery)
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
}
