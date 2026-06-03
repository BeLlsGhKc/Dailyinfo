Dim fso, ws, batPath, folder
Set fso = CreateObject("Scripting.FileSystemObject")
Set ws = CreateObject("Wscript.Shell")

folder = fso.GetParentFolderName(WScript.ScriptFullName)
batPath = folder & "\start.bat"
ws.Run """" & batPath & """", 0
