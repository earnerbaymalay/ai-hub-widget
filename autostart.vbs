' AI Hub Widget v5 - Silent Auto-Start Script
' Place this in your Startup folder: %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

Dim WShell
Set WShell = CreateObject("WScript.Shell")

' Launch v5 widget silently (no console window)
WShell.Run "pythonw C:\Users\pat21\AI-Widget\ai_widget_v5.py", 0, False

Set WShell = Nothing
