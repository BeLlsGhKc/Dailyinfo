@echo off
chcp 65001 >nul
title 每日任务管理
cd /d "%~dp0"
call conda activate Dailyinfo
python Code\daily_tasks.py
pause
