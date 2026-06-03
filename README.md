# 每日任务管理

一款简洁美观的桌面任务管理工具，采用苹果毛玻璃风格设计。

## ✨ 功能特点

- 🎨 苹果风格毛玻璃界面
- 📋 任务管理（添加、完成、删除）
- 🏷️ 四级优先级（计划、高、中、低）
- 📅 计划任务支持截止日期
- 🔍 全局搜索（待办 + 历史）
- 📊 历史记录查看
- 🗓️ 内置日历（含中国节假日）
- ⏰ 过期任务提醒

## 📸 界面预览

```
Dailyinfo                                    ─  □  ✕
📋 每日任务                       2026/06/03 Tue
┌─────────────────────────────────────────────────────┐
│  输入内容       搜索   计划   高   中   低   添加   │
└─────────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 方式一：直接运行 exe

前往 [Releases](../../releases) 页面下载最新版本的 `每日任务管理.exe`。

### 方式二：源码运行

1. 克隆仓库
```bash
git clone https://github.com/你的用户名/每日任务.git
cd 每日任务
```

2. 创建虚拟环境
```bash
conda create -n Dailyinfo python=3.12
conda activate Dailyinfo
```

3. 安装依赖
```bash
pip install PySide6
```

4. 运行程序
```bash
python Code/daily_tasks.py
```

或者直接双击 `run.bat`

## 📁 目录结构

```
每日任务/
├── Code/           # 源代码
│   └── daily_tasks.py
├── Data/           # 数据文件（本地存储，不会上传）
│   └── tasks.json
├── Ico/            # 图标文件
│   └── 岚兮儿.ico
├── .gitignore      # Git 忽略规则
├── README.md       # 说明文档
└── run.bat         # Windows 启动脚本
```

## 🛠️ 技术栈

- Python 3.12
- PySide6 (Qt for Python)
- Windows 毛玻璃 API

## 📝 更新日志

### v1.0.0 (2026-06-03)
- 初始版本发布
- 基础任务管理功能
- 苹果毛玻璃风格界面
- 日历和节假日显示

## 📄 开源协议

MIT License
