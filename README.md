# Dailyinfo 每日任务管理

Dailyinfo 是一款 Windows 桌面任务管理工具，使用 PySide6 构建，界面采用轻量毛玻璃风格和无边框窗口设计。应用以单文件为主，数据保存在本地，适合管理每日待办、计划任务和历史完成记录。

## 当前版本

V2.5.1

## 功能

- 待办任务添加、完成、取消完成和删除
- 计划任务支持截止日期
- 四种优先级：计划、高、中、低
- 任务详情弹窗支持编辑标题、内容、完成状态和任务类型
- 搜索待办和历史任务
- 历史页面查看已完成任务、完成时间和创建时间
- 内置日历，支持农历、干支年、二十四节气、常见节日、中国法定节假日和调休上班日
- 过期任务高亮提醒
- Windows 无边框窗口、毛玻璃效果、圆角容器和自绘窗口按钮

## 运行

### 安装依赖

```bash
pip install PySide6 pyinstaller
```

### 源码运行

```bash
python Code/daily_tasks.py
```

### 打包 exe

```bash
python -m PyInstaller 每日任务管理.spec --clean
```

打包输出位于 `dist/`。打包配置会把图标 `Ico/岚兮儿天下无敌好看.ico` 一起写入程序资源。

## 数据和资源

- 开发运行时，数据保存在项目目录下的 `Data/tasks.json`
- 打包运行时，数据保存在 exe 同级目录的 `Data/tasks.json`
- 图标文件只使用 `Ico/岚兮儿天下无敌好看.ico`
- `Data/`、`build/`、`dist/` 和 Python 缓存文件不应提交

## 项目结构

```text
每日任务/
├── Code/
│   └── daily_tasks.py
├── Data/
│   └── tasks.json
├── docs/
│   └── ui_terms.md
├── Ico/
│   └── 岚兮儿天下无敌好看.ico
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── start.bat
├── go.vbs
└── 每日任务管理.spec
```

## 技术栈

- Python
- PySide6
- PyInstaller
- Windows blur API

## 开发说明

主程序集中在 `Code/daily_tasks.py`：

- `TaskManager`：负责 `tasks.json` 的读取、保存、搜索和任务状态变更
- `TaskApp`：主窗口、任务列表、搜索、历史页、日历入口和窗口行为
- `TaskDetailDialog`：任务详情页，支持编辑、保存、完成、取消完成、删除和转换任务类型
- `HolidayCalendar`：自定义日历控件，负责日期绘制、节日高亮和调休上班日高亮

UI 区块命名参见 `docs/ui_terms.md`。

## 更新记录

### V2.5.1 (2026-06-12)

- 优化按钮焦点残影
- 优化任务详情关闭后的焦点回落
- 重做日历弹窗样式，去掉原生标题栏
- 增加农历、二十四节气、常见节日和调休上班日显示
- 统一主要控件圆角层级
- 调整历史页表头对齐细节

### 2026-06-03

- 初始版本
### V1.0.0 (2026-06-03)

- 支持待办、计划任务、历史记录和本地数据存储
