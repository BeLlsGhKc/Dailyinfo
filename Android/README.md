# Dailyinfo Android 端

Kotlin + Jetpack Compose 实现的安卓端每日任务管理工具。

## 当前状态

app 可以运行，基本功能完整。

## 已完成功能

- ✅ 主页面：输入框 + 搜索按钮 + 优先级选择（计划/高/中/低）+ 添加任务
- ✅ 计划任务：选"计划"后添加，自动弹出日期选择器
- ✅ 任务列表：显示待办，可点击完成
- ✅ 历史页面：已完成任务，可取消完成/置顶
- ✅ 搜索页面：从主页面输入框传关键词，显示结果
- ✅ 任务详情：查看/编辑/删除/完成
- ✅ 本地 JSON 存储

## 待优化

- 🔲 图标资源（还没转换 Ico → PNG）
- 🔲 MySQL 远程存储支持
- 🔲 任务排序逻辑（过期/今天/远期分组）
- 🔲 设置页面
- 🔲 通知/提醒功能

## 项目结构

```
Android/
├── app/src/main/java/com/dailyinfo/
│   ├── data/
│   │   ├── Task.kt              # 数据模型
│   │   └── TaskManager.kt       # 任务管理（JSON 读写）
│   ├── calendar/
│   │   ├── HolidayData.kt       # 节假日数据
│   │   ├── LunarCalendar.kt     # 农历转换
│   │   └── CalendarUtils.kt     # 日历工具
│   ├── ui/
│   │   ├── theme/               # 配色、主题、字体
│   │   ├── screens/             # 页面
│   │   ├── components/          # 组件
│   │   └── navigation/          # 导航
│   └── MainActivity.kt
├── build.gradle.kts
└── gradle.properties
```

## 常用命令

```bash
# 转换图标（需要 Pillow）
python Android/convert_icon.py

# 构建 APK
cd Android && ./gradlew assembleDebug

# 安装到设备
adb install app/build/outputs/apk/debug/app-debug.apk
```

## 注意事项

- 中文路径问题：`gradle.properties` 中 `android.overridePathCheck=true`
- Gradle 下载：`gradle-wrapper.properties` 用腾讯镜像
- 依赖下载：`settings.gradle.kts` 用阿里云镜像
- 数据格式：与 Windows 端 `tasks.json` 完全一致
