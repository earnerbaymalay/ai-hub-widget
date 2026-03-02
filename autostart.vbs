' AI Hub v5 - Silent Auto-Start
' Place in: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
' Uses script location to resolve ai_hub.py dynamically.

Dim WShell, scriptDir, pyPath
Set WShell = CreateObject("WScript.Shell")

scriptDir = Left(WScript.ScriptFullName, InStrRev(WScript.ScriptFullName, "\"))
pyPath = scriptDir & "ai_hub.py"

WShell.Run "pythonw """ & pyPath & """", 0, False
Set WShell = Nothing
