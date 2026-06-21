package com.dailyinfo.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.input.pointer.pointerInput
import com.dailyinfo.data.Task
import com.dailyinfo.data.TaskManager
import com.dailyinfo.ui.components.EmptyState
import com.dailyinfo.ui.components.TaskItem
import com.dailyinfo.ui.theme.AppColors
import kotlinx.datetime.Instant
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime

/**
 * 待办任务页面
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TaskListScreen(
    onNavigateToHistory: () -> Unit,
    onNavigateToDetail: (String) -> Unit
) {
    val context = LocalContext.current
    val taskManager = remember { TaskManager(context) }
    var tasks by remember { mutableStateOf(taskManager.tasks) }
    var inputText by remember { mutableStateOf("") }
    var selectedPriority by remember { mutableStateOf(Task.PRIORITY_PLAN) }
    var showDatePicker by remember { mutableStateOf(false) }
    var pendingPlanTitle by remember { mutableStateOf<String?>(null) }
    var hideFuturePlan by remember { mutableStateOf(true) }
    var isSearchMode by remember { mutableStateOf(false) }
    var searchQuery by remember { mutableStateOf("") }
    var searchResults by remember { mutableStateOf<List<Pair<String, com.dailyinfo.data.Task>>>(emptyList()) }

    fun refresh() {
        taskManager.refresh()
        tasks = taskManager.tasks
    }

    fun toggleFuturePlanVisibility() {
        hideFuturePlan = !hideFuturePlan
    }

    // 排序后的任务列表 - 每次重组时重新计算
    val sortedTasks = taskManager.sortPendingTasks(hideFuturePlan)
    val hiddenFuturePlanCount = taskManager.getFuturePlanCount()

    // 搜索过滤后的任务
    val displayTasks = if (isSearchMode && searchQuery.isNotBlank()) {
        sortedTasks.filter { task ->
            task.title.contains(searchQuery, ignoreCase = true) ||
                task.content.contains(searchQuery, ignoreCase = true)
        }
    } else {
        sortedTasks
    }

    // 实时搜索
    LaunchedEffect(searchQuery) {
        if (searchQuery.isNotBlank()) {
            searchResults = taskManager.searchTasks(searchQuery)
        } else {
            searchResults = emptyList()
        }
    }

    // 日期选择对话框
    if (showDatePicker) {
        val datePickerState = rememberDatePickerState()
        DatePickerDialog(
            onDismissRequest = {
                showDatePicker = false
                pendingPlanTitle = null
            },
            confirmButton = {
                TextButton(onClick = {
                    datePickerState.selectedDateMillis?.let { millis ->
                        val instant = Instant.fromEpochMilliseconds(millis)
                        val localDate = instant.toLocalDateTime(TimeZone.UTC).date
                        pendingPlanTitle?.let { title ->
                            taskManager.addTask(
                                title = title,
                                priority = Task.PRIORITY_PLAN,
                                taskType = Task.TASK_TYPE_PLANNED,
                                deadline = localDate.toString()
                            )
                            inputText = ""
                        }
                    }
                    showDatePicker = false
                    pendingPlanTitle = null
                    refresh()
                }) {
                    Text("确定")
                }
            },
            dismissButton = {
                TextButton(onClick = {
                    showDatePicker = false
                    pendingPlanTitle = null
                }) {
                    Text("取消")
                }
            }
        ) {
            DatePicker(state = datePickerState)
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Column {
                            Text(
                                text = "Dailyinfo",
                                style = MaterialTheme.typography.headlineSmall
                            )
                            Text(
                                text = "待办任务",
                                style = MaterialTheme.typography.bodyMedium,
                                color = AppColors.TextSecondary
                            )
                        }
                        Spacer(
                            modifier = Modifier
                                .weight(1f)
                                .height(56.dp)
                                .pointerInput(hideFuturePlan) {
                                    detectTapGestures(
                                        onDoubleTap = { toggleFuturePlanVisibility() }
                                    )
                                }
                        )
                    }
                },
                actions = {
                    TextButton(onClick = onNavigateToHistory) {
                        Text("历史")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = AppColors.Background
                )
            )
        },
        bottomBar = {
            // 底部状态栏
            val stats = taskManager.getStats()
            Surface(
                modifier = Modifier.fillMaxWidth(),
                color = AppColors.Surface,
                shadowElevation = 4.dp
            ) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp, vertical = 12.dp),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = "待办 ${stats.first} · 今日完成 ${stats.second} · 历史 ${stats.third}",
                        style = MaterialTheme.typography.bodySmall,
                        color = AppColors.TextSecondary
                    )
                }
            }
        },
        floatingActionButton = {
            FloatingActionButton(
                onClick = {
                    val title = inputText.trim()
                    if (title.isNotBlank()) {
                        if (selectedPriority == Task.PRIORITY_PLAN) {
                            pendingPlanTitle = title
                            showDatePicker = true
                        } else {
                            taskManager.addTask(
                                title = title,
                                priority = selectedPriority,
                                taskType = Task.TASK_TYPE_NORMAL
                            )
                            inputText = ""
                            refresh()
                        }
                    }
                },
                containerColor = AppColors.Primary,
                contentColor = AppColors.Surface
            ) {
                Icon(
                    imageVector = Icons.Default.Add,
                    contentDescription = "添加任务"
                )
            }
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            // 输入区域
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp),
                colors = CardDefaults.cardColors(
                    containerColor = AppColors.Surface
                )
            ) {
                Column(
                    modifier = Modifier.padding(16.dp)
                ) {
                    // 输入框
                    OutlinedTextField(
                        value = inputText,
                        onValueChange = { inputText = it },
                        label = { Text("输入任务标题...") },
                        modifier = Modifier.fillMaxWidth(),
                        singleLine = true,
                        shape = RoundedCornerShape(12.dp),
                        trailingIcon = {
                            if (inputText.isNotBlank()) {
                                IconButton(onClick = {
                                    isSearchMode = !isSearchMode
                                    searchQuery = inputText
                                }) {
                                    Icon(
                                        imageVector = Icons.Default.Search,
                                        contentDescription = "搜索",
                                        tint = if (isSearchMode) AppColors.Primary else AppColors.TextSecondary
                                    )
                                }
                            }
                        }
                    )

                    Spacer(modifier = Modifier.height(8.dp))

                    // 优先级选择
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Task.PRIORITY_LIST.forEach { priority ->
                            FilterChip(
                                selected = selectedPriority == priority,
                                onClick = { selectedPriority = priority },
                                label = {
                                    Text(
                                        text = priority,
                                        modifier = Modifier.fillMaxWidth(),
                                        textAlign = TextAlign.Center
                                    )
                                },
                                modifier = Modifier.weight(1f).padding(horizontal = 4.dp),
                                colors = FilterChipDefaults.filterChipColors(
                                    selectedContainerColor = AppColors.getPriorityBgColor(priority),
                                    selectedLabelColor = AppColors.getPriorityColor(priority)
                                )
                            )
                        }
                    }
                }
            }

            // 搜索模式提示
            if (isSearchMode && searchQuery.isNotBlank()) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = AppColors.getPriorityBgColor(Task.PRIORITY_MEDIUM)
                    )
                ) {
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "搜索: $searchQuery (${displayTasks.size}条结果)",
                            style = MaterialTheme.typography.bodySmall,
                            color = AppColors.TextSecondary
                        )
                        TextButton(
                            onClick = {
                                isSearchMode = false
                                searchQuery = ""
                            }
                        ) {
                            Text("清除", style = MaterialTheme.typography.labelMedium)
                        }
                    }
                }
            }

            // 任务列表
            if (displayTasks.isEmpty()) {
                if (isSearchMode && searchQuery.isNotBlank()) {
                    EmptyState(message = "未找到匹配任务")
                } else if (tasks.pending.isEmpty()) {
                    EmptyState(message = "暂无待办任务")
                } else if (hideFuturePlan && hiddenFuturePlanCount > 0 && sortedTasks.isEmpty()) {
                    EmptyState(message = "6天外计划任务已隐藏")
                } else {
                    EmptyState(message = "暂无待办任务")
                }
            } else {
                LazyColumn(
                    modifier = Modifier.fillMaxSize(),
                    contentPadding = PaddingValues(
                        start = 16.dp,
                        top = 12.dp,
                        end = 16.dp
                    ),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    items(displayTasks) { task ->
                        val isOverdue = taskManager.isTaskOverdue(task)
                        val isNormalOverdue = taskManager.isNormalTaskOverdue(task)

                        TaskItem(
                            task = task,
                            isOverdue = isOverdue,
                            isNormalOverdue = isNormalOverdue,
                            onToggleComplete = {
                                taskManager.completeTask(task.id)
                                refresh()
                            },
                            onDelete = {
                                taskManager.deleteTask(task.id)
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
}
