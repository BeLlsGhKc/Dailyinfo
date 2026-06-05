# -*- coding: utf-8 -*-
"""
每日任务管理工具 - 苹果毛玻璃风格 v6
"""

import sys
import json
import os
from datetime import datetime, date
from ctypes import windll, c_int, byref, sizeof, Structure, c_uint, POINTER

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QFrame, QGraphicsDropShadowEffect, QMessageBox, QDialog,
    QTextEdit, QDateEdit, QHeaderView, QCalendarWidget
)
from PySide6.QtCore import Qt, QTimer, QDate
from PySide6.QtGui import QColor, QIcon, QTextCharFormat, QPainter


# 中国节假日数据（2026年）
# 正日子显示节日名，其他假期日显示"节日名假期"
HOLIDAYS = {
    # 元旦
    "2026-01-01": "元旦",
    # 春节
    "2026-02-17": "除夕",
    "2026-02-18": "春节",
    "2026-02-19": "春节假期",
    "2026-02-20": "春节假期",
    "2026-02-21": "春节假期",
    "2026-02-22": "春节假期",
    "2026-02-23": "春节假期",
    # 清明节
    "2026-04-05": "清明节",
    "2026-04-06": "清明节假期",
    "2026-04-07": "清明节假期",
    # 劳动节
    "2026-05-01": "劳动节",
    "2026-05-02": "劳动节假期",
    "2026-05-03": "劳动节假期",
    "2026-05-04": "劳动节假期",
    "2026-05-05": "劳动节假期",
    # 端午节
    "2026-06-19": "端午节",
    "2026-06-20": "端午节假期",
    "2026-06-21": "端午节假期",
    # 中秋节
    "2026-09-25": "中秋节",
    "2026-09-26": "中秋节假期",
    "2026-09-27": "中秋节假期",
    # 国庆节
    "2026-10-01": "国庆节",
    "2026-10-02": "国庆节假期",
    "2026-10-03": "国庆节假期",
    "2026-10-04": "国庆节假期",
    "2026-10-05": "国庆节假期",
    "2026-10-06": "国庆节假期",
    "2026-10-07": "国庆节假期",
}


