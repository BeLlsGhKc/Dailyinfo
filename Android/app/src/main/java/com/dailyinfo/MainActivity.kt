package com.dailyinfo

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.compose.rememberNavController
import com.dailyinfo.ui.navigation.DailyinfoNavGraph
import com.dailyinfo.ui.theme.DailyinfoTheme

/**
 * 主 Activity
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            DailyinfoTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    DailyinfoApp()
                }
            }
        }
    }
}

/**
 * 应用入口
 */
@Composable
fun DailyinfoApp() {
    val navController = rememberNavController()
    DailyinfoNavGraph(navController = navController)
}
