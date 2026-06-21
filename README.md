# Dailyinfo V3.0

> 每日任务管理工具 | Windows + Android 双端支持

Dailyinfo 是一款轻量级的每日任务管理工具，支持 Windows 桌面端和 Android 移动端。Windows 端采用 PySide6 构建，界面设计灵感来自 macOS 毛玻璃风格；Android 端采用 Kotlin + Jetpack Compose 构建，提供原生 Material Design 体验。两端共享数据格式，支持本地 JSON 和远程 MySQL 双存储模式。

## 功能特性

### 任务管理
- 创建、编辑、完成、取消完成、删除任务
- 四种优先级：计划、高、中、低
- 支持截止日期设置，过期任务自动高亮
- 任务详情弹窗，支持编辑标题、内容、状态和类型
- 全局搜索，快速定位待办和历史任务
- 历史任务支持右键置顶，重要完成记录可固定在前面
- 计划任务支持远期任务显隐切换，减少主页面干扰

### 日历功能
- 内置日历控件，支持农历显示
- 干支年、二十四节气标注
- 常见节日、中国法定节假日高亮
- 调休上班日特殊标记

### 数据存储
- **JSON 模式**：数据保存在本地文件，无需额外配置
- **MySQL 模式**：数据保存在远程数据库，支持多设备同步(需要自己准备云端数据库)
- 存储方式一键切换，数据自动合并
- MySQL 密码加密存储，绑定当前机器
- 异步数据库操作，界面响应流畅
- MySQL 连接失败时自动回退本地 JSON，避免启动流程被网络问题阻塞

### 界面设计
- Windows 无边框窗口
- 毛玻璃背景效果
- 圆角容器和阴影
- 自绘窗口控制按钮
- 响应式布局，支持窗口最大化
- 输入框和设置页支持中文右键菜单

## 快速开始

### 环境要求

- Python 3.8+
- Windows 10/11

### 安装依赖

```bash
pip install PySide6 cryptography pymysql pyinstaller
```

如果只使用本地 JSON 模式，`pymysql` 和 `cryptography` 可暂时不安装；切换 MySQL 模式时建议补齐这两个依赖。

### 运行程序

```bash
python Code/daily_tasks.py
```

### 打包为可执行文件

```bash
python -m PyInstaller 每日任务管理.spec --clean
```

打包完成后，可执行文件位于 `dist/Dailyinfo.exe`。打包配置文件为本地打包资源，默认不提交到仓库。

## 配置说明

### 存储模式

程序启动后，点击设置按钮可切换存储模式：

- **JSON 模式**：数据保存在 `Data/tasks.json`，适合单机使用
- **MySQL 模式**：数据保存在远程 MySQL 数据库，适合多设备同步
- **配置文件**：存储方式和数据库配置保存在 `Data/settings.json`
- **切换生效**：保存设置后需要重启应用，新存储方式才会生效

### MySQL 配置

切换到 MySQL 模式时，需要配置以下信息：

| 配置项 | 说明 |
|--------|------|
| 主机地址 | MySQL 服务器地址 |
| 端口 | MySQL 服务端口，默认 3306 |
| 用户名 | 数据库用户名 |
| 密码 | 数据库密码（加密存储） |
| 数据库名 | 目标数据库名称 |

### 数据安全

- MySQL 密码使用 Fernet 对称加密算法加密
- 加密密钥基于当前机器信息生成，配置文件仅在本机可用
- 数据库连接支持超时设置，避免网络问题导致程序卡顿
- 测试连接会自动创建目标数据库，任务表由应用启动或首次连接时自动创建
- 切换存储方式时会合并两端数据，按任务 ID 去重并保留较新的记录

## 项目结构

```text
Dailyinfo/
├── Shared/                       # 跨平台共享目录
│   ├── docs/
│   │   └── ui_terms.md           # UI 术语对照表
│   ├── calendar_utils.py         # 农历/节假日算法
│   ├── task_model.py             # 任务数据模型
│   └── README.md                 # 共享目录说明
├── Data/                         # 共享数据文件
│   ├── tasks.json                # JSON 模式任务数据
│   └── settings.json             # 存储配置
├── Ico/                          # 共享图标资源
│   └── 岚兮儿天下无敌好看.ico
├── Windows/                      # Windows 端
│   ├── Code/
│   │   └── daily_tasks.py        # 主程序代码
│   ├── go.vbs                    # 静默启动脚本
│   ├── 每日任务管理.spec          # PyInstaller 打包配置
│   ├── build/                    # 构建缓存
│   └── dist/                     # 打包输出
├── Android/                      # Android 端
│   ├── app/src/main/
│   │   ├── java/com/dailyinfo/   # Kotlin 源码
│   │   └── res/                  # 资源文件
│   ├── build.gradle.kts          # Gradle 构建配置
│   └── convert_icon.py           # 图标转换脚本
├── Macos/                        # macOS 端（待开发）
├── Ios/                          # iOS 端（待开发）
├── README.md                     # 项目说明文档
├── AGENTS.md                     # AI 代理协作说明
└── CLAUDE.md                     # 本地协作配置
```

