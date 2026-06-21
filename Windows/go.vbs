Dim ws, pythonPath, scriptPath
Set ws = CreateObject("Wscript.Shell")

pythonPath = "E:\Anaconda3\Data\Data-App\envs\Dailyinfo\pythonw.exe"
scriptPath = "G:\Bells_info\Dailyinfo\Code\daily_tasks.py"

ws.Run """" & pythonPath & """ """ & scriptPath & """", 0
