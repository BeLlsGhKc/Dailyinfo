# -*- coding: utf-8 -*-
"""
任务数据模型模块

此文件从 Code/daily_tasks.py 提取，作为 Kotlin 实现的参考源。
安卓端的 data/ 包下的 Task.kt 需与此保持一致。
"""


# 优先级配置
# Kotlin 端需保持相同的颜色方案
PRIORITY_CONFIG = {
    "计划": {"color": "#AF52DE", "bg": "rgba(175, 82, 222, 0.12)"},  # 紫色
    "高":   {"color": "#FF3B30", "bg": "rgba(255, 59, 48, 0.12)"},   # 红色
    "中":   {"color": "#FF9500", "bg": "rgba(255, 149, 0, 0.12)"},   # 橙色
    "低":   {"color": "#34C759", "bg": "rgba(52, 199, 89, 0.12)"},   # 绿色
}

# 优先级列表（用于 UI 排序）
PRIORITY_LIST = ["计划", "高", "中", "低"]

# 任务类型
TASK_TYPE_PLANNED = "计划任务"
TASK_TYPE_NORMAL = "普通"


class Task:
    """
    任务数据模型

    字段说明：
    - id: 字符串，格式 YYYYMMDDHHmmSSffffff（微秒级时间戳）
    - title: 任务标题
    - content: 任务详细内容
    - priority: 优先级，枚举值 "计划" | "高" | "中" | "低"
    - type: 任务类型，"计划任务" | "普通"
    - created_at: 创建时间，格式 "YYYY-MM-DD HH:MM"
    - deadline: 截止日期，格式 "YYYY-MM-DD"，可为空字符串
    - completed_at: 完成时间，格式 "YYYY-MM-DD HH:MM"，未完成为 None
    - pinned: 是否置顶（仅历史任务使用）
    """

    def __init__(self, task_dict=None):
        if task_dict is None:
            task_dict = {}

        self.id = task_dict.get("id", "")
        self.title = task_dict.get("title", "")
        self.content = task_dict.get("content", "")
        self.priority = task_dict.get("priority", "中")
        self.type = task_dict.get("type", TASK_TYPE_NORMAL)
        self.created_at = task_dict.get("created_at", "")
        self.deadline = task_dict.get("deadline", "")
        self.completed_at = task_dict.get("completed_at")
        self.pinned = task_dict.get("pinned", False)

    def to_dict(self):
        """转换为字典（用于 JSON 序列化）"""
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "priority": self.priority,
            "type": self.type,
            "created_at": self.created_at,
            "deadline": self.deadline,
            "completed_at": self.completed_at,
            "pinned": self.pinned,
        }

    @property
    def is_completed(self):
        """是否已完成"""
        return self.completed_at is not None

    @property
    def is_planned(self):
        """是否为计划任务"""
        return self.type == TASK_TYPE_PLANNED

    @property
    def priority_color(self):
        """获取优先级颜色"""
        config = PRIORITY_CONFIG.get(self.priority)
        return config["color"] if config else "#8E8E93"

    @property
    def priority_bg_color(self):
        """获取优先级背景颜色"""
        config = PRIORITY_CONFIG.get(self.priority)
        return config["bg"] if config else "rgba(142, 142, 147, 0.12)"


# ========== tasks.json 格式说明 ==========
#
# 顶层结构：
# {
#     "pending": [ ... ],     // 未完成任务数组
#     "completed": [ ... ]    // 已完成任务数组
# }
#
# 每个任务对象的字段见 Task 类的 docstring
#
# ========== MySQL 表结构 ==========
#
# create table if not exists tasks (
#     id varchar(30) primary key,
#     title text not null,
#     content text,
#     priority varchar(10),
#     type varchar(20),
#     created_at varchar(20),
#     deadline varchar(20),
#     completed_at varchar(20) null,
#     pinned tinyint default 0,
#     status varchar(10) not null default 'pending'
# ) engine=innodb default charset=utf8mb4
#
# 注意：status 字段（"pending"/"completed"）是 MySQL 特有的
# JSON 格式中通过数组位置区分
