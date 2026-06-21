# AGENTS.md

本文档用于指导 Codex 在本仓库内工作。

当前项目版本：V3.1。

## 项目概述

Dailyinfo 是每日任务管理工具，支持 Windows 桌面端和 Android 移动端：

- **Windows 端**：PySide6 开发，界面采用无边框窗口、圆角容器、毛玻璃效果和自绘窗口控制按钮
- **Android 端**：Kotlin + Jetpack Compose 开发，采用 Material Design 3 设计规范
- **数据共享**：两端使用相同的 tasks.json 格式，支持本地 JSON 和远程 MySQL 双存储模式

## 基本约束

- 始终使用中文回复、中文文档和中文提交信息。
- 不要擅自修改用户配置文件，除非用户明确要求。
- 涉及删除、覆盖、批量移动等不可逆操作前，必须先确认。
- 不要执行可能损坏数据的操作，除非用户明确确认。
- 不要回退用户已有改动；遇到无关改动时保持原样。
- 文件路径在沟通中优先使用绝对路径。
- 所有 sql 相关语句、解释和语法统一使用小写。
- 不使用上标字符，平方写成 `x^2`，Python 代码写成 `x**2`。

## 目录结构

```text
Shared/                      # 跨平台共享目录
  ├── docs/ui_terms.md       # UI 术语对照表
  ├── calendar_utils.py      # 农历/节假日算法
  └── task_model.py          # 任务数据模型
Data/                        # 共享数据文件
Ico/                         # 共享图标资源
Windows/                     # Windows 端
  └── Code/daily_tasks.py    # 主程序
Android/                     # Android 端项目
Macos/                       # macOS 端（待开发）
Ios/                         # iOS 端（待开发）
```

## 常用命令

### Windows 端

```bash
python Windows/Code/daily_tasks.py
```

```bash
pip install PySide6 cryptography pymysql pyinstaller
```

```bash
cd Windows && python -m PyInstaller 每日任务管理.spec --clean
```

只运行本地 JSON 模式时，`pymysql` 和 `cryptography` 是可选依赖；涉及 MySQL 模式、密码加密或打包验证时需要补齐。

### Android 端

```bash
# 转换图标（需要 Pillow）
python Android/convert_icon.py
```

```bash
# 构建 APK（需要 Android SDK）
cd Android && ./gradlew assembleDebug
```

```bash
# 安装到设备
adb install Android/app/build/outputs/apk/debug/app-debug.apk
```

## 主要模块

- `TaskManager`：任务数据层，负责 JSON/MySQL 读取、保存、迁移、合并、添加、更新、完成、取消完成、删除、置顶和搜索任务。
- `TaskApp`：主窗口，负责待办页、搜索页、历史页、工具栏、日历弹窗、窗口拖动和缩放。
- `TaskDetailDialog`：任务详情页，负责任务编辑、保存、完成、删除和类型转换。
- `HolidayCalendar`：日历控件，负责日期绘制、节假日、节气、农历和调休上班日显示。
- `SettingsDialog`：设置弹窗，负责存储方式选择、MySQL 连接配置、连接测试和配置保存。
- `TaskHeaderView`：任务表头，负责远期计划任务显隐按钮绘制和交互。
- `WindowControlButton`：自绘窗口按钮，负责最小化、最大化、还原和关闭图标绘制。

## 数据和资源

- 任务数据：`Data/tasks.json`
- 存储配置：`Data/settings.json`
- 图标文件：`Ico/岚兮儿天下无敌好看.ico`
- 打包配置：`Windows/每日任务管理.spec`
- GitHub 跟踪文件不包含 `Data/`、`Windows/build/`、`Windows/dist/`、`*.spec` 和 `CLAUDE.md`，这些是本地数据或本地配置。
- 打包资源必须包含图标：

```python
datas=[('Ico/岚兮儿天下无敌好看.ico', 'Ico')]
```

打包后通过 `getattr(sys, 'frozen', False)` 区分开发环境和 exe 环境；图标资源从 `sys._MEIPASS` 读取，任务数据和配置保存在 exe 同级目录。

## V3.0 存储规则

- 默认使用 JSON 模式，任务数据保存在 `Data/tasks.json`。
- 设置弹窗保存的存储方式、MySQL 主机、端口、用户名、密码和数据库名保存在 `Data/settings.json`。
- MySQL 密码使用 `cryptography.fernet` 加密，加密密钥基于当前机器信息生成。
- 切换存储方式后需要重启应用生效。
- 存储方式变化时会合并 JSON 和 MySQL 两端任务，按任务 ID 去重，并保留较新的记录。
- MySQL 不可用时应保留 JSON 回退路径，避免启动和保存被网络问题卡住。
- sql 语句、sql 解释和 sql 语法说明统一使用小写。

## UI 维护原则

- UI 文本使用中文。
- 变量名和函数名使用英文。
- 注释用中文，且只解释不明显的逻辑。
- 控件圆角层级保持一致：大容器约 `10px`，普通按钮和输入框约 `8px`，小图标按钮约 `6px`。
- 按钮默认不接收键盘焦点，避免点击后出现虚线焦点框。
- 任务详情页打开后保留正文自动聚焦，方便立即编辑。
- 详情页关闭后不要强制聚焦输入框，避免视觉跳动。
- 设置弹窗、输入框和数据库配置表单的右键菜单使用中文。
- 修改设置弹窗、日历面板、截止日期弹窗、类型转换弹窗时，优先沿用无标题栏圆角弹窗样式。

## 页面和区块命名

统一命名参见：

```text
Shared/docs/ui_terms.md
```

修改界面时优先沿用该文档中的名称。
