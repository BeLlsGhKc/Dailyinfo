# -*- coding: utf-8 -*-
"""
每日任务管理工具 - 苹果毛玻璃风格 v6
"""

import sys
import json
import os
import hashlib
import platform
import getpass
import threading
from datetime import datetime, date, timedelta
from ctypes import windll, c_int, c_short, byref, sizeof, Structure, c_uint, POINTER, wintypes, string_at, create_string_buffer, c_void_p

# pymysql 可选依赖
try:
    import pymysql
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QFrame, QGraphicsDropShadowEffect, QMessageBox, QDialog,
    QTextEdit, QDateEdit, QHeaderView, QCalendarWidget, QMenu, QComboBox,
    QCheckBox
)
from PySide6.QtCore import Qt, QTimer, QDate, QEvent, QRect, Signal, QObject
from PySide6.QtGui import QColor, QIcon, QTextCharFormat, QPainter, QPen, QAction


def clean_button_focus(button):
    """关闭按钮键盘焦点框，避免鼠标点击后留下虚线残影。"""
    button.setFocusPolicy(Qt.NoFocus)
    button.setAutoDefault(False)
    button.setDefault(False)
    return button


# 中国节假日数据（2026年）
# 正日子显示节日名，其他假期日显示"节日名假期"
HOLIDAYS = {
    # 元旦
    "2026-01-01": "元旦",
    "2026-01-02": "元旦假期",
    "2026-01-03": "元旦假期",
    # 春节
    "2026-02-15": "春节假期",
    "2026-02-16": "春节假期",
    "2026-02-17": "春节",
    "2026-02-18": "春节假期",
    "2026-02-19": "春节假期",
    "2026-02-20": "春节假期",
    "2026-02-21": "春节假期",
    "2026-02-22": "春节假期",
    "2026-02-23": "春节假期",
    # 清明节
    "2026-04-04": "清明节假期",
    "2026-04-05": "清明节",
    "2026-04-06": "清明节假期",
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


ADJUSTED_WORKDAYS = {
    "2026-01-04": "调休上班",
    "2026-02-14": "调休上班",
    "2026-02-28": "调休上班",
    "2026-05-09": "调休上班",
    "2026-09-20": "调休上班",
    "2026-10-10": "调休上班",
}


SOLAR_FESTIVALS = {
    (2, 14): "情人节",
    (3, 8): "妇女节",
    (3, 12): "植树节",
    (4, 1): "愚人节",
    (5, 4): "青年节",
    (6, 1): "儿童节",
    (9, 10): "教师节",
    (10, 31): "万圣夜",
    (12, 24): "平安夜",
    (12, 25): "圣诞节",
}


SOLAR_TERMS = {
    "2026-01-05": "小寒",
    "2026-01-20": "大寒",
    "2026-02-04": "立春",
    "2026-02-18": "雨水",
    "2026-03-05": "惊蛰",
    "2026-03-20": "春分",
    "2026-04-05": "清明",
    "2026-04-20": "谷雨",
    "2026-05-05": "立夏",
    "2026-05-21": "小满",
    "2026-06-05": "芒种",
    "2026-06-21": "夏至",
    "2026-07-07": "小暑",
    "2026-07-23": "大暑",
    "2026-08-07": "立秋",
    "2026-08-23": "处暑",
    "2026-09-07": "白露",
    "2026-09-23": "秋分",
    "2026-10-08": "寒露",
    "2026-10-23": "霜降",
    "2026-11-07": "立冬",
    "2026-11-22": "小雪",
    "2026-12-07": "大雪",
    "2026-12-22": "冬至",
}


LUNAR_YEAR_INFO = {
    2024: 0x04b60,
    2025: 0x0a6e6,
    2026: 0x0a4e0,
    2027: 0x0d260,
}
LUNAR_BASE_DATE = date(2024, 2, 10)  # 甲辰年正月初一
HEAVENLY_STEMS = "甲乙丙丁戊己庚辛壬癸"
EARTHLY_BRANCHES = "子丑寅卯辰巳午未申酉戌亥"
LUNAR_MONTH_NAMES = ["正月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "冬月", "腊月"]
LUNAR_DAY_NAMES = [
    "初一", "初二", "初三", "初四", "初五", "初六", "初七", "初八", "初九", "初十",
    "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十",
    "廿一", "廿二", "廿三", "廿四", "廿五", "廿六", "廿七", "廿八", "廿九", "三十",
]
LUNAR_FESTIVALS = {
    (1, 1): "春节",
    (1, 15): "元宵节",
    (2, 2): "龙抬头",
    (5, 5): "端午节",
    (7, 7): "七夕",
    (7, 15): "中元节",
    (8, 15): "中秋节",
    (9, 9): "重阳节",
    (12, 8): "腊八节",
}


def lunar_leap_month(year):
    """返回农历闰月，0 表示无闰月。"""
    return LUNAR_YEAR_INFO[year] & 0xF


def lunar_leap_days(year):
    """返回农历闰月天数。"""
    if lunar_leap_month(year) == 0:
        return 0
    return 30 if LUNAR_YEAR_INFO[year] & 0x10000 else 29


def lunar_month_days(year, month):
    """返回农历指定月份天数。"""
    return 30 if LUNAR_YEAR_INFO[year] & (0x10000 >> month) else 29


def lunar_year_days(year):
    """返回农历年份总天数。"""
    total = 0
    for month in range(1, 13):
        total += lunar_month_days(year, month)
    return total + lunar_leap_days(year)


def solar_to_lunar(solar_date):
    """把公历日期转换为 2025-2027 日历范围内的农历日期。"""
    offset = (solar_date - LUNAR_BASE_DATE).days
    if offset < 0:
        return None

    lunar_year = 2024
    while lunar_year in LUNAR_YEAR_INFO:
        year_days = lunar_year_days(lunar_year)
        if offset < year_days:
            break
        offset -= year_days
        lunar_year += 1

    if lunar_year not in LUNAR_YEAR_INFO:
        return None

    leap_month = lunar_leap_month(lunar_year)
    lunar_month = 1
    is_leap_month = False

    while lunar_month <= 12:
        month_days = lunar_leap_days(lunar_year) if is_leap_month else lunar_month_days(lunar_year, lunar_month)
        if offset < month_days:
            return {
                "year": lunar_year,
                "month": lunar_month,
                "day": offset + 1,
                "is_leap_month": is_leap_month,
            }

        offset -= month_days
        if leap_month == lunar_month and not is_leap_month:
            is_leap_month = True
        else:
            is_leap_month = False
            lunar_month += 1

    return None


def lunar_ganzhi_year(year):
    """返回农历干支年。"""
    return f"{HEAVENLY_STEMS[(year - 4) % 10]}{EARTHLY_BRANCHES[(year - 4) % 12]}"


def format_lunar_info(lunar_info):
    """格式化农历信息。"""
    month_name = LUNAR_MONTH_NAMES[lunar_info["month"] - 1]
    if lunar_info["is_leap_month"]:
        month_name = f"闰{month_name}"
    day_name = LUNAR_DAY_NAMES[lunar_info["day"] - 1]
    return f"{lunar_ganzhi_year(lunar_info['year'])}年 农历 {month_name}{day_name}"


def add_calendar_label(labels, name, kind):
    """追加日历标签，避免重复显示。"""
    if not name:
        return
    for existing_name, _ in labels:
        if existing_name == name:
            return
    labels.append((name, kind))


def nth_weekday_of_month(year, month, weekday, nth):
    """返回某月第 nth 个 weekday 日期，weekday 使用 Python 标准：周一为 0。"""
    current = date(year, month, 1)
    offset = (weekday - current.weekday()) % 7
    return current.replace(day=1 + offset + (nth - 1) * 7)


def solar_weekday_festival(solar_date):
    """返回按第几个星期几计算的公历节日。"""
    if solar_date == nth_weekday_of_month(solar_date.year, 5, 6, 2):
        return "母亲节"
    if solar_date == nth_weekday_of_month(solar_date.year, 6, 6, 3):
        return "父亲节"
    return ""


def has_equivalent_label(labels, name):
    """判断是否已有等价标签，例如清明节已覆盖清明。"""
    for existing_name, _ in labels:
        if existing_name == name or existing_name == f"{name}节":
            return True
    return False


def calendar_day_labels(solar_date, lunar_info):
    """返回节日、节气、假期和调休标签。"""
    date_str = solar_date.strftime("%Y-%m-%d")
    labels = []

    add_calendar_label(labels, ADJUSTED_WORKDAYS.get(date_str, ""), "workday")
    add_calendar_label(labels, HOLIDAYS.get(date_str, ""), "holiday")

    if not lunar_info["is_leap_month"]:
        festival = LUNAR_FESTIVALS.get((lunar_info["month"], lunar_info["day"]))
        if festival:
            add_calendar_label(labels, festival, "festival")

    add_calendar_label(labels, SOLAR_FESTIVALS.get((solar_date.month, solar_date.day), ""), "festival")
    add_calendar_label(labels, solar_weekday_festival(solar_date), "festival")

    solar_term = SOLAR_TERMS.get(date_str, "")
    if solar_term and not has_equivalent_label(labels, solar_term):
        add_calendar_label(labels, solar_term, "solar_term")

    return labels


def calendar_label_for_qdate(qdate):
    """返回 qdate 对应的节日、节气、假期和调休标签。"""
    solar_date = date(qdate.year(), qdate.month(), qdate.day())
    lunar_info = solar_to_lunar(solar_date)
    if lunar_info is None:
        date_str = qdate.toString("yyyy-MM-dd")
        labels = []
        add_calendar_label(labels, ADJUSTED_WORKDAYS.get(date_str, ""), "workday")
        add_calendar_label(labels, HOLIDAYS.get(date_str, ""), "holiday")
        add_calendar_label(labels, SOLAR_TERMS.get(date_str, ""), "solar_term")
        return labels
    return calendar_day_labels(solar_date, lunar_info)


def format_calendar_info(qdate):
    """返回底部日历信息文本和是否带节日标签。"""
    solar_date = date(qdate.year(), qdate.month(), qdate.day())
    lunar_info = solar_to_lunar(solar_date)
    if lunar_info is None:
        return "农历信息暂不支持", []

    labels = calendar_day_labels(solar_date, lunar_info)
    text = format_lunar_info(lunar_info)
    if labels:
        label_text = " ".join(name for name, _ in labels)
        return f"{text} {label_text}", [kind for _, kind in labels]
    return text, []


def calendar_info_style(label_kinds):
    """底部日历信息样式。"""
    if "workday" in label_kinds:
        return "color: #C76A00; font-size: 14px; font-weight: 600; padding: 8px;"
    if label_kinds:
        return "color: #00C7BE; font-size: 14px; font-weight: 600; padding: 8px;"
    return "color: #8e8e93; font-size: 13px; font-weight: 500; padding: 8px;"


class HolidayCalendar(QCalendarWidget):
    """带节假日高亮的日历控件"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumDate(QDate(2025, 1, 1))
        self.setMaximumDate(QDate(2027, 12, 31))
        self.setSelectedDate(QDate.currentDate())

    def paintCell(self, painter, rect, qdate):
        """自定义单元格绘制"""
        is_today = qdate == QDate.currentDate()
        is_selected = qdate == self.selectedDate()
        labels = calendar_label_for_qdate(qdate)
        label_names = [name for name, _ in labels]
        label_kinds = [kind for _, kind in labels]
        is_workday = "workday" in label_kinds
        is_holiday = bool(labels)

        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        if is_selected:
            # 选中状态：蓝色圆角背景
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(0, 122, 255))
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 6, 6)
            text_color = QColor(255, 255, 255)
        elif is_today:
            # 今天：深灰色背景，无边框
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(200, 200, 200))
            painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 6, 6)
            text_color = QColor(29, 29, 31)
        elif is_holiday:
            # 节假日、节气、调休工作日：轻色背景区分状态
            color = QColor(255, 149, 0, 40) if is_workday else QColor(0, 199, 190, 40)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 6, 6)
            if is_workday:
                text_color = QColor(199, 106, 0)  # 橙色（调休上班）
            elif any(kind == "festival" for kind in label_kinds) or any(not name.endswith("假期") and kind == "holiday" for name, kind in labels):
                text_color = QColor(255, 59, 48)  # 红色（正日子）
            elif label_names:
                text_color = QColor(0, 199, 190)  # 青色（假期日、节气）
            else:
                text_color = QColor(29, 29, 31)
        else:
            # 普通日期
            text_color = QColor(29, 29, 31)

        # 绘制日期文字
        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignCenter, str(qdate.day()))
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

# 配置文件路径
SETTINGS_FILE = os.path.join(DATA_DIR, "settings.json")
MYSQL_CONNECT_TIMEOUT = 5
MYSQL_READ_TIMEOUT = 8
MYSQL_WRITE_TIMEOUT = 8

# 默认配置（JSON 始终为主存储，MySQL 为可选后台同步）
DEFAULT_SETTINGS = {
    "mysql_enabled": False,
    "mysql": {
        "host": "",
        "port": 3306,
        "user": "",
        "password": "",
        "database": "dailyinfo"
    }
}


# ========== 密码加密 ==========
try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


def _get_machine_key():
    """基于机器信息生成加密密钥"""
    # 组合机器特征信息
    machine_info = f"{platform.node()}-{getpass.getuser()}-{platform.machine()}"
    # 生成 32 字节的密钥（Fernet 要求）
    key_bytes = hashlib.sha256(machine_info.encode()).digest()
    # Fernet 需要 base64 编码的 32 字节密钥
    import base64
    return base64.urlsafe_b64encode(key_bytes)


def encrypt_password(plain_text):
    """加密密码"""
    if not plain_text or not HAS_CRYPTO:
        return plain_text
    try:
        f = Fernet(_get_machine_key())
        return f.encrypt(plain_text.encode()).decode()
    except Exception:
        return plain_text


def decrypt_password(cipher_text):
    """解密密码"""
    if not cipher_text or not HAS_CRYPTO:
        return cipher_text
    try:
        f = Fernet(_get_machine_key())
        return f.decrypt(cipher_text.encode()).decode()
    except Exception:
        # 解密失败说明是明文或密钥不匹配，返回原文
        return cipher_text


def load_settings():
    """读取配置文件，不存在则返回默认配置"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)

            # 旧配置自动升级：storage/mysql_enabled 迁移
            if "storage" in settings:
                old_storage = settings.pop("storage", "json")
                settings.pop("last_storage", None)
                if old_storage == "mysql":
                    mysql_cfg = settings.get("mysql", {})
                    if mysql_cfg.get("host") and mysql_cfg.get("user"):
                        settings["mysql_enabled"] = True
                else:
                    settings["mysql_enabled"] = settings.get("mysql_enabled", False)
                # 立即保存升级后的配置
                save_settings(settings)

            # 兼容旧配置，补充缺失字段
            for key, value in DEFAULT_SETTINGS.items():
                if key not in settings:
                    settings[key] = value
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if k not in settings[key]:
                            settings[key][k] = v

            # 解密密码
            if "mysql" in settings and "password" in settings["mysql"]:
                settings["mysql"]["password"] = decrypt_password(settings["mysql"]["password"])
            return settings
        except Exception:
            pass
    return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """保存配置文件（加密密码）"""
    # 保存前加密密码
    save_data = settings.copy()
    if "mysql" in save_data and "password" in save_data["mysql"]:
        save_data["mysql"] = save_data["mysql"].copy()
        save_data["mysql"]["password"] = encrypt_password(save_data["mysql"]["password"])
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(save_data, f, ensure_ascii=False, indent=2)


# Windows 毛玻璃 API
class ACCENT_POLICY(Structure):
    _fields_ = [("AccentState", c_uint), ("AccentFlags", c_uint),
                ("GradientColor", c_uint), ("AnimationId", c_uint)]

class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [("Attribute", c_int), ("Data", POINTER(ACCENT_POLICY)),
                ("SizeOfData", c_uint)]


class MSG(Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", wintypes.POINT),
    ]


WM_NCHITTEST = 0x0084
HTLEFT = 10
HTRIGHT = 11
HTTOP = 12
HTTOPLEFT = 13
HTTOPRIGHT = 14
HTBOTTOM = 15
HTBOTTOMLEFT = 16
HTBOTTOMRIGHT = 17


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


class TaskManager(QObject):
    # MySQL 异步初始化完成后发出信号
    mysql_ready = Signal()
    # MySQL 初始化失败信号
    mysql_failed = Signal()

    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.data_file = os.path.join(DATA_DIR, "tasks.json")
        self.db = None
        self._mysql_initialized = False
        self._mysql_lock = threading.Lock()  # 保护 db 连接
        self._pending_sync_ids = set()       # 待同步到 MySQL 的 task id
        self._full_sync_needed = False       # 是否需要全量同步

        # 防抖写入：连续操作只触发一次写入
        self._save_timer = None  # QTimer，在 TaskApp 中初始化
        self._save_delay = 500  # 毫秒
        self._mysql_sync_timer = None  # MySQL 同步 QTimer，在 TaskApp 中初始化

        # MySQL 启用状态检查
        self._mysql_enabled = self.settings.get("mysql_enabled", False)
        if self._mysql_enabled:
            mysql_cfg = self.settings.get("mysql", {})
            if not mysql_cfg.get("host") or not mysql_cfg.get("user"):
                self._mysql_enabled = False
            if not HAS_PYMYSQL:
                print("警告: pymysql 未安装，MySQL 同步已禁用")
                self._mysql_enabled = False

        # 永远从 JSON 加载，UI 立即可用
        self.tasks = self._load_from_json()
        self.loading_remote = False

    def init_mysql_async(self):
        """异步连接 MySQL 并拉取最新数据合并到本地"""
        if not self._mysql_enabled:
            return

        def _do_init():
            # 尝试连接 MySQL
            with self._mysql_lock:
                if not self._init_mysql():
                    print("MySQL 连接失败，仅使用本地数据")
                    self.mysql_failed.emit()
                    return

            # 连接成功，从 MySQL 加载数据
            with self._mysql_lock:
                mysql_data = self._load_from_mysql()

            if mysql_data and (mysql_data["pending"] or mysql_data["completed"]):
                # 合并: 本地 JSON 为主，MySQL 数据合并进来
                merged = self._merge_tasks(self.tasks, mysql_data)
                self.tasks = merged
                # 将合并结果写回 JSON
                self._save_to_json()
                # 将合并结果全量同步回 MySQL（确保两端一致）
                with self._mysql_lock:
                    self._full_sync_to_mysql()

            # 通知 UI 刷新
            self.mysql_ready.emit()

        threading.Thread(target=_do_init, daemon=True).start()

    def _sync_mysql(self, task_id=None):
        """将变更异步同步到 MySQL（如果已启用）"""
        if not self._mysql_enabled or not self._mysql_initialized:
            return
        if task_id:
            self._pending_sync_ids.add(task_id)
        self._schedule_mysql_sync()

    def _schedule_mysql_sync(self):
        """防抖 MySQL 同步"""
        if self._mysql_sync_timer and not self._mysql_sync_timer.isActive():
            self._mysql_sync_timer.start(800)

    def _do_mysql_sync(self):
        """实际执行 MySQL 同步（在后台线程）"""
        if not self._mysql_enabled or not self._mysql_initialized:
            return
        if not self._pending_sync_ids and not self._full_sync_needed:
            return

        def _sync():
            with self._mysql_lock:
                try:
                    if self._full_sync_needed:
                        self._full_sync_to_mysql()
                        self._full_sync_needed = False
                        self._pending_sync_ids.clear()
                    elif self._pending_sync_ids:
                        ids = set(self._pending_sync_ids)
                        self._pending_sync_ids.clear()
                        self._incremental_sync_to_mysql(ids)
                except Exception as e:
                    print(f"MySQL 同步失败: {e}")
                    self._full_sync_needed = True

        threading.Thread(target=_sync, daemon=True).start()

    def _incremental_sync_to_mysql(self, task_ids):
        """增量同步指定任务到 MySQL（必须在 _mysql_lock 保护下调用）"""
        for task_id in task_ids:
            task, status = self._find_task_by_id(task_id)
            if task:
                self._mysql_update_task(task_id, status, task)
            else:
                self._mysql_delete_task(task_id)

    def _find_task_by_id(self, task_id):
        """按 ID 查找任务，返回 (task, status)"""
        for task in self.tasks["pending"]:
            if task["id"] == task_id:
                return task, "pending"
        for task in self.tasks["completed"]:
            if task["id"] == task_id:
                return task, "completed"
        return None, None

    def sync_to_mysql_on_close(self):
        """关闭时同步数据到 MySQL（同步阻塞，由 closeEvent 调用）"""
        if not self._mysql_enabled:
            return
        if not self._mysql_initialized:
            with self._mysql_lock:
                if not self._init_mysql():
                    print("关闭时 MySQL 连接失败，跳过同步")
                    return
        try:
            with self._mysql_lock:
                self._full_sync_to_mysql()
            print("关闭时 MySQL 同步完成")
        except Exception as e:
            print(f"关闭时 MySQL 同步失败: {e}")

    def _schedule_save(self):
        """防抖写入：连续操作只触发一次写入，由 TaskApp 中的 QTimer 驱动"""
        if self._save_timer and self._save_timer.isActive():
            self._save_timer.stop()
        self._save_timer.start(self._save_delay)

    def _do_save(self):
        """防抖写入: 永远写 JSON，MySQL 异步同步"""
        self._save_to_json()
        if self._mysql_enabled and self._mysql_initialized:
            self._full_sync_needed = True
            self._schedule_mysql_sync()

    def _init_mysql(self):
        """初始化 MySQL 连接并建表"""
        if self._mysql_initialized and self.db is not None:
            try:
                self.db.ping(reconnect=True)
                return True
            except:
                self.db = None

        mysql_cfg = self.settings["mysql"]
        try:
            self.db = pymysql.connect(
                host=mysql_cfg["host"],
                port=int(mysql_cfg["port"]),
                user=mysql_cfg["user"],
                password=mysql_cfg["password"],
                database=mysql_cfg["database"],
                charset="utf8mb4",
                connect_timeout=MYSQL_CONNECT_TIMEOUT,
                read_timeout=MYSQL_READ_TIMEOUT,
                write_timeout=MYSQL_WRITE_TIMEOUT,
                cursorclass=pymysql.cursors.DictCursor
            )
            self._create_table()
            self._mysql_initialized = True
            return True
        except Exception as e:
            print(f"MySQL 连接失败: {e}")
            self.db = None
            return False

    def _ensure_mysql(self):
        """确保 MySQL 连接可用"""
        if not self._mysql_initialized:
            return self._init_mysql()
        return True

    def _create_table(self):
        """自动建表"""
        sql = """
        CREATE TABLE IF NOT EXISTS tasks (
            id VARCHAR(30) PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT,
            priority VARCHAR(10),
            type VARCHAR(20),
            created_at VARCHAR(20),
            deadline VARCHAR(20),
            completed_at VARCHAR(20) NULL,
            pinned TINYINT DEFAULT 0,
            status VARCHAR(10) NOT NULL DEFAULT 'pending'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
        with self.db.cursor() as cursor:
            cursor.execute(sql)
        self.db.commit()

    def load_data(self):
        """加载数据（始终从 JSON 读取）"""
        return self._load_from_json()

    def _load_from_json(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"pending": [], "completed": []}
        return {"pending": [], "completed": []}

    def _merge_tasks(self, data_a, data_b):
        """合并两个数据源的任务，按 ID 去重，保留更新的版本"""
        merged = {"pending": [], "completed": []}
        seen = {}

        # 合并所有任务到一个列表
        all_tasks = []
        for task in data_a["pending"]:
            all_tasks.append(("pending", task))
        for task in data_a["completed"]:
            all_tasks.append(("completed", task))
        for task in data_b["pending"]:
            all_tasks.append(("pending", task))
        for task in data_b["completed"]:
            all_tasks.append(("completed", task))

        # 按 ID 去重，保留更新时间较新的
        for status, task in all_tasks:
            task_id = task["id"]
            if task_id in seen:
                _, existing_task = seen[task_id]
                # 比较 completed_at 或 created_at
                existing_time = existing_task.get("completed_at") or existing_task.get("created_at", "")
                new_time = task.get("completed_at") or task.get("created_at", "")
                if new_time >= existing_time:
                    seen[task_id] = (status, task)
            else:
                seen[task_id] = (status, task)

        # 分类到 pending 和 completed
        for status, task in seen.values():
            merged[status].append(task)

        return merged

    def _load_from_mysql(self):
        """从 MySQL 加载数据"""
        tasks = {"pending": [], "completed": []}
        try:
            with self.db.cursor() as cursor:
                cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC")
                rows = cursor.fetchall()
                for row in rows:
                    task = {
                        "id": row["id"],
                        "title": row["title"],
                        "content": row["content"] or "",
                        "priority": row["priority"],
                        "type": row["type"],
                        "created_at": row["created_at"],
                        "deadline": row["deadline"] or "",
                        "completed_at": row["completed_at"],
                        "pinned": bool(row["pinned"])
                    }
                    if row["status"] == "completed":
                        tasks["completed"].append(task)
                    else:
                        tasks["pending"].append(task)
        except Exception as e:
            print(f"MySQL 读取失败: {e}")
        return tasks

    def save_data(self):
        """兼容接口，统一走防抖写入"""
        self._do_save()

    def _save_to_json(self):
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.tasks, f, ensure_ascii=False, indent=2)

    def _full_sync_to_mysql(self):
        """全量同步当前数据到 MySQL（必须在 _mysql_lock 保护下调用）"""
        try:
            with self.db.cursor() as cursor:
                cursor.execute("DELETE FROM tasks")
                for status in ["pending", "completed"]:
                    for task in self.tasks[status]:
                        cursor.execute(
                            """INSERT INTO tasks
                            (id, title, content, priority, type, created_at, deadline, completed_at, pinned, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (
                                task["id"], task["title"], task.get("content", ""),
                                task["priority"], task["type"], task["created_at"],
                                task.get("deadline", ""), task.get("completed_at"),
                                1 if task.get("pinned") else 0, status
                            )
                        )
            self.db.commit()
        except Exception as e:
            print(f"MySQL 写入失败: {e}")
            try:
                self._init_mysql()
            except:
                pass

    def _mysql_update_task(self, task_id, status, task):
        """增量更新单条任务到 MySQL"""
        if not self._ensure_mysql():
            return
        try:
            with self.db.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO tasks
                    (id, title, content, priority, type, created_at, deadline, completed_at, pinned, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    title=VALUES(title), content=VALUES(content), priority=VALUES(priority),
                    type=VALUES(type), deadline=VALUES(deadline), completed_at=VALUES(completed_at),
                    pinned=VALUES(pinned), status=VALUES(status)""",
                    (
                        task["id"], task["title"], task.get("content", ""),
                        task["priority"], task["type"], task["created_at"],
                        task.get("deadline", ""), task.get("completed_at"),
                        1 if task.get("pinned") else 0, status
                    )
                )
            self.db.commit()
        except Exception as e:
            print(f"MySQL 更新失败: {e}")

    def _mysql_delete_task(self, task_id):
        """从 MySQL 删除单条任务"""
        if not self._ensure_mysql():
            return
        try:
            with self.db.cursor() as cursor:
                cursor.execute("DELETE FROM tasks WHERE id=%s", (task_id,))
            self.db.commit()
        except Exception as e:
            print(f"MySQL 删除失败: {e}")

    def add_task(self, title, priority="中", task_type="普通", content="", deadline=""):
        task = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "title": title,
            "content": content,
            "priority": priority,
            "type": task_type,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "deadline": deadline,
            "completed_at": None,
            "pinned": False
        }
        self.tasks["pending"].append(task)
        self._sync_mysql(task["id"])
        self._schedule_save()
        return task

    def update_task(self, task_id, updates):
        # 同时查找待办和已完成任务
        for task in self.tasks["pending"]:
            if task["id"] == task_id:
                task.update(updates)
                self._sync_mysql(task_id)
                self._schedule_save()
                return True
        for task in self.tasks["completed"]:
            if task["id"] == task_id:
                completed_at = task.get("completed_at")
                task.update(updates)
                if completed_at:
                    task["completed_at"] = completed_at
                self._sync_mysql(task_id)
                self._schedule_save()
                return True
        return False

    def complete_task(self, task_id):
        for i, task in enumerate(self.tasks["pending"]):
            if task["id"] == task_id:
                task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.tasks["completed"].insert(0, task)
                self.tasks["pending"].pop(i)
                self._sync_mysql(task_id)
                self._schedule_save()
                return True
        return False

    def delete_task(self, task_id):
        for i, task in enumerate(self.tasks["pending"]):
            if task["id"] == task_id:
                self.tasks["pending"].pop(i)
                self._sync_mysql(task_id)
                self._schedule_save()
                return True
        return False

    def uncomplete_task(self, task_id):
        """取消完成，移回待办"""
        for i, task in enumerate(self.tasks["completed"]):
            if task["id"] == task_id:
                task["completed_at"] = None
                self.tasks["pending"].append(task)
                self.tasks["completed"].pop(i)
                self._sync_mysql(task_id)
                self._schedule_save()
                return True
        return False

    def toggle_pin_task(self, task_id):
        """切换任务置顶状态"""
        for task in self.tasks["completed"]:
            if task["id"] == task_id:
                task["pinned"] = not task.get("pinned", False)
                self._sync_mysql(task_id)
                self._schedule_save()
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
                border-radius: 10px;
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
        clean_button_focus(close_btn)
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
        self._setup_edit_context_menu(self.title_edit)
        TaskApp.apply_input_shadow(self.title_edit)
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
        self._setup_edit_context_menu(self.content_edit)
        TaskApp.apply_input_shadow(self.content_edit)
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

    def _setup_edit_context_menu(self, edit_widget):
        """为 QLineEdit 或 QTextEdit 设置中文右键菜单"""
        edit_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        edit_widget.customContextMenuRequested.connect(lambda pos, w=edit_widget: self._show_edit_context_menu(pos, w))

    def _show_edit_context_menu(self, pos, edit_widget):
        """显示中文编辑右键菜单（支持 QLineEdit 和 QTextEdit）"""
        menu = QMenu(self)
        menu.setStyleSheet(TaskApp.get_context_menu_style())

        # 判断控件类型
        is_line_edit = isinstance(edit_widget, QLineEdit)
        is_text_edit = isinstance(edit_widget, QTextEdit)

        # 获取选中状态
        if is_line_edit:
            has_selection = edit_widget.hasSelectedText()
            has_text = len(edit_widget.text()) > 0
        else:
            has_selection = edit_widget.textCursor().hasSelection()
            has_text = len(edit_widget.toPlainText()) > 0

        has_clipboard = QApplication.clipboard().text() != ""

        # 撤销
        undo_action = QAction("撤销", self)
        undo_action.setEnabled(edit_widget.isUndoAvailable())
        undo_action.triggered.connect(edit_widget.undo)
        menu.addAction(undo_action)

        # 重做
        redo_action = QAction("重做", self)
        redo_action.setEnabled(edit_widget.isRedoAvailable())
        redo_action.triggered.connect(edit_widget.redo)
        menu.addAction(redo_action)

        menu.addSeparator()

        # 剪切
        cut_action = QAction("剪切", self)
        cut_action.setEnabled(has_selection)
        cut_action.triggered.connect(edit_widget.cut)
        menu.addAction(cut_action)

        # 复制
        copy_action = QAction("复制", self)
        copy_action.setEnabled(has_selection)
        copy_action.triggered.connect(edit_widget.copy)
        menu.addAction(copy_action)

        # 粘贴
        paste_action = QAction("粘贴", self)
        paste_action.setEnabled(has_clipboard)
        paste_action.triggered.connect(edit_widget.paste)
        menu.addAction(paste_action)

        # 删除
        delete_action = QAction("删除", self)
        delete_action.setEnabled(has_selection)
        if is_line_edit:
            delete_action.triggered.connect(edit_widget.del_)
        else:
            delete_action.triggered.connect(lambda: edit_widget.textCursor().removeSelectedText())
        menu.addAction(delete_action)

        menu.addSeparator()

        # 全选
        select_all_action = QAction("全选", self)
        select_all_action.setEnabled(has_text)
        select_all_action.triggered.connect(edit_widget.selectAll)
        menu.addAction(select_all_action)

        menu.exec(edit_widget.mapToGlobal(pos))

    def _btn(self, text, bg, hover):
        btn = QPushButton(text)
        clean_button_focus(btn)
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
            dlg.setStyleSheet("QDialog { background: rgba(255,255,255,0.98); border-radius: 10px; }")

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
                clean_button_focus(btn)
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
            clean_button_focus(cancel_btn)
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
            dlg.setStyleSheet("QDialog { background: rgba(255,255,255,0.98); border-radius: 10px; }")

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
            # 阴影效果
            TaskApp.apply_input_shadow(date_edit)
            layout.addWidget(date_edit)

            btn_layout = QHBoxLayout()
            btn_layout.setSpacing(8)

            cancel_btn = QPushButton("取消")
            clean_button_focus(cancel_btn)
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
            clean_button_focus(ok_btn)
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


# ========== 设置对话框 ==========
class SettingsDialog(QDialog):
    """设置弹窗：数据存储配置"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(420, 540)
        self._drag_pos = None
        self.settings = load_settings()
        self.result_saved = False
        self._setup_ui()

    def _setup_ui(self):
        # 外层阴影容器
        shadow_frame = QFrame(self)
        shadow_frame.setGeometry(10, 10, 400, 520)
        shadow_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 16px;
                border: 1px solid rgba(0, 0, 0, 0.08);
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow_frame.setGraphicsEffect(shadow)

        # 主容器
        container = QWidget(self)
        container.setGeometry(10, 10, 400, 520)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # 标题栏
        title_bar = QHBoxLayout()
        title_label = QLabel("⚙ 设置")
        title_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #1d1d1f;")
        title_bar.addWidget(title_label)
        title_bar.addStretch()
        close_btn = WindowControlButton("close")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(self.reject)
        title_bar.addWidget(close_btn)
        layout.addLayout(title_bar)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("color: #e0e0e0;")
        layout.addWidget(line)

        # MySQL 启用开关
        mysql_toggle_row = QHBoxLayout()
        mysql_label = QLabel("启用云端同步 (MySQL)")
        mysql_label.setStyleSheet("font-size: 14px; font-weight: 500; color: #1d1d1f;")
        mysql_toggle_row.addWidget(mysql_label)
        mysql_toggle_row.addStretch()

        self.mysql_enabled_cb = QCheckBox()
        self.mysql_enabled_cb.setChecked(self.settings.get("mysql_enabled", False))
        self.mysql_enabled_cb.stateChanged.connect(self._on_mysql_toggled)
        mysql_toggle_row.addWidget(self.mysql_enabled_cb)
        layout.addLayout(mysql_toggle_row)

        # 如果没安装 pymysql，显示提示
        if not HAS_PYMYSQL:
            mysql_hint = QLabel("⚠️ 使用 MySQL 需安装 pymysql: pip install pymysql")
            mysql_hint.setStyleSheet("font-size: 11px; color: #FF9500; margin-top: 4px;")
            layout.addWidget(mysql_hint)

        # MySQL 配置区域
        self.mysql_config = QWidget()
        mysql_layout = QVBoxLayout(self.mysql_config)
        mysql_layout.setContentsMargins(8, 16, 8, 0)
        mysql_layout.setSpacing(16)

        mysql_cfg = self.settings.get("mysql", {})
        label_width = 70
        label_style = "font-size: 12px; color: #636366; padding-top: 7px; font-weight: 500;"

        # 主机地址
        host_row = QHBoxLayout()
        host_row.setAlignment(Qt.AlignVCenter)
        host_label = QLabel("主机地址:")
        host_label.setFixedWidth(label_width)
        host_label.setStyleSheet(label_style)
        host_label.setAlignment(Qt.AlignVCenter)
        self.host_input = QLineEdit(mysql_cfg.get("host", ""))
        self.host_input.setPlaceholderText("例如: 127.0.0.1")
        self._style_input(self.host_input)
        host_row.addWidget(host_label)
        host_row.addWidget(self.host_input)
        mysql_layout.addLayout(host_row)

        # 端口
        port_row = QHBoxLayout()
        port_row.setAlignment(Qt.AlignVCenter)
        port_label = QLabel("端口:")
        port_label.setFixedWidth(label_width)
        port_label.setStyleSheet(label_style)
        port_label.setAlignment(Qt.AlignVCenter)
        self.port_input = QLineEdit(str(mysql_cfg.get("port", 3306)))
        self.port_input.setPlaceholderText("3306")
        self._style_input(self.port_input)
        port_row.addWidget(port_label)
        port_row.addWidget(self.port_input)
        mysql_layout.addLayout(port_row)

        # 用户名
        user_row = QHBoxLayout()
        user_row.setAlignment(Qt.AlignVCenter)
        user_label = QLabel("用户名:")
        user_label.setFixedWidth(label_width)
        user_label.setStyleSheet(label_style)
        user_label.setAlignment(Qt.AlignVCenter)
        self.user_input = QLineEdit(mysql_cfg.get("user", ""))
        self.user_input.setPlaceholderText("数据库用户名")
        self._style_input(self.user_input)
        user_row.addWidget(user_label)
        user_row.addWidget(self.user_input)
        mysql_layout.addLayout(user_row)

        # 密码
        pwd_row = QHBoxLayout()
        pwd_row.setAlignment(Qt.AlignVCenter)
        pwd_label = QLabel("密码:")
        pwd_label.setFixedWidth(label_width)
        pwd_label.setStyleSheet(label_style)
        pwd_label.setAlignment(Qt.AlignVCenter)
        self.pwd_input = QLineEdit(mysql_cfg.get("password", ""))
        self.pwd_input.setPlaceholderText("数据库密码")
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self._style_input(self.pwd_input)
        pwd_row.addWidget(pwd_label)
        pwd_row.addWidget(self.pwd_input)
        mysql_layout.addLayout(pwd_row)

        # 数据库名
        db_row = QHBoxLayout()
        db_row.setAlignment(Qt.AlignVCenter)
        db_label = QLabel("数据库名:")
        db_label.setFixedWidth(label_width)
        db_label.setStyleSheet(label_style)
        db_label.setAlignment(Qt.AlignVCenter)
        self.db_input = QLineEdit(mysql_cfg.get("database", "dailyinfo"))
        self.db_input.setPlaceholderText("dailyinfo")
        self._style_input(self.db_input)
        db_row.addWidget(db_label)
        db_row.addWidget(self.db_input)
        mysql_layout.addLayout(db_row)

        # 测试连接按钮
        self.test_btn = QPushButton("测试连接")
        self.test_btn.setFixedHeight(32)
        self.test_btn.setCursor(Qt.PointingHandCursor)
        self.test_btn.setStyleSheet("""
            QPushButton {
                background: rgba(0, 122, 255, 0.1);
                color: #007AFF;
                border: 1px solid rgba(0, 122, 255, 0.2);
                border-radius: 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(0, 122, 255, 0.18);
            }
        """)
        self.test_btn.clicked.connect(self._test_connection)
        mysql_layout.addWidget(self.test_btn)

        # 提示文字
        self.hint_label = QLabel("")
        self.hint_label.setStyleSheet("font-size: 11px; color: #8e8e93;")
        self.hint_label.setWordWrap(True)
        mysql_layout.addWidget(self.hint_label)

        layout.addWidget(self.mysql_config)

        # 根据 checkbox 显示/隐藏 MySQL 配置
        self.mysql_config.setVisible(self.settings.get("mysql_enabled", False))

        layout.addStretch()

        # 提示
        tip = QLabel("启用后将在后台自动同步数据到 MySQL")
        tip.setStyleSheet("font-size: 11px; color: #8e8e93; font-style: italic;")
        tip.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip)

        # 底部按钮
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(80, 34)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: rgba(142, 142, 147, 0.12);
                border: none;
                border-radius: 8px;
                font-size: 13px;
                color: #636366;
            }
            QPushButton:hover {
                background: rgba(142, 142, 147, 0.22);
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("保存")
        save_btn.setFixedSize(80, 34)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #007AFF;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                color: white;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #0056CC;
            }
        """)
        save_btn.clicked.connect(self._save)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        layout.addLayout(btn_row)

    def _style_input(self, input_widget):
        input_widget.setFixedHeight(32)
        input_widget.setStyleSheet("""
            QLineEdit {
                background: rgba(255, 255, 255, 0.6);
                border: 1px solid rgba(0, 0, 0, 0.08);
                border-radius: 6px;
                padding: 0 10px;
                font-size: 12px;
                color: #1d1d1f;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 122, 255, 0.4);
                background: white;
            }
        """)
        # 中文右键菜单
        input_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        input_widget.customContextMenuRequested.connect(lambda pos, w=input_widget: self._show_context_menu(pos, w))
        # 阴影效果
        TaskApp.apply_input_shadow(input_widget)

    def _show_context_menu(self, pos, line_edit):
        """中文右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(TaskApp.get_context_menu_style())

        has_selection = line_edit.hasSelectedText()
        has_text = len(line_edit.text()) > 0
        has_clipboard = QApplication.clipboard().text() != ""

        undo_action = QAction("撤销", self)
        undo_action.setEnabled(line_edit.isUndoAvailable())
        undo_action.triggered.connect(line_edit.undo)
        menu.addAction(undo_action)

        redo_action = QAction("重做", self)
        redo_action.setEnabled(line_edit.isRedoAvailable())
        redo_action.triggered.connect(line_edit.redo)
        menu.addAction(redo_action)

        menu.addSeparator()

        cut_action = QAction("剪切", self)
        cut_action.setEnabled(has_selection)
        cut_action.triggered.connect(line_edit.cut)
        menu.addAction(cut_action)

        copy_action = QAction("复制", self)
        copy_action.setEnabled(has_selection)
        copy_action.triggered.connect(line_edit.copy)
        menu.addAction(copy_action)

        paste_action = QAction("粘贴", self)
        paste_action.setEnabled(has_clipboard)
        paste_action.triggered.connect(line_edit.paste)
        menu.addAction(paste_action)

        delete_action = QAction("删除", self)
        delete_action.setEnabled(has_selection)
        delete_action.triggered.connect(line_edit.del_)
        menu.addAction(delete_action)

        menu.addSeparator()

        select_all_action = QAction("全选", self)
        select_all_action.setEnabled(has_text)
        select_all_action.triggered.connect(line_edit.selectAll)
        menu.addAction(select_all_action)

        menu.exec(line_edit.mapToGlobal(pos))

    def _on_mysql_toggled(self, state):
        """切换 MySQL 启用状态"""
        if state != Qt.Unchecked:
            self.mysql_config.show()
        else:
            self.mysql_config.hide()

    def _test_connection(self):
        """测试 MySQL 连接，自动创建数据库"""
        if not HAS_PYMYSQL:
            self.hint_label.setText("❌ 请先安装 pymysql: pip install pymysql")
            self.hint_label.setStyleSheet("font-size: 11px; color: #FF3B30;")
            return

        host = self.host_input.text().strip()
        port = int(self.port_input.text().strip() or 3306)
        user = self.user_input.text().strip()
        password = self.pwd_input.text()
        database = self.db_input.text().strip() or "dailyinfo"

        try:
            # 先不指定数据库，测试能否连上服务器
            conn = pymysql.connect(
                host=host, port=port, user=user, password=password,
                charset="utf8mb4", connect_timeout=5
            )
            with conn.cursor() as cursor:
                # 自动创建数据库（如果不存在）
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}` DEFAULT CHARACTER SET utf8mb4")
            conn.close()

            # 再连接到目标数据库验证
            conn = pymysql.connect(
                host=host, port=port, user=user, password=password,
                database=database, charset="utf8mb4", connect_timeout=5
            )
            conn.close()
            self.hint_label.setText(f"✅ 连接成功，数据库 `{database}` 已就绪")
            self.hint_label.setStyleSheet("font-size: 11px; color: #34C759;")
        except Exception as e:
            self.hint_label.setText(f"❌ 连接失败: {e}")
            self.hint_label.setStyleSheet("font-size: 11px; color: #FF3B30;")

    def _save(self):
        """保存配置"""
        self.settings["mysql_enabled"] = self.mysql_enabled_cb.isChecked()
        self.settings["mysql"] = {
            "host": self.host_input.text().strip(),
            "port": int(self.port_input.text().strip() or 3306),
            "user": self.user_input.text().strip(),
            "password": self.pwd_input.text(),
            "database": self.db_input.text().strip() or "dailyinfo"
        }
        save_settings(self.settings)
        self.result_saved = True
        self.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None


# ========== 主应用 ==========
class WindowControlButton(QPushButton):
    """绘制型窗口控制按钮，避免字符图标的基线偏移"""

    def __init__(self, icon_type, parent=None):
        super().__init__(parent)
        clean_button_focus(self)
        self.icon_type = icon_type
        self.setFixedSize(28, 28)
        self.setCursor(Qt.PointingHandCursor)

    def set_icon_type(self, icon_type):
        self.icon_type = icon_type
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor("white") if self.objectName() == "closeBtn" and self.underMouse() else QColor("#6e6e73")
        pen = QPen(color, 1.5)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)

        center_x = self.width() // 2
        center_y = self.height() // 2

        if self.icon_type == "minimize":
            painter.drawLine(center_x - 5, center_y + 1, center_x + 5, center_y + 1)
        elif self.icon_type == "maximize":
            painter.drawRect(center_x - 4, center_y - 3, 8, 8)
        elif self.icon_type == "restore":
            painter.drawRect(center_x - 2, center_y - 3, 7, 7)
            painter.drawLine(center_x - 5, center_y, center_x - 5, center_y + 6)
            painter.drawLine(center_x - 5, center_y + 6, center_x + 1, center_y + 6)
            painter.drawLine(center_x - 5, center_y, center_x - 2, center_y)
        elif self.icon_type == "close":
            painter.drawLine(center_x - 5, center_y - 5, center_x + 5, center_y + 5)
            painter.drawLine(center_x + 5, center_y - 5, center_x - 5, center_y + 5)


class EyeToggleButton(QPushButton):
    """表头小眼睛按钮，避免依赖 QHeaderView section 自绘。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        clean_button_focus(self)
        self.show_all_plan_tasks = False
        self.setFixedSize(26, 26)
        self.setCursor(Qt.PointingHandCursor)

    def set_show_all_plan_tasks(self, show_all):
        self.show_all_plan_tasks = show_all
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        border_color = QColor(0, 122, 255, 95) if self.show_all_plan_tasks else QColor("#c7c7cc")
        bg_color = QColor(0, 122, 255, 28) if self.show_all_plan_tasks else QColor(255, 255, 255, 150)
        icon_color = QColor("#007AFF") if self.show_all_plan_tasks else QColor("#8e8e93")
        if self.underMouse():
            border_color = QColor(0, 122, 255, 110)
            bg_color = QColor(0, 122, 255, 36)
            icon_color = QColor("#007AFF")
        if self.isDown():
            border_color = QColor(0, 122, 255, 135)
            bg_color = QColor(0, 122, 255, 55)

        button_rect = self.rect().adjusted(1, 1, -1, -1)
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(bg_color)
        painter.drawRoundedRect(button_rect, 5, 5)

        center_x = self.rect().center().x() + 1
        center_y = self.rect().center().y() + 1
        eye_rect = QRect(center_x - 8, center_y - 5, 16, 10)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(icon_color, 1.5))
        painter.drawEllipse(eye_rect)
        painter.setBrush(icon_color)
        painter.drawEllipse(QRect(center_x - 2, center_y - 2, 4, 4))

        if not self.show_all_plan_tasks:
            slash_pen = QPen(icon_color, 1.7)
            slash_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(slash_pen)
            painter.drawLine(center_x - 8, center_y + 7, center_x + 8, center_y - 7)


class TaskHeaderView(QHeaderView):
    """任务列表表头，负责绘制和切换6天外计划任务的小眼睛。"""

    toggleVisibilityClicked = Signal()

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.toggle_visible = False
        self.show_all_plan_tasks = False
        self.toggle_pressed = False
        self.toggle_hovered = False
        self.toggle_button = EyeToggleButton(self.viewport())
        self.toggle_button.hide()
        self.toggle_button.clicked.connect(self.toggleVisibilityClicked)
        self.setSectionsClickable(True)
        self.setMouseTracking(True)
        self.sectionResized.connect(lambda *_: self.update_toggle_button_geometry())
        self.sectionMoved.connect(lambda *_: self.update_toggle_button_geometry())

    def set_toggle_visible(self, visible):
        self.toggle_visible = visible
        if not visible:
            self.toggle_pressed = False
            self.toggle_hovered = False
            self.unsetCursor()
        self.toggle_button.setVisible(visible)
        self.update_toggle_button_geometry()
        self.viewport().update()

    def set_show_all_plan_tasks(self, show_all):
        self.show_all_plan_tasks = show_all
        self.toggle_button.set_show_all_plan_tasks(show_all)
        self.setToolTip("显示全部计划任务" if show_all else "隐藏6天外计划任务")
        self.viewport().update()

    def _toggle_rect(self, section_rect):
        width = 26
        height = 26
        x = section_rect.x() + (section_rect.width() - width) // 2 + 1
        y = section_rect.y() + (section_rect.height() - height) // 2
        return QRect(x, y, width, height)

    def update_toggle_button_geometry(self):
        if not self.toggle_visible:
            return
        section_rect = QRect(
            self.sectionViewportPosition(0),
            0,
            self.sectionSize(0),
            self.height()
        )
        self.toggle_button.setGeometry(self._toggle_rect(section_rect))
        self.toggle_button.raise_()

    def _is_toggle_point(self, point):
        if not self.toggle_visible or self.logicalIndexAt(point) != 0:
            return False
        section_rect = QRect(
            self.sectionViewportPosition(0),
            0,
            self.sectionSize(0),
            self.height()
        )
        return self._toggle_rect(section_rect).contains(point)

    def _is_toggle_event(self, event):
        return self._is_toggle_point(event.position().toPoint())

    def paintSection(self, painter, rect, logicalIndex):
        super().paintSection(painter, rect, logicalIndex)
        if logicalIndex != 0 or not self.toggle_visible:
            return
        self.update_toggle_button_geometry()

    def mouseMoveEvent(self, event):
        is_hovered = self._is_toggle_event(event)
        if self.toggle_hovered != is_hovered:
            self.toggle_hovered = is_hovered
            self.setCursor(Qt.PointingHandCursor if is_hovered else Qt.ArrowCursor)
            self.viewport().update()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        if self.toggle_hovered or self.toggle_pressed:
            self.toggle_hovered = False
            self.toggle_pressed = False
            self.unsetCursor()
            self.viewport().update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if self._is_toggle_event(event):
            self.toggle_pressed = True
            self.viewport().update()
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.toggle_pressed:
            self.toggle_pressed = False
            if self._is_toggle_event(event):
                self.toggleVisibilityClicked.emit()
            self.viewport().update()
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self._is_toggle_event(event):
            self.toggle_pressed = False
            self.toggleVisibilityClicked.emit()
            self.viewport().update()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


class TaskApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.manager = TaskManager()
        self.searching = False
        self.showing_history = False
        self.show_far_future_tasks = False
        self.task_refresh_timer = QTimer(self)
        self.task_refresh_timer.setSingleShot(True)
        self.task_refresh_timer.timeout.connect(self.refresh_task_list_after_toggle)

        # JSON 防抖写入定时器
        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.timeout.connect(self.manager._do_save)
        self.manager._save_timer = self._save_timer

        # MySQL 同步防抖定时器
        self._mysql_sync_timer = QTimer(self)
        self._mysql_sync_timer.setSingleShot(True)
        self._mysql_sync_timer.timeout.connect(self.manager._do_mysql_sync)
        self.manager._mysql_sync_timer = self._mysql_sync_timer

        # 异步初始化 MySQL（不阻塞 UI 显示）
        self.manager.mysql_ready.connect(self._on_mysql_ready)
        self.manager.mysql_failed.connect(self._on_mysql_failed)
        QTimer.singleShot(100, self.manager.init_mysql_async)

        self.setWindowTitle("Dailyinfo")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setFocusPolicy(Qt.StrongFocus)

        # 设置任务栏图标
        icon_path = os.path.join(ICO_DIR, "岚兮儿天下无敌好看.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.setup_ui()
        # JSON 始终为主存储，直接刷新列表
        self.refresh_task_list()
        QTimer.singleShot(100, self.enable_blur)

    def enable_blur(self):
        hwnd = int(self.winId())
        enable_blur_behind(hwnd)

    def closeEvent(self, event):
        """关闭窗口时确保数据写入磁盘"""
        # 停止所有定时器
        self._save_timer.stop()
        self._mysql_sync_timer.stop()
        # 确保 JSON 已写入（本地数据不丢）
        self.manager._save_to_json()
        # MySQL 同步不阻塞关闭，后台线程自行完成
        # 下次启动时会自动合并，所以关闭时不同步也不丢数据
        event.accept()

    def setup_ui(self):
        self.central = QWidget()
        self.central.setMouseTracking(True)
        self.central.installEventFilter(self)
        self.setMouseTracking(True)
        self.setCentralWidget(self.central)
        self.outer_layout = QVBoxLayout(self.central)
        self.outer_layout.setContentsMargins(12, 12, 12, 12)

        self.glass = QFrame()
        self.glass.setObjectName("glassContainer")
        self.glass.setMouseTracking(True)
        self.glass.installEventFilter(self)
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(30)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.shadow.setOffset(0, 4)
        self.glass.setGraphicsEffect(self.shadow)

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

        daily_label = QLabel('<span style="font-size:16px;font-weight:600;color:#4e4e53;">Dailyinfo</span><span style="font-size:14px;font-weight:500;color:#4e4e53;vertical-align:sub;margin-left:4px;"> Trying to do better`</span>')
        win_row.addWidget(daily_label)

        win_row.addStretch()

        # 窗口按钮容器
        win_btn_container = QWidget()
        win_btn_container.setObjectName("winBtnContainer")
        win_btn_container.setFixedWidth(125)
        win_btn_layout = QHBoxLayout(win_btn_container)
        win_btn_layout.setContentsMargins(6, 4, 6, 4)
        win_btn_layout.setSpacing(0)

        min_btn = WindowControlButton("minimize")
        min_btn.setObjectName("windowBtn")
        min_btn.clicked.connect(self.showMinimized)
        win_btn_layout.addWidget(min_btn)

        win_btn_layout.addStretch()

        self.max_btn = WindowControlButton("maximize")
        self.max_btn.setObjectName("windowBtn")
        self.max_btn.clicked.connect(self.toggle_maximize)
        win_btn_layout.addWidget(self.max_btn)

        win_btn_layout.addStretch()

        close_btn = WindowControlButton("close")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(self.close)
        win_btn_layout.addWidget(close_btn)

        win_row.addWidget(win_btn_container)

        header_layout.addLayout(win_row)

        # 第二行：每日任务（左） + 日期 星期 历史（右）
        info_row = QHBoxLayout()
        info_row.setContentsMargins(0, 4, 0, 0)
        info_row.setSpacing(12)

        # 标题区域（包含图标和文本）
        self.app_container = QWidget()
        app_layout = QHBoxLayout(self.app_container)
        app_layout.setContentsMargins(8, 0, 0, 0)
        app_layout.setSpacing(6)

        # 绿色对钩图标（历史页面显示）
        self.check_icon = QLabel("✓")
        self.check_icon.setFixedSize(26, 26)
        self.check_icon.setAlignment(Qt.AlignCenter)
        self.check_icon.setStyleSheet("""
            QLabel {
                background: #34C759;
                border: 2px solid #2DA44E;
                border-radius: 5px;
                color: white;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.check_icon.setVisible(False)
        app_layout.addWidget(self.check_icon)

        # 文本标签
        self.app_label = QLabel("📋 待办任务")
        self.app_label.setStyleSheet("font-size: 18px; font-weight: 600; color: #1d1d1f;")
        app_layout.addWidget(self.app_label)

        info_row.addWidget(self.app_container)

        info_row.addStretch()

        now = datetime.now()
        date_label = QLabel(now.strftime("%Y/%m/%d"))
        date_label.setObjectName("timeLabel")
        info_row.addWidget(date_label)

        weekday_btn = QPushButton(WEEKDAYS[now.weekday()][:3])
        clean_button_focus(weekday_btn)
        weekday_btn.setObjectName("weekdayLabel")
        weekday_btn.setCursor(Qt.PointingHandCursor)
        weekday_btn.setFixedHeight(34)
        weekday_btn.setMinimumWidth(56)
        weekday_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                color: #007AFF;
                font-size: 13px;
                font-weight: 500;
                padding: 6px 14px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: rgba(0, 122, 255, 0.08);
            }
        """)
        weekday_btn.clicked.connect(self.show_calendar)
        info_row.addWidget(weekday_btn)

        self.history_btn = QPushButton("历史")
        clean_button_focus(self.history_btn)
        self.history_btn.setObjectName("headerBtn")
        self.history_btn.setCursor(Qt.PointingHandCursor)
        self.history_btn.clicked.connect(self.show_history)
        info_row.addWidget(self.history_btn)

        header_layout.addLayout(info_row)

        main_layout.addWidget(header)

        # ====== 工具栏 ======
        self.toolbar = QFrame()
        self.toolbar.setObjectName("toolBar")
        self.toolbar.setStyleSheet("""
            #toolBar {
                background: rgba(255, 255, 255, 0.6);
                border-radius: 10px;
                border: 1px solid rgba(0, 0, 0, 0.08);
            }
        """)
        toolbar_layout = QHBoxLayout(self.toolbar)
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
                placeholder-text-color: #9a9aa0;
            }
            QLineEdit:focus {
                border: 1px solid rgba(0, 0, 0, 0.10);
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(225, 225, 230, 0.75),
                    stop: 0.18 rgba(255, 255, 255, 0.78),
                    stop: 0.82 rgba(255, 255, 255, 0.78),
                    stop: 1 rgba(232, 232, 236, 0.55)
                );
                placeholder-text-color: #6e6e73;
            }
        """)
        self.task_input.returnPressed.connect(self.add_task)
        self.task_input.textChanged.connect(self.on_input_changed)
        # 中文右键菜单
        self.task_input.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_input.customContextMenuRequested.connect(self._show_input_context_menu)
        # 阴影效果
        TaskApp.apply_input_shadow(self.task_input)
        toolbar_layout.addWidget(self.task_input, 1)

        # 搜索按钮
        self.search_btn = QPushButton("搜索")
        clean_button_focus(self.search_btn)
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
            clean_button_focus(btn)
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
        clean_button_focus(add_btn)
        add_btn.setObjectName("addBtn")
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setFixedHeight(42)
        add_btn.setMinimumWidth(56)
        add_btn.clicked.connect(self.add_task)
        toolbar_layout.addWidget(add_btn)

        toolbar_wrap = QWidget()
        toolbar_wrap_layout = QHBoxLayout(toolbar_wrap)
        toolbar_wrap_layout.setContentsMargins(18, 0, 18, 0)
        toolbar_wrap_layout.setSpacing(0)
        toolbar_wrap_layout.addWidget(self.toolbar)
        main_layout.addWidget(toolbar_wrap)

        # ====== 任务列表 ======
        list_card = QFrame()
        list_card.setObjectName("card")
        list_layout = QVBoxLayout(list_card)
        list_layout.setContentsMargins(6, 6, 6, 6)
        list_layout.setSpacing(0)

        self.task_list = QTreeWidget()
        self.task_header = TaskHeaderView(Qt.Horizontal, self.task_list)
        self.task_header.toggleVisibilityClicked.connect(self.toggle_far_future_tasks)
        self.task_list.setHeader(self.task_header)
        self.task_list.setHeaderLabels(["", "        任务内容                                                                                                                                                                  计划截止日期", "创建时间"])
        self.task_list.setRootIsDecorated(False)
        self.task_list.header().setDefaultAlignment(Qt.AlignLeft)
        self.task_list.setColumnWidth(0, 64)
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

        # 设置按钮
        self.settings_btn = QPushButton("⚙")
        self.settings_btn.setFixedSize(28, 28)
        self.settings_btn.setCursor(Qt.PointingHandCursor)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                color: #8e8e93;
            }
            QPushButton:hover {
                background: rgba(142, 142, 147, 0.12);
                color: #636366;
            }
        """)
        self.settings_btn.clicked.connect(self.show_settings)
        footer_layout.addWidget(self.settings_btn)

        main_layout.addWidget(footer)

        self.outer_layout.addWidget(self.glass)

        # 拖拽
        self._drag_pos = None
        self._resize_edges = set()
        self._resize_start_pos = None
        self._resize_start_geometry = None
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
        else:
            self.showMaximized()

    def update_window_button_state(self):
        """更新最大化按钮图标状态"""
        self.max_btn.set_icon_type("restore" if self.isMaximized() else "maximize")

    def update_layout_for_maximized(self):
        """最大化时调整外边距和阴影"""
        if self.isMaximized():
            self.outer_layout.setContentsMargins(0, 0, 0, 0)
            self.shadow.setEnabled(False)
        else:
            self.outer_layout.setContentsMargins(12, 12, 12, 12)
            QTimer.singleShot(80, self.enable_window_shadow)

    def enable_window_shadow(self):
        """还原窗口后延迟启用阴影，减少状态切换时的重绘卡顿"""
        if not self.isMaximized():
            self.shadow.setEnabled(True)

    def changeEvent(self, event):
        """处理系统快捷键最大化/还原"""
        if event.type() == event.Type.WindowStateChange:
            self.update_window_button_state()
            self.update_layout_for_maximized()
        super().changeEvent(event)

    def nativeEvent(self, event_type, message):
        """无边框窗口边缘缩放命中测试"""
        if event_type == "windows_generic_MSG":
            msg = MSG.from_address(int(message))
            if msg.message == WM_NCHITTEST and not self.isMaximized():
                x = c_short(msg.lParam & 0xFFFF).value
                y = c_short((msg.lParam >> 16) & 0xFFFF).value
                rect = self.frameGeometry()
                border = 8

                on_left = rect.left() <= x < rect.left() + border
                on_right = rect.right() - border < x <= rect.right()
                on_top = rect.top() <= y < rect.top() + border
                on_bottom = rect.bottom() - border < y <= rect.bottom()

                if on_top and on_left:
                    return True, HTTOPLEFT
                if on_top and on_right:
                    return True, HTTOPRIGHT
                if on_bottom and on_left:
                    return True, HTBOTTOMLEFT
                if on_bottom and on_right:
                    return True, HTBOTTOMRIGHT
                if on_left:
                    return True, HTLEFT
                if on_right:
                    return True, HTRIGHT
                if on_top:
                    return True, HTTOP
                if on_bottom:
                    return True, HTBOTTOM
        return super().nativeEvent(event_type, message)

    def eventFilter(self, obj, event):
        """处理无边框窗口边缘的手动缩放"""
        if obj in (getattr(self, "central", None), getattr(self, "glass", None)):
            if event.type() == QEvent.MouseButtonPress:
                if self._start_resize(event):
                    return True
            elif event.type() == QEvent.MouseMove:
                if self._resize_edges:
                    self._perform_resize(event.globalPosition().toPoint())
                    return True
                self._update_resize_cursor(event.globalPosition().toPoint())
            elif event.type() == QEvent.MouseButtonRelease:
                if self._resize_edges:
                    self._finish_resize()
                    return True
            elif event.type() == QEvent.Leave and not self._resize_edges:
                self.unsetCursor()
        return super().eventFilter(obj, event)

    def _resize_edges_at(self, global_pos):
        """获取鼠标所在的窗口缩放边缘"""
        if self.isMaximized():
            return set()

        rect = self.frameGeometry()
        border = 14
        edges = set()

        if rect.left() <= global_pos.x() <= rect.left() + border:
            edges.add("left")
        elif rect.right() - border <= global_pos.x() <= rect.right():
            edges.add("right")

        if rect.top() <= global_pos.y() <= rect.top() + border:
            edges.add("top")
        elif rect.bottom() - border <= global_pos.y() <= rect.bottom():
            edges.add("bottom")

        return edges

    def _update_resize_cursor(self, global_pos):
        """根据边缘位置切换缩放光标"""
        edges = self._resize_edges_at(global_pos)
        if {"top", "left"} <= edges or {"bottom", "right"} <= edges:
            self.setCursor(Qt.SizeFDiagCursor)
        elif {"top", "right"} <= edges or {"bottom", "left"} <= edges:
            self.setCursor(Qt.SizeBDiagCursor)
        elif "left" in edges or "right" in edges:
            self.setCursor(Qt.SizeHorCursor)
        elif "top" in edges or "bottom" in edges:
            self.setCursor(Qt.SizeVerCursor)
        else:
            self.unsetCursor()

    def _start_resize(self, event):
        """开始边缘缩放"""
        if event.button() != Qt.LeftButton:
            return False

        edges = self._resize_edges_at(event.globalPosition().toPoint())
        if not edges:
            return False

        self._resize_edges = edges
        self._resize_start_pos = event.globalPosition().toPoint()
        self._resize_start_geometry = QRect(self.geometry())
        return True

    def _perform_resize(self, global_pos):
        """执行边缘缩放"""
        if not self._resize_edges or self._resize_start_pos is None:
            return

        delta = global_pos - self._resize_start_pos
        geometry = QRect(self._resize_start_geometry)
        min_width = self.minimumWidth()
        min_height = self.minimumHeight()

        if "left" in self._resize_edges:
            geometry.setLeft(min(geometry.left() + delta.x(), geometry.right() - min_width))
        if "right" in self._resize_edges:
            geometry.setRight(max(geometry.right() + delta.x(), geometry.left() + min_width))
        if "top" in self._resize_edges:
            geometry.setTop(min(geometry.top() + delta.y(), geometry.bottom() - min_height))
        if "bottom" in self._resize_edges:
            geometry.setBottom(max(geometry.bottom() + delta.y(), geometry.top() + min_height))

        self.setGeometry(geometry)

    def _finish_resize(self):
        """结束边缘缩放"""
        self._resize_edges = set()
        self._resize_start_pos = None
        self._resize_start_geometry = None

    def show_calendar(self):
        """显示日历弹窗"""
        dlg = QDialog(self)
        dlg.setWindowTitle("日历")
        dlg.setFixedSize(456, 486)
        dlg.setAttribute(Qt.WA_TranslucentBackground)
        dlg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dlg.setStyleSheet("""
            QDialog {
                background: transparent;
            }
        """)

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(0)

        container = QFrame()
        container.setObjectName("calendarDialogContainer")
        container.setStyleSheet("""
            #calendarDialogContainer {
                background: #ffffff;
                border-radius: 10px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title_row = QWidget()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(8)

        title = QLabel("📅 日历")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #1d1d1f;")
        title_row_layout.addWidget(title)
        title_row_layout.addStretch()

        close_btn = WindowControlButton("close")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(dlg.accept)
        title_row_layout.addWidget(close_btn)
        layout.addWidget(title_row)

        drag_pos = {"value": None}

        def calendar_mouse_press(event):
            if event.button() == Qt.LeftButton:
                drag_pos["value"] = event.globalPosition().toPoint() - dlg.pos()

        def calendar_mouse_move(event):
            if drag_pos["value"] and event.buttons() & Qt.LeftButton:
                dlg.move(event.globalPosition().toPoint() - drag_pos["value"])

        def calendar_mouse_release(event):
            drag_pos["value"] = None

        title_row.mousePressEvent = calendar_mouse_press
        title_row.mouseMoveEvent = calendar_mouse_move
        title_row.mouseReleaseEvent = calendar_mouse_release
        title.mousePressEvent = calendar_mouse_press
        title.mouseMoveEvent = calendar_mouse_move
        title.mouseReleaseEvent = calendar_mouse_release

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
                selection-background-color: rgba(180, 180, 180, 0.6);
                selection-color: #1d1d1f;
                font-size: 14px;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: transparent;
            }
        """)
        layout.addWidget(calendar)

        # 节假日信息显示
        today = QDate.currentDate()
        info_text, label_kinds = format_calendar_info(today)
        holiday_info = QLabel(info_text)
        holiday_info.setStyleSheet(calendar_info_style(label_kinds))
        holiday_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(holiday_info)

        def on_date_selected(qdate):
            info_text, label_kinds = format_calendar_info(qdate)
            holiday_info.setText(info_text)
            holiday_info.setStyleSheet(calendar_info_style(label_kinds))

        calendar.clicked.connect(on_date_selected)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        # 回到今天按钮
        back_today_btn = QPushButton("📅 回到今天")
        clean_button_focus(back_today_btn)
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

        layout.addLayout(btn_layout)
        outer.addWidget(container)

        dlg.exec()

    def show_settings(self):
        """打开设置弹窗"""
        dlg = SettingsDialog(self)
        dlg.exec()
        if dlg.result_saved:
            # 热更新 manager 的 MySQL 配置
            self.manager.settings = load_settings()
            new_enabled = self.manager.settings.get("mysql_enabled", False)

            if new_enabled and not self.manager._mysql_enabled:
                # 用户新启用了 MySQL
                self.manager._mysql_enabled = True
                QTimer.singleShot(100, self.manager.init_mysql_async)
            elif not new_enabled and self.manager._mysql_enabled:
                # 用户关闭了 MySQL
                self.manager._mysql_enabled = False
                self.manager._mysql_initialized = False
                if self.manager.db:
                    try:
                        self.manager.db.close()
                    except:
                        pass
                    self.manager.db = None

            QMessageBox.information(self, "提示", "配置已保存。")

    def show_history(self):
        """显示历史页面"""
        if self.showing_history:
            self.go_to_main()
        else:
            # 显示历史
            self.showing_history = True
            self.searching = False
            self.check_icon.setVisible(True)
            self.app_label.setText("已完成任务")
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
            self.history_btn.setText("返回")
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

    def go_to_main(self):
        """回到主页面"""
        self.showing_history = False
        self.searching = False
        self.check_icon.setVisible(False)
        self.app_label.setText("📋 待办任务")
        self.history_btn.setText("历史")
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
        self.refresh_task_list()

    def toggle_far_future_tasks(self):
        """切换主页面是否显示6天外计划任务。"""
        self.show_far_future_tasks = not self.show_far_future_tasks
        self.task_header.set_show_all_plan_tasks(self.show_far_future_tasks)
        self.task_header.viewport().repaint()
        QApplication.processEvents()
        self.task_refresh_timer.start(60)

    def refresh_task_list_after_toggle(self):
        """小眼睛切换后的延迟刷新，只作用于主页面。"""
        if not self.searching and not self.showing_history:
            self.refresh_task_list()

    def clear_task_input_caret(self):
        """清理输入框焦点光标，避免打开详情页后留下蓝色残影。"""
        self.task_input.deselect()
        self.task_input.setCursorPosition(0)
        self.task_input.clearFocus()
        self.setFocus(Qt.OtherFocusReason)
        self.task_input.setEnabled(False)
        self.task_input.update()
        self.task_input.repaint()
        self.toolbar.update()
        self.toolbar.repaint()
        QApplication.processEvents()
        self.task_input.setEnabled(True)
        self.task_input.clearFocus()

    def _show_input_context_menu(self, pos):
        """输入框中文右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(TaskApp.get_context_menu_style())

        line_edit = self.task_input
        has_selection = line_edit.hasSelectedText()
        has_text = len(line_edit.text()) > 0
        has_clipboard = QApplication.clipboard().text() != ""

        # 撤销
        undo_action = QAction("撤销", self)
        undo_action.setEnabled(line_edit.isUndoAvailable())
        undo_action.triggered.connect(line_edit.undo)
        menu.addAction(undo_action)

        # 重做
        redo_action = QAction("重做", self)
        redo_action.setEnabled(line_edit.isRedoAvailable())
        redo_action.triggered.connect(line_edit.redo)
        menu.addAction(redo_action)

        menu.addSeparator()

        # 剪切
        cut_action = QAction("剪切", self)
        cut_action.setEnabled(has_selection)
        cut_action.triggered.connect(line_edit.cut)
        menu.addAction(cut_action)

        # 复制
        copy_action = QAction("复制", self)
        copy_action.setEnabled(has_selection)
        copy_action.triggered.connect(line_edit.copy)
        menu.addAction(copy_action)

        # 粘贴
        paste_action = QAction("粘贴", self)
        paste_action.setEnabled(has_clipboard)
        paste_action.triggered.connect(line_edit.paste)
        menu.addAction(paste_action)

        # 删除
        delete_action = QAction("删除", self)
        delete_action.setEnabled(has_selection)
        delete_action.triggered.connect(line_edit.del_)
        menu.addAction(delete_action)

        menu.addSeparator()

        # 全选
        select_all_action = QAction("全选", self)
        select_all_action.setEnabled(has_text)
        select_all_action.triggered.connect(line_edit.selectAll)
        menu.addAction(select_all_action)

        menu.exec(line_edit.mapToGlobal(pos))

    def _show_date_context_menu(self, pos, date_edit):
        """日期输入框中文右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet(TaskApp.get_context_menu_style())

        # QDateEdit 的右键菜单：复制当前日期文本
        copy_action = QAction("复制", self)
        copy_action.triggered.connect(lambda: QApplication.clipboard().setText(date_edit.date().toString("yyyy-MM-dd")))
        menu.addAction(copy_action)

        # 粘贴
        paste_action = QAction("粘贴", self)
        clipboard_text = QApplication.clipboard().text()
        paste_action.setEnabled(bool(clipboard_text))
        paste_action.triggered.connect(lambda: self._paste_to_date_edit(date_edit, clipboard_text))
        menu.addAction(paste_action)

        menu.addSeparator()

        # 全选（选中日期文本）
        select_all_action = QAction("全选", self)
        select_all_action.setEnabled(False)  # QDateEdit 不支持全选
        menu.addAction(select_all_action)

        menu.exec(date_edit.mapToGlobal(pos))

    def _paste_to_date_edit(self, date_edit, text):
        """将剪贴板文本粘贴到日期输入框"""
        try:
            from PySide6.QtCore import QDate
            date = QDate.fromString(text, "yyyy-MM-dd")
            if date.isValid():
                date_edit.setDate(date)
        except:
            pass

    def header_mouse_press(self, event):
        if event.button() == Qt.LeftButton and not self.isMaximized():
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
                self.go_to_main()

    def on_search_btn_click(self):
        """搜索按钮点击"""
        if self.searching:
            self.go_to_main()
        else:
            # 执行搜索
            keyword = self.task_input.text().strip()
            if keyword:
                self.searching = True
                self.showing_history = False
                self.check_icon.setVisible(False)
                self.app_label.setText("🔍 搜索结果")
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
                self.history_btn.setText("历史")
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
                self.task_input.setPlaceholderText("搜索中...")
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
            if not deadline:
                return  # 用户取消了选择，不创建任务

        self.manager.add_task(title, priority, task_type, deadline=deadline)
        self.task_input.clear()
        self.refresh_task_list()
        self.task_input.setFocus()

    def _pick_deadline(self):
        """弹出截止日期选择"""
        dlg = QDialog(self)
        dlg.setWindowTitle("选择截止日期")
        dlg.setFixedSize(316, 210)
        dlg.setAttribute(Qt.WA_TranslucentBackground)
        dlg.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dlg.setStyleSheet("""
            QDialog {
                background: transparent;
            }
        """)

        outer = QVBoxLayout(dlg)
        outer.setContentsMargins(18, 18, 18, 18)
        outer.setSpacing(0)

        container = QFrame()
        container.setObjectName("deadlineDialogContainer")
        container.setStyleSheet("""
            #deadlineDialogContainer {
                background: #ffffff;
                border-radius: 10px;
                border: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 8)
        container.setGraphicsEffect(shadow)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        title_row = QWidget()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(8)

        label = QLabel("📅 选择截止日期")
        label.setStyleSheet("font-size: 14px; font-weight: 600; color: #1d1d1f;")
        title_row_layout.addWidget(label)
        title_row_layout.addStretch()

        close_btn = WindowControlButton("close")
        close_btn.setObjectName("closeBtn")
        close_btn.clicked.connect(dlg.reject)
        title_row_layout.addWidget(close_btn)
        layout.addWidget(title_row)

        drag_pos = {"value": None}

        def deadline_mouse_press(event):
            if event.button() == Qt.LeftButton:
                drag_pos["value"] = event.globalPosition().toPoint() - dlg.pos()

        def deadline_mouse_move(event):
            if drag_pos["value"] and event.buttons() & Qt.LeftButton:
                dlg.move(event.globalPosition().toPoint() - drag_pos["value"])

        def deadline_mouse_release(event):
            drag_pos["value"] = None

        title_row.mousePressEvent = deadline_mouse_press
        title_row.mouseMoveEvent = deadline_mouse_move
        title_row.mouseReleaseEvent = deadline_mouse_release
        label.mousePressEvent = deadline_mouse_press
        label.mouseMoveEvent = deadline_mouse_move
        label.mouseReleaseEvent = deadline_mouse_release

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
        # 中文右键菜单
        date_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        date_edit.customContextMenuRequested.connect(lambda pos, w=date_edit: self._show_date_context_menu(pos, w))
        # 阴影效果
        TaskApp.apply_input_shadow(date_edit)
        layout.addWidget(date_edit)

        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("取消")
        clean_button_focus(cancel_btn)
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
        clean_button_focus(ok_btn)
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
        outer.addWidget(container)

        if dlg.exec() == QDialog.Accepted:
            return date_edit.date().toString("yyyy-MM-dd")
        return ""

    def on_task_click(self, item, column):
        """点击任务条打开详情"""
        self.clear_task_input_caret()

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
                            self.manager._sync_mysql(task_id)
                            self.manager._schedule_save()
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

        # 清除选中态，焦点回到主窗口，避免输入框突然亮起
        self.task_list.clearSelection()
        self.task_list.setCurrentItem(None)
        self.task_list.clearFocus()
        self.clear_task_input_caret()

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
        self.task_list.setHeaderLabels(["", "        任务内容                                                                                                                                                                  计划截止日期", "创建时间"])
        self.task_header.set_toggle_visible(True)
        self.task_header.set_show_all_plan_tasks(self.show_far_future_tasks)
        self.task_list.clear()

        today_date = date.today()
        today = today_date.strftime("%Y-%m-%d")
        hide_after_date = today_date + timedelta(days=5)
        all_pending = self.manager.tasks["pending"]
        priority_order = {"高": 0, "中": 1, "低": 2}

        def parse_deadline(task):
            deadline = task.get("deadline", "")
            if not deadline:
                return None
            try:
                return date.fromisoformat(deadline)
            except ValueError:
                return None

        def is_far_future_plan(task):
            if task.get("type") != "计划任务":
                return False
            deadline_date = parse_deadline(task)
            return deadline_date is not None and deadline_date > hide_after_date

        def parse_created_date(task):
            try:
                return date.fromisoformat(task.get("created_at", "")[:10])
            except ValueError:
                return today_date

        hidden_count = sum(1 for task in all_pending if is_far_future_plan(task))
        if self.show_far_future_tasks:
            source = list(all_pending)
        else:
            source = [task for task in all_pending if not is_far_future_plan(task)]

        def sort_key(task):
            # 关闭小眼睛：过期计划、过期普通、今天、未来5天；打开后6天外计划任务置顶。
            priority_rank = priority_order.get(task.get("priority"), 1)
            if task.get("type") == "计划任务":
                deadline_date = parse_deadline(task)
                if deadline_date:
                    if self.show_far_future_tasks and deadline_date > hide_after_date:
                        return (0, deadline_date.toordinal(), priority_rank)
                    if deadline_date < today_date:
                        return (1, deadline_date.toordinal(), priority_rank)
                    if deadline_date == today_date:
                        return (3, 0, priority_rank)
                    return (4, deadline_date.toordinal(), priority_rank)
                return (5, 0, priority_rank)
            else:
                created_date = parse_created_date(task)
                if created_date < today_date:
                    return (2, priority_rank, created_date.toordinal())
                return (3, priority_rank, created_date.toordinal())

        source = sorted(source, key=sort_key)

        if len(source) == 0 and hidden_count > 0 and not self.show_far_future_tasks:
            self.empty_label.setText("6天外计划任务已隐藏")
        else:
            self.empty_label.setText("✨ 暂无任务，添加一个吧~")
        self.empty_label.setVisible(len(source) == 0)
        # 不隐藏 task_list，保持表头可见

        for task in source:
            item = QTreeWidgetItem()
            item.setData(0, Qt.UserRole, task["id"])
            self.task_list.addTopLevelItem(item)

            priority = task["priority"]

            # 完成方块
            check_btn = QPushButton()
            clean_button_focus(check_btn)
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
            check_layout.setContentsMargins(2, 8, 0, 0)
            check_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            check_layout.addWidget(check_btn)
            self.task_list.setItemWidget(item, 0, check_container)

            # 任务内容
            content_widget = QWidget()
            content_layout = QHBoxLayout(content_widget)
            content_layout.setContentsMargins(4, 0, 8, 0)
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
                title = f"📝 {title}"
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
                expire_label.setStyleSheet("color: #FF3B30; font-size: 12px; font-weight: 600; background: transparent; border: none; padding-right: 12px;")
                expire_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                content_layout.addWidget(expire_label)
            elif deadline and not is_expired_plan:
                deadline_label = QLabel(deadline)
                deadline_label.setStyleSheet("color: #8e8e93; font-size: 12px; background: transparent; border: none; padding-right: 12px;")
                deadline_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                content_layout.addWidget(deadline_label)

            self.task_list.setItemWidget(item, 1, content_widget)

            # 时间
            if is_expired_normal:
                time_label = QLabel(task["created_at"])
                time_label.setStyleSheet("color: #FF3B30; font-size: 12px; font-weight: 600; background: transparent; border: none; padding-right: 12px;")
            else:
                time_label = QLabel(task["created_at"])
                time_label.setStyleSheet("color: #8e8e93; font-size: 12px; background: transparent; border: none; padding-right: 12px;")
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
        self.task_list.setHeaderLabels(["", "        任务内容                                                                                                                                                                  时间信息", "创建时间"])
        self.task_header.set_toggle_visible(False)
        self.task_list.clear()

        all_tasks = []
        for task_type, task in results:
            all_tasks.append((task_type, task))

        priority_order = {"计划": -1, "高": 0, "中": 1, "低": 2}
        all_tasks.sort(key=lambda x: priority_order.get(x[1]["priority"], 1))

        self.empty_label.setText("✨ 暂无任务，添加一个吧~")
        self.empty_label.setVisible(len(all_tasks) == 0)
        # 不隐藏 task_list，保持表头可见

        for task_type, task in all_tasks:
            item = QTreeWidgetItem()
            item.setData(0, Qt.UserRole, task["id"])
            self.task_list.addTopLevelItem(item)

            priority = task["priority"]
            hover_color = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["color"]
            hover_bg = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["bg"]

            if task_type == "pending":
                # 待办：空方框
                check_btn = QPushButton()
                clean_button_focus(check_btn)
                check_btn.setFixedSize(26, 26)
                check_btn.setCursor(Qt.PointingHandCursor)
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

                check_container = QWidget()
                check_layout = QHBoxLayout(check_container)
                check_layout.setContentsMargins(2, 8, 0, 0)
                check_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                check_layout.addWidget(check_btn)
                self.task_list.setItemWidget(item, 0, check_container)
            else:
                # 已完成：绿色对钩
                uncheck_btn = QPushButton("✓")
                clean_button_focus(uncheck_btn)
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

                btn_container = QWidget()
                btn_layout = QHBoxLayout(btn_container)
                btn_layout.setContentsMargins(2, 8, 0, 0)
                btn_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                btn_layout.addWidget(uncheck_btn)
                self.task_list.setItemWidget(item, 0, btn_container)

            # 任务内容
            content_widget = QWidget()
            content_layout = QHBoxLayout(content_widget)
            content_layout.setContentsMargins(4, 0, 8, 0)
            content_layout.setSpacing(10)

            dot_color = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["color"]
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {dot_color}; font-size: 16px; background: transparent; border: none;")
            dot.setFixedWidth(20)
            dot.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(dot)

            title = task["title"]
            if task["type"] == "计划任务":
                title = f"📅 {title}"
            else:
                title = f"📝 {title}"

            title_label = QLabel(title)
            title_label.setStyleSheet("color: #1d1d1f; font-size: 14px; background: transparent; border: none;")
            content_layout.addWidget(title_label, 1)

            # 右贴边时间信息
            today = date.today().strftime("%Y-%m-%d")
            if task_type == "pending":
                deadline = task.get("deadline", "")
                if deadline:
                    if deadline < today:
                        time_info = QLabel(f"⚠️ 已过期 {deadline}")
                        time_info.setStyleSheet("color: #FF3B30; font-size: 12px; font-weight: 600; background: transparent; border: none; padding-right: 12px;")
                    else:
                        time_info = QLabel(deadline)
                        time_info.setStyleSheet("color: #8e8e93; font-size: 12px; background: transparent; border: none; padding-right: 12px;")
                    time_info.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    content_layout.addWidget(time_info)
            else:
                completed_at = task.get("completed_at", "")
                if completed_at:
                    time_info = QLabel(f"✓ {completed_at}")
                    time_info.setStyleSheet("color: #34C759; font-size: 12px; font-weight: 600; background: transparent; border: none; padding-right: 12px;")
                    time_info.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    content_layout.addWidget(time_info)

            self.task_list.setItemWidget(item, 1, content_widget)

            # 创建时间
            time_label = QLabel(task["created_at"])
            time_label.setStyleSheet("color: #8e8e93; font-size: 12px; background: transparent; border: none; padding-right: 12px;")
            self.task_list.setItemWidget(item, 2, time_label)

            # 背景色
            if task_type == "pending":
                bg = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["bg"]
            else:
                bg = "rgba(52, 199, 89, 0.08)"
            for col in range(3):
                item.setBackground(col, QColor(bg))

        self.update_stats()

    def refresh_history_list(self):
        """刷新历史列表"""
        self.task_list.setHeaderLabels(["", "        任务内容                                                                                                                                                          完成时间", "创建时间"])
        self.task_header.set_toggle_visible(False)
        self.task_list.clear()

        # 启用右键菜单（先断开避免重复连接）
        try:
            self.task_list.customContextMenuRequested.disconnect(self.show_history_context_menu)
        except (TypeError, RuntimeError):
            pass
        self.task_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_list.customContextMenuRequested.connect(self.show_history_context_menu)

        source = self.manager.tasks["completed"]

        self.empty_label.setText("✨ 暂无任务，添加一个吧~")
        self.empty_label.setVisible(len(source) == 0)
        # 不隐藏 task_list，保持表头可见

        # 按置顶状态排序：pinned=True 的排在前面
        sorted_source = sorted(source, key=lambda t: not t.get("pinned", False))

        for task in sorted_source:
            item = QTreeWidgetItem()
            item.setData(0, Qt.UserRole, task["id"])
            self.task_list.addTopLevelItem(item)

            # 取消完成按钮（带对钩的方框）
            priority = task["priority"]
            hover_color = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["color"]
            hover_bg = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["bg"]

            uncheck_btn = QPushButton("✓")
            clean_button_focus(uncheck_btn)
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
            btn_layout.setContentsMargins(2, 8, 0, 0)
            btn_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            btn_layout.addWidget(uncheck_btn)
            self.task_list.setItemWidget(item, 0, btn_container)

            # 任务内容
            content_widget = QWidget()
            content_layout = QHBoxLayout(content_widget)
            content_layout.setContentsMargins(4, 0, 8, 0)
            content_layout.setSpacing(10)

            priority = task["priority"]
            dot_color = PRIORITY_CONFIG.get(priority, PRIORITY_CONFIG["中"])["color"]
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {dot_color}; font-size: 16px; background: transparent; border: none;")
            dot.setFixedWidth(20)
            dot.setAlignment(Qt.AlignCenter)
            content_layout.addWidget(dot)

            title = task["title"]
            if task.get("pinned", False):
                title = f"📌 {title}"
            elif task["type"] == "计划任务":
                title = f"📅 {title}"
            else:
                title = f"📝 {title}"

            title_label = QLabel(title)
            title_label.setStyleSheet("color: #1d1d1f; font-size: 14px; background: transparent; border: none;")
            content_layout.addWidget(title_label, 1)

            # 完成时间（右贴边）
            completed_at = task.get("completed_at", "")
            if completed_at:
                completed_label = QLabel(completed_at)
                completed_label.setStyleSheet("color: #8e8e93; font-size: 12px; background: transparent; border: none; padding-right: 14px;")
                completed_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                content_layout.addWidget(completed_label)

            self.task_list.setItemWidget(item, 1, content_widget)

            # 创建时间
            time_label = QLabel(task["created_at"])
            time_label.setStyleSheet("color: #8e8e93; font-size: 12px; background: transparent; border: none; padding-right: 12px;")
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

    def show_history_context_menu(self, pos):
        """历史页面右键菜单"""
        item = self.task_list.itemAt(pos)
        if not item:
            return
        task_id = item.data(0, Qt.UserRole)
        if not task_id:
            return
        # 查找任务
        task = None
        for t in self.manager.tasks["completed"]:
            if t["id"] == task_id:
                task = t
                break
        if not task:
            return

        is_pinned = task.get("pinned", False)
        self._show_history_pin_popup(pos, task_id, is_pinned)

    def _show_history_pin_popup(self, pos, task_id, is_pinned):
        """历史页面置顶弹出层，避开 QMenu 在 exe 中的原生黑边。"""
        popup = QDialog(self)
        popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint | Qt.NoDropShadowWindowHint)
        popup.setAttribute(Qt.WA_TranslucentBackground)
        popup.setFixedSize(108, 44)
        popup.setStyleSheet("""
            QDialog {
                background: transparent;
                border: none;
            }
        """)

        layout = QVBoxLayout(popup)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(0)

        container = QFrame()
        container.setObjectName("historyPinPopup")
        container.setStyleSheet("""
            #historyPinPopup {
                background: rgba(255, 255, 255, 0.92);
                border: 1px solid rgba(255, 255, 255, 0.78);
                border-radius: 8px;
            }
            QPushButton {
                background: transparent;
                color: #1d1d1f;
                border: none;
                border-radius: 7px;
                padding: 8px 18px;
                font-size: 13px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.06);
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 24))
        shadow.setOffset(0, 2)
        container.setGraphicsEffect(shadow)

        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(3, 3, 3, 3)
        container_layout.setSpacing(0)

        pin_btn = QPushButton("取消置顶" if is_pinned else "置顶")
        clean_button_focus(pin_btn)
        pin_btn.setCursor(Qt.PointingHandCursor)
        pin_btn.clicked.connect(lambda: (popup.accept(), self._toggle_pin(task_id)))
        container_layout.addWidget(pin_btn)
        layout.addWidget(container)

        popup.move(self.task_list.viewport().mapToGlobal(pos))
        popup.exec()

    def _toggle_pin(self, task_id):
        """切换置顶状态"""
        self.manager.toggle_pin_task(task_id)
        self.refresh_history_list()

    def _on_mysql_ready(self):
        """MySQL 异步初始化完成后刷新 UI"""
        # 根据当前页面状态刷新对应列表
        if self.showing_history:
            self.refresh_history_list()
        elif self.searching:
            keyword = self.task_input.text().strip()
            if keyword:
                results = self.manager.search_tasks(keyword)
                self.refresh_search_list(results)
        else:
            self.refresh_task_list()

    def _on_mysql_failed(self):
        """MySQL 连接失败，已回退到本地数据"""
        # 刷新当前页面显示本地数据
        if self.showing_history:
            self.refresh_history_list()
        elif self.searching:
            keyword = self.task_input.text().strip()
            if keyword:
                results = self.manager.search_tasks(keyword)
                self.refresh_search_list(results)
        else:
            self.refresh_task_list()

    def update_stats(self):
        stats = self.manager.get_stats()
        self.stats_label.setText(
            f"待办 {stats['total_pending']}  ·  今日完成 {stats['today_completed']}  ·  历史 {stats['total_completed']}"
        )

    @staticmethod
    def get_context_menu_style():
        """统一的右键菜单样式"""
        return """
            QMenu {
                background: white;
                border: 0px solid transparent;
                border-radius: 8px;
                padding: 4px 0;
                margin: 0px;
            }
            QMenu::item {
                padding: 8px 24px;
                font-size: 13px;
                border: 0px solid transparent;
                outline: none;
            }
            QMenu::item:selected {
                background: #f0f0f0;
                border-radius: 4px;
                border: 0px solid transparent;
                outline: none;
            }
            QMenu::item:disabled {
                color: #c0c0c0;
                border: 0px solid transparent;
                outline: none;
            }
        """

    @staticmethod
    def create_input_shadow():
        """创建统一的输入框阴影效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, 20))  # 浅色低透明度
        shadow.setOffset(0, 2)
        return shadow

    @staticmethod
    def apply_input_shadow(widget):
        """为输入控件应用统一的阴影效果"""
        shadow = TaskApp.create_input_shadow()
        widget.setGraphicsEffect(shadow)
        return shadow


STYLE = """
QMainWindow { background: transparent; }
QWidget { font-family: "SF Pro Display", "PingFang SC", "Microsoft YaHei", sans-serif; }

