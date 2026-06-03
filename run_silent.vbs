Set ws = CreateObject("Wscript.Shell")
ws.CurrentDirectory = "G:\Bells_info\每日任务"
ws.Run "E:\Anaconda3\Data\Data-App\envs\Dailyinfo\pythonw.exe Code\daily_tasks.py", 0