class HolidayCalendar(QCalendarWidget):
    """带节假日高亮的日历控件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumDate(QDate(2025, 1, 1))
        self.setMaximumDate(QDate(2027, 12, 31))
        self.setSelectedDate(QDate.currentDate())

    def paintCell(self, painter, rect, date):
        """自定义单元格绘制"""
        # 先调用默认绘制
        super().paintCell(painter, rect, date)

        date_str = date.toString("yyyy-MM-dd")
        is_today = date == QDate.currentDate()

        # 今天用青柠色高亮
        if is_today:
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)
            color = QColor(180, 230, 30, 80)  # 青柠色，半透明
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 6, 6)
            painter.restore()

        # 节假日显示青色背景
        if date_str in HOLIDAYS:
            painter.save()
            painter.setRenderHint(QPainter.Antialiasing)

            # 半透明青色背景
            color = QColor(0, 199, 190, 40)  # 青色，半透明
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 6, 6)

            # 绘制日期文字（正日子红色，假期日青色）
            holiday_name = HOLIDAYS[date_str]
            if not holiday_name.endswith("假期"):
                text_color = QColor(255, 59, 48)  # 红色（正日子）
            else:
                text_color = QColor(0, 199, 190)  # 青色（假期日）
            painter.setPen(text_color)
            painter.drawText(rect, Qt.AlignCenter, str(date.day()))

            painter.restore()


# 路径配置（Code 的上级目录）
# PyInstaller 打包后，资源文件在临时目录中
if getattr(sys, 'frozen', False):
    # 打包后的路径：临时目录（资源文件解压位置）
    BASE_DIR = sys._MEIPASS
    # 数据文件保存在 exe 同级目录
    DATA_DIR = os.path.join(os.path.dirname(sys.executable), "Data")
else:
    # 开发环境：Code 的上级目录
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "Data")

ICO_DIR = os.path.join(BASE_DIR, "Ico")
os.makedirs(DATA_DIR, exist_ok=True)


# Windows 毛玻璃 API
class ACCENT_POLICY(Structure):
    _fields_ = [("AccentState", c_uint), ("AccentFlags", c_uint),
                ("GradientColor", c_uint), ("AnimationId", c_uint)]

class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [("Attribute", c_int), ("Data", POINTER(ACCENT_POLICY)),
                ("SizeOfData", c_uint)]

def enable_blur_behind(hwnd):
    try:
        accent = ACCENT_POLICY()
        accent.AccentState = 3
        accent.GradientColor = 0xFF000000
        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19
        data.Data = accent
        data.SizeOfData = sizeof(accent)
        windll.user32.SetWindowCompositionAttribute(hwnd, byref(data))
    except:
        pass


WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

PRIORITY_CONFIG = {
    "计划": {"color": "#AF52DE", "bg": "rgba(175, 82, 222, 0.12)"},
    "高":   {"color": "#FF3B30", "bg": "rgba(255, 59, 48, 0.12)"},
    "中":   {"color": "#FF9500", "bg": "rgba(255, 149, 0, 0.12)"},
    "低":   {"color": "#34C759", "bg": "rgba(52, 199, 89, 0.12)"}
}


class TaskManager:
    def __init__(self):
        self.data_file = os.path.join(DATA_DIR, "tasks.json")
        self.tasks = self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"pending": [], "completed": []}
        return {"pending": [], "completed": []}

    def save_data(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def add_task(self, title, priority="中", task_type="普通", content="", deadline=""):
        task = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "title": title,
            "content": content,
            "priority": priority,
            "type": task_type,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "deadline": deadline,
            "completed_at": None
        }
        self.tasks["pending"].append(task)
        self.save_data()
        return task

    def update_task(self, task_id, updates):
        for task in self.tasks["pending"]:
            if task["id"] == task_id:
                task.update(updates)
                self.save_data()
                return True
        return False

    def complete_task(self, task_id):
        for i, task in enumerate(self.tasks["pending"]):
            if task["id"] == task_id:
                task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.tasks["completed"].insert(0, task)
                self.tasks["pending"].pop(i)
                self.save_data()
                return True
        return False

    def delete_task(self, task_id):
        for i, task in enumerate(self.tasks["pending"]):
            if task["id"] == task_id:
                self.tasks["pending"].pop(i)
                self.save_data()
                return True
        return False

    def uncomplete_task(self, task_id):
        """取消完成，移回待办"""
        for i, task in enumerate(self.tasks["completed"]):
            if task["id"] == task_id:
                task["completed_at"] = None
                self.tasks["pending"].append(task)
                self.tasks["completed"].pop(i)
                self.save_data()
                return True
        return False

    def search_tasks(self, keyword):
        results = []
        keyword = keyword.lower()
        for task in self.tasks["pending"]:
            if keyword in task["title"].lower() or keyword in task.get("content", "").lower():
                results.append(("pending", task))
        for task in self.tasks["completed"]:
            if keyword in task["title"].lower() or keyword in task.get("content", "").lower():
                results.append(("completed", task))
        return results

    def get_stats(self):
        total_completed = len(self.tasks["completed"])
        total_pending = len(self.tasks["pending"])
        today = date.today().strftime("%Y-%m-%d")
        today_completed = sum(
            1 for t in self.tasks["completed"]
            if t["completed_at"] and t["completed_at"].startswith(today)
        )
        return {"total_completed": total_completed, "total_pending": total_pending, "today_completed": today_completed}


# ========== 任务详情对话框 ==========
class TaskDetailDialog(QDialog):
    def __init__(self, task, manager, parent=None, is_history=False):
        super().__init__(parent)
        self.task = task
        self.manager = manager
        self.is_history = is_history
        self.result_action = None
        self.result_data = {}
        self.need_refresh = False

        self.setWindowTitle("任务详情")
        # 根据是否有截止日期调整窗口高度
        height = 620 if task.get("deadline") else 560
        self.setFixedSize(500, height)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        self.setup_ui()

    def setup_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        container = QFrame()
        container.setObjectName("dialogContainer")
        container.setStyleSheet("""
            #dialogContainer {
                background: rgba(255, 255, 255, 0.98);
                border-radius: 16px;
                border: 1px solid rgba(0, 0, 0, 0.08);
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # 标题栏
        header = QHBoxLayout()
        title_label = QLabel("📋 任务详情")
        title_label.setStyleSheet("font-size: 16px; font-weight: 600; color: #1d1d1f;")
        header.addWidget(title_label)
        header.addStretch()

        close_btn = QPushButton("✕")
        close_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                font-size: 16px; color: #8e8e93;
                padding: 4px 8px; border-radius: 6px;
            }
            QPushButton:hover { background: rgba(255, 59, 48, 0.1); color: #FF3B30; }
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.reject)
        header.addWidget(close_btn)
        layout.addLayout(header)

        # 实线分隔
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background: rgba(0,0,0,0.15);")
        layout.addWidget(line)

        # 标题（可编辑）
        layout.addWidget(self._label("标题"))
        self.title_edit = QLineEdit(self.task["title"])
        self.title_edit.setFixedHeight(44)
        self.title_edit.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.9);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 15px;
                font-weight: 500;
                color: #1d1d1f;
            }
            QLineEdit:focus {
                border: 1.5px solid #007AFF;
            }
        """)
        layout.addWidget(self.title_edit)

        # 内容（可编辑）
        layout.addWidget(self._label("内容"))
        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(self.task.get("content", ""))
        self.content_edit.setMinimumHeight(120)
        self.content_edit.setMaximumHeight(160)
        self.content_edit.setStyleSheet("""
            QTextEdit {
                background: rgba(255,255,255,0.9);
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 14px;
                color: #1d1d1f;
            }
            QTextEdit:focus {
                border: 1.5px solid #007AFF;
            }
        """)
        layout.addWidget(self.content_edit)

        # 创建时间（只读）
        layout.addWidget(self._label("创建时间"))
        created_label = QLabel(self.task["created_at"])
        created_label.setStyleSheet("color: #1d1d1f; font-size: 14px; padding: 8px 12px; background: rgba(255,255,255,0.9); border: 1px solid rgba(0,0,0,0.1); border-radius: 8px;")
        layout.addWidget(created_label)

        # 截止日期（只读）
        deadline = self.task.get("deadline", "")
        if deadline:
            layout.addWidget(self._label("截止日期"))
            deadline_label = QLabel(deadline)
            deadline_label.setStyleSheet("color: #1d1d1f; font-size: 14px; padding: 8px 12px; background: rgba(255,255,255,0.9); border: 1px solid rgba(0,0,0,0.1); border-radius: 8px;")
            layout.addWidget(deadline_label)

        layout.addStretch()

        # 按钮区
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        if self.is_history:
            # 历史任务：取消完成
            uncomplete_btn = self._btn("↩️ 取消完成", "#FF9500", "#E68A00")
            uncomplete_btn.clicked.connect(self.on_uncomplete)
            btn_layout.addWidget(uncomplete_btn)
        else:
            # 待办任务：标记完成
            complete_btn = self._btn("✅ 标记完成", "#34C759", "#2DA44E")
            complete_btn.clicked.connect(self.on_complete)
            btn_layout.addWidget(complete_btn)

        save_btn = self._btn("💾 保存修改", "#007AFF", "#0056CC")
        save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(save_btn)

        if self.is_history:
            # 历史任务：转换按钮禁用
            convert_btn = self._btn("🔄 转换类型", "#8e8e93", "#8e8e93")
            convert_btn.setEnabled(False)
            convert_btn.setCursor(Qt.ArrowCursor)
            btn_layout.addWidget(convert_btn)
        else:
            convert_btn = self._btn("🔄 转换类型", "#FF9500", "#E68A00")
            convert_btn.clicked.connect(self.on_convert)
            btn_layout.addWidget(convert_btn)

        del_btn = self._btn("🗑️ 删除", "#FF3B30", "#D63027")
        del_btn.clicked.connect(self.on_delete)
        btn_layout.addWidget(del_btn)

        layout.addLayout(btn_layout)

        outer.addWidget(container)
        self._drag_pos = None

        # 延迟设置焦点，确保内容编辑框可立即编辑
        QTimer.singleShot(100, self.content_edit.setFocus)

    def _label(self, text):
        l = QLabel(text)
        l.setStyleSheet("font-size: 12px; font-weight: 600; color: #8e8e93;")
        return l

    def _btn(self, text, bg, hover):
        btn = QPushButton(text)
        btn.setStyleSheet(f"""
            QPushButton {{
                background: {bg}; color: white; border: none;
                border-radius: 8px; padding: 10px 14px; font-size: 13px; font-weight: 500;
            }}
            QPushButton:hover {{ background: {hover}; }}
        """)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def on_complete(self):
        self.result_action = "complete"
        self.accept()

    def on_uncomplete(self):
        """取消完成"""
        self.result_action = "uncomplete"
        self.accept()

    def on_save(self):
        """保存修改但不关闭详情页"""
        title = self.title_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        if not title:
            QMessageBox.warning(self, "提示", "标题不能为空")
            return
        self.manager.update_task(self.task["id"], {"title": title, "content": content})
        self.task["title"] = title
        self.task["content"] = content
        self.need_refresh = True
        QMessageBox.information(self, "提示", "保存成功")

    def on_convert(self):
        """转换类型"""
        if self.task["type"] == "计划任务":
            # 转为普通任务，选择优先级
            dlg = QDialog(self)
            dlg.setWindowTitle("选择优先级")
            dlg.setFixedSize(260, 180)
            dlg.setStyleSheet("QDialog { background: rgba(255,255,255,0.98); border-radius: 12px; }")

            layout = QVBoxLayout(dlg)
            layout.setContentsMargins(20, 16, 20, 16)
            layout.setSpacing(12)

            label = QLabel("选择优先级")
            label.setStyleSheet("font-size: 14px; font-weight: 600; color: #1d1d1f;")
            layout.addWidget(label)

            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(8)

            for priority in ["高", "中", "低"]:
                cfg = PRIORITY_CONFIG[priority]
                btn = QPushButton(priority)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {cfg['color']}; color: white; border: none;
                        border-radius: 8px; padding: 10px 20px; font-size: 14px; font-weight: 600;
                    }}
                    QPushButton:hover {{ opacity: 0.8; }}
                """)
                btn.setCursor(Qt.PointingHandCursor)
                btn.clicked.connect(lambda _, p=priority: (self._set_convert("普通", p), dlg.accept()))
                btn_layout.addWidget(btn)

            layout.addLayout(btn_layout)

            cancel_btn = QPushButton("取消")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0,0,0,0.05); border: none;
                    border-radius: 8px; padding: 8px; font-size: 13px;
                }
                QPushButton:hover { background: rgba(0,0,0,0.08); }
            """)
            cancel_btn.setCursor(Qt.PointingHandCursor)
            cancel_btn.clicked.connect(dlg.reject)
            layout.addWidget(cancel_btn)

            dlg.exec()
        else:
            # 转为计划任务，选择截止日期
            dlg = QDialog(self)
            dlg.setWindowTitle("选择截止日期")
            dlg.setFixedSize(280, 200)
            dlg.setStyleSheet("QDialog { background: rgba(255,255,255,0.98); border-radius: 12px; }")

            layout = QVBoxLayout(dlg)
            layout.setContentsMargins(20, 16, 20, 16)
            layout.setSpacing(12)

            label = QLabel("📅 选择截止日期")
            label.setStyleSheet("font-size: 14px; font-weight: 600; color: #1d1d1f;")
            layout.addWidget(label)

            date_edit = QDateEdit()
            date_edit.setCalendarPopup(True)
            date_edit.setDate(QDate.currentDate().addDays(7))
            date_edit.setDisplayFormat("yyyy-MM-dd")
            date_edit.setStyleSheet("""
                QDateEdit {
                    background: white; border: 1px solid rgba(0,0,0,0.1);
                    border-radius: 8px; padding: 10px 12px; font-size: 14px;
                }
            """)
            layout.addWidget(date_edit)

            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(8)

            cancel_btn = QPushButton("取消")
            cancel_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0,0,0,0.05); border: none;
                    border-radius: 8px; padding: 10px; font-size: 13px;
                }
                QPushButton:hover { background: rgba(0,0,0,0.08); }
            """)
            cancel_btn.setCursor(Qt.PointingHandCursor)
            cancel_btn.clicked.connect(dlg.reject)
            btn_layout.addWidget(cancel_btn)

            ok_btn = QPushButton("确定")
            ok_btn.setStyleSheet("""
                QPushButton {
                    background: #007AFF; color: white; border: none;
                    border-radius: 8px; padding: 10px; font-size: 13px; font-weight: 500;
                }
                QPushButton:hover { background: #0056CC; }
            """)
            ok_btn.setCursor(Qt.PointingHandCursor)
            ok_btn.clicked.connect(lambda: (self._set_convert("计划任务", "计划", date_edit.date().toString("yyyy-MM-dd")), dlg.accept()))
            btn_layout.addWidget(ok_btn)

            layout.addLayout(btn_layout)

            dlg.exec()

    def _set_convert(self, task_type, priority, deadline=""):
        """转换类型但不关闭详情页"""
        updates = {
            "type": task_type,
            "priority": priority,
            "deadline": deadline
        }
        self.manager.update_task(self.task["id"], updates)
        self.task.update(updates)
        self.need_refresh = True
        QMessageBox.information(self, "提示", "转换成功")

    def on_delete(self):
        reply = QMessageBox.question(
            self, "确认", "确定删除此任务？",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.result_action = "delete"
            self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


# ========== 主应用 ==========
class TaskApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = TaskManager()
        self.searching = False
        self.showing_history = False

        self.setWindowTitle("每日任务管理")
        self.setFixedSize(1100, 720)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        # 设置任务栏图标
        icon_path = os.path.join(ICO_DIR, "岚兮儿.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setup_ui()
        self.refresh_task_list()
        QTimer.singleShot(100, self.enable_blur)

    def enable_blur(self):
        hwnd = int(self.winId())
        enable_blur_behind(hwnd)

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(12, 12, 12, 12)

        self.glass = QFrame()
        self.glass.setObjectName("glassContainer")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.glass.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(self.glass)
        main_layout.setContentsMargins(18, 14, 18, 18)
        main_layout.setSpacing(10)

        # ====== 顶部栏 ======
        header = QFrame()
        header.setObjectName("header")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(18, 14, 18, 14)
        header_layout.setSpacing(8)

        # 第一行：Dailyinfo（左） + 窗口控制（右）
        win_row = QHBoxLayout()
        win_row.setContentsMargins(0, 0, 0, 0)

        daily_label = QLabel("Dailyinfo")
        daily_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #8e8e93;")
        win_row.addWidget(daily_label)

        win_row.addStretch()

        min_btn = QPushButton("─")
        min_btn.setObjectName("windowBtn")
        min_btn.setFixedSize(28, 28)
        min_btn.setCursor(Qt.PointingHandCursor)
        min_btn.clicked.connect(self.showMinimized)
        win_row.addWidget(min_btn)

        self.max_btn = QPushButton("□")
        self.max_btn.setObjectName("windowBtn")
        self.max_btn.setFixedSize(28, 28)
        self.max_btn.setCursor(Qt.PointingHandCursor)
        self.max_btn.clicked.connect(self.toggle_maximize)
        win_row.addWidget(self.max_btn)

        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeBtn")
        close_btn.setFixedSize(28, 28)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        win_row.addWidget(close_btn)

        header_layout.addLayout(win_row)

        # 第二行：每日任务（左） + 日期 星期 历史（右）
        info_row = QHBoxLayout()
        info_row.setContentsMargins(0, 4, 0, 0)
        info_row.setSpacing(12)

        app_label = QLabel("📋 每日任务")
        app_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #1d1d1f;")
        info_row.addWidget(app_label)

        info_row.addStretch()

        now = datetime.now()
        date_label = QLabel(now.strftime("%Y/%m/%d"))
        date_label.setObjectName("timeLabel")
        info_row.addWidget(date_label)

        weekday_btn = QPushButton(WEEKDAYS[now.weekday()][:3])
        weekday_btn.setObjectName("weekdayLabel")
        weekday_btn.setCursor(Qt.PointingHandCursor)
        weekday_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #007AFF;
                font-size: 13px;
                font-weight: 500;
                padding: 4px 8px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background: rgba(0, 122, 255, 0.08);
            }
        """)
        weekday_btn.clicked.connect(self.show_calendar)
        info_row.addWidget(weekday_btn)

        self.history_btn = QPushButton("📖 历史")
        self.history_btn.setObjectName("headerBtn")
        self.history_btn.setCursor(Qt.PointingHandCursor)
        self.history_btn.clicked.connect(self.show_history)
        info_row.addWidget(self.history_btn)

        header_layout.addLayout(info_row)

        main_layout.addWidget(header)

        # ====== 工具栏 ======
        toolbar = QFrame()
        toolbar.setObjectName("toolBar")
        toolbar.setStyleSheet("""
            #toolBar {
                background: rgba(255, 255, 255, 0.6);
                border-radius: 12px;
                border: 1px solid rgba(0, 0, 0, 0.08);
            }
        """)
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(12, 10, 12, 10)
        toolbar_layout.setSpacing(8)

        # 输入框
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("输入内容")
        self.task_input.setFixedHeight(42)
        self.task_input.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.45);
                border: 1px solid rgba(0, 0, 0, 0.06);
                border-radius: 8px;
                padding: 0 14px;
                font-size: 14px;
                color: #1d1d1f;
            }
            QLineEdit:focus {
                border: 1.5px solid #007AFF;
                background: rgba(255, 255, 255, 0.7);
            }
        """)
        self.task_input.returnPressed.connect(self.add_task)
        self.task_input.textChanged.connect(self.on_input_changed)
        toolbar_layout.addWidget(self.task_input, 1)

        # 搜索按钮
        self.search_btn = QPushButton("搜索")
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.setFixedHeight(42)
        self.search_btn.setMinimumWidth(52)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #0056CC;
            }
        """)
        self.search_btn.clicked.connect(self.on_search_btn_click)
        toolbar_layout.addWidget(self.search_btn)

        # 优先级按钮（创建任务时选择）
        self.priority_btns = {}
        self.selected_priority = "计划"  # 默认选中

        for label in ["计划", "高", "中", "低"]:
            cfg = PRIORITY_CONFIG[label]
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setFixedHeight(42)
            btn.setMinimumWidth(52)
            btn.clicked.connect(lambda checked, l=label: self.on_priority_select(l))
            self.priority_btns[label] = btn
            toolbar_layout.addWidget(btn)

        # 默认选中"计划"
        self.priority_btns["计划"].setChecked(True)
        self._update_priority_styles()

        # 添加按钮
        add_btn = QPushButton("添加")
        add_btn.setObjectName("addBtn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(42)
        add_btn.setMinimumWidth(56)
        add_btn.clicked.connect(self.add_task)
        toolbar_layout.addWidget(add_btn)

        main_layout.addWidget(toolbar)

        # ====== 任务列表 ======
        list_card = QFrame()
        list_card.setObjectName("card")
        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(6, 6, 6, 6)
        list_layout.setSpacing(0)

        self.task_list = QTreeWidget()
        self.task_list.setHeaderLabels(["", "        任务内容", "创建时间"])
        self.task_list.setRootIsDecorated(False)
        self.task_list.header().setDefaultAlignment(Qt.AlignLeft)
        self.task_list.setColumnWidth(0, 80)
        self.task_list.setColumnWidth(1, 720)
        self.task_list.setColumnWidth(2, 180)
        self.task_list.setIndentation(0)
        self.task_list.header().setStretchLastSection(False)
        self.task_list.header().setSectionResizeMode(0, QHeaderView.Fixed)
        self.task_list.header().setSectionResizeMode(1, QHeaderView.Stretch)
        self.task_list.header().setSectionResizeMode(2, QHeaderView.Fixed)
        self.task_list.itemClicked.connect(self.on_task_click)
        list_layout.addWidget(self.task_list)

        self.empty_label = QLabel("✨ 暂无任务，添加一个吧~")
        self.empty_label.setObjectName("emptyLabel")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setVisible(False)
        list_layout.addWidget(self.empty_label)

        main_layout.addWidget(list_card, 1)

        # ====== 底部 ======
        footer = QWidget()
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(4, 0, 4, 0)

        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #8e8e93; font-size: 12px;")
        footer_layout.addWidget(self.stats_label)
        footer_layout.addStretch()

        main_layout.addWidget(footer)

        outer.addWidget(self.glass)

        # 拖拽
        self._drag_pos = None
        header.mousePressEvent = self.header_mouse_press
        header.mouseMoveEvent = self.header_mouse_move
        header.mouseReleaseEvent = self.header_mouse_release

    def _update_priority_styles(self):
        """更新优先级按钮样式"""
        for label, btn in self.priority_btns.items():
            cfg = PRIORITY_CONFIG[label]
            if btn.isChecked():
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background: {cfg['color']}; color: white;
                        border: none; border-radius: 8px;
                        font-size: 13px; font-weight: 600;
                    }}
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: rgba(0, 0, 0, 0.04);
                        color: #6e6e73;
                        border: 1px solid rgba(0, 0, 0, 0.08);
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background: rgba(0, 0, 0, 0.07);
                    }
                """)

    def on_priority_select(self, label):
        """选择优先级（单选）"""
        for btn in self.priority_btns.values():
            btn.setChecked(False)
        self.priority_btns[label].setChecked(True)
        self.selected_priority = label
        self._update_priority_styles()

    def toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.max_btn.setText("□")
        else:
            self.showMaximized()
            self.max_btn.setText("❐")

    def show_calendar(self):
        """显示日历弹窗"""
        dlg = QDialog(self)
        dlg.setWindowTitle("日历")
        dlg.setFixedSize(420, 450)
        dlg.setStyleSheet("""
            QDialog {
                background: rgba(255,255,255,0.98);
                border-radius: 12px;
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        dlg.setGraphicsEffect(shadow)

        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title = QLabel("📅 日历")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #1d1d1f;")
        layout.addWidget(title)

        # 使用自定义日历控件
        calendar = HolidayCalendar()
        calendar.setStyleSheet("""
            QCalendarWidget {
                background: white;
                border: 1px solid rgba(0,0,0,0.1);
                border-radius: 8px;
            }
            QCalendarWidget QToolButton {
                color: #1d1d1f;
                background: transparent;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 15px;
                font-weight: 600;
            }
            QCalendarWidget QToolButton:hover {
                background: rgba(0, 122, 255, 0.08);
            }
            QCalendarWidget QAbstractItemView {
                selection-background-color: #007AFF;
                selection-color: white;
                font-size: 14px;
            }
        """)
        layout.addWidget(calendar)

        # 节假日信息显示
        today = QDate.currentDate()
        today_str = today.toString("yyyy-MM-dd")
        if today_str in HOLIDAYS:
            holiday_info = QLabel(HOLIDAYS[today_str])
            holiday_info.setStyleSheet("color: #00C7BE; font-size: 14px; font-weight: 600; padding: 8px;")
        else:
            holiday_info = QLabel("点击日期查看节假日信息")
            holiday_info.setStyleSheet("color: #8e8e93; font-size: 13px; padding: 8px;")
        holiday_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(holiday_info)

        def on_date_selected(qdate):
            date_str = qdate.toString("yyyy-MM-dd")
            if date_str in HOLIDAYS:
                holiday_info.setText(HOLIDAYS[date_str])
                holiday_info.setStyleSheet("color: #00C7BE; font-size: 14px; font-weight: 600; padding: 8px;")
            else:
                weekday = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
                holiday_info.setText(weekday[qdate.dayOfWeek() - 1])
                holiday_info.setStyleSheet("color: #8e8e93; font-size: 13px; padding: 8px;")

        calendar.clicked.connect(on_date_selected)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        # 回到今天按钮
        back_today_btn = QPushButton("📅 回到今天")
        back_today_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 122, 255, 0.1);
                color: #007AFF;
                border: 1px solid rgba(0, 122, 255, 0.2);
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 13px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: rgba(0, 122, 255, 0.18);
            }
        """)
        back_today_btn.setCursor(Qt.PointingHandCursor)

        def go_today():
            # 先更新说明文字
            on_date_selected(today)
            # 再跳转日历到当月
            calendar.setSelectedDate(today)
            calendar.showMonth(0)

        back_today_btn.clicked.connect(go_today)
        btn_layout.addWidget(back_today_btn)

        btn_layout.addStretch()

        close_btn = QPushButton("关闭")
        close_btn.setStyleSheet("""
            QPushButton {
                background: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #0056CC;
            }
        """)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(dlg.accept)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

        dlg.exec()

    def show_history(self):
        """显示历史页面"""
        if self.showing_history:
            # 返回主页
            self.showing_history = False
            self.history_btn.setText("📖 历史")
            self.history_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(0, 122, 255, 0.1);
                    color: #007AFF;
                    border: 1px solid rgba(0, 122, 255, 0.2);
                    border-radius: 8px;
                    padding: 6px 14px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: rgba(0, 122, 255, 0.18);
                }
            """)
            self.refresh_task_list()
        else:
            # 显示历史
            self.showing_history = True
            self.searching = False
            self.history_btn.setText("⬅️ 返回")
            self.history_btn.setStyleSheet("""
                QPushButton {
                    background: rgba(142, 142, 147, 0.1);
                    color: #8e8e93;
                    border: 1px solid rgba(142, 142, 147, 0.2);
                    border-radius: 8px;
                    padding: 6px 14px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: rgba(142, 142, 147, 0.18);
                }
            """)
            self.refresh_history_list()

    def header_mouse_press(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.pos()

    def header_mouse_move(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def header_mouse_release(self, event):
        self._drag_pos = None

    def on_input_changed(self, text):
        """输入内容变化时，如果有搜索状态则实时搜索"""
        if self.searching:
            keyword = text.strip()
            if keyword:
                results = self.manager.search_tasks(keyword)
                self.refresh_search_list(results)
            else:
                self.searching = False
                self.refresh_task_list()

    def on_search_btn_click(self):
        """搜索按钮点击"""
        if self.searching:
            # 返回
            self.search_btn.setText("搜索")
            self.search_btn.setStyleSheet("""
                QPushButton {
                    background: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background: #0056CC;
                }
            """)
            self.task_input.clear()
            self.task_input.setPlaceholderText("输入内容")
            self.searching = False
            self.refresh_task_list()
        else:
            # 执行搜索
            keyword = self.task_input.text().strip()
            if keyword:
                self.search_btn.setText("返回")
                self.search_btn.setStyleSheet("""
                    QPushButton {
                        background: #8e8e93;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background: #636366;
                    }
                """)
                self.task_input.setPlaceholderText("搜索中...")
                self.searching = True
                results = self.manager.search_tasks(keyword)
                self.refresh_search_list(results)

    def add_task(self):
        title = self.task_input.text().strip()
        if not title:
            return

        # 如果当前是搜索状态，回车执行搜索
        if self.searching:
            results = self.manager.search_tasks(title)
            self.refresh_search_list(results)
            return

        priority = self.selected_priority
        task_type = "计划任务" if priority == "计划" else "普通"
        deadline = ""

        if priority == "计划":
            deadline = self._pick_deadline()

        self.manager.add_task(title, priority, task_type, deadline=deadline)
        self.task_input.clear()
        self.refresh_task_list()
        self.task_input.setFocus()

    def _pick_deadline(self):
        """弹出截止日期选择"""
        dlg = QDialog(self)
        dlg.setWindowTitle("选择截止日期")
        dlg.setFixedSize(280, 150)
        dlg.setStyleSheet("""
            QDialog {
                background: rgba(255,255,255,0.98);
                border-radius: 12px;
            }
        """)
        layout = QVBoxLayout(dlg)
        layout.setContentsMargins(20, 16, 20, 16)

        label = QLabel("📅 选择截止日期")
        label.setStyleSheet("font-size: 14px; font-weight: 600; color: #1d1d1f;")
        layout.addWidget(label)

        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate().addDays(7))
        date_edit.setDisplayFormat("yyyy-MM-dd")
        date_edit.setStyleSheet("""
            QDateEdit {
                background: white; border: 1px solid rgba(0,0,0,0.1);
                border-radius: 8px; padding: 8px 12px; font-size: 14px;
            }
        """)
        layout.addWidget(date_edit)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0,0,0,0.05); border: none;
                border-radius: 8px; padding: 8px 16px; font-size: 13px;
            }
            QPushButton:hover { background: rgba(0,0,0,0.08); }
        """)
        cancel_btn.clicked.connect(dlg.reject)
        btn_layout.addWidget(cancel_btn)

        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet("""
            QPushButton {
                background: #007AFF; color: white; border: none;
                border-radius: 8px; padding: 8px 16px; font-size: 13px; font-weight: 500;
            }
            QPushButton:hover { background: #0056CC; }
        """)
        ok_btn.clicked.connect(dlg.accept)
        btn_layout.addWidget(ok_btn)

        layout.addLayout(btn_layout)

        if dlg.exec() == QDialog.Accepted:
            return date_edit.date().toString("yyyy-MM-dd")
        return ""

    def on_task_click(self, item, column):
        """点击任务条打开详情"""
        task_id = item.data(0, Qt.UserRole)
        task = self._find_task(task_id)
        if not task:
            return

        # 判断是历史任务还是待办任务
        is_history = task in self.manager.tasks["completed"]

        dlg = TaskDetailDialog(task, self.manager, self, is_history)
        QTimer.singleShot(50, lambda: enable_blur_behind(int(dlg.winId())))

        result = dlg.exec()

        # 处理完成、取消完成和删除操作
        if result == QDialog.Accepted:
            action = dlg.result_action
            if action == "complete":
                self.manager.complete_task(task_id)
            elif action == "uncomplete":
                self.manager.uncomplete_task(task_id)
            elif action == "delete":
                if is_history:
                    # 历史任务删除
                    for i, t in enumerate(self.manager.tasks["completed"]):
                        if t["id"] == task_id:
                            self.manager.tasks["completed"].pop(i)
                            self.manager.save_data()
                            break
                else:
                    self.manager.delete_task(task_id)

        # 无论是否关闭详情页，只要有修改就刷新
        if dlg.need_refresh or result == QDialog.Accepted:
            if self.searching:
                keyword = self.task_input.text().strip()
                if keyword:
                    results = self.manager.search_tasks(keyword)
                    self.refresh_search_list(results)
            elif self.showing_history:
                self.refresh_history_list()
            else:
                self.refresh_task_list()

    def _find_task(self, task_id):
        """查找任务（包括待办和历史）"""
        for task in self.manager.tasks["pending"]:
            if task["id"] == task_id:
                return task
        for task in self.manager.tasks["completed"]:
            if task["id"] == task_id:
                return task
        return None

    def refresh_task_list(self):
        """刷新任务列表（默认显示所有未完成任务）"""
        self.task_list.clear()

        today = date.today().strftime("%Y-%m-%d")
        source = self.manager.tasks["pending"]

        def sort_key(task):
            # 计划任务日期当前（今天或未来）= 0
            # 已过期内容（昨天或更早）= 1
            # 计划（无日期）= 2
            # 高 = 3
            # 中 = 4
            # 低 = 5
            if task["type"] == "计划任务":
                deadline = task.get("deadline", "")
                if deadline:
                    if deadline >= today:
                        return (0, deadline)
                    else:
                        return (1, deadline)
                else:
                    return (2, "")
            else:
                order = {"高": 3, "中": 4, "低": 5}
                return (order.get(task["priority"], 4), "")

        source = sorted(source, key=sort_key)

        self.empty_label.setVisible(len(source) == 0)
        self.task_list.setVisible(len(source) > 0)

        for task in source:
            item = QTreeWidgetItem()
            item.setData(0, Qt.UserRole, task["id"])
            self.task_list.addTopLevelItem(item)

            priority = task["priority"]

            # 完成方块
            check_btn = QPushButton()
            check_btn.setFixedSize(26, 26)
            check_btn.setCursor(Qt.PointingHandCursor)
            hover_color = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["color"]
            hover_bg = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["bg"]
            check_btn.setStyleSheet(f"""
                QPushButton {{
                    background: rgba(255,255,255,0.7);
                    border: 2px solid #c7c7cc;
                    border-radius: 5px;
                }}
                QPushButton:hover {{
                    border: 2px solid {hover_color};
                    background: {hover_bg};
                }}
            """)
            check_btn.clicked.connect(lambda _, tid=task["id"]: self.quick_complete(tid))

            # 完成方块容器（居中偏下）
            check_container = QWidget()
            check_layout = QHBoxLayout(check_container)
            check_layout.setContentsMargins(0, 8, 0, 0)
            check_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            check_layout.addWidget(check_btn)
            self.task_list.setItemWidget(item, 0, check_container)

            # 任务内容
            content_widget = QWidget()
            content_layout = QHBoxLayout(content_widget)
            content_layout.setContentsMargins(12, 0, 8, 0)
            content_layout.setSpacing(10)

            dot_color = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["color"]
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {dot_color}; font-size: 16px; background: transparent; border: none;")
            dot.setFixedWidth(20)
            dot.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(dot)

            title = task["title"]
            is_expired_plan = False
            is_expired_normal = False
            deadline = ""

            if task["type"] == "计划任务":
                title = f"📅 {title}"
                deadline = task.get("deadline", "")
                if deadline:
                    if deadline < today:
                        is_expired_plan = True
            else:
                # 普通任务检查是否过了当天
                created_date = task["created_at"][:10]  # 取日期部分
                if created_date < today:
                    is_expired_normal = True

            # 标题（黑色）
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #1d1d1f; font-size: 14px; background: transparent; border: none;")
            content_layout.addWidget(title_label, 1)

            # 日期提醒（右贴边）
            if is_expired_plan:
                expire_label = QLabel(f"⚠️ 已过期 {deadline}")
                expire_label.setStyleSheet("color: #FF3B30; font-size: 12px; font-weight: 600; background: transparent; border: none;")
                expire_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                content_layout.addWidget(expire_label)
            elif deadline and not is_expired_plan:
                deadline_label = QLabel(deadline)
                deadline_label.setStyleSheet("color: #8e8e93; font-size: 12px; background: transparent; border: none;")
                deadline_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                content_layout.addWidget(deadline_label)

            self.task_list.setItemWidget(item, 1, content_widget)

            # 时间
            if is_expired_normal:
                time_label = QLabel(task["created_at"])
                time_label.setStyleSheet("color: #FF3B30; font-size: 12px; font-weight: 600; background: transparent; border: none;")
            else:
                time_label = QLabel(task["created_at"])
                time_label.setStyleSheet("color: #8e8e93; font-size: 12px; background: transparent; border: none;")
            self.task_list.setItemWidget(item, 2, time_label)

            # 统一背景色（计划任务过期整栏变红）
            if is_expired_plan:
                for col in range(3):
                    item.setBackground(col, QColor(255, 59, 48, 40))  # 红色背景
            else:
                bg = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["bg"]
                for col in range(3):
                    item.setBackground(col, QColor(bg))

        self.update_stats()

    def refresh_search_list(self, results):
        """刷新搜索结果列表"""
        self.task_list.clear()

        all_tasks = []
        for task_type, task in results:
            all_tasks.append((task_type, task))

        priority_order = {"计划": -1, "高": 0, "中": 1, "低": 2}
        all_tasks.sort(key=lambda x: priority_order.get(x[1]["priority"], 1))

        self.empty_label.setVisible(len(all_tasks) == 0)
        self.task_list.setVisible(len(all_tasks) > 0)

        for task_type, task in all_tasks:
            item = QTreeWidgetItem()
            item.setData(0, Qt.UserRole, task["id"])
            self.task_list.addTopLevelItem(item)

            if task_type == "pending":
                check_btn = QPushButton()
                check_btn.setFixedSize(22, 22)
                check_btn.setCursor(Qt.PointingHandCursor)
                check_btn.setStyleSheet("""
                    QPushButton {
                        background: rgba(255,255,255,0.7);
                        border: 2px solid #c7c7cc;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        border: 2px solid #34C759;
                        background: rgba(52,199,89,0.15);
                    }
                """)
                check_btn.clicked.connect(lambda _, tid=task["id"]: self.quick_complete(tid))
                self.task_list.setItemWidget(item, 0, check_btn)
            else:
                done_label = QLabel("✓")
                done_label.setStyleSheet("color: #34C759; font-size: 16px; background: transparent; border: none;")
                done_label.setAlignment(Qt.AlignCenter)
                self.task_list.setItemWidget(item, 0, done_label)

            content_widget = QWidget()
            content_layout = QHBoxLayout(content_widget)
            content_layout.setContentsMargins(8, 0, 8, 0)
            content_layout.setSpacing(10)

            priority = task["priority"]
            dot_color = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["color"]
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {dot_color}; font-size: 16px; background: transparent; border: none;")
            dot.setFixedWidth(20)
            dot.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(dot)

            title = task["title"]
            if task["type"] == "计划任务":
                title = f"📅 {title}"
            if task_type == "completed":
                title += "  [已完成]"

            title_label = QLabel(title)
            title_label.setStyleSheet("color: #1d1d1f; font-size: 14px; background: transparent; border: none;")
            content_layout.addWidget(title_label, 1)

            self.task_list.setItemWidget(item, 1, content_widget)

            time_str = task["completed_at"] if task_type == "completed" else task["created_at"]
            time_label = QLabel(time_str)
            time_label.setStyleSheet("color: #8e8e93; font-size: 12px; background: transparent; border: none;")
            self.task_list.setItemWidget(item, 2, time_label)

            bg = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["bg"]
            for col in range(3):
                item.setBackground(col, QColor(bg))

        self.update_stats()

    def refresh_history_list(self):
        """刷新历史列表"""
        self.task_list.clear()

        source = self.manager.tasks["completed"]

        self.empty_label.setVisible(len(source) == 0)
        self.task_list.setVisible(len(source) > 0)

        for task in source:
            item = QTreeWidgetItem()
            item.setData(0, Qt.UserRole, task["id"])
            self.task_list.addTopLevelItem(item)

            # 取消完成按钮（带对钩的方框）
            priority = task["priority"]
            hover_color = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["color"]
            hover_bg = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["bg"]

            uncheck_btn = QPushButton("✓")
            uncheck_btn.setFixedSize(26, 26)
            uncheck_btn.setCursor(Qt.PointingHandCursor)
            uncheck_btn.setStyleSheet(f"""
                QPushButton {{
                    background: #34C759;
                    border: 2px solid #2DA44E;
                    border-radius: 5px;
                    color: white;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    border: 2px solid {hover_color};
                    background: {hover_bg};
                    color: {hover_color};
                }}
            """)
            uncheck_btn.clicked.connect(lambda _, tid=task["id"]: self.quick_uncomplete(tid))

            # 按钮容器（居中）
            btn_container = QWidget()
            btn_layout = QHBoxLayout(btn_container)
            btn_layout.setContentsMargins(0, 8, 0, 0)
            btn_layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
            btn_layout.addWidget(uncheck_btn)
            self.task_list.setItemWidget(item, 0, btn_container)

            # 任务内容
            content_widget = QWidget()
            content_layout = QHBoxLayout(content_widget)
            content_layout.setContentsMargins(8, 0, 8, 0)
            content_layout.setSpacing(10)

            priority = task["priority"]
            dot_color = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["color"]
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {dot_color}; font-size: 16px; background: transparent; border: none;")
            dot.setFixedWidth(20)
            dot.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(dot)

            title = task["title"]
            if task["type"] == "计划任务":
                title = f"📅 {title}"

            title_label = QLabel(title)
            title_label.setStyleSheet("color: #1d1d1f; font-size: 14px; background: transparent; border: none;")
            content_layout.addWidget(title_label, 1)

            self.task_list.setItemWidget(item, 1, content_widget)

            # 完成时间
            time_label = QLabel(task.get("completed_at", ""))
            time_label.setStyleSheet("color: #8e8e93; font-size: 12px; background: transparent; border: none;")
            self.task_list.setItemWidget(item, 2, time_label)

            bg = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["bg"]
            for col in range(3):
                item.setBackground(col, QColor(bg))

        self.update_stats()

    def quick_complete(self, task_id):
        self.manager.complete_task(task_id)
        if self.searching:
            keyword = self.task_input.text().strip()
            if keyword:
                results = self.manager.search_tasks(keyword)
                self.refresh_search_list(results)
        else:
            self.refresh_task_list()

    def quick_uncomplete(self, task_id):
        """取消完成，回到待办"""
        self.manager.uncomplete_task(task_id)
        if self.searching:
            keyword = self.task_input.text().strip()
            if keyword:
                results = self.manager.search_tasks(keyword)
                self.refresh_search_list(results)
        elif self.showing_history:
            self.refresh_history_list()
        else:
            self.refresh_task_list()

    def update_stats(self):
        stats = self.manager.get_stats()
        self.stats_label.setText(
            f"待办 {stats['total_pending']}  ·  今日完成 {stats['today_completed']}  ·  历史 {stats['total_completed']}"
        )


