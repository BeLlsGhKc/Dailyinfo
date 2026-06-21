package com.dailyinfo.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Star
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.dailyinfo.data.Task
import com.dailyinfo.data.TaskManager
import com.dailyinfo.ui.components.PriorityChip
import com.dailyinfo.ui.theme.AppColors
import kotlinx.datetime.Instant
import kotlinx.datetime.TimeZone
import kotlinx.datetime.toLocalDateTime

/**
 * 任务详情页面
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TaskDetailScreen(
    taskId: String,
    onNavigateBack: () -> Unit
) {
    val context = LocalContext.current
    val taskManager = remember { TaskManager(context) }
    var task by remember { mutableStateOf<Task?>(null) }
    var isEditing by remember { mutableStateOf(false) }
    var editTitle by remember { mutableStateOf("") }
    var editContent by remember { mutableStateOf("") }
    var editDeadline by remember { mutableStateOf("") }
    var editPriority by remember { mutableStateOf(Task.PRIORITY_MEDIUM) }

    // 类型转换相关状态
    var showTypeConversionDialog by remember { mutableStateOf(false) }
    var conversionType by remember { mutableStateOf("") } // "toNormal" or "toPlan"
    var showConversionDatePicker by remember { mutableStateOf(false) }
    var conversionPriority by remember { mutableStateOf(Task.PRIORITY_HIGH) }

    // 加载任务
    LaunchedEffect(taskId) {
        taskManager.refresh()
        task = taskManager.tasks.pending.find { it.id == taskId }
            ?: taskManager.tasks.completed.find { it.id == taskId }
        task?.let {
            editTitle = it.title
            editContent = it.content
            editDeadline = it.deadline
            editPriority = it.priority
        }
    }

    // 保存修改
    fun saveChanges() {
        task?.let {
            taskManager.updateTask(
                it.id,
                mapOf(
                    "title" to editTitle,
                    "content" to editContent,
                    "deadline" to editDeadline,
                    "priority" to editPriority
                )
            )
            taskManager.refresh()
            task = taskManager.tasks.pending.find { t -> t.id == taskId }
                ?: taskManager.tasks.completed.find { t -> t.id == taskId }
            isEditing = false
        }
    }

    // 类型转换日期选择对话框
    if (showConversionDatePicker) {
        val datePickerState = rememberDatePickerState()
        DatePickerDialog(
            onDismissRequest = { showConversionDatePicker = false },
            confirmButton = {
                TextButton(onClick = {
                    datePickerState.selectedDateMillis?.let { millis ->
                        val instant = Instant.fromEpochMilliseconds(millis)
                        val localDate = instant.toLocalDateTime(TimeZone.UTC).date
                        task?.let {
                            taskManager.updateTask(
                                it.id,
                                mapOf(
                                    "type" to Task.TASK_TYPE_PLANNED,
                                    "priority" to Task.PRIORITY_PLAN,
                                    "deadline" to localDate.toString()
                                )
                            )
                            taskManager.refresh()
                            task = taskManager.tasks.pending.find { t -> t.id == taskId }
                                ?: taskManager.tasks.completed.find { t -> t.id == taskId }
                            editDeadline = localDate.toString()
                            editPriority = Task.PRIORITY_PLAN
                        }
                    }
                    showConversionDatePicker = false
                }) {
                    Text("确定")
                }
            },
            dismissButton = {
                TextButton(onClick = { showConversionDatePicker = false }) {
                    Text("取消")
                }
            }
        ) {
            DatePicker(state = datePickerState)
        }
    }

    // 类型转换对话框
    if (showTypeConversionDialog) {
        AlertDialog(
            onDismissRequest = { showTypeConversionDialog = false },
            title = { Text("类型转换") },
            text = {
                if (conversionType == "toNormal") {
                    // 计划任务 -> 普通任务：选择优先级
                    Column {
                        Text(
                            text = "选择优先级",
                            style = MaterialTheme.typography.bodyMedium,
                            color = AppColors.TextSecondary
                        )
                        Spacer(modifier = Modifier.height(12.dp))
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceEvenly
                        ) {
                            listOf(Task.PRIORITY_HIGH, Task.PRIORITY_MEDIUM, Task.PRIORITY_LOW).forEach { priority ->
                                FilterChip(
                                    selected = conversionPriority == priority,
                                    onClick = { conversionPriority = priority },
                                    label = { Text(priority) },
                                    colors = FilterChipDefaults.filterChipColors(
                                        selectedContainerColor = AppColors.getPriorityBgColor(priority),
                                        selectedLabelColor = AppColors.getPriorityColor(priority)
                                    )
                                )
                            }
                        }
                    }
                } else {
                    // 普通任务 -> 计划任务：选择截止日期
                    Text(
                        text = "点击下方按钮选择截止日期",
                        style = MaterialTheme.typography.bodyMedium,
                        color = AppColors.TextSecondary
                    )
                }
            },
            confirmButton = {
                TextButton(onClick = {
                    if (conversionType == "toNormal") {
                        // 转为普通任务
                        task?.let {
                            taskManager.updateTask(
                                it.id,
                                mapOf(
                                    "type" to Task.TASK_TYPE_NORMAL,
                                    "priority" to conversionPriority,
                                    "deadline" to ""
                                )
                            )
                            taskManager.refresh()
                            task = taskManager.tasks.pending.find { t -> t.id == taskId }
                                ?: taskManager.tasks.completed.find { t -> t.id == taskId }
                            task?.let { t ->
                                editPriority = t.priority
                                editDeadline = t.deadline
                            }
                        }
                        showTypeConversionDialog = false
                    } else {
                        // 转为计划任务：打开日期选择器
                        showTypeConversionDialog = false
                        showConversionDatePicker = true
                    }
                }) {
                    Text("确定")
                }
            },
            dismissButton = {
                TextButton(onClick = { showTypeConversionDialog = false }) {
                    Text("取消")
                }
            }
        )
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = if (isEditing) "编辑任务" else "任务详情",
                        style = MaterialTheme.typography.headlineSmall
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            imageVector = Icons.Default.ArrowBack,
                            contentDescription = "返回"
                        )
                    }
                },
                actions = {
                    if (!isEditing && task != null) {
                        // 置顶按钮（仅已完成任务）
                        if (task!!.isCompleted) {
                            IconButton(onClick = {
                                taskManager.togglePinTask(taskId)
                                taskManager.refresh()
                                task = taskManager.tasks.completed.find { it.id == taskId }
                            }) {
                                Icon(
                                    imageVector = Icons.Default.Star,
                                    contentDescription = if (task!!.pinned) "取消置顶" else "置顶",
                                    tint = if (task!!.pinned) AppColors.Primary else AppColors.TextSecondary
                                )
                            }
                        }

                        // 删除按钮
                        IconButton(onClick = {
                            if (task!!.isCompleted) {
                                taskManager.deleteCompletedTask(taskId)
                            } else {
                                taskManager.deleteTask(taskId)
                            }
                            onNavigateBack()
                        }) {
                            Icon(
                                imageVector = Icons.Default.Delete,
                                contentDescription = "删除",
                                tint = AppColors.Error
                            )
                        }
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = AppColors.Background
                )
            )
        }
    ) { paddingValues ->
        task?.let { currentTask ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp)
            ) {
                // 任务状态卡片
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = AppColors.Surface
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            PriorityChip(priority = currentTask.priority)

                            Column {
                                Text(
                                    text = if (currentTask.isCompleted) "已完成" else "待办",
                                    style = MaterialTheme.typography.labelLarge,
                                    color = if (currentTask.isCompleted) AppColors.Success else AppColors.Warning
                                )
                                Text(
                                    text = if (currentTask.isPlanned) "计划任务" else "普通任务",
                                    style = MaterialTheme.typography.bodySmall,
                                    color = AppColors.TextSecondary
                                )
                            }
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        if (isEditing) {
                            OutlinedTextField(
                                value = editTitle,
                                onValueChange = { editTitle = it },
                                label = { Text("标题") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true
                            )
                        } else {
                            Text(
                                text = currentTask.title,
                                style = MaterialTheme.typography.titleLarge,
                                color = AppColors.TextPrimary
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // 详细信息卡片
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = AppColors.Surface
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp)
                    ) {
                        Text(
                            text = "详细信息",
                            style = MaterialTheme.typography.titleMedium,
                            color = AppColors.TextPrimary
                        )

                        Spacer(modifier = Modifier.height(12.dp))

                        // 内容
                        if (isEditing) {
                            OutlinedTextField(
                                value = editContent,
                                onValueChange = { editContent = it },
                                label = { Text("内容") },
                                modifier = Modifier.fillMaxWidth(),
                                minLines = 3
                            )
                        } else {
                            Text(
                                text = if (currentTask.content.isNotEmpty()) currentTask.content else "无内容",
                                style = MaterialTheme.typography.bodyMedium,
                                color = if (currentTask.content.isNotEmpty()) AppColors.TextPrimary else AppColors.TextTertiary
                            )
                        }

                        Spacer(modifier = Modifier.height(12.dp))

                        // 截止日期
                        if (isEditing && currentTask.isPlanned) {
                            OutlinedTextField(
                                value = editDeadline,
                                onValueChange = { editDeadline = it },
                                label = { Text("截止日期 (YYYY-MM-DD)") },
                                modifier = Modifier.fillMaxWidth(),
                                singleLine = true
                            )
                        } else {
                            DetailRow(
                                label = "截止日期",
                                value = if (currentTask.deadline.isNotEmpty()) currentTask.deadline else "无"
                            )
                        }

                        Spacer(modifier = Modifier.height(8.dp))

                        // 创建时间
                        DetailRow(
                            label = "创建时间",
                            value = currentTask.createdAt
                        )

                        // 完成时间
                        if (currentTask.completedAt != null) {
                            Spacer(modifier = Modifier.height(8.dp))
                            DetailRow(
                                label = "完成时间",
                                value = currentTask.completedAt
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(16.dp))

                // 优先级选择（编辑模式）
                if (isEditing) {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = AppColors.Surface
                        )
                    ) {
                        Column(
                            modifier = Modifier.padding(16.dp)
                        ) {
                            Text(
                                text = "优先级",
                                style = MaterialTheme.typography.titleMedium,
                                color = AppColors.TextPrimary
                            )

                            Spacer(modifier = Modifier.height(8.dp))

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceEvenly
                            ) {
                                Task.PRIORITY_LIST.forEach { priority ->
                                    FilterChip(
                                        selected = editPriority == priority,
                                        onClick = { editPriority = priority },
                                        label = { Text(priority) },
                                        colors = FilterChipDefaults.filterChipColors(
                                            selectedContainerColor = AppColors.getPriorityBgColor(priority),
                                            selectedLabelColor = AppColors.getPriorityColor(priority)
                                        )
                                    )
                                }
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(16.dp))
                }

                // 操作按钮
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    if (isEditing) {
                        // 取消按钮
                        OutlinedButton(
                            onClick = {
                                isEditing = false
                                editTitle = currentTask.title
                                editContent = currentTask.content
                                editDeadline = currentTask.deadline
                                editPriority = currentTask.priority
                            },
                            modifier = Modifier.weight(1f)
                        ) {
                            Text("取消")
                        }

                        // 保存按钮
                        Button(
                            onClick = { saveChanges() },
                            modifier = Modifier.weight(1f),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = AppColors.Primary
                            )
                        ) {
                            Text("保存")
                        }
                    } else {
                        // 编辑按钮
                        Button(
                            onClick = { isEditing = true },
                            modifier = Modifier.weight(1f),
                            colors = ButtonDefaults.buttonColors(
                                containerColor = AppColors.Primary
                            )
                        ) {
                            Text("编辑")
                        }

                        // 类型转换按钮
                        OutlinedButton(
                            onClick = {
                                conversionType = if (currentTask.isPlanned) "toNormal" else "toPlan"
                                showTypeConversionDialog = true
                            },
                            modifier = Modifier.weight(1f)
                        ) {
                            Text(
                                text = if (currentTask.isPlanned) "转普通" else "转计划",
                                style = MaterialTheme.typography.labelMedium
                            )
                        }

                        // 完成/取消完成按钮
                        if (currentTask.isCompleted) {
                            OutlinedButton(
                                onClick = {
                                    taskManager.uncompleteTask(taskId)
                                    taskManager.refresh()
                                    task = taskManager.tasks.completed.find { it.id == taskId }
                                        ?: taskManager.tasks.pending.find { it.id == taskId }
                                },
                                modifier = Modifier.weight(1f)
                            ) {
                                Text("取消完成")
                            }
                        } else {
                            Button(
                                onClick = {
                                    taskManager.completeTask(taskId)
                                    taskManager.refresh()
                                    task = taskManager.tasks.completed.find { it.id == taskId }
                                },
                                modifier = Modifier.weight(1f),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = AppColors.Success
                                )
                            ) {
                                Text("完成")
                            }
                        }
                    }
                }
            }
        } ?: run {
            // 任务未找到
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(paddingValues)
            ) {
                Text(
                    text = "任务未找到",
                    style = MaterialTheme.typography.bodyLarge,
                    color = AppColors.TextSecondary,
                    modifier = Modifier.padding(16.dp)
                )
            }
        }
    }
}

/**
 * 详情行组件
 */
@Composable
private fun DetailRow(
    label: String,
    value: String
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = AppColors.TextSecondary
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyMedium,
            color = AppColors.TextPrimary
        )
    }
}
