Unicode True
!include "MUI2.nsh"
!ifndef APP_DIR
!error "Pass APP_DIR: the assembled self-contained application folder"
!endif
!ifndef OUTPUT
!define OUTPUT "GradeA-PaintPlus-0.1.0-Windows-x64-Setup.exe"
!endif
Name "GradeA PaintPlus"
OutFile "${OUTPUT}"
InstallDir "$LOCALAPPDATA\Programs\GradeA PaintPlus"
InstallDirRegKey HKCU "Software\GradeA\PaintPlusInstall" "Path"
RequestExecutionLevel user
SetCompressor /SOLID lzma
!define MUI_ICON "app.ico"
!define MUI_UNICON "app.ico"
!define MUI_FINISHPAGE_RUN "$INSTDIR\runtime\pythonw.exe"
!define MUI_FINISHPAGE_RUN_PARAMETERS '$\"$INSTDIR\launch.py$\"'
!define MUI_FINISHPAGE_RUN_TEXT "Launch GradeA PaintPlus"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "English"
Section "PaintPlus"
  SetShellVarContext current
  SetOutPath "$INSTDIR"
  File /r "${APP_DIR}\*"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  CreateDirectory "$SMPROGRAMS\GradeA PaintPlus"
  CreateShortcut "$SMPROGRAMS\GradeA PaintPlus\GradeA PaintPlus.lnk" "$INSTDIR\runtime\pythonw.exe" '"$INSTDIR\launch.py"' "$INSTDIR\app.ico"
  CreateShortcut "$SMPROGRAMS\GradeA PaintPlus\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  CreateShortcut "$DESKTOP\GradeA PaintPlus.lnk" "$INSTDIR\runtime\pythonw.exe" '"$INSTDIR\launch.py"' "$INSTDIR\app.ico"
  WriteRegStr HKCU "Software\GradeA\PaintPlusInstall" "Path" "$INSTDIR"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GradeAPaintPlus" "DisplayName" "GradeA PaintPlus"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GradeAPaintPlus" "DisplayVersion" "0.1.0"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GradeAPaintPlus" "Publisher" "GradeA"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GradeAPaintPlus" "UninstallString" '$\"$INSTDIR\Uninstall.exe$\"'
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GradeAPaintPlus" "DisplayIcon" "$INSTDIR\app.ico"
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GradeAPaintPlus" "NoModify" 1
  WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GradeAPaintPlus" "NoRepair" 1
  WriteRegStr HKCU "Software\Classes\.paintplus\OpenWithProgids" "GradeAPaintPlus.Project" ""
  WriteRegStr HKCU "Software\Classes\GradeAPaintPlus.Project" "" "PaintPlus editable project"
  WriteRegStr HKCU "Software\Classes\GradeAPaintPlus.Project\DefaultIcon" "" "$INSTDIR\app.ico"
  WriteRegStr HKCU "Software\Classes\GradeAPaintPlus.Project\shell\open\command" "" '$\"$INSTDIR\runtime\pythonw.exe$\" $\"$INSTDIR\launch.py$\" $\"%1$\"'
SectionEnd
Section "Uninstall"
  SetShellVarContext current
  Delete "$DESKTOP\GradeA PaintPlus.lnk"
  RMDir /r "$SMPROGRAMS\GradeA PaintPlus"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\GradeAPaintPlus"
  DeleteRegKey HKCU "Software\GradeA\PaintPlusInstall"
  DeleteRegValue HKCU "Software\Classes\.paintplus\OpenWithProgids" "GradeAPaintPlus.Project"
  DeleteRegKey HKCU "Software\Classes\GradeAPaintPlus.Project"
  RMDir /r "$INSTDIR"
  ; Keep user preferences, referenced asset folders, exported images and projects.
SectionEnd
