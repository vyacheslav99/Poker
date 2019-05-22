; GENERAL ----------------------------------------------------------------------
!include MUI2.nsh
Name "Расписной покер"
OutFile ".\setup_poker.exe"
InstallDir "$PROGRAMFILES\Poker"
InstallDirRegKey HKLM "Software\Poker" "Install_Dir"
RequestExecutionLevel admin
XPStyle on
SetDatablockOptimize on
AutoCloseWindow false
ShowInstDetails show
ShowUninstDetails show
Caption "Установка игры Расписной покер"
  
VIAddVersionKey "ProductName" "Poker"
VIAddVersionKey "Comments" ""
VIAddVersionKey "CompanyName" 'ViSla'
VIAddVersionKey "LegalTrademarks" 'ViSla TM'
VIAddVersionKey "LegalCopyright" '© ViSla'
VIAddVersionKey "FileDescription" "Poker installer"
VIAddVersionKey "FileVersion" "1.0.0.0"
VIProductVersion "1.0.0.0"

Var StartMenuFolder

; DEFINES ----------------------------------------------------------------------
; подтверждение выхода
!define MUI_ABORTWARNING

; иконки
;!define MUI_ICON "ico\logo.ico"  
;!define MUI_UNICON "\uninst.ico"

; заголовок на странице приветствия в 3 строки
!define MUI_WELCOMEPAGE_TITLE_3LINES

; чекбокс принятия лицензии (если не объявлять, то вместо кнопки "далее" будет "принять")
;!define MUI_LICENSEPAGE_CHECKBOX
;!define MUI_LICENSEPAGE_CHECKBOX_TEXT "Я принимаю условия лицензионного соглашения"

; описание устанавливаемых компонентов расположить внизу, (по умолчанию сбоку)  
!define MUI_COMPONENTSPAGE_SMALLDESC

; запишем в реестр имя папки в пуске, введенное пользователем (для унинсталлера) 
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKLM" 
!define MUI_STARTMENUPAGE_REGISTRY_KEY "SOFTWARE\Poker" 
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "StartMenuFolder"

; запутить после установки
;!define MUI_FINISHPAGE_SHOWREADME "readme.txt"
;!define MUI_FINISHPAGE_SHOWREADME_TEXT "Посмотреть описание"
;!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED

; не закрывать сразу страничку прогресса установки, чтоб можно было посмотреть лог
!define MUI_FINISHPAGE_NOAUTOCLOSE
!define MUI_UNFINISHPAGE_NOAUTOCLOSE

; PAGES ------------------------------------------------------------------------
!insertmacro MUI_PAGE_WELCOME
;!insertmacro MUI_PAGE_LICENSE ".\license.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_STARTMENU App $StartMenuFolder
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; LANGUAGE ----------------------------------------------------------------------
!insertmacro MUI_LANGUAGE "Russian"
!insertmacro MUI_RESERVEFILE_LANGDLL

; INST TYPES -------------------------------------------------------------------
!ifndef NOINSTTYPES
  InstType "Полная установка"
!endif

; SECTIONS ---------------------------------------------------------------------

Section "Файлы программы" sBase
  SectionIn RO
  SetOutPath "$INSTDIR"
  File /r ".\data"
  File /r ".\poker.exe"
  ;File /r ".\license.txt"
  ;File /r ".\readme.txt"
  WriteUninstaller "$INSTDIR\uninst.exe"
  !insertmacro MUI_STARTMENU_WRITE_BEGIN App
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Деинсталлировать игру.lnk" "$INSTDIR\uninst.exe" "" "$INSTDIR\uninst.exe" 0
    ;CopyFiles "$INSTDIR\readme.txt" "$SMPROGRAMS\$StartMenuFolder\readme.txt" 0
    ;CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Помощь.lnk" "$INSTDIR\Help\Help.htm" "" "" 0
    CreateShortCut "$SMPROGRAMS\$StartMenuFolder\Расписной покер.lnk" "$INSTDIR\poker.exe" "" "$INSTDIR\poker.exe" 0
  !insertmacro MUI_STARTMENU_WRITE_END
  ; сбросим флаги - такое состояние означает, что ярлыки не создавались  
  StrCpy $0 "0"
SectionEnd

Section "Создать ярлык на рабочем столе" sLinks
  SectionIn 1
  StrCpy $0 "1"
  CreateShortCut "$DESKTOP\Расписной покер.lnk" "$INSTDIR\poker.exe" "" "$INSTDIR\poker.exe" 0
SectionEnd

Section ""
  WriteRegStr HKLM "SOFTWARE\Poker" "Install_Dir" "$INSTDIR"
  DetailPrint "Создан ключ реестра HKLM SOFTWARE\Poker"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Poker" "DisplayName" "Расписной покер"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Poker" "UninstallString" '"$INSTDIR\uninst.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Poker" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Poker" "NoRepair" 1
  DetailPrint "Создан ключ реестра HKLM Software\Microsoft\Windows\CurrentVersion\Uninstall\Poker"
  WriteRegStr HKLM "SOFTWARE\Poker" "Links" $0
  DetailPrint "Запись значений реестра HKLM SOFTWARE\Poker"
SectionEnd

; DESCRIPTIONS -----------------------------------------------------------------
; LangStrings
LangString DESC_sBase ${LANG_RUSSIAN} "Основные файлы программы"
LangString DESC_sLinks ${LANG_RUSSIAN} "Создать ярлык для запуска игры на рабочем столе"

;Assign language strings to sections
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${sBase} $(DESC_sBase)
  !insertmacro MUI_DESCRIPTION_TEXT ${sLinks} $(DESC_sLinks)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;-------------------------------------------------------------------------------

; Uninstaller ------------------------------------------------------------------

Section "Uninstall"
  ; сначала зачитаем параметры установки
  !insertmacro MUI_STARTMENU_GETFOLDER App $StartMenuFolder
  ReadRegStr $0 HKLM "SOFTWARE\Poker" "Links"   
  RMDir /r "$SMPROGRAMS\$StartMenuFolder"
  StrCmp $0 "0" NoLinks
    Delete "$DESKTOP\Расписной покер.lnk"
  NoLinks:
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\Poker"
  DetailPrint "Удален ключ реестра HKLM Software\Microsoft\Windows\CurrentVersion\Uninstall\Poker"
  DeleteRegKey HKLM "SOFTWARE\Poker"
  DetailPrint "Удален ключ реестра HKLM SOFTWARE\Poker"
  RMDir /r "$INSTDIR"
SectionEnd