## 技术架构

### 核心模块

| 模块 | 职责 |
|------|------|
| `TaskManager` | 任务数据管理，支持 JSON 和 MySQL 双存储 |
| `TaskApp` | 主窗口，包含任务列表、搜索、历史页、日历入口 |
| `TaskDetailDialog` | 任务详情弹窗，支持编辑和状态变更 |
| `HolidayCalendar` | 自定义日历控件，负责日期绘制和节日显示 |
| `SettingsDialog` | 设置弹窗，配置存储方式和数据库连接 |
| `TaskHeaderView` | 自定义任务表头，负责远期计划显隐按钮绘制和交互 |
| `WindowControlButton` | 自绘窗口控制按钮，负责最小化、最大化、还原和关闭图标 |

### 技术栈

#### Windows 端
- **UI 框架**：PySide6 (Qt for Python)
- **打包工具**：PyInstaller
- **窗口效果**：Windows Desktop Window Manager API
- **数据库**：PyMySQL（可选）
- **加密**：cryptography (Fernet)

#### Android 端
- **开发语言**：Kotlin
- **UI 框架**：Jetpack Compose
- **设计规范**：Material Design 3
- **JSON 解析**：Gson
- **日期时间**：kotlinx-datetime

### 性能优化

- 延迟数据库连接：启动时使用 JSON 模式，首次操作 MySQL 时才建立连接
- 异步操作：数据库读写在后台线程执行，不阻塞 UI
- 增量更新：单条记录操作，避免全量同步
- 本地回退：MySQL 不可用时保留 JSON 保存路径，降低数据丢失风险

## 开发指南

### 代码规范

- 使用中文注释
- 遵循 PEP 8 代码风格
- 变量名、函数名、类名使用英文

### 调试模式

开发环境下，数据保存在项目目录的 `Data/` 文件夹。可通过以下方式启用调试输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 打包注意事项

- 打包前确保 `Ico/岚兮儿天下无敌好看.ico` 文件存在
- 打包配置中已包含所有必要依赖
- 生成的 exe 文件为单文件，包含所有资源

## 更新日志

### V3.1 (2026-06-13)

**新功能**
- 新增 Android 移动端，采用 Kotlin + Jetpack Compose
- 新增 Shared 目录，提取共享逻辑作为 Kotlin 实现参考
- Android 端支持任务 CRUD、搜索、历史、详情编辑
- Android 端内置农历、节假日、节气显示
- 新增图标转换脚本，支持自动生成多尺寸 PNG

**架构优化**
- 项目结构调整为 Windows + Android 双端架构
- 数据格式保持一致，两端可共享 tasks.json
- .gitignore 更新，排除 Android 构建产物

### V3.0 (2026-06-13)

**新功能**
- 新增 MySQL 存储模式，支持远程数据库
- 新增设置弹窗，可配置数据库连接
- 存储方式切换时自动合并数据，避免数据丢失
- MySQL 密码加密存储，绑定当前机器
- 新增连接测试，支持自动创建目标数据库
- 新增历史任务右键置顶和远期计划任务显隐控制

**性能优化**
- 延迟数据库连接，启动速度提升
- 异步数据库操作，界面响应更流畅
- 增量更新单条记录，操作效率提升
- MySQL 异常时回退本地 JSON 保存，减少网络问题对日常使用的影响

**文档同步**
- README、UI 命名规范和 AI 协作文档统一跟进到 V3.0
- 明确本地生成文件和 GitHub 跟踪文件的边界

### V2.5.1 (2026-06-12)

- 优化按钮焦点残影问题
- 优化任务详情关闭后的焦点回落
- 重做日历弹窗样式，去掉原生标题栏
- 增加农历、二十四节气、常见节日显示
- 统一主要控件圆角层级
- 调整历史页表头对齐细节

### V1.0.0 (2026-06-03)

- 支持待办、计划任务、历史记录
- 本地 JSON 数据存储
- 基础任务管理功能

## 许可证

本项目仅供个人学习和使用。

## 联系方式

如有问题或建议，请通过 GitHub Issues 反馈。