STYLE = """
QMainWindow { background: transparent; }
QWidget { font-family: "SF Pro Display", "PingFang SC", "Microsoft YaHei", sans-serif; }

#glassContainer {
    background: rgba(255, 255, 255, 0.99999999);
    border-radius: 18px;
    border: 1px solid rgba(0, 0, 0, 0.12);
}

#header {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.8);
}

#timeLabel {
    color: #1d1d1f;
    font-size: 15px;
    font-weight: 600;
}

#weekdayLabel {
    color: #007AFF;
    font-size: 13px;
    font-weight: 500;
}

#windowBtn {
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 14px;
    color: #6e6e73;
    min-width: 28px;
    min-height: 28px;
}
#windowBtn:hover {
    background: rgba(0, 0, 0, 0.06);
}

#closeBtn {
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 4px 10px;
    font-size: 14px;
    color: #6e6e73;
    min-width: 28px;
    min-height: 28px;
}
#closeBtn:hover {
    background: #FF3B30;
    color: white;
}

#headerBtn {
    background: rgba(0, 122, 255, 0.1);
    color: #007AFF;
    border: 1px solid rgba(0, 122, 255, 0.2);
    border-radius: 8px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
}
#headerBtn:hover {
    background: rgba(0, 122, 255, 0.18);
}

#addBtn {
    background: #007AFF;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 7px 18px;
    font-size: 13px;
    font-weight: 600;
}
#addBtn:hover { background: #0056CC; }
#addBtn:pressed { background: #004099; }

#card {
    background: rgba(255, 255, 255, 0.65);
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.75);
}

QTreeWidget {
    background: transparent;
    border: none;
    font-size: 13px;
    color: #1d1d1f;
    outline: none;
}
QTreeWidget::item {
    border-radius: 10px;
    padding: 8px 14px;
    margin: 3px 4px;
    min-height: 40px;
}
QTreeWidget::item:hover {
    background: rgba(0, 122, 255, 0.06) !important;
    border: 1px solid rgba(0, 122, 255, 0.15);
}
QTreeWidget::item:selected {
    background: rgba(0, 122, 255, 0.1) !important;
    border: 1px solid rgba(0, 122, 255, 0.3);
}
QHeaderView::section {
    background: transparent;
    border: none;
    border-bottom: 1px solid rgba(0, 0, 0, 0.06);
    padding: 8px 12px;
    font-size: 11px;
    font-weight: 600;
    color: #8e8e93;
}
QScrollBar:vertical {
    background: transparent;
    width: 7px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(0, 0, 0, 0.12);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover { background: rgba(0, 0, 0, 0.22); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }

#emptyLabel {
    color: #8e8e93;
    font-size: 14px;
}
"""


if __name__ == "__main__":
    # Windows 11 任务栏图标修复 - 必须在创建窗口之前调用
    try:
        myappid = 'Dailyinfo.TaskManager.1.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    icon_path = os.path.join(ICO_DIR, "岚兮儿.ico")
    app_icon = QIcon(icon_path) if os.path.exists(icon_path) else None
    if app_icon:
        app.setWindowIcon(app_icon)

    window = TaskApp()
    window.show()

    # 窗口显示后再次设置图标
    if app_icon:
        window.setWindowIcon(app_icon)

    sys.exit(app.exec())
