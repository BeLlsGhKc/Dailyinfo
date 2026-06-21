package com.dailyinfo.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.dailyinfo.ui.screens.HistoryScreen
import com.dailyinfo.ui.screens.SearchScreen
import com.dailyinfo.ui.screens.TaskDetailScreen
import com.dailyinfo.ui.screens.TaskListScreen

/**
 * 导航路由定义
 */
object Routes {
    const val TASK_LIST = "task_list"
    const val HISTORY = "history"
    const val SEARCH = "search/{query}"
    const val TASK_DETAIL = "task_detail/{taskId}"

    fun search(query: String): String = "search/$query"
    fun taskDetail(taskId: String): String = "task_detail/$taskId"
}

/**
 * 导航图
 */
@Composable
fun DailyinfoNavGraph(navController: NavHostController) {
    NavHost(
        navController = navController,
        startDestination = Routes.TASK_LIST
    ) {
        // 待办任务页面
        composable(Routes.TASK_LIST) {
            TaskListScreen(
                onNavigateToHistory = {
                    navController.navigate(Routes.HISTORY)
                },
                onNavigateToDetail = { taskId ->
                    navController.navigate(Routes.taskDetail(taskId))
                }
            )
        }

        // 历史页面
        composable(Routes.HISTORY) {
            HistoryScreen(
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateToDetail = { taskId ->
                    navController.navigate(Routes.taskDetail(taskId))
                }
            )
        }

        // 搜索页面
        composable(
            route = Routes.SEARCH,
            arguments = listOf(
                navArgument("query") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val query = backStackEntry.arguments?.getString("query") ?: ""
            SearchScreen(
                initialQuery = query,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateToDetail = { taskId ->
                    navController.navigate(Routes.taskDetail(taskId))
                }
            )
        }

        // 任务详情页面
        composable(
            route = Routes.TASK_DETAIL,
            arguments = listOf(
                navArgument("taskId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val taskId = backStackEntry.arguments?.getString("taskId") ?: ""
            TaskDetailScreen(
                taskId = taskId,
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
    }
}
