' Portable launch: all dependencies are bundled; no system Python is required.
Set files = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")
root = files.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = root
shell.Run Chr(34) & root & "\runtime\pythonw.exe" & Chr(34) & " " & Chr(34) & root & "\launch.py" & Chr(34), 1, False