#glassContainer {
    background: rgba(255, 255, 255, 0.99999999);
    border-radius: 10px;
    border: 1px solid rgba(0, 0, 0, 0.12);
}

#header {
    background: rgba(255, 255, 255, 0.7);
    border-radius: 8px;
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

#winBtnContainer {
    background: rgba(255, 255, 255, 0.4);
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 10px;
}

#windowBtn {
    background: transparent;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    color: #6e6e73;
}
#windowBtn:hover {
    background: rgba(0, 0, 0, 0.08);
}

#closeBtn {
    background: transparent;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-family: "Segoe UI Variable", "Segoe UI", sans-serif;
    color: #6e6e73;
}
#closeBtn:hover {
    background: rgba(255, 59, 48, 0.8);
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
    border-radius: 8px;
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
    border-radius: 6px;
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
    font-size: 12px;
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
        windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except:
        pass

    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)

    icon_path = os.path.join(ICO_DIR, "岚兮儿天下无敌好看.ico")
    app_icon = QIcon(icon_path) if os.path.exists(icon_path) else None
    if app_icon:
        app.setWindowIcon(app_icon)

    window = TaskApp()
    window.show()

    # 窗口显示后再次设置图标
    if app_icon:
        window.setWindowIcon(app_icon)

    sys.exit(app.exec())
