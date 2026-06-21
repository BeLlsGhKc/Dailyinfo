# Shared - 跨平台共享目录

本目录存放各平台共享的资源和代码，供 Windows、macOS、iOS、Android 端参考使用。

## 目录结构

```
Shared/
├── docs/                  # 文档
│   └── ui_terms.md        # UI 术语对照表（各平台统一命名）
├── calendar_utils.py      # 日历工具（农历、节气、节日计算）
├── task_model.py          # 任务数据模型（字段定义、数据结构）
└── README.md              # 本文件
```

## 各平台目录说明

| 目录 | 平台 | 说明 |
|------|------|------|
| `Windows/` | Windows | Python + PySide6 桌面端 |
| `Macos/` | macOS | 待开发 |
| `Ios/` | iOS | 待开发 |
| `Android/` | Android | Kotlin + Jetpack Compose |

## 共享资源说明

### docs/ui_terms.md

UI 术语对照表，定义了各平台统一使用的中文术语。各平台开发时请参考此文档，保持命名一致。

### calendar_utils.py

日历工具模块，提供：
- 农历日期计算
- 干支年、生肖
- 节气计算
- 常见节日
- 法定节假日和调休上班日

各平台可参考此模块的逻辑，用对应语言实现。

### task_model.py

任务数据模型，定义了：
- 任务字段结构（id、title、content、priority、deadline 等）
- 优先级枚举（计划、高、中、低）
- 任务状态（pending、completed）

各平台的数据存储和同步需遵循此模型。

## 数据互通

Windows 端和安卓端共享数据的方式：

- **JSON 文件同步**：通过网盘/文件传输手动同步 `Data/tasks.json`
- **MySQL 共享**：两端连接同一个 MySQL 数据库（推荐）

## 同步规则

1. **此目录是参考源**：各平台实现需与此保持逻辑一致
2. **数据格式兼容**：tasks.json 格式各端必须完全一致，确保数据可互通
3. **颜色方案一致**：PRIORITY_CONFIG 的颜色值各端保持相同

## 更新日志

- 2026-06-21：重构目录结构，添加 docs/，扩展为多平台共享目录
- 2026-06-13：从 `Code/daily_tasks.py` V3.0 提取初始版本
