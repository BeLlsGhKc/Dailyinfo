# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## 项目概述

每日任务管理工具 - 一款 Windows 桌面应用，采用苹果毛玻璃风格（PySide6 + Windows blur API）。

## 常用命令

```bash
# 源码运行
python Code/daily_tasks.py

# 打包 exe
python -m PyInstaller 每日任务管理.spec --clean

# 安装依赖
pip install PySide6 pyinstaller
```

## 架构

单文件应用：`Code/daily_tasks.py`

- **TaskManager** - 数据层，管理 tasks.json 的增删改查
- **TaskApp(QMainWindow)** - 主界面，包含任务列表、搜索、工具栏
- **TaskDetailDialog(QDialog)** - 任务详情弹窗，支持编辑/完成/删除/转换类型
- **HolidayCalendar(QCalendarWidget)** - 带中国节假日高亮的日历组件

数据存储在 exe 同级目录的 `Data/tasks.json`，打包后通过 `sys._MEIPASS` 读取内置资源（图标），通过 `os.path.dirname(sys.executable)` 定位数据目录。

## 打包注意事项

- `spec` 文件中 `datas` 需包含图标：`datas=[('Ico\\岚兮儿.ico', 'Ico')]`
- `SetCurrentProcessExplicitAppUserModelID` 必须在 `QApplication` 创建前调用，否则任务栏图标不显示
- 打包后路径判断：`getattr(sys, 'frozen', False)` 区分开发/打包环境

## 语言

使用中文编写注释、commit 信息、UI 文本。变量名和函数名使用英文。

## UI 区块命名

UI 区块的统一命名参见 [docs/ui_terms.md](docs/ui_terms.md)。
